# Test Helpers and Utilities
import asyncio
import json
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pytest
import numpy as np
import aiofiles

# Logging and monitoring
from loguru import logger

# HTTP Testing
import httpx
import respx

# Async Utilities
async def async_test_wrapper(test_func, *args, **kwargs):
    """Wrapper to run async test functions with proper error handling."""
    try:
        result = await test_func(*args, **kwargs)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Async test failed: {str(e)}")
        return {"success": False, "error": str(e), "exception": e}

def run_async_test(test_func, *args, **kwargs):
    """Run an async test function and return the result."""
    return asyncio.run(async_test_wrapper(test_func, *args, **kwargs))

# Response Validation
def validate_success_response(response: Dict[str, Any], expected_keys: List[str] = None):
    """Validate that a response indicates success and contains expected keys."""
    assert response.get("success") is True, f"Expected success, got: {response}"
    
    if expected_keys:
        for key in expected_keys:
            assert key in response, f"Expected key '{key}' not found in response"

def validate_error_response(response: Dict[str, Any], expected_error_type: str = None):
    """Validate that a response indicates an error."""
    assert response.get("success") is False, f"Expected error, got: {response}"
    
    if expected_error_type:
        error_info = response.get("error", {})
        assert error_info.get("type") == expected_error_type, \
            f"Expected error type '{expected_error_type}', got: {error_info.get('type')}"

def validate_structure(data: Dict[str, Any], structure_template: Dict[str, Any]):
    """Validate that data matches the expected structure template."""
    for key, expected_type in structure_template.items():
        assert key in data, f"Expected key '{key}' not found in data"
        
        actual_value = data[key]
        if isinstance(expected_type, type):
            assert isinstance(actual_value, expected_type), \
                f"Key '{key}' expected type {expected_type}, got {type(actual_value)}"
        elif isinstance(expected_type, dict):
            assert isinstance(actual_value, dict), \
                f"Key '{key}' expected dict, got {type(actual_value)}"
            validate_structure(actual_value, expected_type)
        elif isinstance(expected_type, list):
            assert isinstance(actual_value, list), \
                f"Key '{key}' expected list, got {type(actual_value)}"

# Data Comparison
def assert_dicts_equal(dict1: Dict[str, Any], dict2: Dict[str, Any], exclude_keys: List[str] = None):
    """Assert that two dictionaries are equal, excluding specified keys."""
    if exclude_keys is None:
        exclude_keys = []
    
    dict1_filtered = {k: v for k, v in dict1.items() if k not in exclude_keys}
    dict2_filtered = {k: v for k, v in dict2.items() if k not in exclude_keys}
    
    assert dict1_filtered == dict2_filtered, f"Dictionaries are not equal: {dict1_filtered} != {dict2_filtered}"

def assert_lists_equal(list1: List[Any], list2: List[Any], order_matters: bool = False):
    """Assert that two lists contain the same elements."""
    if order_matters:
        assert list1 == list2, f"Lists are not equal (order matters): {list1} != {list2}"
    else:
        assert sorted(list1) == sorted(list2), f"Lists are not equal (order doesn't matter): {list1} != {list2}"

def assert_contained_in(needle: Any, haystack: Union[List, Dict, str], message: str = None):
    """Assert that needle is contained in haystack."""
    if isinstance(haystack, (list, tuple)):
        assert needle in haystack, message or f"{needle} not found in {haystack}"
    elif isinstance(haystack, dict):
        assert needle in haystack, message or f"Key {needle} not found in dict"
    elif isinstance(haystack, str):
        assert needle in haystack, message or f"'{needle}' not found in '{haystack}'"
    else:
        raise TypeError(f"Unsupported haystack type: {type(haystack)}")

