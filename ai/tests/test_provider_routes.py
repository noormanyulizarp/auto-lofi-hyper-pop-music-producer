"""Tests for routes/provider.py — AI provider CRUD + test endpoint."""

import pytest
import sys
import uuid
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def _unique_name(prefix="prov"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


class TestListProviders:
    """GET /api/v1/providers"""

    def test_list_providers_returns_seeded(self):
        r = client.get("/api/v1/providers")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 3  # openrouter, heartmula, glm-zai
        assert len(data["providers"]) >= 3

    def test_list_providers_structure(self):
        r = client.get("/api/v1/providers")
        for p in r.json()["providers"]:
            assert "id" in p
            assert "name" in p
            assert "display_name" in p
            assert "provider_type" in p
            assert "status" in p

    def test_filter_by_type_llm(self):
        r = client.get("/api/v1/providers", params={"provider_type": "llm"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 2  # openrouter + glm-zai
        for p in data["providers"]:
            assert p["provider_type"] == "llm"

    def test_filter_by_type_music(self):
        r = client.get("/api/v1/providers", params={"provider_type": "music"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        for p in data["providers"]:
            assert p["provider_type"] == "music"

    def test_filter_by_status_active(self):
        r = client.get("/api/v1/providers", params={"status": "active"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 3
        for p in data["providers"]:
            assert p["status"] == "active"

    def test_filter_nonexistent_type(self):
        r = client.get("/api/v1/providers", params={"provider_type": "nonexistent"})
        assert r.status_code == 200
        assert r.json()["total"] == 0


class TestGetProvider:
    """GET /api/v1/providers/{provider_name}"""

    def test_get_openrouter(self):
        r = client.get("/api/v1/providers/openrouter")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "openrouter"
        assert data["display_name"] == "OpenRouter"
        assert data["provider_type"] == "llm"

    def test_get_heartmula(self):
        r = client.get("/api/v1/providers/heartmula")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "heartmula"
        assert data["provider_type"] == "music"
        assert data["supports_music_generation"] is True

    def test_get_glm_zai(self):
        r = client.get("/api/v1/providers/glm-zai")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "glm-zai"

    def test_get_provider_not_found(self):
        r = client.get("/api/v1/providers/nonexistent")
        assert r.status_code == 404


class TestCreateProvider:
    """POST /api/v1/providers"""

    def test_create_provider(self):
        name = _unique_name("test")
        r = client.post("/api/v1/providers", json={
            "name": name,
            "display_name": "Test Provider",
            "provider_type": "llm",
            "api_base_url": "https://api.test.com/v1",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["message"] == "Provider created"
        assert data["provider"]["name"] == name

    def test_create_duplicate_provider_fails(self):
        name = _unique_name("dup")
        client.post("/api/v1/providers", json={
            "name": name,
            "display_name": "Dup Provider",
        })
        r = client.post("/api/v1/providers", json={
            "name": name,
            "display_name": "Dup Provider 2",
        })
        assert r.status_code == 409

    def test_create_provider_with_all_fields(self):
        name = _unique_name("full")
        r = client.post("/api/v1/providers", json={
            "name": name,
            "display_name": "Full Provider",
            "provider_type": "music",
            "api_key": "sk-test-123",
            "api_base_url": "https://api.full.com",
            "models": [{"id": "model-1", "name": "Model One"}],
            "default_model": "model-1",
            "max_tokens": 65536,
            "temperature": 0.5,
            "timeout_seconds": 600,
            "supports_music_generation": True,
            "supports_lyrics_enhancement": True,
            "supports_audio_analysis": True,
            "description": "A full test provider",
            "config_metadata": {"key": "value"},
        })
        assert r.status_code == 200
        provider = r.json()["provider"]
        assert provider["provider_type"] == "music"
        assert provider["max_tokens"] == 65536
        assert provider["temperature"] == 0.5


class TestUpdateProvider:
    """PATCH /api/v1/providers/{provider_name}"""

    def test_update_provider_display_name(self):
        name = _unique_name("upd")
        client.post("/api/v1/providers", json={
            "name": name, "display_name": "Original",
        })
        r = client.patch(f"/api/v1/providers/{name}", json={
            "display_name": "Updated Test Provider",
        })
        assert r.status_code == 200
        assert r.json()["provider"]["display_name"] == "Updated Test Provider"

    def test_update_provider_status(self):
        name = _unique_name("stat")
        client.post("/api/v1/providers", json={
            "name": name, "display_name": "Status Test",
        })
        r = client.patch(f"/api/v1/providers/{name}", json={
            "status": "inactive",
        })
        assert r.status_code == 200
        assert r.json()["provider"]["status"] == "inactive"

    def test_update_nonexistent_provider(self):
        r = client.patch("/api/v1/providers/no-such-provider", json={
            "display_name": "Ghost",
        })
        assert r.status_code == 404

    def test_update_multiple_fields(self):
        name = _unique_name("multi")
        client.post("/api/v1/providers", json={
            "name": name, "display_name": "Multi",
        })
        r = client.patch(f"/api/v1/providers/{name}", json={
            "display_name": "Multi Update",
            "temperature": 0.9,
            "max_tokens": 128000,
        })
        assert r.status_code == 200
        p = r.json()["provider"]
        assert p["display_name"] == "Multi Update"
        assert p["temperature"] == 0.9
        assert p["max_tokens"] == 128000


class TestDeleteProvider:
    """DELETE /api/v1/providers/{provider_name}"""

    def test_delete_provider(self):
        name = _unique_name("del")
        client.post("/api/v1/providers", json={
            "name": name, "display_name": "To Delete",
        })
        r = client.delete(f"/api/v1/providers/{name}")
        assert r.status_code == 200
        assert "deleted" in r.json()["message"]

    def test_delete_nonexistent_provider(self):
        r = client.delete("/api/v1/providers/no-such-provider-del")
        assert r.status_code == 404

    def test_deleted_provider_not_in_list(self):
        name = _unique_name("tmp")
        client.post("/api/v1/providers", json={
            "name": name, "display_name": "Temp",
        })
        client.delete(f"/api/v1/providers/{name}")
        r = client.get("/api/v1/providers")
        names = [p["name"] for p in r.json()["providers"]]
        assert name not in names


class TestTestProvider:
    """POST /api/v1/providers/{provider_name}/test"""

    def test_test_provider_no_base_url(self):
        name = _unique_name("nourl")
        client.post("/api/v1/providers", json={
            "name": name, "display_name": "No URL",
            "api_base_url": None,
        })
        r = client.post(f"/api/v1/providers/{name}/test")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "error"
        assert "No API base URL" in data["message"]

    def test_test_provider_not_found(self):
        r = client.post("/api/v1/providers/nonexistent-provider-test/test")
        assert r.status_code == 404

    def test_test_provider_connection_error(self):
        name = _unique_name("badurl")
        client.post("/api/v1/providers", json={
            "name": name, "display_name": "Bad URL",
            "api_base_url": "http://localhost:99999",
        })
        r = client.post(f"/api/v1/providers/{name}/test")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "error"

    def test_test_provider_success_mock(self):
        """Test the success path by mocking httpx."""
        from unittest import mock
        name = _unique_name("mock")
        client.post("/api/v1/providers", json={
            "name": name,
            "display_name": "Mock Provider",
            "api_base_url": "https://api.mock.com",
            "api_key": "test-key",
        })

        mock_response = mock.MagicMock()
        mock_response.status_code = 200

        with mock.patch("httpx.AsyncClient") as mock_client_cls:
            mock_cm = mock.AsyncMock()
            mock_cm.get = mock.AsyncMock(return_value=mock_response)
            mock_client_cls.return_value.__aenter__ = mock.AsyncMock(return_value=mock_cm)
            mock_client_cls.return_value.__aexit__ = mock.AsyncMock(return_value=False)

            r = client.post(f"/api/v1/providers/{name}/test")
            assert r.status_code == 200
            data = r.json()
            assert data["status"] == "ok"
            assert data["http_status"] == 200

    def test_test_provider_server_error_mock(self):
        """Test the server error path (status >= 500)."""
        from unittest import mock
        name = _unique_name("mock500")
        client.post("/api/v1/providers", json={
            "name": name,
            "display_name": "Mock 500",
            "api_base_url": "https://api.mock500.com",
            "api_key": "test-key",
        })

        mock_response = mock.MagicMock()
        mock_response.status_code = 503

        with mock.patch("httpx.AsyncClient") as mock_client_cls:
            mock_cm = mock.AsyncMock()
            mock_cm.get = mock.AsyncMock(return_value=mock_response)
            mock_client_cls.return_value.__aenter__ = mock.AsyncMock(return_value=mock_cm)
            mock_client_cls.return_value.__aexit__ = mock.AsyncMock(return_value=False)

            r = client.post(f"/api/v1/providers/{name}/test")
            assert r.status_code == 200
            data = r.json()
            assert data["status"] == "error"
            assert data["http_status"] == 503


class TestProviderStats:
    """GET /api/v1/providers/stats/summary"""

    def test_stats_summary(self):
        r = client.get("/api/v1/providers/stats/summary")
        assert r.status_code == 200
        data = r.json()
        assert "total_providers" in data
        assert "by_type" in data
        assert "by_status" in data
        assert "total_requests" in data
        assert data["total_providers"] >= 3

    def test_stats_by_type(self):
        r = client.get("/api/v1/providers/stats/summary")
        data = r.json()
        by_type = data["by_type"]
        assert "llm" in by_type
        assert "music" in by_type
