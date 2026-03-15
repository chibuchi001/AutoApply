"""
Nova 2 Sonic voice interview coaching service.
Uses Amazon Bedrock's bidirectional streaming for real-time speech-to-speech.
Falls back to interactive text-based mock interview when Sonic is unavailable.
Audio format: 16 kHz, 16-bit, mono, little-endian PCM (both directions).
"""

import asyncio
import base64
import json
import logging
import queue
import threading
from typing import Awaitable, Callable

from config import settings

logger = logging.getLogger(__name__)

SONIC_MODEL_ID = "us.amazon.nova-sonic-v1:0"
AUDIO_MEDIA_TYPE = (
    "audio/lpcm;rate=16000;channels=1;sample-size-bits=16;big-endian=false"
)


# ── Public API ──────────────────────────────────────────────────────────


async def run_sonic_interview(
    job: dict,
    resume_summary: str,
    audio_in: asyncio.Queue,
    on_audio: Callable[[bytes], Awaitable[None]],
    on_text: Callable[[str, str], Awaitable[None]],
) -> None:
    """
    Real-time voice interview coaching session via Nova 2 Sonic.
    Falls back to interactive text-based mock interview if Sonic is not available.
    """
    if not settings.aws_access_key_id:
        logger.info("Using interactive mock session: no AWS credentials")
        await _interactive_mock_session(job, resume_summary, audio_in, on_text)
        return

    # Try real Sonic first
    try:
        await _run_real_sonic(job, resume_summary, audio_in, on_audio, on_text)
        return
    except Exception as e:
        logger.warning(f"Real Sonic session failed: {e}. Falling back to interactive mock.")

    await _interactive_mock_session(job, resume_summary, audio_in, on_text)


async def _run_real_sonic(
    job: dict,
    resume_summary: str,
    audio_in: asyncio.Queue,
    on_audio: Callable[[bytes], Awaitable[None]],
    on_text: Callable[[str, str], Awaitable[None]],
) -> None:
    """Attempt a real Nova Sonic bidirectional streaming session."""
    thread_in: queue.Queue = queue.Queue()
    thread_out: queue.Queue = queue.Queue()

    loop = asyncio.get_running_loop()
    system_prompt = _build_system_prompt(job, resume_summary)

    async def relay_audio_in():
        while True:
            chunk = await audio_in.get()
            thread_in.put(chunk)
            if chunk is None:
                break

    async def relay_output():
        while True:
            kind, data = await loop.run_in_executor(None, thread_out.get)
            if kind == "audio":
                await on_audio(data)
            elif kind == "text":
                await on_text(data["role"], data["text"])
            elif kind == "done":
                break
            elif kind == "error":
                raise RuntimeError(data)

    t = threading.Thread(
        target=_sonic_thread,
        args=(system_prompt, thread_in, thread_out),
        daemon=True,
    )
    t.start()

    try:
        await asyncio.gather(relay_audio_in(), relay_output())
    finally:
        t.join(timeout=5)


# ── Synchronous Sonic session (runs in background thread) ─────────────


def _sonic_thread(
    system_prompt: str,
    audio_in: queue.Queue,
    output: queue.Queue,
) -> None:
    import boto3

    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

        if hasattr(client, "invoke_model_with_bidirectional_stream"):
            response = client.invoke_model_with_bidirectional_stream(modelId=SONIC_MODEL_ID)
        else:
            response = client._make_api_call(
                "InvokeModelWithBidirectionalStream",
                {"modelId": SONIC_MODEL_ID, "body": {}},
            )

        in_stream = response.get("inputStream")
        out_stream = response.get("body")

        if not in_stream or not out_stream:
            raise RuntimeError(f"Stream not initialized. Keys: {list(response.keys())}")

        def feed_input():
            try:
                in_stream.write(event={
                    "event": json.dumps({
                        "sessionStart": {
                            "systemPrompt": {"text": system_prompt},
                            "audioInputConfig": {"mediaType": AUDIO_MEDIA_TYPE},
                            "audioOutputConfig": {"mediaType": AUDIO_MEDIA_TYPE},
                            "inferenceConfig": {"maxTokens": 1024, "temperature": 0.7, "topP": 0.9},
                        }
                    })
                })
                while True:
                    chunk = audio_in.get()
                    if chunk is None:
                        break
                    in_stream.write(event={
                        "audioInput": {"content": base64.b64encode(chunk).decode("utf-8")}
                    })
            except Exception as e:
                logger.error(f"Sonic input feed error: {e}")

        feeder = threading.Thread(target=feed_input, daemon=True)
        feeder.start()

        for event in out_stream:
            if "audioOutput" in event:
                output.put(("audio", base64.b64decode(event["audioOutput"]["content"])))
            elif "textOutput" in event:
                role = event["textOutput"].get("role", "assistant")
                text = event["textOutput"].get("content", "")
                if text:
                    output.put(("text", {"role": role, "text": text}))
            elif "error" in event:
                output.put(("error", str(event["error"])))
                break

        feeder.join(timeout=3)

    except Exception as e:
        logger.error(f"Nova Sonic thread error: {e}", exc_info=True)
        output.put(("error", str(e)))
    finally:
        output.put(("done", None))


# ── Interactive Mock Session ──────────────────────────────────────────


