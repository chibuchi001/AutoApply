# AutoApply — 3-Minute Demo Script
## Amazon Nova Hackathon Submission

---

### PRE-RECORDING CHECKLIST
- [ ] Backend running on localhost:8000 (`uvicorn main:app --reload`)
- [ ] Frontend running on localhost:3000 (`npm run dev`)
- [ ] At least one OAuth provider configured (Google recommended), OR manual profile form ready as fallback
- [ ] Mock data enabled OR Nova Act + Bedrock credentials configured
- [ ] Screen recording software ready (OBS / Loom — record at 1920×1080, export ≤200 MB)
- [ ] Browser in incognito, zoom at 110%
- [ ] A real-looking PDF resume ready (name it `chidi_okafor_resume.pdf`)
- [ ] Microphone tested — record narration cleanly, separate from screen audio
- [ ] Close Slack, Teams, all notifications

---

## SCRIPT

### 00:00 – 00:20 | THE HOOK *(voice over — show a job board with hundreds of listings)*

> "Meet Chidi. Senior .NET developer. Lagos. Five years of fintech experience, two system designs that handled over a million transactions a day.
>
> He's spending 40 hours a week on this — copying his resume into form fields, writing cover letters, answering the same screening questions over and over. Not because he's less qualified. Because the job application process was designed for people who have 40 hours to spare.
>
> AutoApply gives those 40 hours back. Powered by Amazon Nova Act, Nova 2 Lite, and Nova 2 Sonic."

*[Cut to: AutoApply homepage loading cleanly]*

---

### 00:20 – 00:45 | SIGN IN + SETUP *(screen record)*

**Action: Click the Google button in the Profile card**

> "First — no forms. Chidi clicks Sign in with Google. One redirect, one click."

*[OAuth popup → Google consent → redirect back to AutoApply]*
*[Profile card collapses with green "Profile created successfully" tick — name pre-filled from Google]*

> "AutoApply creates his backend account automatically. Token issued, stored, every subsequent request authenticated silently. He never typed a password."

**Action: Upload PDF resume**

> "He drops his resume. Nova 2 Lite — Amazon's fast reasoning model running on Bedrock — parses it in seconds."

*[Click upload, select chidi_okafor_resume.pdf]*
*[Show parsed result: "12 skills found" — Python, .NET, PostgreSQL, Docker visible]*

> "Five years experience. Twelve skills extracted. Certifications matched. Structured data — ready to score against any job listing."

---

### 00:45 – 01:30 | THE MAGIC — LIVE AGENT VIEW *(split screen)*

**Action: Fill search config**

> "Senior .NET Developer. Lagos. All three platforms — Indeed, LinkedIn, Glassdoor. 60% minimum match. Dry run on — so we review before any real submission."

*[Fill query field, select all platforms, drag match slider to 60]*

**Action: Click "Launch Agent"**

> "Launch."

*[Click — immediately switch to split view: left = agent feed, right = browser / narrate]*

> "Three Nova Act browser sessions just opened in parallel — one on each platform. Watch the live feed."

*[Agent feed populates:]*
*`"Starting search on Indeed..."` → `"Starting search on LinkedIn..."` → `"Starting search on Glassdoor..."`*
*`"Found 10 jobs on Indeed"` → `"Found 8 on LinkedIn"`*

> "Nova Act isn't scraping HTML. It's reading the page like a human — clicking, scrolling, extracting structured data using natural language instructions. Titles, requirements, salary ranges, posted dates."

> "Now Nova 2 Lite is scoring each result against Chidi's resume — with extended thinking enabled. The model reasons through the match before giving a score."

*[Show: `"Analyzing: Senior .NET Developer at TechCorp — 87% match"` → `"Analyzing: Lead Dev at Fintech Solutions — 72%"`]*

---

### 01:30 – 02:00 | COACHING + APPLICATION *(screen record)*

**Action: Scroll through results panel**

> "Matched jobs. Sorted by score — 87, 79, 72."

*[Expand the top JobCard]*

> "At 87% — Kubernetes is a gap. But Nova 2 Lite found that Chidi's containerised microservices work is equivalent experience. It's not telling him to lie. It's showing him exactly how to reframe a resume bullet he already has to pass ATS filters."

*[Highlight the amber coaching box — read the first sentence aloud]*

> "Cover letter already written. Not 'I am writing to express my interest' — a specific opening about TechCorp's product."

