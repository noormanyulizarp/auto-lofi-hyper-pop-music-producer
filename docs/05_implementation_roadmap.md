# Implementation Roadmap & Development Plan

**File:** 05_implementation_roadmap.md  
**Task Code:** RSCH023

## Development Phases Overview

This implementation roadmap outlines a systematic approach to developing the auto lofi and hyper pop music producer web application, broken down into manageable phases with clear milestones and deliverables.

### Phase Structure
- **Phase 1:** Foundation & Basic Generation (Weeks 1-4)
- **Phase 2:** Learning System & Advanced Features (Weeks 5-8)  
- **Phase 3:** User Experience & Commercial Features (Weeks 9-12)
- **Phase 4:** Scaling & Production Deployment (Weeks 13-16)
- **Phase 5:** Market Launch & Growth (Weeks 17-20)

---

## Phase 1: Foundation & Basic Generation (Weeks 1-4)

### Phase Goals
- Set up development environment and infrastructure
- Implement basic AI music generation (HeartMuLa)
- Create core React frontend with audio playback
- Establish basic API structure

### Key Deliverables
1. **Development Environment Setup**
2. **HeartMuLa Integration**
3. **Basic React Frontend**
4. **Core API Structure**
5. **Initial LoFi Generation**

### Technical Tasks

#### 1.1 Development Environment Setup (Week 1)
**Tasks:**
- [ ] Set up Git repository with proper branching strategy
- [ ] Create Docker development environment
- [ ] Install HeartMuLa dependencies and models
- [ ] Set up PostgreSQL database with initial schema
- [ ] Configure Redis caching layer
- [ ] Set up CI/CD pipeline (GitHub Actions)

**Technical Specifications:**
```yaml
# Development Environment
python_version: "3.10+"
node_version: "18+"
database: "PostgreSQL 15+"
cache: "Redis 7+"
container: "Docker + Docker Compose"
ci_cd: "GitHub Actions"
```

**Implementation Details:**
```bash
# Project Structure Setup
mkdir -p auto-music-producer/{frontend,backend,ai-services,database,docs}
cd auto-music-producer

# Initialize Git Repository
git init
git flow init  # Git Flow for branching strategy

# Docker Setup
cat > docker-compose.yml << EOF
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/musicdb
      - REDIS_URL=redis://redis:6379
  
  ai-service:
    build: ./ai-services
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: musicdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
EOF
```

#### 1.2 HeartMuLa Integration (Week 1-2)
**Tasks:**
- [ ] Download and install HeartMuLa models
- [ ] Create Python service wrapper for HeartMuLa
- [ ] Implement basic music generation API
- [ ] Add error handling and logging
- [ ] Set up model loading and caching

**Implementation Details:**
```python
# ai-services/heartmula_service.py
import asyncio
import logging
from heartlib.pipelines import MusicGenerationPipeline

class HeartMuLaService:
    def __init__(self, model_path="./models", version="3B"):
        self.model_path = model_path
        self.version = version
        self.pipeline = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize HeartMuLa pipeline"""
        try:
            self.pipeline = MusicGenerationPipeline(
                model_path=self.model_path,
                version=self.version,
                lazy_load=True
            )
            self.logger.info("HeartMuLa pipeline initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize HeartMuLa: {e}")
            raise
    
    async def generate_music(self, request_data):
        """Generate music based on request parameters"""
        try:
            # Extract parameters
            lyrics = request_data.get('lyrics', '')
            tags = request_data.get('tags', 'lofi,chill,relaxing')
            duration = request_data.get('duration', 240)  # 4 minutes
            
            # Generate music
            result = await self._run_generation(
                lyrics=lyrics,
                tags=tags,
                max_audio_length_ms=duration * 1000
            )
            
            return {
                'success': True,
                'result': result,
                'duration': duration
            }
            
        except Exception as e:
            self.logger.error(f"Music generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _run_generation(self, lyrics, tags, max_audio_length_ms):
        """Run HeartMuLa generation"""
        # This would be implemented with proper async handling
        # For now, placeholder for the actual HeartMuLa call
        output_path = f"/tmp/generated_{asyncio.get_event_loop().time()}.mp3"
        
        # HeartMuLa generation call would go here
        # result = self.pipeline.generate(...)
        
        return {
            'output_path': output_path,
            'tags': tags,
            'lyrics': lyrics
        }
```

