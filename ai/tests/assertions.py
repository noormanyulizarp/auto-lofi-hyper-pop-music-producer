# Test Assertions and Validation
import json
import re
from typing import Dict, Any, List, Union, Optional
from datetime import datetime, timedelta
import pytest
import numpy as np

class ResponseAssertions:
    """Assertions for API response validation."""
    
    @staticmethod
    def assert_success_response(response: Dict[str, Any], expected_keys: List[str] = None):
        """Assert that response indicates success and optionally contains expected keys."""
        assert response.get("success") is True, f"Expected success response, got: {response}"
        
        if expected_keys:
            for key in expected_keys:
                assert key in response, f"Expected key '{key}' not found in response"
    
    @staticmethod
    def assert_error_response(response: Dict[str, Any], expected_status_code: int = None):
        """Assert that response indicates an error."""
        assert response.get("success") is False, f"Expected error response, got: {response}"
        
        error_info = response.get("error", {})
        if expected_status_code:
            assert error_info.get("status_code") == expected_status_code, \
                f"Expected status code {expected_status_code}, got: {error_info.get('status_code')}"
    
    @staticmethod
    def assert_response_has_structure(response: Dict[str, Any], structure_template: Dict[str, Any]):
        """Assert that response matches the expected structure template."""
        ResponseAssertions._validate_structure(response, structure_template)
    
    @staticmethod
    def _validate_structure(data: Any, template: Any, path: str = ""):
        """Recursively validate data structure against template."""
        if isinstance(template, type):
            assert isinstance(data, template), \
                f"Expected type {template} at {path}, got {type(data)}"
        
        elif isinstance(template, dict):
            assert isinstance(data, dict), f"Expected dict at {path}, got {type(data)}"
            
            for key, value_template in template.items():
                assert key in data, f"Missing key '{key}' at {path}"
                ResponseAssertions._validate_structure(
                    data[key], value_template, f"{path}.{key}" if path else key
                )
        
        elif isinstance(template, list):
            assert isinstance(data, list), f"Expected list at {path}, got {type(data)}"
            if template:  # If template list is not empty, validate first element
                if data:  # If data list is not empty
                    ResponseAssertions._validate_structure(data[0], template[0], f"{path}[0]")

class MusicAssertions:
    """Assertions specific to music-related responses."""
    
    @staticmethod
    def assert_valid_music_concepts(concepts: Dict[str, Any]):
        """Assert that music concepts structure is valid."""
        required_keys = ["rhythm", "melody", "harmony", "structure"]
        ResponseAssertions.assert_response_has_structure(concepts, {key: list for key in required_keys})
        
        # Validate that each concept category has at least one item
        for key in required_keys:
            assert len(concepts[key]) > 0, f"Concept category '{key}' cannot be empty"
    
    @staticmethod
    def assert_valid_audio_features(features: Dict[str, Any]):
        """Assert that audio features structure is valid."""
        required_sections = ["rhythm", "melody", "harmony", "timbre", "structure", "metadata"]
        ResponseAssertions.assert_response_has_structure(features, {key: dict for key in required_sections})
        
        # Validate numeric ranges
        rhythm = features["rhythm"]
        assert 20.0 <= rhythm["tempo"] <= 200.0, f"Invalid tempo: {rhythm['tempo']}"
        assert 0.0 <= rhythm["beat_strength"] <= 1.0, f"Invalid beat strength: {rhythm['beat_strength']}"
        assert 0.0 <= rhythm["rhythm_complexity"] <= 1.0, f"Invalid rhythm complexity: {rhythm['rhythm_complexity']}"
        assert 0.0 <= rhythm["syncopation"] <= 1.0, f"Invalid syncopation: {rhythm['syncopation']}"
        
        # Validate pitch class histogram
        melody = features["melody"]
        pitch_hist = melody["pitch_class_histogram"]
        assert len(pitch_hist) == 12, f"Pitch class histogram must have 12 values, got {len(pitch_hist)}"
        assert abs(sum(pitch_hist) - 1.0) < 0.01, f"Pitch class histogram must sum to 1.0, got {sum(pitch_hist)}"
    
    @staticmethod
    def assert_valid_generation_parameters(params: Dict[str, Any]):
        """Assert that generation parameters are valid."""
        required_keys = ["tempo", "key", "instrumentation", "duration_structure"]
        ResponseAssertions.assert_response_has_structure(params, {key: ... for key in required_keys})
        
        # Validate tempo
        assert 40 <= params["tempo"] <= 200, f"Invalid tempo: {params['tempo']}"
        
        # Validate key format
        key_pattern = r'^[A-G][#b]?\s+(Major|Minor|maj|min|M|m)$'
        assert re.match(key_pattern, params["key"]), f"Invalid key format: {params['key']}"
        
        # Validate instrumentation
        assert isinstance(params["instrumentation"], list), f"Instrumentation must be a list"
        assert len(params["instrumentation"]) > 0, f"Instrumentation cannot be empty"
        
        # Validate duration structure
        duration_struct = params["duration_structure"]
        assert isinstance(duration_struct, dict), f"Duration structure must be a dict"
        assert all(value > 0 for value in duration_struct.values()), f"All duration values must be positive"

