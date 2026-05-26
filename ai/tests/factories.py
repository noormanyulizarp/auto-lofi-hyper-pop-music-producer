# Test Factories for Data Generation
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from factory import Factory, Faker, SubFactory, lazy_attribute
from factory.alchemy import SQLAlchemyModelFactory
import numpy as np

# Import application models (if available)
try:
    from ai.models.responses import (
        Genre, Mood, TaskStatus,
        GenerateMusicRequest, MusicGenerationResponse,
        AnalyzeVideoRequest, VideoAnalysisResponse
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

class TestMusicRequestFactory:
    """Factory for creating test music generation requests."""
    
    @staticmethod
    def create(
        title: str = None,
        genre: str = None,
        mood: str = None,
        duration: int = None,
        prompt: str = None,
        tempo: int = None,
        key: str = None,
        instruments: List[str] = None,
        model: str = None
    ) -> Dict[str, Any]:
        """Create a test music generation request."""
        if MODELS_AVAILABLE:
            # Use actual model classes if available
            return GenerateMusicRequest(
                title=title or Faker().sentence(),
                genre=genre or random.choice(list(Genre)),
                mood=mood or random.choice(list(Mood)),
                duration=duration or random.randint(30, 300),
                prompt=prompt or Faker().paragraph(),
                tempo=tempo or random.randint(60, 140),
                key=key or random.choice(["C", "G", "D", "A", "E", "F", "B", "F#"]) + " Major",
                instruments=instruments or random.sample([
                    "Piano", "Guitar", "Bass", "Drums", "Synth", 
                    "Violin", "Flute", "Saxophone", "Trumpet"
                ], random.randint(2, 4)),
                model=model or "standard"
            )
        else:
            # Create dictionary structure
            return {
                "title": title or Faker().sentence(),
                "genre": genre or random.choice(["lofi", "electronic", "jazz", "classical", "hiphop"]),
                "mood": mood or random.choice(["chill", "happy", "sad", "energetic", "calm"]),
                "duration": duration or random.randint(30, 300),
                "prompt": prompt or Faker().paragraph(),
                "tempo": tempo or random.randint(60, 140),
                "key": key or random.choice(["C", "G", "D", "A", "E", "F", "B", "F#"]) + " Major",
                "instruments": instruments or random.sample([
                    "Piano", "Guitar", "Bass", "Drums", "Synth",
                    "Violin", "Flute", "Saxophone", "Trumpet"
                ], random.randint(2, 4)),
                "model": model or "standard"
            }

class TestVideoRequestFactory:
    """Factory for creating test video analysis requests."""
    
    @staticmethod
    def create(
        video_url: str = None,
        title: str = None,
        description: str = None,
        focus_type: str = None,
        extract_audio: bool = True,
        analyze_patterns: bool = True,
        duration: int = None
    ) -> Dict[str, Any]:
        """Create a test video analysis request."""
        if MODELS_AVAILABLE:
            return AnalyzeVideoRequest(
                video_url=video_url or "https://youtube.com/watch?v=test123",
                title=title or Faker().sentence(),
                description=description or Faker().paragraph(),
                focus_type=focus_type or random.choice(["rhythm", "melody", "harmony", "structure", "all"]),
                extract_audio=extract_audio,
                analyze_patterns=analyze_patterns,
                duration=duration or random.randint(60, 600)
            )
        else:
            return {
                "video_url": video_url or "https://youtube.com/watch?v=test123",
                "title": title or Faker().sentence(),
                "description": description or Faker().paragraph(),
                "focus_type": focus_type or random.choice(["rhythm", "melody", "harmony", "structure", "all"]),
                "extract_audio": extract_audio,
                "analyze_patterns": analyze_patterns,
                "duration": duration or random.randint(60, 600)
            }

class TestAudioFeaturesFactory:
    """Factory for creating test audio feature data."""
    
    @staticmethod
    def create(
        tempo: float = None,
        key: str = None,
        duration: float = None,
        sample_rate: int = None,
        rhythm_complexity: float = None,
        melodic_complexity: float = None,
        harmonic_complexity: float = None
    ) -> Dict[str, Any]:
        """Create test audio feature data."""
        return {
            "rhythm": {
                "tempo": tempo or random.uniform(60.0, 180.0),
                "beat_strength": random.uniform(0.3, 1.0),
                "rhythm_complexity": rhythm_complexity or random.uniform(0.1, 1.0),
                "syncopation": random.uniform(0.0, 0.8),
                "beat_times": list(np.linspace(0, 4, 17)),  # 4 measures, 4/4 time
                "meter": random.choice(["4/4", "3/4", "6/8", "12/8"])
            },
            "melody": {
                "pitch_range": random.randint(5, 24),
                "melodic_contour": random.choice(["ascending", "descending", "arch", "valley", "wave"]),
                "pitch_class_histogram": list(np.random.dirichlet(np.ones(12))),
                "tonal_strength": random.uniform(0.4, 1.0),
                "pitch_variance": random.uniform(0.1, 0.9)
            },
            "harmony": {
                "chroma_features": list(np.random.dirichlet(np.ones(12))),
                "key_strength": random.uniform(0.5, 1.0),
                "estimated_key": key or random.choice([
                    "C Major", "G Major", "D Major", "A Major", "E Major",
                    "F Major", "B Major", "C# Major", "F# Major",
                    "A Minor", "E Minor", "D Minor", "B Minor"
                ]),
                "harmonic_complexity": harmonic_complexity or random.uniform(0.1, 1.0),
                "chord_changes": random.randint(2, 12)
            },
            "timbre": {
                "spectral_centroid": random.uniform(1000.0, 5000.0),
                "spectral_bandwidth": random.uniform(500.0, 3000.0),
                "spectral_rolloff": random.uniform(1500.0, 8000.0),
                "zero_crossing_rate": random.uniform(0.01, 0.2),
                "mfcc": list(np.random.randn(13)),
                "spectral_contrast": list(np.random.randn(7))
            },
            "structure": {
                "segments": random.randint(2, 8),
                "segment_similarity": random.uniform(0.3, 0.9),
                "form_type": random.choice(["verse-chorus", "ABA", "rondo", "through-composed"]),
                "repetition_score": random.uniform(0.2, 1.0),
                "segment_lengths": list(np.random.randint(10, 60, size=random.randint(2, 8)))
            },
            "metadata": {
                "duration": duration or random.uniform(10.0, 300.0),
                "sample_rate": sample_rate or random.choice([22050, 44100, 48000]),
                "channels": random.choice([1, 2]),
                "bit_depth": random.choice([16, 24, 32]),
                "format": random.choice(["mp3", "wav", "flac", "aac"])
            }
        }

class TestVideoAnalysisFactory:
    """Factory for creating test video analysis data."""
    
    @staticmethod
    def create(
        title: str = None,
        duration: float = None,
        resolution: str = None,
        fps: float = None,
        focus_type: str = None
    ) -> Dict[str, Any]:
        """Create test video analysis data."""
        return {
            "video_info": {
                "title": title or Faker().sentence(),
                "duration": duration or random.uniform(60.0, 600.0),
                "resolution": resolution or random.choice(["1920x1080", "1280x720", "854x480", "640x360"]),
                "fps": fps or random.choice([24, 25, 30, 60]),
                "codec": random.choice(["h264", "h265", "vp9", "av1"]),
                "format": random.choice(["mp4", "mov", "avi", "mkv"]),
                "file_size": random.randint(1000000, 100000000)
            },
            "audio_analysis": TestAudioFeaturesFactory.create(
                duration=duration or random.uniform(60.0, 600.0)
            ),
            "musical_elements": {
                "rhythm": {
                    "patterns": random.sample([
                        "steady beat", "syncopated rhythm", "polyrhythm", "complex groove"
                    ], random.randint(1, 3)),
                    "complexity": random.choice(["simple", "moderate", "complex"]),
                    "instruments": random.sample([
                        "drums", "bass", "guitar", "piano", "synth", "vocals"
                    ], random.randint(2, 4))
                },
                "melody": {
                    "scale": random.choice([
                        "C Major", "G Major", "A Minor", "E Minor",
                        "C Major Pentatonic", "E Minor Pentatonic", "Blues Scale"
                    ]),
                    "range": random.choice(["one octave", "two octaves", "wide range"]),
                    "characteristics": random.sample([
                        "simple", "complex", "repetitive", "varied", "expressive"
                    ], random.randint(2, 4))
                },
                "harmony": {
                    "chords": random.sample([
                        "C", "G", "D", "A", "E", "F", "Am", "Em", "Dm", "B7"
                    ], random.randint(3, 6)),
                    "progression": random.choice([
                        "I-IV-V", "I-vi-IV-V", "ii-V-I", "I-V-vi-IV"
                    ]),
                    "complexity": random.choice(["basic", "intermediate", "advanced"])
                }
            },
            "learning_patterns": {
                "techniques": [
                    {
                        "name": random.choice([
                            "Strumming Pattern", "Fingerpicking", "Chord Transition",
                            "Scale Practice", "Rhythm Exercise", "Melodic Pattern"
                        ]),
                        "description": Faker().sentence(),
                        "confidence": random.uniform(0.6, 0.95),
                        "timestamp": [random.uniform(0, 300), random.uniform(300, 600)],
                        "difficulty": random.choice(["beginner", "intermediate", "advanced"])
                    }
                    for _ in range(random.randint(1, 4))
                ],
                "exercises": [
                    {
                        "title": random.choice([
                            "Practice Strumming", "Scale Exercise", "Chord Practice",
                            "Rhythm Training", "Melody Practice", "Technique Drill"
                        ]),
                        "instructions": Faker().paragraph(),
                        "duration": random.randint(5, 30),
                        "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                        "tempo": random.randint(60, 120)
                    }
                    for _ in range(random.randint(1, 3))
                ]
            }
        }

class TestMusicConceptsFactory:
    """Factory for creating test music concepts."""
    
    @staticmethod
    def create(
        genre: str = None,
        mood: str = None,
        theme: str = None,
        complexity: str = None
    ) -> Dict[str, Any]:
        """Create test music concepts."""
        return {
            "genre": genre or random.choice(["lofi", "electronic", "jazz", "classical", "hiphop", "ambient"]),
            "mood": mood or random.choice(["chill", "happy", "sad", "energetic", "calm", "mysterious"]),
            "theme": theme or random.choice([
                "study music", "relaxation", "party", "meditation", "workout", "focus"
            ]),
            "complexity": complexity or random.choice(["simple", "moderate", "complex"]),
            "concepts": {
                "rhythm": random.sample([
                    "steady beat", "syncopation", "polyrhythm", "complex groove",
                    "minimal percussion", "driving rhythm", "relaxed tempo"
                ], random.randint(2, 5)),
                "melody": random.sample([
                    "simple motifs", "complex melodies", "repetitive patterns",
                    "contrasting themes", "call and response", "improvisation"
                ], random.randint(2, 5)),
                "harmony": random.sample([
                    "basic chords", "extended harmony", "modal interchange",
                    "counterpoint", "dense textures", "sparse harmony"
                ], random.randint(2, 5)),
                "structure": random.sample([
                    "verse-chorus", "ABA form", "through-composed", "rondo",
                    "binary form", "ternary form", "strophic form"
                ], random.randint(2, 4))
            },
            "instruments": random.sample([
                "piano", "guitar", "bass", "drums", "synth", "strings", "brass",
                "woodwinds", "percussion", "electronic", "acoustic", "vocal"
            ], random.randint(3, 7)),
            "technical_specs": {
                "tempo": random.randint(60, 140),
                "key": random.choice([
                    "C", "G", "D", "A", "E", "F", "B", "F#", "C#", "G#", "D#", "A#"
                ]) + " " + random.choice(["Major", "Minor"]),
                "time_signature": random.choice(["4/4", "3/4", "6/8", "12/8", "5/4", "7/8"]),
                "duration_structure": {
                    "intro": random.randint(4, 16),
                    "verse": random.randint(8, 32),
                    "chorus": random.randint(8, 32),
                    "bridge": random.randint(4, 16) if random.random() > 0.3 else 0,
                    "outro": random.randint(4, 16)
                }
            }
        }

class TestProviderResponseFactory:
    """Factory for creating test provider responses."""
    
    @staticmethod
    def create(
        provider: str = None,
        model: str = None,
        response: str = None,
        success: bool = True,
        latency: float = None,
        tokens_used: int = None
    ) -> Dict[str, Any]:
        """Create test provider response."""
        return {
            "success": success,
            "provider": provider or random.choice([
                "anthropic", "openai", "google", "mistral", "cohere", "perplexity"
            ]),
            "model": model or random.choice([
                "claude-3-sonnet", "claude-3-opus", "gpt-4", "gpt-3.5-turbo",
                "gemini-pro", "mixtral", "command", "pplx"
            ]),
            "response": response or Faker().paragraph(),
            "latency": latency or random.uniform(0.5, 3.0),
            "tokens_used": tokens_used or random.randint(50, 500),
            "timestamp": datetime.now().isoformat()
        }

class TestHeartMuLaResponseFactory:
    """Factory for creating test HeartMuLa responses."""
    
    @staticmethod
    def create_generation_response(
        task_id: str = None,
        status: str = None,
        estimated_time: int = None
    ) -> Dict[str, Any]:
        """Create test HeartMuLa generation response."""
        return {
            "success": True,
            "task_id": task_id or f"task_{random.randint(1000, 9999)}",
            "status": status or random.choice(["processing", "queued", "completed", "failed"]),
            "estimated_time": estimated_time or random.randint(10, 120),
            "message": "Music generation started" if status in ["processing", "queued"] else "Music generation completed"
        }
    
    @staticmethod
    def create_status_response(
        task_id: str = None,
        status: str = None,
        progress: int = None,
        result_url: str = None
    ) -> Dict[str, Any]:
        """Create test HeartMuLa status response."""
        return {
            "success": True,
            "task_id": task_id or f"task_{random.randint(1000, 9999)}",
            "status": status or random.choice(["processing", "completed"]),
            "progress": progress or random.randint(0, 100),
            "result_url": result_url or f"https://heartmula.com/music/{random.randint(1000, 9999)}.mp3",
            "download_url": f"https://heartmula.com/download/{random.randint(1000, 9999)}",
            "metadata": {
                "duration": random.randint(30, 300),
                "format": random.choice(["mp3", "wav", "flac"]),
                "size": random.randint(1000000, 10000000),
                "bitrate": random.choice([128, 192, 256, 320])
            }
        }
    
    @staticmethod
    def create_music_details(
        task_id: str = None,
        title: str = None,
        artist: str = None
    ) -> Dict[str, Any]:
        """Create test HeartMuLa music details."""
        return {
            "success": True,
            "music_id": task_id or f"music_{random.randint(1000, 9999)}",
            "title": title or Faker().sentence(),
            "artist": artist or "AI Generator",
            "genre": random.choice(["lofi", "electronic", "jazz", "classical", "hiphop"]),
            "mood": random.choice(["chill", "happy", "sad", "energetic", "calm"]),
            "duration": random.randint(30, 300),
            "audio_url": f"https://heartmula.com/music/{random.randint(1000, 9999)}.mp3",
            "waveform_url": f"https://heartmula.com/waveform/{random.randint(1000, 9999)}.png",
            "metadata": {
                "bpm": random.randint(60, 140),
                "key": random.choice([
                    "C", "G", "D", "A", "E", "F", "B", "F#", "C#", "G#", "D#", "A#"
                ]) + " " + random.choice(["Major", "Minor"]),
                "instruments": random.sample([
                    "Piano", "Guitar", "Bass", "Drums", "Synth", "Strings", "Brass"
                ], random.randint(2, 5)),
                "created_at": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
            }
        }

class TestGLMResponseFactory:
    """Factory for creating test GLM responses."""
    
    @staticmethod
    def create_search_response(
        query: str = None,
        results_count: int = None
    ) -> Dict[str, Any]:
        """Create test GLM search response."""
        return {
            "success": True,
            "query": query or "music trends 2024",
            "results": [
                {
                    "title": Faker().sentence(),
                    "url": f"https://example.com/article{random.randint(1, 100)}",
                    "snippet": Faker().sentence(),
                    "content": Faker().paragraph()
                }
                for _ in range(results_count or random.randint(1, 5))
            ],
            "total_results": results_count or random.randint(1, 10),
            "search_time": random.uniform(0.1, 1.0)
        }
    
    @staticmethod
    def create_reader_response(
        url: str = None,
        word_count: int = None
    ) -> Dict[str, Any]:
        """Create test GLM reader response."""
        return {
            "success": True,
            "url": url or f"https://example.com/article{random.randint(1, 100)}",
            "title": Faker().sentence(),
            "content": Faker().paragraph(nb_sentences=random.randint(5, 15)),
            "word_count": word_count or random.randint(100, 1000),
            "reading_time": random.uniform(0.5, 3.0)
        }

class TestErrorFactory:
    """Factory for creating test error responses."""
    
    @staticmethod
    def create(
        error_type: str = None,
        error_message: str = None,
        status_code: int = None,
        details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create test error response."""
        return {
            "success": False,
            "error": {
                "type": error_type or random.choice([
                    "validation_error", "api_error", "timeout_error", 
                    "authentication_error", "rate_limit_error", "server_error"
                ]),
                "message": error_message or Faker().sentence(),
                "status_code": status_code or random.choice([400, 401, 403, 404, 429, 500, 503]),
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }
        }

class TestDataGenerator:
    """Main data generator for comprehensive test data."""
    
    def __init__(self):
        self.music_request_factory = TestMusicRequestFactory()
        self.video_request_factory = TestVideoRequestFactory()
        self.audio_features_factory = TestAudioFeaturesFactory()
        self.video_analysis_factory = TestVideoAnalysisFactory()
        self.music_concepts_factory = TestMusicConceptsFactory()
        self.provider_response_factory = TestProviderResponseFactory()
        self.heartmula_factory = TestHeartMuLaResponseFactory()
        self.glm_factory = TestGLMResponseFactory()
        self.error_factory = TestErrorFactory()
    
    def generate_music_test_suite(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate a suite of music-related test data."""
        return [
            {
                "request": self.music_request_factory.create(),
                "concepts": self.music_concepts_factory.create(),
                "audio_features": self.audio_features_factory.create(),
                "provider_response": self.provider_response_factory.create(),
                "heartmula_response": self.heartmula_factory.create_generation_response()
            }
            for _ in range(count)
        ]
    
    def generate_video_test_suite(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate a suite of video-related test data."""
        return [
            {
                "request": self.video_request_factory.create(),
                "analysis": self.video_analysis_factory.create(),
                "audio_features": self.audio_features_factory.create(),
                "glm_search": self.glm_factory.create_search_response(),
                "glm_reader": self.glm_factory.create_reader_response()
            }
            for _ in range(count)
        ]
    
    def generate_error_scenarios(self) -> List[Dict[str, Any]]:
        """Generate various error scenarios."""
        return [
            self.error_factory.create("validation_error", "Invalid input data", 400),
            self.error_factory.create("api_error", "External API unavailable", 503),
            self.error_factory.create("timeout_error", "Request timeout", 408),
            self.error_factory.create("authentication_error", "Invalid API key", 401),
            self.error_factory.create("rate_limit_error", "Too many requests", 429),
            self.error_factory.create("server_error", "Internal server error", 500)
        ]

# Global factory instance
test_data_generator = TestDataGenerator()