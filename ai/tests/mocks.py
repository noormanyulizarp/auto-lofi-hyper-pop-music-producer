# Test Mocks and Utilities
import json
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List, Optional
import numpy as np

# OpenRouter API Mocks
class MockOpenRouterClient:
    """Mock OpenRouter client for testing."""
    
    def __init__(self):
        self.chat = Mock()
        self.chat.completions = Mock()
        self.chat.completions.create = AsyncMock()
        
        # Default successful response
        self._set_default_response()
    
    def _set_default_response(self):
        """Set default successful response."""
        self.chat.completions.create.return_value = {
            "id": "chatcmpl-123456789",
            "object": "chat.completion",
            "created": 1640995200,
            "model": "claude-3-sonnet",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a mock response from OpenRouter for testing purposes."
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
    
    def set_custom_response(self, content: str, model: str = "claude-3-sonnet", 
                           tokens: int = 100):
        """Set custom response for testing."""
        self.chat.completions.create.return_value = {
            "id": "chatcmpl-custom",
            "object": "chat.completion",
            "created": 1640995200,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": tokens,
                "total_tokens": 50 + tokens
            }
        }
    
    def set_error_response(self, error_message: str, status_code: int = 400):
        """Set error response for testing."""
        self.chat.completions.create.side_effect = Exception(error_message)

