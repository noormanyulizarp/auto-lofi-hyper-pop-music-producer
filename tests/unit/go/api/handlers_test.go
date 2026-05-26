package api

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
	
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	
	"auto-music-producer/api/internal/models"
)

func TestServerHealthCheck(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	// Create test server
	server := &Server{
		router: gin.Default(),
	}
	
	// Create recorder and request
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/health", nil)
	
	// Serve the request
	server.router.ServeHTTP(w, req)
	
	// Assertions
	assert.Equal(t, http.StatusOK, w.Code)
	
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	require.NoError(t, err)
	
	assert.Equal(t, "healthy", response["status"])
	assert.Equal(t, "auto-music-producer-api", response["service"])
	assert.Equal(t, "1.0.0", response["version"])
}

func TestServerWelcome(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/", nil)
	
	server.router.ServeHTTP(w, req)
	
	// Assertions
	assert.Equal(t, http.StatusOK, w.Code)
	
	var response map[string]string
	err := json.Unmarshal(w.Body.Bytes(), &response)
	require.NoError(t, err)
	
	assert.Contains(t, response["message"], "Auto Music Producer")
	assert.Equal(t, "1.0.0", response["version"])
	assert.Contains(t, response["documentation"], "/swagger")
}

func TestServerRegisterHandler(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	// Test valid registration request
	validUser := models.RegisterRequest{
		Email:    "test@example.com",
		Username: "testuser",
		Password: "password123",
		FullName: "Test User",
	}
	
	jsonData, err := json.Marshal(validUser)
	require.NoError(t, err)
	
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/v1/public/register", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	
	server.router.ServeHTTP(w, req)
	
	// Since handler returns 501 (Not implemented yet), verify that
	assert.Equal(t, http.StatusNotImplemented, w.Code)
	
	var response map[string]string
	err = json.Unmarshal(w.Body.Bytes(), &response)
	require.NoError(t, err)
	
	assert.Contains(t, response["error"], "Not implemented yet")
}

func TestServerLoginHandler(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	// Test valid login request
	loginReq := models.LoginRequest{
		Email:    "test@example.com",
		Password: "password123",
	}
	
	jsonData, err := json.Marshal(loginReq)
	require.NoError(t, err)
	
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/v1/public/login", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	
	server.router.ServeHTTP(w, req)
	
	// Handler returns 501 (Not implemented yet)
	assert.Equal(t, http.StatusNotImplemented, w.Code)
	
	var response map[string]string
	err = json.Unmarshal(w.Body.Bytes(), &response)
	require.NoError(t, err)
	
	assert.Contains(t, response["error"], "Not implemented yet")
}

func TestServerAuthMiddleware(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	// Test protected route without authentication
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/v1/user/profile", nil)
	
	server.router.ServeHTTP(w, req)
	
	// Should return 401 (Authentication required)
	assert.Equal(t, http.StatusUnauthorized, w.Code)
	
	var response map[string]string
	err := json.Unmarshal(w.Body.Bytes(), &response)
	require.NoError(t, err)
	
	assert.Contains(t, response["error"], "Authentication required")
}

func TestServerGenerateMusicHandler(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	// Test music generation request
	musicReq := models.GenerateMusicRequest{
		Title:    "Test LoFi Track",
		Genre:    "lofi",
		Mood:     "chill",
		Duration: 180,
		Prompt:   "Generate a relaxing lofi track",
		Model:    "heartmula",
	}
	
	jsonData, err := json.Marshal(musicReq)
	require.NoError(t, err)
	
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/v1/music/generate", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	
	server.router.ServeHTTP(w, req)
	
	// Returns 401 (Authentication required)
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestServerAnalyzeVideoHandler(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	// Test video analysis request
	videoReq := models.AnalyzeVideoRequest{
		VideoURL:  "https://example.com/video.mp4",
		Title:     "LoFi Tutorial",
		FocusType: "rhythm",
	}
	
	jsonData, err := json.Marshal(videoReq)
	require.NoError(t, err)
	
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/v1/learning/video/analyze", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	
	server.router.ServeHTTP(w, req)
	
	// Returns 401 (Authentication required)
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestServerDashboardStatsHandler(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/v1/dashboard/stats", nil)
	
	server.router.ServeHTTP(w, req)
	
	// Returns 401 (Authentication required)
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestServerErrorHandler(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	// Test with invalid JSON (malformed request)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/v1/public/register", bytes.NewBuffer([]byte("invalid json")))
	req.Header.Set("Content-Type", "application/json")
	
	server.router.ServeHTTP(w, req)
	
	// Should return 400 (Bad Request)
	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestServerInvalidRoute(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/v1/invalid/route", nil)
	
	server.router.ServeHTTP(w, req)
	
	// Should return 404 (Not Found)
	assert.Equal(t, http.StatusNotFound, w.Code)
}

func TestServerMethodNotAllowed(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	// Test POST to a GET-only endpoint
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/health", bytes.NewBuffer([]byte("{}")))
	req.Header.Set("Content-Type", "application/json")
	
	server.router.ServeHTTP(w, req)
	
	// Should return 405 (Method Not Allowed)
	assert.Equal(t, http.StatusMethodNotAllowed, w.Code)
}

// Benchmark test for health check endpoint
func BenchmarkServerHealthCheck(b *testing.B) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	server := &Server{
		router: gin.Default(),
	}
	
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/health", nil)
			server.router.ServeHTTP(w, req)
		}
	})
}

// Test helper function to create API response
func createTestAPIResponse(success bool, message string, data interface{}) map[string]interface{} {
	return map[string]interface{}{
		"success": success,
		"message": message,
		"data":    data,
	}
}

// Test helper function to validate API response format
func validateAPIResponse(t *testing.T, w *httptest.ResponseRecorder, expectedStatusCode int) map[string]interface{} {
	assert.Equal(t, expectedStatusCode, w.Code)
	
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	require.NoError(t, err, "Response should be valid JSON")
	
	// Check that response has required fields
	if _, hasSuccess := response["success"]; hasSuccess {
		assert.IsType(t, true, response["success"])
	}
	
	return response
}