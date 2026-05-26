"""Unit tests for config/settings.py — verify defaults and env overrides."""

import pytest
import os
import sys
from pathlib import Path

# Ensure ai/ on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestSettingsDefaults:
    """Verify Settings has sensible defaults for dev."""

    def test_settings_loads(self):
        from config.settings import settings
        assert settings is not None

    def test_default_host(self):
        from config.settings import settings
        assert settings.HOST == "127.0.0.1"

    def test_default_port(self):
        from config.settings import settings
        assert settings.PORT == 8001

    def test_default_debug(self):
        from config.settings import settings
        assert isinstance(settings.DEBUG, bool)

    def test_database_url_is_sqlite(self):
        from config.settings import settings
        # Should contain sqlite (either aiosqlite or plain sqlite)
        assert "sqlite" in settings.DATABASE_URL

    def test_allowed_origins_list(self):
        from config.settings import settings
        assert isinstance(settings.ALLOWED_ORIGINS, list)
        assert len(settings.ALLOWED_ORIGINS) > 0
        # Should contain localhost
        assert any("localhost" in o or "127.0.0.1" in o for o in settings.ALLOWED_ORIGINS)

    def test_sample_rate(self):
        from config.settings import settings
        assert settings.SAMPLE_RATE == 44100

    def test_max_file_size(self):
        from config.settings import settings
        assert settings.MAX_FILE_SIZE == 100 * 1024 * 1024  # 100MB

    def test_secret_key_exists(self):
        from config.settings import settings
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 0

    def test_provider_urls(self):
        from config.settings import settings
        assert "openrouter.ai" in settings.OPENROUTER_BASE_URL
        assert "z.ai" in settings.GLM_ZAI_BASE_URL

    def test_log_level(self):
        from config.settings import settings
        assert settings.LOG_LEVEL in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
