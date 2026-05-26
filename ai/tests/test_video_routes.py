"""Unit tests for video routes — analyze, upload, status."""

import pytest
import sys
import io
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


class TestVideoAnalyze:
    def test_analyze_youtube_url(self):
        r = client.post("/api/v1/analyze", json={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "extract_audio": True,
            "analyze_patterns": False,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "accepted"
        assert "message" in data

    def test_analyze_default_params(self):
        r = client.post("/api/v1/analyze", json={"url": "https://youtube.com/test"})
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "accepted"
        assert data["audio_extracted"] is False
        assert data["patterns_found"] == 0

    def test_analyze_missing_url(self):
        r = client.post("/api/v1/analyze", json={})
        assert r.status_code == 422  # validation error — url is required


class TestVideoUpload:
    def test_upload_fake_file(self):
        fake_video = io.BytesIO(b"fake video content")
        r = client.post(
            "/api/v1/upload",
            files={"file": ("test.mp4", fake_video, "video/mp4")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "accepted"
        assert data["filename"] == "test.mp4"

    def test_upload_no_file(self):
        r = client.post("/api/v1/upload")
        assert r.status_code == 422  # file is required


class TestVideoStatus:
    def test_get_status(self):
        r = client.get("/api/v1/status/vid-task-123")
        assert r.status_code == 200
        data = r.json()
        assert data["task_id"] == "vid-task-123"
        assert data["status"] == "pending"
