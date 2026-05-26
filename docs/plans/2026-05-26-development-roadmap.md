# Auto LoFi Hyper Pop Music Producer - Development Roadmap

> **For Hermes:** Use subagent-driven-development skill to implement tasks. Work methodically, commit frequently.

**Goal:** Build a working AI-powered music generation platform that can run on a resource-constrained VPS (2GB RAM).

**Architecture:** React frontend + Python FastAPI AI services + Go API gateway. Start lightweight, scale up.

**Key Constraint:** VPS only has ~522MB RAM available. Heavy deps (whisper, essentia, celery) deferred.

---

## Phase 1: Fix & Stabilize (Priority: NOW)

### Task 1.1: Fix .gitignore & security
- Create proper `.gitignore` (node_modules, .env, __pycache__, etc.)
- Remove sensitive defaults from committed files
- Add `.env.example` files

### Task 1.2: Fix Python AI broken imports
- `ai/app/main.py` imports `from .routes import video` but `routes/video.py` doesn't exist
- Fix: create `ai/routes/video.py` stub, or remove import temporarily
- Verify: `cd ai && python -c "from app.main import app"`

### Task 1.3: Fix Go module name
- `api/go.mod` says `module auto-music-producer/api` → should match new repo name
- Fix import paths in all Go files

### Task 1.4: Fix React missing components
- `App.tsx` imports components that don't exist yet
- Create minimal stub components so app at least renders
- Verify: `cd app && pnpm install && pnpm build`

### Task 1.5: Trim Python requirements (VPS-friendly)
- Remove heavy deps: essentia, pyaudio, whisper, selenium, celery, redis
- Keep core: fastapi, uvicorn, pydantic, loguru, python-dotenv
- Keep music: librosa, soundfile, pydub (lighter audio processing)
- Use SQLite instead of PostgreSQL for dev
- Verify: `cd ai && pip install -r requirements.txt` succeeds without OOM

---

## Phase 2: Core Backend Working (Priority: HIGH)

### Task 2.1: Python AI service - minimal FastAPI
- Fix all imports, ensure FastAPI starts
- Health check endpoint working
- Config from `.env` file
- Verify: `cd ai && uvicorn app.main:app --port 8001` starts

### Task 2.2: HeartMuLa integration (music generation core)
- Integrate HeartMuLa service for actual music generation
- Basic generate endpoint: POST /api/v1/music/generate
- Takes genre/mood/tempo params, returns audio file
- Verify: curl generates actual audio output

### Task 2.3: Go API gateway - basic setup
- Rename module, fix imports
- Health check endpoint
- Proxy to Python AI service
- Verify: `cd api && go build ./cmd/main.go`

### Task 2.4: SQLite database setup
- SQLAlchemy models for: User, MusicGeneration, LearningSession
- Auto-create tables on startup
- Alembic migrations ready
- Verify: tables created on first run

---

## Phase 3: Frontend Working (Priority: HIGH)

### Task 3.1: React app setup
- Install proper dependencies (react-router, axios, zustand, tailwind)
- Create working Layout components (Header, Sidebar)
- Create page stubs (Home, Generate, Learn, Dashboard)
- Verify: `pnpm dev` runs and renders

### Task 3.2: Music Generation UI
- Build GeneratePage with form (genre, mood, tempo, duration)
- Audio player component for playback
- Connect to AI service endpoint
- Verify: can generate and play music from UI

### Task 3.3: Dashboard & History
- List generated tracks
- Playback history
- Basic user stats

---

## Phase 4: Polish & Deploy (Priority: MEDIUM)

### Task 4.1: Docker setup (lightweight)
- Multi-stage Dockerfile for each service
- docker-compose.yml for orchestration
- Total target: < 1.5GB RAM

### Task 4.2: Nginx reverse proxy
- Route / → React frontend
- Route /api → Go gateway
- Route /ai → Python AI service

### Task 4.3: Testing
- Unit tests for Go handlers
- Unit tests for Python services
- Integration tests for API endpoints

---

## Execution Order

```
Phase 1 (Fix)     → Phase 2.1 (Python starts) → Phase 2.2 (Music gen)
                  → Phase 3.1 (React renders) → Phase 3.2 (Gen UI)
                  → Phase 2.3 (Go gateway)    → Phase 2.4 (Database)
Phase 4 (Polish)  → Docker → Nginx → Tests
```

**First milestone:** Generate music via API call and hear it in the browser.

## VPS Resource Budget

| Service | RAM Target | Notes |
|---------|-----------|-------|
| Python AI | ~150MB | FastAPI + librosa, no whisper/essentia |
| Go API | ~30MB | Gin gateway |
| React static | ~0MB | Built files served by nginx |
| SQLite | ~5MB | File-based, no separate process |
| **Total** | **~185MB** | Fits in available 522MB |
