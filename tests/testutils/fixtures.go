package testutils

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
	
	"github.com/stretchr/testify/require"
)

// TestUser represents a test user fixture
type TestUser struct {
	ID           int    `json:"id"`
	Email        string `json:"email"`
	Username     string `json:"username"`
	Password     string `json:"password"`
	FullName     string `json:"full_name"`
	PlanType     string `json:"plan_type"`
}

// TestMusicGeneration represents a test music generation fixture
type TestMusicGeneration struct {
	ID        int    `json:"id"`
	UserID    int    `json:"user_id"`
	Title     string `json:"title"`
	Genre     string `json:"genre"`
	Mood      string `json:"mood"`
	Duration  int    `json:"duration"`
	Prompt    string `json:"prompt"`
	Status    string `json:"status"`
}

// TestLearningSession represents a test learning session fixture
type TestLearningSession struct {
	ID                int    `json:"id"`
	UserID            int    `json:"user_id"`
	VideoURL          string `json:"video_url"`
	VideoTitle        string `json:"video_title"`
	Status            string `json:"status"`
}

// LoadTestUsers loads test user fixtures from JSON file
func LoadTestUsers(t *testing.T) []TestUser {
	t.Helper()

	users := make([]TestUser, 0)
	err := loadJSONFixture(t, "users.json", &users)
	require.NoError(t, err, "Failed to load test users")

	return users
}

// LoadTestMusicGenerations loads test music generation fixtures from JSON file
func LoadTestMusicGenerations(t *testing.T) []TestMusicGeneration {
	t.Helper()

	generations := make([]TestMusicGeneration, 0)
	err := loadJSONFixture(t, "music_generations.json", &generations)
	require.NoError(t, err, "Failed to load test music generations")

	return generations
}

// LoadTestLearningSessions loads test learning session fixtures from JSON file
func LoadTestLearningSessions(t *testing.T) []TestLearningSession {
	t.Helper()

	sessions := make([]TestLearningSession, 0)
	err := loadJSONFixture(t, "learning_sessions.json", &sessions)
	require.NoError(t, err, "Failed to load test learning sessions")

	return sessions
}

// loadJSONFixture loads a JSON fixture file
func loadJSONFixture(t *testing.T, filename string, target interface{}) error {
	t.Helper()

	// Get fixtures directory path
	fixturesDir := getFixturesDir()
	filePath := filepath.Join(fixturesDir, filename)

	// Read the file
	data, err := os.ReadFile(filePath)
	if err != nil {
		return err
	}

	// Unmarshal JSON
	return json.Unmarshal(data, target)
}

// getFixturesDir returns the path to the fixtures directory
func getFixturesDir() string {
	// Start from current directory and find fixtures dir
	currentDir, _ := os.Getwd()
	for {
		fixturesPath := filepath.Join(currentDir, "tests", "fixtures")
		if _, err := os.Stat(fixturesPath); err == nil {
			return fixturesPath
		}

		// Move up one directory
		parent := filepath.Dir(currentDir)
		if parent == currentDir {
			// Reached root directory
			break
		}
		currentDir = parent
	}

	// Fallback to current directory
	return "tests/fixtures"
}

// GetDefaultTestUser returns a default test user
func GetDefaultTestUser() TestUser {
	return TestUser{
		Email:    "test@example.com",
		Username: "testuser",
		Password: "testpass123",
		FullName: "Test User",
		PlanType: "free",
	}
}

// GetDefaultMusicGeneration returns a default test music generation
func GetDefaultMusicGeneration() TestMusicGeneration {
	return TestMusicGeneration{
		Title:    "Test LoFi Track",
		Genre:    "lofi",
		Mood:     "chill",
		Duration: 180,
		Prompt:   "Generate a relaxing lofi track",
		Status:   "pending",
	}
}

// GetDefaultLearningSession returns a default test learning session
func GetDefaultLearningSession() TestLearningSession {
	return TestLearningSession{
		VideoURL:   "https://example.com/video.mp4",
		VideoTitle: "LoFi Tutorial",
		Status:     "pending",
	}
}