*[Expand cover letter section, scroll quickly]*

**Action: Click Apply**

> "Apply."

*[Agent feed shows:]*
*`"Filling personal information..."` → `"Resume uploaded"` → `"Cover letter added"` → `"Answering: Do you have right to work in Nigeria? → Yes"`*

> "Every field. Every file upload. Every screening question — answered from Chidi's real profile. Nothing fabricated. Review step — he sees everything before it goes."

---

### 02:00 – 02:40 | VOICE INTERVIEW COACH *(screen record)*

**Action: Click "Practice Interview" on a job card**

> "AutoApply doesn't just get Chidi to the interview stage. It prepares him for it."

*[Voice Coach panel opens — show job context: TechCorp, .NET Developer]*

**Action: Click Start and speak**

> "Nova 2 Sonic — Amazon's voice AI — runs a live mock interview. Chidi speaks. The model responds with spoken feedback. Real-time."

*[Speak: "I led the migration of a monolithic payments service to microservices using Docker and Azure Service Bus..."]*
*[Sonic responds — show transcript updating while audio plays back]*

> "The model knows the role. It's coaching on .NET, Kubernetes, fintech — not generic tips."

---

### 02:40 – 03:00 | CLOSE *(voice over — hold on full dashboard)*

> "Application tracker. Every job. Every status. Every confirmation number. Full audit trail.
>
> When a CAPTCHA appears — AutoApply escalates to Chidi via the live feed and hands him a direct link into the browser session to solve it. Human-in-the-loop, not a dead end.
>
> Nova Act found the jobs. Nova 2 Lite matched and coached them. Nova 2 Sonic prepared him for the call.
>
> For Chidi in Lagos. For the developer in Nairobi who has the skills and not the time.
>
> AutoApply. #AmazonNova."

*[Hold on final dashboard — job cards visible, good match scores, Voice Coach panel in background]*

---

## BACKUP PLAN (if live demo fails)

| Failure | Fallback |
|---|---|
| OAuth flow fails | Use manual profile form — name, email, click Create Profile |
| Nova Act credentials missing | Mock data shows realistic Nigerian job listings automatically |
| Bedrock rate limit | Mock fallback returns 85/72/68 match scores automatically |
| Voice coaching WebSocket drops | Show static transcript screenshot, narrate what Sonic said |
| Browser session crashes | Pre-record the application segment, cut to it |

---

## POST-RECORDING CHECKLIST

- [ ] Export at 1080p, compress to under 200 MB (HandBrake: H.264, CRF 23)
- [ ] Add burnt-in captions — judges watch without audio first
- [ ] Add `#AmazonNova` as a text overlay at 02:50
- [ ] Trim the first and last 3 seconds of dead air
- [ ] Test playback on a phone — check captions are readable at small size
- [ ] Upload to YouTube (unlisted) and paste the link into Devpost


---

## SCRIPT

### 00:00 – 00:20 | THE HOOK (voice over, show job board screen)

> "Meet Chidi. He's a .NET developer in Lagos with 5 years of fintech experience. He's qualified. He's skilled. But he's spending 40 hours a week copy-pasting his resume into form after form on LinkedIn, Indeed, Glassdoor — each one slightly different. Each one taking 30 minutes.
>
> He's competing against candidates in London who have those 40 hours free because they're not battling a 2-hour commute and a different time zone.
>
> AutoApply changes that. Powered by Amazon Nova Act and Nova 2 Lite, it turns 40 hours of job hunting into 40 minutes."

*[Show: The AutoApply homepage loading cleanly]*

---

### 00:20 – 00:50 | SETUP (screen record)

**Action: Fill in profile form**

> "First, Chidi enters his basic information — name, email, phone, location. Takes 30 seconds."

*[Type quickly: Chidi Okafor, chidi@example.com, +234..., Lagos, Nigeria]*

**Action: Upload PDF resume**

> "He uploads his resume. Nova 2 Lite — Amazon's fast reasoning model — parses it in seconds."

*[Click upload, select PDF, click "Parse with Nova 2 Lite"]*

*[Show the parsed result appearing: 12 skills found, 5 years experience, Python, .NET, PostgreSQL listed]*

> "Notice what just happened — the model extracted his skills, years of experience, certifications, everything. Structured. Typed. Ready to match against job listings."

---

### 00:50 – 01:30 | THE MAGIC — LIVE AGENT VIEW (split screen)

