"""Music generation routes — AI-powered music generation endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import sys
from pathlib import Path

# Add ai/ to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.heartmula import heartmula_service

router = APIRouter()


class Genre(str, Enum):
    lofi = "lofi"
    hyper_pop = "hyper-pop"
    ambient = "ambient"
    synthwave = "synthwave"
    trap = "trap"
    chillhop = "chillhop"
    vaporwave = "vaporwave"


class Mood(str, Enum):
    chill = "chill"
    energetic = "energetic"
    melancholic = "melancholic"
    upbeat = "upbeat"
    dark = "dark"
    dreamy = "dreamy"


class GenerateMusicRequest(BaseModel):
    title: str = "Untitled Track"
    genre: Genre = Genre.lofi
    mood: Mood = Mood.chill
    duration: int = 30
    tempo: Optional[int] = None
    key: Optional[str] = None
    instruments: Optional[List[str]] = None
    prompt: Optional[str] = None


@router.post("/generate")
async def generate_music(request: GenerateMusicRequest):
    """Generate music using HeartMuLa AI."""
    try:
        logger.info(f"Generate request: {request.title} ({request.genre}/{request.mood})")

        if request.duration < 10 or request.duration > 600:
            raise HTTPException(400, "Duration must be 10-600 seconds")

        result = await heartmula_service.generate_music(
            title=request.title,
            genre=request.genre.value,
            mood=request.mood.value,
            duration=request.duration,
            prompt=request.prompt,
            tempo=request.tempo,
            key=request.key,
            instruments=request.instruments,
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate error: {e}")
        raise HTTPException(500, str(e))


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get generation task status."""
    return await heartmula_service.get_status(task_id)


@router.get("/download/{task_id}")
async def download_music(task_id: str):
    """Download generated audio file."""
    audio = await heartmula_service.get_audio(task_id)
    if not audio:
        raise HTTPException(404, f"Audio for task {task_id} not found")
    return FileResponse(
        path=f"uploads/music/{task_id}.mp3",
        media_type="audio/mpeg",
        filename=f"{task_id}.mp3",
    )


@router.get("/genres")
async def list_genres():
    """List available genres and moods."""
    return {
        "genres": [g.value for g in Genre],
        "moods": [m.value for m in Mood],
    }


@router.get("/history")
async def get_history(limit: int = 20, offset: int = 0):
    """Get generation history."""
    return await heartmula_service.list_tasks(limit, offset)