# File and Path Utilities
def create_temp_file(content: Union[str, bytes] = b"test content", suffix: str = ".tmp") -> Path:
    """Create a temporary file with given content and return its path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        if isinstance(content, str):
            content = content.encode('utf-8')
        temp_file.write(content)
        return Path(temp_file.name)

def create_temp_directory() -> Path:
    """Create a temporary directory and return its path."""
    temp_dir = tempfile.mkdtemp()
    return Path(temp_dir)

def cleanup_temp_file(file_path: Union[str, Path]):
    """Clean up a temporary file."""
    try:
        os.unlink(str(file_path))
    except (OSError, FileNotFoundError):
        pass  # File might already be deleted

def cleanup_temp_directory(dir_path: Union[str, Path]):
    """Clean up a temporary directory and its contents."""
    import shutil
    try:
        shutil.rmtree(str(dir_path), ignore_errors=True)
    except (OSError, FileNotFoundError):
        pass  # Directory might already be deleted

async def read_file_async(file_path: Union[str, Path]) -> bytes:
    """Read file content asynchronously."""
    async with aiofiles.open(str(file_path), 'rb') as file:
        return await file.read()

# Time Utilities
def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()

def get_timestamp_seconds_ago(seconds: int) -> str:
    """Get timestamp from specified seconds ago."""
    return (datetime.now() - timedelta(seconds=seconds)).isoformat()

def measure_execution_time(func, *args, **kwargs):
    """Measure execution time of a function."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time

class Timer:
    """Context manager for timing code execution."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"{self.name} took {duration:.4f} seconds")
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

# HTTP Testing Utilities
def create_test_client(app, **kwargs):
    """Create a test client for FastAPI application."""
    from fastapi.testclient import TestClient
    return TestClient(app, **kwargs)

def mock_http_response(status_code: int = 200, json_data: Dict = None, text: str = None):
    """Create a mock HTTP response."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    mock_response.text = text or ""
    mock_response.content = (text or "").encode('utf-8')
    return mock_response

