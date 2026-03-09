# AutoApply — AI-Powered Job Application Agent

> **Amazon Nova Hackathon Submission** · Categories: UI Automation + Agentic AI · Voice AI

AutoApply is an AI agent fleet that automates end-to-end job applications across multiple job boards, coaches candidates through voice interview prep with Amazon Nova 2 Sonic, and uses Nova 2 Lite to provide intelligent job matching and skill gap coaching.

Upload your resume. Sign in with Google, Amazon, Apple, or Facebook. Let the agents apply while you practice for the interview.

**Built with:** Amazon Nova Act · Amazon Nova 2 Lite (Bedrock) · Amazon Nova 2 Sonic (Bedrock) · FastAPI · Next.js · NextAuth.js

---

## Demo

> 🎥 [Demo Video — 3 minutes] *(link to video)*

**What the demo shows:**
1. OAuth sign-in (Google / Amazon / Apple / Facebook) — one click, no form
2. Resume upload → Nova 2 Lite extracts 12+ skills, years of experience, certifications
3. Live agent feed: three Nova Act browser sessions searching Indeed, LinkedIn, Glassdoor in parallel
4. Match scores + AI skill gap coaching populating in real time
5. Nova Act filling and submitting a real job application form
6. Voice interview coaching with Nova 2 Sonic — live spoken feedback
7. Application tracker dashboard with confirmation numbers

---

## Features

| Feature | Technology |
|---|---|
| **Social Sign-In** | NextAuth — Google, Amazon, Apple, Facebook OAuth |
| **Multi-board parallel search** | Nova Act — 3 job boards via Python threading |
| **Intelligent job matching** | Nova 2 Lite + extended thinking — 0–100 match score |
| **Skill gap coaching** | Nova 2 Lite — reframes existing experience for missing requirements |
| **Tailored cover letters** | Nova 2 Lite — company-specific, cliché-free |
| **Automated form filling** | Nova Act — handles diverse layouts, file uploads, screening Q&A |
| **Voice interview coaching** | Nova 2 Sonic — bidirectional 16kHz PCM voice, live AI interviewer |
| **Human-in-the-loop** | CAPTCHA escalation + review-before-submit toggle |
| **Real-time agent view** | WebSocket feed showing every agent action live |
| **Application tracker** | Full history with status, scores, confirmation numbers |
| **Token authentication** | `X-User-Token` header — auto-injected by Axios interceptor |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js 16 + Tailwind + NextAuth)             │
│  OAuth Login · Resume Upload · Preferences               │
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
│  PostgreSQL · S3 (resumes) · In-memory queue            │
└──────────────────────────────────────────────────────────┘
```

---

## AWS Services Used

| Service | Purpose |
|---|---|
| **Amazon Nova Act** | Browser automation — job search and form submission |
| **Amazon Nova 2 Lite** | Resume parsing, job matching (extended thinking), cover letters |
| **Amazon Nova 2 Sonic** | Bidirectional voice interview coaching |
| **Amazon Bedrock** | Inference API for Nova 2 Lite and Nova 2 Sonic |
| **Amazon S3** | Resume and cover letter storage |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Nova Act API key → [nova.amazon.com](https://nova.amazon.com)
- AWS credentials with Bedrock access to `us.amazon.nova-2-lite-v1:0` and `us.amazon.nova-sonic-v1:0`
- (Optional) OAuth app credentials for social login

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

# Add any OAuth providers you have credentials for:
# GOOGLE_CLIENT_ID=...       GOOGLE_CLIENT_SECRET=...
# FACEBOOK_APP_ID=...        FACEBOOK_APP_SECRET=...
# AMAZON_CLIENT_ID=...       AMAZON_CLIENT_SECRET=...
# APPLE_ID=...  APPLE_TEAM_ID=...  APPLE_KEY_ID=...  APPLE_PRIVATE_KEY=...

npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### No API keys? No problem.

All three AI services fall back to realistic mock data:
- **Nova Act** → returns Nigerian-market mock job listings (Jobberman / RemoteAfrica salary ranges)
- **Nova 2 Lite** → returns a default match structure with `match_score: 50`
- **Nova 2 Sonic** → plays a mock voice session with pre-written Q&A

The full UI works end-to-end with zero credentials configured.

---

## Project Structure

```
autoapply/
├── backend/
│   ├── main.py                     # FastAPI app, routes, lifespan
│   ├── config.py                   # pydantic-settings from .env
│   ├── agents/
│   │   ├── job_searcher.py         # Nova Act — parallel job search
│   │   └── application_agent.py    # Nova Act — form filling + submission
│   ├── services/
│   │   ├── resume_parser.py        # PDF → Nova 2 Lite structured data
│   │   ├── job_matcher.py          # Match scoring, gap coaching, cover letters
│   │   ├── orchestrator.py         # Full pipeline coordinator
│   │   ├── voice_service.py        # Nova 2 Sonic bidirectional streaming
│   │   └── s3_service.py           # S3 resume storage with local fallback
│   ├── api/
│   │   ├── websocket_manager.py    # Real-time WebSocket event bus
│   │   └── routes/
│   │       ├── users.py            # User CRUD, resume upload, token auth
│   │       ├── jobs.py             # Search, apply, match analysis
│   │       └── voice.py            # Nova 2 Sonic WebSocket endpoint
│   └── db/
│       └── models.py               # SQLAlchemy models
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── layout.tsx          # SessionProvider wrapper
│       │   ├── page.tsx            # Main dashboard
│       │   └── api/auth/[...nextauth]/route.ts
│       ├── components/
│       │   ├── agent/
│       │   │   ├── AgentFeed.tsx
│       │   │   ├── HumanEscalation.tsx
│       │   │   └── VoiceCoach.tsx  # Nova 2 Sonic voice UI
│       │   └── dashboard/
│       │       ├── ProfileSetup.tsx  # Social login buttons + form
│       │       ├── JobCard.tsx
│       │       └── ...
│       ├── lib/
│       │   ├── api.ts              # Axios client + auth interceptor
│       │   └── auth.config.ts      # NextAuth provider config
│       └── types/
│           └── index.ts
└── docs/
    ├── blog-post.md                # builder.aws.com submission
    └── demo-script.md              # 3-minute demo video script
