import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from .provider_service import provider_service
from ..models.responses import Genre, Mood, TaskStatus

class MusicAIService:
    """Service for using AI models to enhance music generation and analysis"""
    
    def __init__(self):
        self.provider_service = provider_service
        
    async def generate_music_concepts(
        self, 
        genre: Genre, 
        mood: Mood, 
        theme: str,
        duration: int
    ) -> Dict[str, Any]:
        """Generate music concepts using AI models"""
        try:
            logger.info(f"Generating music concepts for {genre} {mood} - {theme}")
            
            # Use different models for different aspects
            concepts = {}
            
            # Music theory and structure (using trinity-thinking)
            structure_prompt = f"""
            Generate a music structure for a {genre.value} song with {mood.value} mood.
            Theme: {theme}
            Duration: {duration} seconds
            
            Provide:
            1. Overall structure (verse, chorus, bridge, etc.)
            2. Time signature and tempo suggestions
            3. Key and scale recommendations
            4. Instrumentation ideas
            """
            
            structure_result = await self.provider_service.call_model_by_task(
                task_type="music_theory",
                messages=[{"role": "user", "content": structure_prompt}]
            )
            
            concepts["structure"] = structure_result.get("content", "")
            
            # Melodic ideas (using music-friendly model)
            melody_prompt = f"""
            Generate melodic ideas for a {genre.value} song with {mood.value} mood.
            Theme: {theme}
            
            Provide:
            1. Melodic patterns and motifs
            2. Rhythmic suggestions
            3. Harmony considerations
            4. Creative elements unique to {genre.value}
            """
            
            melody_result = await self.provider_service.call_model_by_task(
                task_type="music_generation",
                messages=[{"role": "user", "content": melody_prompt}]
            )
            
            concepts["melody"] = melody_result.get("content", "")
            
            # Lyrical concepts (if applicable)
            if genre in [Genre.LOFI, Genre.HYPERPOP, Genre.HIPHOP]:
                lyrics_prompt = f"""
                Write lyrical concepts and themes for a {genre.value} song with {mood.value} mood.
                Theme: {theme}
                Duration: {duration} seconds
                
                Provide:
                1. Main themes and storytelling approach
                2. Key phrases and hooks
                3. Rhyme scheme suggestions
                4. Vocal style recommendations
                """
                
                lyrics_result = await self.provider_service.call_model_by_task(
                    task_type="lyrical_composition",
                    messages=[{"role": "user", "content": lyrics_prompt}]
                )
                
                concepts["lyrics"] = lyrics_result.get("content", "")
            
            # Production techniques (using deep analysis)
            production_prompt = f"""
            Suggest production techniques for a {genre.value} song with {mood.value} mood.
            Theme: {theme}
            
            Provide:
            1. Sound design recommendations
            2. Mixing and mastering tips
            3. Effects and processing suggestions
            4. Genre-specific production techniques
            """
            
            production_result = await self.provider_service.call_model_by_task(
                task_type="deep_analysis",
                messages=[{"role": "user", "content": production_prompt}]
            )
            
            concepts["production"] = production_result.get("content", "")
            
            logger.info(f"Music concepts generated successfully")
            return {
                "success": True,
                "concepts": concepts,
                "genre": genre.value,
                "mood": mood.value,
                "theme": theme,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Music concepts generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "concepts": {}
            }
    
    async def enhance_music_prompt(
        self, 
        base_prompt: str,
        genre: Genre, 
        mood: Mood,
        technical_specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance music generation prompt using AI insights"""
        try:
            logger.info(f"Enhancing prompt for {genre} {mood}")
            
            enhancement_prompt = f"""
            Enhance this music generation prompt for optimal results:
            
            Original Prompt: {base_prompt}
            Genre: {genre.value}
            Mood: {mood.value}
            Technical Specs: {technical_specs}
            
            Provide an enhanced version that:
            1. Includes specific musical elements and techniques
            2. Incorporates genre-specific characteristics
            3. Adds technical details for better generation
            4. Maintains the original creative intent
            
            Return only the enhanced prompt text.
            """
            
            result = await self.provider_service.call_model_by_task(
                task_type="music_generation",
                messages=[{"role": "user", "content": enhancement_prompt}]
            )
            
            enhanced_prompt = result.get("content", base_prompt)
            
            logger.info(f"Prompt enhanced successfully")
            return {
                "success": True,
                "original_prompt": base_prompt,
                "enhanced_prompt": enhanced_prompt,
                "improvements": self._analyze_prompt_improvements(base_prompt, enhanced_prompt)
            }
            
        except Exception as e:
            logger.error(f"Prompt enhancement failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "enhanced_prompt": base_prompt
            }
    
    async def analyze_music_trends(self, genre: Genre, mood: Mood) -> Dict[str, Any]:
        """Analyze current music trends using web search and AI analysis"""
        try:
            logger.info(f"Analyzing trends for {genre} {mood}")
            
            # Search for current trends
            search_query = f"current {genre.value} music trends 2026 {mood.value}"
            search_result = await self.provider_service.call_web_search(search_query, max_results=5)
            
            if not search_result.get("success"):
                logger.warning("Web search failed, using general knowledge")
            
            # Analyze trends with AI
            analysis_prompt = f"""
            Based on the search results for "{search_query}", analyze current music trends:
            
            Search Results: {search_result.get('data', {})}
            
            Provide:
            1. Current popular trends in {genre.value} music
            2. Production techniques gaining popularity
            3. Emerging subgenres or styles
            4. Recommendations for creating contemporary {mood.value} {genre.value} music
            """
            
            analysis_result = await self.provider_service.call_model_by_task(
                task_type="deep_analysis",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            logger.info(f"Trend analysis completed")
            return {
                "success": True,
                "genre": genre.value,
                "mood": mood.value,
                "trends_analysis": analysis_result.get("content", ""),
                "search_data": search_result.get("data", {}),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_music_theory_advice(
        self, 
        musical_ideas: str,
        complexity_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """Generate music theory advice and suggestions"""
        try:
            logger.info(f"Generating music theory advice (complexity: {complexity_level})")
            
            theory_prompt = f"""
            Provide music theory advice and analysis for these musical ideas:
            
            Musical Ideas: {musical_ideas}
            Complexity Level: {complexity_level}
            
            Provide:
            1. Music theory concepts that apply
            2. Harmonic analysis and suggestions
            3. Melodic development techniques
            4. Rhythmic considerations
            5. Structural recommendations
            6. Practical examples and exercises
            """
            
            result = await self.provider_service.call_model_by_task(
                task_type="music_theory",
                messages=[{"role": "user", "content": theory_prompt}]
            )
            
            logger.info(f"Music theory advice generated")
            return {
                "success": True,
                "advice": result.get("content", ""),
                "complexity_level": complexity_level,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Music theory advice failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_optimal_generation_parameters(
        self,
        genre: Genre,
        mood: Mood,
        duration: int,
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get optimal parameters for music generation"""
        try:
            logger.info(f"Getting optimal parameters for {genre} {mood}")
            
            # Use pattern recognition model to determine best parameters
            param_prompt = f"""
            Determine optimal music generation parameters:
            
            Genre: {genre.value}
            Mood: {mood.value}
            Duration: {duration} seconds
            User Preferences: {user_preferences}
            
            Recommend optimal:
            1. Tempo (BPM)
            2. Musical key
            3. Time signature
            4. Primary instrumentation
            5. Production style
            6. any special effects or techniques
            
            Provide these as a JSON structure with specific recommendations.
            """
            
            result = await self.provider_service.call_model_by_task(
                task_type="pattern_recognition",
                messages=[{"role": "user", "content": param_prompt}]
            )
            
            # Parse the recommended parameters
            parameters = self._parse_parameters(result.get("content", "{}"))
            
            logger.info(f"Optimal parameters generated")
            return {
                "success": True,
                "parameters": parameters,
                "reasoning": result.get("content", ""),
                "genre": genre.value,
                "mood": mood.value
            }
            
        except Exception as e:
            logger.error(f"Parameter generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "parameters": {}
            }
    
    def _analyze_prompt_improvements(self, original: str, enhanced: str) -> List[str]:
        """Analyze differences between original and enhanced prompts"""
        improvements = []
        
        # Simple analysis based on length and content differences
        if len(enhanced) > len(original) * 1.5:
            improvements.append("Added more detailed descriptions")
        
        # Check for musical terms
        musical_terms = ["rhythm", "melody", "harmony", "tempo", "key", "scale", "chord", "progression"]
        for term in musical_terms:
            if term in enhanced.lower() and term not in original.lower():
                improvements.append(f"Added {term} considerations")
        
        # Check for technical specifications
        tech_terms = ["bpm", "hz", "khz", "stereo", "mono", "layer", "mix"]
        for term in tech_terms:
            if term in enhanced.lower() and term not in original.lower():
                improvements.append(f"Added {term} specifications")
        
        return improvements if improvements else ["General improvements and clarifications"]
    
    def _parse_parameters(self, content: str) -> Dict[str, Any]:
        """Parse parameter recommendations from AI response"""
        import json
        import re
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{[^}]*\}', content)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback to basic parameter extraction
        parameters = {
            "tempo": 120,
            "key": "C",
            "time_signature": "4/4",
            "instrumentation": ["piano", "drums", "bass"],
            "production_style": "modern",
            "effects": []
        }
        
        # Extract tempo if mentioned
        tempo_match = re.search(r'(\d+)\s*bpm', content.lower())
        if tempo_match:
            parameters["tempo"] = int(tempo_match.group(1))
        
        # Extract key if mentioned
        key_match = re.search(r'key\s*[:\-]?\s*([A-G][#b]?)', content.lower())
        if key_match:
            parameters["key"] = key_match.group(1).upper()
        
        return parameters

# Global service instance
music_ai_service = MusicAIService()