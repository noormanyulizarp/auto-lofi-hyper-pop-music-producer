"""Tests for routes/presets.py — preset CRUD endpoints."""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


class TestListPresets:
    """GET /api/v1/music/presets"""

    def test_list_presets_returns_seeded_data(self):
        r = client.get("/api/v1/music/presets")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 10  # app seeds 11 presets
        assert len(data["presets"]) >= 10

    def test_list_presets_structure(self):
        r = client.get("/api/v1/music/presets")
        data = r.json()
        for preset in data["presets"]:
            assert "id" in preset
            assert "name" in preset
            assert "genre" in preset
            assert "mood" in preset
            assert "instruments" in preset
            assert "tags" in preset

    def test_filter_by_genre_lofi(self):
        r = client.get("/api/v1/music/presets", params={"genre": "lofi"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 4  # 4 lofi presets seeded
        for p in data["presets"]:
            assert p["genre"] == "lofi"

    def test_filter_by_genre_hyper_pop(self):
        r = client.get("/api/v1/music/presets", params={"genre": "hyper-pop"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 2
        for p in data["presets"]:
            assert p["genre"] == "hyper-pop"

    def test_filter_by_mood(self):
        r = client.get("/api/v1/music/presets", params={"mood": "chill"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        for p in data["presets"]:
            assert p["mood"] == "chill"

    def test_filter_defaults_only(self):
        r = client.get("/api/v1/music/presets", params={"defaults_only": True})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        for p in data["presets"]:
            assert p["is_default"] is True

    def test_filter_genre_and_mood(self):
        r = client.get("/api/v1/music/presets", params={"genre": "lofi", "mood": "dreamy"})
        assert r.status_code == 200
        data = r.json()
        for p in data["presets"]:
            assert p["genre"] == "lofi"
            assert p["mood"] == "dreamy"

    def test_filter_nonexistent_genre_returns_empty(self):
        r = client.get("/api/v1/music/presets", params={"genre": "nonexistent"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["presets"] == []

    def test_presets_ordered_by_display_order(self):
        r = client.get("/api/v1/music/presets")
        data = r.json()
        orders = [p["display_order"] for p in data["presets"]]
        assert orders == sorted(orders)


class TestGetPreset:
    """GET /api/v1/music/presets/{preset_id}"""

    def test_get_preset_by_id(self):
        # First list to get an ID
        list_r = client.get("/api/v1/music/presets")
        first_preset = list_r.json()["presets"][0]
        preset_id = first_preset["id"]

        r = client.get(f"/api/v1/music/presets/{preset_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == preset_id
        assert data["name"] == first_preset["name"]

    def test_get_preset_not_found(self):
        r = client.get("/api/v1/music/presets/nonexistent-id-999")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()


class TestListGenres:
    """GET /api/v1/music/presets/genres/list"""

    def test_list_genres(self):
        r = client.get("/api/v1/music/presets/genres/list")
        assert r.status_code == 200
        data = r.json()
        assert "genres" in data
        assert len(data["genres"]) >= 1

    def test_genres_have_counts(self):
        r = client.get("/api/v1/music/presets/genres/list")
        data = r.json()
        for entry in data["genres"]:
            assert "genre" in entry
            assert "preset_count" in entry
            assert entry["preset_count"] > 0

    def test_genres_include_all_seeded_genres(self):
        r = client.get("/api/v1/music/presets/genres/list")
        data = r.json()
        genre_names = [g["genre"] for g in data["genres"]]
        expected = ["lofi", "hyper-pop", "ambient", "synthwave", "vaporwave", "chillhop", "trap"]
        for g in expected:
            assert g in genre_names, f"Missing genre: {g}"
