# Test Fixtures
import asyncio
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import redis
from loguru import logger

# Import application
from ai.app.main import app
from ai.config import settings
from ai.services.database import get_db
from ai.services.music_ai_service import MusicAIService
from ai.services.audio_feature_extractor import AudioFeatureExtractor
from ai.services.video_analysis import VideoAnalysisService
from ai.services.provider_service import ProviderService
from ai.services.heartmula import HeartMuLaService

# Test Configuration
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_REDIS_URL = "redis://localhost:6379/1"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_app():
    """Create a test FastAPI application."""
    # Override database settings for testing
    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.REDIS_URL = TEST_REDIS_URL
    settings.DEBUG = True
    settings.TESTING = True
    
    return app

@pytest.fixture
def client(test_app):
    """Create a test client for the FastAPI application."""
    return TestClient(test_app)

@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def test_db_session_factory(test_db_engine):
    """Create a test database session factory."""
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    return TestSession

@pytest.fixture
def test_db(test_db_session_factory):
    """Create a test database session."""
    session = test_db_session_factory()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def override_get_db(test_db):
    """Override the database dependency for testing."""
    def _override_get_db():
        try:
            yield test_db
        finally:
            pass
    return _override_get_db

@pytest.fixture
def test_redis():
    """Create a test Redis connection."""
    try:
        redis_client = redis.from_url(TEST_REDIS_URL, db=1)
        yield redis_client
        # Clean up test data
        redis_client.flushdb()
        redis_client.close()
    except redis.ConnectionError:
        # Skip Redis tests if not available
        pytest.skip("Redis not available for testing")

@pytest.fixture
def temp_directory():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def test_audio_file(temp_directory):
    """Create a test audio file."""
    audio_file = temp_directory / "test_audio.mp3"
    # Create a minimal MP3 file (header only for testing)
    with open(audio_file, 'wb') as f:
        # Write minimal MP3 header
        f.write(b'\xFF\xFB\x90\x00')  # Simplified MP3 header
    return str(audio_file)

@pytest.fixture
def test_video_file(temp_directory):
    """Create a test video file."""
    video_file = temp_directory / "test_video.mp4"
    # Create a minimal MP4 file (header only for testing)
    with open(video_file, 'wb') as f:
        # Write minimal MP4 header
        f.write(b'\x00\x00\x00\x18ftypmp41')  # Simplified MP4 header
    return str(video_file)

@pytest.fixture
def test_music_request():
    """Create a test music generation request."""
    from ai.models.responses import GenerateMusicRequest, Genre, Mood
    
    return GenerateMusicRequest(
        title="Test Music",
        genre=Genre.LOFI,
        mood=Mood.CHILL,
        duration=60,
        prompt="Test prompt for music generation",
        tempo=None,
        key=None,
        instruments=None
    )

@pytest.fixture
def test_video_request():
    """Create a test video analysis request."""
    from ai.models.responses import AnalyzeVideoRequest
    
    return AnalyzeVideoRequest(
        video_url="https://youtube.com/watch?v=test",
        title="Test Video Tutorial",
        description="A test video for analysis",
        focus_type="rhythm",
        extract_audio=True,
        analyze_patterns=True
    )

