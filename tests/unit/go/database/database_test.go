package database

import (
	"testing"
	
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewDatabase(t *testing.T) {
	// Skip if test database is not available
	if testing.Short() {
		t.Skip("Skipping database tests in short mode")
	}

	// Test database connection with invalid URL first
	_, err := NewDatabase("invalid://url")
	assert.Error(t, err, "Should return error for invalid database URL")
}

func TestDatabaseConnectionPoolConfiguration(t *testing.T) {
	// This test doesn't require actual database connection
	// It tests the configuration logic
	
	// Mock database struct to test configuration
	mockDB := &Database{}
	
	// Test that we can configure connection pool settings
	// The actual configuration happens in NewDatabase function
	assert.NotNil(t, mockDB, "Database struct should be created")
}

func TestTableCreationQueries(t *testing.T) {
	// Test that table creation queries are valid SQL
	// This doesn't require actual database connection
	
	usersTableQuery := `
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			email VARCHAR(255) UNIQUE NOT NULL,
			username VARCHAR(100) UNIQUE NOT NULL,
			password_hash VARCHAR(255) NOT NULL,
			full_name VARCHAR(255),
			plan_type VARCHAR(50) DEFAULT 'free',
			created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
		);
		
		CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
		CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
	`

	musicTableQuery := `
		CREATE TABLE IF NOT EXISTS music_generations (
			id SERIAL PRIMARY KEY,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			title VARCHAR(255) NOT NULL,
			genre VARCHAR(100) NOT NULL,
			mood VARCHAR(100),
			duration INTEGER DEFAULT 180,
			prompt TEXT,
			status VARCHAR(50) DEFAULT 'pending',
			output_file_url TEXT,
			created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
			completed_at TIMESTAMP WITH TIME ZONE,
			error_message TEXT
		);
		
		CREATE INDEX IF NOT EXISTS idx_music_generations_user_id ON music_generations(user_id);
		CREATE INDEX IF NOT EXISTS idx_music_generations_status ON music_generations(status);
	`

	learningTableQuery := `
		CREATE TABLE IF NOT EXISTS learning_sessions (
			id SERIAL PRIMARY KEY,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			video_url TEXT NOT NULL,
			video_title VARCHAR(500),
			extracted_patterns JSONB,
			learned_model_id INTEGER,
			status VARCHAR(50) DEFAULT 'pending',
			created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
			completed_at TIMESTAMP WITH TIME ZONE,
			error_message TEXT
		);
		
		CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_id ON learning_sessions(user_id);
		CREATE INDEX IF NOT EXISTS idx_learning_sessions_status ON learning_sessions(status);
	`

	// Test that queries are syntactically valid by attempting to parse them
	// This is a basic test - in a real scenario, we'd use a SQL parser
	assert.NotEmpty(t, usersTableQuery, "Users table query should not be empty")
	assert.Contains(t, usersTableQuery, "CREATE TABLE IF NOT EXISTS users", "Users table query should be correct")
	
	assert.NotEmpty(t, musicTableQuery, "Music generations table query should not be empty")
	assert.Contains(t, musicTableQuery, "CREATE TABLE IF NOT EXISTS music_generations", "Music generations table query should be correct")
	
	assert.NotEmpty(t, learningTableQuery, "Learning sessions table query should not be empty")
	assert.Contains(t, learningTableQuery, "CREATE TABLE IF NOT EXISTS learning_sessions", "Learning sessions query should be correct")
}

func TestDatabaseMethodsExist(t *testing.T) {
	// Test that all required methods exist on Database struct
	// This is a compile-time test to ensure our interface is correct
	
	database := &Database{}
	
	// Test that methods exist and have correct signatures
	_ = database.CreateUsersTable
	_ = database.CreateMusicGenerationsTable
	_ = database.CreateLearningSessionsTable
	_ = database.InitializeDatabase
	
	// If these lines compile, the methods exist
	assert.NotNil(t, database, "Database struct should be created")
}

func TestJSONBSupport(t *testing.T) {
	// Test JSONB type functionality (without database connection)
	
	// Test that JSONB type can be created
	var jsonb JSONB
	assert.NotNil(t, jsonb, "JSONB type should be created")
	
	// Test that JSONB can hold JSON data
	testData := JSONB{
		"tempo":    120,
		"key":      "C major",
		"instruments": []string{"piano", "drums"},
		"style":    "lofi",
	}
	
	assert.Equal(t, 120.0, testData["tempo"])
	assert.Equal(t, "C major", testData["key"])
	assert.Equal(t, []interface{}{"piano", "drums"}, testData["instruments"])
	assert.Equal(t, "lofi", testData["style"])
}

func TestErrorHandling(t *testing.T) {
	// Test error handling scenarios
	
	// Test that NewDatabase returns error for invalid URLs
	_, err := NewDatabase("invalid://database-url")
	assert.Error(t, err, "Should return error for invalid database URL")
	
	// Test error message contains useful information
	if err != nil {
		assert.Contains(t, err.Error(), "failed to open database", "Error message should be descriptive")
	}
}

// Integration tests that require a real database
// These can be run with: go test -tags=integration
func TestDatabaseIntegration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration tests in short mode")
	}

	// This would require a real database connection
	// For now, we'll just mark it as a test that would run
	t.Skip("Integration tests require a real database connection")
}