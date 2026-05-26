"""Music generation routes — HeartMuLa-powered AI music generation."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import sys
from pathlib import Path

# Add ai/ to path for service imports
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
    """Request model for music generation."""
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
        logger.info(f"Music generation request: {request.title} ({request.genre}/{request.mood})")

        if request.duration < 10 or request.duration > 600:
            raise HTTPException(status_code=400, detail="Duration must be between 10 and 600 seconds")

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

        logger.info(f"Music generation result: {result.get('task_id')} — {result.get('status')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Music generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_generation_status(task_id: str):
    """Get music generation status."""
    logger.info(f"Status request: {task_id}")
    result = await heartmula_service.get_status(task_id)

    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return result


@router.get("/download/{task_id}")
async def download_music(task_id: str):
    """Download generated music file."""
    logger.info(f"Download request: {task_id}")

    audio_bytes = await heartmula_service.get_audio(task_id)
    if audio_bytes:
        audio_path = Path("uploads/music") / f"{task_id}.mp3"
        return FileResponse(
            path=str(audio_path),
            media_type="audio/mpeg",
            filename=f"{task_id}.mp3",
        )

    raise HTTPException(status_code=404, detail=f"Audio for task {task_id} not found")


@router.get("/genres")
async def list_genres():
    """List available music genres and moods."""
    return {
        "genres": [g.value for g in Genre],
        "moods": [m.value for m in Mood],
    }


@router.get("/history")
async def get_generation_history(limit: int = 20, offset: int = 0):
    """Get music generation history."""
    return await heartmula_service.list_tasks(limit, offset)
