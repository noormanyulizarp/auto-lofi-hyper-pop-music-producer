"""Tests for services/heartmula.py — HeartMuLa music generation service."""

import pytest
import sys
import asyncio
import os
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.heartmula import HeartMuLaService


@pytest.fixture
def service():
    """Create a fresh service instance for each test."""
    return HeartMuLaService()


class TestGenreToTags:
    """Test _genre_to_tags conversion."""

    def test_lofi_genre(self, service):
        tags = service._genre_to_tags("lofi", "chill")
        assert "lofi" in tags
        assert "relaxed" in tags  # chill -> relaxed
        assert "piano" in tags

    def test_hyper_pop_genre(self, service):
        tags = service._genre_to_tags("hyper-pop", "energetic")
        assert "pop" in tags
        assert "energetic" in tags
        assert "synth" in tags

    def test_ambient_genre(self, service):
        tags = service._genre_to_tags("ambient", "dreamy")
        assert "ambient" in tags
        assert "dreamy" in tags

    def test_synthwave_genre(self, service):
        tags = service._genre_to_tags("synthwave", "dark")
        assert "synthwave" in tags
        assert "dark" in tags

    def test_trap_genre(self, service):
        tags = service._genre_to_tags("trap", "dark")
        assert "trap" in tags
        assert "dark" in tags

    def test_chillhop_genre(self, service):
        tags = service._genre_to_tags("chillhop", "chill")
        assert "chillhop" in tags
        assert "relaxed" in tags

    def test_vaporwave_genre(self, service):
        tags = service._genre_to_tags("vaporwave", "chill")
        assert "vaporwave" in tags
        assert "relaxed" in tags

    def test_unknown_genre_defaults_to_pop(self, service):
        tags = service._genre_to_tags("unknown-genre", "chill")
        assert "pop" in tags
        assert "instrumental" in tags
        # "chill" mood gets mapped to "relaxed"
        assert "relaxed" in tags

    def test_mood_mapping(self, service):
        tags = service._genre_to_tags("lofi", "melancholic")
        assert "sad" in tags

    def test_upbeat_mood(self, service):
        tags = service._genre_to_tags("lofi", "upbeat")
        assert "happy" in tags

    def test_unknown_mood_passthrough(self, service):
        tags = service._genre_to_tags("lofi", "unknown_mood")
        assert "unknown_mood" in tags

    def test_instruments_appended(self, service):
        tags = service._genre_to_tags("lofi", "chill", instruments=["guitar", "bass"])
        assert "guitar" in tags
        assert "bass" in tags

    def test_no_instruments(self, service):
        tags = service._genre_to_tags("lofi", "chill", instruments=None)
        # Should not fail
        assert "lofi" in tags

    def test_tags_are_deduplicated(self, service):
        tags = service._genre_to_tags("lofi", "chill", instruments=["lofi"])
        # "lofi" appears in base tags and instruments — should be deduped
        tag_list = tags.split(",")
        assert tag_list.count("lofi") == 1

    def test_tags_comma_separated(self, service):
        tags = service._genre_to_tags("lofi", "chill")
        assert isinstance(tags, str)
        assert "," in tags


class TestGenerateLyrics:
    """Test _generate_lyrics."""

    def test_default_lyrics_structure(self, service):
        lyrics = service._generate_lyrics("My Song", "lofi", "chill")
        assert "[Intro]" in lyrics
        assert "[Verse]" in lyrics
        assert "[Chorus]" in lyrics
        assert "[Bridge]" in lyrics
        assert "[Outro]" in lyrics

    def test_title_in_lyrics(self, service):
        lyrics = service._generate_lyrics("Sunset Drive", "lofi", "chill")
        assert "Sunset Drive" in lyrics

    def test_custom_prompt_in_lyrics(self, service):
        lyrics = service._generate_lyrics("Song", "lofi", "chill", prompt="Custom prompt text")
        assert "Custom prompt text" in lyrics

    def test_default_prompt_incorporates_params(self, service):
        lyrics = service._generate_lyrics("Title", "hyper-pop", "energetic")
        assert "energetic" in lyrics
        assert "hyper-pop" in lyrics