**Action: Set search preferences**

> "Chidi wants .NET developer roles in Lagos. He selects all three platforms — Indeed, LinkedIn, Glassdoor — and sets 60% as his minimum match threshold."

*[Fill: ".NET Developer", "Lagos Nigeria", select all platforms, set slider to 60]*

**Action: Click "Launch Agent"**

> "And launch."

*[Click Launch Agent button]*

**SWITCH TO SPLIT SCREEN: Left = dashboard agent feed, Right = describe what's happening]*

> "Watch the live agent feed on the left. Three Nova Act browser sessions just opened simultaneously — one on each job board. They're searching right now."

*[Agent feed shows: "Starting search on Indeed..." "Starting search on LinkedIn..." "Starting search on Glassdoor..."]*

> "Jobs are being extracted in real time. Not just titles — Nova Act is pulling structured data: job URL, requirements, salary range, posted date. All via natural language instructions to the browser."

*[Jobs start populating: "Found 10 jobs on Indeed" "Found 8 jobs on LinkedIn"]*

> "And now Nova 2 Lite is analyzing each listing against Chidi's resume. With extended thinking enabled — the model reasons through each match before scoring it."

*[Show: "Analyzing: Senior .NET Developer at TechCorp — 87% match" "Analyzing: Lead Developer at Fintech Solutions — 72% match"]*

---

### 01:30 – 02:10 | INTELLIGENT MATCHING + APPLICATION (screen record)

**Action: Show results panel**

> "Here are Chidi's matched jobs, sorted by match score. 87%, 79%, 72%."

*[Show JobCard components expanded for the top result]*

> "Look at this 87% match. Nova 2 Lite isn't just scoring it — it's coaching him. He's missing 'Kubernetes' from his skillset, but the model identified that his containerized microservices work is equivalent experience, and tells him exactly how to reframe his resume bullet to pass ATS filters. Without lying. Without fabricating."

*[Highlight the amber "AI Career Coaching" box in the job card]*

> "And it's already written his cover letter. Specific to TechCorp. Not 'I am writing to express my interest.' Watch."

*[Expand cover letter section, scroll through it quickly]*

**Action: Click Apply on the top job**

> "Now let's apply. In a live demo — with a real form."

*[Click Apply button — Nova Act session opens]*

> "Nova Act opens the application page, finds the Apply button, fills in name, email, phone. Uploads the resume using Playwright's file API for reliability. Pastes the cover letter. Answers the screening questions — 'Do you have right to work in Nigeria?' — using the candidate's actual profile data."

*[Show agent feed messages: "Filling personal info..." "Resume uploaded" "Cover letter added" "Answering screening questions..."]*

> "And — review step before submit. Chidi can see everything that was filled. One click to approve."

*[Show the review message in agent feed]*

---

### 02:10 – 02:40 | DASHBOARD + AUDIT TRAIL (screen record)

**Action: Show application tracker / stats**

> "The application tracker shows every job Chidi has applied to — status, match score, confirmation number, which platform. Complete history."

*[Show the 3 stat cards: Jobs Found, Matched, Platforms]*

> "Every session is recorded for audit trail — Nova Act's built-in video recording means Chidi has proof of every application submitted. Useful for follow-ups, useful for disputes."

*[Mention the video recording capability briefly]*

> "And when a CAPTCHA appears — which happens — AutoApply escalates to Chidi via the real-time feed and hands him a direct link to the browser session to solve it. Human-in-the-loop, not a dead end."

---

### 02:40 – 03:00 | CLOSE (voice over)

> "AutoApply: Powered by Amazon Nova Act for browser automation and Nova 2 Lite for intelligent matching. What used to take 40 hours now takes 40 minutes.
>
> For Chidi in Lagos. For developers in Nairobi and Accra and everywhere the job hunting process is stacked against talented people who just need a fair shot.
>
> AutoApply. #AmazonNova."

*[Show final dashboard with multiple matched jobs visible, good match scores, clean UI]*

---

## POST-RECORDING TIPS

1. **Compress to under 200MB** before uploading to Devpost
2. **Add captions** — many judges watch without audio first
3. **Add the hashtag #AmazonNova** visually at the end (not just in description)
4. **Voiceover separately** if screen recording audio is poor — clean narration matters
5. **Pre-record the LinkedIn segment** as a backup in case live demo fails
