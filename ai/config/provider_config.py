from pydantic_settings import BaseSettings
from typing import Dict, Any
import os


class ProviderConfig(BaseSettings):
    """AI Provider configuration — OpenRouter (8 free) + HeartMuLa + GLM Z.ai Direct."""

    # OpenRouter — loaded from .env
    OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # GLM Z.ai Direct — loaded from .env
    GLM_ZAI_API_KEY: str = os.environ.get("GLM_ZAI_API_KEY", "")
    GLM_ZAI_BASE_URL: str = "https://api.z.ai/api/coding/paas/v4"

    # Defaults
    DEFAULT_PROVIDER: str = "openrouter"
    DEFAULT_MODEL: str = "baidu/cobuddy:free"

    # 8-model rotation via OpenRouter (all free)
    MODELS: Dict[str, Dict[str, Any]] = {
        "openrouter-cobuddy": {
            "model": "baidu/cobuddy:free",
            "provider": "openrouter",
            "api_base": "https://openrouter.ai/api/v1",
            "fallbacks": ["openrouter-gpt-oss-20b"],
            "specialty": "assistant",
            "max_tokens": 32768,
            "temperature": 0.7,
        },
        "openrouter-gpt-oss-20b": {
            "model": "openai/gpt-oss-20b:free",
            "provider": "openrouter",
            "api_base": "https://openrouter.ai/api/v1",
            "fallbacks": ["openrouter-gpt-oss-120b"],
            "specialty": "general",
            "max_tokens": 32768,
            "temperature": 0.7,
        },
        "openrouter-gpt-oss-120b": {
            "model": "openai/gpt-oss-120b:free",
            "provider": "openrouter",
            "api_base": "https://openrouter.ai/api/v1",
            "fallbacks": ["openrouter-nemotron-9b"],
            "specialty": "large_context",
            "max_tokens": 65536,
            "temperature": 0.7,
        },
        "openrouter-nemotron-9b": {
            "model": "nvidia/nemotron-nano-9b-v2:free",
            "provider": "openrouter",
            "api_base": "https://openrouter.ai/api/v1",
            "fallbacks": ["openrouter-nemotron-30b"],
            "specialty": "fast_response",
            "max_tokens": 16384,
            "temperature": 0.7,
        },
        "openrouter-nemotron-30b": {
            "model": "nvidia/nemotron-3-nano-30b-a3b:free",
            "provider": "openrouter",
            "api_base": "https://openrouter.ai/api/v1",
            "fallbacks": ["openrouter-trinity-thinking"],
            "specialty": "balanced",
            "max_tokens": 32768,
            "temperature": 0.7,
        },
        "openrouter-trinity-thinking": {
            "model": "arcee-ai/trinity-large-thinking:free",
            "provider": "openrouter",
            "api_base": "https://openrouter.ai/api/v1",
            "fallbacks": ["openrouter-nemotron-120b"],
            "specialty": "complex_reasoning",
            "max_tokens": 32768,
            "temperature": 0.3,
        },
        "openrouter-nemotron-120b": {
            "model": "nvidia/nemotron-3-super-120b-a12b:free",
            "provider": "openrouter",
            "api_base": "https://openrouter.ai/api/v1",
            "fallbacks": ["openrouter-glm-air"],
            "specialty": "deep_analysis",
            "max_tokens": 65536,
            "temperature": 0.5,
        },
        "openrouter-glm-air": {
            "model": "z-ai/glm-4.5-air:free",
            "provider": "openrouter",
            "api_base": "https://openrouter.ai/api/v1",
            "fallbacks": [],
            "specialty": "music_friendly",
            "max_tokens": 32768,
            "temperature": 0.7,
        },

        # ── GLM Z.ai Direct (bypass OpenRouter for lower latency) ──
        "zai-glm-4.5-air": {
            "model": "glm-4.5-air",
            "provider": "glm-zai",
            "api_base": "https://api.z.ai/api/coding/paas/v4",
            "fallbacks": ["zai-glm-4.5"],
            "specialty": "fast_llm",
            "max_tokens": 32768,
            "temperature": 0.7,
        },
        "zai-glm-4.5": {
            "model": "glm-4.5",
            "provider": "glm-zai",
            "api_base": "https://api.z.ai/api/coding/paas/v4",
            "fallbacks": ["zai-glm-4.7"],
            "specialty": "balanced_llm",
            "max_tokens": 65536,
            "temperature": 0.7,
        },
        "zai-glm-4.7": {
            "model": "glm-4.7",
            "provider": "glm-zai",
            "api_base": "https://api.z.ai/api/coding/paas/v4",
            "fallbacks": ["openrouter-glm-air"],
            "specialty": "complex_reasoning",
            "max_tokens": 65536,
            "temperature": 0.5,
        },
    }

    # HeartMuLa (local music generation)
    HEARTMULA_BASE_URL: str = "http://localhost:8000"
    HEARTMULA_API_KEY: str = os.environ.get("HEARTMULA_API_KEY", "")

    # GLM Web services
    GLM_WEB_SEARCH_URL: str = "https://api.z.ai/api/mcp/web_search_prime/mcp"
    GLM_WEB_READER_URL: str = "https://api.z.ai/api/mcp/web_reader/mcp"
    GLM_API_TOKEN: str = os.environ.get("GLM_API_TOKEN", "")

    # GitHub
    GITHUB_TOKEN: str = os.environ.get("GITHUB_PAT", "")

    # Service
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 300
    FALLBACK_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global config instance
provider_config = ProviderConfig()