class TestGenerateMusicFallback:
    """Test generate_music in fallback mode (no heartlib)."""

    @pytest.mark.asyncio
    async def test_fallback_returns_completed(self, service):
        result = await service.generate_music(
            title="Test Track", genre="lofi", mood="chill"
        )
        assert result["status"] == "completed"
        assert result["progress"] == 1.0
        assert "task_id" in result
        assert result["title"] == "Test Track"
        assert result["genre"] == "lofi"
        assert result["mood"] == "chill"

    @pytest.mark.asyncio
    async def test_fallback_has_tags_and_lyrics(self, service):
        result = await service.generate_music(
            title="Test", genre="lofi", mood="chill"
        )
        assert "tags" in result
        assert "lyrics" in result

    @pytest.mark.asyncio
    async def test_fallback_stores_task(self, service):
        result = await service.generate_music(
            title="Stored Task", genre="lofi", mood="chill"
        )
        task_id = result["task_id"]
        assert task_id in service._tasks

    @pytest.mark.asyncio
    async def test_fallback_with_all_params(self, service):
        result = await service.generate_music(
            title="Full", genre="hyper-pop", mood="energetic",
            duration=60, prompt="Custom prompt", tempo=140,
            key="C major", instruments=["synth"],
        )
        assert result["duration"] == 60
        assert "synth" in result["tags"]

    @pytest.mark.asyncio
    async def test_unique_task_ids(self, service):
        r1 = await service.generate_music(title="T1", genre="lofi", mood="chill")
        r2 = await service.generate_music(title="T2", genre="lofi", mood="chill")
        assert r1["task_id"] != r2["task_id"]


class TestGenerateMusicLocal:
    """Test generate_music with heartlib_path set (local mode)."""

    @pytest.mark.asyncio
    async def test_generate_local_success(self, service, tmp_path):
        """Test _generate_local when subprocess succeeds and creates output."""
        task_id = "localtest1"
        output_file = service.output_dir / f"{task_id}.mp3"

        # Create the output file to simulate successful generation
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Set heartlib_path so _generate_local doesn't bail early
        service.heartlib_path = "/opt/heartlib"

        async def fake_exec(*args, **kwargs):
            # Create output file to simulate success
            output_file.write_bytes(b"fake mp3 audio")
            proc = mock.MagicMock()
            proc.communicate = mock.AsyncMock(return_value=(b"", b""))
            proc.returncode = 0
            return proc

        with mock.patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
            result = await service._generate_local(
                task_id, "Test Song", "lofi,chill", "[Intro]\nTest", 30
            )

        assert result["status"] == "completed"
        assert result["progress"] == 1.0
        assert "audio_url" in result
        assert result["task_id"] == task_id

        # Cleanup
        output_file.unlink(missing_ok=True)
        service.heartlib_path = None

    @pytest.mark.asyncio
    async def test_generate_local_failure(self, service):
        """Test _generate_local when subprocess fails."""
        task_id = "localfail1"
        service.heartlib_path = "/opt/heartlib"

        async def fake_exec(*args, **kwargs):
            proc = mock.MagicMock()
            proc.communicate = mock.AsyncMock(return_value=(b"", b"Error: model not found"))
            proc.returncode = 1
            return proc

        with mock.patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
            result = await service._generate_local(
                task_id, "Fail Song", "pop", "[Intro]\nFail", 30
            )

        assert result["status"] == "failed"
        assert "error" in result
        assert result["task_id"] == task_id
        service.heartlib_path = None

    @pytest.mark.asyncio
    async def test_generate_local_timeout(self, service):
        """Test _generate_local when subprocess times out."""
        task_id = "localtimeout1"
        service.heartlib_path = "/opt/heartlib"

        async def fake_exec(*args, **kwargs):
            proc = mock.MagicMock()
            proc.communicate = mock.AsyncMock(side_effect=asyncio.TimeoutError())
            return proc

        with mock.patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
            result = await service._generate_local(
                task_id, "Timeout Song", "pop", "[Intro]\nTimeout", 30
            )

        assert result["status"] == "failed"
        assert "timed out" in result["error"].lower()
        service.heartlib_path = None

    @pytest.mark.asyncio
    async def test_generate_local_exception(self, service):
        """Test _generate_local when subprocess raises unexpected error."""
        task_id = "localexc1"
        service.heartlib_path = "/opt/heartlib"

        async def fake_exec(*args, **kwargs):
            raise OSError("Permission denied")

        with mock.patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
            result = await service._generate_local(
                task_id, "Exc Song", "pop", "[Intro]\nExc", 30
            )

        assert result["status"] == "failed"
        assert "Permission denied" in result["error"]
        service.heartlib_path = None

    @pytest.mark.asyncio
    async def test_generate_local_with_stderr(self, service):
        """Test _generate_local when subprocess fails with stderr output."""
        task_id = "localstderr1"
        service.heartlib_path = "/opt/heartlib"

        async def fake_exec(*args, **kwargs):
            proc = mock.MagicMock()
            proc.communicate = mock.AsyncMock(return_value=(b"", b"STDERR: something went wrong"))
            proc.returncode = 1
            return proc

        with mock.patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
            result = await service._generate_local(
                task_id, "Stderr Song", "pop", "[Intro]\nStderr", 30
            )

        assert result["status"] == "failed"
        assert "STDERR" in result["error"]
        service.heartlib_path = None

    @pytest.mark.asyncio
    async def test_generate_music_dispatches_to_local(self, service, tmp_path):
        """When heartlib_path is set, generate_music calls _generate_local."""
        service.heartlib_path = "/opt/heartlib"

        async def fake_exec(*args, **kwargs):
            # Extract task_id from the --save_path argument in cmd
            task_id_local = None
            for i, arg in enumerate(args):
                if str(arg) == "--save_path" and i + 1 < len(args):
                    save_path = Path(args[i + 1])
                    task_id_local = save_path.stem  # filename without .mp3
                    break

            # Create the output file so _generate_local sees it as success
            if task_id_local:
                of = service.output_dir / f"{task_id_local}.mp3"
                of.parent.mkdir(parents=True, exist_ok=True)
                of.write_bytes(b"test audio")

            proc = mock.MagicMock()
            proc.communicate = mock.AsyncMock(return_value=(b"", b""))
            proc.returncode = 0
            return proc

        try:
            with mock.patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
                result = await service.generate_music(
                    title="Local Dispatch Test",
                    genre="lofi",
                    mood="chill",
                    duration=30,
                )
            assert result["status"] == "completed"
            assert result["progress"] == 1.0
        finally:
            # Cleanup generated files
            for f in service.output_dir.glob("*.mp3"):
                f.unlink(missing_ok=True)
            service.heartlib_path = None


