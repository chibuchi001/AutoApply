"""
Nova Act application submission agent.
Fills out and submits job applications on real websites.
Handles different form types, cover letter fields, file uploads, and screening questions.
"""

import logging
import time
from typing import Optional
from pydantic import BaseModel
from config import settings

logger = logging.getLogger(__name__)

try:
    from nova_act import NovaAct
    NOVA_ACT_AVAILABLE = True
except ImportError:
    NOVA_ACT_AVAILABLE = False

from services.job_matcher import answer_screening_question


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ScreeningQuestion(BaseModel):
    question_text: str
    field_type: str  # text, dropdown, radio, checkbox, number
    options: list[str] = []


class ScreeningQuestions(BaseModel):
    questions: list[ScreeningQuestion] = []


class SubmissionResult(BaseModel):
    success: bool
    confirmation_number: Optional[str] = None
    confirmation_message: Optional[str] = None
    requires_human: bool = False
    error: Optional[str] = None
    status: str = "unknown"


# ── Main application agent ────────────────────────────────────────────────────

def apply_to_job(
    job_url: str,
    user_profile: dict,
    resume_path: str,
    cover_letter: str,
    resume_text: str = "",
    websocket_callback=None,
    dry_run: bool = False,  # If True, don't actually submit
) -> dict:
    """
    Nova Act agent that fills out and submits a job application.

    user_profile must contain: name, email, phone, location, years_experience, skills
    """

    def notify(status: str, message: str, data: dict = None):
        if websocket_callback:
            payload = {"type": "application_progress", "status": status, "message": message}
            if data:
                payload.update(data)
            websocket_callback(payload)
        logger.info(f"[Application] {status}: {message}")

    if not NOVA_ACT_AVAILABLE:
        return _mock_application_result(job_url, dry_run)

    try:
        notify("starting", f"Opening job application at {job_url[:60]}...")

        with NovaAct(
            starting_page=job_url,
            headless=False,  # Visible for demo and human oversight
            record_video=True,  # Record for audit trail
            nova_act_api_key=settings.nova_act_api_key,
        ) as nova:

            # ── Step 1: Find Apply button ─────────────────────────────────────
            notify("clicking_apply", "Looking for Apply button...")
            nova.act(
                "Find and click the 'Apply', 'Apply Now', or 'Easy Apply' button on this page. "
                "If there are multiple, click the most prominent one."
            )
            time.sleep(2)

            # ── Step 2: Detect application type ──────────────────────────────
            app_type_result = nova.act(
                "Is this a quick/easy apply form on the current site, "
                "or did it open a new tab or redirect to a company career page? "
                "Return 'quick_apply' if the form is on this page, 'external' if redirected.",
                schema={"type": "string", "enum": ["quick_apply", "external"]},
            )
            app_type = app_type_result.parsed_response or "quick_apply"
            notify("form_detected", f"Detected form type: {app_type}")

            # ── Step 3: Fill personal information ────────────────────────────
            notify("filling_info", "Filling in personal information...")
            nova.act(
                f"Fill in the applicant's name with '{user_profile['name']}'. "
                f"Fill in the email field with '{user_profile['email']}'. "
                f"Fill in the phone number with '{user_profile.get('phone', '')}'. "
                "Skip fields that don't exist."
            )
            time.sleep(0.5)

            # Location/address if present
            if user_profile.get("location"):
                nova.act(
                    f"If there is a location or city field, fill it with '{user_profile.get('location', '')}'. "
                    "Skip if it doesn't exist."
                )

            # ── Step 4: Upload resume ─────────────────────────────────────────
            notify("uploading_resume", "Uploading resume...")
            nova.act("Find the resume upload button or area and click it if it exists")
            time.sleep(0.5)

            try:
                # Use Playwright directly for reliable file upload
                nova.page.set_input_files('input[type="file"]', resume_path)
                time.sleep(1)
                notify("resume_uploaded", "Resume uploaded successfully")
            except Exception as e:
                logger.warning(f"Direct file upload failed: {e}. Trying Nova Act approach.")
                nova.act(f"Upload the resume file. The file path is {resume_path}")

            # ── Step 5: Cover letter ──────────────────────────────────────────
            notify("cover_letter", "Adding cover letter...")
            cover_letter_type = nova.act(
                "Check if there is a cover letter section. "
                "Return 'text_field' if there's a text area to type/paste, "
                "'upload' if there's a file upload for cover letter, "
                "'none' if there's no cover letter section.",
                schema={"type": "string", "enum": ["text_field", "upload", "none"]},
            )

            cl_type = cover_letter_type.parsed_response
            if cl_type == "text_field":
                nova.act(
                    f"Find the cover letter text area and paste this text into it:\n\n{cover_letter}"
                )
                notify("cover_letter_added", "Cover letter pasted")
            elif cl_type == "upload":
                # Would need to save cover letter to temp file first
                notify("cover_letter_skipped", "Cover letter upload field found but skipping for now")

            # ── Step 6: Screening questions ───────────────────────────────────
            notify("screening_questions", "Checking for screening questions...")
            questions_result = nova.act(
                "Look for any screening or qualifying questions on this page. "
                "These might be about work authorization, years of experience, "
                "salary expectations, availability, or role-specific skills. "
                "Extract all questions you can see along with their field types.",
                schema=ScreeningQuestions.model_json_schema(),
            )

            if questions_result.parsed_response:
                try:
                    screening_data = ScreeningQuestions.model_validate_json(
                        questions_result.parsed_response
                    )
                    for q in screening_data.questions:
                        answer = answer_screening_question(
                            q.question_text, user_profile, resume_text
                        )
                        nova.act(
                            f"For the question '{q.question_text}', "
                            f"provide this answer: '{answer}'. "
                            "Select the appropriate option if it's a dropdown or radio button."
                        )
                        time.sleep(0.3)
                    notify("screening_complete", f"Answered {len(screening_data.questions)} screening questions")
                except Exception as e:
                    logger.warning(f"Screening question parsing failed: {e}")

            # ── Step 7: CAPTCHA check ─────────────────────────────────────────
            captcha_result = nova.act(
                "Is there a CAPTCHA, 'I am not a robot' checkbox, or verification puzzle visible? "
                "Return 'yes' or 'no'.",
                schema={"type": "string", "enum": ["yes", "no"]},
            )

            if captcha_result.parsed_response == "yes":
                notify(
                    "captcha_detected",
                    "CAPTCHA detected — human review required",
                    {"requires_human": True, "devtools_url": nova.devtools_frontend_url},
                )
                return {
                    "success": False,
                    "requires_human": True,
                    "devtools_url": nova.devtools_frontend_url,
                    "status": "captcha_escalation",
                    "error": "CAPTCHA requires human intervention",
                }

            # ── Step 8: Review ────────────────────────────────────────────────
            notify("reviewing", "Reviewing application before submit...")
            nova.act(
                "Scroll through the entire application form from top to bottom "
                "to verify all required fields are filled in correctly."
            )
            time.sleep(1)

            # ── Step 9: Submit or dry run ─────────────────────────────────────
            if dry_run:
                notify("dry_run", "Dry run mode — NOT submitting")
                return {
                    "success": True,
                    "requires_human": False,
                    "status": "dry_run_complete",
                    "confirmation_message": "Dry run completed — form was filled but not submitted",
                }

            notify("submitting", "Submitting application...")
            nova.act(
                "Click the Submit, Send Application, or Apply button to submit the application. "
                "Only click once."
            )
            time.sleep(3)

            # ── Step 10: Confirm ──────────────────────────────────────────────
            confirmation_result = nova.act(
                "Check if the application was submitted successfully. "
                "Look for a confirmation message, thank you page, or confirmation number. "
                "Return a JSON with 'success' (boolean), 'confirmation_number' (string or null), "
                "'confirmation_message' (the text you see).",
                schema=SubmissionResult.model_json_schema(),
            )

            result = SubmissionResult.model_validate_json(confirmation_result.parsed_response)
            notify(
                "submitted",
                f"Application submitted! Confirmation: {result.confirmation_number or 'N/A'}",
            )

            return {
                "success": result.success,
                "confirmation_number": result.confirmation_number,
                "confirmation_message": result.confirmation_message,
                "requires_human": False,
                "status": "submitted",
            }

    except Exception as e:
        logger.error(f"Application agent error: {e}")
        notify("error", f"Application failed: {str(e)[:200]}")
        return {
            "success": False,
            "error": str(e),
            "status": "error",
            "requires_human": True,
        }


def _mock_application_result(job_url: str, dry_run: bool) -> dict:
    """Mock result when Nova Act is not available."""
    import random
    time.sleep(2)  # Simulate processing time
    return {
        "success": True,
        "confirmation_number": f"APP-{random.randint(100000, 999999)}",
        "confirmation_message": "Your application has been submitted successfully! (MOCK)",
        "requires_human": False,
        "status": "submitted_mock",
    }
