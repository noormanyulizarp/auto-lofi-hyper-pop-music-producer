# Development Guide - Auto Lofi & Hyper Pop Music Producer

## **Overview**

This guide provides comprehensive instructions for developers working on the Auto Lofi & Hyper Pop Music Producer project. It covers setup, development workflow, coding standards, and best practices.

## **Prerequisites**

### **System Requirements**
- **Operating System:** Linux, macOS, Windows (with WSL2)
- **Memory:** 8GB RAM minimum, 16GB recommended
- **Storage:** 20GB free space
- **Docker:** Docker 20.10+
- **Node.js:** 18.x or higher
- **Python:** 3.9 or higher
- **Go:** 1.19 or higher
- **PostgreSQL:** 14.x or higher
- **Redis:** 6.x or higher

### **Required Tools**
- **Git:** Version control
- **Docker Compose:** Multi-container applications
- **Make:** Build automation
- **VS Code:** Recommended IDE with extensions
- **Postman:** API testing
- **pgAdmin:** Database management

## **Project Setup**

### **1. Clone Repository**
```bash
git clone <repository-url> /root/producy
cd /root/producy
```

### **2. Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/music_prod
REDIS_URL=redis://localhost:6379
VECTOR_DB_URL=qdrant://localhost:6333

# AI Providers
SUNO_API_KEY=your_suno_api_key
YUE_MODEL_PATH=/models/yue
RIFFUSION_MODEL_PATH=/models/riffusion

# External Services
STRIPE_SECRET_KEY=your_stripe_secret
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Security
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Storage
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=your_bucket_name
```

### **3. Install Dependencies**

#### **Backend (Python)**
```bash
cd src/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

#### **Frontend (TypeScript/React)**
```bash
cd src/frontend

# Install Node.js dependencies
npm install

# Install development dependencies
npm install --dev
```

#### **Services (Golang)**
```bash
# Install Go dependencies for each service
cd src/services/auth-service
go mod tidy

cd ../music-service
go mod tidy

cd ../storage-service
go mod tidy

cd ../payment-service
go mod tidy

cd ../distribution-service
go mod tidy
```

### **4. Database Setup**
```bash
# Start development services
docker-compose -f ../infrastructure/docker/docker-compose.dev.yml up -d postgres redis

# Run database migrations
cd src/backend
python manage.py migrate

# Load initial data
python manage.py loaddata initial_data
```

### **5. Start Development Servers**

#### **Option A: Individual Services (Recommended for Development)**
```bash
# Terminal 1: Start backend
cd src/backend
python main.py

# Terminal 2: Start frontend
cd src/frontend
npm start

# Terminal 3: Start auth service
cd src/services/auth-service
go run cmd/main.go

# Terminal 4: Start music service
cd src/services/music-service
go run cmd/main.go

# Continue with other services as needed...
```

#### **Option B: Docker Compose (All Services)**
```bash
# Start all services
docker-compose -f ../infrastructure/docker/docker-compose.dev.yml up

# Build and start
docker-compose -f ../infrastructure/docker/docker-compose.dev.yml up --build
```

## **Development Workflow**

### **1. Feature Development**

#### **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

#### **Development Steps**
1. **Plan:** Understand requirements and create implementation plan
2. **Code:** Write code following the project standards
3. **Test:** Write and run tests
4. **Review:** Self-review and team review
5. **Deploy:** Deploy to development environment

#### **Commit Standards**
```bash
# Format: <type>(<scope>): <description>
# Types: feat, fix, docs, style, refactor, test, chore

# Examples
git commit -m "feat(auth): add OAuth2 Google integration"
git commit -m "fix(music): resolve audio playback stuttering"
git commit -m "docs(readme): update installation instructions"
git commit -m "style(frontend): improve responsive design"
git commit -m "refactor(backend): optimize database queries"
git commit -m "test(auth): add unit tests for JWT validation"
git commit -m "chore(deps): update dependencies"
```

### **2. Code Organization**

#### **File Naming Conventions**
- **Python:** snake_case.py (e.g., `user_service.py`)
- **Go:** camelCase.go (e.g., `userService.go`)
- **TypeScript:** camelCase.ts (e.g., `userService.ts`)
- **Components:** PascalCase.tsx (e.g., `MusicPlayer.tsx`)
- **Tests:** *_test.py, *_test.go, *.test.ts

#### **Directory Structure Guidelines**
```
Component/
├── index.tsx            # Main component file
├── styles.ts           # Styled components
├── hooks.ts            # Custom hooks
├── utils.ts            # Utility functions
├── types.ts            # TypeScript types
├── constants.ts        # Constants
└── __tests__/          # Test files
    ├── component.test.ts
    └── hooks.test.ts
```

### **3. Testing**

#### **Testing Strategy**
- **Unit Tests:** Individual components and functions
- **Integration Tests:** Service interactions
- **End-to-End Tests:** Complete user flows
- **Performance Tests:** Load and stress testing

#### **Running Tests**
```bash
# Backend tests
cd src/backend
pytest
pytest --cov=.           # With coverage
pytest --cov=report html # HTML coverage report

# Frontend tests
cd src/frontend
npm test
npm test -- --coverage   # With coverage
npm test -- --watch       # Watch mode

# Go services tests
cd src/services/auth-service
go test ./...
go test -cover ./...      # With coverage
```

#### **Test Examples**
```python
# Python unit test
def test_music_generation():
    # Arrange
    generator = MusicGenerator()
    prompt = "lofi music"
    
    # Act
    result = generator.generate(prompt)
    
    # Assert
    assert result is not None
    assert result.duration > 0
    assert result.format == "wav"
```

