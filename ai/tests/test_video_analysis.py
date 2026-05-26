# Unit Tests for Video Analysis Service
import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from tests.fixtures import (
    mock_video_analysis_service,
    test_video_file,
    test_video_request,
    sample_video_metadata
)
from tests.mocks import MockVideoProcessor, mock_video_processing
from tests.assertions import (
    assert_success_response,
    assert_error_response,
    assert_valid_video_analysis,
    assert_valid_learning_techniques,
    assert_valid_exercises
)

# Import the service class
from ai.services.video_analysis import VideoAnalysisService


class TestVideoAnalysisService:
    """Test suite for Video Analysis Service."""
    
    @pytest.fixture
    def video_service(self, mock_video_processor):
        """Create a Video Analysis Service instance with mocked dependencies."""
        with mock_video_processing():
            service = VideoAnalysisService()
            service.moviepy = mock_video_processor
            service.cv2 = mock_video_processor
            service.audio_extractor = Mock()
            return service
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_video_tutorial_success(self, video_service):
        """Test successful video tutorial analysis."""
        request_data = {
            "video_url": "https://youtube.com/watch?v=test123",
            "title": "Guitar Tutorial",
            "description": "Learn basic guitar chords",
            "focus_type": "harmony",
            "extract_audio": True,
            "analyze_patterns": True
        }
        
        result = await video_service.analyze_video_tutorial(request_data)
        
        assert_success_response(result)
        assert_valid_video_analysis(result["analysis"])
        
        # Verify analysis structure
        analysis = result["analysis"]
        assert "video_info" in analysis
        assert "audio_analysis" in analysis
        assert "musical_elements" in analysis
        assert "learning_patterns" in analysis
        
        # Validate video info
        video_info = analysis["video_info"]
        assert video_info["title"] == "Guitar Tutorial"
        assert video_info["duration"] > 0
        assert video_info["width"] > 0
        assert video_info["height"] > 0
        assert video_info["fps"] > 0
        
        # Validate musical elements
        musical_elements = analysis["musical_elements"]
        for element_type in ["rhythm", "melody", "harmony"]:
            assert element_type in musical_elements
            assert isinstance(musical_elements[element_type], dict)
        
        # Validate learning patterns
        learning_patterns = analysis["learning_patterns"]
        assert "techniques" in learning_patterns
        assert "exercises" in learning_patterns
        assert_valid_learning_techniques(learning_patterns["techniques"])
        assert_valid_exercises(learning_patterns["exercises"])
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_video_tutorial_minimal_request(self, video_service):
        """Test video tutorial analysis with minimal request data."""
        request_data = {
            "video_url": "https://youtube.com/watch?v=minimal",
            "title": "Minimal Tutorial"
        }
        
        result = await video_service.analyze_video_tutorial(request_data)
        
        assert_success_response(result)
        assert "analysis" in result
        
        # Should still provide basic analysis
        analysis = result["analysis"]
        assert "video_info" in analysis
        assert "musical_elements" in analysis
        assert "learning_patterns" in analysis
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_video_tutorial_invalid_url(self, video_service):
        """Test video tutorial analysis with invalid URL."""
        request_data = {
            "video_url": "invalid-url",
            "title": "Invalid URL Tutorial"
        }
        
        result = await video_service.analyze_video_tutorial(request_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_audio_from_video_success(self, video_service):
        """Test successful audio extraction from video."""
        # Mock video processor
        video_service.moviepy.extract_audio.return_value = {
            "success": True,
            "audio_path": "/tmp/extracted_audio.wav",
            "duration": 180.0,
            "sample_rate": 44100,
            "channels": 2
        }
        
        result = await video_service.extract_audio_from_video(test_video_file)
        
        assert_success_response(result)
        
        # Validate result structure
        assert "audio_path" in result
        assert "duration" in result
        assert "format" in result
        assert "sample_rate" in result
        
        # Validate values
        assert result["duration"] > 0
        assert result["sample_rate"] > 0
        assert result["format"] in ["wav", "mp3", "aac"]
        
        # Verify method was called
        video_service.moviepy.extract_audio.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_audio_from_video_nonexistent_file(self, video_service):
        """Test audio extraction from non-existent video file."""
        # Mock video processor to raise error
        video_service.moviepy.extract_audio.side_effect = Exception("File not found")
        
        result = await video_service.extract_audio_from_video("/nonexistent/video.mp4")
        
        assert_error_response(result)
        assert "File not found" in result["error"]["message"]
        assert result["error"]["status_code"] == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_video_frames_success(self, video_service):
        """Test successful video frame analysis."""
        # Mock video frames
        mock_frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(10)
        ]
        video_service.cv2.read_frames.return_value = iter(mock_frames)
        
        result = await video_service.analyze_video_frames(test_video_file)
        
        assert_success_response(result)
        
        # Validate result structure
        assert "frame_count" in result
        assert "resolution" in result
        assert "fps" in result
        assert "visual_elements" in result
        
        # Validate values
        assert result["frame_count"] == 10
        assert result["resolution"] == "640x480"
        assert result["fps"] > 0
        
        # Validate visual elements
        visual_elements = result["visual_elements"]
        assert "instruments" in visual_elements
        assert "hand_positions" in visual_elements
        assert "playing_techniques" in visual_elements
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_video_frames_corrupted_file(self, video_service):
        """Test frame analysis with corrupted video file."""
        # Mock video processor to raise error
        video_service.cv2.read_frames.side_effect = Exception("Corrupted video file")
        
        result = await video_service.analyze_video_frames(test_video_file)
        
        assert_error_response(result)
        assert "Corrupted" in result["error"]["message"]
        assert result["error"]["status_code"] == 422
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_instruments_in_video_success(self, video_service):
        """Test successful instrument detection in video."""
        # Mock video frames with guitar characteristics
        mock_frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(10)
        ]
        video_service.cv2.read_frames.return_value = iter(mock_frames)
        
        result = await video_service.detect_instruments_in_video(test_video_file)
        
        assert_success_response(result)
        
        # Validate result structure
        assert "detected_instruments" in result
        assert "confidence_scores" in result
        assert "timestamp_segments" in result
        
        # Validate instruments
        instruments = result["detected_instruments"]
        assert isinstance(instruments, list)
        assert len(instruments) > 0
        
        # Validate confidence scores
        confidence_scores = result["confidence_scores"]
        assert isinstance(confidence_scores, dict)
        for instrument, score in confidence_scores.items():
            assert 0.0 <= score <= 1.0
        
        # Validate timestamp segments
        timestamp_segments = result["timestamp_segments"]
        assert isinstance(timestamp_segments, list)
        for segment in timestamp_segments:
            assert "start_time" in segment
            assert "end_time" in segment
            assert "instrument" in segment
            assert segment["start_time"] <= segment["end_time"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_playing_techniques_success(self, video_service):
        """Test successful playing technique detection."""
        # Mock video frames with playing technique characteristics
        mock_frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(20)  # More frames for technique detection
        ]
        video_service.cv2.read_frames.return_value = iter(mock_frames)
        
        result = await video_service.detect_playing_techniques(test_video_file)
        
        assert_success_response(result)
        
        # Validate result structure
        assert "techniques" in result
        assert "confidence_scores" in result
        assert "timestamp_segments" in result
        
        # Validate techniques
        techniques = result["techniques"]
        assert isinstance(techniques, list)
        assert len(techniques) > 0
        
        # Each technique should have required fields
        for technique in techniques:
            assert "name" in technique
            assert "description" in technique
            assert "difficulty" in technique
            assert "timestamp" in technique
            assert technique["difficulty"] in ["beginner", "intermediate", "advanced"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_chord_progressions_from_video_success(self, video_service):
        """Test successful chord progression extraction from video."""
        # Mock combined video and audio analysis
        video_service.audio_extractor.extract_harmony_features.return_value = {
            "success": True,
            "chroma_features": [0.3, 0.1, 0.2, 0.05, 0.15, 0.05, 0.1, 0.05, 0.0, 0.05, 0.0, 0.0],
            "key_strength": 0.85,
            "estimated_key": "C Major",
            "harmonic_complexity": 0.4
        }
        
        result = await video_service.extract_chord_progressions_from_video(test_video_file)
        
        assert_success_response(result)
        
        # Validate result structure
        assert "chord_progressions" in result
        assert "key" in result
        assert "confidence_scores" in result
        assert "timestamp_segments" in result
        
        # Validate chord progressions
        chord_progressions = result["chord_progressions"]
        assert isinstance(chord_progressions, list)
        assert len(chord_progressions) > 0
        
        # Validate key
        assert "key" in result
        key_pattern = r'^[A-G][#b]?\s+(Major|Minor|maj|min|M|m)$'
        import re
        assert re.match(key_pattern, result["key"]), f"Invalid key format: {result['key']}"
        
        # Validate confidence scores
        confidence_scores = result["confidence_scores"]
        assert isinstance(confidence_scores, dict)
        for chord, score in confidence_scores.items():
            assert 0.0 <= score <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_learning_exercises_success(self, video_service):
        """Test successful learning exercise generation."""
        # Mock video analysis data
        video_analysis = {
            "musical_elements": {
                "rhythm": {
                    "patterns": ["strumming", "fingerpicking"],
                    "complexity": "intermediate"
                },
                "melody": {
                    "scale": "C Major",
                    "range": "one octave"
                },
                "harmony": {
                    "chords": ["C", "G", "Am", "F"],
                    "progression": "I-V-vi-IV"
                }
            },
            "learning_patterns": {
                "techniques": [
                    {
                        "name": "Basic Strumming",
                        "description": "Simple down-up pattern",
                        "difficulty": "beginner",
                        "timestamp": [30, 60]
                    }
                ]
            }
        }
        
        result = await video_service.generate_learning_exercises(video_analysis)
        
        assert_success_response(result)
        
        # Validate result structure
        assert "exercises" in result
        assert "difficulty_progression" in result
        assert "estimated_practice_time" in result
        
        # Validate exercises
        exercises = result["exercises"]
        assert isinstance(exercises, list)
        assert len(exercises) > 0
        assert_valid_exercises(exercises)
        
        # Validate difficulty progression
        difficulty_progression = result["difficulty_progression"]
        assert isinstance(difficulty_progression, list)
        assert all(level in ["beginner", "intermediate", "advanced"] for level in difficulty_progression)
        
        # Validate estimated practice time
        assert result["estimated_practice_time"] > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_teacher_demonstrations_success(self, video_service):
        """Test successful teacher demonstration analysis."""
        # Mock video frames with teacher demonstration
        mock_frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(30)
        ]
        video_service.cv2.read_frames.return_value = iter(mock_frames)
        
        result = await video_service.analyze_teacher_demonstrations(test_video_file)
        
        assert_success_response(result)
        
        # Validate result structure
        assert "demonstrations" in result
        assert "teaching_quality" in result
        assert "clarity_score" in result
        assert "effectiveness_rating" in result
        
        # Validate demonstrations
        demonstrations = result["demonstrations"]
        assert isinstance(demonstrations, list)
        assert len(demonstrations) > 0
        
        # Each demonstration should have required fields
        for demo in demonstrations:
            assert "technique" in demo
            assert "timestamp" in demo
            assert "clarity" in demo
            assert "pace" in demo
            assert "effectiveness" in demo
            assert 0.0 <= demo["clarity"] <= 1.0
            assert 0.0 <= demo["effectiveness"] <= 1.0
        
        # Validate quality scores
        assert 0.0 <= result["teaching_quality"] <= 1.0
        assert 0.0 <= result["clarity_score"] <= 1.0
        assert 0.0 <= result["effectiveness_rating"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_visual_cues_success(self, video_service):
        """Test successful visual cue extraction."""
        # Mock video frames with visual cues
        mock_frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(15)
        ]
        video_service.cv2.read_frames.return_value = iter(mock_frames)
        
        result = await video_service.extract_visual_cues(test_video_file)
        
        assert_success_response(result)
        
        # Validate result structure
        assert "hand_positions" in result
        assert "finger_movements" in result
        assert "body_posture" in result
        assert "instrument_position" in result
        
        # Validate hand positions
        hand_positions = result["hand_positions"]
        assert isinstance(hand_positions, list)
        assert len(hand_positions) > 0
        
        for position in hand_positions:
            assert "timestamp" in position
            assert "position_type" in position
            assert "coordinates" in position
        
        # Validate finger movements
        finger_movements = result["finger_movements"]
        assert isinstance(finger_movements, list)
        assert len(finger_movements) > 0
        
        for movement in finger_movements:
            assert "technique" in movement
            assert "timestamp" in movement
            assert "movement_type" in movement
        
        # Validate body posture
        body_posture = result["body_posture"]
        assert isinstance(body_posture, dict)
        assert "overall_posture" in body_posture
        assert "posture_changes" in body_posture
        
        # Validate instrument position
        instrument_position = result["instrument_position"]
        assert isinstance(instrument_position, dict)
        assert "position_type" in instrument_position
        assert "stability" in instrument_position
        assert 0.0 <= instrument_position["stability"] <= 1.0