#### 1.3 Basic React Frontend (Week 2-3)
**Tasks:**
- [ ] Set up React project with TypeScript
- [ ] Create main dashboard layout
- [ ] Implement audio player component
- [ ] Add generation form with basic controls
- [ ] Create responsive design for mobile/desktop

**Implementation Details:**
```typescript
// frontend/src/types/index.ts
export interface GenerationRequest {
  genre: 'lofi' | 'hyper_pop';
  mood: string[];
  tempo: number;
  duration: number;
  instruments: string[];
  commercialRights: boolean;
}

export interface GenerationResponse {
  success: boolean;
  result?: {
    output_path: string;
    tags: string;
    lyrics: string;
  };
  error?: string;
  duration: number;
}

export interface AudioTrack {
  id: string;
  title: string;
  genre: string;
  duration: number;
  url: string;
  createdAt: Date;
}
```

```typescript
// frontend/src/components/AudioPlayer.tsx
import React, { useState, useRef } from 'react';
import { FaPlay, FaPause, FaDownload } from 'react-icons/fa';

interface AudioPlayerProps {
  track: AudioTrack;
  onPlay?: () => void;
  onPause?: () => void;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ track, onPlay, onPause }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const handlePlayPause = () => {
    if (isPlaying) {
      audioRef.current?.pause();
      onPause?.();
    } else {
      audioRef.current?.play();
      onPlay?.();
    }
    setIsPlaying(!isPlaying);
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = track.url;
    link.download = `${track.title}.mp3`;
    link.click();
  };

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={track.url}
        onEnded={() => setIsPlaying(false)}
      />
      
      <div className="player-controls">
        <button
          onClick={handlePlayPause}
          className="play-button"
        >
          {isPlaying ? <FaPause /> : <FaPlay />}
        </button>
        
        <div className="track-info">
          <h3>{track.title}</h3>
          <p>{track.genre} • {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}</p>
        </div>
        
        <button
          onClick={handleDownload}
          className="download-button"
        >
          <FaDownload />
        </button>
      </div>
    </div>
  );
};

export default AudioPlayer;
```

#### 1.4 Core API Structure (Week 3-4)
**Tasks:**
- [ ] Set up Go backend with Gin framework
- [ ] Create REST API endpoints
- [ ] Implement database models and queries
- [ ] Add authentication middleware
- [ ] Set up WebSocket for real-time updates

**Implementation Details:**
```go
// backend/main.go
package main

import (
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all origins in development
	},
}

type MusicGenerationRequest struct {
	Genre            string   `json:"genre"`
	Mood             []string `json:"mood"`
	Tempo            int      `json:"tempo"`
	Duration         int      `json:"duration"`
	Instruments      []string `json:"instruments"`
	CommercialRights bool     `json:"commercial_rights"`
}

type MusicGenerationResponse struct {
	Success  bool   `json:"success"`
	TrackURL string `json:"track_url,omitempty"`
	Error    string `json:"error,omitempty"`
	Duration int    `json:"duration"`
}

func main() {
	// Initialize Gin router
	r := gin.Default()
	
	// CORS middleware
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
		
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		
		c.Next()
	})
	
	// API routes
	api := r.Group("/api/v1")
	{
		api.POST("/generate", generateMusicHandler)
		api.GET("/tracks/:id", getTrackHandler)
		api.GET("/tracks", listTracksHandler)
		api.POST("/auth/register", registerHandler)
		api.POST("/auth/login", loginHandler)
	}
	
	// WebSocket endpoint
	r.GET("/ws", websocketHandler)
	
	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
			"timestamp": time.Now().Unix(),
		})
	})
	
	log.Println("Server starting on :8080")
	if err := r.Run(":8080"); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}

func generateMusicHandler(c *gin.Context) {
	var req MusicGenerationRequest
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, MusicGenerationResponse{
			Success: false,
			Error:   "Invalid request format",
			Duration: 0,
		})
		return
	}
	
	// Validate request
	if req.Genre == "" {
		c.JSON(http.StatusBadRequest, MusicGenerationResponse{
			Success: false,
			Error:   "Genre is required",
			Duration: 0,
		})
		return
	}
	
	// Forward to AI service (HeartMuLa)
	trackURL, err := callHeartMuLaService(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, MusicGenerationResponse{
			Success: false,
			Error:   err.Error(),
			Duration: req.Duration,
		})
		return
	}
	
	c.JSON(http.StatusOK, MusicGenerationResponse{
		Success:  true,
		TrackURL: trackURL,
		Duration: req.Duration,
	})
}

func callHeartMuLaService(req MusicGenerationRequest) (string, error) {
	// This would make HTTP call to the HeartMuLa service
	// For now, return mock URL
	return "http://localhost:8001/generated/track.mp3", nil
}

func websocketHandler(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Println("WebSocket upgrade error:", err)
		return
	}
	defer conn.Close()
	
	for {
		// Handle WebSocket messages
		_, _, err := conn.ReadMessage()
		if err != nil {
			log.Println("WebSocket read error:", err)
			break
		}
	}
}
```

