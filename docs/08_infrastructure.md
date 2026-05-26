# Infrastructure Documentation

**Project:** Auto LoFi & Hyper Pop Music Producer  
**Task Code:** RSCH023  
**Version:** 1.0  
**Last Updated:** May 22, 2026

## Table of Contents
1. [Overview](#overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Production Environment (Later)](#production-environment-later)
4. [Database Setup](#database-setup)
5. [Cache Setup](#cache-setup)
6. [File Storage Setup](#file-storage-setup)
7. [Security Configuration](#security-configuration)
8. [Monitoring & Logging](#monitoring--logging)
9. [Deployment Strategy](#deployment-strategy)
10. [Scaling Considerations](#scaling-considerations)

---

## Overview

This infrastructure documentation focuses on a **traditional, non-containerized** approach for initial development and deployment. We'll use native installations and configuration files rather than Docker or Kubernetes. This approach is ideal for:

- **Initial Development:** Easier debugging and development workflow
- **Small Teams:** Less complex setup and maintenance
- **Learning:** Better understanding of each component
- **Cost-Effective:** No container orchestration overhead

### Core Components
- **Frontend:** React + TypeScript (Node.js server)
- **Backend:** Go API (native binary)
- **AI Services:** Python (native Python environment)
- **Database:** PostgreSQL (native installation)
- **Cache:** Redis (native installation)
- **Storage:** Local filesystem → Cloud storage later

---

## Development Environment Setup

### Prerequisites

#### System Requirements
- **OS:** Linux (Ubuntu 22.04+ recommended), macOS, or Windows with WSL2
- **RAM:** 8GB minimum, 16GB recommended
- **CPU:** 4 cores minimum, 8 cores recommended
- **Storage:** 50GB free space (for models, audio files, and development)
- **GPU:** NVIDIA GPU with 16GB VRAM (optional, for AI model acceleration)

#### Software Dependencies
```bash
# Node.js (for React frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Go (for backend API)
wget https://golang.org/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc

# Python (for AI services)
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-venv python3-pip

# PostgreSQL (database)
sudo apt-get install -y postgresql postgresql-contrib

# Redis (cache)
sudo apt-get install -y redis-server

# Development tools
sudo apt-get install -y git build-essential curl wget ffmpeg
```

### Development Environment Setup

#### 1. Project Structure Setup
```bash
# Create project directory
mkdir auto-music-producer
cd auto-music-producer

# Create main directories
mkdir -p app api ai shared config scripts logs models

# Initialize Git repository
git init
```

#### 2. Frontend Setup (React + TypeScript)
```bash
# Navigate to frontend directory
cd app

# Initialize React project with TypeScript
npx create-react-app . --template typescript
npm install

# Install additional dependencies
npm install @types/react @types/react-dom
npm install axios react-router-dom @types/react-router-dom
npm install tailwindcss postcss autoprefixer
npm install @tailwindcss/typography @headlessui/react
npm install howler wavesurfer.js react-query
npm install @types/howler

# Configure Tailwind CSS
npx tailwindcss init -p
```

#### 3. Backend Setup (Go)
```bash
# Navigate to backend directory
cd ../api

# Initialize Go module
go mod init auto-music-producer/api

# Create basic directory structure
mkdir -p cmd/internal/{api,services,models,clients,config}
mkdir -p pkg/{logger,utils,middleware}
mkdir -p migrations

# Install Go dependencies
go get -u github.com/gin-gonic/gin
go get -u github.com/gin-contrib/cors
go get -u gorm.io/gorm
go get -u gorm.io/driver/postgres
go get -u github.com/go-redis/redis/v8
go get -u github.com/golang-jwt/jwt/v5
go get -u github.com/spf13/viper
go get -u go.uber.org/zap
```

#### 4. AI Services Setup (Python)
```bash
# Navigate to AI services directory
cd ../ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Create basic directory structure
mkdir -p services models utils api/{endpoints,schemas}
mkdir -p models/heartmula models/ml_models

# Install Python dependencies
pip install fastapi uvicorn[standard]
pip install sqlalchemy alembic
pip install redis
pip install tensorflow librosa scikit-learn
pip install pydub soundfile ffmpeg-python
pip install boto3 requests
pip install python-multipart
pip install python-jose[cryptography]
pip install passlib[bcrypt]

# Install HeartMuLa (clone from repository)
git clone https://github.com/heartmula/heartmula.git models/heartmula
cd models/heartmula
pip install -e .
```

#### 5. Database Setup (PostgreSQL)
```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database user and database
sudo -u postgres createuser musicuser
sudo -u postgres createdb musicdb -O musicuser
sudo -u postgres psql -c "ALTER USER musicuser PASSWORD 'musicpass';"

# Create database schema
sudo -u postgres psql -d musicdb -f ../shared/migrations/init.sql
```

#### 6. Redis Setup (Cache)
```bash
# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
# Should return: PONG

# Configure Redis for development
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup
sudo sed -i 's/^# maxmemory .*/maxmemory 512mb/' /etc/redis/redis.conf
sudo sed -i 's/^# maxmemory-policy .*/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
sudo systemctl restart redis-server
```

---

## Production Environment (Later)

### Production Server Requirements
- **Server:** Ubuntu 22.04 LTS or CentOS 9 Stream
- **RAM:** 32GB minimum, 64GB recommended
- **CPU:** 8 cores minimum, 16 cores recommended
- **Storage:** 1TB SSD minimum, 2TB recommended
- **Network:** 1Gbps connection, static IP address
- **Backup:** Automated backup system with off-site storage

### Production Setup Steps

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Create application user
sudo useradd -m -s /bin/bash musicapp
sudo usermod -aG sudo musicapp

# Install dependencies
sudo apt install -y curl wget git build-essential
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y nginx
sudo apt install -y ffmpeg
```

#### 2. Database Setup (Production)
```bash
# Configure PostgreSQL for production
sudo nano /etc/postgresql/15/main/postgresql.conf

# Key settings to modify:
# listen_addresses = 'localhost'
# max_connections = 200
# shared_buffers = 4GB
# effective_cache_size = 12GB
# maintenance_work_mem = 1GB
# checkpoint_completion_target = 0.9
# wal_buffers = 16MB
# default_statistics_target = 100
# random_page_cost = 1.1
# effective_io_concurrency = 200
# work_mem = 16MB
# min_wal_size = 4GB
# max_wal_size = 16GB

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### 3. Redis Setup (Production)
```bash
# Configure Redis for production
sudo nano /etc/redis/redis.conf

# Key settings to modify:
# maxmemory 8gb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# save 60 10000
# appendonly yes
# appendfsync everysec

# Restart Redis
sudo systemctl restart redis-server
```

#### 4. Web Server Setup (Nginx)
```bash
# Configure Nginx as reverse proxy
sudo nano /etc/nginx/sites-available/music-producer

# Nginx configuration:
"""
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # AI Services
    location /ai/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

# Enable site
sudo ln -s /etc/nginx/sites-available/music-producer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Database Setup

### PostgreSQL Configuration

#### Development Configuration
```yaml
# config/database.development.yaml
database:
  host: localhost
  port: 5432
  name: musicdb
  user: musicuser
  password: musicpass
  ssl_mode: disable
  max_connections: 20
  connection_pool_size: 10
  connection_timeout: 30s
  idle_timeout: 10m
  max_idle_connections: 5
```

#### Production Configuration
```yaml
# config/database.production.yaml
database:
  host: localhost
  port: 5432
  name: musicdb
  user: musicuser
  password: ${DATABASE_PASSWORD}
  ssl_mode: require
  max_connections: 200
  connection_pool_size: 50
  connection_timeout: 60s
  idle_timeout: 30m
  max_idle_connections: 25
  backup_schedule: "0 2 * * *"  # Daily at 2 AM
  retention_days: 30
```

### Database Schema

#### User Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    subscription_plan VARCHAR(20) DEFAULT 'free',
    credits_balance INTEGER DEFAULT 100,
    preferences JSONB DEFAULT '{}'
);
```

#### Music Tracks Table
```sql
CREATE TABLE music_tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    mood VARCHAR(100)[] DEFAULT '{}',
    tempo INTEGER,
    duration INTEGER,
    audio_url TEXT NOT NULL,
    quality_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_public BOOLEAN DEFAULT FALSE,
    play_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0
);
```

#### Learning Data Table
```sql
CREATE TABLE learning_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,  -- 'video_tutorial', 'user_feedback', 'system_analysis'
    source_url TEXT,
    extracted_patterns JSONB NOT NULL,
    genre_influences VARCHAR(50)[] DEFAULT '{}',
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
```

---

## Cache Setup

### Redis Configuration

#### Development Configuration
```yaml
# config/redis.development.yaml
redis:
  host: localhost
  port: 6379
  password: ""
  db: 0
  pool_size: 10
  min_idle_connections: 2
  max_connection_age: 30m
  read_timeout: 5s
  write_timeout: 5s
  dial_timeout: 5s
  tls_enabled: false
```

#### Production Configuration
```yaml
# config/redis.production.yaml
redis:
  host: localhost
  port: 6379
  password: ${REDIS_PASSWORD}
  db: 0
  pool_size: 50
  min_idle_connections: 10
  max_connection_age: 1h
  read_timeout: 10s
  write_timeout: 10s
  dial_timeout: 10s
  tls_enabled: true
  tls_cert_path: "/etc/ssl/certs/redis.crt"
```

### Cache Strategies

#### 1. Session Cache
```go
// Go backend session caching
type SessionCache struct {
    client *redis.Client
}

func (c *SessionCache) GetSession(sessionID string) (*Session, error) {
    key := fmt.Sprintf("session:%s", sessionID)
    data, err := c.client.Get(context.Background(), key).Result()
    if err != nil {
        return nil, err
    }
    
    var session Session
    if err := json.Unmarshal([]byte(data), &session); err != nil {
        return nil, err
    }
    
    return &session, nil
}

func (c *SessionCache) SetSession(sessionID string, session *Session, expiration time.Duration) error {
    key := fmt.Sprintf("session:%s", sessionID)
    data, err := json.Marshal(session)
    if err != nil {
        return err
    }
    
    return c.client.Set(context.Background(), key, data, expiration).Err()
}
```

#### 2. API Response Cache
```python
# Python AI services API caching
import redis
import json
from datetime import timedelta

class APICache:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_cached_response(self, cache_key: str, expiration: timedelta = timedelta(hours=1)):
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Cache error: {e}")
        return None
    
    def cache_response(self, cache_key: str, data: dict, expiration: timedelta = timedelta(hours=1)):
        try:
            self.redis.setex(cache_key, int(expiration.total_seconds()), json.dumps(data))
        except Exception as e:
            print(f"Cache error: {e}")
```

---

## File Storage Setup

### Local Development Storage
```yaml
# config/storage.development.yaml
storage:
  type: "local"
  local:
    base_path: "./storage"
    directories:
      audio: "audio_files"
      models: "ai_models"
      uploads: "user_uploads"
      logs: "logs"
      backups: "backups"
  max_file_size: "100MB"
  allowed_extensions: ["mp3", "wav", "flac", "m4a", "json"]
```

### Production Storage Setup
```yaml
# config/storage.production.yaml
storage:
  type: "s3"
  s3:
    region: "us-east-1"
    bucket: "music-producer-audio"
    access_key_id: "${AWS_ACCESS_KEY_ID}"
    secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
  cdn:
    enabled: true
    domain: "cdn.your-domain.com"
    cloudfront_distribution_id: "${CLOUDFRONT_DISTRIBUTION_ID}"
  backup:
    enabled: true
    schedule: "0 3 * * *"  # Daily at 3 AM
    retention_days: 90
```

### Storage Structure
```
storage/
├── audio_files/           # Generated music files
│   ├── lofi/
│   ├── hyper_pop/
│   └── user_uploads/
├── ai_models/             # AI model files
│   ├── heartmula/
│   ├── ml_models/
│   └── cached_models/
├── user_uploads/          # User uploaded files
│   ├── video_tutorials/
│   └── reference_audio/
├── logs/                  # Application logs
│   ├── api/
│   ├── ai_services/
│   └── frontend/
└── backups/               # Database and file backups
    ├── daily/
    ├── weekly/
    └── monthly/
```

---

## Security Configuration

### Environment Variables
```bash
# .env.development
# Database
DATABASE_URL=postgresql://musicuser:musicpass@localhost:5432/musicdb

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# API Keys (for external services)
HEARTMULA_API_KEY=your-heartmula-api-key
OPENAI_API_KEY=your-openai-api-key

# File Storage
STORAGE_TYPE=local
STORAGE_BASE_PATH=./storage

# Logging
LOG_LEVEL=debug
LOG_FILE=./logs/development.log

# AI Service Settings
AI_MODEL_PATH=./ai/models
AI_MAX_GENERATIONS_PER_DAY=100
```

### Security Middleware

#### Go Backend Security
```go
// Security middleware
func SecurityMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // Security headers
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-XSS-Protection", "1; mode=block")
        c.Header("Content-Security-Policy", "default-src 'self'")
        
        // Rate limiting
        if !RateLimitCheck(c) {
            c.AbortWithStatusJSON(429, gin.H{"error": "Too many requests"})
            return
        }
        
        // CORS
        c.Header("Access-Control-Allow-Origin", os.Getenv("ALLOWED_ORIGINS"))
        c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        
        c.Next()
    }
}
```

#### Python AI Service Security
```python
# Security middleware for FastAPI
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("AI_SERVICE_API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    return api_key

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

---

## Monitoring & Logging

### Logging Configuration

#### Go Backend Logging
```go
// Go logging setup with Zap
package logger

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func NewLogger(config *Config) (*zap.Logger, error) {
    encoderConfig := zapcore.EncoderConfig{
        TimeKey:        "time",
        LevelKey:       "level",
        NameKey:        "logger",
        CallerKey:      "caller",
        FunctionKey:    zapcore.OmitKey,
        MessageKey:     "msg",
        StacktraceKey:  "stacktrace",
        LineEnding:     zapcore.DefaultLineEnding,
        EncodeLevel:    zapcore.LowercaseLevelEncoder,
        EncodeTime:     zapcore.ISO8601TimeEncoder,
        EncodeDuration: zapcore.SecondsDurationEncoder,
        EncodeCaller:   zapcore.ShortCallerEncoder,
    }

    var zapConfig zap.Config
    if config.Environment == "production" {
        zapConfig = zap.NewProductionConfig()
    } else {
        zapConfig = zap.NewDevelopmentConfig()
    }

    zapConfig.EncoderConfig = encoderConfig
    zapConfig.OutputPaths = []string{config.LogFile, "stdout"}
    
    return zapConfig.Build()
}
```

#### Python AI Service Logging
```python
# Python logging setup
import logging
import logging.handlers
from datetime import datetime

def setup_logging(config):
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        config.log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### Basic Monitoring
```bash
# Create monitoring scripts directory
mkdir -p scripts/monitoring

# Basic health check script
cat > scripts/monitoring/health_check.sh << 'EOF'
#!/bin/bash

# Check if services are running
check_service() {
    if systemctl is-active --quiet $1; then
        echo "$1: ✅ Running"
    else
        echo "$1: ❌ Stopped"
    fi
}

# Check services
echo "=== Service Status ==="
check_service postgresql
check_service redis-server
check_service nginx

# Check ports
echo -e "\n=== Port Status ==="
netstat -tuln | grep -E ':(3000|8080|8001|5432|6379)' || echo "No services found on expected ports"

# Check disk space
echo -e "\n=== Disk Space ==="
df -h | grep -E 'Filesystem|/dev/sda|/dev/vda'

# Check memory usage
echo -e "\n=== Memory Usage ==="
free -h

echo -e "\n=== Process Status ==="
ps aux | grep -E '(node|go|python)' | grep -v grep
EOF

chmod +x scripts/monitoring/health_check.sh
```

---

## Deployment Strategy

### Development Deployment
```bash
# Development startup script
cat > scripts/start_dev.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Music Producer Development Environment"

# Start database and cache
echo "📊 Starting database and cache..."
sudo systemctl start postgresql
sudo systemctl start redis-server

# Start backend API
echo "🔧 Starting Go backend..."
cd api
go run cmd/main.go &
API_PID=$!
cd ..

# Start AI services
echo "🤖 Starting Python AI services..."
cd ai
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8001 &
AI_PID=$!
cd ..

# Start frontend
echo "🎨 Starting React frontend..."
cd app
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ All services started successfully"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8080"
echo "🤖 AI Services: http://localhost:8001"

# Trap to cleanup on exit
trap cleanup INT
cleanup() {
    echo "🛑 Stopping services..."
    kill $API_PID $AI_PID $FRONTEND_PID
    exit 0
}

# Wait for processes
wait
EOF

chmod +x scripts/start_dev.sh
```

### Production Deployment (Later)
```bash
# Production deployment script
cat > scripts/deploy_prod.sh << 'EOF'
#!/bin/bash

echo "🚀 Deploying to Production"

# Build Go backend
echo "🔧 Building Go backend..."
cd api
go build -o music-api cmd/main.go
sudo systemctl stop music-api
sudo cp music-api /usr/local/bin/
sudo systemctl start music-api
cd ..

# Deploy Python AI services
echo "🤖 Deploying Python AI services..."
cd ai
sudo systemctl stop music-ai
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start music-ai
cd ..

# Build and deploy React frontend
echo "🎨 Building and deploying React frontend..."
cd app
npm run build
sudo rm -rf /var/www/music-producer/*
sudo cp -r build/* /var/www/music-producer/
cd ..

# Restart nginx
echo "🌐 Restarting web server..."
sudo systemctl restart nginx

echo "✅ Production deployment completed"
EOF

chmod +x scripts/deploy_prod.sh
```

---

## Scaling Considerations

### Horizontal Scaling Strategy
When you're ready to scale beyond a single server, consider this progression:

#### Phase 1: Single Server Optimization
- **Database:** Read replicas, connection pooling
- **Cache:** Redis with persistence
- **File Storage:** Local SSD with backup to cloud
- **Load:** Nginx as reverse proxy and load balancer

#### Phase 2: Multiple Servers
- **Application:** Multiple backend servers behind load balancer
- **Database:** Primary + read replica setup
- **Cache:** Redis cluster or Sentinel
- **Files:** Cloud storage (S3, Google Cloud Storage)

#### Phase 3: Cloud Migration
- **Compute:** Cloud VMs or container orchestration
- **Database:** Managed database service
- **Cache:** Managed Redis service
- **Storage:** Cloud storage with CDN

#### Phase 4: Advanced Scaling
- **Containers:** Docker containers with orchestration
- **Kubernetes:** For automated scaling and management
- **Microservices:** Further service decomposition
- **Global:** Multi-region deployment

### Performance Optimization Tips

#### Database Optimization
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_music_tracks_user_id ON music_tracks(user_id);
CREATE INDEX idx_music_tracks_genre ON music_tracks(genre);
CREATE INDEX idx_music_tracks_created_at ON music_tracks(created_at);

-- Optimize PostgreSQL configuration
-- Adjust shared_buffers, work_mem, maintenance_work_mem based on available RAM
```

#### Cache Optimization
```python
# Cache frequently accessed data
def get_user_preferences(user_id):
    cache_key = f"user:{user_id}:preferences"
    cached_data = redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # Cache miss - fetch from database
    preferences = database.get_user_preferences(user_id)
    redis.setex(cache_key, 3600, json.dumps(preferences))  # Cache for 1 hour
    return preferences
```

#### Frontend Optimization
```javascript
// Implement lazy loading and code splitting
const LazyAudioPlayer = React.lazy(() => import('./components/AudioPlayer'));

// Use React Query for data caching
const { data: user, isLoading } = useQuery(
  ['user', userId],
  () => api.getUser(userId),
  { staleTime: 5 * 60 * 1000 } // Cache for 5 minutes
);
```

---

## Next Steps

1. **Start Development:** Begin with the single-server setup
2. **Build MVP:** Focus on core functionality first
3. **Test Thoroughly:** Ensure all components work together
4. **Monitor Performance:** Use basic monitoring scripts
5. **Plan Scaling:** Prepare for when you need to scale
6. **Document Everything:** Keep documentation updated

This infrastructure setup provides a solid foundation for your Auto LoFi & Hyper Pop Music Producer without the complexity of containers and orchestration. You can always add Docker and Kubernetes later when the application grows and scaling becomes necessary.