from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import aiohttp

from ..services.database import check_database_connection, check_redis_connection
from ..services.heartmula import heartmula_service
from ..utils.logger import get_logger

logger = get_logger("health_service")

class HealthService:
    """Service for health monitoring"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_detailed_health(self) -> Dict[str, Any]:
        """Get detailed health status of all services"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "auto-music-producer-ai",
                "version": "1.0.0",
                "dependencies": {}
            }
            
            # Check database
            db_healthy = check_database_connection()
            health_status["dependencies"]["database"] = {
                "status": "healthy" if db_healthy else "unhealthy",
                "connected": db_healthy
            }
            
            # Check Redis
            redis_healthy = check_redis_connection()
            health_status["dependencies"]["redis"] = {
                "status": "healthy" if redis_healthy else "unhealthy",
                "connected": redis_healthy
            }
            
            # Check HeartMuLa API
            try:
                models = await heartmula_service.get_available_models()
                health_status["dependencies"]["heartmula"] = {
                    "status": "healthy",
                    "connected": True,
                    "models_count": len(models.get("models", []))
                }
            except Exception as e:
                health_status["dependencies"]["heartmula"] = {
                    "status": "unhealthy",
                    "connected": False,
                    "error": str(e)
                }
            
            # Check external APIs (OpenAI, Anthropic)
            health_status["dependencies"]["openai"] = await self._check_openai()
            health_status["dependencies"]["anthropic"] = await self._check_anthropic()
            
            # Determine overall status
            all_healthy = all(
                dep["status"] == "healthy" 
                for dep in health_status["dependencies"].values()
            )
            health_status["status"] = "healthy" if all_healthy else "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "auto-music-producer-ai",
                "error": str(e)
            }
    
    async def check_dependencies(self) -> Dict[str, Any]:
        """Check all external dependencies"""
        try:
            dependencies = {
                "database": check_database_connection(),
                "redis": check_redis_connection(),
                "heartmula": await self._check_heartmula(),
                "openai": await self._check_openai(),
                "anthropic": await self._check_anthropic()
            }
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "dependencies": dependencies,
                "healthy": all(dependencies.values())
            }
            
        except Exception as e:
            logger.error(f"Dependency check error: {str(e)}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "dependencies": {},
                "healthy": False,
                "error": str(e)
            }
    
    async def readiness_check(self) -> Dict[str, Any]:
        """Readiness check for Kubernetes/Liveness"""
        try:
            # Check critical dependencies
            db_ok = check_database_connection()
            redis_ok = check_redis_connection()
            
            # For readiness, we need database and Redis
            ready = db_ok and redis_ok
            
            return {
                "ready": ready,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": {
                    "database": db_ok,
                    "redis": redis_ok
                }
            }
            
        except Exception as e:
            logger.error(f"Readiness check error: {str(e)}")
            return {
                "ready": False,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def _check_heartmula(self) -> bool:
        """Check HeartMuLa API connectivity"""
        try:
            models = await heartmula_service.get_available_models()
            return len(models.get("models", [])) > 0
        except Exception as e:
            logger.warning(f"HeartMuLa check failed: {str(e)}")
            return False
    
    async def _check_openai(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity"""
        try:
            # Simple check - we'll implement this when OpenAI integration is added
            return {
                "status": "not_configured",
                "connected": False,
                "note": "OpenAI integration not yet implemented"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
    
    async def _check_anthropic(self) -> Dict[str, Any]:
        """Check Anthropic API connectivity"""
        try:
            # Simple check - we'll implement this when Anthropic integration is added
            return {
                "status": "not_configured", 
                "connected": False,
                "note": "Anthropic integration not yet implemented"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }