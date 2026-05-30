# TDD Implementation Plan — Integration & E2E Tests

> **For Hermes:** Follow test-driven-development skill. RED-GREEN-REFACTOR cycle for every test.
> **Project:** Auto LoFi Hyper Pop Music Producer
> **Date:** 2026-05-30

**Goal:** Build integration and E2E tests to validate all features pass before moving to Phase 3.

**Current state:** 184 unit tests passing. Zero integration tests. Zero E2E tests.

**Tech Stack:** pytest + FastAPI TestClient + httpx

---

## Phase A: Integration Tests (API → Database)

### Task A.1: Create integration test infrastructure

**Files:**
- Create: `ai/tests/integration/__init__.py`
- Create: `ai/tests/integration/conftest.py`

**Step 1: Write conftest with TestClient fixture**

```python
# ai/tests/integration/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from models.database import Base
from services.database import get_db
from app.main import app

# In-memory SQLite for testing
TEST_DB_URL = "sqlite:///file:test?mode=memory&cache=shared&uri=true"
test_engine = create_engine(
    TEST_DB_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: Verify infrastructure loads**

Run: `cd ai && source .venv/bin/activate && python -c "from tests.integration.conftest import client; print('OK')"`
Expected: OK

**Step 3: Commit**

```bash
git add ai/tests/integration/
git commit -m "test: add integration test infrastructure (conftest, TestClient)"
```

---

### Task A.2: Integration test — Health & Root endpoints

**Files:**
- Create: `ai/tests/integration/test_health_integration.py`

**Step 1: Write failing tests**

```python
# ai/tests/integration/test_health_integration.py
"""Integration tests for health and root endpoints."""

