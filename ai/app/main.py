"""AI Music Producer — FastAPI Application Entry Point.

Run: cd ai && python -m app.main
Or:  cd ai && uvicorn app.main:app --reload --port 8001
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

# Add ai/ to path so routes can import services, models, config as top-level
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from routes import music, video, provider, presets
from config import settings
from services.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup & shutdown."""
    logger.info("Starting Auto LoFi Hyper Pop Music Producer AI Service")

    # Initialize database (create tables + seed providers)
    init_database()
    logger.info("Database initialized")

    yield

    logger.info("Shutting down Auto LoFi Hyper Pop Music Producer AI Service")


# Create FastAPI application
app = FastAPI(
    title="Auto LoFi Hyper Pop Music Producer AI",
    description="AI-powered music generation and learning platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(music.router, prefix="/api/v1", tags=["music"])
app.include_router(video.router, prefix="/api/v1", tags=["video"])
app.include_router(provider.router, prefix="/api/v1", tags=["provider"])
app.include_router(presets.router, prefix="/api/v1/music", tags=["presets"])


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Auto LoFi Hyper Pop Music Producer AI",
        "version": "0.1.0",
        "description": "AI-powered music generation platform",
        "endpoints": {
            "music": "/api/v1/music",
            "video": "/api/v1/video",
            "provider": "/api/v1/provider",
            "providers": "/api/v1/providers",
            "docs": "/docs",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Auto LoFi Hyper Pop Music Producer AI",
        "version": "0.1.0",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
