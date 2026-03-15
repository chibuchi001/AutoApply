"""
Job matching and cover letter generation service.
Uses Nova 2 Lite via Amazon Bedrock for resume-to-job analysis.
"""

import boto3
import json
import logging
from botocore.config import Config
from config import settings

logger = logging.getLogger(__name__)

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    config=Config(read_timeout=300),
)


def analyze_job_match(resume_text: str, job_listing: dict) -> dict:
    """
    Use Nova 2 Lite to analyze resume-to-job fit and return structured match data.
    """
    prompt = f"""You are an expert career coach and ATS (Applicant Tracking System) specialist.
Analyze the match between this candidate's resume and the job listing.

CANDIDATE RESUME:
{resume_text}

JOB LISTING:
Title: {job_listing.get('title', '')}
Company: {job_listing.get('company', '')}
Location: {job_listing.get('location', '')}
Requirements: {', '.join(job_listing.get('requirements', []))}
Description: {job_listing.get('description', '')[:1000]}

Analyze deeply and return a JSON object with:
{{
  "match_score": number 0-100,
  "matching_skills": ["skills that align well"],
  "skill_gaps": ["skills the candidate is missing"],
  "skill_gap_coaching": "Specific, actionable advice: how can the candidate reframe their EXISTING experience to address each skill gap? Be specific. Mention concrete ways to rephrase resume bullets without lying.",
  "tailored_summary": "2-3 sentence summary emphasizing the candidate's most relevant experience for THIS specific job",
  "recommended_keywords": ["ATS keywords the candidate should include"],
  "strengths": ["top 3 reasons to hire this candidate"],
  "should_apply": true or false (true if match_score >= 60),
  "ats_score": number 0-100 (estimated ATS pass rate based on keyword matching),
  "experience_match": "over/under/perfect",
  "culture_notes": "brief note on company culture fit based on job description"
}}

Return ONLY valid JSON."""

    try:
        response = bedrock.converse(
            modelId=settings.bedrock_model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.2, "maxTokens": 4000},
        )

        content = response["output"]["message"]["content"]
        for item in content:
            if item.get("type") == "text" or "text" in item:
                text = item.get("text", "").strip()
                if not text:
                    continue
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                try:
                    return json.loads(text.strip())
                except json.JSONDecodeError:
                    continue

    except Exception as e:
        logger.error(f"Bedrock job match analysis failed: {e}")

    # Return a safe default if Bedrock is unavailable or parsing fails
    return {
        "match_score": 50,
        "matching_skills": [],
        "skill_gaps": [],
        "skill_gap_coaching": "Unable to analyze at this time.",
        "tailored_summary": "",
        "recommended_keywords": [],
        "strengths": [],
        "should_apply": True,
        "ats_score": 50,
        "experience_match": "unknown",
        "culture_notes": "",
    }


def generate_cover_letter(resume_text: str, job: dict, match_analysis: dict) -> str:
    """
    Generate a tailored, non-generic cover letter using Nova 2 Lite.
    Explicitly avoids clichéd phrases and focuses on concrete value.
    """
    prompt = f"""You are an expert cover letter writer. Write a compelling, tailored cover letter.

CANDIDATE RESUME:
{resume_text[:3000]}

JOB: {job.get('title', '')} at {job.get('company', '')}
Location: {job.get('location', '')}

MATCH ANALYSIS:
- Matching skills: {', '.join(match_analysis.get('matching_skills', []))}
- Keywords to emphasize: {', '.join(match_analysis.get('recommended_keywords', []))}
- Tailored angle: {match_analysis.get('tailored_summary', '')}
- Candidate strengths: {', '.join(match_analysis.get('strengths', []))}

Write a professional 3-paragraph cover letter that:
1. Opens with a SPECIFIC hook about the company or role — NOT "I am writing to express my interest"
2. Paragraph 2: Highlights the 2-3 most relevant experiences with CONCRETE results and numbers
3. Closing: Brief, confident close with a clear call to action

STRICT RULES:
- NEVER use: "I am writing to", "passionate about", "team player", "hard worker", "results-driven"
- Use first person but make it about VALUE to them, not just your history
- Keep it under 350 words
- Sound human, not AI-generated

Return ONLY the cover letter text, no subject line, no extra formatting."""

    try:
        response = bedrock.converse(
            modelId=settings.bedrock_model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.75, "maxTokens": 2000},
        )
        content = response["output"]["message"]["content"]
        for item in content:
            if "text" in item:
                return item["text"].strip()
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")

    return ""


def answer_screening_question(question: str, user_profile: dict, resume_text: str) -> str:
    """
    Generate an appropriate answer to a job application screening question.
    Uses candidate's actual background to answer truthfully.
    """
    prompt = f"""Answer this job application screening question truthfully based on the candidate's profile.

QUESTION: {question}

CANDIDATE PROFILE:
Name: {user_profile.get('name', '')}
Location: {user_profile.get('location', '')}
Years Experience: {user_profile.get('years_experience', '')}
Skills: {', '.join(user_profile.get('skills', [])[:20])}

RESUME EXCERPT:
{resume_text[:1500]}

Rules:
- Answer truthfully based ONLY on information in the profile
- Keep answers concise (1-3 sentences for text questions)
- For yes/no questions, just answer "Yes" or "No"
- For numeric questions (salary, years experience), use real data from profile
- Never fabricate achievements or skills not in the resume

Return ONLY the answer text."""

    try:
        response = bedrock.converse(
            modelId=settings.bedrock_model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.2, "maxTokens": 500},
        )
        content = response["output"]["message"]["content"]
        for item in content:
            if "text" in item:
                return item["text"].strip()
    except Exception as e:
        logger.error(f"Screening question answer failed: {e}")

    return ""
