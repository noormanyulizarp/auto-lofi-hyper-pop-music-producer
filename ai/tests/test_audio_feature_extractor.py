# Unit Tests for Audio Feature Extractor Service
import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from tests.fixtures import (
    mock_audio_feature_extractor,
    test_audio_file,
    sample_audio_data
)
from tests.mocks import MockLibrosaLoader, mock_librosa
from tests.assertions import (
    assert_success_response,
    assert_error_response,
    assert_valid_audio_features,
    assert_approximately_equal
)

# Import the service class
from ai.services.audio_feature_extractor import AudioFeatureExtractor


class TestAudioFeatureExtractor:
    """Test suite for Audio Feature Extractor Service."""
    
    @pytest.fixture
    def audio_extractor(self, mock_librosa_loader):
        """Create an Audio Feature Extractor instance with mocked dependencies."""
        with mock_librosa():
            extractor = AudioFeatureExtractor()
            extractor.librosa = mock_librosa_loader
            return extractor
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_comprehensive_features_success(self, audio_extractor, sample_audio_data):
        """Test successful comprehensive feature extraction."""
        # Mock librosa.load to return sample data
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_comprehensive_features(test_audio_file)
        
        assert_success_response(result)
        assert "features" in result
        assert "metadata" in result
        
        # Validate features structure
        assert_valid_audio_features(result["features"])
        
        # Validate metadata
        metadata = result["metadata"]
        assert metadata["duration"] == sample_audio_data["duration"]
        assert metadata["sample_rate"] == sample_audio_data["sample_rate"]
        assert metadata["channels"] in [1, 2]
        assert metadata["bit_depth"] in [16, 24, 32]
        
        # Verify librosa.load was called
        audio_extractor.librosa.load.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_comprehensive_features_invalid_file(self, audio_extractor):
        """Test comprehensive feature extraction with invalid file."""
        # Mock librosa.load to raise an exception
        audio_extractor.librosa.load.side_effect = Exception("File not found")
        
        result = await audio_extractor.extract_comprehensive_features("/nonexistent/file.mp3")
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 404
        assert "File not found" in result["error"]["message"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_rhythm_features_success(self, audio_extractor, sample_audio_data):
        """Test successful rhythm feature extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_rhythm_features(test_audio_file)
        
        assert_success_response(result)
        
        # Validate rhythm features
        assert "tempo" in result
        assert "beat_times" in result
        assert "beat_strength" in result
        assert "rhythm_complexity" in result
        
        # Validate tempo range
        assert 40.0 <= result["tempo"] <= 200.0
        
        # Validate beat times
        beat_times = result["beat_times"]
        assert isinstance(beat_times, list)
        assert len(beat_times) > 0
        assert all(isinstance(t, (int, float)) for t in beat_times)
        
        # Validate beat strength and complexity
        assert 0.0 <= result["beat_strength"] <= 1.0
        assert 0.0 <= result["rhythm_complexity"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_melody_features_success(self, audio_extractor, sample_audio_data):
        """Test successful melody feature extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_melody_features(test_audio_file)
        
        assert_success_response(result)
        
        # Validate melody features
        expected_keys = [
            "pitch_contour", "melodic_intervals", 
            "pitch_class_distribution", "tonal_strength"
        ]
        for key in expected_keys:
            assert key in result
        
        # Validate pitch contour
        pitch_contour = result["pitch_contour"]
        assert isinstance(pitch_contour, list)
        assert len(pitch_contour) > 0
        
        # Validate melodic intervals
        intervals = result["melodic_intervals"]
        assert isinstance(intervals, list)
        assert len(intervals) == len(pitch_contour) - 1
        
        # Validate pitch class distribution
        pcd = result["pitch_class_distribution"]
        assert isinstance(pcd, list)
        assert len(pcd) == 12
        assert_approximately_equal(sum(pcd), 1.0, tolerance=0.01)
        
        # Validate tonal strength
        assert 0.0 <= result["tonal_strength"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_harmony_features_success(self, audio_extractor, sample_audio_data):
        """Test successful harmony feature extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_harmony_features(test_audio_file)
        
        assert_success_response(result)
        
        # Validate harmony features
        expected_keys = [
            "chroma_features", "key_strength", 
            "estimated_key", "harmonic_complexity"
        ]
        for key in expected_keys:
            assert key in result
        
        # Validate chroma features
        chroma = result["chroma_features"]
        assert isinstance(chroma, list)
        assert len(chroma) == 12
        
        # Validate key strength
        assert 0.0 <= result["key_strength"] <= 1.0
        
        # Validate estimated key format
        key_pattern = r'^[A-G][#b]?\s+(Major|Minor|maj|min|M|m)$'
        import re
        assert re.match(key_pattern, result["estimated_key"]), \
            f"Invalid key format: {result['estimated_key']}"
        
        # Validate harmonic complexity
        assert 0.0 <= result["harmonic_complexity"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_timbre_features_success(self, audio_extractor, sample_audio_data):
        """Test successful timbre feature extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_timbre_features(test_audio_file)
        
        assert_success_response(result)
        
        # Validate timbre features
        expected_keys = [
            "spectral_centroid", "spectral_bandwidth", 
            "spectral_rolloff", "zero_crossing_rate", "mfcc"
        ]
        for key in expected_keys:
            assert key in result
        
        # Validate spectral features (should be positive)
        assert result["spectral_centroid"] > 0
        assert result["spectral_bandwidth"] > 0
        assert result["spectral_rolloff"] > 0
        assert result["zero_crossing_rate"] >= 0
        
        # Validate MFCC
        mfcc = result["mfcc"]
        assert isinstance(mfcc, list)
        assert len(mfcc) == 13  # Standard 13 MFCC coefficients
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_structure_features_success(self, audio_extractor, sample_audio_data):
        """Test successful structure feature extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_structure_features(test_audio_file)
        
        assert_success_response(result)
        
        # Validate structure features
        expected_keys = [
            "segments", "segment_similarity", 
            "form_type", "repetition_score"
        ]
        for key in expected_keys:
            assert key in result
        
        # Validate segments
        assert result["segments"] > 0
        assert isinstance(result["segments"], int)
        
        # Validate segment similarity
        assert 0.0 <= result["segment_similarity"] <= 1.0
        
        # Validate form type
        valid_forms = ["verse-chorus", "ABA", "rondo", "through-composed", "unknown"]
        assert result["form_type"] in valid_forms
        
        # Validate repetition score
        assert 0.0 <= result["repetition_score"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_tempo_and_meter_success(self, audio_extractor, sample_audio_data):
        """Test successful tempo and meter extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_tempo_and_meter(test_audio_file)
        
        assert_success_response(result)
        
        # Validate tempo
        assert "tempo" in result
        assert "meter" in result
        assert "confidence" in result
        
        assert 40.0 <= result["tempo"] <= 200.0
        
        # Validate meter format
        meter_pattern = r'^\d+/\d+$'
        import re
        assert re.match(meter_pattern, result["meter"]), \
            f"Invalid meter format: {result['meter']}"
        
        # Validate confidence
        assert 0.0 <= result["confidence"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_pitch_and_tuning_success(self, audio_extractor, sample_audio_data):
        """Test successful pitch and tuning extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_pitch_and_tuning(test_audio_file)
        
        assert_success_response(result)
        
        # Validate pitch and tuning features
        expected_keys = [
            "fundamental_frequency", "pitch_deviation", 
            "tuning_accuracy", "estimated_tuning"
        ]
        for key in expected_keys:
            assert key in result
        
        # Validate fundamental frequency
        assert result["fundamental_frequency"] > 0  # Should be positive
        
        # Validate pitch deviation
        assert result["pitch_deviation"] >= 0  # Should be non-negative
        
        # Validate tuning accuracy
        assert 0.0 <= result["tuning_accuracy"] <= 1.0
        
        # Validate estimated tuning (in cents)
        assert isinstance(result["estimated_tuning"], (int, float))
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_dynamics_features_success(self, audio_extractor, sample_audio_data):
        """Test successful dynamics feature extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_dynamics_features(test_audio_file)
        
        assert_success_response(result)
        
        # Validate dynamics features
        expected_keys = [
            "loudness", "dynamic_range", 
            "compression_ratio", "transients"
        ]
        for key in expected_keys:
            assert key in result
        
        # Validate loudness (in dB)
        assert isinstance(result["loudness"], (int, float))
        
        # Validate dynamic range (in dB)
        assert result["dynamic_range"] >= 0
        
        # Validate compression ratio
        assert result["compression_ratio"] >= 1.0
        
        # Validate transients
        assert "transient_count" in result["transients"]
        assert "average_transient_strength" in result["transients"]
        assert result["transients"]["transient_count"] >= 0
        assert result["transients"]["average_transient_strength"] >= 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_spectral_features_success(self, audio_extractor, sample_audio_data):
        """Test successful spectral feature extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_spectral_features(test_audio_file)
        
        assert_success_response(result)
        
        # Validate spectral features
        expected_keys = [
            "spectral_centroid", "spectral_bandwidth", 
            "spectral_rolloff", "spectral_flux", "spectral_contrast"
        ]
        for key in expected_keys:
            assert key in result
        
        # Validate basic spectral features (should be positive)
        assert result["spectral_centroid"] > 0
        assert result["spectral_bandwidth"] > 0
        assert result["spectral_rolloff"] > 0
        assert result["spectral_flux"] >= 0
        
        # Validate spectral contrast
        spectral_contrast = result["spectral_contrast"]
        assert isinstance(spectral_contrast, list)
        assert len(spectral_contrast) == 7  # Standard 7 spectral contrast bands
        assert all(band >= 0 for band in spectral_contrast)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_audio_metadata_success(self, audio_extractor, sample_audio_data):
        """Test successful audio metadata extraction."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        result = await audio_extractor.extract_audio_metadata(test_audio_file)
        
        assert_success_response(result)
        
        # Validate metadata
        expected_keys = [
            "duration", "sample_rate", "channels", 
            "bit_depth", "format", "file_size"
        ]
        for key in expected_keys:
            assert key in result
        
        # Validate numeric values
        assert result["duration"] > 0
        assert result["sample_rate"] > 0
        assert result["channels"] in [1, 2]
        assert result["bit_depth"] in [16, 24, 32]
        assert result["file_size"] > 0
        
        # Validate format
        valid_formats = ["mp3", "wav", "flac", "aac", "ogg"]
        assert result["format"] in valid_formats


class TestAudioFeatureExtractorErrorHandling:
    """Test error handling in Audio Feature Extractor."""
    
    @pytest.fixture
    def error_prone_extractor(self):
        """Create an extractor that simulates various errors."""
        extractor = AudioFeatureExtractor()
        
        # Mock librosa to raise exceptions
        extractor.librosa = Mock()
        extractor.librosa.load.side_effect = Exception("Audio processing error")
        
        return extractor
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_audio_processing_error_handling(self, error_prone_extractor):
        """Test handling of audio processing errors."""
        result = await error_prone_extractor.extract_comprehensive_features(test_audio_file)
        
        assert_error_response(result)
        assert "Audio processing error" in result["error"]["message"]
        assert result["error"]["status_code"] == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unsupported_format_error_handling(self, error_prone_extractor):
        """Test handling of unsupported format errors."""
        # Mock specific error for unsupported format
        class UnsupportedFormatError(Exception):
            pass
        
        error_prone_extractor.librosa.load.side_effect = UnsupportedFormatError("Unsupported audio format")
        
        result = await error_prone_extractor.extract_comprehensive_features("test.unsupported")
        
        assert_error_response(result)
        assert "Unsupported" in result["error"]["message"]
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_corrupted_file_error_handling(self, error_prone_extractor):
        """Test handling of corrupted file errors."""
        # Mock specific error for corrupted file
        class CorruptedFileError(Exception):
            pass
        
        error_prone_extractor.librosa.load.side_effect = CorruptedFileError("Corrupted audio file")
        
        result = await error_prone_extractor.extract_comprehensive_features("test_corrupted.mp3")
        
        assert_error_response(result)
        assert "Corrupted" in result["error"]["message"]
        assert result["error"]["status_code"] == 422


class TestAudioFeatureExtractorIntegration:
    """Integration tests for Audio Feature Extractor."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_feature_analysis_workflow(self, audio_extractor, sample_audio_data):
        """Test complete feature analysis workflow."""
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        # Step 1: Extract comprehensive features
        comprehensive_result = await audio_extractor.extract_comprehensive_features(test_audio_file)
        assert_success_response(comprehensive_result)
        
        # Step 2: Extract individual feature sets
        rhythm_result = await audio_extractor.extract_rhythm_features(test_audio_file)
        assert_success_response(rhythm_result)
        
        melody_result = await audio_extractor.extract_melody_features(test_audio_file)
        assert_success_response(melody_result)
        
        harmony_result = await audio_extractor.extract_harmony_features(test_audio_file)
        assert_success_response(harmony_result)
        
        timbre_result = await audio_extractor.extract_timbre_features(test_audio_file)
        assert_success_response(timbre_result)
        
        structure_result = await audio_extractor.extract_structure_features(test_audio_file)
        assert_success_response(structure_result)
        
        # Step 3: Verify consistency between comprehensive and individual features
        comprehensive_features = comprehensive_result["features"]
        
        # Compare rhythm features
        assert comprehensive_features["rhythm"]["tempo"] == rhythm_result["tempo"]
        assert comprehensive_features["rhythm"]["beat_strength"] == rhythm_result["beat_strength"]
        
        # Compare melody features
        assert (comprehensive_features["melody"]["tonal_strength"] == 
                melody_result["tonal_strength"])
        
        # Compare harmony features
        assert (comprehensive_features["harmony"]["key_strength"] == 
                harmony_result["key_strength"])
        assert (comprehensive_features["harmony"]["estimated_key"] == 
                harmony_result["estimated_key"])
        
        # Compare timbre features
        assert (comprehensive_features["timbre"]["spectral_centroid"] == 
                timbre_result["spectral_centroid"])
        assert (comprehensive_features["timbre"]["mfcc"] == 
                timbre_result["mfcc"])
        
        # Compare structure features
        assert (comprehensive_features["structure"]["segments"] == 
                structure_result["segments"])
        assert (comprehensive_features["structure"]["form_type"] == 
                structure_result["form_type"])
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_multiple_file_analysis_consistency(self, audio_extractor):
        """Test feature extraction consistency across multiple similar files."""
        # Create multiple test audio files with similar characteristics
        test_files = [
            "/tmp/test_audio_1.mp3",
            "/tmp/test_audio_2.mp3", 
            "/tmp/test_audio_3.mp3"
        ]
        
        # Mock similar audio data for all files
        sample_rate = 22050
        duration = 2.0
        frequency = 440.0  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        base_audio = np.sin(2 * np.pi * frequency * t)
        
        # Add slight variations to each file
        audio_variations = [
            base_audio + np.random.normal(0, 0.01, len(base_audio)),
            base_audio + np.random.normal(0, 0.01, len(base_audio)),
            base_audio + np.random.normal(0, 0.01, len(base_audio))
        ]
        
        results = []
        
        for i, (file_path, audio_data) in enumerate(zip(test_files, audio_variations)):
            # Mock librosa.load for each file
            audio_extractor.librosa.load.return_value = (audio_data, sample_rate)
            
            result = await audio_extractor.extract_comprehensive_features(file_path)
            assert_success_response(result)
            results.append(result["features"])
        
        # Verify that features are consistent across similar files
        # Check that tempos are similar (within reasonable tolerance)
        tempos = [r["rhythm"]["tempo"] for r in results]
        avg_tempo = sum(tempos) / len(tempos)
        
        for tempo in tempos:
            assert_approximately_equal(tempo, avg_tempo, tolerance=10.0)
        
        # Check that keys are the same or closely related
        keys = [r["harmony"]["estimated_key"] for r in results]
        # All should be the same key for this simple test
        assert all(key == keys[0] for key in keys)
        
        # Check that spectral features are in similar ranges
        spectral_centroids = [r["timbre"]["spectral_centroid"] for r in results]
        avg_centroid = sum(spectral_centroids) / len(spectral_centroids)
        
        for centroid in spectral_centroids:
            assert_approximately_equal(centroid, avg_centroid, tolerance=500.0)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_feature_extraction_performance(self, audio_extractor, sample_audio_data):
        """Test performance of feature extraction."""
        import time
        
        # Mock librosa.load
        audio_extractor.librosa.load.return_value = (
            sample_audio_data["audio_data"], 
            sample_audio_data["sample_rate"]
        )
        
        # Measure extraction time
        start_time = time.time()
        result = await audio_extractor.extract_comprehensive_features(test_audio_file)
        end_time = time.time()
        
        extraction_time = end_time - start_time
        
        # Verify successful extraction
        assert_success_response(result)
        
        # Verify performance (should complete within reasonable time)
        assert extraction_time < 5.0, f"Feature extraction took {extraction_time}s, expected < 5s"
        
        # For a 1-second audio file, extraction should be much faster
        assert extraction_time < 1.0, f"Feature extraction took {extraction_time}s, expected < 1s for short audio"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_feature_validation_edge_cases(self, audio_extractor):
        """Test feature extraction with edge cases."""
        import numpy as np
        
        # Test with very short audio
        short_audio = np.random.randn(100)  # Only 100 samples
        audio_extractor.librosa.load.return_value = (short_audio, 22050)
        
        result = await audio_extractor.extract_comprehensive_features(test_audio_file)
        
        # Should still work but might have limited features
        assert_success_response(result)
        
        # Test with silent audio
        silent_audio = np.zeros(22050)  # 1 second of silence
        audio_extractor.librosa.load.return_value = (silent_audio, 22050)
        
        result = await audio_extractor.extract_comprehensive_features(test_audio_file)
        assert_success_response(result)
        
        # Silent audio should have specific characteristics
        features = result["features"]
        assert features["rhythm"]["tempo"] == 0 or features["rhythm"]["beat_strength"] == 0
        assert features["timbre"]["spectral_centroid"] == 0
        
        # Test with very loud audio (clipping)
        loud_audio = np.ones(22050)  # Maximum amplitude
        audio_extractor.librosa.load.return_value = (loud_audio, 22050)
        
        result = await audio_extractor.extract_comprehensive_features(test_audio_file)
        assert_success_response(result)
        
        # Loud audio should have high zero crossing rate due to clipping
        features = result["features"]
        assert features["timbre"]["zero_crossing_rate"] > 0.1