class VideoAssertions:
    """Assertions specific to video-related responses."""
    
    @staticmethod
    def assert_valid_video_analysis(analysis: Dict[str, Any]):
        """Assert that video analysis structure is valid."""
        required_sections = ["video_info", "audio_analysis", "musical_elements", "learning_patterns"]
        ResponseAssertions.assert_response_has_structure(analysis, {key: dict for key in required_sections})
        
        # Validate video info
        video_info = analysis["video_info"]
        assert video_info["duration"] > 0, f"Video duration must be positive: {video_info['duration']}"
        assert video_info["width"] > 0, f"Video width must be positive: {video_info['width']}"
        assert video_info["height"] > 0, f"Video height must be positive: {video_info['height']}"
        assert video_info["fps"] > 0, f"Video fps must be positive: {video_info['fps']}"
        
        # Validate musical elements
        musical_elements = analysis["musical_elements"]
        for element_type in ["rhythm", "melody", "harmony"]:
            assert element_type in musical_elements, f"Missing musical element: {element_type}"
        
        # Validate learning patterns
        learning_patterns = analysis["learning_patterns"]
        assert "techniques" in learning_patterns, f"Missing techniques in learning patterns"
        assert "exercises" in learning_patterns, f"Missing exercises in learning patterns"
    
    @staticmethod
    def assert_valid_learning_techniques(techniques: List[Dict[str, Any]]):
        """Assert that learning techniques are valid."""
        for technique in techniques:
            required_keys = ["name", "description", "confidence", "timestamp"]
            ResponseAssertions.assert_response_has_structure(technique, {key: ... for key in required_keys})
            
            assert 0.0 <= technique["confidence"] <= 1.0, \
                f"Invalid confidence value: {technique['confidence']}"
            
            assert len(technique["timestamp"]) == 2, \
                f"Timestamp must have 2 values: {technique['timestamp']}"
            
            start, end = technique["timestamp"]
            assert start <= end, f"Start time must be <= end time: {start} > {end}"
    
    @staticmethod
    def assert_valid_exercises(exercises: List[Dict[str, Any]]):
        """Assert that exercises are valid."""
        for exercise in exercises:
            required_keys = ["title", "instructions", "duration", "difficulty"]
            ResponseAssertions.assert_response_has_structure(exercise, {key: ... for key in required_keys})
            
            assert exercise["duration"] > 0, f"Exercise duration must be positive: {exercise['duration']}"
            
            assert exercise["difficulty"] in ["beginner", "intermediate", "advanced"], \
                f"Invalid difficulty level: {exercise['difficulty']}"

class ProviderAssertions:
    """Assertions specific to provider service responses."""
    
    @staticmethod
    def assert_valid_provider_status(status: Dict[str, Any]):
        """Assert that provider status is valid."""
        assert "providers" in status, f"Missing providers in status"
        assert "total_providers" in status, f"Missing total_providers in status"
        assert "available_providers" in status, f"Missing available_providers in status"
        
        # Validate each provider
        for provider_name, provider_info in status["providers"].items():
            assert "status" in provider_info, f"Missing status for provider {provider_name}"
            assert "models" in provider_info, f"Missing models for provider {provider_name}"
            assert "latency" in provider_info, f"Missing latency for provider {provider_name}"
            assert "success_rate" in provider_info, f"Missing success_rate for provider {provider_name}"
            
            # Validate numeric values
            assert provider_info["latency"] >= 0, f"Invalid latency for {provider_name}: {provider_info['latency']}"
            assert 0.0 <= provider_info["success_rate"] <= 1.0, \
                f"Invalid success rate for {provider_name}: {provider_info['success_rate']}"
    
    @staticmethod
    def assert_valid_routing_response(response: Dict[str, Any]):
        """Assert that provider routing response is valid."""
        required_keys = ["success", "provider", "model", "response", "latency", "tokens_used"]
        ResponseAssertions.assert_response_has_structure(response, {key: ... for key in required_keys})
        
        assert response["latency"] >= 0, f"Invalid latency: {response['latency']}"
        assert response["tokens_used"] > 0, f"Invalid tokens used: {response['tokens_used']}"

