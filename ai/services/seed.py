"""Seed the database with default presets and provider configs."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from loguru import logger
from models.database import AIProvider, LofiPreset
from services.db import get_engine


async def seed():
    engine = await get_engine()
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Check if already seeded
        from sqlalchemy import select
        existing = (await session.execute(select(LofiPreset))).scalars().first()
        if existing:
            logger.info("Database already seeded, skipping.")
            await engine.dispose()
            return

        # --- Lofi Presets ---
        presets = [
            LofiPreset(
                name="Lo-Fi Chill Study",
                genre="lofi", mood="chill",
                tempo_min=70, tempo_max=85,
                key_signature="C major",
                instruments=["piano", "vinyl crackle", "soft drums"],
                tags="lo-fi,chill,study,piano,vinyl,ambient",
                prompt_template="A {mood} lo-fi beat with {instruments}, perfect for studying",
                is_default=True, icon="📚", display_order=1,
            ),
            LofiPreset(
                name="Hyper Pop Banger",
                genre="hyper-pop", mood="energetic",
                tempo_min=130, tempo_max=160,
                key_signature="C minor",
                instruments=["synth", "808 bass", "distorted vocals"],
                tags="hyper-pop,energetic,synth,808,bass,punchy",
                prompt_template="An energetic hyper-pop track with {instruments}",
                is_default=True, icon="⚡", display_order=2,
            ),
            LofiPreset(
                name="Ambient Dream",
                genre="ambient", mood="dreamy",
                tempo_min=60, tempo_max=80,
                key_signature="D minor",
                instruments=["pad synth", "reverb guitar", "nature sounds"],
                tags="ambient,dreamy,pad,reverb,ethereal",
                prompt_template="A {mood} ambient soundscape with {instruments}",
                is_default=True, icon="🌙", display_order=3,
            ),
            LofiPreset(
                name="Synthwave Night Drive",
                genre="synthwave", mood="dark",
                tempo_min=100, tempo_max=120,
                key_signature="A minor",
                instruments=["analog synth", "drum machine", "bass"],
                tags="synthwave,retro,80s,analog,bass,night",
                prompt_template="A {mood} synthwave track with {instruments}, like an 80s night drive",
                is_default=True, icon="🌆", display_order=4,
            ),
            LofiPreset(
                name="Trap Heavy",
                genre="trap", mood="dark",
                tempo_min=140, tempo_max=160,
                key_signature="G minor",
                instruments=["808", "hi-hats", "synth lead"],
                tags="trap,dark,808,hi-hats,bass-heavy",
                prompt_template="A {mood} trap beat with {instruments}",
                is_default=True, icon="🔥", display_order=5,
            ),
            LofiPreset(
                name="Chillhop Cafe",
                genre="chillhop", mood="upbeat",
                tempo_min=80, tempo_max=95,
                key_signature="F major",
                instruments=["jazz guitar", "rhodes", "boom bap drums"],
                tags="chillhop,jazz,guitar,rhodes,cafe,relaxed",
                prompt_template="A {mood} chillhop vibe with {instruments}, like a sunny cafe",
                is_default=True, icon="☕", display_order=6,
            ),
            LofiPreset(
                name="Vaporwave Mall",
                genre="vaporwave", mood="dreamy",
                tempo_min=70, tempo_max=100,
                key_signature="E major",
                instruments=["slowed synth", "vocal chops", "reverb"],
                tags="vaporwave,aesthetic,slowed,mall,reverb,dreamy",
                prompt_template="A {mood} vaporwave track with {instruments}, nostalgic mall vibes",
                is_default=True, icon="🌴", display_order=7,
            ),
        ]

        # --- AI Providers ---
        providers = [
            AIProvider(
                name="heartmula",
                display_name="HeartMuLa",
                provider_type="music",
                api_base_url="http://localhost:7860",
                models=["heartmula-v1"],
                default_model="heartmula-v1",
                supports_music_generation=True,
                supports_lyrics_enhancement=True,
                description="Open-source AI music generation engine",
                icon_url="🎵",
            ),
            AIProvider(
                name="openrouter",
                display_name="OpenRouter",
                provider_type="llm",
                api_base_url="https://openrouter.ai/api/v1",
                models=["glm-4.5-air", "nemotron"],
                default_model="glm-4.5-air",
                supports_lyrics_enhancement=True,
                description="Multi-model LLM provider for prompt enhancement",
                icon_url="🤖",
            ),
        ]

        session.add_all(presets + providers)
        await session.commit()
        logger.info(f"Seeded {len(presets)} presets and {len(providers)} providers")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
