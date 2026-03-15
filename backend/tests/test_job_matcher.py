"""
Tests for job_matcher service.
All Bedrock calls are mocked — no AWS costs in CI.
"""

import pytest
import json
import os
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

RESUME_TEXT = """
Senior .NET Developer, 6 years experience.
Skills: C#, ASP.NET Core, PostgreSQL, AWS, Docker, microservices.
Led team of 5 engineers at TechBank Nigeria.
"""

SAMPLE_JOB = {
    "title": "Senior Backend Developer",
    "company": "Fintech Corp",
    "location": "Lagos, Nigeria",
    "requirements": ["C#", ".NET", "PostgreSQL", "5+ years experience"],
    "description": "We are looking for a senior backend developer to join our team.",
}

MATCH_RESPONSE = {
    "match_score": 85,
    "matching_skills": ["C#", ".NET", "PostgreSQL"],
    "skill_gaps": ["Kubernetes"],
    "skill_gap_coaching": "Your Docker experience maps directly to container orchestration. Reframe your microservices bullet to mention 'containerized deployments'.",
    "tailored_summary": "Experienced .NET developer with fintech background perfectly aligned with this role.",
    "recommended_keywords": ["ASP.NET Core", "microservices", "CI/CD"],
    "strengths": ["5+ years .NET", "fintech domain", "team leadership"],
    "should_apply": True,
    "ats_score": 78,
    "experience_match": "perfect",
    "culture_notes": "Fast-paced fintech environment aligns with candidate background.",
}

COVER_LETTER_RESPONSE = """Dear Hiring Manager at Fintech Corp,

Your recent expansion into cross-border payments caught my attention — it aligns directly with the payment gateway work I led at TechBank Nigeria, where I architected APIs processing over 500,000 daily transactions.

Over six years building .NET microservices for the Nigerian fintech sector, I've reduced API latency by 40% and successfully migrated a legacy monolith serving 200k users. The PostgreSQL optimization and gRPC experience listed in your requirements are core parts of my daily toolkit.

I'd welcome the opportunity to discuss how my background maps to your technical roadmap.

Best regards,
John Doe"""


def make_bedrock_response(text: str) -> dict:
    return {"output": {"message": {"content": [{"text": text}]}}}


class TestAnalyzeJobMatch:
    @patch("services.job_matcher.bedrock")
    def test_returns_full_analysis(self, mock_bedrock):
        mock_bedrock.converse.return_value = make_bedrock_response(json.dumps(MATCH_RESPONSE))

        from services.job_matcher import analyze_job_match
        result = analyze_job_match(RESUME_TEXT, SAMPLE_JOB)

        assert result["match_score"] == 85
        assert "C#" in result["matching_skills"]
        assert "Kubernetes" in result["skill_gaps"]
        assert result["should_apply"] is True
        assert len(result["skill_gap_coaching"]) > 10

    @patch("services.job_matcher.bedrock")
    def test_fallback_on_bedrock_error(self, mock_bedrock):
        """Should return safe default dict if Bedrock fails."""
        mock_bedrock.converse.side_effect = Exception("Bedrock unavailable")

        from services.job_matcher import analyze_job_match
        result = analyze_job_match(RESUME_TEXT, SAMPLE_JOB)

        # Should not raise — returns a default dict
        assert isinstance(result, dict)
        assert "match_score" in result
        assert "should_apply" in result

    @patch("services.job_matcher.bedrock")
    def test_strips_markdown_fences(self, mock_bedrock):
        wrapped = f"```json\n{json.dumps(MATCH_RESPONSE)}\n```"
        mock_bedrock.converse.return_value = make_bedrock_response(wrapped)

        from services.job_matcher import analyze_job_match
        result = analyze_job_match(RESUME_TEXT, SAMPLE_JOB)
        assert result["match_score"] == 85

    @patch("services.job_matcher.bedrock")
    def test_extended_thinking_fallback(self, mock_bedrock):
        """Should fall back to standard inference if extended thinking fails."""
        call_count = 0

        def side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if "additionalModelRequestFields" in kwargs:
                raise Exception("Extended thinking not supported")
            return make_bedrock_response(json.dumps(MATCH_RESPONSE))

        mock_bedrock.converse.side_effect = side_effect

        from services.job_matcher import analyze_job_match
        result = analyze_job_match(RESUME_TEXT, SAMPLE_JOB)

        # Should have been called twice (once with thinking, once without)
        assert call_count == 2
        assert result["match_score"] == 85


class TestGenerateCoverLetter:
    @patch("services.job_matcher.bedrock")
    def test_generates_non_empty_letter(self, mock_bedrock):
        mock_bedrock.converse.return_value = make_bedrock_response(COVER_LETTER_RESPONSE)

        from services.job_matcher import generate_cover_letter
        letter = generate_cover_letter(RESUME_TEXT, SAMPLE_JOB, MATCH_RESPONSE)

        assert len(letter) > 100
        assert "Fintech Corp" in letter

    @patch("services.job_matcher.bedrock")
    def test_does_not_contain_banned_phrases(self, mock_bedrock):
        """Cover letter should not contain clichéd openers."""
        mock_bedrock.converse.return_value = make_bedrock_response(COVER_LETTER_RESPONSE)

        from services.job_matcher import generate_cover_letter
        letter = generate_cover_letter(RESUME_TEXT, SAMPLE_JOB, MATCH_RESPONSE)

        banned = ["I am writing to express", "I am writing to apply", "passionate about"]
        for phrase in banned:
            assert phrase.lower() not in letter.lower(), f"Found banned phrase: '{phrase}'"


class TestAnswerScreeningQuestion:
    @patch("services.job_matcher.bedrock")
    def test_answers_work_authorization(self, mock_bedrock):
        mock_bedrock.converse.return_value = make_bedrock_response("Yes")

        from services.job_matcher import answer_screening_question
        user_profile = {"name": "John", "location": "Lagos, Nigeria", "years_experience": 6, "skills": []}
        answer = answer_screening_question(
            "Are you authorized to work in Nigeria?", user_profile, RESUME_TEXT
        )
        assert answer == "Yes"

    @patch("services.job_matcher.bedrock")
    def test_returns_empty_string_on_error(self, mock_bedrock):
        mock_bedrock.converse.return_value = {"output": {"message": {"content": []}}}

        from services.job_matcher import answer_screening_question
        answer = answer_screening_question("Q?", {}, "")
        assert answer == ""