class TestVideoAnalysisServiceErrorHandling:
    """Test error handling in Video Analysis Service."""
    
    @pytest.fixture
    def error_prone_service(self):
        """Create a service that simulates various errors."""
        service = VideoAnalysisService()
        
        # Mock video processing to raise exceptions
        service.moviepy = Mock()
        service.moviepy.extract_audio.side_effect = Exception("Video processing error")
        service.cv2 = Mock()
        service.cv2.read_frames.side_effect = Exception("Frame processing error")
        
        return service
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_video_processing_error_handling(self, error_prone_service):
        """Test handling of video processing errors."""
        request_data = {
            "video_url": "https://youtube.com/watch?v=test123",
            "title": "Error Test Video"
        }
        
        result = await error_prone_service.analyze_video_tutorial(request_data)
        
        assert_error_response(result)
        assert "Video processing error" in result["error"]["message"]
        assert result["error"]["status_code"] == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_frame_processing_error_handling(self, error_prone_service):
        """Test handling of frame processing errors."""
        result = await error_prone_service.analyze_video_frames(test_video_file)
        
        assert_error_response(result)
        assert "Frame processing error" in result["error"]["message"]
        assert result["error"]["status_code"] == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unsupported_video_format_error_handling(self, error_prone_service):
        """Test handling of unsupported video format errors."""
        # Mock specific error for unsupported format
        class UnsupportedFormatError(Exception):
            pass
        
        error_prone_service.moviepy.extract_audio.side_effect = UnsupportedFormatError("Unsupported video format")
        
        result = await error_prone_service.extract_audio_from_video("test.unsupported")
        
        assert_error_response(result)
        assert "Unsupported" in result["error"]["message"]
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_network_error_handling(self, error_prone_service):
        """Test handling of network errors."""
        # Mock network error
        class NetworkError(Exception):
            pass
        
        error_prone_service.moviepy.extract_audio.side_effect = NetworkError("Network connection failed")
        
        result = await error_prone_service.extract_audio_from_video("https://remote.com/video.mp4")
        
        assert_error_response(result)
        assert "Network" in result["error"]["message"]
        assert result["error"]["status_code"] == 503


