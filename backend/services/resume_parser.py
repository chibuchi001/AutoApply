"""
Resume parsing service.
Extracts text from PDF resumes and uses Nova 2 Lite to parse structured data.
Falls back to regex-based parsing when Bedrock is unavailable or throttled.
"""

import re
import pdfplumber
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
    config=Config(read_timeout=120),
)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from a PDF resume using pdfplumber."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    full_text = "\n\n".join(text_parts)
    logger.info(f"Extracted {len(full_text)} characters from PDF")
    return full_text


def _basic_parse(raw_text: str) -> dict:
    """
    Fallback parser using regex when Bedrock is unavailable.
    Extracts basic info from resume text without any AI model.
    """
    text_lower = raw_text.lower()

    # Extract email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', raw_text)
    email = email_match.group(0) if email_match else ""

    # Extract phone
    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,15}', raw_text)
    phone = phone_match.group(0).strip() if phone_match else ""

    # Extract name (first non-empty line that isn't an email/phone)
    name = ""
    for line in raw_text.split("\n"):
        line = line.strip()
        if line and not "@" in line and not re.match(r'^[\d\+\-\(\)\s]+$', line) and len(line) < 60:
            name = line
            break

    # Common tech skills to look for
    skill_keywords = [
        "python", "javascript", "typescript", "react", "node.js", "nodejs", "next.js",
        "fastapi", "django", "flask", "express", "vue", "angular", "svelte",
        "html", "css", "tailwind", "bootstrap",
        "postgresql", "mysql", "mongodb", "redis", "sqlite",
        "aws", "s3", "ec2", "lambda", "bedrock", "docker", "kubernetes", "ci/cd",
        "git", "github", "linux", "rest api", "graphql", "websocket",
        "solidity", "rust", "c++", "c#", ".net", "java", "go", "golang",
        "smart contract", "blockchain", "ethereum", "web3",
        "machine learning", "ai", "deep learning", "tensorflow", "pytorch",
        "agile", "scrum", "jira", "figma",
    ]
    found_skills = []
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.title() if len(skill) > 3 else skill.upper())

    # Estimate years of experience
    years = 0
    year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)?', text_lower)
    if year_matches:
        years = max(int(y) for y in year_matches)

    # Extract location hints
    location = ""
    location_patterns = [
        r'(lagos|abuja|port harcourt|owerri|nairobi|accra|kano|ibadan|enugu)[,\s]*(nigeria|kenya|ghana)?',
        r'(nigeria|kenya|ghana|south africa|remote)',
    ]
    for pattern in location_patterns:
        loc_match = re.search(pattern, text_lower)
        if loc_match:
            location = loc_match.group(0).title()
            break

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "summary": f"Professional with experience in {', '.join(found_skills[:5])}." if found_skills else "",
        "years_experience": years if years else 3,
        "skills": found_skills,
        "technical_skills": found_skills,
        "soft_skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "languages": ["English"],
        "linkedin_url": None,
        "github_url": None,
        "portfolio_url": None,
    }


def parse_resume_with_nova(raw_text: str) -> dict:
    """
    Use Nova 2 Lite to extract structured data from resume text.
    """
    prompt = f"""You are a professional resume parser. Extract structured information from this resume.

RESUME TEXT:
{raw_text[:4000]}

Return a JSON object with exactly these fields:
{{
  "name": "Full name",
  "email": "email address",
  "phone": "phone number",
  "location": "city, country",
  "summary": "2-3 sentence professional summary",
  "years_experience": number,
  "skills": ["skill1", "skill2"],
  "technical_skills": ["specific tech skills"],
  "soft_skills": ["communication", "leadership"],
  "experience": [{{"company": "Name", "title": "Title", "duration": "2021-2023", "highlights": ["achievement"]}}],
  "education": [{{"institution": "University", "degree": "BSc", "year": "2024"}}],
  "certifications": [],
  "languages": ["English"],
  "linkedin_url": null,
  "github_url": null,
  "portfolio_url": null
}}

Return ONLY valid JSON."""

    response = bedrock.converse(
        modelId=settings.bedrock_model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"temperature": 0.1, "maxTokens": 3000},
    )

    content = response["output"]["message"]["content"]
    for item in content:
        if "text" in item:
            text = item["text"].strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())

    raise ValueError("No text content in Bedrock response")


def parse_resume(pdf_path: str) -> dict:
    """Full pipeline: PDF → text → structured data. Falls back to basic parsing."""
    raw_text = extract_text_from_pdf(pdf_path)

    # Try Nova 2 Lite first
    try:
        parsed = parse_resume_with_nova(raw_text)
        logger.info(f"Resume parsed with Nova 2 Lite: {len(parsed.get('skills', []))} skills found")
    except Exception as e:
        logger.warning(f"Nova resume parsing failed, using basic parser: {e}")
        parsed = _basic_parse(raw_text)
        logger.info(f"Basic parser found {len(parsed.get('skills', []))} skills")

    parsed["raw_text"] = raw_text
    return parsed