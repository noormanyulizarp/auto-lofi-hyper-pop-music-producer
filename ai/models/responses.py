from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class Genre(str, Enum):
    """Music genres supported"""
    LOFI = "lofi"
    HYPERPOP = "hyperpop"
    CHILLOUT = "chillout"
    AMBIENT = "ambient"
    ELECTRONIC = "electronic"
    HIPHOP = "hiphop"
    JAZZ = "jazz"
    CLASSICAL = "classical"

class Mood(str, Enum):
    """Music moods supported"""
    CHILL = "chill"
    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    CALM = "calm"
    MYSTERIOUS = "mysterious"
    ROMANTIC = "romantic"
    INTENSE = "intense"

class TaskStatus(str, Enum):
    """Task status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Health Check Models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: str

# Music Generation Models
class GenerateMusicRequest(BaseModel):
    """Music generation request"""
    title: str
    genre: Genre
    mood: Mood
    duration: int  # in seconds
    prompt: str
    model: str = "heartmula"
    tempo: Optional[int] = None
    key: Optional[str] = None
    instruments: Optional[List[str]] = None

class MusicGenerationResponse(BaseModel):
    """Music generation response"""
    task_id: str
    status: TaskStatus
    estimated_time: Optional[int] = None  # in seconds
    message: str

class MusicGenerationStatus(BaseModel):
    """Music generation status"""
    task_id: str
    status: TaskStatus
    progress: Optional[float] = None  # 0.0 to 1.0
    result_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class GeneratedMusic(BaseModel):
    """Generated music result"""
    id: str
    title: str
    genre: str
    mood: str
    duration: int
    audio_url: str
    metadata: Dict[str, Any]
    created_at: datetime

# Video Analysis Models
class AnalyzeVideoRequest(BaseModel):
    """Video analysis request"""
    video_url: str
    title: str
    focus_type: str = "rhythm"  # rhythm, melody, harmony, structure
    extract_audio: bool = True
    generate_transcript: bool = True

class VideoAnalysisResponse(BaseModel):
    """Video analysis response"""
    task_id: str
    status: TaskStatus
    estimated_time: Optional[int] = None
    message: str

class VideoAnalysisResult(BaseModel):
    """Video analysis result"""
    task_id: str
    status: TaskStatus
    video_info: Dict[str, Any]
    audio_features: Optional[Dict[str, Any]] = None
    transcript: Optional[str] = None
    musical_elements: Optional[Dict[str, Any]] = None
    learned_patterns: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

# Learning Session Models
class LearningSession(BaseModel):
    """Learning session"""
    id: str
    user_id: str
    video_url: str
    video_title: str
    status: TaskStatus
    analysis_result: Optional[VideoAnalysisResult] = None
    created_at: datetime
    updated_at: datetime

# Error Response Models
class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    code: Optional[int] = None

# Success Response Models
class SuccessResponse(BaseModel):
    """Success response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Generic Response Models
class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool