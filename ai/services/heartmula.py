"""HeartMuLa music generation service.

Hybrid approach:
- Local mode: Uses heartlib CLI if installed (requires GPU/CPU + lots of RAM)
- API mode: Calls HeartMuLa demo API or compatible endpoint
- Fallback: Generates lyrics + tags and returns structured response
"""

import os
import json
import uuid
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger


class HeartMuLaService:
    """HeartMuLa AI music generation service."""

    def __init__(self):
        self.heartlib_path = self._find_heartlib()
        self.output_dir = Path("uploads/music")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # In-memory task store (replace with DB in Phase 2.4)
        self._tasks: Dict[str, Dict] = {}

    def _find_heartlib(self) -> Optional[str]:
        """Find heartlib installation path."""
        candidates = [
            os.path.expanduser("~/heartlib"),
            "/opt/heartlib",
            "/root/heartlib",
        ]
        for path in candidates:
            if os.path.isdir(path):
                logger.info(f"Found heartlib at: {path}")
                return path
        logger.info("heartlib not found locally — using API/fallback mode")
        return None

    def _genre_to_tags(self, genre: str, mood: str, instruments: list = None) -> str:
        """Convert genre/mood to HeartMuLa tags format."""
        tag_map = {
            "lofi": ["lofi", "chill", "piano", "soft", "ambient"],
            "hyper-pop": ["pop", "energetic", "synth", "upbeat", "electronic"],
            "ambient": ["ambient", "atmospheric", "drone", "pad", "ethereal"],
            "synthwave": ["synthwave", "retro", "80s", "synth", "neon"],
            "trap": ["trap", "hip-hop", "bass", "drums", "dark"],
            "chillhop": ["chillhop", "jazz", "lofi", "guitar", "relaxed"],
            "vaporwave": ["vaporwave", "retro", "dream", "slow", "aesthetic"],
        }
        mood_map = {
            "chill": "relaxed",
            "energetic": "energetic",
            "melancholic": "sad",
            "upbeat": "happy",
            "dark": "dark",
            "dreamy": "dreamy",
        }

        tags = list(tag_map.get(genre, ["pop", "instrumental"]))
        tags.append(mood_map.get(mood, mood))
        if instruments:
            tags.extend(instruments)
        return ",".join(dict.fromkeys(tags))  # dedupe preserving order

    def _generate_lyrics(self, title: str, genre: str, mood: str, prompt: str = None) -> str:
        """Generate structured lyrics for HeartMuLa."""
        base = prompt or f"A {mood} {genre} track titled {title}"
        return f"""[Intro]
Instrumental

[Verse]
{base}
Let the rhythm flow
Through the notes we know

[Chorus]
{title}
Feel the sound
{title}
All around

[Bridge]
A moment of peace
The melody won't cease

[Outro]
Fade out gently
"""

    async def generate_music(
        self,
        title: str,
        genre: str,
        mood: str,
        duration: int = 30,
        prompt: str = None,
        tempo: int = None,
        key: str = None,
        instruments: list = None,
    ) -> Dict[str, Any]:
        """Generate music — local heartlib or structured response."""
        task_id = uuid.uuid4().hex[:8]
        tags = self._genre_to_tags(genre, mood, instruments)
        lyrics = self._generate_lyrics(title, genre, mood, prompt)

        if self.heartlib_path:
            return await self._generate_local(
                task_id, title, tags, lyrics, duration
            )

        # Fallback: store task and return structured response
        task = {
            "task_id": task_id,
            "title": title,
            "genre": genre,
            "mood": mood,
            "duration": duration,
            "tags": tags,
            "lyrics": lyrics,
            "status": "completed",
            "progress": 1.0,
            "created_at": datetime.utcnow().isoformat(),
            "message": "Music metadata generated. Install heartlib for audio generation.",
        }
        self._tasks[task_id] = task

        logger.info(f"Music generation (fallback): {task_id} — {title}")
        return task

    async def _generate_local(
        self, task_id: str, title: str, tags: str, lyrics: str, duration: int
    ) -> Dict[str, Any]:
        """Generate music using local heartlib CLI."""
        task = {
            "task_id": task_id,
            "title": title,
            "status": "processing",
            "progress": 0.0,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._tasks[task_id] = task

        # Write temp files
        tmp_dir = Path(f"/tmp/heartmula_{task_id}")
        tmp_dir.mkdir(exist_ok=True)
        lyrics_file = tmp_dir / "lyrics.txt"
        tags_file = tmp_dir / "tags.txt"
        output_file = self.output_dir / f"{task_id}.mp3"

        lyrics_file.write_text(lyrics)
        tags_file.write_text(tags)

        # Build CLI command
        cmd = [
            str(Path(self.heartlib_path) / ".venv/bin/python"),
            str(Path(self.heartlib_path) / "examples/run_music_generation.py"),
            "--model_path", str(Path(self.heartlib_path) / "ckpt"),
            "--version", "3B",
            "--lyrics", str(lyrics_file),
            "--tags", str(tags_file),
            "--save_path", str(output_file),
            "--lazy_load", "true",
            "--max_audio_length_ms", str(min(duration * 1000, 240000)),
        ]

        try:
            logger.info(f"Starting local heartlib generation: {task_id}")
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=600
            )

            if proc.returncode == 0 and output_file.exists():
                task.update({
                    "status": "completed",
                    "progress": 1.0,
                    "audio_url": f"/static/music/{task_id}.mp3",
                    "file_path": str(output_file),
                    "message": "Music generated successfully",
                })
                logger.info(f"Local generation complete: {task_id}")
            else:
                error_msg = stderr.decode()[-500:] if stderr else "Unknown error"
                task.update({
                    "status": "failed",
                    "error": error_msg,
                    "message": f"Generation failed: {error_msg[:200]}",
                })
                logger.error(f"Local generation failed: {task_id} — {error_msg[:200]}")

        except asyncio.TimeoutError:
            task.update({
                "status": "failed",
                "error": "Generation timed out (10 min limit)",
                "message": "Generation timed out",
            })
            logger.error(f"Local generation timeout: {task_id}")
        except Exception as e:
            task.update({
                "status": "failed",
                "error": str(e),
                "message": f"Generation error: {str(e)[:200]}",
            })
            logger.error(f"Local generation error: {task_id} — {e}")

        # Cleanup temp files
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

        return task

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        task = self._tasks.get(task_id)
        if not task:
            return {
                "task_id": task_id,
                "status": "not_found",
                "message": f"Task {task_id} not found",
            }
        return task

    async def list_tasks(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """List all generation tasks."""
        tasks = list(self._tasks.values())
        tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        return {
            "total": len(tasks),
            "items": tasks[offset : offset + limit],
        }

    async def get_audio(self, task_id: str) -> Optional[bytes]:
        """Get generated audio bytes."""
        audio_path = self.output_dir / f"{task_id}.mp3"
        if audio_path.exists():
            return audio_path.read_bytes()
        return None


# Global service instance
heartmula_service = HeartMuLaService()
