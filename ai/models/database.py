"""Database models — SQLAlchemy ORM models with SQLite support."""

from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass


def gen_uuid():
    return str(uuid.uuid4())


class AIProvider(Base):
    """AI Provider configuration — manageable via dashboard."""

    __tablename__ = "ai_providers"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)  # e.g. "openrouter", "heartmula"
    display_name = Column(String, nullable=False)  # e.g. "OpenRouter"
    provider_type = Column(String, nullable=False)  # "llm", "music", "video"
    status = Column(String, default="active")  # active, inactive, error

    # API config
    api_key = Column(String)
    api_base_url = Column(String)
    auth_header_format = Column(String, default="Bearer {api_key}")

    # Models this provider offers (JSON array)
    models = Column(JSON, default=list)

    # Default settings
    default_model = Column(String)
    max_tokens = Column(Integer, default=32768)
    temperature = Column(Float, default=0.7)
    timeout_seconds = Column(Integer, default=300)

    # Feature flags
    supports_music_generation = Column(Boolean, default=False)
    supports_lyrics_enhancement = Column(Boolean, default=False)
    supports_audio_analysis = Column(Boolean, default=False)

    # Metadata
    description = Column(Text)
    icon_url = Column(String)
    docs_url = Column(String)
    config_metadata = Column(JSON, default=dict)  # Extra provider-specific config

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)
    last_error = Column(Text)

    # Usage stats
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "provider_type": self.provider_type,
            "status": self.status,
            "api_base_url": self.api_base_url,
            "models": self.models or [],
            "default_model": self.default_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "supports_music_generation": self.supports_music_generation,
            "supports_lyrics_enhancement": self.supports_lyrics_enhancement,
            "supports_audio_analysis": self.supports_audio_analysis,
            "description": self.description,
            "config_metadata": self.config_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
        }


class MusicGeneration(Base):
    """Music generation task records."""

    __tablename__ = "music_generations"

    id = Column(String, primary_key=True, default=gen_uuid)
    task_id = Column(String, unique=True, nullable=False, index=True)

    # Request data
    title = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    mood = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    original_prompt = Column(Text)
    enhanced_prompt = Column(Text)

    # AI parameters
    tempo = Column(Integer)
    key = Column(String)
    instruments = Column(JSON)
    tags = Column(String)  # HeartMuLa tags format

    # Provider used
    provider_name = Column(String, default="heartmula")
    model = Column(String)

    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    error_message = Column(Text)

    # Results
    result_url = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)

    # Lyrics & tags
    lyrics = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "title": self.title,
            "genre": self.genre,
            "mood": self.mood,
            "duration": self.duration,
            "original_prompt": self.original_prompt,
            "enhanced_prompt": self.enhanced_prompt,
            "tempo": self.tempo,
            "key": self.key,
            "instruments": self.instruments,
            "tags": self.tags,
            "provider_name": self.provider_name,
            "model": self.model,
            "status": self.status,
            "progress": self.progress,
            "error_message": self.error_message,
            "result_url": self.result_url,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class LofiPreset(Base):
    """Lofi / genre preset templates — default seed data for quick generation."""

    __tablename__ = "lofi_presets"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)  # e.g. "Lo-Fi Chill Study"
    genre = Column(String, nullable=False)  # lofi, hyper-pop, ambient, etc.
    mood = Column(String, nullable=False)  # chill, dreamy, melancholic, etc.

    # Music parameters
    tempo_min = Column(Integer, default=70)
    tempo_max = Column(Integer, default=90)
    key_signature = Column(String, default="C major")
    duration_default = Column(Integer, default=30)  # seconds

    # Instruments (JSON array of strings)
    instruments = Column(JSON, default=list)
    # HeartMuLa-style tags
    tags = Column(String)  # comma-separated: "lo-fi,vinyl,rain,piano,mellow"

    # Prompt templates
    prompt_template = Column(Text)  # e.g. "A {mood} lo-fi beat with {instruments}"

    # Metadata
    is_default = Column(Boolean, default=False)  # shown as "quick pick"
    icon = Column(String, default="🎵")  # emoji icon
    description = Column(Text)
    display_order = Column(Integer, default=0)  # lower = shown first

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.genre,
            "mood": self.mood,
            "tempo_min": self.tempo_min,
            "tempo_max": self.tempo_max,
            "key_signature": self.key_signature,
            "duration_default": self.duration_default,
            "instruments": self.instruments or [],
            "tags": self.tags,
            "prompt_template": self.prompt_template,
            "is_default": self.is_default,
            "icon": self.icon,
            "description": self.description,
            "display_order": self.display_order,
        }


class VideoAnalysis(Base):
    """Video analysis records."""

    __tablename__ = "video_analyses"

    id = Column(String, primary_key=True, default=gen_uuid)
    task_id = Column(String, unique=True, nullable=False, index=True)

    video_url = Column(String, nullable=False)
    video_title = Column(String)
    focus_type = Column(String, default="general")

    status = Column(String, default="pending")
    progress = Column(Float, default=0.0)
    error_message = Column(Text)

    transcript = Column(Text)
    audio_features = Column(JSON)
    learned_patterns = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "video_url": self.video_url,
            "video_title": self.video_title,
            "focus_type": self.focus_type,
            "status": self.status,
            "progress": self.progress,
            "transcript": self.transcript,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
