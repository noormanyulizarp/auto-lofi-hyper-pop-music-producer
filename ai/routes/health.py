from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..services.database import get_db
from ..services.health import HealthService
from ..models.responses import HealthResponse

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check"""
    return HealthResponse(
        status="healthy",
        service="auto-music-producer-ai",
        version="1.0.0",
        timestamp="now"
    )

@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with all services"""
    health_service = HealthService(db)
    return await health_service.get_detailed_health()

@router.get("/dependencies")
async def check_dependencies(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Check all external dependencies"""
    health_service = HealthService(db)
    return await health_service.check_dependencies()

@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Readiness check for Kubernetes/Liveness"""
    health_service = HealthService(db)
    return await health_service.readiness_check()