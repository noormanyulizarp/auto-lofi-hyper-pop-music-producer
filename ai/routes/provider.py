"""Provider dashboard routes — CRUD for AI provider management."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.database import get_db
from models.database import AIProvider

router = APIRouter()


# ─── Request/Response Models ───

class ProviderCreate(BaseModel):
    name: str
    display_name: str
    provider_type: str = "llm"  # llm, music, video
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    auth_header_format: str = "Bearer {api_key}"
    models: List[Dict[str, str]] = []
    default_model: Optional[str] = None
    max_tokens: int = 32768
    temperature: float = 0.7
    timeout_seconds: int = 300
    supports_music_generation: bool = False
    supports_lyrics_enhancement: bool = False
    supports_audio_analysis: bool = False
    description: Optional[str] = None
    icon_url: Optional[str] = None
    config_metadata: Dict[str, Any] = {}


class ProviderUpdate(BaseModel):
    display_name: Optional[str] = None
    provider_type: Optional[str] = None
    status: Optional[str] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    auth_header_format: Optional[str] = None
    models: Optional[List[Dict[str, str]]] = None
    default_model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    timeout_seconds: Optional[int] = None
    supports_music_generation: Optional[bool] = None
    supports_lyrics_enhancement: Optional[bool] = None
    supports_audio_analysis: Optional[bool] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    config_metadata: Optional[Dict[str, Any]] = None


# ─── Endpoints ───

@router.get("/providers")
async def list_providers(
    provider_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all configured AI providers with optional filters."""
    query = db.query(AIProvider)

    if provider_type:
        query = query.filter(AIProvider.provider_type == provider_type)
    if status:
        query = query.filter(AIProvider.status == status)

    providers = query.order_by(AIProvider.created_at).all()
    return {
        "total": len(providers),
        "providers": [p.to_dict() for p in providers],
    }


@router.get("/providers/{provider_name}")
async def get_provider(provider_name: str, db: Session = Depends(get_db)):
    """Get detailed info for a specific provider."""
    provider = db.query(AIProvider).filter(AIProvider.name == provider_name).first()
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")
    return provider.to_dict()


@router.post("/providers")
async def create_provider(data: ProviderCreate, db: Session = Depends(get_db)):
    """Add a new AI provider."""
    # Check for duplicate name
    existing = db.query(AIProvider).filter(AIProvider.name == data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Provider '{data.name}' already exists")

    provider = AIProvider(
        name=data.name,
        display_name=data.display_name,
        provider_type=data.provider_type,
        api_key=data.api_key,
        api_base_url=data.api_base_url,
        auth_header_format=data.auth_header_format,
        models=data.models,
        default_model=data.default_model,
        max_tokens=data.max_tokens,
        temperature=data.temperature,
        timeout_seconds=data.timeout_seconds,
        supports_music_generation=data.supports_music_generation,
        supports_lyrics_enhancement=data.supports_lyrics_enhancement,
        supports_audio_analysis=data.supports_audio_analysis,
        description=data.description,
        icon_url=data.icon_url,
        config_metadata=data.config_metadata,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)

    logger.info(f"Created AI provider: {data.name}")
    return {"message": "Provider created", "provider": provider.to_dict()}


@router.patch("/providers/{provider_name}")
async def update_provider(
    provider_name: str,
    data: ProviderUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing AI provider configuration."""
    provider = db.query(AIProvider).filter(AIProvider.name == provider_name).first()
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(provider, key, value)

    provider.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(provider)

    logger.info(f"Updated AI provider: {provider_name} — fields: {list(update_data.keys())}")
    return {"message": "Provider updated", "provider": provider.to_dict()}


@router.delete("/providers/{provider_name}")
async def delete_provider(provider_name: str, db: Session = Depends(get_db)):
    """Remove an AI provider."""
    provider = db.query(AIProvider).filter(AIProvider.name == provider_name).first()
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    db.delete(provider)
    db.commit()

    logger.info(f"Deleted AI provider: {provider_name}")
    return {"message": f"Provider '{provider_name}' deleted"}


@router.post("/providers/{provider_name}/test")
async def test_provider(provider_name: str, db: Session = Depends(get_db)):
    """Test connection to an AI provider."""
    provider = db.query(AIProvider).filter(AIProvider.name == provider_name).first()
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    import httpx

    if not provider.api_base_url:
        return {"status": "error", "message": "No API base URL configured"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {}
            if provider.api_key:
                headers["Authorization"] = provider.auth_header_format.format(api_key=provider.api_key)

            response = await client.get(
                f"{provider.api_base_url.rstrip('/')}/models",
                headers=headers,
            )

        is_ok = response.status_code < 500
        provider.last_used_at = datetime.utcnow()
        provider.total_requests = (provider.total_requests or 0) + 1
        if is_ok:
            provider.successful_requests = (provider.successful_requests or 0) + 1
            provider.status = "active"
        else:
            provider.failed_requests = (provider.failed_requests or 0) + 1
            provider.last_error = f"HTTP {response.status_code}"
        db.commit()

        return {
            "status": "ok" if is_ok else "error",
            "http_status": response.status_code,
            "message": "Connection successful" if is_ok else f"HTTP {response.status_code}",
        }
    except Exception as e:
        provider.failed_requests = (provider.failed_requests or 0) + 1
        provider.last_error = str(e)
        provider.status = "error"
        db.commit()

        return {"status": "error", "message": str(e)}


@router.get("/providers/stats/summary")
async def provider_stats(db: Session = Depends(get_db)):
    """Get usage statistics for all providers."""
    providers = db.query(AIProvider).all()
    return {
        "total_providers": len(providers),
        "by_type": {
            pt: len([p for p in providers if p.provider_type == pt])
            for pt in set(p.provider_type for p in providers)
        },
        "by_status": {
            s: len([p for p in providers if p.status == s])
            for s in set(p.status for p in providers)
        },
        "total_requests": sum(p.total_requests or 0 for p in providers),
    }
