# Auto LoFi & Hyper Pop Music Producer - Testing Guide

## 🎯 Testing Strategy
- **Unit Tests:** Individual component testing
- **Integration Tests:** API endpoint testing
- **E2E Tests:** Full workflow testing (future)

---

## 📁 Testing Structure
```
tests/
├── 📂 unit/                    # Unit tests
│   ├── 📂 go/                 # Go backend unit tests
│   │   ├── 📄 models_test.go
│   │   ├── 📄 handlers_test.go
│   │   ├── 📄 middleware_test.go
│   │   └── 📄 database_test.go
│   └── 📂 react/              # React frontend unit tests
│       ├── 📄 components/
│       ├── 📄 hooks/
│       └── 📄 utils/
├── 📂 integration/            # Integration tests
│   ├── 📄 api_test.go         # Go API integration tests
│   ├── 📄 database_test.go    # Database integration tests
│   └── 📂 e2e/               # End-to-end tests (future)
├── 📂 fixtures/               # Test data
│   ├── 📄 users.json
│   ├── 📄 music_generations.json
│   └── 📄 learning_sessions.json
├── 📂 testutils/              # Test utilities
│   ├── 📄 setup.go
│   ├── 📄 database.go
│   └── 📄 fixtures.go
└── 📄 README.md               # This file
```

---

## 🧪 Test Coverage Goals

### Go Backend
- **Models:** 95% coverage
- **Handlers:** 90% coverage  
- **Database:** 95% coverage
- **Middleware:** 90% coverage

### React Frontend
- **Components:** 85% coverage
- **Hooks:** 90% coverage
- **Utils:** 95% coverage

---

## 🚀 Running Tests

### Go Tests
```bash
# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Run with coverage profile
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Run specific test file
go test ./api/internal/models
```

### React Tests
```bash
# Install test dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Integration Tests
```bash
# Setup test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
go test -tags=integration ./tests/integration

# Cleanup
docker-compose -f docker-compose.test.yml down
```

---

## 📊 Test Reports

### Coverage Reports
- Go: `coverage.out` + HTML report
- React: `coverage/lcov-report/index.html`
- Integration: Test results in `test-results/`

### CI/CD Integration
- Tests run on every push
- Coverage requirements enforced
- Failed tests block deployment

---
*Last Updated: May 22, 2026 1:15 PM*