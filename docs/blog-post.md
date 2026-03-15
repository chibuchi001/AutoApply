# How We Used Amazon Nova to Give African Job Seekers the Same Unfair Advantage as Everyone Else

*Published on builder.aws.com · #AmazonNova*

---

## A Wednesday Night in Lagos

It was 11pm on a Wednesday when Tunde, a mid-level .NET developer with six years of fintech experience, sent me a message. He had been job hunting for three months. He had applied to 74 positions. He had received 6 first-round interviews. He was exhausted — not from the interviews, but from the applications.

"I'm spending more time copying my phone number into forms," he wrote, "than I am preparing for actual interviews."

Tunde is not an outlier. He is the rule. Across Nigeria, Ghana, Kenya, and South Africa, a generation of skilled engineers, product managers, and designers is losing dozens of hours every week to the mechanical labour of job applications — hours that candidates in San Francisco or London spend on interview prep, portfolio projects, or simply sleeping.

The tools that exist to solve this problem — resume optimizers, auto-apply extensions, ATS keyword scanners — were built for Western job markets. They struggle with African job board layouts, don't understand local salary ranges, and are priced at $30–$50/month USD for a market where that represents a significant fraction of a monthly salary.

**AutoApply is our attempt to fix that imbalance using Amazon Nova.**

---

## The Numbers Behind the Exhaustion

Before writing a single line of code, we tried to understand the actual scale of the problem.

Based on conversations with job seekers across Lagos, Accra, and Nairobi tech communities:

- A single job application on most platforms takes **25–45 minutes** to complete properly
- The average candidate in the Nigerian tech market submits **60–80 applications** before receiving an offer
- That math produces **25–60 hours of form-filling** per job offer — for a role that may pay less than $1,000/month
- Career coaching services that could help — ATS optimization, interview preparation, cover letter writing — typically cost **$150–$300 per session**, priced entirely out of reach

The problem is not that African developers are less skilled. Studies of diaspora tech workers consistently show comparable or superior performance to local hires in the same roles. The problem is that **the application process itself is a filter with nothing to do with competence** — and candidates with more resources clear it more easily.

A developer in a well-resourced environment might use a tool to auto-apply to 100 jobs in an afternoon. Their counterpart in Lagos is doing it by hand, one form at a time, after a full day of work.

We built AutoApply to erase that gap.

---

## What AutoApply Does — and Why It Matters

AutoApply is an AI agent fleet that handles the full job search pipeline, from discovery to application submission to interview preparation. A candidate uploads their resume once, sets their preferences, and the system takes over.

But the goal was never just speed. The goal was to give every candidate access to the kind of support that used to require either money or connections.

### 1. Parallel Job Search with Nova Act

Nova Act — Amazon's browser automation service — powers AutoApply's job search layer. Three simultaneous browser agents search Indeed, LinkedIn, and Glassdoor at the same time, extracting structured job listings with titles, companies, locations, salaries, and requirements.

What makes Nova Act the right tool here is that African job boards do not have standardised UX. Forms look different on every site, every company career page uses different field names, and layout varies widely even within a single platform across regions. Traditional browser automation tools require brittle site-specific scripts. Nova Act understands form semantics from natural language instructions — the same instruction works across all three boards without custom tuning.

```python
nova.act("Find the job search bar and type 'Senior .NET Developer' then press Enter")
nova.act("Find the location field and set it to 'Lagos, Nigeria'")
nova.act("Filter results to show only jobs posted in the last 7 days if that option exists")
```

### 2. Intelligent Matching with Nova 2 Lite

Finding jobs is easy. Finding the *right* jobs is hard.

AutoApply uses Nova 2 Lite via Amazon Bedrock with a carefully structured prompt that asks the model to reason through the resume and job description before producing a score. The prompt specifies exactly what to analyse — skill overlap, experience level, ATS keyword density — and asks for a structured JSON response with every dimension of the match in a single call.

The depth of the output is possible because the prompt gives Nova 2 Lite full context: the entire resume, the full job description, and explicit instructions to identify connections between existing experience and stated requirements. The result looks like this:

