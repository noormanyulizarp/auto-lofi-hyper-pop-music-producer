"""Tests for services/database.py — init, seed, and get_db."""

import pytest
import sys
import os
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models.database import Base, AIProvider, LofiPreset
from services.database import get_db, init_database


class TestGetDb:
    """Test the get_db generator dependency."""

    def test_get_db_yields_session(self):
        gen = get_db()
        session = next(gen)
        assert session is not None
        # Cleanup
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_db_session_is_usable(self):
        gen = get_db()
        session = next(gen)
        # Should be able to query
        count = session.query(AIProvider).count()
        assert isinstance(count, int)
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_db_closes_session(self):
        """Verify the generator completes and cleanup runs without error."""
        gen = get_db()
        session = next(gen)
        assert session is not None
        # Consume the generator to trigger the finally block
        try:
            next(gen)
        except StopIteration:
            pass


class TestInitDatabase:
    """Test init_database creates tables and seeds data."""

    def test_init_database_creates_tables(self, tmp_path):
        """Init with a fresh DB should create all tables."""
        db_path = str(tmp_path / "test_init.db")
        db_url = f"sqlite:///{db_path}"

        test_engine = create_engine(
            db_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )

        # Verify tables don't exist yet
        insp = inspect(test_engine)
        assert len(insp.get_table_names()) == 0

        # Create tables
        Base.metadata.create_all(bind=test_engine)

        insp = inspect(test_engine)
        tables = insp.get_table_names()
        assert "ai_providers" in tables
        assert "lofi_presets" in tables
        assert "music_generations" in tables
        assert "video_analyses" in tables

    def test_init_database_idempotent(self):
        """Calling init_database multiple times should be safe."""
        # The app already called init_database on startup
        init_database()
        # Should not raise
        init_database()

    def test_seed_providers_creates_records(self):
        """After init, providers should be seeded."""
        from services.database import SessionLocal
        db = SessionLocal()
        try:
            count = db.query(AIProvider).count()
            assert count >= 3
        finally:
            db.close()

    def test_seed_providers_openrouter(self):
        from services.database import SessionLocal
        db = SessionLocal()
        try:
            provider = db.query(AIProvider).filter(AIProvider.name == "openrouter").first()
            assert provider is not None
            assert provider.display_name == "OpenRouter"
            assert provider.provider_type == "llm"
            assert provider.status == "active"
            assert len(provider.models) == 8
            assert provider.default_model == "baidu/cobuddy:free"
        finally:
            db.close()

    def test_seed_providers_heartmula(self):
        from services.database import SessionLocal
        db = SessionLocal()
        try:
            provider = db.query(AIProvider).filter(AIProvider.name == "heartmula").first()
            assert provider is not None
            assert provider.display_name == "HeartMuLa"
            assert provider.provider_type == "music"
            assert provider.supports_music_generation is True
            assert len(provider.models) == 2
        finally:
            db.close()

    def test_seed_providers_glm_zai(self):
        from services.database import SessionLocal
        db = SessionLocal()
        try:
            provider = db.query(AIProvider).filter(AIProvider.name == "glm-zai").first()
            assert provider is not None
            assert provider.display_name == "GLM Z.ai (Direct)"
            assert provider.provider_type == "llm"
            assert len(provider.models) == 3
        finally:
            db.close()

    def test_seed_presets_creates_records(self):
        """After init, presets should be seeded."""
        from services.database import SessionLocal
        db = SessionLocal()
        try:
            count = db.query(LofiPreset).count()
            assert count >= 10
        finally:
            db.close()

    def test_seed_presets_all_genres(self):
        from services.database import SessionLocal
        db = SessionLocal()
        try:
            genres = set(
                row[0] for row in db.query(LofiPreset.genre).distinct().all()
            )
            expected = {"lofi", "hyper-pop", "ambient", "synthwave", "vaporwave", "chillhop", "trap"}
            assert expected.issubset(genres)
        finally:
            db.close()

    def test_seed_presets_lofi_chill_study(self):
        from services.database import SessionLocal
        db = SessionLocal()
        try:
            preset = db.query(LofiPreset).filter(LofiPreset.name == "Lo-Fi Chill Study").first()
            assert preset is not None
            assert preset.genre == "lofi"
            assert preset.mood == "chill"
            assert preset.is_default is True
            assert preset.display_order == 1
        finally:
            db.close()

    def test_seed_not_duplicated(self):
        """Seed functions should not create duplicates."""
        from services.database import SessionLocal
        db = SessionLocal()
        try:
            count_before = db.query(AIProvider).count()
        finally:
            db.close()

        # Re-init (should skip seeding)
        init_database()

        db = SessionLocal()
        try:
            count_after = db.query(AIProvider).count()
            assert count_after == count_before
        finally:
            db.close()