```

---

## Nova Act Usage Highlights

**Atomic `act()` calls** for reliability:
```python
nova.act("Find and click the 'Apply' button")
nova.act(f"Fill the name field with '{name}'")
nova.act("Check if there is a cover letter text field")
```

**Pydantic schema extraction** for typed output:
```python
result = nova.act(
    "Extract job title, company, location, requirements for the first 10 listings",
    schema=JobResults.model_json_schema()
)
jobs = JobResults.model_validate_json(result.parsed_response)
```

**Playwright interop** for reliable file uploads:
```python
nova.page.set_input_files('input[type="file"]', resume_path)
```

**Human escalation** via devtools URL:
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
const processor = ctx.createScriptProcessor(512, 1, 1);
processor.onaudioprocess = (e) => {
  const chunk = encodeChunk(e.inputBuffer.getChannelData(0));
  ws.send(JSON.stringify({ type: 'audio', data: chunk }));
};
```

---

## Security Notes

- All user-facing routes require `X-User-Token` header (generated on account creation via `secrets.token_urlsafe(32)`)
- Token is stored in `localStorage` and auto-injected by the Axios request interceptor
- OAuth flow (NextAuth) auto-creates the backend user and stores the token in an encrypted JWT cookie
- Resume upload restricted to PDF, max 10 MB
- File system paths never returned to clients
- `dry_run: true` default prevents accidental live submissions

---

## The Problem We're Solving

Job seekers in emerging markets face a structural disadvantage: the mechanics of job hunting are time-intensive, and candidates in major tech hubs have more time and tools to navigate the process.

A developer in Lagos with identical skills to one in San Francisco shouldn't lose opportunities simply because they can't afford to spend 40 hours a week on applications.

AutoApply levels that playing field. Read the full story in our [blog post](docs/blog-post.md).

---

## License

MIT — free to use, adapt, and build upon.

---

*#AmazonNova · Amazon Nova Hackathon 2025*


---

## Demo

> 🎥 [Demo Video — 3 minutes] (link to video)

**What the demo shows:**
- Resume upload → Nova 2 Lite parses and extracts structured data
- Live split-screen of Nova Act agents searching Indeed, LinkedIn, Glassdoor simultaneously
- Match scores and skill gap coaching populating in real time
- Nova Act filling out a real job application form
- Application tracker dashboard with confirmation

---

## Features

- **Multi-board parallel search** — Nova Act searches 3 job boards simultaneously via Python threading
- **Intelligent matching** — Nova 2 Lite with extended thinking scores resume-to-job fit (0-100)
- **Skill gap coaching** — AI explains how to reframe existing experience for missing requirements
- **Tailored cover letters** — Non-generic, company-specific letters generated per application
- **Automated form filling** — Nova Act handles diverse form layouts, file uploads, screening questions
- **Human-in-the-loop** — CAPTCHA escalation, review-before-submit toggle for high-value applications
- **Real-time agent view** — WebSocket feed shows exactly what the agent is doing, live
- **Application tracker** — Dashboard with status, match scores, confirmation numbers

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND (Next.js + Tailwind)                      │
│  Resume Upload · Preferences · Live Agent View      │
│  Application Dashboard · Match Scores               │
└──────────────────────┬──────────────────────────────┘
                       │ REST + WebSocket