# HeartMuLa API Mocks
class MockHeartMuLaClient:
    """Mock HeartMuLa client for testing."""
    
    def __init__(self):
        self.generate = AsyncMock()
        self.status = AsyncMock()
        self.download = AsyncMock()
        self.details = AsyncMock()
        
        # Set default responses
        self._set_default_responses()
    
    def _set_default_responses(self):
        """Set default successful responses."""
        task_id = "heartmula_task_123"
        
        # Generate response
        self.generate.return_value = {
            "success": True,
            "task_id": task_id,
            "estimated_time": 30,
            "status": "processing",
            "message": "Music generation started successfully"
        }
        
        # Status response
        self.status.return_value = {
            "success": True,
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "result_url": f"https://heartmula.com/music/{task_id}.mp3",
            "download_url": f"https://heartmula.com/download/{task_id}",
            "metadata": {
                "duration": 60,
                "format": "mp3",
                "size": 2400000,
                "bitrate": 320
            }
        }
        
        # Details response
        self.details.return_value = {
            "success": True,
            "music_id": task_id,
            "title": "Test Music",
            "artist": "AI Generator",
            "genre": "lofi",
            "mood": "chill",
            "duration": 60,
            "audio_url": f"https://heartmula.com/music/{task_id}.mp3",
            "waveform_url": f"https://heartmula.com/waveform/{task_id}.png",
            "metadata": {
                "bpm": 85,
                "key": "C Major",
                "instruments": ["Piano", "Drums", "Bass"],
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    
    def set_processing_status(self, progress: int = 50):
        """Set processing status response."""
        self.status.return_value = {
            "success": True,
            "task_id": "heartmula_task_123",
            "status": "processing",
            "progress": progress,
            "message": f"Processing: {progress}% complete"
        }
    
    def set_error_response(self, error_message: str):
        """Set error response for testing."""
        self.generate.side_effect = Exception(error_message)
        self.status.side_effect = Exception(error_message)

# GLM Service Mocks
class MockGLMClient:
    """Mock GLM client for testing."""
    
    def __init__(self):
        self.search = AsyncMock()
        self.reader = AsyncMock()
        
        # Set default responses
        self._set_default_responses()
    
    def _set_default_responses(self):
        """Set default successful responses."""
        # Search response
        self.search.return_value = {
            "success": True,
            "query": "music trends 2024",
            "results": [
                {
                    "title": "Music Production Trends 2024",
                    "url": "https://example.com/music-trends-2024",
                    "snippet": "The latest trends in music production include AI-generated music, immersive audio experiences, and genre-blending compositions.",
                    "content": "Full article content about music trends..."
                },
                {
                    "title": "LoFi Music Production Techniques",
                    "url": "https://example.com/lofi-techniques",
                    "snippet": "Essential techniques for producing authentic LoFi music including vinyl crackle, sample selection, and mixing tips.",
                    "content": "Detailed guide on LoFi production..."
                }
            ],
            "total_results": 2,
            "search_time": 0.5
        }
        
        # Reader response
        self.reader.return_value = {
            "success": True,
            "url": "https://example.com/music-trends-2024",
            "title": "Music Production Trends 2024",
            "content": """
            Music Production Trends for 2024
            
            1. AI-Generated Music: Artificial intelligence is revolutionizing music creation, enabling artists to generate complex compositions and explore new creative possibilities.
            
            2. Immersive Audio: Spatial audio and 3D sound experiences are becoming increasingly popular, especially in gaming and virtual reality applications.
            
            3. Genre Blending: Artists are increasingly mixing traditional genres with electronic elements, creating unique hybrid styles.
            
            4. Sustainable Production: Eco-friendly production methods and digital-only releases are reducing the environmental impact of music creation.
            """,
            "word_count": 150,
            "reading_time": 1.2
        }
    
    def set_empty_search_results(self):
        """Set empty search results."""
        self.search.return_value = {
            "success": True,
            "query": "obscure music query",
            "results": [],
            "total_results": 0,
            "search_time": 0.3
        }
    
    def set_reader_error(self, error_message: str):
        """Set reader error response."""
        self.reader.side_effect = Exception(error_message)

# Audio Processing Mocks
class MockLibrosaLoader:
    """Mock librosa functions for testing."""
    
    def __init__(self):
        self.load = Mock(return_value=np.random.randn(22050))  # 1 second of audio
        self.feature = Mock()
        self.beat = Mock()
        self.pitch = Mock()
        self.tonnetz = Mock()
        self.chroma = Mock()
        self.tempogram = Mock()
        
        # Set default feature values
        self._set_default_features()
    
    def _set_default_features(self):
        """Set default feature values."""
        # Tempo and beat tracking
        self.beat.tempo = Mock(return_value=120.0)
        self.beat.beat_track = Mock(return_value=(np.array([0, 1, 2]), np.array([0.5, 1.0, 1.5])))
        
        # Pitch detection
        self.pitch.pitch_tuning = Mock(return_value=440.0)
        self.pitch.piptrack = Mock(return_value=(np.random.rand(128, 100), np.random.rand(128, 100)))
        
        # Chroma features
        self.chroma.stft = Mock(return_value=np.random.rand(12, 100))
        
        # Spectral features
        self.feature.spectral_centroid = Mock(return_value=np.array([2500.0]))
        self.feature.spectral_bandwidth = Mock(return_value=np.array([1200.0]))
        self.feature.spectral_rolloff = Mock(return_value=np.array([3000.0]))
        self.feature.zero_crossing_rate = Mock(return_value=np.array([0.05]))
        self.feature.mfcc = Mock(return_value=np.random.rand(13, 100))
        
        # Temporal features
        self.tempogram = Mock(return_value=np.random.rand(384, 100))
        
        # Tonnetz
        self.tonnetz.tonnetz = Mock(return_value=np.random.rand(6, 100))

# Video Processing Mocks
class MockVideoProcessor:
    """Mock video processing functions for testing."""
    
    def __init__(self):
        self.extract_audio = Mock()
        self.get_video_info = Mock()
        self.read_frames = Mock()
        
        # Set default responses
        self._set_default_responses()
    
    def _set_default_responses(self):
        """Set default successful responses."""
        # Audio extraction
        self.extract_audio.return_value = {
            "success": True,
            "audio_path": "/tmp/extracted_audio.wav",
            "duration": 180.0,
            "sample_rate": 44100,
            "channels": 2
        }
        
        # Video info
        self.get_video_info.return_value = {
            "title": "Test Video Tutorial",
            "duration": 180.0,
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "codec": "h264",
            "format": "mp4"
        }
        
        # Frame reading
        self.read_frames.return_value = iter([
            np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
            for _ in range(10)  # 10 test frames
        ])

# Database Mocks
class MockDatabaseSession:
    """Mock database session for testing."""
    
    def __init__(self):
        self.query = Mock()
        self.add = Mock()
        self.commit = Mock()
        self.rollback = Mock()
        self.close = Mock()
        
        # Mock query results
        self._setup_query_mocks()
    
    def _setup_query_mocks(self):
        """Setup query method mocks."""
        mock_result = Mock()
        mock_result.filter = Mock(return_value=mock_result)
        mock_result.first = Mock(return_value=None)  # Default: no result found
        mock_result.all = Mock(return_value=[])
        mock_result.count = Mock(return_value=0)
        
        self.query.return_value = mock_result

class MockRedisClient:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.get = Mock(return_value=None)
        self.set = Mock(return_value=True)
        self.delete = Mock(return_value=1)
        self.exists = Mock(return_value=0)
        self.keys = Mock(return_value=[])
        self.flushdb = Mock(return_value=True)
        self.pipeline = Mock(return_value=self)
        self.execute = Mock(return_value=[True])
        
        # Mock pubsub
        self.pubsub = Mock()
        self.pubsub.subscribe = Mock(return_value=None)
        self.pubsub.listen = Mock(return_value=iter([]))

# HTTP Client Mocks
class MockHTTPClient:
    """Mock HTTP client for testing."""
    
    def __init__(self):
        self.get = AsyncMock()
        self.post = AsyncMock()
        self.put = AsyncMock()
        self.delete = AsyncMock()
        self.patch = AsyncMock()
        
        # Set default responses
        self._set_default_responses()
    
    def _set_default_responses(self):
        """Set default successful responses."""
        success_response = Mock()
        success_response.status_code = 200
        success_response.json = Mock(return_value={"success": True})
        success_response.text = "Success"
        success_response.content = b"Success content"
        
        for method in [self.get, self.post, self.put, self.delete, self.patch]:
            method.return_value = success_response
    
    def set_error_response(self, status_code: int = 500, error_message: str = "Internal Server Error"):
        """Set error response for all methods."""
        error_response = Mock()
        error_response.status_code = status_code
        error_response.json = Mock(return_value={"error": error_message})
        error_response.text = error_message
        error_response.content = error_message.encode()
        
        for method in [self.get, self.post, self.put, self.delete, self.patch]:
            method.return_value = error_response
    
    def set_timeout_response(self):
        """Set timeout response."""
        timeout_error = asyncio.TimeoutError("Request timeout")
        for method in [self.get, self.post, self.put, self.delete, self.patch]:
            method.side_effect = timeout_error

# File System Mocks
class MockFileSystem:
    """Mock file system operations for testing."""
    
    def __init__(self):
        self.exists = Mock(return_value=True)
        self.open = Mock()
        self.remove = Mock(return_value=None)
        self.makedirs = Mock(return_value=None)
        self.listdir = Mock(return_value=[])
        self.path = Mock()
        
        # Setup file handle mock
        self.file_handle = Mock()
        self.file_handle.read = Mock(return_value=b"mock file content")
        self.file_handle.write = Mock(return_value=None)
        self.file_handle.close = Mock(return_value=None)
        
        self.open.return_value.__enter__ = Mock(return_value=self.file_handle)
        self.open.return_value.__exit__ = Mock(return_value=None)

# Context Manager Mocks
class MockAsyncContextManager:
    """Mock async context manager for testing."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
        self.aenter_called = False
        self.aexit_called = False
    
    async def __aenter__(self):
        self.aenter_called = True
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.aexit_called = True
        return None

# Patch Decorators
def mock_openrouter():
    """Patch OpenRouter client."""
    return patch('ai.services.provider_service.OpenRouterClient', MockOpenRouterClient)

def mock_heartmula():
    """Patch HeartMuLa client."""
    return patch('ai.services.heartmula.HeartMuLaClient', MockHeartMuLaClient)

def mock_glm():
    """Patch GLM clients."""
    return [
        patch('ai.services.music_ai_service.GLMWebSearchClient', MockGLMClient),
        patch('ai.services.music_ai_service.GLMWebReaderClient', MockGLMClient)
    ]

def mock_librosa():
    """Patch librosa functions."""
    return patch('ai.services.audio_feature_extractor.librosa', MockLibrosaLoader)

def mock_video_processing():
    """Patch video processing functions."""
    return [
        patch('ai.services.video_analysis.moviepy', MockVideoProcessor),
        patch('ai.services.video_analysis.cv2', MockVideoProcessor)
    ]

def mock_database():
    """Patch database session."""
    return patch('ai.services.database.SessionLocal', MockDatabaseSession)

def mock_redis():
    """Patch Redis client."""
    return patch('ai.services.redis_client', MockRedisClient)

def mock_http_client():
    """Patch HTTP client."""
    return patch('ai.utils.http_client.HTTPClient', MockHTTPClient)

def mock_file_system():
    """Patch file system operations."""
    return [
        patch('os.path.exists', MockFileSystem().exists),
        patch('builtins.open', MockFileSystem().open),
        patch('os.makedirs', MockFileSystem().makedirs),
        patch('os.listdir', MockFileSystem().listdir)
    ]

# Utility Mocks
class MockLogger:
    """Mock logger for testing."""
    
    def __init__(self):
        self.info = Mock()
        self.debug = Mock()
        self.warning = Mock()
        self.error = Mock()
        self.critical = Mock()
        self.exception = Mock()
    
    def assert_called_with_info(self, message: str):
        """Assert that info was called with specific message."""
        self.info.assert_called_with(message)
    
    def assert_called_with_error(self, message: str):
        """Assert that error was called with specific message."""
        self.error.assert_called_with(message)

# Test Data Generators
def generate_test_music_concepts() -> Dict[str, Any]:
    """Generate test music concepts data."""
    return {
        "rhythm": ["steady beat", "syncopated rhythm", "polyrhythmic elements"],
        "melody": ["ascending scale", "contrasting motifs", "call and response"],
        "harmony": ["I-IV-V progression", "modal interchange", "extended chords"],
        "structure": ["ABA form", "verse-chorus", "through-composed"]
    }

def generate_test_audio_features() -> Dict[str, Any]:
    """Generate test audio features data."""
    return {
        "rhythm": {
            "tempo": 120.5,
            "beat_strength": 0.8,
            "rhythm_complexity": 0.6,
            "syncopation": 0.3
        },
        "melody": {
            "pitch_range": 12,
            "melodic_contour": "ascending-descending",
            "pitch_class_histogram": [0.2] * 12,
            "tonal_strength": 0.75
        },
        "harmony": {
            "chroma_features": [0.1] * 12,
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
    }

def generate_test_video_analysis() -> Dict[str, Any]:
    """Generate test video analysis data."""
    return {
        "video_info": {
            "title": "Advanced Guitar Tutorial",
            "duration": 600.0,
            "resolution": "1920x1080",
            "fps": 30
        },
        "audio_analysis": {
            "duration": 600.0,
            "sample_rate": 44100,
            "channels": 2,
            "tempo": 120.0,
            "key": "E Minor"
        },
        "musical_elements": {
            "rhythm": {
                "patterns": ["strumming pattern", "fingerpicking"],
                "complexity": "intermediate",
                "instruments": ["acoustic guitar", "voice"]
            },
            "melody": {
                "scale": "E Minor Pentatonic",
                "range": "two octaves",
                "characteristics": ["bluesy", "expressive"]
            },
            "harmony": {
                "chords": ["Em", "Am", "B7", "C"],
                "progression": "i-iv-VII-VI",
                "complexity": "intermediate"
            }
        },
        "learning_patterns": {
            "techniques": [
                {
                    "name": "Fingerpicking Pattern",
                    "description": " Travis picking technique",
                    "confidence": 0.95,
                    "timestamp": [120, 180]
                },
                {
                    "name": "Chord Embellishment",
                    "description": "Adding hammer-ons to chords",
                    "confidence": 0.88,
                    "timestamp": [240, 300]
                }
            ],
            "exercises": [
                {
                    "title": "Practice Travis Picking",
                    "instructions": "Slow practice of the fingerpicking pattern",
                    "duration": 15,
                    "difficulty": "intermediate"
                }
            ]
        }
    }

# Async Test Utilities
async def run_async_test(test_func, *args, **kwargs):
    """Utility to run async test functions."""
    try:
        return await test_func(*args, **kwargs)
    except Exception as e:
        return {"error": str(e), "success": False}

def create_async_mock(return_value=None, side_effect=None):
    """Create an async mock with specified return value or side effect."""
    mock = AsyncMock()
    if return_value is not None:
        mock.return_value = return_value
    if side_effect is not None:
        mock.side_effect = side_effect
    return mock

# Assertion Utilities
def assert_success_response(response: Dict[str, Any]):
    """Assert that response indicates success."""
    assert response.get("success") is True, f"Expected success response, got: {response}"

def assert_error_response(response: Dict[str, Any]):
    """Assert that response indicates error."""
    assert response.get("success") is False, f"Expected error response, got: {response}"

def assert_contains_keys(data: Dict[str, Any], keys: List[str]):
    """Assert that dictionary contains all specified keys."""
    for key in keys:
        assert key in data, f"Expected key '{key}' not found in data"

def assert_not_contains_keys(data: Dict[str, Any], keys: List[str]):
    """Assert that dictionary does not contain specified keys."""
    for key in keys:
        assert key not in data, f"Unexpected key '{key}' found in data"