@pytest.fixture
def mock_music_ai_service():
    """Create a mock Music AI Service."""
    mock_service = Mock(spec=MusicAIService)
    
    # Mock async methods
    mock_service.generate_music_concepts = AsyncMock(return_value={
        "success": True,
        "concepts": {
            "rhythm": ["steady beat", "relaxed tempo"],
            "melody": ["simple melodies", "repetitive patterns"],
            "harmony": ["basic chords", "minimal changes"],
            "structure": ["verse-chorus", "predictable form"]
        }
    })
    
    mock_service.enhance_music_prompt = AsyncMock(return_value={
        "success": True,
        "enhanced_prompt": "Enhanced: A relaxing lofi track with steady beats and simple melodies, perfect for studying or chilling. Features gentle percussion, soft synth pads, and minimal harmonic changes to maintain a calm atmosphere.",
        "enhancements": [
            "Added specific texture descriptions",
            "Enhanced rhythmic detail",
            "Added harmonic context",
            "Improved mood specificity"
        ]
    })
    
    mock_service.get_optimal_generation_parameters = AsyncMock(return_value={
        "success": True,
        "parameters": {
            "tempo": 85,
            "key": "C Major",
            "instrumentation": [
                "Electric Piano",
                "Synth Pad",
                "Drum Machine",
                "Bass Synth"
            ],
            "duration_structure": {
                "intro": 8,
                "verse": 16,
                "chorus": 16,
                "outro": 8
            }
        },
        "confidence": 0.85
    })
    
    mock_service.generate_music_theory_advice = AsyncMock(return_value={
        "success": True,
        "advice": {
            "chord_progressions": ["C-Am-F-G", "Am-G-C-F"],
            "scale_options": ["C Major Pentatonic", "A Minor"],
            "rhythm_patterns": ["8th note hi-hats", "kick on 1 and 3"],
            "production_tips": [
                "Use sidechain compression for that classic lofi pump",
                "Add vinyl crackle for authenticity",
                "Keep bass frequencies below 100Hz",
                "Use warm analog-style EQ"
            ]
        }
    })
    
    return mock_service

@pytest.fixture
def mock_audio_feature_extractor():
    """Create a mock Audio Feature Extractor."""
    mock_service = Mock(spec=AudioFeatureExtractor)
    
    # Mock async methods
    mock_service.extract_comprehensive_features = AsyncMock(return_value={
        "success": True,
        "features": {
            "rhythm": {
                "tempo": 120.5,
                "beat_strength": 0.8,
                "rhythm_complexity": 0.6,
                "syncopation": 0.3
            },
            "melody": {
                "pitch_range": 12,
                "melodic_contour": "ascending-descending",
                "pitch_class_histogram": [0.2, 0.1, 0.15, 0.05, 0.1, 0.05, 0.15, 0.1, 0.05, 0.05, 0.05, 0.0],
                "tonal_strength": 0.75
            },
            "harmony": {
                "chroma_features": [0.3, 0.1, 0.2, 0.05, 0.15, 0.05, 0.1, 0.05, 0.0, 0.05, 0.0, 0.0],
                "key_strength": 0.85,
                "estimated_key": "C Major",
                "harmonic_complexity": 0.4
            },
            "timbre": {
                "spectral_centroid": 2500.0,
                "spectral_bandwidth": 1200.0,
                "spectral_rolloff": 3000.0,
                "zero_crossing_rate": 0.05,
                "mfcc": [i * 0.1 for i in range(13)]
            },
            "structure": {
                "segments": 4,
                "segment_similarity": 0.7,
                "form_type": "verse-chorus",
                "repetition_score": 0.8
            }
        },
        "metadata": {
            "duration": 30.0,
            "sample_rate": 22050,
            "channels": 2,
            "bit_depth": 16
        }
    })
    
    mock_service.extract_rhythm_features = AsyncMock(return_value={
        "success": True,
        "tempo": 120.5,
        "beat_times": [0.5, 1.0, 1.5, 2.0],
        "beat_strength": 0.8,
        "rhythm_complexity": 0.6
    })
    
    mock_service.extract_melody_features = AsyncMock(return_value={
        "success": True,
        "pitch_contour": [60, 62, 64, 65, 64, 62, 60],
        "melodic_intervals": [2, 2, 1, -1, -2, -2],
        "pitch_class_distribution": [0.3, 0.1, 0.2, 0.05, 0.15, 0.05, 0.1, 0.05, 0.0, 0.05, 0.0, 0.0],
        "tonal_centroid": [0.8, 0.2, 0.1]
    })
    
    return mock_service

