"""
Orchestrator service.
Manages the full pipeline: search → match → cover letter → apply → track.
Coordinates Nova Act agents and Nova 2 Lite intelligence.
"""

import asyncio
import logging
import uuid
from typing import Optional, Callable
from datetime import datetime

from agents.job_searcher import search_all_platforms
from agents.application_agent import apply_to_job
from services.job_matcher import analyze_job_match, generate_cover_letter
from config import settings

logger = logging.getLogger(__name__)


class ApplicationOrchestrator:
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        self.active_sessions: dict = {}

    async def notify(self, user_id: str, message: dict):
        if self.websocket_manager:
            try:
                await self.websocket_manager.send_to_user(user_id, message)
            except Exception:
                pass
        logger.info(f"[{user_id}] {message.get('type', '')}: {message.get('message', '')}")

    def sync_notify(self, user_id: str, message: dict):
        logger.info(f"[{user_id}] {message.get('type', '')}: {message.get('message', '')}")

    async def run_job_search(
        self,
        user_id: str,
        query: str,
        location: str,
        platforms: list[str],
        resume_text: str,
        min_match_score: int = 60,
    ) -> dict:
        session_id = str(uuid.uuid4())[:8]

        await self.notify(user_id, {
            "type": "search_started",
            "session_id": session_id,
            "message": f"Starting parallel search across {len(platforms)} platforms...",
            "platforms": platforms,
        })

        loop = asyncio.get_running_loop()

        def sync_callback(msg):
            self.sync_notify(user_id, msg)

        search_results = await loop.run_in_executor(
            None,
            lambda: search_all_platforms(query, location, platforms, sync_callback),
        )

        await self.notify(user_id, {
            "type": "search_complete",
            "message": f"Found {search_results['total']} jobs across {len(platforms)} platforms",
            "total_jobs": search_results["total"],
        })

        matched_jobs = []
        jobs = search_results.get("jobs", [])

        await self.notify(user_id, {
            "type": "matching_started",
            "message": f"Analyzing match scores for {len(jobs)} jobs...",
        })

        for i, job in enumerate(jobs):
            try:
                analysis = await loop.run_in_executor(
                    None,
                    lambda j=job: analyze_job_match(resume_text, j),
                )
                job["match_analysis"] = analysis
                job["match_score"] = analysis.get("match_score", 0)
            except Exception as e:
                logger.warning(f"Match analysis failed for {job.get('title', '?')}: {e}")
                # Assign a reasonable default score based on keyword overlap
                job["match_score"] = _estimate_basic_score(resume_text, job)
                job["match_analysis"] = {
                    "match_score": job["match_score"],
                    "matching_skills": [],
                    "skill_gaps": [],
                    "skill_gap_coaching": "Match analysis unavailable — Bedrock quota may be exceeded. Try again later.",
                    "tailored_summary": "",
                    "recommended_keywords": [],
                    "strengths": [],
                    "should_apply": job["match_score"] >= min_match_score,
                    "ats_score": job["match_score"],
                    "experience_match": "unknown",
                    "culture_notes": "",
                }

            await self.notify(user_id, {
                "type": "job_matched",
                "job_title": job["title"],
                "company": job["company"],
                "match_score": job["match_score"],
                "progress": f"{i+1}/{len(jobs)}",
            })

            if job["match_score"] >= min_match_score:
                matched_jobs.append(job)

        matched_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)

        await self.notify(user_id, {
            "type": "matching_complete",
            "message": f"{len(matched_jobs)} jobs above {min_match_score}% match threshold",
            "matched_count": len(matched_jobs),
        })

        return {
            "session_id": session_id,
            "all_jobs": jobs,
            "matched_jobs": matched_jobs,
            "total_found": search_results["total"],
            "errors": search_results.get("errors", []),
        }

    async def prepare_application(
        self,
        user_id: str,
        job: dict,
        resume_text: str,
    ) -> dict:
        await self.notify(user_id, {
            "type": "cover_letter_generating",
            "message": f"Generating tailored cover letter for {job['title']} at {job['company']}...",
        })

        loop = asyncio.get_running_loop()
        match_analysis = job.get("match_analysis", {})

        try:
            cover_letter = await loop.run_in_executor(
                None,
                lambda: generate_cover_letter(resume_text, job, match_analysis),
            )
        except Exception as e:
            logger.warning(f"Cover letter generation failed: {e}")
            cover_letter = _generate_basic_cover_letter(job, resume_text)

        job["cover_letter"] = cover_letter

        await self.notify(user_id, {
            "type": "cover_letter_ready",
            "message": "Cover letter generated",
            "job_title": job["title"],
            "company": job["company"],
        })

        return job

    async def submit_application(
        self,
        user_id: str,
        job: dict,
        user_profile: dict,
        resume_path: str,
        resume_text: str,
        dry_run: bool = False,
        require_review: bool = True,
    ) -> dict:
        if require_review:
            await self.notify(user_id, {
                "type": "pending_review",
                "message": f"Application ready for {job['title']} at {job['company']} — awaiting your approval",
                "job": {
                    "title": job["title"],
                    "company": job["company"],
                    "match_score": job.get("match_score", 0),
                    "cover_letter_preview": job.get("cover_letter", "")[:200],
                },
                "action_required": True,
            })
            return {"status": "pending_review", "job": job}

        await self.notify(user_id, {
            "type": "application_starting",
            "message": f"Applying to {job['title']} at {job['company']}...",
        })

        loop = asyncio.get_running_loop()

        def sync_callback(msg):
            self.sync_notify(user_id, msg)

        result = await loop.run_in_executor(
            None,
            lambda: apply_to_job(
                job_url=job["url"],
                user_profile=user_profile,
                resume_path=resume_path,
                cover_letter=job.get("cover_letter", ""),
                resume_text=resume_text,
                websocket_callback=sync_callback,
                dry_run=dry_run,
            ),
        )

        if result.get("requires_human"):
            await self.notify(user_id, {
                "type": "human_required",
                "message": "Human intervention needed (CAPTCHA or complex form)",
                "devtools_url": result.get("devtools_url"),
                "job": {"title": job["title"], "company": job["company"]},
            })
        elif result.get("success"):
            await self.notify(user_id, {
                "type": "application_submitted",
                "message": f"Successfully applied to {job['title']} at {job['company']}!",
                "confirmation": result.get("confirmation_number"),
                "job": {"title": job["title"], "company": job["company"]},
            })

        result["job"] = job
        return result

    async def run_full_pipeline(
        self,
        user_id: str,
        query: str,
        location: str,
        platforms: list[str],
        resume_text: str,
        user_profile: dict,
        resume_path: str,
        min_match_score: int = 60,
        auto_apply: bool = False,
        max_applications: int = 5,
        dry_run: bool = False,
    ) -> dict:
        search_result = await self.run_job_search(
            user_id=user_id,
            query=query,
            location=location,
            platforms=platforms,
            resume_text=resume_text,
            min_match_score=min_match_score,
        )

        matched_jobs = search_result["matched_jobs"][:max_applications]

        # Generate cover letters
        for i, job in enumerate(matched_jobs):
            matched_jobs[i] = await self.prepare_application(user_id, job, resume_text)

        results = {
            "session_id": search_result["session_id"],
            "total_found": search_result["total_found"],
            "matched_count": len(matched_jobs),
            "applications": [],
        }

        if not auto_apply:
            await self.notify(user_id, {
                "type": "pipeline_complete",
                "message": f"Ready to apply to {len(matched_jobs)} matched jobs. Review and approve each application.",
                "matched_jobs": [
                    {
                        "title": j["title"],
                        "company": j["company"],
                        "match_score": j.get("match_score", 0),
                        "url": j["url"],
                        "platform": j.get("platform", ""),
                    }
                    for j in matched_jobs
                ],
            })
            results["applications"] = matched_jobs
            return results

        for job in matched_jobs:
            app_result = await self.submit_application(
                user_id=user_id,
                job=job,
                user_profile=user_profile,
                resume_path=resume_path,
                resume_text=resume_text,
                dry_run=dry_run,
                require_review=False,
            )
            results["applications"].append(app_result)
            if settings.application_delay_seconds > 0:
                await asyncio.sleep(settings.application_delay_seconds)

        await self.notify(user_id, {
            "type": "pipeline_complete",
            "message": f"Pipeline complete. Applied to {len(results['applications'])} jobs.",
            "total_applications": len(results["applications"]),
        })

        return results


