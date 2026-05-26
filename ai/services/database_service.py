from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
from loguru import logger
import json
from datetime import datetime

from ..models.database import Base, MusicGeneration, VideoAnalysis, LearningPattern
from ..config.settings import DATABASE_URL, DEBUG

class DatabaseService:
    """Service for database operations with AI-enhanced music data"""
    
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            echo=DEBUG,
            pool_pre_ping=True,
            pool_recycle=300
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self.create_tables()
        
        logger.info("Database service initialized")
    
    def create_tables(self):
        """Create database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # Music Generation Operations
    def create_music_generation(self, generation_data: Dict[str, Any]) -> MusicGeneration:
        """Create a new music generation record"""
        session = self.get_session()
        try:
            generation = MusicGeneration(**generation_data)
            session.add(generation)
            session.commit()
            session.refresh(generation)
            
            logger.info(f"Music generation record created: {generation.task_id}")
            return generation
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create music generation: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_music_generation(self, task_id: str) -> Optional[MusicGeneration]:
        """Get music generation by task ID"""
        session = self.get_session()
        try:
            generation = session.query(MusicGeneration).filter(
                MusicGeneration.task_id == task_id
            ).first()
            return generation
        except SQLAlchemyError as e:
            logger.error(f"Failed to get music generation: {str(e)}")
            return None
        finally:
            session.close()
    
    def update_music_generation(self, task_id: str, update_data: Dict[str, Any]) -> Optional[MusicGeneration]:
        """Update music generation record"""
        session = self.get_session()
        try:
            generation = session.query(MusicGeneration).filter(
                MusicGeneration.task_id == task_id
            ).first()
            
            if not generation:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(generation, key):
                    setattr(generation, key, value)
            
            generation.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(generation)
            
            logger.info(f"Music generation updated: {task_id}")
            return generation
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update music generation: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_user_generations(self, user_id: str, limit: int = 20, offset: int = 0) -> List[MusicGeneration]:
        """Get user's music generation history"""
        session = self.get_session()
        try:
            generations = session.query(MusicGeneration).filter(
                MusicGeneration.user_id == user_id
            ).order_by(MusicGeneration.created_at.desc()).offset(offset).limit(limit).all()
            
            return generations
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get user generations: {str(e)}")
            return []
        finally:
            session.close()
    
    def delete_music_generation(self, task_id: str) -> bool:
        """Delete music generation record"""
        session = self.get_session()
        try:
            generation = session.query(MusicGeneration).filter(
                MusicGeneration.task_id == task_id
            ).first()
            
            if not generation:
                return False
            
            session.delete(generation)
            session.commit()
            
            logger.info(f"Music generation deleted: {task_id}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to delete music generation: {str(e)}")
            return False
        finally:
            session.close()
    
    # Video Analysis Operations
    def create_video_analysis(self, analysis_data: Dict[str, Any]) -> VideoAnalysis:
        """Create a new video analysis record"""
        session = self.get_session()
        try:
            analysis = VideoAnalysis(**analysis_data)
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
            
            logger.info(f"Video analysis record created: {analysis.task_id}")
            return analysis
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create video analysis: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_video_analysis(self, task_id: str) -> Optional[VideoAnalysis]:
        """Get video analysis by task ID"""
        session = self.get_session()
        try:
            analysis = session.query(VideoAnalysis).filter(
                VideoAnalysis.task_id == task_id
            ).first()
            return analysis
        except SQLAlchemyError as e:
            logger.error(f"Failed to get video analysis: {str(e)}")
            return None
        finally:
            session.close()
    
    def update_video_analysis(self, task_id: str, update_data: Dict[str, Any]) -> Optional[VideoAnalysis]:
        """Update video analysis record"""
        session = self.get_session()
        try:
            analysis = session.query(VideoAnalysis).filter(
                VideoAnalysis.task_id == task_id
            ).first()
            
            if not analysis:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(analysis, key):
                    setattr(analysis, key, value)
            
            analysis.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(analysis)
            
            logger.info(f"Video analysis updated: {task_id}")
            return analysis
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update video analysis: {str(e)}")
            return None
        finally:
            session.close()
    
    # Learning Pattern Operations
    def create_learning_pattern(self, pattern_data: Dict[str, Any]) -> LearningPattern:
        """Create a new learning pattern record"""
        session = self.get_session()
        try:
            pattern = LearningPattern(**pattern_data)
            session.add(pattern)
            session.commit()
            session.refresh(pattern)
            
            logger.info(f"Learning pattern created: {pattern.name}")
            return pattern
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create learning pattern: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_learning_patterns(
        self, 
        pattern_type: Optional[str] = None,
        genre: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 50
    ) -> List[LearningPattern]:
        """Get learning patterns with optional filtering"""
        session = self.get_session()
        try:
            query = session.query(LearningPattern)
            
            if pattern_type:
                query = query.filter(LearningPattern.pattern_type == pattern_type)
            
            if difficulty:
                query = query.filter(LearningPattern.difficulty_level == difficulty)
            
            # Handle genre filtering (JSON field)
            if genre:
                query = query.filter(LearningPattern.applicable_genres.contains([genre]))
            
            # Filter by public patterns
            query = query.filter(LearningPattern.is_public == True)
            
            # Order by usage count and confidence score
            query = query.order_by(
                LearningPattern.usage_count.desc(),
                LearningPattern.confidence_score.desc()
            ).limit(limit)
            
            patterns = query.all()
            return patterns
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get learning patterns: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_learning_pattern(self, pattern_id: str) -> Optional[LearningPattern]:
        """Get learning pattern by ID"""
        session = self.get_session()
        try:
            pattern = session.query(LearningPattern).filter(
                LearningPattern.id == pattern_id
            ).first()
            return pattern
        except SQLAlchemyError as e:
            logger.error(f"Failed to get learning pattern: {str(e)}")
            return None
        finally:
            session.close()
    
    def update_pattern_usage(self, pattern_id: str, success: bool = True) -> bool:
        """Update pattern usage statistics"""
        session = self.get_session()
        try:
            pattern = session.query(LearningPattern).filter(
                LearningPattern.id == pattern_id
            ).first()
            
            if not pattern:
                return False
            
            # Update usage statistics
            pattern.usage_count += 1
            pattern.last_used_at = datetime.utcnow()
            
            # Update success rate (simplified)
            if pattern.success_rate is None:
                pattern.success_rate = 1.0 if success else 0.0
            else:
                # Simple moving average
                pattern.success_rate = (pattern.success_rate * 0.9) + (1.0 if success else 0.0) * 0.1
            
            session.commit()
            
            logger.info(f"Pattern usage updated: {pattern.name}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update pattern usage: {str(e)}")
            return False
        finally:
            session.close()
    
    # AI Enhancement Integration
    def save_ai_enhanced_generation(
        self, 
        task_id: str, 
        enhanced_data: Dict[str, Any]
    ) -> Optional[MusicGeneration]:
        """Save AI-enhanced music generation data"""
        try:
            # Extract relevant AI data
            ai_data = {
                "enhanced_prompt": enhanced_data.get("enhanced_prompt"),
                "ai_enhanced": True,
                "ai_concepts": enhanced_data.get("ai_concepts"),
                "optimal_parameters": enhanced_data.get("optimal_parameters"),
                "trend_analysis": enhanced_data.get("trend_analysis"),
                "confidence_score": enhanced_data.get("confidence_score", 0.0)
            }
            
            return self.update_music_generation(task_id, ai_data)
            
        except Exception as e:
            logger.error(f"Failed to save AI enhanced generation: {str(e)}")
            return None
    
    def save_video_analysis_results(
        self, 
        task_id: str, 
        analysis_results: Dict[str, Any]
    ) -> Optional[VideoAnalysis]:
        """Save video analysis results with AI enhancements"""
        try:
            # Prepare analysis data
            analysis_data = {
                "status": "completed",
                "progress": 100.0,
                "transcript": analysis_results.get("transcript"),
                "audio_features": analysis_results.get("audio_features"),
                "musical_elements": analysis_results.get("musical_elements"),
                "learned_patterns": analysis_results.get("learned_patterns"),
                "confidence_score": analysis_results.get("confidence_score", 0.0),
                "completed_at": datetime.utcnow()
            }
            
            analysis = self.update_video_analysis(task_id, analysis_data)
            
            # If learned patterns exist, save them to the patterns table
            if analysis and analysis_results.get("learned_patterns"):
                self._extract_and_save_patterns(
                    task_id, 
                    analysis_results["learned_patterns"],
                    analysis.video_title,
                    analysis.focus_type
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to save video analysis results: {str(e)}")
            return None
    
    def _extract_and_save_patterns(
        self, 
        source_id: str, 
        learned_patterns: List[Dict[str, Any]],
        video_title: str,
        focus_type: str
    ):
        """Extract and save learned patterns from video analysis"""
        try:
            session = self.get_session()
            
            for pattern_data in learned_patterns:
                # Create pattern record
                pattern = LearningPattern(
                    pattern_type=focus_type,
                    name=f"{video_title[:50]} - Pattern",
                    description=pattern_data.get("description", ""),
                    confidence_score=pattern_data.get("confidence", 0.5),
                    pattern_data=pattern_data,
                    application_guide=pattern_data.get("application", ""),
                    variations=pattern_data.get("variations", []),
                    applicable_genres=pattern_data.get("genres", ["lofi", "chill"]),
                    difficulty_level=pattern_data.get("skill_level", "intermediate"),
                    source_type="video_analysis",
                    source_id=source_id,
                    source_analysis=pattern_data.get("source_analysis", "")
                )
                
                session.add(pattern)
            
            session.commit()
            logger.info(f"Saved {len(learned_patterns)} patterns from video analysis")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save patterns: {str(e)}")
        finally:
            session.close()
    
    # Analytics and Reporting
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics and analytics"""
        session = self.get_session()
        try:
            # Music generation stats
            total_generations = session.query(MusicGeneration).filter(
                MusicGeneration.user_id == user_id
            ).count()
            
            completed_generations = session.query(MusicGeneration).filter(
                MusicGeneration.user_id == user_id,
                MusicGeneration.status == "completed"
            ).count()
            
            # Video analysis stats
            total_analyses = session.query(VideoAnalysis).filter(
                VideoAnalysis.user_id == user_id
            ).count()
            
            completed_analyses = session.query(VideoAnalysis).filter(
                VideoAnalysis.user_id == user_id,
                VideoAnalysis.status == "completed"
            ).count()
            
            # Average quality metrics
            avg_confidence = session.query(
                func.avg(MusicGeneration.confidence_score)
            ).filter(
                MusicGeneration.user_id == user_id,
                MusicGeneration.confidence_score.isnot(None)
            ).scalar() or 0.0
            
            return {
                "total_generations": total_generations,
                "completed_generations": completed_generations,
                "generation_success_rate": (completed_generations / total_generations * 100) if total_generations > 0 else 0,
                "total_analyses": total_analyses,
                "completed_analyses": completed_analyses,
                "analysis_success_rate": (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0,
                "average_confidence_score": avg_confidence,
                "ai_enhanced_generations": session.query(MusicGeneration).filter(
                    MusicGeneration.user_id == user_id,
                    MusicGeneration.ai_enhanced == True
                ).count()
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get user statistics: {str(e)}")
            return {}
        finally:
            session.close()

# Global service instance
database_service = DatabaseService()

# Dependency for FastAPI
def get_db():
    """Database dependency for FastAPI routes"""
    session = database_service.get_session()
    try:
        yield session
    finally:
        session.close()