@pytest.fixture
def mock_video_analysis_service():
    """Create a mock Video Analysis Service."""
    mock_service = Mock(spec=VideoAnalysisService)
    
    # Mock async methods
    mock_service.analyze_video_tutorial = AsyncMock(return_value={
        "success": True,
        "analysis": {
            "video_info": {
                "title": "Test Video Tutorial",
                "duration": 180.0,
                "resolution": "1920x1080",
                "fps": 30
            },
            "audio_analysis": {
                "duration": 180.0,
                "sample_rate": 44100,
                "channels": 2,
                "tempo": 120.0,
                "key": "C Major"
            },
            "musical_elements": {
                "rhythm": {
                    "patterns": ["steady beat", "4/4 time"],
                    "complexity": "low",
                    "instruments": ["drums", "bass"]
                },
                "melody": {
                    "scale": "C Major",
                    "range": "one octave",
                    "characteristics": ["simple", "repetitive"]
                },
                "harmony": {
                    "chords": ["C", "Am", "F", "G"],
                    "progression": "I-vi-IV-V",
                    "complexity": "basic"
                }
            },
            "learning_patterns": {
                "techniques": [
                    {
                        "name": "Basic Strumming",
                        "description": "Simple down-up strumming pattern",
                        "confidence": 0.9,
                        "timestamp": [30, 45]
                    },
                    {
                        "name": "Chord Transition",
                        "description": "Smooth C to Am transition",
                        "confidence": 0.85,
                        "timestamp": [60, 75]
                    }
                ],
                "exercises": [
                    {
                        "title": "Practice Strumming",
                        "instructions": "Practice the basic strumming pattern slowly",
                        "duration": 10,
                        "difficulty": "beginner"
                    }
                ]
            }
        }
    })
    
    mock_service.extract_audio_from_video = AsyncMock(return_value={
        "success": True,
        "audio_path": "/tmp/test_audio.wav",
        "duration": 180.0,
        "format": "wav",
        "sample_rate": 44100
    })
    
    return mock_service

@pytest.fixture
def mock_provider_service():
    """Create a mock Provider Service."""
    mock_service = Mock(spec=ProviderService)
    
    # Mock async methods
    mock_service.get_provider_status = AsyncMock(return_value={
        "success": True,
        "providers": {
            "anthropic": {
                "name": "Anthropic Claude",
                "status": "available",
                "models": ["claude-3-sonnet", "claude-3-opus"],
                "latency": 1.2,
                "success_rate": 0.98
            },
            "openai": {
                "name": "OpenAI",
                "status": "available", 
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "latency": 0.8,
                "success_rate": 0.99
            }
        },
        "total_providers": 2,
        "available_providers": 2
    })
    
    mock_service.route_to_provider = AsyncMock(return_value={
        "success": True,
        "provider": "anthropic",
        "model": "claude-3-sonnet",
        "response": "Mock AI response for testing",
        "latency": 1.2,
        "tokens_used": 150
    })
    
    mock_service.test_model_routing = AsyncMock(return_value={
        "success": True,
        "routing_results": [
            {
                "task_type": "music_theory",
                "selected_provider": "openai",
                "selected_model": "gpt-4",
                "confidence": 0.9
            },
            {
                "task_type": "creative_content",
                "selected_provider": "anthropic", 
                "selected_model": "claude-3-sonnet",
                "confidence": 0.85
            }
        ],
        "routing_accuracy": 0.875
    })
    
    return mock_service

