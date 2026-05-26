import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from ..app.main import app
from ..services.music_ai_service import MusicAIService
from ..services.audio_feature_extractor import AudioFeatureExtractor
from ..services.database_service import DatabaseService
from ..services.heartmula import HeartMuLaService
from ..config.settings import get_settings

class TestMusicGenerationIntegration:
    """Test suite for AI-enhanced music generation integration"""
    
    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_music_ai_service(self):
        """Mock Music AI Service"""
        service = Mock(spec=MusicAIService)
        
        # Mock methods
        service.generate_music_concepts = AsyncMock(return_value={
            "success": True,
            "concepts": {
                "structure": "Verse-Chorus-Verse-Chorus-Bridge-Chorus",
                "melody": "Catchy, repetitive hook with rhythmic variation",
                "rhythm": "Medium-tempo 4/4 beat with syncopation",
                "instruments": ["piano", "bass", "drums", "synth"],
                "mood": "Uplifting and energetic"
            }
        })
        
        service.enhance_music_prompt = AsyncMock(return_value={
            "success": True,
            "enhanced_prompt": "Create an energetic electronic track with catchy melodies, featuring piano, bass, drums, and synth elements. The song should have a Verse-Chorus structure with a memorable hook. Tempo should be around 120 BPM with a modern electronic feel.",
            "improvements": [
                "Added specific instrumentation details",
                "Included tempo suggestion",
                "Added structural guidance",
                "Enhanced mood description"
            ]
        })
        
        service.get_optimal_generation_parameters = AsyncMock(return_value={
            "success": True,
            "parameters": {
                "tempo": 120,
                "key": "C major",
                "instrumentation": ["piano", "bass", "drums", "synth"],
                "style": "electronic",
                "complexity": "medium"
            }
        })
        
        return service
    
    @pytest.fixture
    def mock_heartmula_service(self):
        """Mock HeartMuLa Service"""
        service = Mock(spec=HeartMuLaService)
        
        service.generate_music = AsyncMock(return_value={
            "success": True,
            "task_id": "heartmula_12345",
            "estimated_time": 30,
            "message": "Music generation started successfully"
        })
        
        service.get_generation_status = AsyncMock(return_value={
            "success": True,
            "task_id": "heartmula_12345",
            "status": "completed",
            "progress": 100.0,
            "result_url": "https://heartmula.example.com/music/12345.mp3"
        })
        
        return service
    
    @pytest.fixture
    def mock_database_service(self):
        """Mock Database Service"""
        service = Mock(spec=DatabaseService)
        
        service.create_music_generation = Mock(return_value=Mock(
            task_id="test_12345",
            to_dict=Mock(return_value={
                "task_id": "test_12345",
                "title": "Test Song",
                "genre": "electronic",
                "mood": "energetic",
                "status": "pending"
            })
        ))
        
        return service
    
    def test_generate_music_ai_enhanced(self, client, mock_music_ai_service, mock_heartmula_service):
        """Test AI-enhanced music generation"""
        with patch('..services.music_ai_service.music_ai_service', mock_music_ai_service), \
             patch('..services.heartmula.heartmula_service', mock_heartmula_service):
            
            request_data = {
                "title": "Test Song",
                "genre": "electronic",
                "mood": "energetic",
                "duration": 30,
                "prompt": "Create an energetic electronic track",
                "tempo": None,
                "key": None,
                "instruments": None
            }
            
            response = client.post("/api/music/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["ai_enhanced"] is True
            assert data["enhanced_prompt"] is not None
            assert data["ai_concepts"] is not None
    
    def test_music_concepts_analysis(self, client, mock_music_ai_service):
        """Test music concepts analysis without generation"""
        with patch('..services.music_ai_service.music_ai_service', mock_music_ai_service):
            
            request_data = {
                "genre": "electronic",
                "mood": "energetic",
                "theme": "Night city lights",
                "duration": 30
            }
            
            response = client.post("/api/music/analyze-concepts", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "concepts" in data["data"]
            assert "structure" in data["data"]["concepts"]
    
    def test_prompt_enhancement(self, client, mock_music_ai_service):
        """Test prompt enhancement"""
        with patch('..services.music_ai_service.music_ai_service', mock_music_ai_service):
            
            request_data = {
                "prompt": "Create an energetic track",
                "genre": "electronic",
                "mood": "energetic",
                "tempo": None,
                "key": None,
                "instruments": None
            }
            
            response = client.post("/api/music/enhance-prompt", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "enhanced_prompt" in data["data"]
            assert "improvements" in data["data"]
    
    def test_optimal_parameters(self, client, mock_music_ai_service):
        """Test optimal parameters generation"""
        with patch('..services.music_ai_service.music_ai_service', mock_music_ai_service):
            
            request_data = {
                "genre": "electronic",
                "mood": "energetic",
                "duration": 30,
                "user_preferences": {}
            }
            
            response = client.post("/api/music/optimal-parameters", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "parameters" in data["data"]
            assert "tempo" in data["data"]["parameters"]

class TestVideoAnalysisIntegration:
    """Test suite for AI-enhanced video analysis integration"""
    
    @pytest.fixture
    def mock_video_analysis_service(self):
        """Mock Video Analysis Service"""
        from unittest.mock import AsyncMock
        
        service = Mock()
        service.analyze_video = AsyncMock(return_value={
            "success": True,
            "task_id": "video_12345",
            "estimated_time": 45,
            "message": "Video analysis started successfully"
        })
        
        service.check_analysis_status = AsyncMock(return_value={
            "success": True,
            "task_id": "video_12345",
            "status": "completed",
            "progress": 100.0,
            "results": {
                "audio_features": {
                    "tempo": 120.5,
                    "key": "C major",
                    "energy": 0.75,
                    "danceability": 0.68
                },
                "musical_elements": {
                    "rhythm": "Steady 4/4 beat with syncopation",
                    "melody": "Catchy hook in C major",
                    "harmony": "Simple chord progression",
                    "structure": "Intro-Verse-Chorus-Verse-Chorus-Bridge-Chorus-Outro"
                },
                "learned_patterns": [
                    {
                        "type": "rhythm",
                        "description": "Syncopated drum pattern with off-beat accents",
                        "confidence": 0.85,
                        "application": "Use in chorus sections for energy",
                        "variations": ["slower version for verses", "double-time for bridge"]
                    }
                ],
                "transcript": "Welcome to this music tutorial...",
                "confidence_score": 0.87
            }
        })
        
        return service
    
    def test_video_analysis_complete(self, client, mock_video_analysis_service):
        """Test complete video analysis workflow"""
        with patch('..services.video_analysis.video_analysis_service', mock_video_analysis_service):
            
            request_data = {
                "video_url": "https://youtube.com/watch?v=test123",
                "video_title": "Music Production Tutorial",
                "focus_type": "rhythm",
                "extract_audio": True,
                "generate_transcript": True
            }
            
            # Start analysis
            response = client.post("/api/video/analyze", json=request_data)
            assert response.status_code == 200
            
            # Check status (mocking completion)
            response = client.get("/api/video/status/video_12345")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["status"] == "completed"
            assert "audio_features" in data["results"]
            assert "musical_elements" in data["results"]
            assert "learned_patterns" in data["results"]

class TestAudioFeatureExtraction:
    """Test suite for audio feature extraction"""
    
    @pytest.fixture
    def audio_extractor(self):
        """Audio Feature Extractor instance"""
        return AudioFeatureExtractor()
    
    def test_extract_rhythm_features(self, audio_extractor):
        """Test rhythm feature extraction"""
        # Mock audio data
        mock_y = Mock(shape=(22050,))  # 1 second of audio at 22.05kHz
        mock_sr = 22050
        
        features = audio_extractor.extract_rhythm_features(mock_y, mock_sr)
        
        assert "tempo" in features
        assert "beats" in features
        assert "rhythmic_complexity" in features
        assert isinstance(features["tempo"], (int, float))
    
    def test_extract_melody_features(self, audio_extractor):
        """Test melody feature extraction"""
        mock_y = Mock(shape=(22050,))
        mock_sr = 22050
        
        features = audio_extractor.extract_melody_features(mock_y, mock_sr)
        
        assert "pitch" in features
        assert "melodic_contour" in features
        assert "key" in features
        assert "scale" in features
    
    def test_extract_harmony_features(self, audio_extractor):
        """Test harmony feature extraction"""
        mock_y = Mock(shape=(22050,))
        mock_sr = 22050
        
        features = audio_extractor.extract_harmony_features(mock_y, mock_sr)
        
        assert "chords" in features
        assert "harmonic_complexity" in features
        assert "key_change" in features

class TestDatabaseIntegration:
    """Test suite for database integration"""
    
    @pytest.fixture
    def mock_database_service(self):
        """Mock Database Service"""
        service = Mock(spec=DatabaseService)
        
        service.create_music_generation = Mock(return_value=Mock(
            task_id="db_test_123",
            to_dict=Mock(return_value={
                "task_id": "db_test_123",
                "title": "Database Test",
                "status": "pending"
            })
        ))
        
        service.save_ai_enhanced_generation = Mock(return_value=Mock(
            task_id="db_test_123",
            to_dict=Mock(return_value={
                "task_id": "db_test_123",
                "ai_enhanced": True,
                "confidence_score": 0.85
            })
        ))
        
        service.save_video_analysis_results = Mock(return_value=Mock(
            task_id="video_db_test",
            to_dict=Mock(return_value={
                "task_id": "video_db_test",
                "confidence_score": 0.92
            })
        ))
        
        return service
    
    def test_save_ai_enhanced_generation(self, mock_database_service):
        """Test saving AI-enhanced generation to database"""
        enhanced_data = {
            "enhanced_prompt": "AI enhanced prompt",
            "ai_concepts": {"test": "concept"},
            "optimal_parameters": {"tempo": 120},
            "confidence_score": 0.85
        }
        
        result = mock_database_service.save_ai_enhanced_generation("db_test_123", enhanced_data)
        
        assert result is not None
        assert mock_database_service.update_music_generation.called
    
    def test_save_video_analysis_results(self, mock_database_service):
        """Test saving video analysis results to database"""
        analysis_results = {
            "audio_features": {"tempo": 120},
            "musical_elements": {"rhythm": "test"},
            "learned_patterns": [{"type": "rhythm"}],
            "confidence_score": 0.92
        }
        
        result = mock_database_service.save_video_analysis_results("video_db_test", analysis_results)
        
        assert result is not None
        assert mock_database_service.update_video_analysis.called

class TestAPIIntegration:
    """Test suite for overall API integration"""
    
    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)
    
    def test_get_supported_genres(self, client):
        """Test getting supported genres"""
        response = client.get("/api/music/genres")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "genres" in data
        assert "electronic" in data["genres"]
        assert "lofi" in data["genres"]
        assert "descriptions" in data
    
    def test_get_supported_moods(self, client):
        """Test getting supported moods"""
        response = client.get("/api/music/moods")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "moods" in data
        assert "energetic" in data["moods"]
        assert "chill" in data["moods"]
        assert "descriptions" in data
    
    def test_get_ai_capabilities(self, client):
        """Test getting AI capabilities"""
        response = client.get("/api/music/ai-capabilities")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "capabilities" in data
        assert "provider_system" in data
        
        # Check specific capabilities
        capabilities = data["capabilities"]
        assert "music_concept_generation" in capabilities
        assert "prompt_enhancement" in capabilities
        assert "audio_analysis" in capabilities
        
        # Check provider system
        provider_system = data["provider_system"]
        assert provider_system["total_models"] == 8
        assert "Z.AI" in provider_system["providers"]
        assert "OpenRouter" in provider_system["providers"]

class TestErrorHandling:
    """Test suite for error handling"""
    
    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)
    
    def test_invalid_music_generation_request(self, client):
        """Test invalid music generation request"""
        # Missing required fields
        invalid_data = {
            "title": "",  # Empty title
            "genre": "invalid_genre",  # Invalid genre
            "mood": "energetic",
            "duration": 5,  # Too short
            "prompt": "test"
        }
        
        response = client.post("/api/music/generate", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_nonexistent_task_status(self, client):
        """Test getting status of non-existent task"""
        response = client.get("/api/music/status/nonexistent_task")
        
        assert response.status_code == 404
    
    def test_invalid_video_analysis_request(self, client):
        """Test invalid video analysis request"""
        invalid_data = {
            "video_url": "invalid_url",
            "video_title": "",
            "focus_type": "invalid_focus"
        }
        
        response = client.post("/api/video/analyze", json=invalid_data)
        
        assert response.status_code == 422

# Integration Tests
class TestEndToEndWorkflow:
    """Test suite for end-to-end workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_music_generation_workflow(self):
        """Test complete music generation workflow from start to finish"""
        # This would test the entire flow:
        # 1. User submits music generation request
        # 2. AI generates concepts and enhances prompt
        # 3. System gets optimal parameters
        # 4. HeartMuLa generates music
        # 5. System checks status and retrieves results
        # 6. Results are saved to database
        
        # This would require more complex mocking and integration
        pass
    
    @pytest.mark.asyncio
    async def test_complete_video_analysis_workflow(self):
        """Test complete video analysis workflow"""
        # This would test:
        # 1. User submits video URL for analysis
        # 2. System downloads and processes video
        # 3. AI extracts audio and analyzes features
        # 4. System learns patterns
        # 5. Results are saved to database
        # 6. Patterns are extracted and stored
        
        pass

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])