class TestGetStatus:
    """Test get_status."""

    @pytest.mark.asyncio
    async def test_get_status_found(self, service):
        result = await service.generate_music(title="Status Test", genre="lofi", mood="chill")
        task_id = result["task_id"]

        status = await service.get_status(task_id)
        assert status["task_id"] == task_id
        assert status["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_status_not_found(self, service):
        status = await service.get_status("nonexistent-task-id")
        assert status["status"] == "not_found"
        assert "not found" in status["message"]


class TestListTasks:
    """Test list_tasks."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, service):
        result = await service.list_tasks()
        assert result["total"] == 0
        assert result["items"] == []

    @pytest.mark.asyncio
    async def test_list_tasks_after_generate(self, service):
        await service.generate_music(title="Task1", genre="lofi", mood="chill")
        await service.generate_music(title="Task2", genre="lofi", mood="chill")

        result = await service.list_tasks()
        assert result["total"] == 2
        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_list_tasks_pagination(self, service):
        for i in range(5):
            await service.generate_music(title=f"Pag{i}", genre="lofi", mood="chill")

        result = await service.list_tasks(limit=2, offset=0)
        assert len(result["items"]) == 2
        assert result["total"] == 5

        result2 = await service.list_tasks(limit=2, offset=2)
        assert len(result2["items"]) == 2

    @pytest.mark.asyncio
    async def test_list_tasks_sorted_by_created_at_desc(self, service):
        await service.generate_music(title="First", genre="lofi", mood="chill")
        await service.generate_music(title="Second", genre="lofi", mood="chill")

        result = await service.list_tasks()
        # Most recent first
        assert result["items"][0]["title"] == "Second"
        assert result["items"][1]["title"] == "First"


class TestGetAudio:
    """Test get_audio."""

    @pytest.mark.asyncio
    async def test_get_audio_no_file(self, service):
        result = await service.get_audio("nonexistent-task-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_audio_with_file(self, service, tmp_path):
        """Test get_audio when an actual file exists."""
        task_id = "test-audio-file"
        # Write a fake audio file
        audio_dir = service.output_dir
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = audio_dir / f"{task_id}.mp3"
        audio_path.write_bytes(b"fake mp3 data")

        result = await service.get_audio(task_id)
        assert result == b"fake mp3 data"

        # Cleanup
        audio_path.unlink(missing_ok=True)


class TestFindHeartlib:
    """Test _find_heartlib."""

    def test_heartlib_not_found_by_default(self):
        svc = HeartMuLaService()
        # In test environment, heartlib is not installed
        assert svc.heartlib_path is None

    def test_heartlib_found_if_dir_exists(self):
        with mock.patch("os.path.isdir") as mock_isdir:
            mock_isdir.side_effect = lambda p: p == os.path.expanduser("~/heartlib")
            svc = HeartMuLaService()
            assert svc.heartlib_path == os.path.expanduser("~/heartlib")