@pytest.fixture
def mock_heartmula_service():
    """Create a mock HeartMuLa Service."""
    mock_service = Mock(spec=HeartMuLaService)
    
    # Mock async methods
    mock_service.generate_music = AsyncMock(return_value={
        "success": True,
        "task_id": "test_task_123",
        "estimated_time": 30,
        "status": "processing",
        "message": "Music generation started"
    })
    
    mock_service.check_generation_status = AsyncMock(return_value={
        "success": True,
        "task_id": "test_task_123",
        "status": "completed",
        "progress": 100,
        "result_url": "https://heartmula.com/music/test_task_123.mp3",
        "download_url": "https://heartmula.com/download/test_task_123",
        "metadata": {
            "duration": 60,
            "format": "mp3",
            "size": 2400000,
            "bitrate": 320
        }
    })
    
    mock_service.get_music_details = AsyncMock(return_value={
        "success": True,
        "music_id": "test_task_123",
        "title": "Test Music",
        "artist": "AI Generator",
        "genre": "lofi",
        "mood": "chill",
        "duration": 60,
        "audio_url": "https://heartmula.com/music/test_task_123.mp3",
        "waveform_url": "https://heartmula.com/waveform/test_task_123.png",
        "metadata": {
            "bpm": 85,
            "key": "C Major",
            "instruments": ["Piano", "Drums", "Bass"],
            "created_at": "2024-01-01T00:00:00Z"
        }
    })
    
    return mock_service

@pytest.fixture
def mock_openrouter_client():
    """Create a mock OpenRouter client."""
    mock_client = Mock()
    
    mock_client.chat.completions.create = AsyncMock(return_value={
        "id": "test_completion_123",
        "object": "chat.completion",
        "created": 1640995200,
        "model": "claude-3-sonnet",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Mock AI response for testing purposes. This is a simulated response from the OpenRouter API."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150
        }
    })
    
    return mock_client

@pytest.fixture
def mock_responses():
    """Create a mock responses fixture for HTTP requests."""
    import respx
    
    with respx.mock(assert_all_called=False) as mock:
        # Mock OpenRouter API
        mock.post("https://openrouter.ai/api/v1/chat/completions").respond(
            200,
            json={
                "id": "test_completion_123",
                "object": "chat.completion",
                "created": 1640995200,
                "model": "claude-3-sonnet",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Mock OpenRouter response"
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 100,
                    "total_tokens": 150
                }
            }
        )
        
        # Mock HeartMuLa API
        mock.post("https://api.heartmula.com/v1/generate").respond(
            200,
            json={
                "success": True,
                "task_id": "test_task_123",
                "estimated_time": 30
            }
        )
        
        # Mock GLM Web Search API
        mock.post("https://glm.web.search/api/v1/search").respond(
            200,
            json={
                "success": True,
                "results": [
                    {
                        "title": "Music Trends 2024",
                        "url": "https://example.com/music-trends",
                        "snippet": "Latest music production trends and techniques"
                    }
                ]
            }
        )
        
        yield mock

@pytest.fixture
def test_data_directory():
    """Create test data directory structure."""
    data_dir = Path(__file__).parent / "test_data"
    data_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (data_dir / "audio").mkdir(exist_ok=True)
    (data_dir / "video").mkdir(exist_ok=True)
    (data_dir / "uploads").mkdir(exist_ok=True)
    (data_dir / "cache").mkdir(exist_ok=True)
    
    return data_dir

@pytest.fixture
def sample_audio_data():
    """Create sample audio data for testing."""
    import numpy as np
    
    # Generate simple sine wave audio data
    sample_rate = 22050
    duration = 1.0  # 1 second
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    return {
        "audio_data": audio_data,
        "sample_rate": sample_rate,
        "duration": duration,
        "frequency": frequency
    }

@pytest.fixture
def sample_video_metadata():
    """Create sample video metadata for testing."""
    return {
        "title": "Test Video Tutorial",
        "description": "A comprehensive guitar tutorial for beginners",
        "duration": 300.0,
        "view_count": 10000,
        "like_count": 500,
        "channel": "Guitar Master",
        "publish_date": "2024-01-01T00:00:00Z",
        "tags": ["guitar", "tutorial", "beginner", "music"],
        "category": "Music"
    }

@pytest.fixture
def benchmark_config():
    """Create benchmark configuration for performance testing."""
    return {
        "iterations": 10,
        "warmup": 2,
        "max_time": 30.0,
        "min_rounds": 5,
        "max_time_per_round": 10.0
    }