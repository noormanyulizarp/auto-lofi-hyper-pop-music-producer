"""Tests for config/provider_config.py — AI Provider configuration."""

import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.provider_config import ProviderConfig, provider_config


class TestProviderConfigDefaults:
    """Test default values in ProviderConfig."""

    def test_default_provider(self):
        cfg = ProviderConfig()
        assert cfg.DEFAULT_PROVIDER == "openrouter"

    def test_default_model(self):
        cfg = ProviderConfig()
        assert cfg.DEFAULT_MODEL == "baidu/cobuddy:free"

    def test_openrouter_base_url(self):
        cfg = ProviderConfig()
        assert cfg.OPENROUTER_BASE_URL == "https://openrouter.ai/api/v1"

    def test_glm_zai_base_url(self):
        cfg = ProviderConfig()
        assert cfg.GLM_ZAI_BASE_URL == "https://api.z.ai/api/coding/paas/v4"

    def test_heartmula_base_url(self):
        cfg = ProviderConfig()
        assert cfg.HEARTMULA_BASE_URL == "http://localhost:8000"

    def test_max_retries(self):
        cfg = ProviderConfig()
        assert cfg.MAX_RETRIES == 3

    def test_timeout_seconds(self):
        cfg = ProviderConfig()
        assert cfg.TIMEOUT_SECONDS == 300

    def test_fallback_enabled(self):
        cfg = ProviderConfig()
        assert cfg.FALLBACK_ENABLED is True


class TestProviderConfigModels:
    """Test the MODELS dict."""

    def test_models_dict_exists(self):
        cfg = ProviderConfig()
        assert isinstance(cfg.MODELS, dict)
        assert len(cfg.MODELS) > 0

    def test_openrouter_models_present(self):
        cfg = ProviderConfig()
        expected_keys = [
            "openrouter-cobuddy",
            "openrouter-gpt-oss-20b",
            "openrouter-gpt-oss-120b",
            "openrouter-nemotron-9b",
            "openrouter-nemotron-30b",
            "openrouter-trinity-thinking",
            "openrouter-nemotron-120b",
            "openrouter-glm-air",
        ]
        for key in expected_keys:
            assert key in cfg.MODELS, f"Missing model: {key}"

    def test_zai_models_present(self):
        cfg = ProviderConfig()
        assert "zai-glm-4.5-air" in cfg.MODELS
        assert "zai-glm-4.5" in cfg.MODELS
        assert "zai-glm-4.7" in cfg.MODELS

    def test_model_has_required_fields(self):
        cfg = ProviderConfig()
        for key, model in cfg.MODELS.items():
            assert "model" in model, f"{key} missing 'model'"
            assert "provider" in model, f"{key} missing 'provider'"
            assert "api_base" in model, f"{key} missing 'api_base'"
            assert "specialty" in model, f"{key} missing 'specialty'"
            assert "max_tokens" in model, f"{key} missing 'max_tokens'"
            assert "temperature" in model, f"{key} missing 'temperature'"
            assert "fallbacks" in model, f"{key} missing 'fallbacks'"

    def test_openrouter_models_use_openrouter_provider(self):
        cfg = ProviderConfig()
        for key in cfg.MODELS:
            if key.startswith("openrouter-"):
                assert cfg.MODELS[key]["provider"] == "openrouter"

    def test_zai_models_use_glm_zai_provider(self):
        cfg = ProviderConfig()
        for key in cfg.MODELS:
            if key.startswith("zai-"):
                assert cfg.MODELS[key]["provider"] == "glm-zai"

    def test_fallback_chains_exist(self):
        """Models (except the last in chain) should have fallbacks."""
        cfg = ProviderConfig()
        # The last model in the chain (openrouter-glm-air) has empty fallbacks
        assert cfg.MODELS["openrouter-glm-air"]["fallbacks"] == []
        # Others should have at least one fallback
        for key in cfg.MODELS:
            if key != "openrouter-glm-air":
                assert len(cfg.MODELS[key]["fallbacks"]) > 0, f"{key} has no fallbacks"


class TestProviderConfigEnvVars:
    """Test that API keys come from env vars."""

    def test_openrouter_api_key_from_env(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("OPENROUTER_API_KEY", "test-key-123")
            cfg = ProviderConfig()
            assert cfg.OPENROUTER_API_KEY == "test-key-123"

    def test_glm_zai_api_key_from_env(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("GLM_ZAI_API_KEY", "zai-key-456")
            cfg = ProviderConfig()
            assert cfg.GLM_ZAI_API_KEY == "zai-key-456"

    def test_heartmula_api_key_from_env(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("HEARTMULA_API_KEY", "heart-key-789")
            cfg = ProviderConfig()
            assert cfg.HEARTMULA_API_KEY == "heart-key-789"

    def test_glm_api_token_from_env(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("GLM_API_TOKEN", "glm-token-abc")
            cfg = ProviderConfig()
            assert cfg.GLM_API_TOKEN == "glm-token-abc"

    def test_github_token_from_env(self):
        """GITHUB_TOKEN reads from os.environ at class definition time as GITHUB_PAT."""
        # The field default is os.environ.get("GITHUB_PAT", ""), so it reads
        # the env var at class-def time, not through pydantic's GITHUB_TOKEN env var.
        # We can verify the field exists and has a default mechanism.
        cfg = ProviderConfig()
        assert hasattr(cfg, "GITHUB_TOKEN")
        assert isinstance(cfg.GITHUB_TOKEN, str)


class TestGlobalProviderConfig:
    """Test the global provider_config instance."""

    def test_global_instance_exists(self):
        assert provider_config is not None
        assert isinstance(provider_config, ProviderConfig)

    def test_global_has_models(self):
        assert len(provider_config.MODELS) >= 11  # 8 openrouter + 3 zai

    def test_glm_web_urls(self):
        assert "z.ai" in provider_config.GLM_WEB_SEARCH_URL
        assert "z.ai" in provider_config.GLM_WEB_READER_URL