#### 1.5 Initial LoFi Generation (Week 4)
**Tasks:**
- [ ] Create LoFi-specific generation templates
- [ ] Implement basic LoFi parameter presets
- [ ] Add vinyl crackle and warm audio effects
- [ ] Create sample LoFi tracks for testing
- [ ] Set up basic audio post-processing

**Implementation Details:**
```python
# ai-services/lofi_generator.py
import asyncio
import logging
from typing import Dict, List, Optional
import numpy as np
import soundfile as sf

class LoFiGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.presets = self._load_lofi_presets()
    
    def _load_lofi_presets(self) -> Dict:
        """Load LoFi generation presets"""
        return {
            'chill_study': {
                'tempo': 85,
                'mood': ['relaxing', 'chill', 'focus'],
                'instruments': ['piano', 'guitar', 'drums', 'bass'],
                'effects': ['vinyl_crackle', 'warm_eq', 'compression']
            },
            'vintage_vibes': {
                'tempo': 78,
                'mood': ['nostalgic', 'warm', 'intimate'],
                'instruments': ['piano', 'vinyl_samples', 'light_drums'],
                'effects': ['vinyl_crackle', 'tape_saturation', 'reverb']
            },
            'beats_to_relax': {
                'tempo': 92,
                'mood': ['calm', 'peaceful', 'meditative'],
                'instruments': ['synth_pad', 'soft_drums', 'bass'],
                'effects': ['delay', 'warm_eq', 'subtle_reverb']
            }
        }
    
    async def generate_lofi(self, preset_name: str, custom_params: Optional[Dict] = None) -> Dict:
        """Generate LoFi music based on preset or custom parameters"""
        try:
            # Get preset parameters
            preset = self.presets.get(preset_name, self.presets['chill_study'])
            params = {**preset, **(custom_params or {})}
            
            # Generate base music with HeartMuLa
            base_track = await self._generate_base_track(params)
            
            # Apply LoFi-specific effects
            processed_track = await self._apply_lofi_effects(base_track, params)
            
            # Add metadata
            track_data = {
                'title': f"LoFi {preset_name.replace('_', ' ').title()}",
                'genre': 'lofi',
                'tempo': params['tempo'],
                'duration': 240,  # 4 minutes
                'mood': params['mood'],
                'url': processed_track['url'],
                'created_at': asyncio.get_event_loop().time()
            }
            
            return {
                'success': True,
                'track': track_data
            }
            
        except Exception as e:
            self.logger.error(f"LoFi generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_base_track(self, params: Dict) -> Dict:
        """Generate base music track using HeartMuLa"""
        # This would integrate with the HeartMuLa service
        # For now, return mock data
        return {
            'url': 'http://localhost:8001/generated/base_lofi.mp3',
            'duration': 240
        }
    
    async def _apply_lofi_effects(self, track: Dict, params: Dict) -> Dict:
        """Apply LoFi-specific audio effects"""
        # Load audio file
        audio_data, sample_rate = sf.read(track['url'])
        
        # Apply effects based on preset
        if 'vinyl_crackle' in params['effects']:
            audio_data = await self._add_vinyl_crackle(audio_data, sample_rate)
        
        if 'warm_eq' in params['effects']:
            audio_data = await self._apply_warm_eq(audio_data, sample_rate)
        
        # Save processed audio
        processed_url = track['url'].replace('base_', 'processed_')
        sf.write(processed_url, audio_data, sample_rate)
        
        return {
            'url': processed_url,
            'duration': track['duration']
        }
    
    async def _add_vinyl_crackle(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Add vinyl crackle effect to audio"""
        # Generate noise for crackle
        noise = np.random.normal(0, 0.001, len(audio))
        
        # Apply envelope to make it subtle
        envelope = np.random.uniform(0.1, 0.3, len(audio))
        crackle = noise * envelope
        
        # Mix with original audio
        return audio + crackle
    
    async def _apply_warm_eq(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply warm EQ to audio"""
        # Simple warm EQ simulation - boost low frequencies, reduce high frequencies
        # In a real implementation, this would use proper EQ filters
        return audio * 0.95  # Slight volume reduction to simulate warmth
```

