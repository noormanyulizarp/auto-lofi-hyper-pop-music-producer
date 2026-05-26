from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings — SQLite for dev, PostgreSQL for prod."""

    # Basic settings
    HOST: str = "127.0.0.1"
    PORT: int = 8001
    DEBUG: bool = True

    # Database — SQLite default (lightweight, no external service needed)
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/music_producer.db"

    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # AI Provider keys (configurable via dashboard / .env)
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    HEARTMULA_API_KEY: Optional[str] = None
    HEARTMULA_BASE_URL: str = "http://localhost:8000"

    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Audio processing
    SAMPLE_RATE: int = 44100
    AUDIO_FORMAT: str = "wav"

    # JWT settings
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/ai_services.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
