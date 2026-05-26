import httpx
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..config import settings
from ..models.responses import (
    GenerateMusicRequest, 
    MusicGenerationResponse,
    MusicGenerationStatus,
    TaskStatus
)

class HeartMuLaService:
    """HeartMuLa AI music generation service"""
    
    def __init__(self):
        self.api_key = settings.HEARTMULA_API_KEY
        self.base_url = settings.HEARTMULA_BASE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=300.0  # 5 minutes timeout
        )
        
    async def generate_music(self, request: GenerateMusicRequest) -> MusicGenerationResponse:
        """Generate music using HeartMuLa AI"""
        try:
            logger.info(f"Generating music: {request.title} - {request.genre}")
            
            # Prepare HeartMuLa request payload
            payload = {
                "title": request.title,
                "genre": request.genre.value,
                "mood": request.mood.value,
                "duration": request.duration,
                "prompt": request.prompt,
                "model": request.model,
                "tempo": request.tempo,
                "key": request.key,
                "instruments": request.instruments or []
            }
            
            # Make API call to HeartMuLa
            response = await self.client.post("/generate", json=payload)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Create response
            music_response = MusicGenerationResponse(
                task_id=data["task_id"],
                status=TaskStatus(data.get("status", "pending")),
                estimated_time=data.get("estimated_time"),
                message=data.get("message", "Music generation started successfully")
            )
            
            logger.info(f"Music generation started: {music_response.task_id}")
            return music_response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HeartMuLa API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"HeartMuLa API error: {e.response.status_code}")
            
        except Exception as e:
            logger.error(f"Music generation error: {str(e)}")
            raise Exception(f"Failed to generate music: {str(e)}")
    
    async def get_generation_status(self, task_id: str) -> MusicGenerationStatus:
        """Get music generation status"""
        try:
            logger.info(f"Checking generation status: {task_id}")
            
            response = await self.client.get(f"/status/{task_id}")
            response.raise_for_status()
            
            data = response.json()
            
            status = MusicGenerationStatus(
                task_id=task_id,
                status=TaskStatus(data.get("status", "pending")),
                progress=data.get("progress"),
                result_url=data.get("result_url"),
                error=data.get("error"),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"])
            )
            
            logger.info(f"Generation status: {task_id} - {status.status}")
            return status
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HeartMuLa status error: {e.response.status_code}")
            raise Exception(f"HeartMuLa API error: {e.response.status_code}")
            
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            raise Exception(f"Failed to get status: {str(e)}")
    
    async def download_generated_music(self, task_id: str, output_path: str) -> str:
        """Download generated music file"""
        try:
            logger.info(f"Downloading music: {task_id} to {output_path}")
            
            response = await self.client.get(f"/download/{task_id}")
            response.raise_for_status()
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Music downloaded successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            raise Exception(f"Failed to download music: {str(e)}")
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get available music generation models"""
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Models error: {str(e)}")
            raise Exception(f"Failed to get models: {str(e)}")
    
    async def get_music_metadata(self, task_id: str) -> Dict[str, Any]:
        """Get detailed metadata about generated music"""
        try:
            response = await self.client.get(f"/metadata/{task_id}")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Metadata error: {str(e)}")
            raise Exception(f"Failed to get metadata: {str(e)}")

# Global service instance
heartmula_service = HeartMuLaService()