> *"The candidate has six years of ASP.NET Core experience and led a team of five. The role requires 'team leadership' and '.NET microservices' — both directly satisfied. The candidate lacks explicit Kubernetes experience, but their Docker and AWS Lambda work covers the underlying container orchestration concepts. Match score: 82. Recommend applying."*

This is the quality of feedback a senior recruiter or career coach would give. It is available to every candidate, for every job, in seconds.

### 3. Skill Gap Coaching — Career Advice at Scale

The feature that resonates most with users is not the automation. It is the coaching.

When Nova 2 Lite identifies a skill gap, AutoApply does not just flag it. It explains **how to address it honestly using experience the candidate already has**:

> *"You don't have Kubernetes listed, but your microservices work on AWS ECS directly maps to container orchestration. Rephrase your resume bullet from 'Deployed services on AWS' to 'Deployed and orchestrated containerised microservices on AWS ECS, managing service discovery and scaling.' You will pass ATS filters for Kubernetes roles."*

This is what a $200/hr career coach tells you. AutoApply delivers it for every application, personalised to the specific job description, at no marginal cost.

### 4. Tailored Cover Letters — Not Templates

Generic cover letters are worse than no cover letter. AutoApply's cover letter generation uses specific instructions to avoid every cliché:

- No "I am writing to express my interest"
- No "passionate", "team player", "results-driven"
- Opens with a specific hook about the company or role
- Second paragraph uses concrete numbers and outcomes from the candidate's actual experience
- Keeps it under 350 words

The result reads like a letter written by someone who actually researched the company — because the model is given the full job description and the match analysis as context.

### 5. Automated Form Submission

When the candidate approves an application, a Nova Act agent opens the job listing, clicks Apply, fills every field, uploads the resume, answers screening questions using the candidate's real background, and submits. The entire session is visible in a live WebSocket feed — the candidate can watch their agent work in real time.

A human review gate sits before every submission. The candidate sees the filled form before it goes out. For high-stakes applications, this is essential. For routine applications to well-matched roles, it can be disabled.

### 6. Voice Interview Coaching with Nova 2 Sonic

The newest feature addresses the step **after** the application: the interview.

Nova 2 Sonic — Amazon's real-time speech-to-speech model — powers a mock interview coach that activates directly on any matched job. The candidate clicks Practice on a job card, grants microphone access, and Nova 2 Sonic conducts a 4-question mock interview tailored to that specific role and the candidate's resume.

After each answer, the coach gives 1–2 sentences of specific, constructive feedback. After the fourth question, it closes with three personalized coaching tips based on what it actually heard.

This matters enormously for candidates who have never had access to interview coaching. A 9am interview is coming. It is 2am. There is no career coach to call. AutoApply's voice coach is available right now, trained on this exact job description, speaking directly to this candidate's experience.

```
Nova 2 Sonic to candidate:

"Your answer about the payment gateway migration was strong — 
the 40% latency reduction is a memorable number. Next time, lead 
with the business impact before the technical detail. 'We reduced 
checkout abandonment by 12%, which I achieved by cutting API latency 
40%' lands harder than the reverse order."
```

---

## The Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│  CANDIDATE                                              │
│  Browser · Microphone · Resume PDF                      │
└─────────────────────┬───────────────────────────────────┘
                      │ REST + WebSocket
┌─────────────────────▼───────────────────────────────────┐
│  FastAPI BACKEND (Python)                               │
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────────┐ │
│  │ NOVA 2 LITE          │  │ NOVA ACT AGENTS          │ │
│  │ (Amazon Bedrock)     │  │ (Parallel browser fleet) │ │
│  │                      │  │                          │ │
│  │ • Resume parsing     │  │ • Search Indeed          │ │
│  │ • Job match scoring  │  │ • Search LinkedIn        │ │
│  │ • Skill gap coaching │  │ • Search Glassdoor       │ │
│  │ • Cover letters      │  │ • Fill application forms │ │
│  │ • Screening answers  │  │ • Handle file uploads    │ │
│  └──────────────────────┘  │ • Submit & confirm       │ │
│                             └──────────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │ NOVA 2 SONIC (Amazon Bedrock)                    │   │
│  │ Real-time speech-to-speech interview coaching    │   │
│  │ Bidirectional 16kHz PCM audio stream             │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

