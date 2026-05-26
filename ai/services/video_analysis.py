import asyncio
import os
import tempfile
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import yt_dlp
import cv2
from moviepy.editor import VideoFileClip
import whisper
from loguru import logger

from ..config import settings
from ..models.responses import (
    AnalyzeVideoRequest,
    VideoAnalysisResponse,
    VideoAnalysisResult,
    TaskStatus
)
from .audio_feature_extractor import audio_feature_extractor

class VideoAnalysisService:
    """Service for analyzing video tutorials and extracting musical elements"""
    
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        self.supported_formats = settings.VIDEO_FORMATS
        self.max_duration = settings.MAX_VIDEO_DURATION
        
    async def analyze_video(self, request: AnalyzeVideoRequest) -> VideoAnalysisResponse:
        """Analyze video tutorial and extract musical elements"""
        try:
            logger.info(f"Starting video analysis: {request.video_url}")
            
            # Validate request
            self._validate_video_request(request)
            
            # Create task
            task_id = self._generate_task_id()
            
            # Start analysis in background
            asyncio.create_task(self._process_video_analysis(task_id, request))
            
            response = VideoAnalysisResponse(
                task_id=task_id,
                status=TaskStatus.PROCESSING,
                estimated_time=120,  # 2 minutes estimated
                message="Video analysis started successfully"
            )
            
            logger.info(f"Video analysis started: {task_id}")
            return response
            
        except Exception as e:
            logger.error(f"Video analysis error: {str(e)}")
            raise Exception(f"Failed to analyze video: {str(e)}")
    
    async def get_analysis_status(self, task_id: str) -> VideoAnalysisResult:
        """Get video analysis status and results"""
        try:
            logger.info(f"Checking analysis status: {task_id}")
            
            # TODO: Implement status check from database or cache
            # For now, return mock status
            result = VideoAnalysisResult(
                task_id=task_id,
                status=TaskStatus.PROCESSING,
                video_info={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            logger.info(f"Analysis status: {task_id} - {result.status}")
            return result
            
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            raise Exception(f"Failed to get analysis status: {str(e)}")
    
    async def _process_video_analysis(self, task_id: str, request: AnalyzeVideoRequest):
        """Process video analysis in background"""
        try:
            # Download video
            video_path = await self._download_video(request.video_url, task_id)
            
            # Extract video info
            video_info = await self._extract_video_info(video_path)
            
            # Extract audio if requested
            audio_features = None
            if request.extract_audio:
                audio_features = await self._extract_audio_features(video_path)
            
            # Generate transcript if requested
            transcript = None
            if request.generate_transcript:
                transcript = await self._generate_transcript(video_path)
            
            # Analyze musical elements
            musical_elements = await self._analyze_musical_elements(
                video_path, request.focus_type, audio_features, transcript
            )
            
            # Extract learned patterns
            learned_patterns = await self._extract_learned_patterns(
                musical_elements, transcript, request.focus_type
            )
            
            # Save results
            result = VideoAnalysisResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                video_info=video_info,
                audio_features=audio_features,
                transcript=transcript,
                musical_elements=musical_elements,
                learned_patterns=learned_patterns,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # TODO: Save to database
            logger.info(f"Video analysis completed: {task_id}")
            
        except Exception as e:
            logger.error(f"Video analysis failed: {task_id} - {str(e)}")
            # TODO: Update task status to failed in database
    
    async def _download_video(self, video_url: str, task_id: str) -> str:
        """Download video using yt-dlp"""
        try:
            logger.info(f"Downloading video: {video_url}")
            
            # Create download directory
            download_dir = Path("uploads/videos")
            download_dir.mkdir(exist_ok=True)
            
            # Configure yt-dlp
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': str(download_dir / f"{task_id}.%(ext)s"),
                'quiet': True,
                'no_warnings': True,
                'max_filesize': settings.MAX_FILE_SIZE,
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                video_path = ydl.prepare_filename(info)
            
            logger.info(f"Video downloaded: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Video download failed: {str(e)}")
            raise Exception(f"Failed to download video: {str(e)}")
    
    async def _extract_video_info(self, video_path: str) -> Dict[str, Any]:
        """Extract basic video information"""
        try:
            with VideoFileClip(video_path) as video:
                return {
                    "duration": video.duration,
                    "fps": video.fps,
                    "size": video.size,
                    "resolution": f"{video.w}x{video.h}",
                    "has_audio": video.audio is not None
                }
                
        except Exception as e:
            logger.error(f"Video info extraction failed: {str(e)}")
            return {}
    
    async def _extract_audio_features(self, video_path: str) -> Dict[str, Any]:
        """Extract audio features from video using librosa"""
        try:
            logger.info(f"Extracting audio features: {video_path}")
            
            # Extract audio from video
            with VideoFileClip(video_path) as video:
                if video.audio is None:
                    logger.warning("No audio found in video")
                    return {
                        "duration": 0,
                        "sample_rate": 44100,
                        "channels": 0,
                        "tempo": 0,
                        "key": "Unknown",
                        "features": {},
                        "extraction_error": "No audio found"
                    }
                
                # Save audio temporarily
                audio_path = video_path.replace(".mp4", ".wav")
                video.audio.write_audiofile(audio_path, codec='pcm_s16le')
            
            # Use comprehensive audio feature extractor
            features_result = await audio_feature_extractor.extract_comprehensive_features(audio_path)
            
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            if features_result.get("success"):
                audio_features = features_result["features"]
                
                # Extract high-level information
                return {
                    "duration": audio_features.get("duration", 0),
                    "sample_rate": audio_features.get("sample_rate", 44100),
                    "channels": 2,  # Assuming stereo
                    "tempo": audio_features.get("tempo", 120),
                    "key": audio_features.get("detected_key", "C"),
                    "rhythmic_complexity": audio_features.get("rhythmic_complexity", 0.0),
                    "harmonic_percussive_ratio": audio_features.get("harmonic_percussive_ratio", 1.0),
                    "spectral_centroid": audio_features.get("spectral_centroid_mean", 0.0),
                    "dynamic_range": audio_features.get("dynamic_range", 0.0),
                    "features": audio_features,
                    "extraction_successful": True
                }
            else:
                logger.error(f"Audio feature extraction failed: {features_result.get('error')}")
                return {
                    "duration": 0,
                    "sample_rate": 44100,
                    "channels": 2,
                    "tempo": 0,
                    "key": "Unknown",
                    "features": {},
                    "extraction_successful": False,
                    "extraction_error": features_result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {str(e)}")
            return {
                "duration": 0,
                "sample_rate": 44100,
                "channels": 0,
                "tempo": 0,
                "key": "Unknown",
                "features": {},
                "extraction_successful": False,
                "extraction_error": str(e)
            }
    
    async def _generate_transcript(self, video_path: str) -> str:
        """Generate transcript using Whisper"""
        try:
            logger.info(f"Generating transcript: {video_path}")
            
            # Extract audio
            with VideoFileClip(video_path) as video:
                if video.audio is None:
                    return "No audio found in video"
                
                # Save audio temporarily
                audio_path = video_path.replace(".mp4", ".mp3")
                video.audio.write_audiofile(audio_path)
            
            # Generate transcript
            result = self.whisper_model.transcribe(audio_path)
            transcript = result["text"]
            
            # Clean up
            os.remove(audio_path)
            
            logger.info(f"Transcript generated: {len(transcript)} chars")
            return transcript
            
        except Exception as e:
            logger.error(f"Transcript generation failed: {str(e)}")
            return ""
    
    async def _analyze_musical_elements(
        self, 
        video_path: str, 
        focus_type: str, 
        audio_features: Dict[str, Any], 
        transcript: str
    ) -> Dict[str, Any]:
        """Analyze musical elements from video using AI"""
        try:
            logger.info(f"Analyzing musical elements: {focus_type}")
            
            from .provider_service import provider_service
            
            # Prepare analysis context
            analysis_context = {
                "focus_type": focus_type,
                "audio_features": audio_features,
                "transcript_length": len(transcript) if transcript else 0,
                "tempo": audio_features.get("tempo", 120),
                "key": audio_features.get("key", "C"),
                "duration": audio_features.get("duration", 0)
            }
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the musical elements from this video tutorial focusing on {focus_type}.
            
            Video Analysis Context:
            - Focus Type: {focus_type}
            - Detected Tempo: {analysis_context['tempo']} BPM
            - Detected Key: {analysis_context['key']}
            - Duration: {analysis_context['duration']:.2f} seconds
            - Audio Features Available: {bool(audio_features.get('features'))}
            - Transcript Available: {bool(transcript)}
            
            Based on the audio analysis and any transcript available, provide detailed analysis of:
            
            1. Rhythm Patterns: Identify rhythmic patterns, time signature, beat patterns
            2. Melody Patterns: Identify melodic contours, scales, melodic development
            3. Harmony Patterns: Identify chord progressions, harmonic relationships
            4. Structure Patterns: Identify song structure, section arrangements
            5. Instruments Detected: Identify instruments and their roles
            6. Techniques Observed: Identify playing techniques and methods
            
            Provide specific, actionable musical insights that can be applied to music creation.
            """
            
            # Use AI to analyze musical elements
            result = await provider_service.call_model_by_task(
                task_type="music_theory",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            # Parse the AI response into structured data
            analysis_content = result.get("content", "")
            
            # Structure the analysis based on focus type
            musical_elements = {
                "focus_type": focus_type,
                "analysis_context": analysis_context,
                "ai_analysis": analysis_content,
                "rhythm_patterns": self._extract_rhythm_patterns(analysis_content, audio_features),
                "melody_patterns": self._extract_melody_patterns(analysis_content, audio_features),
                "harmony_patterns": self._extract_harmony_patterns(analysis_content, audio_features),
                "structure_patterns": self._extract_structure_patterns(analysis_content, audio_features),
                "instruments_detected": self._extract_instruments(analysis_content),
                "techniques_observed": self._extract_techniques(analysis_content),
                "key_insights": self._extract_key_insights(analysis_content, focus_type)
            }
            
            logger.info(f"Musical elements analysis completed: {focus_type}")
            return musical_elements
            
        except Exception as e:
            logger.error(f"Musical element analysis failed: {str(e)}")
            return {
                "focus_type": focus_type,
                "analysis_error": str(e),
                "rhythm_patterns": [],
                "melody_patterns": [],
                "harmony_patterns": [],
                "structure_patterns": [],
                "instruments_detected": [],
                "techniques_observed": []
            }
    
    def _extract_rhythm_patterns(self, content: str, audio_features: Dict[str, Any]) -> List[str]:
        """Extract rhythm patterns from AI analysis"""
        patterns = []
        
        # Use audio features to enhance rhythm analysis
        if audio_features.get("features"):
            features = audio_features["features"]
            tempo = features.get("tempo", 120)
            rhythmic_complexity = features.get("rhythmic_complexity", 0.0)
            
            if tempo > 140:
                patterns.append(f"Fast tempo detected ({tempo} BPM) - suitable for energetic music")
            elif tempo < 90:
                patterns.append(f"Slow tempo detected ({tempo} BPM) - suitable for ambient/chill music")
            else:
                patterns.append(f"Moderate tempo detected ({tempo} BPM) - versatile for various genres")
            
            if rhythmic_complexity > 0.5:
                patterns.append("High rhythmic complexity - intricate patterns suitable for advanced compositions")
        
        # Add patterns from AI analysis
        rhythm_keywords = ["rhythm", "beat", "tempo", "syncopation", "groove", "pulse"]
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in rhythm_keywords) and len(line.strip()) > 10:
                patterns.append(line.strip())
        
        return patterns[:5]  # Limit to top 5 patterns
    
    def _extract_melody_patterns(self, content: str, audio_features: Dict[str, Any]) -> List[str]:
        """Extract melody patterns from AI analysis"""
        patterns = []
        
        # Use audio features to enhance melody analysis
        if audio_features.get("features"):
            features = audio_features["features"]
            key = features.get("detected_key", "C")
            spectral_centroid = features.get("spectral_centroid_mean", 0.0)
            
            patterns.append(f"Key context: {key} major/minor")
            if spectral_centroid > 3000:
                patterns.append("Bright spectral characteristics - suggests higher register melodic content")
        
        # Add patterns from AI analysis
        melody_keywords = ["melody", "melodic", "phrase", "motif", "contour", "scale", "pitch"]
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in melody_keywords) and len(line.strip()) > 10:
                patterns.append(line.strip())
        
        return patterns[:5]
    
    def _extract_harmony_patterns(self, content: str, audio_features: Dict[str, Any]) -> List[str]:
        """Extract harmony patterns from AI analysis"""
        patterns = []
        
        # Use audio features to enhance harmony analysis
        if audio_features.get("features"):
            features = audio_features["features"]
            harmonic_ratio = features.get("harmonic_percussive_ratio", 1.0)
            
            if harmonic_ratio > 2.0:
                patterns.append("High harmonic content - rich harmonic structure suitable for complex progressions")
            elif harmonic_ratio < 0.5:
                patterns.append("Low harmonic content - percussive/drum-focused arrangement")
            else:
                patterns.append("Balanced harmonic content - suitable for most genres")
        
        # Add patterns from AI analysis
        harmony_keywords = ["harmony", "chord", "progression", "harmonic", "voicing", "cadence"]
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in harmony_keywords) and len(line.strip()) > 10:
                patterns.append(line.strip())
        
        return patterns[:5]
    
    def _extract_structure_patterns(self, content: str, audio_features: Dict[str, Any]) -> List[str]:
        """Extract structure patterns from AI analysis"""
        patterns = []
        
        # Use audio features to enhance structure analysis
        if audio_features.get("features"):
            features = audio_features["features"]
            segment_count = features.get("segment_count", 4)
            dynamic_range = features.get("dynamic_range", 0.0)
            
            patterns.append(f"Detected {segment_count} structural segments")
            if dynamic_range > 0.5:
                patterns.append("High dynamic range - suggests dynamic contrast in arrangement")
        
        # Add patterns from AI analysis
        structure_keywords = ["structure", "form", "section", "verse", "chorus", "bridge", "arrangement"]
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in structure_keywords) and len(line.strip()) > 10:
                patterns.append(line.strip())
        
        return patterns[:5]
    
    def _extract_instruments(self, content: str) -> List[str]:
        """Extract instrument information from AI analysis"""
        instruments = []
        
        # Common instrument keywords
        instrument_keywords = [
            "piano", "guitar", "bass", "drums", "synth", "violin", "cello", 
            "trumpet", "saxophone", "flute", "vocals", "keyboard", "percussion"
        ]
        
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            for instrument in instrument_keywords:
                if instrument in line_lower:
                    instruments.append(instrument.capitalize())
        
        # Remove duplicates and limit
        return list(set(instruments))[:8]
    
    def _extract_techniques(self, content: str) -> List[str]:
        """Extract playing techniques from AI analysis"""
        techniques = []
        
        # Common technique keywords
        technique_keywords = [
            "strumming", "picking", "fingering", "bending", "vibrato", 
            "sliding", "hammer-on", "pull-off", "palm mute", "sweep",
            "tapping", "harmonics", "distortion", "reverb", "delay"
        ]
        
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            for technique in technique_keywords:
                if technique in line_lower:
                    techniques.append(technique.replace("-", " ").title())
        
        # Remove duplicates and limit
        return list(set(techniques))[:8]
    
    def _extract_key_insights(self, content: str, focus_type: str) -> List[str]:
        """Extract key insights from AI analysis"""
        insights = []
        
        # Look for insight keywords
        insight_keywords = ["insight", "key", "important", "essential", "crucial", "fundamental"]
        
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in insight_keywords) and len(line.strip()) > 15:
                insights.append(line.strip())
        
        # Add focus-specific insights
        if focus_type == "rhythm":
            insights.append("Focus on rhythmic precision and groove development")
        elif focus_type == "melody":
            insights.append("Focus on melodic development and phrase construction")
        elif focus_type == "harmony":
            insights.append("Focus on chord progressions and harmonic movement")
        elif focus_type == "structure":
            insights.append("Focus on song form and arrangement techniques")
        
        return insights[:5]
    
    async def _extract_learned_patterns(
        self, 
        musical_elements: Dict[str, Any], 
        transcript: str, 
        focus_type: str
    ) -> List[Dict[str, Any]]:
        """Extract learned patterns from analysis using AI and ML"""
        try:
            logger.info(f"Extracting learned patterns: {focus_type}")
            
            from .provider_service import provider_service
            
            # Prepare comprehensive context
            context = {
                "focus_type": focus_type,
                "rhythm_patterns": musical_elements.get("rhythm_patterns", []),
                "melody_patterns": musical_elements.get("melody_patterns", []),
                "harmony_patterns": musical_elements.get("harmony_patterns", []),
                "structure_patterns": musical_elements.get("structure_patterns", []),
                "instruments": musical_elements.get("instruments_detected", []),
                "techniques": musical_elements.get("techniques_observed", []),
                "insights": musical_elements.get("key_insights", []),
                "transcript_summary": transcript[:500] if transcript else ""
            }
            
            # Create pattern learning prompt
            learning_prompt = f"""
            Analyze this musical analysis data and extract actionable learning patterns for music creation.
            
            Focus Type: {focus_type}
            Analysis Context: {context}
            
            Extract specific, actionable patterns that can be applied to music creation:
            
            1. Identify 3-5 core musical patterns from the analysis
            2. For each pattern, provide:
               - Pattern type and description
               - How to apply it in original compositions
               - Which genres it works best with
               - Skill level required (beginner/intermediate/advanced)
               - Practice recommendations
               - Common variations and modifications
            
            3. Include specific examples and implementation guidance
            4. Focus on practical, usable patterns rather than theoretical concepts
            
            Return the analysis in a structured format that can be directly used for music learning and creation.
            """
            
            # Use AI to extract learned patterns
            result = await provider_service.call_model_by_task(
                task_type="deep_analysis",
                messages=[{"role": "user", "content": learning_prompt}]
            )
            
            # Parse the AI response into structured patterns
            patterns_content = result.get("content", "")
            learned_patterns = self._parse_learned_patterns(patterns_content, focus_type, context)
            
            logger.info(f"Learned patterns extracted: {len(learned_patterns)} patterns")
            return learned_patterns
            
        except Exception as e:
            logger.error(f"Pattern extraction failed: {str(e)}")
            # Return basic fallback pattern
            return [{
                "pattern_type": focus_type,
                "description": f"Basic {focus_type} pattern from tutorial analysis",
                "application": f"Apply {focus_type} concepts learned from tutorial",
                "genres": ["lofi", "chill"],
                "skill_level": "beginner",
                "practice_advice": f"Practice {focus_type} exercises regularly",
                "variations": ["Basic", "Intermediate", "Advanced"],
                "confidence": 0.6,
                "source_analysis": "Analysis unavailable due to error",
                "extracted_at": datetime.utcnow().isoformat()
            }]
    
    def _parse_learned_patterns(self, content: str, focus_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into structured learned patterns"""
        patterns = []
        
        # Split content into potential pattern sections
        sections = content.split('\n\n')
        
        # Pattern keywords to identify pattern descriptions
        pattern_keywords = ["pattern", "approach", "technique", "method", "strategy", "concept", "idea"]
        
        current_pattern = {}
        
        for section in sections:
            section = section.strip()
            if len(section) < 20:  # Skip very short sections
                continue
                
            # Check if this section starts a new pattern
            first_line = section.split('\n')[0].lower()
            
            # Look for numbered patterns or pattern keywords
            if (any(keyword in first_line for keyword in pattern_keywords) or 
                any(char.isdigit() for char in first_line[:10])):
                
                # Save previous pattern if exists
                if current_pattern:
                    patterns.append(current_pattern)
                
                # Start new pattern
                current_pattern = {
                    "pattern_type": focus_type,
                    "description": section,
                    "application": "",
                    "genres": ["lofi", "chill", "ambient"],
                    "skill_level": self._determine_skill_level(section),
                    "practice_advice": "",
                    "variations": [],
                    "confidence": self._calculate_confidence(section, context),
                    "source_analysis": section[:200],
                    "extracted_at": datetime.utcnow().isoformat()
                }
            
            # Enhance current pattern with additional details
            elif current_pattern:
                section_lower = section.lower()
                
                # Look for application information
                if any(word in section_lower for word in ["apply", "use", "implement", "how to"]):
                    current_pattern["application"] = section
                
                # Look for genre information
                elif any(word in section_lower for word in ["genre", "style", "music", "works best"]):
                    genres = self._extract_genres(section)
                    if genres:
                        current_pattern["genres"] = genres
                
                # Look for skill level information
                elif any(word in section_lower for word in ["beginner", "intermediate", "advanced", "skill"]):
                    current_pattern["skill_level"] = self._determine_skill_level(section)
                
                # Look for practice advice
                elif any(word in section_lower for word in ["practice", "exercise", "drill", "learn"]):
                    current_pattern["practice_advice"] = section
                
                # Look for variations
                elif any(word in section_lower for word in ["variation", "alternative", "modify", "different"]):
                    variations = self._extract_variations(section)
                    current_pattern["variations"] = variations
        
        # Add the last pattern
        if current_pattern:
            patterns.append(current_pattern)
        
        # If no patterns were found, create a comprehensive pattern from the full content
        if not patterns:
            patterns.append({
                "pattern_type": focus_type,
                "description": content[:500],
                "application": f"Apply {focus_type} concepts from analysis to original compositions",
                "genres": ["lofi", "chill"],
                "skill_level": "intermediate",
                "practice_advice": f"Practice {focus_type} techniques and experiment with variations",
                "variations": ["Standard", "Modified", "Advanced"],
                "confidence": 0.7,
                "source_analysis": content[:300],
                "extracted_at": datetime.utcnow().isoformat()
            })
        
        # Ensure we have a reasonable number of patterns
        return patterns[:6]  # Limit to top 6 patterns
    
    def _determine_skill_level(self, text: str) -> str:
        """Determine skill level from text content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["beginner", "basic", "simple", "easy", "start"]):
            return "beginner"
        elif any(word in text_lower for word in ["advanced", "complex", "difficult", "expert", "master"]):
            return "advanced"
        else:
            return "intermediate"
    
    def _extract_genres(self, text: str) -> List[str]:
        """Extract genre information from text"""
        genres = []
        common_genres = [
            "lofi", "chill", "ambient", "electronic", "hiphop", "jazz", 
            "classical", "rock", "pop", "blues", "funk", "soul", "reggae",
            "country", "folk", "experimental", "dance", "house", "techno"
        ]
        
        text_lower = text.lower()
        for genre in common_genres:
            if genre in text_lower:
                genres.append(genre)
        
        return genres if genres else ["lofi", "chill"]
    
    def _extract_variations(self, text: str) -> List[str]:
        """Extract variations from text"""
        variations = []
        
        # Common variation keywords
        variation_keywords = ["basic", "standard", "simple", "modified", "advanced", "complex", "alternative"]
        
        text_lower = text.lower()
        for keyword in variation_keywords:
            if keyword in text_lower:
                variations.append(keyword.title())
        
        return variations if variations else ["Basic", "Modified"]
    
    def _calculate_confidence(self, text: str, context: Dict[str, Any]) -> float:
        """Calculate confidence score for pattern based on context and content"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if there are specific details
        if any(keyword in text.lower() for keyword in ["specific", "detailed", "precise", "exactly"]):
            confidence += 0.1
        
        # Increase confidence if there are practical applications
        if any(keyword in text.lower() for keyword in ["apply", "use", "implement", "practice"]):
            confidence += 0.1
        
        # Increase confidence if there are multiple elements from context
        element_count = sum(1 for key, value in context.items() if value and isinstance(value, list) and len(value) > 0)
        if element_count > 3:
            confidence += 0.1
        
        # Cap confidence at 0.95
        return min(confidence, 0.95)
    
    def _validate_video_request(self, request: AnalyzeVideoRequest):
        """Validate video analysis request"""
        if not request.video_url or len(request.video_url.strip()) == 0:
            raise Exception("Video URL is required")
        
        if not request.title or len(request.title.strip()) == 0:
            raise Exception("Title is required")
        
        # TODO: Validate video URL format and accessibility
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        import uuid
        return str(uuid.uuid4())

# Global service instance
video_analysis_service = VideoAnalysisService()