"""Unit tests for database models — AIProvider, MusicGeneration, LofiPreset, VideoAnalysis."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.database import Base, AIProvider, MusicGeneration, LofiPreset, VideoAnalysis, gen_uuid


class TestGenUuid:
    def test_gen_uuid_returns_string(self):
        uid = gen_uuid()
        assert isinstance(uid, str)
        assert len(uid) == 36  # standard UUID format

    def test_gen_uuid_unique(self):
        ids = {gen_uuid() for _ in range(100)}
        assert len(ids) == 100  # all unique


class TestAIProvider:
    def test_create_provider(self):
        p = AIProvider(
            name="test-provider",
            display_name="Test Provider",
            provider_type="llm",
            status="active",
        )
        assert p.name == "test-provider"
        assert p.display_name == "Test Provider"
        assert p.provider_type == "llm"
        assert p.status == "active"

    def test_default_values(self):
        """SQLAlchemy Column defaults only apply on INSERT, not on in-memory objects.
        Verify the Column definitions have the correct defaults declared."""
        from sqlalchemy import inspect as sa_inspect
        from models.database import AIProvider

        mapper = sa_inspect(AIProvider)
        col_defaults = {c.key: c.default for c in mapper.columns if c.default}

        # Verify defaults are declared in the model
        assert col_defaults["max_tokens"].arg == 32768
        assert col_defaults["temperature"].arg == 0.7
        assert col_defaults["timeout_seconds"].arg == 300
        assert col_defaults["supports_music_generation"].arg is False
        assert col_defaults["supports_lyrics_enhancement"].arg is False
        assert col_defaults["supports_audio_analysis"].arg is False
        assert col_defaults["total_requests"].arg == 0
        assert col_defaults["successful_requests"].arg == 0
        assert col_defaults["failed_requests"].arg == 0

    def test_to_dict(self):
        p = AIProvider(
            name="test",
            display_name="Test",
            provider_type="music",
            models=[{"id": "model-1", "name": "Model 1"}],
        )
        d = p.to_dict()
        assert d["name"] == "test"
        assert d["provider_type"] == "music"
        assert d["models"] == [{"id": "model-1", "name": "Model 1"}]
        assert "created_at" not in d or d["created_at"] is None  # not yet persisted

    def test_to_dict_no_models(self):
        p = AIProvider(name="t", display_name="T", provider_type="llm")
        d = p.to_dict()
        assert d["models"] == []

    def test_tablename(self):
        assert AIProvider.__tablename__ == "ai_providers"


class TestMusicGeneration:
    def test_create(self):
        m = MusicGeneration(
            task_id="abc123",
            title="Chill Beats",
            genre="lofi",
            mood="chill",
            duration=30,
        )
        assert m.task_id == "abc123"
        assert m.title == "Chill Beats"
        assert m.genre == "lofi"
        assert m.duration == 30

    def test_defaults(self):
        """Verify column defaults declared in model."""
        from sqlalchemy import inspect as sa_inspect
        mapper = sa_inspect(MusicGeneration)
        col_defaults = {c.key: c.default for c in mapper.columns if c.default}
        assert col_defaults["status"].arg == "pending"
        assert col_defaults["progress"].arg == 0.0
        assert col_defaults["provider_name"].arg == "heartmula"

    def test_to_dict(self):
        m = MusicGeneration(
            task_id="abc",
            title="Test",
            genre="ambient",
            mood="dreamy",
            duration=60,
            original_prompt="test prompt",
        )
        d = m.to_dict()
        assert d["task_id"] == "abc"
        assert d["genre"] == "ambient"
        assert d["original_prompt"] == "test prompt"

    def test_tablename(self):
        assert MusicGeneration.__tablename__ == "music_generations"


class TestLofiPreset:
    def test_create(self):
        p = LofiPreset(
            name="Lo-Fi Chill Study",
            genre="lofi",
            mood="chill",
        )
        assert p.name == "Lo-Fi Chill Study"
        assert p.genre == "lofi"

    def test_defaults(self):
        """Verify column defaults declared in model."""
        from sqlalchemy import inspect as sa_inspect
        mapper = sa_inspect(LofiPreset)
        col_defaults = {c.key: c.default for c in mapper.columns if c.default}
        assert col_defaults["tempo_min"].arg == 70
        assert col_defaults["tempo_max"].arg == 90
        assert col_defaults["key_signature"].arg == "C major"
        assert col_defaults["duration_default"].arg == 30
        assert col_defaults["is_default"].arg is False
        assert col_defaults["icon"].arg == "🎵"
        assert col_defaults["display_order"].arg == 0

    def test_to_dict(self):
        p = LofiPreset(
            name="Test Preset",
            genre="trap",
            mood="dark",
            instruments=["808", "hi_hat"],
            tags="trap,dark,808",
        )
        d = p.to_dict()
        assert d["name"] == "Test Preset"
        assert d["instruments"] == ["808", "hi_hat"]
        assert d["tags"] == "trap,dark,808"

    def test_to_dict_no_instruments(self):
        p = LofiPreset(name="X", genre="lofi", mood="chill")
        d = p.to_dict()
        assert d["instruments"] == []

    def test_tablename(self):
        assert LofiPreset.__tablename__ == "lofi_presets"


class TestVideoAnalysis:
    def test_create(self):
        v = VideoAnalysis(
            task_id="vid-1",
            video_url="https://youtube.com/watch?v=test",
        )
        assert v.task_id == "vid-1"
        assert v.video_url == "https://youtube.com/watch?v=test"

    def test_defaults(self):
        """Verify column defaults declared in model."""
        from sqlalchemy import inspect as sa_inspect
        mapper = sa_inspect(VideoAnalysis)
        col_defaults = {c.key: c.default for c in mapper.columns if c.default}
        assert col_defaults["status"].arg == "pending"
        assert col_defaults["progress"].arg == 0.0
        assert col_defaults["focus_type"].arg == "general"

    def test_to_dict(self):
        v = VideoAnalysis(
            task_id="v2",
            video_url="http://test",
            video_title="Test Video",
        )
        d = v.to_dict()
        assert d["task_id"] == "v2"
        assert d["video_title"] == "Test Video"

    def test_tablename(self):
        assert VideoAnalysis.__tablename__ == "video_analyses"
