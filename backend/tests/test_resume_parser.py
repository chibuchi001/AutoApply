"""
Tests for resume_parser service.
Uses mocked Bedrock responses to avoid AWS costs during CI.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open

# Add backend root to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_RESUME_TEXT = """
John Doe
john.doe@example.com | +234 801 234 5678 | Lagos, Nigeria

SUMMARY
Senior .NET Developer with 6 years of experience in fintech.

EXPERIENCE
TechBank Nigeria — Lead Developer (2021–2024)
  - Built ASP.NET Core APIs serving 500k daily transactions
  - Migrated monolith to microservices on AWS

SKILLS
C#, .NET, ASP.NET Core, PostgreSQL, SQL Server, Docker, AWS, gRPC, REST APIs

EDUCATION
University of Lagos — BSc Computer Science (2017)
"""

SAMPLE_PARSED_RESPONSE = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+234 801 234 5678",
    "location": "Lagos, Nigeria",
    "summary": "Senior .NET Developer with 6 years of experience in fintech.",
    "years_experience": 6,
    "skills": ["C#", ".NET", "ASP.NET Core", "PostgreSQL", "AWS"],
    "technical_skills": ["C#", ".NET Core", "PostgreSQL", "SQL Server", "Docker", "AWS", "gRPC"],
    "soft_skills": ["leadership", "communication"],
    "experience": [
        {
            "company": "TechBank Nigeria",
            "title": "Lead Developer",
            "duration": "2021-2024",
            "highlights": ["Built ASP.NET Core APIs", "Migrated to microservices"]
        }
    ],
    "education": [
        {
            "institution": "University of Lagos",
            "degree": "BSc Computer Science",
            "year": "2017"
        }
    ],
    "certifications": [],
    "languages": ["English"],
    "linkedin_url": None,
    "github_url": None,
    "portfolio_url": None
}


def make_bedrock_response(content: dict) -> dict:
    """Build a mock Bedrock converse() response."""
    return {
        "output": {
            "message": {
                "content": [{"text": json.dumps(content)}]
            }
        }
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestExtractTextFromPdf:
    def test_extracts_text_from_valid_pdf(self, tmp_path):
        """Should extract text from a real PDF file."""
        from services.resume_parser import extract_text_from_pdf

        # Create a minimal valid PDF using reportlab if available, else skip
        pytest.importorskip("reportlab")
        from reportlab.pdfgen import canvas

        pdf_path = str(tmp_path / "test_resume.pdf")
        c = canvas.Canvas(pdf_path)
        c.drawString(100, 750, "John Doe — Software Engineer")
        c.save()

        text = extract_text_from_pdf(pdf_path)
        assert "John Doe" in text

    def test_raises_on_missing_file(self):
        from services.resume_parser import extract_text_from_pdf
        with pytest.raises(Exception):
            extract_text_from_pdf("/nonexistent/path/resume.pdf")


class TestParseResumeWithNova:
    @patch("services.resume_parser.bedrock")
    def test_returns_structured_data(self, mock_bedrock):
        """Should parse resume text into structured dict."""
        mock_bedrock.converse.return_value = make_bedrock_response(SAMPLE_PARSED_RESPONSE)

        from services.resume_parser import parse_resume_with_nova
        result = parse_resume_with_nova(SAMPLE_RESUME_TEXT)

        assert result["name"] == "John Doe"
        assert result["email"] == "john.doe@example.com"
        assert result["years_experience"] == 6
        assert "C#" in result["skills"]

    @patch("services.resume_parser.bedrock")
    def test_handles_markdown_wrapped_json(self, mock_bedrock):
        """Should strip ```json ... ``` fences if Bedrock wraps output."""
        wrapped = f"```json\n{json.dumps(SAMPLE_PARSED_RESPONSE)}\n```"
        mock_bedrock.converse.return_value = {
            "output": {"message": {"content": [{"text": wrapped}]}}
        }

        from services.resume_parser import parse_resume_with_nova
        result = parse_resume_with_nova(SAMPLE_RESUME_TEXT)
        assert result["name"] == "John Doe"

    @patch("services.resume_parser.bedrock")
    def test_raises_on_empty_response(self, mock_bedrock):
        """Should raise ValueError when Bedrock returns no text content."""
        mock_bedrock.converse.return_value = {
            "output": {"message": {"content": []}}
        }

        from services.resume_parser import parse_resume_with_nova
        with pytest.raises(ValueError):
            parse_resume_with_nova(SAMPLE_RESUME_TEXT)


class TestParseResume:
    @patch("services.resume_parser.bedrock")
    @patch("services.resume_parser.extract_text_from_pdf")
    def test_full_pipeline(self, mock_extract, mock_bedrock):
        """Full pipeline: PDF path → structured data with raw_text."""
        mock_extract.return_value = SAMPLE_RESUME_TEXT
        mock_bedrock.converse.return_value = make_bedrock_response(SAMPLE_PARSED_RESPONSE)

        from services.resume_parser import parse_resume
        result = parse_resume("/fake/path/resume.pdf")

        assert result["name"] == "John Doe"
        assert result["raw_text"] == SAMPLE_RESUME_TEXT
        mock_extract.assert_called_once_with("/fake/path/resume.pdf")
