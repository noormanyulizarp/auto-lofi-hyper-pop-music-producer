# Unit Tests for Music AI Service
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from tests.fixtures import (
    mock_music_ai_service, 
    test_music_request,
    test_app,
    client
)
from tests.mocks import (
    MockOpenRouterClient, 
    mock_openrouter,
    MockGLMClient,
    mock_glm
)
from tests.assertions import (
    assert_success_response,
    assert_error_response,
    assert_valid_music_concepts,
    assert_valid_generation_parameters,
    assert_approximately_equal
)

# Import the service class
from ai.services.music_ai_service import MusicAIService


class TestMusicAIService:
    """Test suite for Music AI Service."""
    
    @pytest.fixture
    def music_service(self, mock_openrouter_client):
        """Create a Music AI Service instance with mocked dependencies."""
        with mock_openrouter():
            service = MusicAIService()
            service.openrouter_client = mock_openrouter_client
            service.glm_search_client = MockGLMClient()
            service.glm_reader_client = MockGLMClient()
            return service
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_music_concepts_success(self, music_service):
        """Test successful music concept generation."""
        request_data = {
            "genre": "lofi",
            "mood": "chill",
            "title": "Test Music",
            "prompt": "A relaxing lofi track"
        }
        
        result = await music_service.generate_music_concepts(request_data)
        
        assert_success_response(result)
        assert "concepts" in result
        assert_valid_music_concepts(result["concepts"])
        
        # Verify expected concept categories
        concepts = result["concepts"]
        for category in ["rhythm", "melody", "harmony", "structure"]:
            assert category in concepts
            assert len(concepts[category]) > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_music_concepts_invalid_input(self, music_service):
        """Test music concept generation with invalid input."""
        request_data = {
            "genre": "invalid_genre",
            "mood": "chill",
            "title": "",
            "prompt": "A relaxing lofi track"
        }
        
        result = await music_service.generate_music_concepts(request_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_enhance_music_prompt_success(self, music_service):
        """Test successful music prompt enhancement."""
        original_prompt = "A relaxing lofi track"
        
        result = await music_service.enhance_music_prompt(original_prompt)
        
        assert_success_response(result)
        assert "enhanced_prompt" in result
        assert "enhancements" in result
        
        # Verify enhanced prompt is different from original
        assert result["enhanced_prompt"] != original_prompt
        assert len(result["enhanced_prompt"]) > len(original_prompt)
        
        # Verify enhancements list
        assert isinstance(result["enhancements"], list)
        assert len(result["enhancements"]) > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_enhance_music_prompt_empty_input(self, music_service):
        """Test prompt enhancement with empty input."""
        result = await music_service.enhance_music_prompt("")
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_optimal_generation_parameters_success(self, music_service):
        """Test successful optimal generation parameters retrieval."""
        request_data = {
            "genre": "lofi",
            "mood": "chill",
            "duration": 60
        }
        
        result = await music_service.get_optimal_generation_parameters(request_data)
        
        assert_success_response(result)
        assert "parameters" in result
        assert "confidence" in result
        
        # Validate parameters structure
        params = result["parameters"]
        assert_valid_generation_parameters(params)
        
        # Validate confidence score
        confidence = result["confidence"]
        assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_optimal_generation_parameters_unknown_genre(self, music_service):
        """Test optimal parameters with unknown genre."""
        request_data = {
            "genre": "unknown_genre",
            "mood": "chill",
            "duration": 60
        }
        
        result = await music_service.get_optimal_generation_parameters(request_data)
        
        # Should still work but with lower confidence
        assert_success_response(result)
        assert result["confidence"] < 0.5
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_music_theory_advice_success(self, music_service):
        """Test successful music theory advice generation."""
        request_data = {
            "genre": "jazz",
            "key": "C Major",
            "complexity": "intermediate"
        }
        
        result = await music_service.generate_music_theory_advice(request_data)
        
        assert_success_response(result)
        assert "advice" in result
        
        # Validate advice structure
        advice = result["advice"]
        expected_keys = ["chord_progressions", "scale_options", "rhythm_patterns", "production_tips"]
        for key in expected_keys:
            assert key in advice
            assert isinstance(advice[key], list)
            assert len(advice[key]) > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_music_theory_advice_invalid_key(self, music_service):
        """Test music theory advice with invalid key."""
        request_data = {
            "genre": "jazz",
            "key": "invalid key",
            "complexity": "intermediate"
        }
        
        result = await music_service.generate_music_theory_advice(request_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_music_trends_success(self, music_service):
        """Test successful music trends analysis."""
        genre = "lofi"
        
        result = await music_service.analyze_music_trends(genre)
        
        assert_success_response(result)
        assert "trends" in result
        assert "insights" in result
        
        # Validate trends data
        trends = result["trends"]
        assert isinstance(trends, list)
        assert len(trends) > 0
        
        # Validate insights
        insights = result["insights"]
        assert isinstance(insights, str)
        assert len(insights) > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_music_trends_with_timeframe(self, music_service):
        """Test music trends analysis with specific timeframe."""
        genre = "electronic"
        timeframe = "2024"
        
        result = await music_service.analyze_music_trends(genre, timeframe)
        
        assert_success_response(result)
        assert "trends" in result
        
        # Verify timeframe is incorporated in analysis
        trends = result["trends"]
        for trend in trends:
            assert "2024" in trend.get("period", "") or "2024" in trend.get("description", "")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_genre_characteristics_success(self, music_service):
        """Test successful genre characteristics retrieval."""
        genre = "classical"
        
        result = await music_service.get_genre_characteristics(genre)
        
        assert_success_response(result)
        assert "characteristics" in result
        
        # Validate characteristics structure
        characteristics = result["characteristics"]
        expected_keys = ["rhythm", "harmony", "melody", "instrumentation", "structure"]
        for key in expected_keys:
            assert key in characteristics
            assert isinstance(characteristics[key], list)
            assert len(characteristics[key]) > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_genre_characteristics_unknown_genre(self, music_service):
        """Test genre characteristics for unknown genre."""
        result = await music_service.get_genre_characteristics("unknown_genre")
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_suggest_instrument_combinations_success(self, music_service):
        """Test successful instrument combination suggestions."""
        genre = "jazz"
        mood = "upbeat"
        
        result = await music_service.suggest_instrument_combinations(genre, mood)
        
        assert_success_response(result)
        assert "combinations" in result
        
        # Validate combinations
        combinations = result["combinations"]
        assert isinstance(combinations, list)
        assert len(combinations) > 0
        
        # Each combination should have valid structure
        for combo in combinations:
            assert "instruments" in combo
            assert "description" in combo
            assert "suitability_score" in combo
            assert 0.0 <= combo["suitability_score"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_suggest_instrument_combinations_with_primary(self, music_service):
        """Test instrument combinations with primary instrument specified."""
        genre = "rock"
        mood = "energetic"
        primary_instrument = "electric guitar"
        
        result = await music_service.suggest_instrument_combinations(
            genre, mood, primary_instrument
        )
        
        assert_success_response(result)
        
        # Verify primary instrument is included in combinations
        combinations = result["combinations"]
        for combo in combinations:
            instruments = combo["instruments"]
            assert primary_instrument in instruments
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_musical_outline_success(self, music_service):
        """Test successful musical outline creation."""
        request_data = {
            "title": "Test Composition",
            "genre": "electronic",
            "duration": 180,
            "structure_type": "verse-chorus",
            "mood": "energetic"
        }
        
        result = await music_service.create_musical_outline(request_data)
        
        assert_success_response(result)
        assert "outline" in result
        
        # Validate outline structure
        outline = result["outline"]
        expected_keys = ["sections", "total_duration", "time_signature", "key"]
        for key in expected_keys:
            assert key in outline
        
        # Validate sections
        sections = outline["sections"]
        assert isinstance(sections, list)
        assert len(sections) > 0
        
        # Validate section structure
        for section in sections:
            assert "name" in section
            assert "duration" in section
            assert "description" in section
            assert section["duration"] > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_musical_outline_invalid_structure(self, music_service):
        """Test musical outline with invalid structure type."""
        request_data = {
            "title": "Test Composition",
            "genre": "electronic",
            "duration": 180,
            "structure_type": "invalid_structure",
            "mood": "energetic"
        }
        
        result = await music_service.create_musical_outline(request_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_harmonic_progression_success(self, music_service):
        """Test successful harmonic progression analysis."""
        progression = ["C", "G", "Am", "F"]
        key = "C Major"
        
        result = await music_service.analyze_harmonic_progression(progression, key)
        
        assert_success_response(result)
        assert "analysis" in result
        
        # Validate analysis structure
        analysis = result["analysis"]
        expected_keys = ["function", "complexity", "commonness", "suggestions"]
        for key in expected_keys:
            assert key in analysis
        
        # Validate complexity score
        assert 0.0 <= analysis["complexity"] <= 1.0
        assert 0.0 <= analysis["commonness"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_harmonic_progression_invalid_chords(self, music_service):
        """Test harmonic progression analysis with invalid chords."""
        progression = ["C", "invalid_chord", "Am", "F"]
        key = "C Major"
        
        result = await music_service.analyze_harmonic_progression(progression, key)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_melodic_ideas_success(self, music_service):
        """Test successful melodic ideas generation."""
        request_data = {
            "key": "C Major",
            "scale": "major",
            "mood": "happy",
            "complexity": "simple",
            "duration_bars": 4
        }
        
        result = await music_service.generate_melodic_ideas(request_data)
        
        assert_success_response(result)
        assert "melodic_ideas" in result
        
        # Validate melodic ideas
        ideas = result["melodic_ideas"]
        assert isinstance(ideas, list)
        assert len(ideas) > 0
        
        # Validate each idea structure
        for idea in ideas:
            assert "notes" in idea
            assert "rhythm" in idea
            assert "description" in idea
            assert "difficulty" in idea
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_melodic_ideas_invalid_key(self, music_service):
        """Test melodic ideas generation with invalid key."""
        request_data = {
            "key": "invalid key",
            "scale": "major",
            "mood": "happy",
            "complexity": "simple",
            "duration_bars": 4
        }
        
        result = await music_service.generate_melodic_ideas(request_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommend_production_techniques_success(self, music_service):
        """Test successful production techniques recommendation."""
        genre = "lofi"
        instruments = ["piano", "drums"]
        target_mood = "chill"
        
        result = await music_service.recommend_production_techniques(
            genre, instruments, target_mood
        )
        
        assert_success_response(result)
        assert "techniques" in result
        
        # Validate techniques
        techniques = result["techniques"]
        assert isinstance(techniques, list)
        assert len(techniques) > 0
        
        # Validate each technique
        for technique in techniques:
            assert "name" in technique
            assert "description" in technique
            assert "difficulty" in technique
            assert "applicability" in technique
            assert technique["difficulty"] in ["beginner", "intermediate", "advanced"]
            assert 0.0 <= technique["applicability"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommend_production_techniques_unknown_genre(self, music_service):
        """Test production techniques for unknown genre."""
        result = await music_service.recommend_production_techniques(
            "unknown_genre", ["piano"], "chill"
        )
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 404


class TestMusicAIServiceErrorHandling:
    """Test error handling in Music AI Service."""
    
    @pytest.fixture
    def error_prone_service(self):
        """Create a service that simulates various errors."""
        service = MusicAIService()
        
        # Mock the OpenRouter client to raise exceptions
        service.openrouter_client = Mock()
        service.openrouter_client.chat.completions.create.side_effect = Exception("API Error")
        
        return service
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_api_error_handling(self, error_prone_service):
        """Test handling of API errors."""
        request_data = {
            "genre": "lofi",
            "mood": "chill",
            "title": "Test Music",
            "prompt": "A relaxing lofi track"
        }
        
        result = await error_prone_service.generate_music_concepts(request_data)
        
        assert_error_response(result)
        assert "API Error" in result["error"]["message"]
        assert result["error"]["status_code"] == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, error_prone_service):
        """Test handling of timeout errors."""
        import asyncio
        
        # Simulate timeout error
        error_prone_service.openrouter_client.chat.completions.create.side_effect = \
            asyncio.TimeoutError("Request timeout")
        
        request_data = {
            "genre": "lofi",
            "mood": "chill",
            "title": "Test Music",
            "prompt": "A relaxing lofi track"
        }
        
        result = await error_prone_service.generate_music_concepts(request_data)
        
        assert_error_response(result)
        assert "timeout" in result["error"]["message"].lower()
        assert result["error"]["status_code"] == 408
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self, error_prone_service):
        """Test handling of rate limit errors."""
        # Simulate rate limit error
        class RateLimitError(Exception):
            def __init__(self):
                self.status_code = 429
                self.message = "Rate limit exceeded"
        
        error_prone_service.openrouter_client.chat.completions.create.side_effect = RateLimitError()
        
        request_data = {
            "genre": "lofi",
            "mood": "chill",
            "title": "Test Music",
            "prompt": "A relaxing lofi track"
        }
        
        result = await error_prone_service.generate_music_concepts(request_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 429
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, error_prone_service):
        """Test handling of authentication errors."""
        # Simulate authentication error
        class AuthenticationError(Exception):
            def __init__(self):
                self.status_code = 401
                self.message = "Invalid API key"
        
        error_prone_service.openrouter_client.chat.completions.create.side_effect = AuthenticationError()
        
        request_data = {
            "genre": "lofi",
            "mood": "chill",
            "title": "Test Music",
            "prompt": "A relaxing lofi track"
        }
        
        result = await error_prone_service.generate_music_concepts(request_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 401


class TestMusicAIServiceIntegration:
    """Integration tests for Music AI Service."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self, music_service):
        """Test complete workflow from prompt to parameters."""
        # Start with a basic prompt
        original_prompt = "A relaxing lofi track for studying"
        
        # Step 1: Enhance the prompt
        enhanced_result = await music_service.enhance_music_prompt(original_prompt)
        assert_success_response(enhanced_result)
        enhanced_prompt = enhanced_result["enhanced_prompt"]
        
        # Step 2: Generate music concepts
        concepts_request = {
            "genre": "lofi",
            "mood": "chill",
            "title": "Study Music",
            "prompt": enhanced_prompt
        }
        concepts_result = await music_service.generate_music_concepts(concepts_request)
        assert_success_response(concepts_result)
        
        # Step 3: Get optimal parameters
        params_request = {
            "genre": "lofi",
            "mood": "chill",
            "duration": 120
        }
        params_result = await music_service.get_optimal_generation_parameters(params_request)
        assert_success_response(params_result)
        
        # Step 4: Get production techniques
        techniques_result = await music_service.recommend_production_techniques(
            "lofi", ["piano", "drums"], "chill"
        )
        assert_success_response(techniques_result)
        
        # Verify all steps produced consistent results
        assert enhanced_prompt != original_prompt
        assert "concepts" in concepts_result
        assert "parameters" in params_result
        assert "techniques" in techniques_result
        
        # Verify parameters match the genre/mood
        parameters = params_result["parameters"]
        assert 60 <= parameters["tempo"] <= 100  # Typical lofi tempo range
        assert "Major" in parameters["key"] or "Minor" in parameters["key"]
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_multiple_genre_analysis(self, music_service):
        """Test analysis across multiple genres."""
        genres = ["lofi", "jazz", "classical", "electronic"]
        
        results = {}
        for genre in genres:
            # Get genre characteristics
            char_result = await music_service.get_genre_characteristics(genre)
            assert_success_response(char_result)
            
            # Get optimal parameters
            params_result = await music_service.get_optimal_generation_parameters({
                "genre": genre,
                "mood": "neutral",
                "duration": 120
            })
            assert_success_response(params_result)
            
            results[genre] = {
                "characteristics": char_result["characteristics"],
                "parameters": params_result["parameters"]
            }
        
        # Verify that different genres produce different results
        lofi_params = results["lofi"]["parameters"]
        jazz_params = results["jazz"]["parameters"]
        classical_params = results["classical"]["parameters"]
        electronic_params = results["electronic"]["parameters"]
        
        # Tempos should vary significantly between genres
        tempos = [
            lofi_params["tempo"],
            jazz_params["tempo"],
            classical_params["tempo"],
            electronic_params["tempo"]
        ]
        
        # Check that tempos are not all the same
        assert len(set(tempos)) > 1, "All genres should not have the same tempo"
        
        # Check that characteristics are genre-appropriate
        lofi_char = results["lofi"]["characteristics"]
        assert any("simple" in char.lower() for char in lofi_char["rhythm"])
        
        jazz_char = results["jazz"]["characteristics"]
        assert any("complex" in char.lower() for char in jazz_char["harmony"])
        
        classical_char = results["classical"]["characteristics"]
        assert any("orchestra" in char.lower() or "strings" in char.lower() 
                  for char in classical_char["instrumentation"])
        
        electronic_char = results["electronic"]["characteristics"]
        assert any("synth" in char.lower() or "electronic" in char.lower() 
                  for char in electronic_char["instrumentation"])