### Phase 1 Success Metrics
- [ ] HeartMuLa model successfully loaded and functional
- [ ] React frontend with basic audio playback working
- [ ] Go backend API with music generation endpoint
- [ ] PostgreSQL database with initial schema
- [ ] Basic LoFi generation producing recognizable music
- [ ] CI/CD pipeline running successfully
- [ ] Docker containers building and running

---

## Phase 2: Learning System & Advanced Features (Weeks 5-8)

### Phase Goals
- Implement video tutorial analysis system
- Develop machine learning pattern recognition
- Add Hyper Pop genre support
- Create user preference learning system

### Key Deliverables
1. **Video Tutorial Analysis Engine**
2. **Machine Learning Pattern Recognition**
3. **Hyper Pop Generation Support**
4. **User Learning System**
5. **Advanced Audio Processing**

This phase will be detailed in the full implementation plan, continuing with the same level of technical depth and specificity.

---

## Phase 3: User Experience & Commercial Features (Weeks 9-12)

### Phase Goals
- Implement user authentication and profiles
- Create subscription and billing system
- Add commercial music licensing
- Develop marketplace features

### Key Deliverables
1. **User Authentication System**
2. **Subscription Management**
3. **Commercial Licensing**
4. **Music Marketplace**
5. **Enhanced User Interface**

---

## Phase 4: Scaling & Production Deployment (Weeks 13-16)

### Phase Goals
- Optimize for production performance
- Implement scalable architecture
- Add monitoring and analytics
- Deploy to production environment

### Key Deliverables
1. **Production Infrastructure**
2. **Performance Optimization**
3. **Monitoring & Analytics**
4. **Automated Deployment**
5. **Production Testing**

---

## Phase 5: Market Launch & Growth (Weeks 17-20)

### Phase Goals
- Official product launch
- Marketing campaign execution
- User onboarding and support
- Growth optimization

### Key Deliverables
1. **Launch Marketing Campaign**
2. **User Onboarding System**
3. **Customer Support Platform**
4. **Growth Analytics Dashboard**
5. **Post-Launch Optimization Plan**

---

## Resource Requirements

### Team Composition
- **Full-Stack Developer:** 1 (React + Go + Python)
- **AI/Machine Learning Engineer:** 1 (HeartMuLa + ML)
- **Frontend Developer:** 1 (React + UI/UX)
- **DevOps Engineer:** 0.5 (Part-time for infrastructure)
- **UI/UX Designer:** 0.5 (Part-time for design)

### Hardware Requirements
- **Development:** 4x workstations with 16GB RAM each
- **Testing:** 1 server with 32GB RAM + GPU
- **Production:** Cloud infrastructure with autoscaling

### Software Requirements
- **Development Tools:** VS Code, Git, Docker, Postman
- **Project Management:** Jira or Trello
- **Communication:** Slack, Discord
- **Monitoring:** Prometheus, Grafana, Sentry

### Budget Estimate (20 Weeks)
- **Development Team:** $200,000-300,000
- **Infrastructure:** $20,000-30,000
- **Software Licenses:** $10,000-15,000
- **Marketing:** $30,000-50,000
- **Contingency:** $40,000-60,000
- **Total Estimated Budget:** $300,000-455,000

This implementation roadmap provides a comprehensive plan for developing the auto lofi and hyper pop music producer, with clear phases, technical details, and realistic timelines for bringing the product to market.