```typescript
// TypeScript unit test
import { render, screen } from '@testing-library/react';
import { MusicPlayer } from './MusicPlayer';

test('renders music player component', () => {
  render(<MusicPlayer />);
  const playerElement = screen.getByTestId('music-player');
  expect(playerElement).toBeInTheDocument();
});
```

```go
// Go unit test
func TestAuthMiddleware(t *testing.T) {
    req := httptest.NewRequest("GET", "/protected", nil)
    w := httptest.NewRecorder()
    
    handler := http.HandlerFunc(authMiddleware)
    handler.ServeHTTP(w, req)
    
    if w.Code != http.StatusOK {
        t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
    }
}
```

### **4. Code Quality**

#### **Linting and Formatting**
```bash
# Python linting
cd src/backend
flake8 .
black .
isort .

# Go formatting
cd src/services/auth-service
go fmt ./...
golangci-lint run

# TypeScript linting
cd src/frontend
npm run lint
npm run format
```

#### **Code Review Checklist**
- [ ] Code follows project standards
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive data in code
- [ ] Performance considerations
- [ ] Security implications
- [ ] Error handling is robust
- [ ] Logging is appropriate

### **5. Debugging**

#### **Debugging Tools**
- **Backend:** Python debugger (pdb), logging
- **Frontend:** React DevTools, browser debugger
- **Services:** Go debugger (delve), logging
- **Database:** pgAdmin, query logs
- **API:** Postman, curl, swagger UI

#### **Common Debugging Commands**
```bash
# Backend debugging
python -m pdb main.py
tail -f logs/backend.log

# Frontend debugging
npm run dev
# Open Chrome DevTools

# Service debugging
go run -tags debug cmd/main.go
docker logs -f service-name

# Database debugging
psql $DATABASE_URL
EXPLAIN ANALYZE SELECT * FROM users;
```

## **Deployment**

### **1. Development Deployment**
```bash
# Build and start development environment
docker-compose -f infrastructure/docker/docker-compose.dev.yml up --build

# Stop services
docker-compose -f infrastructure/docker/docker-compose.dev.yml down

# Clean up
docker-compose -f infrastructure/docker/docker-compose.dev.yml down -v
```

### **2. Production Deployment**
```bash
# Build production images
docker-compose -f infrastructure/docker/docker-compose.prod.yml build

# Deploy to production
docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d

# Health check
docker-compose -f infrastructure/docker/docker-compose.prod.yml ps
```

### **3. Kubernetes Deployment**
```bash
# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/

# Check deployment status
kubectl get pods -n music-prod
kubectl get services -n music-prod

# Update deployment
kubectl apply -f infrastructure/kubernetes/deployments/backend-deployment.yaml
```

## **API Documentation**

### **1. Swagger/OpenAPI Documentation**
- **Backend API:** `http://localhost:8000/docs` (FastAPI auto-docs)
- **Service APIs:** Check each service's documentation
- **GraphQL Schema:** `http://localhost:4000/graphql` (if using GraphQL)

### **2. API Usage Examples**

#### **Authentication**
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### **Music Generation**
```bash
# Generate music
curl -X POST http://localhost:8000/api/v1/music/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "genre": "lofi",
    "duration": 120,
    "tempo": 90,
    "mood": "chill",
    "instruments": ["piano", "drums", "bass"]
  }'

# Response
{
  "id": "music_123",
  "title": "Lofi Chill Beats",
  "duration": 120,
  "status": "processing",
  "download_url": "http://localhost:8000/api/v1/music/123/download"
}
```

## **Performance Optimization**

### **1. Frontend Optimization**
- **Code Splitting:** Lazy load components
- **Image Optimization:** Compress images, use WebP
- **Caching:** Service workers, browser caching
- **Bundle Size:** Tree shaking, minification

### **2. Backend Optimization**
- **Database:** Index queries, use connection pooling
- **Caching:** Redis for frequent queries
- **Async Processing:** Background tasks for heavy operations
- **API Rate Limiting:** Prevent abuse

### **3. Service Optimization**
- **Go:** Use goroutines for concurrency
- **Connection Pooling:** Reuse database connections
- **Memory Management:** Profile and optimize memory usage
- **Load Balancing:** Distribute requests

## **Security Best Practices**

### **1. Authentication & Authorization**
- Use JWT for stateless authentication
- Implement OAuth2 for third-party login
- Role-based access control (RBAC)
- Token expiration and refresh

### **2. Data Security**
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Validate and sanitize all inputs
- Implement rate limiting

### **3. API Security**
- API key management
- Request validation
- Error message sanitization
- CORS configuration

## **Troubleshooting**

### **Common Issues**

#### **Database Connection Issues**
```bash
# Check PostgreSQL status
docker exec -it postgres psql -U user -d music_prod

# Check Redis status
docker exec -it redis redis-cli ping

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### **Service Communication Issues**
```bash
# Check service logs
docker logs -f backend-service
docker logs -f auth-service

# Test service health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

#### **Frontend Build Issues**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear cache
npm run clean
npm run build
```

### **Debugging Checklist**
1. Check service logs
2. Verify environment variables
3. Test database connection
4. Check network connectivity
5. Validate API endpoints
6. Review recent code changes

## **Contributing Guidelines**

### **1. Before Contributing**
1. Fork the repository
2. Create a feature branch
3. Install dependencies
4. Set up development environment
5. Run tests locally

### **2. Making Changes**
1. Write code following project standards
2. Add appropriate tests
3. Update documentation
4. Run linting and formatting
5. Test changes thoroughly

### **3. Submitting Changes**
1. Commit changes with descriptive messages
2. Push to your fork
3. Create pull request
4. Respond to code review feedback
5. Merge after approval

---

*Development Guide v1.0 - Auto Lofi & Hyper Pop Music Producer*
*Last Updated: 2026-05-22*