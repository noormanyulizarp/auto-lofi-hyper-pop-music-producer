"""Unit tests for music routes — generate, status, genres, history, download."""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


class TestRootAndHealth:
    def test_root_returns_service_info(self):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["service"] == "Auto LoFi Hyper Pop Music Producer AI"
        assert data["version"] == "0.1.0"
        assert "endpoints" in data

    def test_health_check(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"


class TestGenerateMusic:
    def test_generate_default(self):
        r = client.post("/api/v1/generate", json={})
        assert r.status_code == 200
        data = r.json()
        assert "task_id" in data
        # HeartMuLa fallback returns completed status
        assert data["status"] == "completed"
        assert data["genre"] == "lofi"  # default genre
        assert data["mood"] == "chill"  # default mood
        assert data["duration"] == 30

    def test_generate_with_params(self):
        r = client.post("/api/v1/generate", json={
            "title": "My Track",
            "genre": "hyper-pop",
            "mood": "energetic",
            "duration": 60,
            "tempo": 140,
            "key": "C major",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "My Track"
        assert data["genre"] == "hyper-pop"
        assert data["mood"] == "energetic"
        assert data["duration"] == 60

    def test_generate_duration_too_short(self):
        r = client.post("/api/v1/generate", json={"duration": 5})
        assert r.status_code == 400

    def test_generate_duration_too_long(self):
        r = client.post("/api/v1/generate", json={"duration": 700})
        assert r.status_code == 400

    def test_generate_task_id_unique(self):
        r1 = client.post("/api/v1/generate", json={})
        r2 = client.post("/api/v1/generate", json={})
        assert r1.json()["task_id"] != r2.json()["task_id"]

    def test_generate_all_genres(self):
        genres = ["lofi", "hyper-pop", "ambient", "synthwave", "trap", "chillhop", "vaporwave"]
        for genre in genres:
            r = client.post("/api/v1/generate", json={"genre": genre})
            assert r.status_code == 200, f"Genre {genre} failed"
            assert r.json()["genre"] == genre

    def test_generate_all_moods(self):
        moods = ["chill", "energetic", "melancholic", "upbeat", "dark", "dreamy"]
        for mood in moods:
            r = client.post("/api/v1/generate", json={"mood": mood})
            assert r.status_code == 200, f"Mood {mood} failed"
            assert r.json()["mood"] == mood

    def test_generate_invalid_genre(self):
        r = client.post("/api/v1/generate", json={"genre": "death-metal"})
        assert r.status_code == 422  # validation error

    def test_generate_invalid_mood(self):
        r = client.post("/api/v1/generate", json={"mood": "rage"})
        assert r.status_code == 422

    def test_generate_returns_tags_and_lyrics(self):
        r = client.post("/api/v1/generate", json={"title": "Test Track"})
        data = r.json()
        assert "tags" in data
        assert "lyrics" in data
        assert "lofi" in data["tags"]

    def test_generate_with_instruments(self):
        r = client.post("/api/v1/generate", json={
            "instruments": ["piano", "guitar"]
        })
        assert r.status_code == 200
        data = r.json()
        assert "piano" in data["tags"]
        assert "guitar" in data["tags"]

    def test_generate_with_prompt(self):
        r = client.post("/api/v1/generate", json={
            "title": "Sunset Drive",
            "prompt": "A chill sunset drive along the coast",
        })
        assert r.status_code == 200
        data = r.json()
        assert "chill sunset drive" in data["lyrics"].lower()


class TestGenresEndpoint:
    def test_list_genres(self):
        r = client.get("/api/v1/genres")
        assert r.status_code == 200
        data = r.json()
        assert "genres" in data
        assert "moods" in data
        assert len(data["genres"]) == 7
        assert len(data["moods"]) == 6

    def test_genres_include_lofi(self):
        r = client.get("/api/v1/genres")
        assert "lofi" in r.json()["genres"]

    def test_moods_include_chill(self):
        r = client.get("/api/v1/genres")
        assert "chill" in r.json()["moods"]


class TestStatusEndpoint:
    def test_get_status_after_generate(self):
        """Generate a track first, then check its status."""
        gen = client.post("/api/v1/generate", json={"title": "Status Test"})
        task_id = gen.json()["task_id"]

        r = client.get(f"/api/v1/status/{task_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["task_id"] == task_id
        assert data["status"] == "completed"

    def test_get_status_not_found(self):
        """Unknown task_id should return 404."""
        r = client.get("/api/v1/status/nonexistent-task-999")
        assert r.status_code == 404


class TestDownloadEndpoint:
    def test_download_existing_task(self):
        """Generate first, then try to download."""
        gen = client.post("/api/v1/generate", json={"title": "Download Test"})
        task_id = gen.json()["task_id"]

        r = client.get(f"/api/v1/download/{task_id}")
        # Fallback mode returns JSON (no actual audio file)
        assert r.status_code == 200

    def test_download_not_found(self):
        r = client.get("/api/v1/download/nonexistent-task-999")
        assert r.status_code == 404


class TestHistoryEndpoint:
    def test_history_not_empty_after_generate(self):
        """After generating tracks, history should have entries."""
        # Generate a track to ensure history has data
        client.post("/api/v1/generate", json={"title": "History Test Track"})

        r = client.get("/api/v1/history")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_history_with_params(self):
        r = client.get("/api/v1/history?limit=10&offset=0")
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "items" in data