class HeartMuLaAssertions:
    """Assertions specific to HeartMuLa service responses."""
    
    @staticmethod
    def assert_valid_generation_response(response: Dict[str, Any]):
        """Assert that HeartMuLa generation response is valid."""
        required_keys = ["success", "task_id", "status", "estimated_time"]
        ResponseAssertions.assert_response_has_structure(response, {key: ... for key in required_keys})
        
        assert response["estimated_time"] > 0, f"Invalid estimated time: {response['estimated_time']}"
        assert response["status"] in ["processing", "queued", "completed", "failed"], \
            f"Invalid status: {response['status']}"
    
    @staticmethod
    def assert_valid_status_response(response: Dict[str, Any]):
        """Assert that HeartMuLa status response is valid."""
        required_keys = ["success", "task_id", "status", "progress"]
        ResponseAssertions.assert_response_has_structure(response, {key: ... for key in required_keys})
        
        assert 0 <= response["progress"] <= 100, f"Invalid progress: {response['progress']}"
        
        if response["status"] == "completed":
            assert "result_url" in response, f"Missing result_url for completed task"
            assert "metadata" in response, f"Missing metadata for completed task"
    
    @staticmethod
    def assert_valid_music_details(details: Dict[str, Any]):
        """Assert that HeartMuLa music details are valid."""
        required_keys = ["success", "music_id", "title", "artist", "genre", "mood", "duration"]
        ResponseAssertions.assert_response_has_structure(details, {key: ... for key in required_keys})
        
        assert details["duration"] > 0, f"Invalid duration: {details['duration']}"
        assert "audio_url" in details, f"Missing audio_url in music details"
        
        if "metadata" in details:
            metadata = details["metadata"]
            assert "bpm" in metadata, f"Missing bpm in metadata"
            assert "key" in metadata, f"Missing key in metadata"
            assert metadata["bpm"] > 0, f"Invalid bpm: {metadata['bpm']}"

class AudioDataAssertions:
    """Assertions for audio data validation."""
    
    @staticmethod
    def assert_valid_audio_data(audio_data: np.ndarray, sample_rate: int = 22050):
        """Assert that audio data is valid."""
        assert isinstance(audio_data, np.ndarray), f"Audio data must be numpy array, got {type(audio_data)}"
        assert audio_data.ndim == 1, f"Audio data must be 1-dimensional, got {audio_data.ndim} dimensions"
        assert len(audio_data) > 0, f"Audio data cannot be empty"
        assert sample_rate > 0, f"Sample rate must be positive: {sample_rate}"
        
        # Check that audio values are within reasonable range (-1 to 1)
        max_abs_value = np.max(np.abs(audio_data))
        assert max_abs_value <= 1.0, f"Audio values exceed [-1, 1] range: max abs value = {max_abs_value}"
    
    @staticmethod
    def assert_valid_spectrogram(spectrogram: np.ndarray):
        """Assert that spectrogram data is valid."""
        assert isinstance(spectrogram, np.ndarray), f"Spectrogram must be numpy array, got {type(spectrogram)}"
        assert spectrogram.ndim == 2, f"Spectrogram must be 2-dimensional, got {spectrogram.ndim} dimensions"
        assert spectrogram.shape[0] > 0 and spectrogram.shape[1] > 0, f"Spectrogram cannot be empty"
        assert np.all(spectrogram >= 0), f"Spectrogram values must be non-negative"

class VideoDataAssertions:
    """Assertions for video data validation."""
    
    @staticmethod
    def assert_valid_video_frames(frames: List[np.ndarray]):
        """Assert that video frames are valid."""
        assert len(frames) > 0, f"Video frames list cannot be empty"
        
        for i, frame in enumerate(frames):
            assert isinstance(frame, np.ndarray), f"Frame {i} must be numpy array, got {type(frame)}"
            assert frame.ndim == 3, f"Frame {i} must be 3-dimensional (H, W, C), got {frame.ndim} dimensions"
            assert frame.shape[2] == 3, f"Frame {i} must have 3 channels (RGB), got {frame.shape[2]} channels"
            assert frame.shape[0] > 0 and frame.shape[1] > 0, f"Frame {i} cannot be empty"
            assert np.all((frame >= 0) & (frame <= 255)), f"Frame {i} values must be in [0, 255] range"
    
    @staticmethod
    def assert_consistent_frame_dimensions(frames: List[np.ndarray]):
        """Assert that all video frames have consistent dimensions."""
        if not frames:
            return
        
        reference_shape = frames[0].shape
        for i, frame in enumerate(frames[1:], 1):
            assert frame.shape == reference_shape, \
                f"Frame {i} dimensions {frame.shape} don't match reference {reference_shape}"