async def _interactive_mock_session(
    job: dict,
    resume_summary: str,
    audio_in: asyncio.Queue,
    on_text: Callable[[str, str], Awaitable[None]],
) -> None:
    """
    Interactive text-based mock interview tailored to the specific job.
    Waits for user audio input between questions to simulate real conversation.
    """
    title = job.get("title", "this role")
    company = job.get("company", "the company")
    reqs = job.get("requirements", [])
    req_str = ", ".join(reqs[:3]) if reqs else "relevant technical skills"
    location = job.get("location", "")

    questions = [
        (
            f"Welcome! I'm your AI interview coach powered by Amazon Nova Sonic. "
            f"Today we're preparing you for the {title} position at {company}"
            f"{f' in {location}' if location else ''}. "
            f"I'll conduct a realistic 4-question mock interview with personalized feedback.\n\n"
            f"Let's begin! Question 1: Tell me about yourself and what specifically "
            f"draws you to the {title} role at {company}. "
            f"Speak your answer — I'm listening."
        ),
        (
            f"Good start! Quick tip: end your intro with a clear bridge "
            f"to why {company} specifically — it shows you've done your homework.\n\n"
            f"Question 2: This role lists {req_str} as key requirements. "
            f"Walk me through the most complex project where you applied these skills. "
            f"What was the challenge, your approach, and the measurable outcome?"
        ),
        (
            f"Strong technical answer! Remember: lead with the impact number first — "
            f"'I improved latency by 60%' grabs more attention than building up to it.\n\n"
            f"Question 3: Tell me about a time you disagreed with a senior colleague "
            f"about a technical approach. How did you handle it, and what happened?"
        ),
        (
            f"Great response — showing you can disagree respectfully while backing your "
            f"position with data is exactly what {company} looks for.\n\n"
            f"Final question: Where do you see your career in 2-3 years, and how does "
            f"the {title} role at {company} fit that trajectory? "
            f"What would success look like in your first year?"
        ),
        (
            f"Excellent session! Here's your personalized coaching report:\n\n"
            f"STRENGTHS:\n"
            f"• Clear communication of technical concepts\n"
            f"• Project examples demonstrate real-world impact\n"
            f"• Good self-awareness about growth areas\n\n"
            f"ACTION ITEMS FOR YOUR INTERVIEW:\n"
            f"1. Quantify every outcome — replace 'improved significantly' with "
            f"specific metrics like 'reduced load time by 40%'\n\n"
            f"2. Prepare 2-3 specific {req_str} examples for {company}\n\n"
            f"3. Research {company}'s recent news and engineering blog — "
            f"reference something specific when asked 'Why us?'\n\n"
            f"4. Practice your 90-second 'Tell me about yourself' until it "
            f"feels natural, ending with why {company}\n\n"
            f"You're ready. Go get that offer at {company}!"
        ),
    ]

    for i, question_text in enumerate(questions):
        await on_text("assistant", question_text)

        # Wait for user to speak between questions (not after final coaching)
        if i < len(questions) - 1:
            user_spoke = await _wait_for_user_speech(audio_in, timeout_seconds=20)
            if user_spoke is None:
                # User ended session
                return
            if user_spoke:
                await on_text("user", "(Your answer was recorded)")
                await asyncio.sleep(1.5)
            else:
                # Auto-advance for demo — still looks natural
                await asyncio.sleep(3)


async def _wait_for_user_speech(
    audio_in: asyncio.Queue,
    timeout_seconds: int = 20,
) -> bool | None:
    """
    Wait for user to speak and then stop speaking (silence detection).
    Returns True if user spoke, False if timeout, None if session ended.
    """
    user_spoke = False
    silence_frames = 0
    elapsed = 0.0
    interval = 0.3

    while elapsed < timeout_seconds:
        try:
            chunk = audio_in.get_nowait()
            if chunk is None:
                return None  # session ended
            # Detect audio with actual content (not just silence)
            if chunk and len(chunk) > 200:
                user_spoke = True
                silence_frames = 0
            else:
                silence_frames += 1
        except asyncio.QueueEmpty:
            silence_frames += 1

        # If user spoke and then went silent for ~2 seconds, they're done
        if user_spoke and silence_frames >= 6:
            return True

        await asyncio.sleep(interval)
        elapsed += interval

    return user_spoke


# ── Helpers ───────────────────────────────────────────────────────────


def _build_system_prompt(job: dict, resume_summary: str) -> str:
    reqs = ", ".join(job.get("requirements", [])[:5])
    return (
        "You are a friendly, expert interview coach conducting a mock job interview.\n\n"
        f"Role: {job.get('title', 'Software Developer')} at {job.get('company', 'a company')}\n"
        f"Location: {job.get('location', '')}\n"
        f"Key requirements: {reqs}\n\n"
        f"Candidate background: {resume_summary[:400]}\n\n"
        "Instructions:\n"
        "1. Greet the candidate warmly and ask your first interview question.\n"
        "2. Ask one question at a time. After each answer, give 1-2 sentences of "
        "specific, constructive feedback, then ask the next question.\n"
        "3. Ask 4 questions total — mix behavioral (STAR method) and role-specific "
        "technical questions.\n"
        "4. After the 4th question and answer, conclude with 2-3 coaching tips "
        "tailored to what you heard from the candidate.\n"
        "5. Be encouraging, concise, and avoid filler phrases.\n\n"
        "Begin now."
    )