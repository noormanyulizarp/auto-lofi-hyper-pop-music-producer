package testutils

import (
	"database/sql"
	"fmt"
	"os"
	"testing"
	
	"auto-music-producer/api/pkg/database"
	
	"github.com/stretchr/testify/require"
)

// TestDatabaseConfig holds configuration for test database
type TestDatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	Database string
}

// DefaultTestDatabaseConfig returns default test database configuration
func DefaultTestDatabaseConfig() *TestDatabaseConfig {
	return &TestDatabaseConfig{
		Host:     "localhost",
		Port:     5432,
		User:     "testuser",
		Password: "testpass",
		Database: "musicdb_test",
	}
}

// CreateTestDatabase creates a test database and returns connection
func CreateTestDatabase(t *testing.T, config *TestDatabaseConfig) *sql.DB {
	t.Helper()

	// Check if test database URL is provided via environment variable
	testDBURL := os.Getenv("TEST_DATABASE_URL")
	if testDBURL == "" {
		// Build test database URL from config
		testDBURL = fmt.Sprintf("postgres://%s:%s@%s:%d/%s?sslmode=disable",
			config.User, config.Password, config.Host, config.Port, config.Database)
	}

	// Connect to the database
	db, err := database.NewDatabase(testDBURL)
	require.NoError(t, err, "Failed to connect to test database")

	// Initialize database tables
	err = db.InitializeDatabase()
	require.NoError(t, err, "Failed to initialize test database tables")

	// Cleanup function
	t.Cleanup(func() {
		// Clean up test data
		cleanupTestData(t, db)
		
		// Close database connection
		err := db.Close()
		require.NoError(t, err, "Failed to close test database connection")
	})

	return db.DB
}

// cleanupTestData removes all test data from the database
func cleanupTestData(t *testing.T, db *database.Database) {
	t.Helper()

	// Delete data from all tables in correct order to respect foreign keys
	tables := []string{
		"learning_sessions",
		"music_generations",
		"users",
	}

	for _, table := range tables {
		_, err := db.Exec(fmt.Sprintf("TRUNCATE TABLE %s CASCADE", table))
		require.NoError(t, err, "Failed to truncate table %s", table)
	}
}

// CreateTestUser creates a test user in the database
func CreateTestUser(t *testing.T, db *sql.DB) int {
	t.Helper()

	var userID int
	err := db.QueryRow(`
		INSERT INTO users (email, username, password_hash, full_name, plan_type)
		VALUES ($1, $2, $3, $4, $5)
		RETURNING id`,
		"test@example.com",
		"testuser",
		"hashed_password",
		"Test User",
		"free",
	).Scan(&userID)

	require.NoError(t, err, "Failed to create test user")
	return userID
}

// CreateTestMusicGeneration creates a test music generation record
func CreateTestMusicGeneration(t *testing.T, db *sql.DB, userID int) int {
	t.Helper()

	var generationID int
	err := db.QueryRow(`
		INSERT INTO music_generations 
		(user_id, title, genre, mood, duration, prompt, status)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING id`,
		userID,
		"Test LoFi Track",
		"lofi",
		"chill",
		180,
		"Generate a relaxing lofi track",
		"completed",
	).Scan(&generationID)

	require.NoError(t, err, "Failed to create test music generation")
	return generationID
}

// CreateTestLearningSession creates a test learning session
func CreateTestLearningSession(t *testing.T, db *sql.DB, userID int) int {
	t.Helper()

	var sessionID int
	err := db.QueryRow(`
		INSERT INTO learning_sessions 
		(user_id, video_url, video_title, status)
		VALUES ($1, $2, $3, $4)
		RETURNING id`,
		userID,
		"https://example.com/video.mp4",
		"LoFi Tutorial",
		"completed",
	).Scan(&sessionID)

	require.NoError(t, err, "Failed to create test learning session")
	return sessionID
}