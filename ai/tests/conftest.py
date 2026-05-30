"""Shared test fixtures for all tests."""

import sys
import os
import pytest
from pathlib import Path

# Ensure ai/ is on sys.path so imports work like the app does
AI_DIR = Path(__file__).resolve().parent.parent
if str(AI_DIR) not in sys.path:
    sys.path.insert(0, str(AI_DIR))

# Use a temp SQLite DB for tests so we never touch production data
TEST_DB_PATH = str(AI_DIR / "data" / "test_music_producer.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="session", autouse=True)
def _setup_test_env():
    """Set environment variables before any imports that read settings."""
    # Clean up any leftover test DB from a previous run
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["DEBUG"] = "false"
    os.environ["HOST"] = "127.0.0.1"
    os.environ["PORT"] = "8001"
    yield
    # Cleanup temp DB
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
