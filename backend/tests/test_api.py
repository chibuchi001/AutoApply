"""
Integration tests for FastAPI routes.
Uses TestClient — no real HTTP calls, no AWS costs.
"""

import pytest
import os
import sys
import io
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked external services."""
    # Patch Bedrock and Nova Act before importing main
    with patch("boto3.client"), patch.dict("sys.modules", {"nova_act": MagicMock()}):
        from main import app
        with TestClient(app) as c:
            yield c


@pytest.fixture
def user_id(client):
    """Create a test user and return their ID."""
    response = client.post("/api/users", json={
        "name": "Test User",
        "email": "test@autoapply.test",
        "phone": "+234 800 000 0001",
        "location": "Lagos, Nigeria",
    })
    assert response.status_code == 200
    return response.json()["user_id"]


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestUserRoutes:
    def test_create_user_success(self, client):
        response = client.post("/api/users", json={
            "name": "Chidi Okafor",
            "email": "chidi@test.com",
        })
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert len(data["user_id"]) > 0

    def test_create_user_missing_name(self, client):
        response = client.post("/api/users", json={"email": "no-name@test.com"})
        # Pydantic validation should reject this
        assert response.status_code == 422

    def test_get_user_not_found(self, client):
        response = client.get("/api/users/nonexistent-id")
        assert response.status_code == 404

    def test_get_user_found(self, client, user_id):
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test User"

    def test_duplicate_email_returns_existing(self, client):
        payload = {"name": "Alice", "email": "alice@unique-test.com"}
        r1 = client.post("/api/users", json=payload)
        r2 = client.post("/api/users", json=payload)
        assert r1.status_code == 200
        assert r2.status_code == 200
        # Should return same user_id
        assert r1.json()["user_id"] == r2.json()["user_id"]


class TestResumeUpload:
    def test_upload_requires_pdf(self, client, user_id):
        """Non-PDF file should return 400."""
        files = {"file": ("resume.docx", b"fake content", "application/vnd.openxmlformats")}
        response = client.post(f"/api/users/{user_id}/resume", files=files)
        assert response.status_code == 400

    def test_upload_nonexistent_user(self, client):
        files = {"file": ("resume.pdf", b"%PDF fake", "application/pdf")}
        response = client.post("/api/users/no-such-user/resume", files=files)
        assert response.status_code == 404

    @patch("api.routes.users.parse_resume")
    def test_upload_success(self, mock_parse, client, user_id):
        mock_parse.return_value = {
            "name": "Test User",
            "email": "test@autoapply.test",
            "skills": ["Python", "FastAPI"],
            "technical_skills": ["Python", "FastAPI", "PostgreSQL"],
            "years_experience": 4,
            "raw_text": "Test User resume content...",
        }

        pdf_content = b"%PDF-1.4 fake pdf content"
        files = {"file": ("resume.pdf", pdf_content, "application/pdf")}
        response = client.post(f"/api/users/{user_id}/resume", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["skills_found"] == 2
        assert data["experience_years"] == 4


class TestSearchJobs:
    def test_search_without_resume_returns_400(self, client, user_id):
        response = client.post("/api/search", json={
            "user_id": user_id,
            "query": ".NET Developer",
            "location": "Lagos",
        })
        assert response.status_code == 400
        assert "resume" in response.json()["detail"].lower()

    def test_search_unknown_user_returns_404(self, client):
        response = client.post("/api/search", json={
            "user_id": "ghost-user",
            "query": "Developer",
            "location": "Lagos",
        })
        assert response.status_code == 404


class TestApplicationsTracker:
    def test_returns_empty_list_for_new_user(self, client, user_id):
        response = client.get(f"/api/users/{user_id}/applications")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["applications"] == []
