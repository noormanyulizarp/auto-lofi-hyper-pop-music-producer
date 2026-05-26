package middleware

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"testing"
	
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	
	"auto-music-producer/api/pkg/logger"
)

func TestCORSMiddleware(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	// Create a mock logger
	mockLogger := &logger.Logger{}
	
	// Create router with CORS middleware
	router := gin.New()
	router.Use(CORS())
	
	// Add a test endpoint
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "test"})
	})
	
	// Test preflight request (OPTIONS)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("OPTIONS", "/test", nil)
	req.Header.Set("Origin", "http://localhost:3000")
	req.Header.Set("Access-Control-Request-Method", "GET")
	
	router.ServeHTTP(w, req)
	
	// Should return 204 No Content for preflight
	assert.Equal(t, http.StatusNoContent, w.Code)
	
	// Check CORS headers
	assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
	assert.Equal(t, "true", w.Header().Get("Access-Control-Allow-Credentials"))
	assert.Contains(t, w.Header().Get("Access-Control-Allow-Headers"), "Content-Type")
	assert.Contains(t, w.Header().Get("Access-Control-Allow-Methods"), "GET")
	
	// Test actual GET request
	w = httptest.NewRecorder()
	req, _ = http.NewRequest("GET", "/test", nil)
	req.Header.Set("Origin", "http://localhost:3000")
	
	router.ServeHTTP(w, req)
	
	// Should return 200 OK
	assert.Equal(t, http.StatusOK, w.Code)
	
	// Check CORS headers are present
	assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
}

func TestLoggerMiddleware(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	// Create a mock logger
	mockLogger := &logger.Logger{}
	
	// Create router with Logger middleware
	router := gin.New()
	router.Use(Logger(mockLogger))
	
	// Add a test endpoint
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "test"})
	})
	
	// Test request
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)
	
	router.ServeHTTP(w, req)
	
	// Should return 200 OK
	assert.Equal(t, http.StatusOK, w.Code)
	
	// Logger middleware should pass the request through
	// In a real test, we would verify that the logger was called
	// but for now, we just verify the request completes successfully
}

func TestRecoveryMiddleware(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	// Create a mock logger
	mockLogger := &logger.Logger{}
	
	// Create router with Recovery middleware
	router := gin.New()
	router.Use(Recovery(mockLogger))
	
	// Add an endpoint that panics
	router.GET("/panic", func(c *gin.Context) {
		panic("test panic")
	})
	
	// Add a normal endpoint
	router.GET("/normal", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "normal"})
	})
	
	// Test normal request (should work fine)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/normal", nil)
	
	router.ServeHTTP(w, req)
	
	// Should return 200 OK
	assert.Equal(t, http.StatusOK, w.Code)
	
	// Test panic request (should be recovered)
	w = httptest.NewRecorder()
	req, _ = http.NewRequest("GET", "/panic", nil)
	
	router.ServeHTTP(w, req)
	
	// Should return 500 Internal Server Error
	assert.Equal(t, http.StatusInternalServerError, w.Code)
	
	var response map[string]string
	err := json.Unmarshal(w.Body.Bytes(), &response)
	require.NoError(t, err)
	
	assert.Equal(t, "Internal Server Error", response["error"])
}

func TestMiddlewareChain(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	// Create a mock logger
	mockLogger := &logger.Logger{}
	
	// Create router with all middleware
	router := gin.New()
	router.Use(CORS())
	router.Use(Logger(mockLogger))
	router.Use(Recovery(mockLogger))
	
	// Add a test endpoint
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "middleware chain test"})
	})
	
	// Test request with all middleware
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)
	req.Header.Set("Origin", "http://localhost:3000")
	
	router.ServeHTTP(w, req)
	
	// Should return 200 OK
	assert.Equal(t, http.StatusOK, w.Code)
	
	// Check CORS headers are present
	assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
	
	var response map[string]string
	err := json.Unmarshal(w.Body.Bytes(), &response)
	require.NoError(t, err)
	
	assert.Equal(t, "middleware chain test", response["message"])
}

func TestCORSMiddlewareWithMultipleOrigins(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	router := gin.New()
	router.Use(CORS())
	
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "test"})
	})
	
	// Test with different origins
	origins := []string{
		"http://localhost:3000",
		"http://localhost:3001",
		"http://127.0.0.1:3000",
		"https://example.com",
	}
	
	for _, origin := range origins {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("OPTIONS", "/test", nil)
		req.Header.Set("Origin", origin)
		req.Header.Set("Access-Control-Request-Method", "GET")
		
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusNoContent, w.Code)
		assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
	}
}

func TestCORSMiddlewareWithHeaders(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	router := gin.New()
	router.Use(CORS())
	
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "test"})
	})
	
	// Test preflight request with various headers
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("OPTIONS", "/test", nil)
	req.Header.Set("Origin", "http://localhost:3000")
	req.Header.Set("Access-Control-Request-Method", "POST")
	req.Header.Set("Access-Control-Request-Headers", "Content-Type, Authorization")
	
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusNoContent, w.Code)
	
	// Check that the requested headers are allowed
	allowedHeaders := w.Header().Get("Access-Control-Allow-Headers")
	assert.Contains(t, allowedHeaders, "Content-Type")
	assert.Contains(t, allowedHeaders, "Authorization")
}

func TestCORSMiddlewareWithMethods(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	router := gin.New()
	router.Use(CORS())
	
	// Add different types of routes
	router.GET("/get", func(c *gin.Context) {
		c.JSON(200, gin.H{"method": "GET"})
	})
	router.POST("/post", func(c *gin.Context) {
		c.JSON(200, gin.H{"method": "POST"})
	})
	router.PUT("/put", func(c *gin.Context) {
		c.JSON(200, gin.H{"method": "PUT"})
	})
	router.DELETE("/delete", func(c *gin.Context) {
		c.JSON(200, gin.H{"method": "DELETE"})
	})
	
	methods := []string{"GET", "POST", "PUT", "DELETE"}
	for _, method := range methods {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("OPTIONS", "/"+method, nil)
		req.Header.Set("Origin", "http://localhost:3000")
		req.Header.Set("Access-Control-Request-Method", method)
		
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusNoContent, w.Code)
		
		allowedMethods := w.Header().Get("Access-Control-Allow-Methods")
		assert.Contains(t, allowedMethods, method)
	}
}

// Benchmark test for middleware performance
func BenchmarkCORSMiddleware(b *testing.B) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	router := gin.New()
	router.Use(CORS())
	
	router.GET("/benchmark", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "benchmark"})
	})
	
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/benchmark", nil)
			req.Header.Set("Origin", "http://localhost:3000")
			
			router.ServeHTTP(w, req)
		}
	})
}