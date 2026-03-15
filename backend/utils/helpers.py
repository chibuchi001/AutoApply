"""
Shared utility functions used across the AutoApply backend.
"""

import re
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


def generate_id(prefix: str = "") -> str:
    """Generate a short unique ID, optionally prefixed."""
    short = str(uuid.uuid4()).replace("-", "")[:12]
    return f"{prefix}{short}" if prefix else short


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from a filename."""
    name = re.sub(r"[^\w\s.-]", "", filename)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:100]  # Limit length


def truncate(text: str, max_len: int = 200, suffix: str = "…") -> str:
    """Truncate text to max_len characters."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def clean_json_text(text: str) -> str:
    """
    Strip markdown code fences from LLM responses before JSON parsing.
    Nova 2 Lite sometimes wraps JSON in ```json ... ``` blocks.
    """
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last fence lines
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def hash_string(s: str) -> str:
    """Return a short deterministic hash of a string (for deduplication)."""
    return hashlib.md5(s.encode()).hexdigest()[:16]


def mask_email(email: str) -> str:
    """Mask an email address for logging: chidi@example.com → c***i@example.com"""
    parts = email.split("@")
    if len(parts) != 2:
        return "***"
    local = parts[0]
    if len(local) <= 2:
        return f"{'*' * len(local)}@{parts[1]}"
    return f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}@{parts[1]}"


def format_salary(amount: Optional[int], currency: str = "₦") -> str:
    """Format a salary number for display."""
    if not amount:
        return "Not specified"
    if amount >= 1_000_000:
        return f"{currency}{amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"{currency}{amount / 1_000:.0f}K"
    return f"{currency}{amount:,}"


def extract_years_from_text(text: str) -> int:
    """
    Extract years of experience from free-form text.
    e.g. "5+ years" → 5, "three years" → 3
    """
    word_map = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    }
    text_lower = text.lower()

    # Numeric: "5+ years", "3-5 years", "5 years"
    match = re.search(r"(\d+)\+?\s*(?:to\s*\d+\s*)?years?", text_lower)
    if match:
        return int(match.group(1))

    # Word form: "five years"
    for word, num in word_map.items():
        if word in text_lower and "year" in text_lower:
            return num

    return 0


def job_url_to_platform(url: str) -> str:
    """Infer platform name from a job URL."""
    if "linkedin.com" in url:
        return "linkedin"
    if "indeed.com" in url:
        return "indeed"
    if "glassdoor.com" in url:
        return "glassdoor"
    return "other"
