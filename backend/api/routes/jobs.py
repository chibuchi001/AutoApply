"""
Job search and application routes.
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from services.orchestrator import ApplicationOrchestrator
from api.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["jobs"])

# Shared stores (referenced by users.py too)
application_store: dict = {}

orchestrator = ApplicationOrchestrator(ws_manager)


class JobSearchRequest(BaseModel):
    user_id: str
    query: str
    location: str
    platforms: list[str] = ["indeed", "linkedin", "glassdoor"]
    min_match_score: int = 60
    auto_apply: bool = False
    max_applications: int = 5
    dry_run: bool = True


class ApplyJobRequest(BaseModel):
    user_id: str
    job: dict
    dry_run: bool = True


class MatchJobRequest(BaseModel):
    resume_text: str
    job: dict


@router.post("/search")
async def search_jobs(request: JobSearchRequest, x_user_token: str = Header(default="")):
    from api.routes.users import user_store, _check_token

    user = _check_token(request.user_id, x_user_token)

    resume = user.get("resume")
    if not resume:
        raise HTTPException(400, "Please upload a resume before searching")

    resume_text = resume.get("raw_text", "")
    resume_path = resume.get("file_path", "")

    user_profile = {
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "phone": user.get("phone", ""),
        "location": user.get("location", request.location),
        "years_experience": resume.get("parsed", {}).get("years_experience", 0),
        "skills": resume.get("parsed", {}).get("skills", []),
        "resume_path": resume_path,
    }

    result = await orchestrator.run_full_pipeline(
        user_id=request.user_id,
        query=request.query,
        location=request.location,
        platforms=request.platforms,
        resume_text=resume_text,
        user_profile=user_profile,
        resume_path=resume_path,
        min_match_score=request.min_match_score,
        auto_apply=request.auto_apply,
        max_applications=request.max_applications,
        dry_run=request.dry_run,
    )

    session_id = result.get("session_id", "")
    application_store[session_id] = result
    application_store[session_id]["user_id"] = request.user_id

    matched = result.get("applications", result.get("matched_jobs", []))

    return {
        "session_id": session_id,
        "total_found": result.get("total_found", 0),
        "matched_count": result.get("matched_count", 0),
        "message": f"Found {result.get('total_found', 0)} jobs, "
                   f"{result.get('matched_count', 0)} matched your criteria",
        "matched_jobs": [
            {
                "title": j.get("title"),
                "company": j.get("company"),
                "location": j.get("location"),
                "salary_range": j.get("salary_range"),
                "platform": j.get("platform", ""),
                "url": j.get("url"),
                "posted_date": j.get("posted_date"),
                "match_score": j.get("match_score", 0),
                "matching_skills": j.get("match_analysis", {}).get("matching_skills", []),
                "skill_gaps": j.get("match_analysis", {}).get("skill_gaps", []),
                "skill_gap_coaching": j.get("match_analysis", {}).get("skill_gap_coaching", ""),
                "recommended_keywords": j.get("match_analysis", {}).get("recommended_keywords", []),
                "cover_letter": j.get("cover_letter", ""),
                "strengths": j.get("match_analysis", {}).get("strengths", []),
                "ats_score": j.get("match_analysis", {}).get("ats_score", 0),
            }
            for j in matched if isinstance(j, dict)
        ],
    }


@router.post("/apply")
async def apply_to_job(request: ApplyJobRequest, x_user_token: str = Header(default="")):
    from api.routes.users import user_store, _check_token

    user = _check_token(request.user_id, x_user_token)

    resume = user.get("resume")
    if not resume:
        raise HTTPException(400, "Resume required before applying")

    user_profile = {
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "phone": user.get("phone", ""),
        "location": user.get("location", ""),
        "resume_path": resume.get("file_path", ""),
        "years_experience": resume.get("parsed", {}).get("years_experience", 0),
        "skills": resume.get("parsed", {}).get("skills", []),
    }

    result = await orchestrator.submit_application(
        user_id=request.user_id,
        job=request.job,
        user_profile=user_profile,
        resume_path=resume.get("file_path", ""),
        resume_text=resume.get("raw_text", ""),
        dry_run=request.dry_run,
        require_review=False,
    )

    return result


@router.post("/analyze-match")
async def analyze_match(request: MatchJobRequest):
    from services.job_matcher import analyze_job_match
    try:
        loop = asyncio.get_running_loop()
        analysis = await loop.run_in_executor(
            None,
            lambda: analyze_job_match(request.resume_text, request.job),
        )
        return analysis
    except Exception as e:
        logger.error(f"Match analysis error: {e}")
        raise HTTPException(500, f"Match analysis failed: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = application_store.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session