class PerformanceAssertions:
    """Assertions for performance-related validation."""
    
    @staticmethod
    def assert_response_time(response_time: float, max_allowed: float):
        """Assert that response time is within acceptable limits."""
        assert response_time >= 0, f"Response time cannot be negative: {response_time}"
        assert response_time <= max_allowed, \
            f"Response time {response_time}s exceeds maximum allowed {max_allowed}s"
    
    @staticmethod
    def assert_memory_usage(memory_mb: float, max_allowed_mb: float):
        """Assert that memory usage is within acceptable limits."""
        assert memory_mb >= 0, f"Memory usage cannot be negative: {memory_mb}"
        assert memory_mb <= max_allowed_mb, \
            f"Memory usage {memory_mb}MB exceeds maximum allowed {max_allowed_mb}MB"
    
    @staticmethod
    def assert_success_rate(success_rate: float, min_required: float):
        """Assert that success rate meets minimum requirements."""
        assert 0.0 <= success_rate <= 1.0, f"Success rate must be between 0 and 1: {success_rate}"
        assert success_rate >= min_required, \
            f"Success rate {success_rate} below minimum required {min_required}"

class ErrorAssertions:
    """Assertions for error response validation."""
    
    @staticmethod
    def assert_error_structure(error_response: Dict[str, Any]):
        """Assert that error response has proper structure."""
        assert "success" in error_response, f"Missing 'success' field in error response"
        assert error_response["success"] is False, f"Error response should have success=False"
        assert "error" in error_response, f"Missing 'error' field in error response"
        
        error_info = error_response["error"]
        required_error_keys = ["type", "message", "status_code"]
        ResponseAssertions.assert_response_has_structure(error_info, {key: ... for key in required_error_keys})
        
        assert error_info["status_code"] in [400, 401, 403, 404, 429, 500, 503], \
            f"Invalid error status code: {error_info['status_code']}"
    
    @staticmethod
    def assert_specific_error(error_response: Dict[str, Any], expected_error_type: str):
        """Assert that error response matches specific error type."""
        ErrorAssertions.assert_error_structure(error_response)
        assert error_response["error"]["type"] == expected_error_type, \
            f"Expected error type '{expected_error_type}', got: {error_response['error']['type']}"

