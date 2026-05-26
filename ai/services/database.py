"""Database service — SQLite + SQLAlchemy with full seed data."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from loguru import logger
from typing import Generator
import os

from config import settings
from models.database import Base


# Sync engine for SQLite (StaticPool = single connection, thread-safe for SQLite)
engine = create_engine(
    settings.DATABASE_URL.replace("+aiosqlite", ""),
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Create all tables if they don't exist, then seed defaults."""
    db_path = settings.DATABASE_URL.split("///")[-1]
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    _seed_default_providers()
    _seed_lofi_presets()


# ─── Provider seed data (OpenRouter + HeartMuLa + GLM Z.ai Direct) ──────

def _build_openrouter_models():
    """All 8 free models from config.json."""
    return [
        {"id": "baidu/cobuddy:free",                  "name": "CoBuddy",           "specialty": "assistant"},
        {"id": "openai/gpt-oss-20b:free",             "name": "GPT-OSS 20B",       "specialty": "general"},
        {"id": "openai/gpt-oss-120b:free",            "name": "GPT-OSS 120B",      "specialty": "large_context"},
        {"id": "nvidia/nemotron-nano-9b-v2:free",      "name": "Nemotron 9B",       "specialty": "fast_response"},
        {"id": "nvidia/nemotron-3-nano-30b-a3b:free",  "name": "Nemotron 30B",      "specialty": "balanced"},
        {"id": "arcee-ai/trinity-large-thinking:free", "name": "Trinity Thinking",  "specialty": "complex_reasoning"},
        {"id": "nvidia/nemotron-3-super-120b-a12b:free","name": "Nemotron 120B",     "specialty": "deep_analysis"},
        {"id": "z-ai/glm-4.5-air:free",               "name": "GLM 4.5 Air",       "specialty": "music_friendly"},
    ]


def _build_glm_zai_models():
    """GLM models direct from Z.ai (Zhipu) — lower latency than OpenRouter."""
    return [
        {"id": "glm-4.5-air", "name": "GLM 4.5 Air", "specialty": "fast_llm"},
        {"id": "glm-4.5",     "name": "GLM 4.5",     "specialty": "balanced_llm"},
        {"id": "glm-4.7",     "name": "GLM 4.7",     "specialty": "complex_reasoning"},
    ]


def _seed_default_providers():
    """Insert AI providers if table is empty. API keys loaded from .env."""
    from models.database import AIProvider
    import os

    api_key = os.environ.get("OPENROUTER_API_KEY", "")

    db = SessionLocal()
    try:
        count = db.query(AIProvider).count()
        if count > 0:
            logger.info(f"Providers already seeded ({count} rows), skipping")
            return

        providers = [
            # ── OpenRouter (all 8 models) ──
            AIProvider(
                name="openrouter",
                display_name="OpenRouter",
                provider_type="llm",
                status="active",
                api_key=api_key,
                api_base_url="https://openrouter.ai/api/v1",
                auth_header_format="Bearer {api_key}",
                models=_build_openrouter_models(),
                default_model="baidu/cobuddy:free",
                max_tokens=32768,
                temperature=0.7,
                timeout_seconds=300,
                supports_music_generation=False,
                supports_lyrics_enhancement=True,
                supports_audio_analysis=True,
                description="8 free LLM models via OpenRouter — fallback chain for reliability",
                docs_url="https://openrouter.ai/docs",
                config_metadata={
                    "fallback_chain": [
                        "baidu/cobuddy:free",
                        "openai/gpt-oss-20b:free",
                        "nvidia/nemotron-nano-9b-v2:free",
                        "z-ai/glm-4.5-air:free",
                    ],
                    "task_routing": {
                        "music_generation": "z-ai/glm-4.5-air:free",
                        "lyrical_composition": "baidu/cobuddy:free",
                        "music_theory": "arcee-ai/trinity-large-thinking:free",
                        "pattern_recognition": "nvidia/nemotron-3-nano-30b-a3b:free",
                        "quick_ideas": "nvidia/nemotron-nano-9b-v2:free",
                        "deep_analysis": "nvidia/nemotron-3-super-120b-a12b:free",
                        "general": "openai/gpt-oss-20b:free",
                        "long_form": "openai/gpt-oss-120b:free",
                    },
                },
            ),

            # ── HeartMuLa (music generation) ──
            AIProvider(
                name="heartmula",
                display_name="HeartMuLa",
                provider_type="music",
                status="active",
                api_base_url="http://localhost:8000",
                auth_header_format="Bearer {api_key}",
                models=[
                    {"id": "heartmula-3b", "name": "HeartMuLa 3B", "specialty": "fast_generation"},
                    {"id": "heartmula-7b", "name": "HeartMuLa 7B", "specialty": "quality_generation"},
                ],
                default_model="heartmula-3b",
                max_tokens=2048,
                temperature=0.8,
                timeout_seconds=600,
                supports_music_generation=True,
                supports_lyrics_enhancement=False,
                supports_audio_analysis=False,
                description="Open-source AI music generation engine (Apache-2.0) — generates audio from text prompts",
                docs_url="https://github.com/HeartMuLa/heartmula",
                config_metadata={
                    "output_format": "wav",
                    "sample_rate": 44100,
                    "max_duration": 300,
                },
            ),

            # ── GLM Z.ai Direct (Zhipu AI — bypass OpenRouter for lower latency) ──
            AIProvider(
                name="glm-zai",
                display_name="GLM Z.ai (Direct)",
                provider_type="llm",
                status="active",
                api_key=os.environ.get("GLM_ZAI_API_KEY", ""),
                api_base_url="https://api.z.ai/api/coding/paas/v4",
                auth_header_format="Bearer {api_key}",
                models=_build_glm_zai_models(),
                default_model="glm-4.5-air",
                max_tokens=65536,
                temperature=0.7,
                timeout_seconds=300,
                supports_music_generation=False,
                supports_lyrics_enhancement=True,
                supports_audio_analysis=True,
                description="GLM models direct from Zhipu AI — lower latency, no OpenRouter overhead. Models: glm-4.5-air (fast), glm-4.5 (balanced), glm-4.7 (complex)",
                docs_url="https://open.bigmodel.cn/dev/api",
                config_metadata={
                    "endpoint": "/chat/completions",
                    "supports_streaming": True,
                    "fallback_to_openrouter": True,
                    "task_routing": {
                        "fast_llm": "glm-4.5-air",
                        "balanced": "glm-4.5",
                        "complex_reasoning": "glm-4.7",
                    },
                },
            ),
        ]

        for provider in providers:
            db.add(provider)
        db.commit()
        logger.info(f"Seeded {len(providers)} AI providers (OpenRouter + HeartMuLa + GLM Z.ai Direct)")

    except Exception as e:
        db.rollback()
        logger.error(f"Seed providers error: {e}")
    finally:
        db.close()


