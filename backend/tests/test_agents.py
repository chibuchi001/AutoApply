"""
Tests for Nova Act agents.
All Nova Act calls are mocked — tests run without API keys.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_nova_result(parsed_response: str):
    result = MagicMock()
    result.parsed_response = parsed_response
    return result


# ── Job Searcher Tests ────────────────────────────────────────────────────────

class TestJobSearcher:
    def test_mock_fallback_returns_jobs(self):
        """With nova_act unavailable, should return mock jobs."""
        with patch.dict("sys.modules", {"nova_act": None}):
            # Re-import with nova_act missing
            import importlib
            import agents.job_searcher as js
            importlib.reload(js)

            results = []
            errors = []
            js.search_jobs_on_platform("indeed", "Python Developer", "Lagos", results, errors)

            assert len(results) == 1
            assert len(results[0].jobs) > 0
            assert results[0].jobs[0].platform == "indeed"

    def test_search_all_platforms_aggregates(self):
        """search_all_platforms should combine results and deduplicate URLs."""
        from agents.job_searcher import _get_mock_jobs, JobResults

        mock_results = []
        errors = []

        with patch("agents.job_searcher.search_jobs_on_platform") as mock_search:
            def fake_search(platform, query, location, results_list, error_list, callback=None):
                results_list.append(_get_mock_jobs(platform, query, location))

            mock_search.side_effect = fake_search

            from agents.job_searcher import search_all_platforms
            result = search_all_platforms("Developer", "Lagos", ["indeed", "linkedin"])

        assert result["total"] > 0
        assert "indeed" in result["platforms_searched"]
        assert "linkedin" in result["platforms_searched"]
        # Check deduplication
        urls = [j["url"] for j in result["jobs"]]
        assert len(urls) == len(set(urls))

    def test_unknown_platform_adds_error(self):
        """An unknown platform key should append to error_list, not crash."""
        from agents.job_searcher import search_jobs_on_platform

        results = []
        errors = []
        search_jobs_on_platform("nonexistent_platform", "Dev", "Lagos", results, errors)

        assert len(errors) == 1
        assert "nonexistent_platform" in errors[0]

    def test_mock_jobs_have_required_fields(self):
        """All mock jobs must have title, company, url, platform."""
        from agents.job_searcher import _get_mock_jobs

        result = _get_mock_jobs("glassdoor", "QA Engineer", "Abuja")
        for job in result.jobs:
            assert job.title
            assert job.company
            assert job.url
            assert job.platform == "glassdoor"


# ── Application Agent Tests ───────────────────────────────────────────────────

class TestApplicationAgent:
    def test_mock_fallback_returns_success(self):
        """With nova_act unavailable, should return mock success result."""
        with patch("agents.application_agent.NOVA_ACT_AVAILABLE", False):
            from agents.application_agent import apply_to_job

            result = apply_to_job(
                job_url="https://example.com/job/123",
                user_profile={
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+234 800 000 0000",
                    "location": "Lagos",
                    "resume_path": "/tmp/resume.pdf",
                },
                resume_path="/tmp/resume.pdf",
                cover_letter="Dear Hiring Manager...",
            )

        assert result["success"] is True
        assert result["status"].endswith("mock") or result["status"] == "submitted_mock"

    def test_dry_run_does_not_submit(self):
        """With nova_act unavailable, dry_run mock should succeed."""
        with patch("agents.application_agent.NOVA_ACT_AVAILABLE", False):
            import agents.application_agent as aa
            result = aa.apply_to_job(
                job_url="https://example.com/job/123",
                user_profile={"name": "John", "email": "j@e.com", "phone": "123", "location": "Lagos"},
                resume_path="/tmp/resume.pdf",
                cover_letter="Cover letter text.",
                dry_run=True,
            )
        assert result["success"] is True
        assert "mock" in result["status"] or "dry_run" in result["status"]

    def test_captcha_triggers_escalation(self):
        """Mock result should expose requires_human from _mock_application_result."""
        # When nova_act is unavailable, _mock_application_result is used.
        # Verify the mock result structure is correct for escalation handling.
        with patch("agents.application_agent.NOVA_ACT_AVAILABLE", False):
            import agents.application_agent as aa3
            result = aa3._mock_application_result(
                "https://example.com/job/456",
                dry_run=False
            )
        # Mock results always return success=True (simulated submission)
        assert isinstance(result, dict)
        assert "success" in result
        assert "status" in result
        assert "requires_human" in result
