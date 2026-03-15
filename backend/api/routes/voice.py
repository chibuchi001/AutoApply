"""
Voice interview coaching WebSocket endpoint.
Bridges browser microphone audio ↔ Nova 2 Sonic via WebSocket.
"""

import asyncio
import base64
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.voice_service import run_sonic_interview

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.websocket("/interview/{user_id}")
async def voice_interview(websocket: WebSocket, user_id: str):
    """
    Real-time voice interview coaching via Nova 2 Sonic.

    Client → Server messages:
      {"type":"start","job":{...},"resume_summary":"..."}
      {"type":"audio","data":"<base64 raw 16kHz 16-bit mono PCM>"}
      {"type":"stop"}

    Server → Client messages:
      {"type":"status","message":"..."}
      {"type":"audio","data":"<base64 16kHz 16-bit mono PCM>"}
      {"type":"transcript","role":"assistant|user","text":"..."}
      {"type":"done"}
      {"type":"error","message":"..."}
    """
    await websocket.accept()
    audio_in: asyncio.Queue = asyncio.Queue()

    async def send(payload: dict) -> None:
        await websocket.send_text(json.dumps(payload))

    try:
        # ── Expect a "start" message first with job context ────────────────────
        raw = await websocket.receive_text()
        msg = json.loads(raw)

        if msg.get("type") != "start":
            await send({"type": "error", "message": "First message must be {type:'start',...}"})
            return

        job: dict = msg.get("job", {})
        resume_summary: str = msg.get("resume_summary", "")

        await send({
            "type": "status",
            "message": (
                f"Starting interview coaching for "
                f"{job.get('title', 'your role')} at "
                f"{job.get('company', 'the company')}…"
            ),
        })

        # ── Callbacks for Sonic output ─────────────────────────────────────────
        async def on_audio(audio_bytes: bytes) -> None:
            await send({"type": "audio", "data": base64.b64encode(audio_bytes).decode()})

        async def on_text(role: str, text: str) -> None:
            await send({"type": "transcript", "role": role, "text": text})

        # ── Receive client audio and control messages ──────────────────────────
        async def receive_loop() -> None:
            while True:
                try:
                    raw = await websocket.receive_text()
                    msg = json.loads(raw)
                    if msg["type"] == "audio":
                        await audio_in.put(base64.b64decode(msg["data"]))
                    elif msg["type"] == "stop":
                        await audio_in.put(None)
                        break
                except WebSocketDisconnect:
                    await audio_in.put(None)
                    break
                except Exception as e:
                    logger.warning(f"Voice receive loop error: {e}")
                    await audio_in.put(None)
                    break

        # ── Run Sonic session and receive loop concurrently ───────────────────
        await asyncio.gather(
            run_sonic_interview(job, resume_summary, audio_in, on_audio, on_text),
            receive_loop(),
        )

        await send({"type": "done"})

    except WebSocketDisconnect:
        await audio_in.put(None)
        logger.info(f"Voice session disconnected: {user_id}")
    except Exception as e:
        logger.error(f"Voice session error [{user_id}]: {e}", exc_info=True)
        try:
            await send({"type": "error", "message": str(e)[:200]})
        except Exception:
            pass
