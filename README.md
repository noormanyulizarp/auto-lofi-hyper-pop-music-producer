# 🎵 Auto LoFi & Hyper Pop Music Producer

> AI-powered music generation and learning platform — create LoFi beats, Hyper Pop tracks, and more using AI.

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)](https://fastapi.tiangolo.com)
[![Go](https://img.shields.io/badge/Go-1.21-00ADD8)](https://go.dev)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🎯 What is this?

An AI-powered music production platform that lets you:
- **Generate music** in 7 genres (LoFi, Hyper Pop, Ambient, Synthwave, Trap, Chillhop, Vaporwave)
- **Learn from video tutorials** — analyze YouTube production content
- **Dashboard** — track your generated music and progress

Powered by **HeartMuLa** (open-source AI music generation) and **OpenRouter** (multi-model AI provider).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  React Frontend                  │
│          (TypeScript + TailwindCSS)              │
├─────────────────────────────────────────────────┤
│               Go API Gateway                     │
│          (Routing + Auth + Proxy)                │
├─────────────────────────────────────────────────┤
│            Python AI Service                     │
│    (FastAPI + HeartMuLa + Audio Analysis)        │
├─────────────────────────────────────────────────┤
│              SQLite Database                     │
│         (SQLAlchemy + Alembic)                   │
└─────────────────────────────────────────────────┘
```

Three-tier hybrid stack designed for lightweight VPS deployment (2GB RAM).

---

## 📁 Project Structure

```
auto-lofi-hyper-pop-music-producer/
├── ai/                          # Python AI Service (FastAPI)
│   ├── app/main.py              # FastAPI entry point
│   ├── config/settings.py       # Configuration (pydantic-settings)
│   ├── routes/                  # API endpoints
│   │   ├── music.py             # Music generation routes
│   │   ├── video.py             # Video analysis routes
│   │   └── provider.py          # AI provider management
│   ├── services/                # Business logic
│   │   ├── heartmula.py         # HeartMuLa integration
│   │   ├── music_ai_service.py  # AI music concepts
│   │   └── audio_feature_extractor.py
│   ├── models/                  # Data models (SQLAlchemy + Pydantic)
│   ├── tests/                   # Python test suite
│   └── requirements.txt         # Python dependencies
│
├── api/                         # Go API Gateway
│   ├── cmd/main.go              # Go entry point
│   ├── internal/                # Internal packages
│   │   ├── api/                 # HTTP handlers
│   │   ├── config/              # Go config
│   │   ├── middleware/          # Auth, CORS, logging
│   │   └── models/              # Go data models
│   └── pkg/                     # Shared Go packages
│
├── app/                         # React Frontend (Vite + TypeScript)
│   ├── src/
│   │   ├── components/Layout/   # Header, Sidebar
│   │   ├── pages/               # HomePage, GeneratePage, etc.
│   │   ├── hooks/               # Custom React hooks
│   │   ├── stores/              # State management
│   │   └── utils/               # Utility functions
│   └── package.json
│
├── docs/                        # Documentation
│   ├── 01_overview.md
│   ├── 02_technology_stack.md
│   ├── 03_ai_music_generation.md
│   ├── 07_system_architecture.md
│   └── plans/                   # Development plans
│
├── tests/                       # Integration & E2E tests
├── shared/                      # Shared types & scripts
└── package.json                 # Root workspace config
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Go 1.21+
- Node.js 18+ & pnpm
- ffmpeg (for audio processing)

### 1. Python AI Service

```bash
cd ai

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the service
uvicorn app.main:app --reload --port 8001
```

API available at `http://localhost:8001`
Swagger docs at `http://localhost:8001/docs`

### 2. Go API Gateway

```bash
cd api

# Download dependencies
go mod tidy

# Run the gateway
go run cmd/main.go
```

### 3. React Frontend

```bash
cd app

# Install dependencies
pnpm install

# Run dev server
pnpm dev
```

---

## 🔌 API Endpoints

### Music Generation
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/generate` | Generate music track |
| `GET` | `/api/v1/status/{task_id}` | Check generation status |
| `GET` | `/api/v1/download/{task_id}` | Download generated audio |
| `GET` | `/api/v1/genres` | List available genres & moods |
| `GET` | `/api/v1/history` | Generation history |

### Video Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze` | Analyze video tutorial |
| `POST` | `/api/v1/upload` | Upload video for analysis |
| `GET` | `/api/v1/status/{task_id}` | Check analysis status |

### Provider Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/list` | List AI providers |
| `GET` | `/api/v1/status/{provider}` | Provider status |
| `POST` | `/api/v1/configure/{provider}` | Configure provider |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/` | Service info |

---

## 🎸 Supported Genres

| Genre | Description |
|-------|-------------|
| **LoFi** | Chill beats, relaxed vibes |
| **Hyper Pop** | High-energy, experimental pop |
| **Ambient** | Atmospheric soundscapes |
| **Synthwave** | Retro-futuristic electronic |
| **Trap** | Heavy bass, rhythmic patterns |
| **Chillhop** | Hip-hop meets chill |
| **Vaporwave** | Nostalgic, dreamy aesthetic |

---

## 🤖 AI Providers

| Provider | Purpose | Status |
|----------|---------|--------|
| **HeartMuLa** | Open-source AI music generation | Core integration |
| **OpenRouter** | Multi-model AI (GLM-4.5, Nemotron, etc.) | Prompt enhancement |

---

## ⚙️ Configuration

Environment variables (see `ai/.env.example`):

```env
# Application
DEBUG=true
HOST=0.0.0.0
PORT=8001
SECRET_KEY=your-secret-key

# Database (SQLite for dev)
DATABASE_URL=sqlite+aiosqlite:///./data/music_producer.db

# AI Providers
OPENROUTER_API_KEY=your-key
HEARTMULA_API_URL=http://localhost:8000
```

---

## 🛠️ Development Status

- [x] **Phase 1** — Project structure, fix broken imports, security
- [x] **Phase 2.1** — FastAPI running, all endpoints verified
- [ ] **Phase 2.2** — HeartMuLa real integration
- [ ] **Phase 2.3** — Go API gateway build
- [ ] **Phase 3** — React frontend build & connect to API

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ by [Noorman Prabowo](https://github.com/noormanyulizarp)*
