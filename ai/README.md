# 🤖 Auto LoFi & Hyper Pop Music Producer — AI Service

Python FastAPI service powering AI music generation, video analysis, and provider management.

## Quick Start

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
uvicorn app.main:app --reload --port 8001
```

## API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

## Architecture

```
ai/
├── app/main.py              # FastAPI application entry point
├── config/
│   ├── settings.py          # Pydantic settings (env-based config)
│   └── provider_config.py   # AI provider configuration
├── routes/
│   ├── music.py             # Music generation endpoints
│   ├── video.py             # Video analysis endpoints
│   ├── provider.py          # AI provider management
│   └── health.py            # Health check
├── services/
│   ├── heartmula.py         # HeartMuLa AI music generation
│   ├── music_ai_service.py  # AI music concept generation
│   ├── audio_feature_extractor.py
│   ├── provider_service.py  # Multi-provider routing
│   └── database_service.py  # Database operations
├── models/
│   ├── database.py          # SQLAlchemy models
│   └── responses.py         # Pydantic response models
├── utils/logger.py          # Loguru logger setup
└── tests/                   # Test suite
```

## Endpoints

### Music Generation
- `POST /api/v1/generate` — Generate a music track
- `GET /api/v1/status/{task_id}` — Check generation status
- `GET /api/v1/download/{task_id}` — Download generated audio
- `GET /api/v1/genres` — List available genres and moods
- `GET /api/v1/history` — Generation history

### Video Analysis
- `POST /api/v1/analyze` — Analyze video tutorial
- `POST /api/v1/upload` — Upload video file
- `GET /api/v1/status/{task_id}` — Check analysis status

### Provider Management
- `GET /api/v1/list` — List AI providers
- `GET /api/v1/status/{provider_name}` — Provider status
- `POST /api/v1/configure/{provider_name}` — Configure provider

### System
- `GET /` — Service info
- `GET /health` — Health check

## Configuration

See `.env.example` for all available environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `true` | Enable debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8001` | Server port |
| `SECRET_KEY` | — | Application secret key |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/music_producer.db` | Database URL |
| `OPENROUTER_API_KEY` | — | OpenRouter API key |
| `HEARTMULA_API_URL` | `http://localhost:8000` | HeartMuLa service URL |

## Supported Genres

`lofi` · `hyper-pop` · `ambient` · `synthwave` · `trap` · `chillhop` · `vaporwave`

## Testing

```bash
pytest tests/ -v
```

## Dependencies (16 packages)

Core: fastapi, uvicorn, pydantic, pydantic-settings, sqlalchemy, alembic, aiosqlite

Audio: librosa, soundfile, pydub, numpy

HTTP: httpx, aiohttp

Utils: python-dotenv, loguru, python-multipart