class UtilityAssertions:
    """General utility assertions."""
    
    @staticmethod
    def assert_timestamp_format(timestamp: str):
        """Assert that timestamp has valid ISO format."""
        try:
            # Try to parse the timestamp
            parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            assert parsed.tzinfo is not None, f"Timestamp must include timezone info: {timestamp}"
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp}")
    
    @staticmethod
    def assert_timestamp_recent(timestamp: str, max_age_seconds: int = 60):
        """Assert that timestamp is recent (within max_age_seconds)."""
        UtilityAssertions.assert_timestamp_format(timestamp)
        
        parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(parsed_time.tzinfo)
        age = (now - parsed_time).total_seconds()
        
        assert age <= max_age_seconds, \
            f"Timestamp {timestamp} is too old (age: {age}s, max allowed: {max_age_seconds}s)"
    
    @staticmethod
    def assert_valid_uuid(uuid_string: str):
        """Assert that string is a valid UUID."""
        import uuid
        try:
            uuid.UUID(uuid_string)
        except ValueError:
            pytest.fail(f"Invalid UUID format: {uuid_string}")
    
    @staticmethod
    def assert_valid_url(url: str):
        """Assert that string is a valid URL."""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            assert all([result.scheme, result.netloc]), f"Invalid URL: {url}"
        except Exception as e:
            pytest.fail(f"Invalid URL format '{url}': {str(e)}")
    
    @staticmethod
    def assert_valid_email(email: str):
        """Assert that string is a valid email address."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert re.match(email_pattern, email), f"Invalid email format: {email}"
    
    @staticmethod
    def assert_file_exists(file_path: str):
        """Assert that file exists."""
        import os
        assert os.path.exists(file_path), f"File does not exist: {file_path}"
        assert os.path.isfile(file_path), f"Path is not a file: {file_path}"
    
    @staticmethod
    def assert_directory_exists(dir_path: str):
        """Assert that directory exists."""
        import os
        assert os.path.exists(dir_path), f"Directory does not exist: {dir_path}"
        assert os.path.isdir(dir_path), f"Path is not a directory: {dir_path}"
    
    @staticmethod
    def assert_file_content(file_path: str, expected_content: str, encoding: str = 'utf-8'):
        """Assert that file contains expected content."""
        UtilityAssertions.assert_file_exists(file_path)
        
        with open(file_path, 'r', encoding=encoding) as file:
            actual_content = file.read()
        
        assert actual_content == expected_content, \
            f"File content mismatch. Expected: {expected_content}, Actual: {actual_content}"

class NumericAssertions:
    """Assertions for numeric value validation."""
    
    @staticmethod
    def assert_approximately_equal(actual: float, expected: float, tolerance: float = 0.001, message: str = None):
        """Assert that two float values are approximately equal within tolerance."""
        diff = abs(actual - expected)
        assert diff <= tolerance, message or f"Values {actual} and {expected} differ by {diff}, which is more than tolerance {tolerance}"
    
    @staticmethod
    def assert_in_range(value: float, min_val: float, max_val: float, inclusive: bool = True):
        """Assert that value is within specified range."""
        if inclusive:
            assert min_val <= value <= max_val, f"Value {value} not in range [{min_val}, {max_val}]"
        else:
            assert min_val < value < max_val, f"Value {value} not in range ({min_val}, {max_val})"
    
    @staticmethod
    def assert_positive(value: Union[int, float], zero_allowed: bool = False):
        """Assert that value is positive."""
        if zero_allowed:
            assert value >= 0, f"Value {value} is not positive (zero allowed)"
        else:
            assert value > 0, f"Value {value} is not positive"
    
    @staticmethod
    def assert_percentage(value: float, allow_zero: bool = True, allow_negative: bool = False):
        """Assert that value is a valid percentage."""
        assert 0.0 <= value <= 100.0, f"Value {value} is not a valid percentage"
        
        if not allow_zero and value == 0.0:
            pytest.fail(f"Zero percentage not allowed: {value}")
        
        if not allow_negative and value < 0.0:
            pytest.fail(f"Negative percentage not allowed: {value}")

class CollectionAssertions:
    """Assertions for collection validation."""
    
    @staticmethod
    def assert_not_empty(collection):
        """Assert that collection is not empty."""
        assert len(collection) > 0, f"Collection is empty"
    
    @staticmethod
    def assert_has_length(collection, expected_length: int):
        """Assert that collection has expected length."""
        assert len(collection) == expected_length, \
            f"Collection length {len(collection)} != expected {expected_length}"
    
    @staticmethod
    def assert_contains_all(collection, items: list):
        """Assert that collection contains all specified items."""
        for item in items:
            assert item in collection, f"Item {item} not found in collection"
    
    @staticmethod
    def assert_contains_none(collection, items: list):
        """Assert that collection contains none of the specified items."""
        for item in items:
            assert item not in collection, f"Item {item} unexpectedly found in collection"
    
    @staticmethod
    def assert_unique_items(collection):
        """Assert that all items in collection are unique."""
        assert len(collection) == len(set(collection)), \
            f"Collection contains duplicate items: {collection}"

# Convenience functions for common assertions
def assert_success_response(response: Dict[str, Any], expected_keys: List[str] = None):
    """Convenience function for success response assertion."""
    ResponseAssertions.assert_success_response(response, expected_keys)

def assert_error_response(response: Dict[str, Any], expected_status_code: int = None):
    """Convenience function for error response assertion."""
    ResponseAssertions.assert_error_response(response, expected_status_code)

def assert_valid_music_concepts(concepts: Dict[str, Any]):
    """Convenience function for music concepts assertion."""
    MusicAssertions.assert_valid_music_concepts(concepts)

def assert_valid_audio_features(features: Dict[str, Any]):
    """Convenience function for audio features assertion."""
    MusicAssertions.assert_valid_audio_features(features)

def assert_valid_video_analysis(analysis: Dict[str, Any]):
    """Convenience function for video analysis assertion."""
    VideoAssertions.assert_valid_video_analysis(analysis)

def assert_approximately_equal(actual: float, expected: float, tolerance: float = 0.001):
    """Convenience function for approximate equality assertion."""
    NumericAssertions.assert_approximately_equal(actual, expected, tolerance)