async def make_async_request(client, method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make an asynchronous HTTP request."""
    async with client.stream(method, url, **kwargs) as response:
        content = await response.json()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": content
        }

# Database Testing Utilities
class DatabaseTestHelper:
    """Helper for database testing operations."""
    
    def __init__(self, session):
        self.session = session
    
    def create_test_record(self, model_class, **kwargs):
        """Create a test record in the database."""
        record = model_class(**kwargs)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
    
    def get_test_record(self, model_class, record_id: int):
        """Get a test record by ID."""
        return self.session.query(model_class).filter(model_class.id == record_id).first()
    
    def delete_test_record(self, model_class, record_id: int):
        """Delete a test record by ID."""
        record = self.get_test_record(model_class, record_id)
        if record:
            self.session.delete(record)
            self.session.commit()
    
    def count_records(self, model_class):
        """Count records of a specific model."""
        return self.session.query(model_class).count()
    
    def clear_table(self, model_class):
        """Clear all records from a table."""
        self.session.query(model_class).delete()
        self.session.commit()

# Redis Testing Utilities
class RedisTestHelper:
    """Helper for Redis testing operations."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def set_test_data(self, key: str, value: Any, expire: int = 3600):
        """Set test data in Redis."""
        serialized_value = json.dumps(value, default=str)
        return self.redis.set(key, serialized_value, ex=expire)
    
    def get_test_data(self, key: str):
        """Get test data from Redis."""
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    def delete_test_data(self, key: str):
        """Delete test data from Redis."""
        return self.redis.delete(key)
    
    def clear_test_data(self, pattern: str = "test:*"):
        """Clear test data from Redis using pattern."""
        keys = self.redis.keys(pattern)
        if keys:
            return self.redis.delete(*keys)
        return 0

# Audio/Video Testing Utilities
def create_dummy_audio_file(duration: float = 1.0, sample_rate: int = 22050) -> np.ndarray:
    """Create a dummy audio file for testing."""
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440  # A4 note
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Add some noise
    noise = np.random.normal(0, 0.01, audio_data.shape)
    audio_data += noise
    
    # Normalize
    audio_data = np.clip(audio_data, -1, 1)
    
    return audio_data

def create_dummy_video_frames(width: int = 640, height: int = 480, frames: int = 10) -> List[np.ndarray]:
    """Create dummy video frames for testing."""
    video_frames = []
    
    for i in range(frames):
        # Create gradient frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add horizontal gradient
        for x in range(width):
            color_value = int((x / width) * 255)
            frame[:, x, 0] = color_value  # Red channel
        
        # Add vertical gradient
        for y in range(height):
            color_value = int((y / height) * 255)
            frame[y, :, 1] = color_value  # Green channel
        
        # Add some variation per frame
        frame[:, :, 2] = (i * 25) % 255  # Blue channel
        
        video_frames.append(frame)
    
    return video_frames

# Performance Testing Utilities
class PerformanceMonitor:
    """Monitor performance metrics during testing."""
    
    def __init__(self):
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "duration": None,
            "memory_usage": [],
            "cpu_usage": [],
            "request_count": 0,
            "error_count": 0
        }
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.metrics["start_time"] = time.time()
    
    def record_request(self, success: bool = True):
        """Record a request."""
        self.metrics["request_count"] += 1
        if not success:
            self.metrics["error_count"] += 1
    
    def record_memory_usage(self):
        """Record current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            self.metrics["memory_usage"].append(memory_info.rss / 1024 / 1024)  # MB
        except ImportError:
            pass  # psutil not available
    
    def record_cpu_usage(self):
        """Record current CPU usage."""
        try:
            import psutil
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            self.metrics["cpu_usage"].append(cpu_percent)
        except ImportError:
            pass  # psutil not available
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.metrics["end_time"] = time.time()
        if self.metrics["start_time"]:
            self.metrics["duration"] = self.metrics["end_time"] - self.metrics["start_time"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        summary = {
            "total_requests": self.metrics["request_count"],
            "error_count": self.metrics["error_count"],
            "success_rate": (self.metrics["request_count"] - self.metrics["error_count"]) / max(self.metrics["request_count"], 1),
            "duration_seconds": self.metrics["duration"],
        }
        
        if self.metrics["memory_usage"]:
            summary["avg_memory_mb"] = sum(self.metrics["memory_usage"]) / len(self.metrics["memory_usage"])
            summary["max_memory_mb"] = max(self.metrics["memory_usage"])
        
        if self.metrics["cpu_usage"]:
            summary["avg_cpu_percent"] = sum(self.metrics["cpu_usage"]) / len(self.metrics["cpu_usage"])
            summary["max_cpu_percent"] = max(self.metrics["cpu_usage"])
        
        return summary

# Stress Testing Utilities
class LoadTestScenario:
    """Define a load testing scenario."""
    
    def __init__(self, name: str, concurrent_users: int, duration: int, requests_per_user: int):
        self.name = name
        self.concurrent_users = concurrent_users
        self.duration = duration
        self.requests_per_user = requests_per_user
        self.results = []
    
    async def run_scenario(self, test_func, *args, **kwargs):
        """Run the load test scenario."""
        import asyncio
        
        async def user_task():
            user_results = []
            for _ in range(self.requests_per_user):
                try:
                    result = await test_func(*args, **kwargs)
                    user_results.append(result)
                except Exception as e:
                    user_results.append({"error": str(e)})
                await asyncio.sleep(0.1)  # Small delay between requests
            return user_results
        
        # Run concurrent user tasks
        tasks = [user_task() for _ in range(self.concurrent_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for user_result in results:
            if isinstance(user_result, Exception):
                self.results.append({"error": str(user_result)})
            else:
                self.results.extend(user_result)
        
        return self.get_summary()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get load test summary."""
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if "error" not in r])
        failed_requests = total_requests - successful_requests
        
        return {
            "scenario": self.name,
            "concurrent_users": self.concurrent_users,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "requests_per_second": total_requests / self.duration if self.duration > 0 else 0
        }

# Async Context Managers
class AsyncTempFile:
    """Async context manager for temporary file handling."""
    
    def __init__(self, content: Union[str, bytes] = b"test content", suffix: str = ".tmp"):
        self.content = content
        self.suffix = suffix
        self.file_path = None
    
    async def __aenter__(self):
        self.file_path = create_temp_file(self.content, self.suffix)
        return self.file_path
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.file_path:
            cleanup_temp_file(self.file_path)