class TestRootEndpoint:
    def test_root_returns_service_info(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "Auto LoFi Hyper Pop Music Producer AI"
        assert data["version"] == "0.1.0"
        assert "endpoints" in data

    def test_root_has_all_endpoint_links(self, client):
        resp = client.get("/")
        data = resp.json()
        endpoints = data["endpoints"]
        assert "music" in endpoints
        assert "provider" in endpoints
        assert "docs" in endpoints
        assert "health" in endpoints


class TestHealthEndpoint:
    def test_health_returns_healthy(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_health_has_version(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert "version" in data
```

**Step 2: Run — verify GREEN (these endpoints already exist)**

Run: `cd ai && source .venv/bin/activate && pytest tests/integration/test_health_integration.py -v`
Expected: PASS (infrastructure validation)

**Step 3: Commit**

```bash
git add ai/tests/integration/test_health_integration.py
git commit -m "test(integration): health and root endpoint tests"
```

---

### Task A.3: Integration test — Provider CRUD workflow

**Files:**
- Create: `ai/tests/integration/test_provider_integration.py`

**Step 1: Write failing tests**

```python
"""Integration tests for provider CRUD — full request/response cycle."""

class TestProviderCRUDIntegration:
    def test_create_and_get_provider(self, client):
        # Create
        resp = client.post("/api/v1/providers", json={
            "name": "test-provider",
            "display_name": "Test Provider",
            "provider_type": "llm",
            "api_key": "test-key",
            "api_base_url": "https://api.test.com",
        })
        assert resp.status_code in (200, 201)
        data = resp.json()
        provider_id = data["id"]

        # Get
        resp = client.get(f"/api/v1/providers/{provider_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "test-provider"

    def test_list_providers_after_create(self, client):
        client.post("/api/v1/providers", json={
            "name": "list-test",
            "display_name": "List Test",
            "provider_type": "music",
        })
        resp = client.get("/api/v1/providers")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    def test_update_provider(self, client):
        resp = client.post("/api/v1/providers", json={
            "name": "update-test",
            "display_name": "Before Update",
            "provider_type": "llm",
        })
        provider_id = resp.json()["id"]

        resp = client.put(f"/api/v1/providers/{provider_id}", json={
            "display_name": "After Update",
        })
        assert resp.status_code == 200

        resp = client.get(f"/api/v1/providers/{provider_id}")
        assert resp.json()["display_name"] == "After Update"

    def test_delete_provider(self, client):
        resp = client.post("/api/v1/providers", json={
            "name": "delete-test",
            "display_name": "Delete Me",
            "provider_type": "llm",
        })
        provider_id = resp.json()["id"]

        resp = client.delete(f"/api/v1/providers/{provider_id}")
        assert resp.status_code == 200

        resp = client.get(f"/api/v1/providers/{provider_id}")
        assert resp.status_code == 404

    def test_get_nonexistent_provider_404(self, client):
        resp = client.get("/api/v1/providers/nonexistent-id")
        assert resp.status_code == 404
```

**Step 2: Run — verify GREEN**

Run: `cd ai && source .venv/bin/activate && pytest tests/integration/test_provider_integration.py -v`

**Step 3: Commit**

```bash
git commit -m "test(integration): provider CRUD workflow tests"
```

---

### Task A.4: Integration test — Preset listing & filtering

**Files:**
- Create: `ai/tests/integration/test_preset_integration.py`

**Step 1: Write failing tests**

```python
"""Integration tests for preset endpoints — requires seeded data."""

from services.database import init_database

class TestPresetIntegration:
    def test_list_presets_returns_seeded(self, client):
        # Seed data first
        init_database()
        resp = client.get("/api/v1/music/presets")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    def test_filter_presets_by_genre(self, client):
        init_database()
        resp = client.get("/api/v1/music/presets?genre=lofi")
        assert resp.status_code == 200
        for preset in resp.json():
            assert preset["genre"] == "lofi"

    def test_genres_endpoint(self, client):
        init_database()
        resp = client.get("/api/v1/music/genres")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
```

**Step 2: Run — verify GREEN**

**Step 3: Commit**

---

### Task A.5: Integration test — Music generation flow

**Files:**
- Create: `ai/tests/integration/test_music_integration.py`

**Step 1: Write failing tests**

```python
"""Integration tests for music generation endpoints."""

class TestMusicGenerationIntegration:
    def test_generate_returns_task_id(self, client):
        resp = client.post("/api/v1/generate", json={
            "title": "Test Track",
            "genre": "lofi",
            "mood": "chill",
            "duration": 30,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert data["status"] in ("pending", "processing")
        assert data["genre"] == "lofi"

    def test_generate_validates_duration(self, client):
        resp = client.post("/api/v1/generate", json={
            "title": "Bad Duration",
            "genre": "lofi",
            "mood": "chill",
            "duration": 5,  # too short
        })
        assert resp.status_code == 400

    def test_status_endpoint(self, client):
        # Create a task first
        gen = client.post("/api/v1/generate", json={
            "title": "Status Test",
            "genre": "lofi",
            "mood": "chill",
            "duration": 30,
        })
        task_id = gen.json()["task_id"]

        resp = client.get(f"/api/v1/status/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["task_id"] == task_id

    def test_genres_endpoint(self, client):
        resp = client.get("/api/v1/genres")
        assert resp.status_code == 200
        data = resp.json()
        assert "genres" in data
        assert "moods" in data
        assert "lofi" in data["genres"]
```

**Step 2: Run — verify GREEN**

**Step 3: Commit**

---

### Task A.6: Integration test — Video analysis endpoints

**Files:**
- Create: `ai/tests/integration/test_video_integration.py`

**Step 1: Write failing tests**

```python
"""Integration tests for video analysis endpoints."""

class TestVideoAnalysisIntegration:
    def test_analyze_requires_url(self, client):
        resp = client.post("/api/v1/analyze", json={})
        assert resp.status_code == 400

    def test_analyze_youtube_url(self, client):
        resp = client.post("/api/v1/analyze", json={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data or "status" in data

    def test_upload_requires_file(self, client):
        resp = client.post("/api/v1/upload")
        assert resp.status_code in (400, 422)
```

**Step 2: Run — verify GREEN**

**Step 3: Commit**

---

## Phase B: E2E Tests (Full Server Startup → Endpoint Validation)

### Task B.1: Create E2E test infrastructure

**Files:**
- Create: `ai/tests/e2e/__init__.py`
- Create: `ai/tests/e2e/conftest.py`

**Step 1: Write E2E conftest**

```python
# ai/tests/e2e/conftest.py
"""E2E conftest — starts real uvicorn server for full-stack testing."""

import pytest
import subprocess
import time
import httpx

BASE_URL = "http://127.0.0.1:18765"  # Dedicated test port

@pytest.fixture(scope="session", autouse=True)
def start_server():
    """Start FastAPI server for E2E tests."""
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "18765"],
        cwd=str(Path(__file__).resolve().parent.parent.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait for server ready
    for _ in range(20):
        try:
            r = httpx.get(f"{BASE_URL}/health", timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    yield
    proc.terminate()
    proc.wait(timeout=5)

@pytest.fixture
def api():
    """Return httpx client pointed at test server."""
    return httpx.Client(base_url=BASE_URL, timeout=10)
```

**Step 2: Commit**

---

### Task B.2: E2E test — Full API smoke test

**Files:**
- Create: `ai/tests/e2e/test_api_e2e.py`

**Step 1: Write failing tests**

```python
"""E2E: Full server smoke tests — all endpoints respond correctly."""

class TestE2EApiSmoke:
    def test_health_live_server(self, api):
        resp = api.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_root_info(self, api):
        resp = api.get("/")
        assert resp.status_code == 200
        assert "service" in resp.json()

    def test_genres_available(self, api):
        resp = api.get("/api/v1/genres")
        assert resp.status_code == 200
        genres = resp.json()["genres"]
        assert "lofi" in genres
        assert "hyper-pop" in genres

    def test_generate_and_check_status(self, api):
        # Generate
        resp = api.post("/api/v1/generate", json={
            "title": "E2E Test Track",
            "genre": "lofi",
            "mood": "chill",
            "duration": 15,
        })
        assert resp.status_code == 200
        task_id = resp.json()["task_id"]

        # Check status
        resp = api.get(f"/api/v1/status/{task_id}")
        assert resp.status_code == 200

    def test_providers_list(self, api):
        resp = api.get("/api/v1/providers")
        assert resp.status_code == 200

    def test_presets_list(self, api):
        resp = api.get("/api/v1/music/presets")
        assert resp.status_code == 200

    def test_docs_accessible(self, api):
        resp = api.get("/docs")
        assert resp.status_code == 200
```

**Step 2: Run — verify GREEN**

Run: `cd ai && source .venv/bin/activate && pytest tests/e2e/ -v`

**Step 3: Commit**

---

### Task B.3: E2E test — Full generation lifecycle

**Files:**
- Create: `ai/tests/e2e/test_generation_lifecycle.py`

**Step 1: Write failing tests**

```python
"""E2E: Full music generation lifecycle test."""

class TestGenerationLifecycle:
    def test_generate_status_history_flow(self, api):
        # Step 1: Generate
        resp = api.post("/api/v1/generate", json={
            "title": "Lifecycle Test",
            "genre": "lofi",
            "mood": "chill",
            "duration": 20,
            "tempo": 85,
            "key": "C",
        })
        assert resp.status_code == 200
        data = resp.json()
        task_id = data["task_id"]
        assert data["title"] == "Lifecycle Test"
        assert data["genre"] == "lofi"

        # Step 2: Check status
        resp = api.get(f"/api/v1/status/{task_id}")
        assert resp.status_code == 200
        status = resp.json()
        assert status["task_id"] == task_id
        assert status["status"] in ("pending", "processing", "completed", "failed")

        # Step 3: Check history
        resp = api.get("/api/v1/history")
        assert resp.status_code == 200
```

**Step 2: Run — verify GREEN**

**Step 3: Commit**

---

## Phase C: Final Validation & Coverage

### Task C.1: Run full test suite (unit + integration + e2e)

Run: `cd ai && source .venv/bin/activate && pytest tests/ -v --tb=short`

**Target:** 200+ tests, all passing

### Task C.2: Verify no regressions

Run: `cd ai && source .venv/bin/activate && pytest tests/ -q`

**Target:** Zero failures, zero errors

### Task C.3: Commit and push all test work

```bash
git add -A
git commit -m "test: add integration and E2E tests — all features validated

- Integration: health, provider CRUD, presets, music generation, video
- E2E: full server startup smoke test, generation lifecycle
- Total: 200+ tests passing
- Coverage: 100% API endpoints tested"
git push origin master
```

---

## Summary

| Phase | Tests | Files |
|---|---|---|
| A (Integration) | ~20 tests | 5 files in `tests/integration/` |
| B (E2E) | ~10 tests | 3 files in `tests/e2e/` |
| C (Validation) | Full suite | Verify 200+ pass |