# ─── Lofi preset seed data ────────────────────────────────────────────

def _seed_lofi_presets():
    """Insert lofi / genre preset templates if table is empty."""
    from models.database import LofiPreset

    db = SessionLocal()
    try:
        count = db.query(LofiPreset).count()
        if count > 0:
            logger.info(f"Lofi presets already seeded ({count} rows), skipping")
            return

        presets = [
            # ── LoFi presets (the main focus) ──
            LofiPreset(
                name="Lo-Fi Chill Study",
                genre="lofi", mood="chill",
                tempo_min=70, tempo_max=85, key_signature="C major",
                duration_default=60,
                instruments=["piano", "vinyl_crackle", "soft_drums", "bass"],
                tags="lo-fi,chill,study,piano,vinyl,rain,mellow,relaxing",
                prompt_template="A {mood} lo-fi hip hop beat with {instruments} at {tempo} BPM in {key}, warm vinyl texture",
                is_default=True, icon="📚", display_order=1,
                description="Perfect for studying — warm piano, soft drums, vinyl crackle",
            ),
            LofiPreset(
                name="Lo-Fi Dreamy Night",
                genre="lofi", mood="dreamy",
                tempo_min=65, tempo_max=80, key_signature="D minor",
                duration_default=60,
                instruments=["rhodes", "pad", "tape_hiss", "sub_bass"],
                tags="lo-fi,dreamy,night,rhodes,pad,tape,ethereal,spacey",
                prompt_template="A {mood} lo-fi dreamscape with {instruments}, tape-saturated and reverb-heavy",
                is_default=True, icon="🌙", display_order=2,
                description="Late night vibes — Rhodes piano, ambient pads, tape warmth",
            ),
            LofiPreset(
                name="Lo-Fi Rainy Day",
                genre="lofi", mood="melancholic",
                tempo_min=60, tempo_max=75, key_signature="A minor",
                duration_default=60,
                instruments=["guitar", "rain_ambience", "shaker", "mellow_bass"],
                tags="lo-fi,rainy,melancholic,guitar,rain,sad,cozy,introspective",
                prompt_template="A {mood} rainy lo-fi track with {instruments}, gentle and nostalgic",
                is_default=True, icon="🌧️", display_order=3,
                description="Rainy window mood — acoustic guitar, rain ambience, gentle bass",
            ),
            LofiPreset(
                name="Lo-Fi Sunday Morning",
                genre="lofi", mood="upbeat",
                tempo_min=80, tempo_max=95, key_signature="G major",
                duration_default=45,
                instruments=["epiano", "snap", "bass_guitar", "bird_chirps"],
                tags="lo-fi,upbeat,sunday,morning,happy,bright,electric piano,breezy",
                prompt_template="An {mood} lo-fi morning beat with {instruments}, sunny and warm",
                is_default=True, icon="☀️", display_order=4,
                description="Bright morning energy — electric piano, snappy drums, birds",
            ),

            # ── Hyper-Pop presets ──
            LofiPreset(
                name="Hyper-Pop Sugar Rush",
                genre="hyper-pop", mood="energetic",
                tempo_min=140, tempo_max=170, key_signature="C major",
                duration_default=30,
                instruments=["synth_lead", "808_bass", "crash_cymbal", "vocal_chops"],
                tags="hyper-pop,energetic,sugar,rush,synth,bright,loud,bouncy",
                prompt_template="A {mood} hyper-pop banger with {instruments}, distorted bass and sparkling synths",
                is_default=True, icon="⚡", display_order=10,
                description="High energy — distorted 808s, bright synths, vocal chops",
            ),
            LofiPreset(
                name="Hyper-Pop Glitch Core",
                genre="hyper-pop", mood="dark",
                tempo_min=150, tempo_max=180, key_signature="E minor",
                duration_default=30,
                instruments=["glitch_synth", "hard_kick", "distorted_bass", "sirens"],
                tags="hyper-pop,dark,glitch,aggressive,distorted,industrial,heavy",
                prompt_template="A {mood} hyper-pop glitch track with {instruments}, aggressive and distorted",
                is_default=True, icon="💀", display_order=11,
                description="Dark glitched out — distorted bass, sirens, heavy kicks",
            ),

            # ── Ambient presets ──
            LofiPreset(
                name="Ambient Space",
                genre="ambient", mood="dreamy",
                tempo_min=40, tempo_max=60, key_signature="F# minor",
                duration_default=120,
                instruments=["pad", "reverb_piano", "drone", "nature_sounds"],
                tags="ambient,space,dreamy,pad,drone,ethereal,meditation",
                prompt_template="An {mood} ambient space journey with {instruments}, floating and vast",
                is_default=True, icon="🌌", display_order=20,
                description="Deep space ambient — pads, drones, reverb-soaked piano",
            ),

            # ── Synthwave presets ──
            LofiPreset(
                name="Synthwave Night Drive",
                genre="synthwave", mood="dark",
                tempo_min=100, tempo_max=120, key_signature="A minor",
                duration_default=45,
                instruments=["juno_pad", "arpeggio", "analog_bass", "drum_machine"],
                tags="synthwave,night,drive,retro,80s,neon,arpeggio",
                prompt_template="A {mood} synthwave night drive with {instruments}, retro 80s neon vibes",
                is_default=True, icon="🚗", display_order=30,
                description="Retro night drive — Juno pads, arpeggios, analog bass",
            ),

            # ── Vaporwave presets ──
            LofiPreset(
                name="Vaporwave Mall",
                genre="vaporwave", mood="chill",
                tempo_min=60, tempo_max=80, key_signature="Eb major",
                duration_default=45,
                instruments=["slowed_samples", "reverb_guitar", "vhs_hiss", "smooth_bass"],
                tags="vaporwave,mall,chill,slowed,vhs,nostalgic,retro,aesthetic",
                prompt_template="A {mood} vaporwave mall track with {instruments}, slowed down and VHS-soaked",
                is_default=True, icon="🏬", display_order=40,
                description="Mall music from another dimension — slowed samples, VHS texture",
            ),

            # ── Chillhop presets ──
            LofiPreset(
                name="Chillhop Café",
                genre="chillhop", mood="chill",
                tempo_min=75, tempo_max=90, key_signature="Bb major",
                duration_default=45,
                instruments=["rhodes", "boom_bap_drums", "double_bass", "saxophone"],
                tags="chillhop,café,jazz,chill,rhodes,sax,boom-bap,cozy",
                prompt_template="A {mood} chillhop café vibe with {instruments}, jazzy and smooth",
                is_default=True, icon="☕", display_order=50,
                description="Café vibes — Rhodes, boom-bap drums, saxophone, double bass",
            ),

            # ── Trap presets ──
            LofiPreset(
                name="Trap After Dark",
                genre="trap", mood="dark",
                tempo_min=130, tempo_max=150, key_signature="G minor",
                duration_default=30,
                instruments=["808_slide", "hi_hat_rolls", "dark_pad", "pluck"],
                tags="trap,dark,808,night,hi-hat,heavy,mysterious",
                prompt_template="A {mood} trap beat with {instruments}, sliding 808s and dark atmosphere",
                is_default=True, icon="🌑", display_order=60,
                description="Dark trap — sliding 808s, hi-hat rolls, atmospheric pads",
            ),
        ]

        for preset in presets:
            db.add(preset)
        db.commit()
        logger.info(f"Seeded {len(presets)} lofi/genre presets across 7 genres")

    except Exception as e:
        db.rollback()
        logger.error(f"Seed presets error: {e}")
    finally:
        db.close()
