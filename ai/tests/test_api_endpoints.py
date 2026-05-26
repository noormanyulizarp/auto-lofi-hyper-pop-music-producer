# API Endpoint Tests
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from tests.fixtures import (
    client,
    test_app,
    test_music_request,
    test_video_request,
    mock_music_ai_service,
    mock_audio_feature_extractor,
    mock_video_analysis_service,
    mock_provider_service,
    mock_heartmula_service
)
from tests.mocks import (
    mock_openrouter,
    mock_heartmula,
    mock_glm,
    mock_librosa,
    mock_video_processing,
    mock_responses
)
from tests.assertions import (
    assert_success_response,
    assert_error_response,
    assert_valid_music_concepts,
    assert_valid_audio_features,
    assert_valid_video_analysis
)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "uptime" in data
    
    def test_health_check_with_service_status(self, client):
        """Test health check with service status details."""
        response = client.get("/health?detailed=true")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "services" in data
        assert "database" in data["services"]
        assert "redis" in data["services"]
        assert "external_apis" in data["services"]


class TestMusicGenerationEndpoints:
    """Test music generation endpoints."""
    
    @pytest.mark.api
    def test_generate_music_concepts_success(self, client, mock_music_ai_service):
        """Test successful music concepts generation."""
        request_data = {
            "genre": "lofi",
            "mood": "chill",
            "title": "Test Music",
            "prompt": "A relaxing lofi track",
            "duration": 120,
            "instruments": ["piano", "drums"],
            "model": "standard"
        }
        
        with patch('ai.routes.music_ai_service.MusicAIService') as mock_service_class:
            mock_service = mock_music_ai_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/music/concepts", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "concepts" in data
            assert_valid_music_concepts(data["concepts"])
    
    @pytest.mark.api
    def test_generate_music_concepts_invalid_input(self, client):
        """Test music concepts generation with invalid input."""
        request_data = {
            "genre": "invalid_genre",
            "mood": "chill",
            "title": "",
            "prompt": "A relaxing lofi track"
        }
        
        response = client.post("/api/v1/music/concepts", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    def test_enhance_music_prompt_success(self, client, mock_music_ai_service):
        """Test successful music prompt enhancement."""
        request_data = {
            "prompt": "A relaxing lofi track",
            "genre": "lofi",
            "mood": "chill"
        }
        
        with patch('ai.routes.music_ai_service.MusicAIService') as mock_service_class:
            mock_service = mock_music_ai_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/music/enhance-prompt", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "enhanced_prompt" in data
            assert "enhancements" in data
            assert len(data["enhanced_prompt"]) > len(request_data["prompt"])
    
    @pytest.mark.api
    def test_get_optimal_parameters_success(self, client, mock_music_ai_service):
        """Test successful optimal parameters retrieval."""
        request_data = {
            "genre": "lofi",
            "mood": "chill",
            "duration": 60,
            "complexity": "simple"
        }
        
        with patch('ai.routes.music_ai_service.MusicAIService') as mock_service_class:
            mock_service = mock_music_ai_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/music/optimal-parameters", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "parameters" in data
            assert "confidence" in data
            
            params = data["parameters"]
            assert "tempo" in params
            assert "key" in params
            assert "instrumentation" in params
            assert "duration_structure" in params
    
    @pytest.mark.api
    def test_generate_music_theory_advice_success(self, client, mock_music_ai_service):
        """Test successful music theory advice generation."""
        request_data = {
            "genre": "jazz",
            "key": "C Major",
            "complexity": "intermediate",
            "focus_areas": ["chord_progressions", "scales"]
        }
        
        with patch('ai.routes.music_ai_service.MusicAIService') as mock_service_class:
            mock_service = mock_music_ai_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/music/theory-advice", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "advice" in data
            
            advice = data["advice"]
            assert "chord_progressions" in advice
            assert "scale_options" in advice
            assert "rhythm_patterns" in advice
            assert "production_tips" in advice
    
    @pytest.mark.api
    def test_suggest_instrument_combinations_success(self, client, mock_music_ai_service):
        """Test successful instrument combination suggestions."""
        request_data = {
            "genre": "rock",
            "mood": "energetic",
            "primary_instrument": "electric_guitar",
            "additional_instruments": ["bass", "drums"]
        }
        
        with patch('ai.routes.music_ai_service.MusicAIService') as mock_service_class:
            mock_service = mock_music_ai_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/music/instrument-combinations", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "combinations" in data
            
            combinations = data["combinations"]
            assert isinstance(combinations, list)
            assert len(combinations) > 0
            
            for combo in combinations:
                assert "instruments" in combo
                assert "description" in combo
                assert "suitability_score" in combo


class TestAudioAnalysisEndpoints:
    """Test audio analysis endpoints."""
    
    @pytest.mark.api
    def test_extract_comprehensive_features_success(self, client, mock_audio_feature_extractor, test_audio_file):
        """Test successful comprehensive feature extraction."""
        # Create a mock file upload
        files = {"audio_file": ("test.mp3", b"mock audio content", "audio/mpeg")}
        data = {
            "analysis_type": "comprehensive",
            "include_metadata": True,
            "include_visualization": False
        }
        
        with patch('ai.routes.audio_analysis.AudioFeatureExtractor') as mock_service_class:
            mock_service = mock_audio_feature_extractor
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/audio/extract-features", files=files, data=data)
            
            assert response.status_code == 200
            response_data = response.json()
            
            assert_success_response(response_data)
            assert "features" in response_data
            assert_valid_audio_features(response_data["features"])
    
    @pytest.mark.api
    def test_extract_rhythm_features_success(self, client, mock_audio_feature_extractor):
        """Test successful rhythm feature extraction."""
        files = {"audio_file": ("test.mp3", b"mock audio content", "audio/mpeg")}
        
        with patch('ai.routes.audio_analysis.AudioFeatureExtractor') as mock_service_class:
            mock_service = mock_audio_feature_extractor
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/audio/extract-features/rhythm", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "tempo" in data
            assert "beat_times" in data
            assert "beat_strength" in data
            assert "rhythm_complexity" in data
    
    @pytest.mark.api
    def test_extract_melody_features_success(self, client, mock_audio_feature_extractor):
        """Test successful melody feature extraction."""
        files = {"audio_file": ("test.mp3", b"mock audio content", "audio/mpeg")}
        
        with patch('ai.routes.audio_analysis.AudioFeatureExtractor') as mock_service_class:
            mock_service = mock_audio_feature_extractor
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/audio/extract-features/melody", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "pitch_contour" in data
            assert "melodic_intervals" in data
            assert "pitch_class_distribution" in data
            assert "tonal_strength" in data
    
    @pytest.mark.api
    def test_extract_harmony_features_success(self, client, mock_audio_feature_extractor):
        """Test successful harmony feature extraction."""
        files = {"audio_file": ("test.mp3", b"mock audio content", "audio/mpeg")}
        
        with patch('ai.routes.audio_analysis.AudioFeatureExtractor') as mock_service_class:
            mock_service = mock_audio_feature_extractor
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/audio/extract-features/harmony", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "chroma_features" in data
            assert "key_strength" in data
            assert "estimated_key" in data
            assert "harmonic_complexity" in data


class TestVideoAnalysisEndpoints:
    """Test video analysis endpoints."""
    
    @pytest.mark.api
    def test_analyze_video_tutorial_success(self, client, mock_video_analysis_service):
        """Test successful video tutorial analysis."""
        request_data = {
            "video_url": "https://youtube.com/watch?v=test123",
            "title": "Guitar Tutorial",
            "description": "Learn basic guitar chords",
            "focus_type": "harmony",
            "extract_audio": True,
            "analyze_patterns": True
        }
        
        with patch('ai.routes.video_analysis.VideoAnalysisService') as mock_service_class:
            mock_service = mock_video_analysis_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/video/analyze-tutorial", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "analysis" in data
            assert_valid_video_analysis(data["analysis"])
    
    @pytest.mark.api
    def test_extract_audio_from_video_success(self, client, mock_video_analysis_service):
        """Test successful audio extraction from video."""
        request_data = {
            "video_url": "https://youtube.com/watch?v=test123",
            "output_format": "wav",
            "quality": "high"
        }
        
        with patch('ai.routes.video_analysis.VideoAnalysisService') as mock_service_class:
            mock_service = mock_video_analysis_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/video/extract-audio", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "audio_path" in data
            assert "duration" in data
            assert "format" in data
            assert "sample_rate" in data
    
    @pytest.mark.api
    def test_detect_instruments_in_video_success(self, client, mock_video_analysis_service):
        """Test successful instrument detection in video."""
        request_data = {
            "video_url": "https://youtube.com/watch?v=test123",
            "target_instruments": ["guitar", "piano", "drums"],
            "confidence_threshold": 0.7
        }
        
        with patch('ai.routes.video_analysis.VideoAnalysisService') as mock_service_class:
            mock_service = mock_video_analysis_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/video/detect-instruments", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "detected_instruments" in data
            assert "confidence_scores" in data
            assert "timestamp_segments" in data
    
    @pytest.mark.api
    def test_generate_learning_exercises_success(self, client, mock_video_analysis_service):
        """Test successful learning exercise generation."""
        # Mock video analysis data
        video_analysis_data = {
            "musical_elements": {
                "rhythm": {"patterns": ["strumming"]},
                "melody": {"scale": "C Major"},
                "harmony": {"chords": ["C", "G", "Am", "F"]}
            },
            "learning_patterns": {
                "techniques": [
                    {"name": "Basic Strumming", "difficulty": "beginner"}
                ]
            }
        }
        
        request_data = {
            "video_analysis": video_analysis_data,
            "difficulty_levels": ["beginner", "intermediate"],
            "focus_areas": ["rhythm", "harmony"],
            "exercise_count": 5
        }
        
        with patch('ai.routes.video_analysis.VideoAnalysisService') as mock_service_class:
            mock_service = mock_video_analysis_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/video/generate-exercises", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "exercises" in data
            assert "difficulty_progression" in data
            assert "estimated_practice_time" in data
            
            exercises = data["exercises"]
            assert len(exercises) <= request_data["exercise_count"]


class TestProviderEndpoints:
    """Test provider service endpoints."""
    
    @pytest.mark.api
    def test_get_provider_status_success(self, client, mock_provider_service):
        """Test successful provider status retrieval."""
        with patch('ai.routes.provider_service.ProviderService') as mock_service_class:
            mock_service = mock_provider_service
            mock_service_class.return_value = mock_service
            
            response = client.get("/api/v1/providers/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "providers" in data
            assert "total_providers" in data
            assert "available_providers" in data
    
    @pytest.mark.api
    def test_route_to_provider_success(self, client, mock_provider_service):
        """Test successful provider routing."""
        request_data = {
            "task_type": "music_theory",
            "prompt": "Explain chord progressions",
            "model_preference": "fast",
            "complexity": "simple"
        }
        
        with patch('ai.routes.provider_service.ProviderService') as mock_service_class:
            mock_service = mock_provider_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/providers/route", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "provider" in data
            assert "model" in data
            assert "response" in data
            assert "latency" in data
            assert "tokens_used" in data
    
    @pytest.mark.api
    def test_get_provider_models_success(self, client, mock_provider_service):
        """Test successful provider models retrieval."""
        provider_name = "anthropic"
        
        with patch('ai.routes.provider_service.ProviderService') as mock_service_class:
            mock_service = mock_provider_service
            mock_service_class.return_value = mock_service
            
            response = client.get(f"/api/v1/providers/{provider_name}/models")
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert data["provider"] == provider_name
            assert "models" in data
            assert "capabilities" in data
    
    @pytest.mark.api
    def test_estimate_request_cost_success(self, client, mock_provider_service):
        """Test successful request cost estimation."""
        request_data = {
            "provider": "anthropic",
            "model": "claude-3-sonnet",
            "prompt_tokens": 100,
            "max_completion_tokens": 500
        }
        
        with patch('ai.routes.provider_service.ProviderService') as mock_service_class:
            mock_service = mock_provider_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/providers/estimate-cost", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "estimated_cost" in data
            assert "currency" in data
            assert "cost_breakdown" in data


class TestHeartMuLaEndpoints:
    """Test HeartMuLa service endpoints."""
    
    @pytest.mark.api
    def test_generate_music_success(self, client, mock_heartmula_service):
        """Test successful music generation."""
        request_data = {
            "title": "Test Music",
            "genre": "lofi",
            "mood": "chill",
            "duration": 60,
            "prompt": "A relaxing lofi track",
            "instrumentation": ["piano", "drums"],
            "tempo": 85,
            "key": "C Major"
        }
        
        with patch('ai.routes.heartmula.HeartMuLaService') as mock_service_class:
            mock_service = mock_heartmula_service
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/heartmula/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert "task_id" in data
            assert "estimated_time" in data
            assert "status" in data
    
    @pytest.mark.api
    def test_check_generation_status_success(self, client, mock_heartmula_service):
        """Test successful generation status check."""
        task_id = "heartmula_task_123"
        
        with patch('ai.routes.heartmula.HeartMuLaService') as mock_service_class:
            mock_service = mock_heartmula_service
            mock_service_class.return_value = mock_service
            
            response = client.get(f"/api/v1/heartmula/status/{task_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert data["task_id"] == task_id
            assert "status" in data
            assert "progress" in data
            assert "result_url" in data if data["status"] == "completed" else True
    
    @pytest.mark.api
    def test_get_music_details_success(self, client, mock_heartmula_service):
        """Test successful music details retrieval."""
        music_id = "heartmula_music_123"
        
        with patch('ai.routes.heartmula.HeartMuLaService') as mock_service_class:
            mock_service = mock_heartmula_service
            mock_service_class.return_value = mock_service
            
            response = client.get(f"/api/v1/heartmula/music/{music_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert_success_response(data)
            assert data["music_id"] == music_id
            assert "title" in data
            assert "artist" in data
            assert "genre" in data
            assert "mood" in data
            assert "duration" in data
            assert "audio_url" in data


class TestFileUploadEndpoints:
    """Test file upload endpoints."""
    
    @pytest.mark.api
    def test_upload_audio_file_success(self, client):
        """Test successful audio file upload."""
        # Create a mock audio file
        audio_content = b"mock audio content"
        files = {
            "file": ("test.mp3", audio_content, "audio/mpeg"),
            "metadata": ("metadata.json", b'{"title": "Test Audio"}', "application/json")
        }
        
        response = client.post("/api/v1/upload/audio", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert_success_response(data)
        assert "file_id" in data
        assert "file_path" in data
        assert "metadata" in data
    
    @pytest.mark.api
    def test_upload_video_file_success(self, client):
        """Test successful video file upload."""
        # Create a mock video file
        video_content = b"mock video content"
        files = {
            "file": ("test.mp4", video_content, "video/mp4"),
            "metadata": ("metadata.json", b'{"title": "Test Video"}', "application/json")
        }
        
        response = client.post("/api/v1/upload/video", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert_success_response(data)
        assert "file_id" in data
        assert "file_path" in data
        assert "metadata" in data
    
    @pytest.mark.api
    def test_upload_invalid_file_type(self, client):
        """Test file upload with invalid file type."""
        # Create a mock file with invalid type
        invalid_content = b"mock invalid content"
        files = {
            "file": ("test.exe", invalid_content, "application/x-executable")
        }
        
        response = client.post("/api/v1/upload/audio", files=files)
        
        assert response.status_code == 400
        data = response.json()
        
        assert_error_response(data)
        assert "file type" in data["error"]["message"].lower()


class TestErrorHandling:
    """Test error handling across all endpoints."""
    
    @pytest.mark.api
    def test_invalid_endpoint(self, client):
        """Test access to invalid endpoint."""
        response = client.get("/api/v1/invalid/endpoint")
        
        assert response.status_code == 404
        data = response.json()
        
        assert_error_response(data)
        assert data["error"]["status_code"] == 404
    
    @pytest.mark.api
    def test_method_not_allowed(self, client):
        """Test method not allowed for endpoint."""
        response = client.delete("/api/v1/providers/status")  # DELETE on GET-only endpoint
        
        assert response.status_code == 405
        data = response.json()
        
        assert_error_response(data)
        assert data["error"]["status_code"] == 405
    
    @pytest.mark.api
    def test_missing_required_field(self, client):
        """Test request with missing required field."""
        request_data = {"genre": "lofi"}  # Missing required fields for music concepts
        
        response = client.post("/api/v1/music/concepts", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert_error_response(data)
        assert data["error"]["status_code"] == 422
    
    @pytest.mark.api
    def test_rate_limiting(self, client):
        """Test rate limiting functionality."""
        # Make multiple rapid requests to trigger rate limiting
        for _ in range(100):  # Assuming rate limit is lower than this
            response = client.get("/health")
            if response.status_code == 429:
                break
        
        # If rate limiting is implemented, we should get a 429 response
        if response.status_code == 429:
            data = response.json()
            assert_error_response(data)
            assert data["error"]["status_code"] == 429
            assert "rate limit" in data["error"]["message"].lower()


class TestAPIIntegration:
    """Integration tests for API workflows."""
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_complete_music_analysis_workflow(self, client, mock_music_ai_service, mock_audio_feature_extractor):
        """Test complete music analysis workflow through API."""
        with patch('ai.routes.music_ai_service.MusicAIService') as mock_music_class:
            mock_music_class.return_value = mock_music_ai_service
            
            with patch('ai.routes.audio_analysis.AudioFeatureExtractor') as mock_audio_class:
                mock_audio_class.return_value = mock_audio_feature_extractor
                
                # Step 1: Generate music concepts
                concepts_request = {
                    "genre": "lofi",
                    "mood": "chill",
                    "title": "Analysis Test",
                    "prompt": "A lofi track for analysis"
                }
                
                concepts_response = client.post("/api/v1/music/concepts", json=concepts_request)
                assert concepts_response.status_code == 200
                concepts_data = concepts_response.json()
                
                # Step 2: Upload audio file for analysis
                audio_content = b"mock audio for analysis"
                files = {"file": ("analysis.mp3", audio_content, "audio/mpeg")}
                upload_response = client.post("/api/v1/upload/audio", files=files)
                assert upload_response.status_code == 200
                upload_data = upload_response.json()
                
                # Step 3: Extract comprehensive features
                feature_files = {"audio_file": ("analysis.mp3", audio_content, "audio/mpeg")}
                features_response = client.post("/api/v1/audio/extract-features", files=feature_files)
                assert features_response.status_code == 200
                features_data = features_response.json()
                
                # Verify workflow consistency
                assert "concepts" in concepts_data
                assert "file_id" in upload_data
                assert "features" in features_data
                
                # Verify that genre and mood are consistent
                assert concepts_data["concepts"]["rhythm"][0] in ["steady beat", "simple rhythm"]
                assert features_data["features"]["rhythm"]["tempo"] >= 60
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_complete_video_tutorial_workflow(self, client, mock_video_analysis_service, mock_heartmula_service):
        """Test complete video tutorial workflow through API."""
        with patch('ai.routes.video_analysis.VideoAnalysisService') as mock_video_class:
            mock_video_class.return_value = mock_video_analysis_service
            
            with patch('ai.routes.heartmula.HeartMuLaService') as mock_heartmula_class:
                mock_heartmula_class.return_value = mock_heartmula_service
                
                # Step 1: Analyze video tutorial
                analysis_request = {
                    "video_url": "https://youtube.com/watch?v=tutorial_test",
                    "title": "Complete Tutorial Analysis",
                    "description": "A comprehensive guitar tutorial",
                    "focus_type": "all",
                    "extract_audio": True,
                    "analyze_patterns": True
                }
                
                analysis_response = client.post("/api/v1/video/analyze-tutorial", json=analysis_request)
                assert analysis_response.status_code == 200
                analysis_data = analysis_response.json()
                
                # Step 2: Generate learning exercises
                exercises_request = {
                    "video_analysis": analysis_data["analysis"],
                    "difficulty_levels": ["beginner", "intermediate"],
                    "focus_areas": ["rhythm", "harmony"],
                    "exercise_count": 3
                }
                
                exercises_response = client.post("/api/v1/video/generate-exercises", json=exercises_request)
                assert exercises_response.status_code == 200
                exercises_data = exercises_response.json()
                
                # Step 3: Generate practice music using HeartMuLa
                music_request = {
                    "title": "Practice Music",
                    "genre": "lofi",
                    "mood": "chill",
                    "duration": 120,
                    "prompt": "Background music for practice",
                    "based_on_analysis": True,
                    "analysis_data": {
                        "key": analysis_data["analysis"]["musical_elements"]["harmony"]["estimated_key"],
                        "tempo": analysis_data["analysis"]["audio_analysis"]["rhythm"]["tempo"]
                    }
                }
                
                music_response = client.post("/api/v1/heartmula/generate", json=music_request)
                assert music_response.status_code == 200
                music_data = music_response.json()
                
                # Verify workflow consistency
                assert "analysis" in analysis_data
                assert "exercises" in exercises_data
                assert "task_id" in music_data
                
                # Verify that exercises match the analysis difficulty
                exercises = exercises_data["exercises"]
        analysis_difficulty = analysis_data["analysis"]["learning_patterns"]["techniques"][0]["difficulty"]
        
        # At least one exercise should match the analysis difficulty
        assert any(ex["difficulty"] == analysis_difficulty for ex in exercises)
        
        # Verify that generated music matches analysis key and tempo
        assert "based_on_analysis" in music_request
        assert music_request["analysis_data"]["key"] == analysis_data["analysis"]["musical_elements"]["harmony"]["estimated_key"]
        assert abs(music_request["analysis_data"]["tempo"] - analysis_data["analysis"]["audio_analysis"]["rhythm"]["tempo"]) < 10