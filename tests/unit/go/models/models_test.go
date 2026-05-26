package models

import (
	"testing"
	"time"
	
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestUserModel(t *testing.T) {
	// Test user creation
	user := User{
		ID:        1,
		Email:     "test@example.com",
		Username:  "testuser",
		FullName:  "Test User",
		PlanType:  "free",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Test user fields
	assert.Equal(t, 1, user.ID)
	assert.Equal(t, "test@example.com", user.Email)
	assert.Equal(t, "testuser", user.Username)
	assert.Equal(t, "Test User", user.FullName)
	assert.Equal(t, "free", user.PlanType)
	assert.NotZero(t, user.CreatedAt)
	assert.NotZero(t, user.UpdatedAt)
}

func TestMusicGenerationModel(t *testing.T) {
	now := time.Now()
	completedAt := time.Now()

	music := MusicGeneration{
		ID:            1,
		UserID:        1,
		Title:         "Test LoFi Track",
		Genre:         "lofi",
		Mood:          "chill",
		Duration:      180,
		Prompt:        "Generate a relaxing lofi track",
		Status:        "completed",
		OutputFileURL: "https://example.com/track.mp3",
		CreatedAt:     now,
		CompletedAt:   &completedAt,
		ErrorMessage:  "",
	}

	// Test music generation fields
	assert.Equal(t, 1, music.ID)
	assert.Equal(t, 1, music.UserID)
	assert.Equal(t, "Test LoFi Track", music.Title)
	assert.Equal(t, "lofi", music.Genre)
	assert.Equal(t, "chill", music.Mood)
	assert.Equal(t, 180, music.Duration)
	assert.Equal(t, "Generate a relaxing lofi track", music.Prompt)
	assert.Equal(t, "completed", music.Status)
	assert.Equal(t, "https://example.com/track.mp3", music.OutputFileURL)
	assert.Equal(t, now, music.CreatedAt)
	assert.NotNil(t, music.CompletedAt)
	assert.Equal(t, completedAt, *music.CompletedAt)
	assert.Empty(t, music.ErrorMessage)
}

func TestLearningSessionModel(t *testing.T) {
	now := time.Now()
	completedAt := time.Now()
	modelID := 1
	patterns := JSONB{
		"tempo":    120,
		"key":      "C major",
		"instruments": []string{"piano", "drums"},
		"style":    "lofi",
	}

	session := LearningSession{
		ID:                1,
		UserID:            1,
		VideoURL:          "https://example.com/video.mp4",
		VideoTitle:        "LoFi Tutorial",
		ExtractedPatterns: patterns,
		LearnedModelID:    &modelID,
		Status:            "completed",
		CreatedAt:         now,
		CompletedAt:       &completedAt,
		ErrorMessage:      "",
	}

	// Test learning session fields
	assert.Equal(t, 1, session.ID)
	assert.Equal(t, 1, session.UserID)
	assert.Equal(t, "https://example.com/video.mp4", session.VideoURL)
	assert.Equal(t, "LoFi Tutorial", session.VideoTitle)
	assert.Equal(t, patterns, session.ExtractedPatterns)
	assert.NotNil(t, session.LearnedModelID)
	assert.Equal(t, modelID, *session.LearnedModelID)
	assert.Equal(t, "completed", session.Status)
	assert.Equal(t, now, session.CreatedAt)
	assert.NotNil(t, session.CompletedAt)
	assert.Equal(t, completedAt, *session.CompletedAt)
	assert.Empty(t, session.ErrorMessage)
}

func TestJSONBValue(t *testing.T) {
	patterns := JSONB{
		"tempo":    120,
		"key":      "C major",
		"instruments": []string{"piano", "drums"},
		"style":    "lofi",
	}

	value, err := patterns.Value()
	require.NoError(t, err)
	assert.NotNil(t, value)
}

func TestJSONBScan(t *testing.T) {
	// Test scanning valid JSON
	validJSON := []byte(`{"tempo":120,"key":"C major","instruments":["piano","drums"],"style":"lofi"}`)
	var j JSONB

	err := j.Scan(validJSON)
	require.NoError(t, err)
	assert.Equal(t, 120.0, j["tempo"])
	assert.Equal(t, "C major", j["key"])
	assert.Equal(t, []interface{}{"piano", "drums"}, j["instruments"])
	assert.Equal(t, "lofi", j["style"])

	// Test scanning nil value
	var j2 JSONB
	err = j2.Scan(nil)
	require.NoError(t, err)
	assert.Nil(t, j2)

	// Test scanning invalid type
	var j3 JSONB
	err = j3.Scan("invalid")
	require.Error(t, err)
}

func TestRegisterRequestValidation(t *testing.T) {
	// Test valid request
	validReq := RegisterRequest{
		Email:    "test@example.com",
		Username: "testuser",
		Password: "password123",
		FullName: "Test User",
	}

	assert.Equal(t, "test@example.com", validReq.Email)
	assert.Equal(t, "testuser", validReq.Username)
	assert.Equal(t, "password123", validReq.Password)
	assert.Equal(t, "Test User", validReq.FullName)
}

func TestLoginRequestValidation(t *testing.T) {
	// Test valid request
	validReq := LoginRequest{
		Email:    "test@example.com",
		Password: "password123",
	}

	assert.Equal(t, "test@example.com", validReq.Email)
	assert.Equal(t, "password123", validReq.Password)
}

func TestGenerateMusicRequestValidation(t *testing.T) {
	// Test valid request
	validReq := GenerateMusicRequest{
		Title:    "Test Track",
		Genre:    "lofi",
		Mood:     "chill",
		Duration: 180,
		Prompt:   "Generate a relaxing track",
		Model:    "heartmula",
	}

	assert.Equal(t, "Test Track", validReq.Title)
	assert.Equal(t, "lofi", validReq.Genre)
	assert.Equal(t, "chill", validReq.Mood)
	assert.Equal(t, 180, validReq.Duration)
	assert.Equal(t, "Generate a relaxing track", validReq.Prompt)
	assert.Equal(t, "heartmula", validReq.Model)
}

func TestAnalyzeVideoRequestValidation(t *testing.T) {
	// Test valid request
	validReq := AnalyzeVideoRequest{
		VideoURL:  "https://example.com/video.mp4",
		Title:     "Music Tutorial",
		FocusType: "rhythm",
	}

	assert.Equal(t, "https://example.com/video.mp4", validReq.VideoURL)
	assert.Equal(t, "Music Tutorial", validReq.Title)
	assert.Equal(t, "rhythm", validReq.FocusType)
}

func TestAPIResponse(t *testing.T) {
	// Test successful response
	successResp := APIResponse{
		Success: true,
		Message: "Operation successful",
		Data:    map[string]interface{}{"id": 1},
	}

	assert.True(t, successResp.Success)
	assert.Equal(t, "Operation successful", successResp.Message)
	assert.Equal(t, map[string]interface{}{"id": 1}, successResp.Data)
	assert.Empty(t, successResp.Error)

	// Test error response
	errorResp := APIResponse{
		Success: false,
		Error:   "Something went wrong",
	}

	assert.False(t, errorResp.Success)
	assert.Equal(t, "Something went wrong", errorResp.Error)
	assert.Empty(t, errorResp.Message)
	assert.Nil(t, errorResp.Data)
}

func TestPaginationRequest(t *testing.T) {
	// Test pagination request
	pagination := PaginationRequest{
		Page:     1,
		PageSize: 10,
	}

	assert.Equal(t, 1, pagination.Page)
	assert.Equal(t, 10, pagination.PageSize)
}

func TestDashboardStats(t *testing.T) {
	stats := DashboardStats{
		TotalGenerations:      100,
		TotalLearningSessions: 50,
		CompletedGenerations:  80,
		PendingGenerations:   15,
		FailedGenerations:    5,
	}

	assert.Equal(t, int64(100), stats.TotalGenerations)
	assert.Equal(t, int64(50), stats.TotalLearningSessions)
	assert.Equal(t, int64(80), stats.CompletedGenerations)
	assert.Equal(t, int64(15), stats.PendingGenerations)
	assert.Equal(t, int64(5), stats.FailedGenerations)
}

func TestRecentActivity(t *testing.T) {
	now := time.Now()
	activity := RecentActivity{
		Type:      "generation",
		Title:     "New Track",
		Status:    "completed",
		CreatedAt: now,
	}

	assert.Equal(t, "generation", activity.Type)
	assert.Equal(t, "New Track", activity.Title)
	assert.Equal(t, "completed", activity.Status)
	assert.Equal(t, now, activity.CreatedAt)
}