class AsyncTempDirectory:
    """Async context manager for temporary directory handling."""
    
    def __init__(self):
        self.dir_path = None
    
    async def __aenter__(self):
        self.dir_path = create_temp_directory()
        return self.dir_path
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.dir_path:
            cleanup_temp_directory(self.dir_path)

# Test Data Builders
class TestDataBuilder:
    """Builder for creating complex test data structures."""
    
    def __init__(self):
        self.data = {}
    
    def with_field(self, key: str, value: Any):
        """Add a field to the test data."""
        self.data[key] = value
        return self
    
    def with_nested_field(self, parent_key: str, key: str, value: Any):
        """Add a nested field to the test data."""
        if parent_key not in self.data:
            self.data[parent_key] = {}
        self.data[parent_key][key] = value
        return self
    
    def with_list_field(self, key: str, values: List[Any]):
        """Add a list field to the test data."""
        self.data[key] = values
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the test data."""
        return self.data.copy()

# Assertion Helpers
class ExtendedAssertions:
    """Extended assertion utilities for testing."""
    
    @staticmethod
    def assert_approximately_equal(actual: float, expected: float, tolerance: float = 0.001, message: str = None):
        """Assert that two float values are approximately equal within tolerance."""
        diff = abs(actual - expected)
        assert diff <= tolerance, message or f"Values {actual} and {expected} differ by {diff}, which is more than tolerance {tolerance}"
    
    @staticmethod
    def assert_timestamp_recent(timestamp: str, max_age_seconds: int = 60):
        """Assert that a timestamp is recent (within max_age_seconds)."""
        try:
            timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(timestamp_dt.tzinfo)
            age = (now - timestamp_dt).total_seconds()
            assert age <= max_age_seconds, f"Timestamp {timestamp} is too old (age: {age}s, max allowed: {max_age_seconds}s)"
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp}")
    
    @staticmethod
    def assert_valid_uuid(uuid_string: str):
        """Assert that a string is a valid UUID."""
        import uuid
        try:
            uuid.UUID(uuid_string)
        except ValueError:
            pytest.fail(f"Invalid UUID format: {uuid_string}")
    
    @staticmethod
    def assert_valid_email(email: str):
        """Assert that a string is a valid email address."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert re.match(email_pattern, email), f"Invalid email format: {email}"
    
    @staticmethod
    def assert_valid_url(url: str):
        """Assert that a string is a valid URL."""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            assert all([result.scheme, result.netloc]), f"Invalid URL: {url}"
        except Exception:
            pytest.fail(f"Invalid URL format: {url}")

# Test Environment Utilities
class TestEnvironment:
    """Manage test environment setup and teardown."""
    
    def __init__(self):
        self.temp_files = []
        self.temp_directories = []
        self.env_vars = {}
    
    def add_temp_file(self, content: Union[str, bytes] = b"test content", suffix: str = ".tmp") -> Path:
        """Add a temporary file to be cleaned up."""
        file_path = create_temp_file(content, suffix)
        self.temp_files.append(file_path)
        return file_path
    
    def add_temp_directory(self) -> Path:
        """Add a temporary directory to be cleaned up."""
        dir_path = create_temp_directory()
        self.temp_directories.append(dir_path)
        return dir_path
    
    def set_env_var(self, key: str, value: str):
        """Set an environment variable for testing."""
        original_value = os.environ.get(key)
        self.env_vars[key] = original_value
        os.environ[key] = value
    
    def cleanup(self):
        """Clean up all temporary files, directories, and environment variables."""
        # Clean up temporary files
        for file_path in self.temp_files:
            cleanup_temp_file(file_path)
        
        # Clean up temporary directories
        for dir_path in self.temp_directories:
            cleanup_temp_directory(dir_path)
        
        # Restore environment variables
        for key, original_value in self.env_vars.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()