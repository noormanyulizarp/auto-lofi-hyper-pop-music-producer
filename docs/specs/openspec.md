# OpenSpec — Auto LoFi Hyper Pop Music Producer

> Version: 0.2.0  
> Last updated: 2026-05-30

---

## 1. System Overview

**Auto LoFi Hyper Pop Music Producer** is a full-stack AI-powered music generation platform. Users select genres/moods, customize parameters, and generate original music tracks via the HeartMuLa AI engine.

**Architecture:** Monorepo with 3 services
- **ai/** — Python FastAPI (AI engine, port 8001)
- **api/** — Go API gateway (port 8080)  
- **app/** — React + TypeScript frontend (Vite dev server port 5173)

---

## 2. Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React 18 + TypeScript + Vite + TailwindCSS | SPA with React Router |
| API Gateway | Go 1.21 + Gin | Reverse proxy + auth |
| AI Service | Python 3.12 + FastAPI + SQLAlchemy | HeartMuLa music generation |
| Database | SQLite (dev) / PostgreSQL (prod) | SQLAlchemy ORM |
| Testing | pytest (unit/integration), Vitest + RTL (React), Go testing | TDD workflow |

---

## 3. API Surface — AI Service (FastAPI, port 8001)

### 3.1 Health & Info

| Method | Path | Description |
|---|---|---|
| GET | `/` | Service info |
| GET | `/health` | Health check |

### 3.2 Music Generation

| Method | Path | Description | Body |
|---|---|---|---|
| POST | `/api/v1/generate` | Queue music generation | `{title, genre, mood, duration, tempo?, key?, instruments?, prompt?}` |
| GET | `/api/v1/status/{task_id}` | Check generation status | — |
| GET | `/api/v1/download/{task_id}` | Download generated audio | — |
| GET | `/api/v1/genres` | List available genres & moods | — |
| GET | `/api/v1/history` | Get generation history | `?limit=20&offset=0` |

### 3.3 Presets

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/music/presets` | List presets (filter: `?genre=&mood=&defaults_only=`) |
| GET | `/api/v1/music/presets/{id}` | Get preset by ID |
| GET | `/api/v1/music/genres` | List genres with preset counts |

### 3.4 Providers

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/providers` | List AI providers (filter: `?type=&status=`) |
| GET | `/api/v1/providers/{id}` | Get provider details |
| POST | `/api/v1/providers` | Create provider |
| PUT | `/api/v1/providers/{id}` | Update provider |
| DELETE | `/api/v1/providers/{id}` | Delete provider |
| POST | `/api/v1/providers/{id}/test` | Test provider connection |
| GET | `/api/v1/providers/stats` | Provider statistics |

### 3.5 Video Analysis

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/analyze` | Analyze YouTube video URL |
| POST | `/api/v1/upload` | Upload video file |
| GET | `/api/v1/status/{task_id}` | Get analysis status |

---

## 4. Data Models

### 4.1 AIProvider
```
id: UUID (PK)
name: String (unique)           # "openrouter", "heartmula", "glm-zai"
display_name: String            # "OpenRouter"
provider_type: String           # "llm", "music", "video"
status: String                  # "active", "inactive", "error"
api_key: String?
api_base_url: String?
models: JSON[]                  # Available models
default_model: String?
max_tokens: Integer             # default: 32768
temperature: Float              # default: 0.7
created_at: DateTime
updated_at: DateTime
```

### 4.2 MusicGeneration
```
id: UUID (PK)
task_id: String (unique)
title: String
genre: String
mood: String
duration: Integer               # seconds
tempo: Integer?
key: String?
instruments: JSON[]
prompt: Text?
enhanced_prompt: Text?
status: String                  # "pending", "processing", "completed", "failed"
provider_id: FK → AIProvider
model_used: String?
audio_file_path: String?
error_message: Text?
created_at: DateTime
completed_at: DateTime?
```

### 4.3 LofiPreset
```
id: UUID (PK)
name: String
genre: String
mood: String
description: Text
default_tempo: Integer
default_key: String
default_instruments: JSON[]
default_duration: Integer
prompt_template: Text
is_default: Boolean
display_order: Integer
created_at: DateTime
```

### 4.4 VideoAnalysis
```
id: UUID (PK)
url: String
title: String?
analysis_result: JSON?
status: String                  # "pending", "processing", "completed", "failed"
error_message: Text?
created_at: DateTime
completed_at: DateTime?
```

---

## 5. Frontend Routes

| Path | Component | Description |
|---|---|---|
| `/` | HomePage | Landing + quick actions |
| `/generate` | GeneratePage | Music generation form |
| `/learn` | LearnPage | Video analysis (placeholder) |
| `/dashboard` | DashboardPage | Stats & history |

---

## 6. Test Architecture

### 6.1 Unit Tests (pytest)
- **184 tests already passing** ✅
- Coverage: config, models, database service, routes (music, provider, video, presets), HeartMuLa service

### 6.2 Integration Tests (NEW — to be built)
- Full request/response cycle via FastAPI TestClient
- Database integration (create → read → update → delete workflows)
- HeartMuLa API integration (mocked external, real internal flow)

### 6.3 E2E Tests (NEW — to be built)
- Start FastAPI server → hit all endpoints → verify responses
- Frontend build → serve → verify pages render
- Full flow: generate music → check status → download

---

## 7. Test Coverage Requirements

| Category | Target | Current |
|---|---|---|
| Unit tests | 200+ | 184 ✅ |
| Integration tests | 20+ | 0 ❌ |
| E2E tests | 10+ | 0 ❌ |
| API endpoint coverage | 100% | ~80% |
| Model field coverage | 100% | ~90% |

---

## 8. Current Status

### ✅ Working
- FastAPI server starts, all routes registered
- SQLite database with seed data (providers, presets)
- HeartMuLa service (local + API mode)
- 184 unit tests passing
- React components (Header, Sidebar, pages)
- Go module renamed

### ⚠️ Needs Work
- Integration tests (zero)
- E2E tests (zero)
- Frontend not connected to API
- Go API gateway not building
- HeartMuLa actual audio generation (needs heartlib binary)