┌──────────────────────▼──────────────────────────────┐
│  BACKEND (FastAPI + Python)                         │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  ORCHESTRATOR                                │  │
│  │  Manages sessions, queuing, WS notifications │  │
│  └──────┬─────────────────────┬────────────────┘  │
│         │                     │                    │
│  ┌──────▼──────┐    ┌─────────▼───────────────┐   │
│  │ NOVA 2 LITE │    │     NOVA ACT AGENTS      │   │
│  │ (Bedrock)   │    │  Parallel browser fleet  │   │
│  │             │    │  Indeed + LinkedIn +     │   │
│  │ • Resume    │    │  Glassdoor               │   │
│  │   parsing   │    │                          │   │
│  │ • Matching  │    │ • Search jobs            │   │
│  │ • Gap coach │    │ • Fill forms             │   │
│  │ • Cover     │    │ • Upload resume          │   │
│  │   letters   │    │ • Answer questions       │   │
│  │ • Screening │    │ • Submit / confirm       │   │
│  └─────────────┘    └──────────────────────────┘   │
│                                                     │
│  PostgreSQL · S3 (resumes) · In-memory queue       │
└─────────────────────────────────────────────────────┘
```

---

## AWS Services Used

| Service | Purpose |
|---------|---------|
| **Nova Act** | Browser automation — job search and application submission |
| **Nova 2 Lite (Bedrock)** | Resume parsing, job matching with extended thinking, cover letter generation |
| **S3** | Resume and cover letter storage |
| **Amazon Bedrock** | API gateway for Nova 2 Lite inference |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or SQLite for testing)
- Nova Act API key → [nova.amazon.com](https://nova.amazon.com)
- AWS credentials with Bedrock access to `us.amazon.nova-2-lite-v1:0`

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and fill in:
# NOVA_ACT_API_KEY=your_key
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# DATABASE_URL=postgresql+asyncpg://...

# Start backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Test without API keys

Both Nova Act and Bedrock have graceful fallbacks to mock data. Set environment variables to empty strings and the app will use realistic mock job listings and simulated match scores — useful for UI development.

---

## Project Structure

```
autoapply/
├── backend/
│   ├── main.py                    # FastAPI app + all routes
│   ├── config.py                  # Settings from .env
│   ├── agents/
│   │   ├── job_searcher.py        # Nova Act: parallel job search
│   │   └── application_agent.py   # Nova Act: form filling + submission
│   ├── services/
│   │   ├── resume_parser.py       # PDF → text → Nova 2 Lite structured data
│   │   ├── job_matcher.py         # Match scoring, gap coaching, cover letters
│   │   └── orchestrator.py        # Full pipeline coordinator
│   ├── api/
│   │   └── websocket_manager.py   # Real-time WebSocket updates
│   └── db/
│       └── models.py              # SQLAlchemy models
├── frontend/
│   └── src/
│       ├── app/
│       │   └── page.tsx           # Main dashboard UI
│       ├── hooks/
│       │   └── useAgentWebSocket.ts
│       ├── lib/
│       │   └── api.ts             # API client
│       └── types/
│           └── index.ts
└── docs/
    ├── blog-post.md               # builder.aws.com blog post
    └── demo-script.md             # 3-minute demo video script
```

---

## Nova Act Usage Highlights

This project demonstrates advanced Nova Act patterns:

**Atomic act() calls** for reliability:
```python
nova.act("Find and click the 'Apply' button")
nova.act(f"Fill the name field with '{name}'")
nova.act("Check if there is a cover letter text field")
```

**Pydantic schema extraction** for structured data:
```python
result = nova.act(
    "Extract job title, company, location, requirements for first 10 listings",
    schema=JobResults.model_json_schema()
)
jobs = JobResults.model_validate_json(result.parsed_response)
```

**Playwright interop** for reliable file uploads:
```python
nova.page.set_input_files('input[type="file"]', resume_path)
```

**Human escalation** via devtools URL:
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

## The Problem We're Solving

Job seekers in emerging markets face a structural disadvantage: the mechanics of job hunting are time-intensive, and candidates in major tech hubs have more time and tools to navigate the process. A developer in Lagos with identical skills to one in San Francisco shouldn't lose opportunities simply because they can't afford to spend 40 hours a week on applications.

AutoApply levels that playing field. Read the full story in our [blog post](docs/blog-post.md).

---

## License

MIT — free to use, adapt, and build upon.

---

*#AmazonNova · Amazon Nova Hackathon 2025*
#   A u t o A p p l y  
 