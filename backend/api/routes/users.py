"""
User management routes.
"""

import uuid
import shutil
import secrets
import logging
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from services.resume_parser import parse_resume
from services.s3_service import upload_resume

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

# Shared in-memory store (imported by main.py)
user_store: dict = {}


def _check_token(user_id: str, token: str):
    """Verify X-User-Token matches the stored token for this user."""
    user = user_store.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not token or user.get("token") != token:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return user


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None


@router.post("")
async def create_user(profile: UserCreate):
    """Create a new user profile."""
    # Check for duplicate email — return existing user with their token
    for uid, u in user_store.items():
        if u.get("email") == profile.email:
            return {"user_id": uid, "token": u.get("token", ""), "message": "Existing user returned"}

    user_id = str(uuid.uuid4())
    token = secrets.token_urlsafe(32)
    try:
        user_store[user_id] = {
            "id": user_id,
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "location": profile.location,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "resume": None,
            "preferences": None,
            "token": token,
        }
        logger.info(f"User created: {user_id}")
        return {"user_id": user_id, "token": token, "message": "User created"}
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        raise HTTPException(500, "Failed to create user profile")


@router.get("/{user_id}")
async def get_user(user_id: str, x_user_token: str = Header(default="")):
    user = _check_token(user_id, x_user_token)
    # Return safe subset — exclude sensitive/internal fields
    return {k: v for k, v in user.items() if k not in ("resume", "token")}


@router.post("/{user_id}/resume")
async def upload_user_resume(user_id: str, file: UploadFile = File(...), x_user_token: str = Header(default="")):
    """Upload and parse a PDF resume with Nova 2 Lite."""
    _check_token(user_id, x_user_token)

    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    # Reject files over 10 MB to prevent DoS
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(400, "Resume file must be under 10 MB")

    file_id = str(uuid.uuid4())[:8]
    safe_name = f"{user_id}_{file_id}.pdf"
    local_path = UPLOAD_DIR / safe_name

    with open(local_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        parsed = parse_resume(str(local_path))
    except Exception as e:
        local_path.unlink(missing_ok=True)
        logger.error(f"Resume parse error for {user_id}: {e}")
        raise HTTPException(500, f"Resume parsing failed: {str(e)}")

    # Upload to S3 (falls back to local if S3 not configured)
    s3_key = upload_resume(str(local_path), user_id, safe_name)

    user_store[user_id]["resume"] = {
        "file_path": str(local_path),
        "s3_key": s3_key,
        "filename": file.filename,
        "parsed": parsed,
        "raw_text": parsed.get("raw_text", ""),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

    # Auto-fill empty profile fields from resume
    for field in ["name", "email", "phone", "location"]:
        if parsed.get(field) and not user_store[user_id].get(field):
            user_store[user_id][field] = parsed[field]

    logger.info(f"Resume uploaded for {user_id}: {len(parsed.get('skills', []))} skills found")

    return {
        "message": "Resume uploaded and parsed successfully",
        "parsed": {k: v for k, v in parsed.items() if k != "raw_text"},
        "skills_found": len(parsed.get("skills", [])),
        "experience_years": parsed.get("years_experience", 0),
    }


@router.post("/{user_id}/preferences")
async def save_user_preferences(user_id: str, prefs: dict, x_user_token: str = Header(default="")):
    """Save job search preferences for a user."""
    _check_token(user_id, x_user_token)
    user_store[user_id]["preferences"] = prefs
    return {"message": "Preferences saved"}


@router.get("/{user_id}/applications")
async def get_user_applications(user_id: str, x_user_token: str = Header(default="")):
    """Get all application sessions for a user."""
    _check_token(user_id, x_user_token)

    try:
        from api.routes.jobs import application_store
        apps = []
        for session_id, session_data in application_store.items():
            if session_data.get("user_id") != user_id:
                continue
            for job in session_data.get("applications", session_data.get("matched_jobs", [])):
                if isinstance(job, dict):
                    apps.append({
                        "session_id": session_id,
                        "title": job.get("title", ""),
                        "company": job.get("company", ""),
                        "platform": job.get("platform", ""),
                        "match_score": job.get("match_score", 0),
                        "status": job.get("status", "matched"),
                        "url": job.get("url", ""),
                        "confirmation": job.get("confirmation_number"),
                        "applied_at": job.get("applied_at"),
                    })
        return {"applications": apps, "total": len(apps)}
    except Exception as e:
        logger.error(f"Applications fetch error: {e}")
        raise HTTPException(500, "Failed to fetch applications")
