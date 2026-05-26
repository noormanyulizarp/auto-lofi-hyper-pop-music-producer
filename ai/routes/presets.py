"""Preset routes — lofi / genre preset CRUD endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from sqlalchemy.orm import Session
from typing import Optional

from services.database import get_db
from models.database import LofiPreset

router = APIRouter()


@router.get("/presets")
async def list_presets(
    genre: Optional[str] = None,
    mood: Optional[str] = None,
    defaults_only: bool = False,
    db: Session = Depends(get_db),
):
    """List all genre/lofi presets, optionally filtered."""
    query = db.query(LofiPreset)

    if genre:
        query = query.filter(LofiPreset.genre == genre)
    if mood:
        query = query.filter(LofiPreset.mood == mood)
    if defaults_only:
        query = query.filter(LofiPreset.is_default == True)

    presets = query.order_by(LofiPreset.display_order).all()
    return {
        "total": len(presets),
        "presets": [p.to_dict() for p in presets],
    }


@router.get("/presets/{preset_id}")
async def get_preset(preset_id: str, db: Session = Depends(get_db)):
    """Get a single preset by ID."""
    preset = db.query(LofiPreset).filter(LofiPreset.id == preset_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset.to_dict()


@router.get("/presets/genres/list")
async def list_genres_with_presets(db: Session = Depends(get_db)):
    """List all genres that have presets, with counts."""
    from sqlalchemy import func
    results = (
        db.query(LofiPreset.genre, func.count(LofiPreset.id))
        .group_by(LofiPreset.genre)
        .all()
    )
    return {
        "genres": [
            {"genre": genre, "preset_count": count}
            for genre, count in results
        ]
    }