All three Nova services are used for distinct, non-overlapping purposes. Nova Act handles web interaction tasks where the challenge is reliable UI navigation. Nova 2 Lite handles reasoning and language tasks where the challenge is analysis quality. Nova 2 Sonic handles real-time voice interaction where the challenge is latency and conversational naturalness. None of them could substitute for the others.

---

## Three Things That Surprised Us

**Nova Act's generalisation across form layouts.** We expected to write platform-specific handling for each job board. Instead, the same natural language instructions worked across all three platforms with minimal adjustment. The model understands form *intent*, not DOM structure — which is exactly what you need when you're operating across sites you don't control.

**Nova 2 Lite's coaching quality with structured prompting.** The quality of the skill gap coaching comes down to prompt design. Giving the model the full job description, the full resume, and explicit instructions to identify *bridges* between existing experience and listed requirements — rather than just flagging gaps — produces advice that reads like a career coach wrote it. The model surfaces connections a keyword scan would miss entirely.

**Human-in-the-loop as a trust builder, not a limitation.** We initially designed the review gate as a fallback for edge cases. In testing, candidates consistently preferred having it — not because they didn't trust the automation, but because approving each application felt like being in control of their own job search rather than delegating it blindly. The Nova Act `devtoolsFrontendUrl` makes the handover seamless when the candidate wants to inspect or correct a form before submission.

---

## The Community We're Building For

AutoApply was built with the pan-African tech community explicitly in mind. The mock data uses Nigerian salary ranges. The location defaults to Lagos. The language of the coaching is direct and practical, not corporate.

The path to adoption runs through this community:

**Immediate release**: The code is open source under the MIT licence. Any developer can deploy it with their own AWS credentials. The Nova Act and Bedrock costs at reasonable usage volumes are low enough that a community org or a developer community could run a shared instance.

**Community partnerships**: She Code Africa (10,000+ members), the Andela Learning Community, and the Google Developer Student Clubs across West and East Africa represent direct channels to the candidates this tool was built for. These communities already run job hunt support groups — AutoApply gives those groups a concrete tool to offer.

**African-specific job boards**: Jobberman (Nigeria), BrighterMonday (Kenya/Uganda), Fuzu (East Africa), and Careers24 (South Africa) are currently not in the AutoApply search fleet. The Nova Act agent architecture makes adding them straightforward — each board is a separate thread with its own search instructions. We plan to add all four in the next sprint post-hackathon.

**Pricing for the market**: A commercial tier would be priced in local currency at rates reflecting local purchasing power — not a flat USD price applied globally. Career coaching having a flat global price is how disparities get baked in.

---

## What This Looks Like in Practice

Here is the experience a candidate has today:

1. Upload resume PDF — Nova 2 Lite extracts skills, experience, contact info, and stores it
2. Set job title and location — "Senior .NET Developer, Lagos, Nigeria"
3. Click Search — three Nova Act agents open three browser windows simultaneously
4. Watch the live feed as jobs populate, match scores calculate, and cover letters generate
5. Review matched jobs sorted by fit — see exactly which skills matched and which gaps exist, with specific coaching on each gap
6. Click Apply on approved jobs — Nova Act handles the forms while the candidate preps for the call
7. Click Practice on high-priority jobs — Nova 2 Sonic conducts a role-specific mock interview with live feedback

What took Tunde 45 minutes per application now takes him 45 seconds to approve.

He sent a follow-up message six weeks after we showed him the prototype. He had gone from 6 first-round interviews over three months to 11 first-round interviews in two weeks, with better-matched roles and prepared interview answers.

That is the real metric. Not lines of code or API calls. Whether a skilled developer in Lagos is getting the same shot as someone with the same skills in a better-resourced market.

Amazon Nova made it possible to build all three layers — search automation, intelligent matching, and voice coaching — in a single coherent application. The technology was not the hard part. The hard part was understanding clearly enough what the problem actually was.

---

*Built with Amazon Nova Act, Nova 2 Lite, and Nova 2 Sonic for the Amazon Nova Hackathon 2026.*  
*Code: [https://github.com/chibuchi001/AutoApply.git] · #AmazonNova*