class TestSeedWithFreshDb:
    """Test seed functions against a completely fresh DB to cover all seed code paths."""

    def test_seed_providers_on_fresh_db(self, tmp_path):
        """Run _seed_default_providers on a fresh DB to cover the insert path."""
        db_path = str(tmp_path / "fresh_seed.db")
        db_url = f"sqlite:///{db_path}"

        fresh_engine = create_engine(
            db_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=fresh_engine)
        FreshSession = sessionmaker(autocommit=False, autoflush=False, bind=fresh_engine)

        # Import seed function
        from services.database import _seed_default_providers, _seed_lofi_presets

        # Temporarily replace SessionLocal
        import services.database as db_mod
        original_session_local = db_mod.SessionLocal
        db_mod.SessionLocal = FreshSession

        try:
            # Should insert 3 providers
            _seed_default_providers()

            session = FreshSession()
            providers = session.query(AIProvider).all()
            assert len(providers) == 3
            names = {p.name for p in providers}
            assert names == {"openrouter", "heartmula", "glm-zai"}
            session.close()

            # Calling again should skip (already seeded)
            _seed_default_providers()
            session = FreshSession()
            assert session.query(AIProvider).count() == 3
            session.close()
        finally:
            db_mod.SessionLocal = original_session_local

    def test_seed_presets_on_fresh_db(self, tmp_path):
        """Run _seed_lofi_presets on a fresh DB to cover the insert path."""
        db_path = str(tmp_path / "fresh_presets.db")
        db_url = f"sqlite:///{db_path}"

        fresh_engine = create_engine(
            db_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=fresh_engine)
        FreshSession = sessionmaker(autocommit=False, autoflush=False, bind=fresh_engine)

        from services.database import _seed_lofi_presets
        import services.database as db_mod
        original_session_local = db_mod.SessionLocal
        db_mod.SessionLocal = FreshSession

        try:
            _seed_lofi_presets()

            session = FreshSession()
            presets = session.query(LofiPreset).all()
            assert len(presets) == 11
            genres = {p.genre for p in presets}
            assert "lofi" in genres
            assert "hyper-pop" in genres
            assert "ambient" in genres
            session.close()

            # Calling again should skip
            _seed_lofi_presets()
            session = FreshSession()
            assert session.query(LofiPreset).count() == 11
            session.close()
        finally:
            db_mod.SessionLocal = original_session_local

    def test_seed_providers_error_handling(self, tmp_path):
        """Test that seed handles exceptions gracefully."""
        from services.database import _seed_default_providers
        import services.database as db_mod

        # Create a session factory that raises on commit
        class BadSession:
            def __init__(self, *a, **kw):
                pass
            def query(self, *a):
                class Q:
                    def count(self):
                        return 0  # Pretend empty so seed tries to insert
                return Q()
            def add(self, *a):
                pass
            def commit(self):
                raise RuntimeError("DB commit failed")
            def rollback(self):
                pass
            def close(self):
                pass

        original = db_mod.SessionLocal
        db_mod.SessionLocal = BadSession

        try:
            # Should not raise, just log error
            _seed_default_providers()
        finally:
            db_mod.SessionLocal = original

    def test_seed_presets_error_handling(self, tmp_path):
        """Test that preset seed handles exceptions gracefully."""
        from services.database import _seed_lofi_presets
        import services.database as db_mod

        class BadSession:
            def __init__(self, *a, **kw):
                pass
            def query(self, *a):
                class Q:
                    def count(self):
                        return 0
                return Q()
            def add(self, *a):
                pass
            def commit(self):
                raise RuntimeError("DB preset commit failed")
            def rollback(self):
                pass
            def close(self):
                pass

        original = db_mod.SessionLocal
        db_mod.SessionLocal = BadSession

        try:
            _seed_lofi_presets()
        finally:
            db_mod.SessionLocal = original

    def test_init_database_creates_parent_dirs(self, tmp_path):
        """Test that init_database creates the parent directory for the DB."""
        from config import settings
        import services.database as db_mod

        # Use a nested path that doesn't exist yet
        nested_db = str(tmp_path / "nested" / "dir" / "test.db")
        db_url = f"sqlite:///{nested_db}"

        # Mock the settings to return our URL
        with mock.patch.object(settings, 'DATABASE_URL', db_url):
            # Temporarily swap engine and SessionLocal
            original_engine = db_mod.engine
            original_session = db_mod.SessionLocal

            fresh_engine = create_engine(
                db_url.replace("+aiosqlite", ""),
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
                echo=False,
            )
            db_mod.engine = fresh_engine
            db_mod.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=fresh_engine
            )

            try:
                db_mod.init_database()
                assert os.path.exists(nested_db)
            finally:
                db_mod.engine = original_engine
                db_mod.SessionLocal = original_session


class TestSeedHelperFunctions:
    """Test the model builder helpers."""

    def test_build_openrouter_models(self):
        from services.database import _build_openrouter_models
        models = _build_openrouter_models()
        assert len(models) == 8
        for m in models:
            assert "id" in m
            assert "name" in m
            assert "specialty" in m
        assert models[0]["id"] == "baidu/cobuddy:free"

    def test_build_glm_zai_models(self):
        from services.database import _build_glm_zai_models
        models = _build_glm_zai_models()
        assert len(models) == 3
        model_ids = [m["id"] for m in models]
        assert "glm-4.5-air" in model_ids
        assert "glm-4.5" in model_ids
        assert "glm-4.7" in model_ids
