"""Music generation routes - AI-powered music generation endpoints."""

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

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


class MusicGenerationResponse(BaseModel):
    """Response model for music generation."""
    task_id: str
    status: str = "pending"
    message: str
    title: str
    genre: str
    mood: str
    duration: int


class MusicGenerationStatus(BaseModel):
    """Status response for generation task."""
    task_id: str
    status: str
    progress: float = 0.0
    message: Optional[str] = None
    audio_url: Optional[str] = None


@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(request: GenerateMusicRequest):
    """Generate music using AI (HeartMuLa integration)."""
    try:
        logger.info(f"Music generation request: {request.title} ({request.genre}/{request.mood})")

        # Validate
        if request.duration < 10 or request.duration > 600:
            raise HTTPException(status_code=400, detail="Duration must be between 10 and 600 seconds")

        # TODO: Connect to HeartMuLa service for actual generation
        # For now, return a mock task
        import uuid
        task_id = str(uuid.uuid4())[:8]

        return MusicGenerationResponse(
            task_id=task_id,
            status="pending",
            message="Music generation queued. HeartMuLa integration coming in Phase 2.2.",
            title=request.title,
            genre=request.genre.value,
            mood=request.mood.value,
            duration=request.duration,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Music generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=MusicGenerationStatus)
async def get_generation_status(task_id: str):
    """Get music generation status."""
    logger.info(f"Status request: {task_id}")

    # TODO: Query actual task status from HeartMuLa
    return MusicGenerationStatus(
        task_id=task_id,
        status="pending",
        progress=0.0,
        message="Task status tracking coming soon.",
    )


@router.get("/download/{task_id}")
async def download_music(task_id: str):
    """Download generated music file."""
    logger.info(f"Download request: {task_id}")

    # TODO: Serve actual generated file
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Download will be available after HeartMuLa integration.",
    }


@router.get("/genres")
async def list_genres():
    """List available music genres."""
    return {
        "genres": [g.value for g in Genre],
        "moods": [m.value for m in Mood],
    }


@router.get("/history")
async def get_generation_history(limit: int = 20, offset: int = 0):
    """Get music generation history."""
    # TODO: Query from database
    return {
        "total": 0,
        "items": [],
        "message": "History tracking coming with database integration.",
    }