def _estimate_basic_score(resume_text: str, job: dict) -> int:
    """Simple keyword-overlap score when Bedrock is unavailable."""
    resume_lower = resume_text.lower()
    title_words = job.get("title", "").lower().split()
    req_words = [r.lower() for r in job.get("requirements", [])]

    matches = 0
    total = len(title_words) + len(req_words)
    if total == 0:
        return 65

    for word in title_words:
        if word in resume_lower and len(word) > 2:
            matches += 1
    for req in req_words:
        if req in resume_lower:
            matches += 1

    score = int((matches / max(total, 1)) * 100)
    return max(45, min(score, 95))


def _generate_basic_cover_letter(job: dict, resume_text: str) -> str:
    """Simple template cover letter when Bedrock is unavailable."""
    title = job.get("title", "the open position")
    company = job.get("company", "your company")

    return f"""Dear Hiring Team at {company},

Your {title} role caught my attention because it aligns closely with the work I've been doing over the past several years — building full stack applications, working across frontend and backend systems, and shipping products that serve real users.

In my recent work, I've built and deployed web applications using modern stacks including React, Node.js, Python, and cloud infrastructure on AWS. I've worked on fintech platforms processing real transactions, healthcare systems managing sensitive data, and AI-powered products that automate complex workflows. I'm comfortable owning features end-to-end, from database schema design to responsive UI implementation.

I'd welcome the chance to discuss how my experience maps to what you're building at {company}. I'm available for a conversation at your convenience.

Best regards"""