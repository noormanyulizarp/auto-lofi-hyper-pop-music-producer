# Test Suite — Auto LoFi & Hyper Pop Music Producer

## Structure

```
tests/
├── unit/              # Unit tests
│   ├── go/           # Go unit tests
│   └── react/        # React component tests
├── integration/       # Integration tests
├── e2e/              # End-to-end tests
├── fixtures/         # Test data
│   ├── music_generations.json
│   ├── learning_sessions.json
│   └── users.json
├── testutils/        # Test utilities (Go)
│   ├── database.go
│   └── fixtures.go
└── README.md

ai/tests/             # Python AI service tests
├── test_api_endpoints.py
├── test_audio_feature_extractor.py
├── test_music_ai_service.py
├── test_provider_service.py
├── test_video_analysis.py
├── fixtures.py
├── factories.py
├── mocks.py
└── helpers.py
```

## Running Tests

### Python AI Tests
```bash
cd ai
source .venv/bin/activate
pytest tests/ -v
```

### Go Gateway Tests
```bash
cd api
go test ./...
```

### React Frontend Tests
```bash
cd app
pnpm test
```

### Integration Tests
```bash
# Requires all services running
cd tests/integration
go test ./...
```