class TestVideoAnalysisServiceIntegration:
    """Integration tests for Video Analysis Service."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_video_analysis_workflow(self, video_service):
        """Test complete video analysis workflow."""
        # Mock video processing
        mock_frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(20)
        ]
        video_service.cv2.read_frames.return_value = iter(mock_frames)
        video_service.moviepy.extract_audio.return_value = {
            "success": True,
            "audio_path": "/tmp/extracted_audio.wav",
            "duration": 180.0,
            "sample_rate": 44100,
            "channels": 2
        }
        
        # Mock audio extractor
        video_service.audio_extractor.extract_comprehensive_features.return_value = {
            "success": True,
            "features": {
                "rhythm": {"tempo": 120.0, "beat_strength": 0.8},
                "melody": {"tonal_strength": 0.75},
                "harmony": {"estimated_key": "C Major", "key_strength": 0.85},
                "timbre": {"spectral_centroid": 2500.0},
                "structure": {"form_type": "verse-chorus"}
            },
            "metadata": {"duration": 180.0, "sample_rate": 44100}
        }
        
        request_data = {
            "video_url": "https://youtube.com/watch?v=workflow_test",
            "title": "Complete Workflow Test",
            "focus_type": "all",
            "extract_audio": True,
            "analyze_patterns": True
        }
        
        # Step 1: Analyze video tutorial
        tutorial_result = await video_service.analyze_video_tutorial(request_data)
        assert_success_response(tutorial_result)
        
        # Step 2: Extract audio
        audio_result = await video_service.extract_audio_from_video(test_video_file)
        assert_success_response(audio_result)
        
        # Step 3: Analyze video frames
        frames_result = await video_service.analyze_video_frames(test_video_file)
        assert_success_response(frames_result)
        
        # Step 4: Detect instruments
        instruments_result = await video_service.detect_instruments_in_video(test_video_file)
        assert_success_response(instruments_result)
        
        # Step 5: Detect playing techniques
        techniques_result = await video_service.detect_playing_techniques(test_video_file)
        assert_success_response(techniques_result)
        
        # Step 6: Extract chord progressions
        chords_result = await video_service.extract_chord_progressions_from_video(test_video_file)
        assert_success_response(chords_result)
        
        # Step 7: Generate learning exercises
        exercises_result = await video_service.generate_learning_exercises(tutorial_result["analysis"])
        assert_success_response(exercises_result)
        
        # Step 8: Analyze teacher demonstrations
        demo_result = await video_service.analyze_teacher_demonstrations(test_video_file)
        assert_success_response(demo_result)
        
        # Verify consistency across results
        tutorial_analysis = tutorial_result["analysis"]
        
        # Verify that musical elements are consistent
        assert tutorial_analysis["musical_elements"]["harmony"]["estimated_key"] == chords_result["key"]
        
        # Verify that techniques are detected
        detected_techniques = techniques_result["techniques"]
        learning_techniques = tutorial_analysis["learning_patterns"]["techniques"]
        
        # Should have some overlap in techniques
        technique_names = [t["name"] for t in detected_techniques]
        learning_names = [t["name"] for t in learning_techniques]
        
        # At least some techniques should match
        assert len(set(technique_names) & set(learning_names)) > 0
        
        # Verify exercises are based on detected elements
        exercises = exercises_result["exercises"]
        assert len(exercises) > 0
        
        # Exercises should match the difficulty level of detected techniques
        difficulties = [ex["difficulty"] for ex in exercises]
        technique_difficulties = [t["difficulty"] for t in detected_techniques]
        
        # Should cover the range of difficulties
        assert set(difficulties).issubset({"beginner", "intermediate", "advanced"})
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_multiple_video_analysis_consistency(self, video_service):
        """Test analysis consistency across multiple similar videos."""
        # Create mock data for multiple similar videos
        videos = [
            {"url": "https://youtube.com/watch?v=similar1", "title": "Similar Guitar Lesson 1"},
            {"url": "https://youtube.com/watch?v=similar2", "title": "Similar Guitar Lesson 2"},
            {"url": "https://youtube.com/watch?v=similar3", "title": "Similar Guitar Lesson 3"}
        ]
        
        # Mock consistent video processing
        mock_frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(20)
        ]
        video_service.cv2.read_frames.return_value = iter(mock_frames)
        video_service.moviepy.extract_audio.return_value = {
            "success": True,
            "audio_path": "/tmp/extracted_audio.wav",
            "duration": 180.0,
            "sample_rate": 44100,
            "channels": 2
        }
        
        # Mock consistent audio features
        video_service.audio_extractor.extract_comprehensive_features.return_value = {
            "success": True,
            "features": {
                "rhythm": {"tempo": 120.0, "beat_strength": 0.8},
                "melody": {"tonal_strength": 0.75},
                "harmony": {"estimated_key": "G Major", "key_strength": 0.85},
                "timbre": {"spectral_centroid": 2500.0},
                "structure": {"form_type": "verse-chorus"}
            },
            "metadata": {"duration": 180.0, "sample_rate": 44100}
        }
        
        results = []
        
        for video in videos:
            request_data = {
                "video_url": video["url"],
                "title": video["title"],
                "focus_type": "all",
                "extract_audio": True,
                "analyze_patterns": True
            }
            
            result = await video_service.analyze_video_tutorial(request_data)
            assert_success_response(result)
            results.append(result["analysis"])
        
        # Verify consistency across similar videos
        # All should have the same estimated key
        keys = [r["musical_elements"]["harmony"]["estimated_key"] for r in results]
        assert all(key == keys[0] for key in keys)
        
        # All should have similar tempo ranges
        tempos = [r["audio_analysis"]["rhythm"]["tempo"] for r in results]
        avg_tempo = sum(tempos) / len(tempos)
        
        for tempo in tempos:
            assert abs(tempo - avg_tempo) < 10.0  # Within 10 BPM
        
        # All should detect similar instruments
        instruments_list = [r["musical_elements"]["rhythm"]["instruments"] for r in results]
        common_instruments = set(instruments_list[0])
        for instruments in instruments_list[1:]:
            common_instruments = common_instruments & set(instruments)
        
        # Should have at least some common instruments
        assert len(common_instruments) > 0
        
        # All should have similar musical complexity
        complexities = []
        for r in results:
            rhythm_complexity = r["musical_elements"]["rhythm"]["complexity"]
            harmonic_complexity = r["musical_elements"]["harmony"]["complexity"]
            complexities.append((rhythm_complexity, harmonic_complexity))
        
        # Complexities should be similar
        # (This is a loose check since complexity can be subjective)
        complexity_levels = set([c[0] for c in complexities] + [c[1] for c in complexities])
        assert len(complexity_levels) <= 4  # Should not have too many different complexity levels
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_performance_optimization(self, video_service):
        """Test performance optimization of video analysis."""
        import time
        
        # Mock video processing
        mock_frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(10)  # Fewer frames for performance test
        ]
        video_service.cv2.read_frames.return_value = iter(mock_frames)
        video_service.moviepy.extract_audio.return_value = {
            "success": True,
            "audio_path": "/tmp/extracted_audio.wav",
            "duration": 60.0,  # Shorter duration for performance test
            "sample_rate": 44100,
            "channels": 2
        }
        
        # Mock audio extractor
        video_service.audio_extractor.extract_comprehensive_features.return_value = {
            "success": True,
            "features": {
                "rhythm": {"tempo": 120.0, "beat_strength": 0.8},
                "melody": {"tonal_strength": 0.75},
                "harmony": {"estimated_key": "C Major", "key_strength": 0.85},
                "timbre": {"spectral_centroid": 2500.0},
                "structure": {"form_type": "verse-chorus"}
            },
            "metadata": {"duration": 60.0, "sample_rate": 44100}
        }
        
        request_data = {
            "video_url": "https://youtube.com/watch?v=performance_test",
            "title": "Performance Test Video",
            "focus_type": "basic",
            "extract_audio": True,
            "analyze_patterns": False  # Disable pattern analysis for performance
        }
        
        # Measure performance
        start_time = time.time()
        result = await video_service.analyze_video_tutorial(request_data)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Verify successful analysis
        assert_success_response(result)
        
        # Verify performance (should be fast for short video)
        assert analysis_time < 3.0, f"Analysis took {analysis_time}s, expected < 3s for short video"
        
        # Verify that optimization flags were respected
        analysis = result["analysis"]
        assert "patterns" not in analysis.get("learning_patterns", {}) or \
               len(analysis.get("learning_patterns", {}).get("patterns", [])) == 0