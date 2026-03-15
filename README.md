<div align="center">

# AutoApply
### AI-Powered Job Application Agent

*Amazon Nova Hackathon 2026 Submission*

[![Nova Act](https://img.shields.io/badge/Amazon-Nova%20Act-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://nova.amazon.com)
[![Nova 2 Lite](https://img.shields.io/badge/Amazon-Nova%202%20Lite-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock)
[![Nova 2 Sonic](https://img.shields.io/badge/Amazon-Nova%202%20Sonic-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Categories:** UI Automation · Agentic AI · Voice AI

Upload your resume. Set your preferences. Let the agents apply while you practice for the interview.

</div>

---

AutoApply is an AI agent fleet that automates end-to-end job applications across multiple job boards, coaches candidates through voice interview prep with Amazon Nova 2 Sonic, and uses Nova 2 Lite to provide intelligent job matching and skill gap coaching.

> 🌍 **Built for the pan-African tech community** — giving every developer in Lagos, Nairobi, and Accra the same tools as candidates in San Francisco.

---

## Demo

> 🎥 [Demo Video — 3 minutes] *(link to video)*

**What the demo shows:**
1. Profile creation and resume upload
2. Resume parsing → Nova 2 Lite extracts 34 skills, years of experience, education
3. Live agent feed: Nova Act browser sessions searching job boards in real time
4. Match scores + AI skill gap coaching populating in real time
5. Tailored cover letters generated for each matched job
6. One-click apply with Nova Act — automated form filling with human escalation for CAPTCHAs
7. Voice interview coaching with Nova 2 Sonic — job-tailored mock interviews with spoken feedback
8. Application tracker dashboard with status tracking

---

## Features

| Feature | Technology |
|---|---|
| **Profile setup** | Manual entry with OAuth-ready architecture (Google, Amazon, Apple, Facebook) |
| **Multi-board parallel search** | Nova Act — Indeed, LinkedIn, Glassdoor via Python threading |
| **Intelligent job matching** | Nova 2 Lite — structured prompt analysis, 0–100 match score |
| **Skill gap coaching** | Nova 2 Lite — reframes existing experience for missing requirements |
| **Tailored cover letters** | Nova 2 Lite — company-specific, cliché-free, auto-generated per job |
| **Automated form filling** | Nova Act — handles diverse layouts, file uploads, screening Q&A |
| **Voice interview coaching** | Nova 2 Sonic — bidirectional 16kHz PCM voice, live AI interviewer |
| **Human-in-the-loop** | CAPTCHA escalation + review-before-submit toggle + dry-run mode |
| **Real-time agent view** | WebSocket feed showing every agent action live |
| **Application tracker** | Full history with status, match scores, and platform tracking |
| **Graceful degradation** | All AI services fall back to realistic mock data when APIs are unavailable |
| **Token authentication** | `X-User-Token` header — auto-injected by Axios interceptor |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js 16 + Tailwind)                        │
│  Profile Setup · Resume Upload · Search Config           │
│  Live Agent Feed · Match Cards · Voice Coach             │
│  Application Dashboard                                   │
└──────────────────────────┬───────────────────────────────┘
                           │ REST + WebSocket
┌──────────────────────────▼───────────────────────────────┐
│  BACKEND (FastAPI + Python 3.11)                         │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  ORCHESTRATOR — pipeline coordinator              │  │
│  │  Sessions · Queuing · WebSocket notifications     │  │
│  └──────┬────────────────┬──────────────────────────┘  │
│         │                │                              │
│  ┌──────▼──────┐  ┌──────▼──────────────────────────┐  │
│  │ NOVA 2 LITE │  │       NOVA ACT AGENTS            │  │
│  │  (Bedrock)  │  │  Parallel browser fleet          │  │
│  │             │  │  Indeed · LinkedIn · Glassdoor   │  │
│  │ • Parsing   │  │                                  │  │
│  │ • Matching  │  │  • Search & extract              │  │
│  │ • Gap coach │  │  • Fill forms                    │  │
│  │ • Cover     │  │  • Upload resume                 │  │
│  │   letters   │  │  • Answer screening Q&A          │  │
│  │ • Screening │  │  • Submit / confirm              │  │
│  └─────────────┘  └─────────────────────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  NOVA 2 SONIC — Voice Interview Coach            │  │
│  │  WebSocket ↔ Bidirectional PCM streaming         │  │
│  │  Live AI interviewer · Spoken feedback           │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  S3 (resumes) · In-memory store (dev) · PostgreSQL (prod)│
└──────────────────────────────────────────────────────────┘
```

---

## AWS Services Used

| Service | Purpose |
|---|---|
| **Amazon Nova Act** | Browser automation — job search, extraction, and form submission across multiple platforms |
| **Amazon Nova 2 Lite** | Resume parsing (34+ skills extracted), job matching (0-100 scores), cover letter generation |
| **Amazon Nova 2 Sonic** | Bidirectional voice interview coaching — real-time speech AI with job-tailored questions |
| **Amazon Bedrock** | Inference API for Nova 2 Lite and Nova 2 Sonic |
| **Amazon S3** | Resume and cover letter storage |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Nova Act API key → [nova.amazon.com](https://nova.amazon.com)
- AWS credentials with Bedrock access to `us.amazon.nova-2-lite-v1:0` and `us.amazon.nova-sonic-v1:0`

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in NOVA_ACT_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Minimum .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<run: openssl rand -base64 32>

npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### No API keys? No problem.

All three AI services degrade gracefully with realistic fallbacks:
- **Nova Act** → returns Nigerian-market mock job listings with realistic companies and Naira salary ranges
- **Nova 2 Lite** → regex-based resume parser extracts skills and experience; keyword-overlap match scoring
- **Nova 2 Sonic** → interactive text-based mock interview with job-tailored questions and coaching tips

The full UI works end-to-end with zero credentials configured.

---

## Nova Act Usage Highlights

**Atomic `act()` calls** for reliability:
```python
nova.act("Find the job search bar and type 'Software Engineer' then press Enter")
nova.act("Find the location filter field and set it to 'Lagos, Nigeria'")
```

**JSON schema extraction** for structured output:
```python
result = nova.act(
    "Read the visible job listing cards and extract job title, company, location "
    "for the first 5 listings. Do NOT click on any job.",
    schema=SIMPLE_EXTRACTION_SCHEMA,
)
```

**Playwright interop** for reliable file uploads:
```python
nova.page.set_input_files('input[type="file"]', resume_path)
```

**Human escalation** when CAPTCHAs are detected:
```python
if captcha_detected:
    return {"requires_human": True, "devtools_url": nova.devtools_frontend_url}
```

**Parallel sessions** via Python threading:
```python
for platform in platforms:
    t = threading.Thread(target=search_jobs_on_platform, args=(platform, ...))
    t.start()
```

---

## Nova 2 Sonic Usage Highlights

**Bidirectional PCM streaming** via Bedrock:
```python
stream = bedrock.invoke_model_with_bidirectional_stream(
    modelId="us.amazon.nova-sonic-v1:0",
    body=initial_event
)
# Stream mic audio in → receive spoken response audio out
```

**Frontend audio pipeline** (16kHz PCM ↔ AudioContext):
```typescript
const source = ctx.createMediaStreamSource(stream);
const processor = ctx.createScriptProcessor(4096, 1, 1);
processor.onaudioprocess = (e) => {
  const chunk = encodeChunk(e.inputBuffer.getChannelData(0));
  ws.send(JSON.stringify({ type: 'audio', data: chunk }));
};
```

**Interactive interview flow** with silence detection:
```python
async def _wait_for_user_speech(audio_in, timeout_seconds=20):
    # Detects when user starts and stops speaking
    # Auto-advances after silence to keep interview flowing
```

---

## Design Decisions

### Graceful Degradation
Every AI service in AutoApply has a built-in fallback:
- If Nova Act hits a CAPTCHA → escalates to the user instead of bypassing security
- If Bedrock is throttled → uses keyword-overlap matching and template cover letters
- If Nova Sonic SDK isn't available → runs an interactive text-based mock interview
- If no API keys are configured → full demo mode with realistic mock data

This ensures the application always works and demonstrates responsible AI design.

### Human-in-the-Loop
AutoApply never submits a job application without user awareness:
- **Dry-run mode** (default ON) fills forms but doesn't click submit
- **Review-before-submit** lets users approve each application
- **CAPTCHA escalation** hands control back to the user rather than attempting to bypass security measures

---

## Security Notes

- All user-facing routes require `X-User-Token` header (generated on account creation via `secrets.token_urlsafe(32)`)
- Token is stored in `localStorage` and auto-injected by the Axios request interceptor
- Resume upload restricted to PDF, max 10 MB
- File system paths never returned to clients
- `dry_run: true` default prevents accidental live submissions
- AWS credentials never exposed to the frontend

---

## The Problem We're Solving

Job seekers in emerging markets face a structural disadvantage: the mechanics of job hunting are time-intensive, and candidates in major tech hubs have more time and tools to navigate the process.

A developer in Lagos with identical skills to one in San Francisco shouldn't lose opportunities simply because they can't afford to spend 40 hours a week on applications.

AutoApply levels that playing field. Read the full story in our [blog post](docs/blog-post.md).

---

## License

MIT — free to use, adapt, and build upon.

---

*#AmazonNova · Amazon Nova Hackathon 2026*