from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger

from ..services.database import get_db
from ..services.heartmula import heartmula_service
from ..services.music_ai_service import music_ai_service
from ..models.responses import (
    GenerateMusicRequest,
    MusicGenerationResponse,
    MusicGenerationStatus,
    GeneratedMusic,
    SuccessResponse,
    ErrorResponse,
    Genre,
    Mood,
    TaskStatus
)
from ..utils.logger import get_logger

router = APIRouter()
logger = get_logger("music_routes")

# In-memory task storage (in production, use Redis or database)
music_tasks = {}

@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(
    request: GenerateMusicRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate music using AI-enhanced HeartMuLa"""
    try:
        logger.info(f"AI-enhanced music generation request: {request.title} ({request.genre} {request.mood})")
        
        # Validate request
        if not request.title or len(request.title.strip()) == 0:
            raise HTTPException(status_code=400, detail="Title is required")
        
        if request.duration < 10 or request.duration > 600:
            raise HTTPException(
                status_code=400, 
                detail="Duration must be between 10 and 600 seconds"
            )
        
        if not request.prompt or len(request.prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Generate music concepts using AI
        concepts_result = await music_ai_service.generate_music_concepts(
            genre=request.genre,
            mood=request.mood,
            theme=request.title,
            duration=request.duration
        )
        
        if not concepts_result.get("success"):
            logger.error("Music concept generation failed - using original prompt")
            enhanced_prompt = request.prompt
        else:
            # Enhance the original prompt using AI concepts
            enhancement_result = await music_ai_service.enhance_music_prompt(
                base_prompt=request.prompt,
                genre=request.genre,
                mood=request.mood,
                technical_specs={
                    "duration": request.duration,
                    "tempo": request.tempo,
                    "key": request.key,
                    "instruments": request.instruments
                }
            )
            
            enhanced_prompt = enhancement_result.get("enhanced_prompt", request.prompt)
            
            # Get optimal parameters using AI
            param_result = await music_ai_service.get_optimal_generation_parameters(
                genre=request.genre,
                mood=request.mood,
                duration=request.duration,
                user_preferences={
                    "tempo": request.tempo,
                    "key": request.key,
                    "instruments": request.instruments
                }
            )
            
            # Use AI-optimized parameters if available
            if param_result.get("success"):
                optimal_params = param_result["parameters"]
                if not request.tempo and optimal_params.get("tempo"):
                    request.tempo = optimal_params["tempo"]
                if not request.key and optimal_params.get("key"):
                    request.key = optimal_params["key"]
                if not request.instruments and optimal_params.get("instrumentation"):
                    request.instruments = optimal_params["instrumentation"]
        
        # Update request with enhanced data
        enhanced_request = request.copy()
        enhanced_request.prompt = enhanced_prompt
        
        # Generate music using HeartMuLa
        response = await heartmula_service.generate_music(enhanced_request)
        
        # Store task with AI metadata
        if hasattr(response, 'task_id'):
            music_tasks[response.task_id] = {
                "task_id": response.task_id,
                "status": TaskStatus.PROCESSING,
                "original_request": request.dict(),
                "enhanced_prompt": enhanced_prompt,
                "ai_concepts": concepts_result.get("concepts", {}),
                "optimal_parameters": param_result.get("parameters", {}) if param_result.get("success") else {},
                "heartmula_response": response.dict() if hasattr(response, 'dict') else {},
                "created_at": background_tasks
            }
        
        # Add AI metadata to response
        response_dict = response.dict() if hasattr(response, 'dict') else {"task_id": response}
        response_dict["ai_enhanced"] = True
        response_dict["original_prompt"] = request.prompt
        response_dict["enhanced_prompt"] = enhanced_prompt
        response_dict["ai_concepts"] = concepts_result.get("concepts", {})
        response_dict["optimal_parameters"] = param_result.get("parameters", {}) if param_result.get("success") else {}
        
        logger.info(f"AI-enhanced music generation started: {response.task_id}")
        return response
        
    except Exception as e:
        logger.error(f"AI-enhanced music generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}", response_model=MusicGenerationStatus)
async def get_generation_status(task_id: str, db: Session = Depends(get_db)):
    """Get music generation status"""
    try:
        logger.info(f"Status request: {task_id}")
        
        if not task_id or len(task_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Task ID is required")
        
        # Check HeartMuLa status
        status = await heartmula_service.get_generation_status(task_id)
        
        logger.info(f"Generation status: {task_id} - {status.status}")
        return status
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{task_id}")
async def download_music(task_id: str, db: Session = Depends(get_db)):
    """Download generated music file"""
    try:
        logger.info(f"Download request: {task_id}")
        
        if not task_id or len(task_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Task ID is required")
        
        # Generate output path
        import os
        output_dir = "uploads/music"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{task_id}.mp3")
        
        # Download music
        file_path = await heartmula_service.download_generated_music(task_id, output_path)
        
        logger.info(f"Music downloaded: {file_path}")
        return {
            "success": True,
            "message": "Music downloaded successfully",
            "file_path": file_path,
            "download_url": f"/static/music/{task_id}.mp3"
        }
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_available_models(db: Session = Depends(get_db)):
    """Get available music generation models"""
    try:
        logger.info("Models request")
        
        models = await heartmula_service.get_available_models()
        
        logger.info(f"Available models: {len(models.get('models', []))}")
        return {
            "success": True,
            "message": "Available models retrieved",
            "data": models
        }
        
    except Exception as e:
        logger.error(f"Models error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metadata/{task_id}")
async def get_music_metadata(task_id: str, db: Session = Depends(get_db)):
    """Get music metadata"""
    try:
        logger.info(f"Metadata request: {task_id}")
        
        if not task_id or len(task_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Task ID is required")
        
        metadata = await heartmula_service.get_music_metadata(task_id)
        
        logger.info(f"Metadata retrieved: {task_id}")
        return {
            "success": True,
            "message": "Metadata retrieved",
            "data": metadata
        }
        
    except Exception as e:
        logger.error(f"Metadata error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generations", response_model=List[MusicGenerationStatus])
async def get_user_generations(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get user's music generation history"""
    try:
        logger.info(f"User generations request: {user_id}")
        
        if not user_id or len(user_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # TODO: Implement database query for user generations
        # For now, return empty list
        logger.info(f"Retrieved generations for user: {user_id}")
        return []
        
    except Exception as e:
        logger.error(f"Generations history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/generation/{task_id}")
async def delete_generation(task_id: str, db: Session = Depends(get_db)):
    """Delete a music generation"""
    try:
        logger.info(f"Delete generation request: {task_id}")
        
        if not task_id or len(task_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Task ID is required")
        
        # TODO: Implement database deletion
        # For now, just return success
        logger.info(f"Generation deleted: {task_id}")
        return {
            "success": True,
            "message": "Generation deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# New AI-enhanced endpoints

@router.get("/genres")
async def get_supported_genres():
    """Get supported music genres"""
    try:
        return {
            "success": True,
            "message": "Supported genres retrieved",
            "data": {
                "genres": [genre.value for genre in Genre],
                "descriptions": {
                    "lofi": "Low-fidelity, relaxed beats perfect for studying or relaxing",
                    "hyperpop": "Experimental, high-energy electronic pop with digital production",
                    "chillout": "Smooth, relaxing electronic music with atmospheric elements",
                    "ambient": "Atmospheric, texture-focused music creating an immersive environment",
                    "electronic": "Various styles of electronically produced music",
                    "hiphop": "Hip-hop and rap influenced beats with rhythmic elements",
                    "jazz": "Jazz-inspired compositions with improvisational elements",
                    "classical": "Classical music influences with orchestral elements"
                }
            }
        }
    except Exception as e:
        logger.error(f"Genres error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/moods")
async def get_supported_moods():
    """Get supported music moods"""
    try:
        return {
            "success": True,
            "message": "Supported moods retrieved",
            "data": {
                "moods": [mood.value for mood in Mood],
                "descriptions": {
                    "chill": "Relaxed, easy-going atmosphere",
                    "happy": "Uplifting, positive emotions",
                    "sad": "Melancholic, emotional depth",
                    "energetic": "High-energy, motivating feel",
                    "calm": "Peaceful, serene atmosphere",
                    "mysterious": "Intriguing, enigmatic mood",
                    "romantic": "Love-focused, emotional intimacy",
                    "intense": "Strong, powerful emotions"
                }
            }
        }
    except Exception as e:
        logger.error(f"Moods error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-concepts")
async def analyze_music_concepts(
    genre: Genre,
    mood: Mood,
    theme: str,
    duration: int = 30
):
    """Generate music concepts using AI without actual music generation"""
    try:
        logger.info(f"Music concepts analysis: {genre} {mood} - {theme}")
        
        result = await music_ai_service.generate_music_concepts(
            genre=genre,
            mood=mood,
            theme=theme,
            duration=duration
        )
        
        if result.get("success"):
            return SuccessResponse(
                success=True,
                message="Music concepts generated successfully",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Concept generation failed"))
            
    except Exception as e:
        logger.error(f"Concept analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trends")
async def analyze_music_trends(genre: Genre, mood: Mood):
    """Analyze current music trends using AI"""
    try:
        logger.info(f"Music trends analysis: {genre} {mood}")
        
        result = await music_ai_service.analyze_music_trends(genre, mood)
        
        if result.get("success"):
            return SuccessResponse(
                success=True,
                message="Music trends analyzed successfully",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Trend analysis failed"))
            
    except Exception as e:
        logger.error(f"Trend analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhance-prompt")
async def enhance_music_prompt(
    prompt: str,
    genre: Genre,
    mood: Mood,
    tempo: Optional[int] = None,
    key: Optional[str] = None,
    instruments: Optional[list] = None
):
    """Enhance music generation prompt using AI"""
    try:
        logger.info(f"Prompt enhancement: {genre} {mood}")
        
        result = await music_ai_service.enhance_music_prompt(
            base_prompt=prompt,
            genre=genre,
            mood=mood,
            technical_specs={
                "tempo": tempo,
                "key": key,
                "instruments": instruments
            }
        )
        
        if result.get("success"):
            return SuccessResponse(
                success=True,
                message="Prompt enhanced successfully",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Prompt enhancement failed"))
            
    except Exception as e:
        logger.error(f"Prompt enhancement error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimal-parameters")
async def get_optimal_parameters(
    genre: Genre,
    mood: Mood,
    duration: int,
    user_preferences: dict = {}
):
    """Get optimal music generation parameters using AI"""
    try:
        logger.info(f"Optimal parameters request: {genre} {mood}")
        
        result = await music_ai_service.get_optimal_generation_parameters(
            genre=genre,
            mood=mood,
            duration=duration,
            user_preferences=user_preferences
        )
        
        if result.get("success"):
            return SuccessResponse(
                success=True,
                message="Optimal parameters generated successfully",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Parameter generation failed"))
            
    except Exception as e:
        logger.error(f"Optimal parameters error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/theory-advice")
async def get_music_theory_advice(
    musical_ideas: str,
    complexity_level: str = "intermediate"
):
    """Get music theory advice using AI"""
    try:
        logger.info(f"Music theory advice request: {complexity_level}")
        
        result = await music_ai_service.generate_music_theory_advice(
            musical_ideas=musical_ideas,
            complexity_level=complexity_level
        )
        
        if result.get("success"):
            return SuccessResponse(
                success=True,
                message="Music theory advice generated successfully",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Theory advice failed"))
            
    except Exception as e:
        logger.error(f"Music theory advice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks")
async def list_music_tasks():
    """List all music generation tasks"""
    try:
        tasks_data = []
        
        for task_id, task in music_tasks.items():
            tasks_data.append({
                "task_id": task_id,
                "status": task["status"].value if hasattr(task["status"], "value") else str(task["status"]),
                "title": task["original_request"]["title"],
                "genre": task["original_request"]["genre"].value if hasattr(task["original_request"]["genre"], "value") else str(task["original_request"]["genre"]),
                "mood": task["original_request"]["mood"].value if hasattr(task["original_request"]["mood"], "value") else str(task["original_request"]["mood"]),
                "duration": task["original_request"]["duration"],
                "ai_enhanced": "enhanced_prompt" in task,
                "created_at": task.get("created_at")
            })
        
        return SuccessResponse(
            success=True,
            message="Music tasks retrieved successfully",
            data={"tasks": tasks_data, "total": len(tasks_data)}
        )
        
    except Exception as e:
        logger.error(f"Task listing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))