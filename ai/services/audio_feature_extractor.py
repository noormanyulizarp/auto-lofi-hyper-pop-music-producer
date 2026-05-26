import librosa
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

class AudioFeatureExtractor:
    """Service for extracting detailed audio features using librosa"""
    
    def __init__(self):
        self.sample_rate = 22050
        
    async def extract_comprehensive_features(self, audio_path: str) -> Dict[str, Any]:
        """Extract comprehensive audio features for music analysis"""
        try:
            logger.info(f"Extracting audio features: {audio_path}")
            
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            features = {}
            
            # Basic features
            features.update(self._extract_basic_features(y, sr))
            
            # Rhythmic features
            features.update(self._extract_rhythmic_features(y, sr))
            
            # Melodic features
            features.update(self._extract_melodic_features(y, sr))
            
            # Harmonic features
            features.update(self._extract_harmonic_features(y, sr))
            
            # Timbral features
            features.update(self._extract_timbral_features(y, sr))
            
            # Structural features
            features.update(self._extract_structural_features(y, sr))
            
            # Genre classification features
            features.update(self._classify_genre_features(y, sr))
            
            logger.info(f"Audio features extracted successfully")
            return {
                "success": True,
                "features": features,
                "sample_rate": sr,
                "duration": len(y) / sr,
                "extracted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "features": {}
            }
    
    def _extract_basic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract basic audio features"""
        features = {}
        
        # Tempo and beat tracking
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features["tempo"] = float(tempo)
        features["beat_count"] = len(beats)
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)
        features["zero_crossing_rate_mean"] = float(np.mean(zcr))
        features["zero_crossing_rate_std"] = float(np.std(zcr))
        
        # RMS energy
        rms = librosa.feature.rms(y=y)
        features["rms_mean"] = float(np.mean(rms))
        features["rms_std"] = float(np.std(rms))
        
        # Spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        features["spectral_centroid_mean"] = float(np.mean(spectral_centroid))
        features["spectral_centroid_std"] = float(np.std(spectral_centroid))
        
        return features
    
    def _extract_rhythmic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract rhythmic features"""
        features = {}
        
        # Onset detection
        onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
        features["onset_strength_mean"] = float(np.mean(onset_envelope))
        features["onset_strength_std"] = float(np.std(onset_envelope))
        
        # Tempo estimation with multiple methods
        tempo_harmonic, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
        tempo_percussive = librosa.beat.tempo(y=y, sr=sr, onset_envelope=onset_envelope)[0]
        
        features["tempo_harmonic"] = float(tempo_harmonic)
        features["tempo_percussive"] = float(tempo_percussive)
        
        # Beat strength
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        beat_strength = np.mean(chroma, axis=0)
        features["beat_strength_mean"] = float(np.mean(beat_strength))
        features["beat_strength_std"] = float(np.std(beat_strength))
        
        # Rhythmic complexity
        hop_length = 512
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
        tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr, hop_length=hop_length)
        features["rhythmic_complexity"] = float(np.std(tempogram))
        
        return features
    
    def _extract_melodic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract melodic features"""
        features = {}
        
        # Pitch detection
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        features["pitch_mean"] = float(np.mean(pitches[magnitudes > np.max(magnitudes) * 0.1]))
        features["pitch_std"] = float(np.std(pitches[magnitudes > np.max(magnitudes) * 0.1]))
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        for i, chroma_vec in enumerate(chroma):
            features[f"chroma_{i}_mean"] = float(np.mean(chroma_vec))
            features[f"chroma_{i}_std"] = float(np.std(chroma_vec))
        
        # Mel-spectrogram features
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        features["mel_spec_mean"] = float(np.mean(mel_spec_db))
        features["mel_spec_std"] = float(np.std(mel_spec_db))
        
        # MFCC features
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        for i in range(13):
            features[f"mfcc_{i}_mean"] = float(np.mean(mfcc[i]))
            features[f"mfcc_{i}_std"] = float(np.std(mfcc[i]))
        
        return features
    
    def _extract_harmonic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract harmonic features"""
        features = {}
        
        # Harmonic-percussive separation
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        # Harmonic features
        harmonic_rms = librosa.feature.rms(y=y_harmonic)
        features["harmonic_energy_mean"] = float(np.mean(harmonic_rms))
        features["harmonic_energy_std"] = float(np.std(harmonic_rms))
        
        # Percussive features
        percussive_rms = librosa.feature.rms(y=y_percussive)
        features["percussive_energy_mean"] = float(np.mean(percussive_rms))
        features["percussive_energy_std"] = float(np.std(percussive_rms))
        
        # Harmonic-percussive ratio
        h_p_ratio = np.mean(harmonic_rms) / (np.mean(percussive_rms) + 1e-10)
        features["harmonic_percussive_ratio"] = float(h_p_ratio)
        
        # Chroma harmony features
        chroma = librosa.feature.chroma_stft(y=y_harmonic, sr=sr)
        features["chroma_harmony_mean"] = float(np.mean(chroma))
        features["chroma_harmony_std"] = float(np.std(chroma))
        
        # Key detection
        key = self._detect_key(chroma)
        features["detected_key"] = key
        
        return features
    
    def _extract_timbral_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract timbral features"""
        features = {}
        
        # Spectral features
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        features["spectral_bandwidth_mean"] = float(np.mean(spectral_bandwidth))
        features["spectral_bandwidth_std"] = float(np.std(spectral_bandwidth))
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        features["spectral_rolloff_mean"] = float(np.mean(spectral_rolloff))
        features["spectral_rolloff_std"] = float(np.std(spectral_rolloff))
        
        spectral_flatness = librosa.feature.spectral_flatness(y=y)
        features["spectral_flatness_mean"] = float(np.mean(spectral_flatness))
        features["spectral_flatness_std"] = float(np.std(spectral_flatness))
        
        # Tonnetz features
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        features["tonnetz_mean"] = float(np.mean(tonnetz))
        features["tonnetz_std"] = float(np.std(tonnetz))
        
        return features
    
    def _extract_structural_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract structural features"""
        features = {}
        
        # Segment boundaries detection
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        segment_boundaries = librosa.segment.agglomerative(chroma, k=8)
        
        features["segment_count"] = int(len(np.unique(segment_boundaries)))
        features["segment_duration_mean"] = float(len(y) / sr / len(np.unique(segment_boundaries)))
        
        # Self-similarity matrix
        sim_matrix = librosa.segment.cross_similarity(chroma, chroma)
        features["self_similarity_mean"] = float(np.mean(sim_matrix))
        features["self_similarity_std"] = float(np.std(sim_matrix))
        
        # Dynamic features
        rms = librosa.feature.rms(y=y)
        features["dynamic_range"] = float(np.max(rms) - np.min(rms))
        features["dynamic_mean"] = float(np.mean(rms))
        
        return features
    
    def _classify_genre_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract genre classification features"""
        features = {}
        
        # Rhythmic complexity for genre detection
        onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
        features["onset_envelope_mean"] = float(np.mean(onset_envelope))
        features["onset_envelope_variance"] = float(np.var(onset_envelope))
        
        # Spectral contrast
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        for i, contrast_vec in enumerate(spectral_contrast):
            features[f"spectral_contrast_{i}_mean"] = float(np.mean(contrast_vec))
        
        # Polyphonic features
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        harmonic_energy = np.sum(y_harmonic ** 2)
        percussive_energy = np.sum(y_percussive ** 2)
        total_energy = harmonic_energy + percussive_energy
        
        features["harmonic_ratio"] = float(harmonic_energy / total_energy)
        features["percussive_ratio"] = float(percussive_energy / total_energy)
        
        # Tempo-based genre indicators
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features["tempo_category"] = self._categorize_tempo(float(tempo))
        
        return features
    
    def _detect_key(self, chroma: np.ndarray) -> str:
        """Detect musical key from chroma features"""
        # Simple key detection using correlation with key profiles
        key_profiles = {
            'C': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
            'C#': [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
            'D': [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            'D#': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            'E': [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            'F': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
            'F#': [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            'G': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            'G#': [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            'A': [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1],
            'A#': [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            'B': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        }
        
        # Calculate correlation with each key profile
        chroma_mean = np.mean(chroma, axis=1)
        best_key = 'C'
        best_correlation = -1
        
        for key, profile in key_profiles.items():
            correlation = np.corrcoef(chroma_mean, profile)[0, 1]
            if correlation > best_correlation:
                best_correlation = correlation
                best_key = key
        
        return best_key
    
    def _categorize_tempo(self, tempo: float) -> str:
        """Categorize tempo into genre-relevant categories"""
        if tempo < 60:
            return "slow"
        elif tempo < 90:
            return "moderate_slow"
        elif tempo < 120:
            return "moderate"
        elif tempo < 140:
            return "fast"
        elif tempo < 180:
            return "very_fast"
        else:
            return "extreme"

# Global service instance  
audio_feature_extractor = AudioFeatureExtractor()