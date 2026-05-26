package api

import (
	"auto-lofi-hyper-pop-music-producer/api/internal/config"
	"auto-lofi-hyper-pop-music-producer/api/pkg/logger"
	
	"github.com/gin-gonic/gin"
	"database/sql"
	"net/http"
	"io"
	"time"
	"bytes"
	"encoding/json"
)

type Server struct {
	router *gin.Engine
	db     *sql.DB
	config *config.Config
	logger *logger.Logger
}

// Request models
type GenerateMusicRequest struct {
	Title      string   `json:"title"`
	Genre      string   `json:"genre"`
	Mood       string   `json:"mood"`
	Duration   int      `json:"duration"`
	Tempo      *int     `json:"tempo,omitempty"`
	Key        string   `json:"key,omitempty"`
	Instruments []string `json:"instruments,omitempty"`
	Prompt     string   `json:"prompt,omitempty"`
}

func SetupRoutes(router *gin.Engine, db *sql.DB, cfg *config.Config, logger *logger.Logger) {
	server := &Server{
		router: router,
		db:     db,
		config: cfg,
		logger: logger,
	}

	// Global middleware
	router.Use(server.CORSMiddleware())

	// Health check (no auth)
	router.GET("/health", server.healthCheck)
	router.GET("/", server.welcome)

	// API v1 group
	v1 := router.Group("/api/v1")
	{
		v1.GET("/health", server.healthCheck)

		// Public auth routes
		public := v1.Group("/public")
		{
			public.POST("/register", server.register)
			public.POST("/login", server.login)
		}

		// Music routes — proxy to Python AI service
		music := v1.Group("/music")
		{
			music.GET("/genres", server.proxyToAI("GET", "/api/v1/genres"))
			music.POST("/generate", server.proxyToAI("POST", "/api/v1/generate"))
			music.GET("/status/:task_id", server.proxyToAICapture("GET", "/api/v1/status/"))
			music.GET("/download/:task_id", server.proxyToAICapture("GET", "/api/v1/download/"))
			music.GET("/history", server.proxyToAI("GET", "/api/v1/history"))
		}

		// Video routes — proxy to Python AI service
		video := v1.Group("/video")
		{
			video.POST("/analyze", server.proxyToAI("POST", "/api/v1/analyze"))
			video.POST("/upload", server.proxyToAI("POST", "/api/v1/upload"))
			video.GET("/status/:task_id", server.proxyToAICapture("GET", "/api/v1/status/"))
		}

		// Provider routes
		provider := v1.Group("/providers")
		{
			provider.GET("", server.proxyToAI("GET", "/api/v1/list"))
			provider.GET("/stats/summary", server.proxyToAI("GET", "/api/v1/list"))
			provider.GET("/:name", server.proxyToAICapture("GET", "/api/v1/status/"))
			provider.POST("/:name/test", server.proxyToAICapture("POST", "/api/v1/configure/"))
		}

		// Protected routes (auth required for user data)
		protected := v1.Group("")
		protected.Use(server.AuthMiddleware())
		{
			user := protected.Group("/user")
			{
				user.GET("/profile", server.getUserProfile)
				user.PUT("/profile", server.updateUserProfile)
			}
			dashboard := protected.Group("/dashboard")
			{
				dashboard.GET("/stats", server.getDashboardStats)
				dashboard.GET("/recent-activity", server.getRecentActivity)
			}
		}
	}
}

// CORSMiddleware adds CORS headers for frontend
func (s *Server) CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	}
}

// proxyToAI forwards request to Python AI service
func (s *Server) proxyToAI(method string, aiPath string) gin.HandlerFunc {
	return func(c *gin.Context) {
		targetURL := s.config.AIService.BaseURL + aiPath

		var body io.Reader
		if method == "POST" || method == "PUT" {
			bodyBytes, _ := io.ReadAll(c.Request.Body)
			body = bytes.NewReader(bodyBytes)
		}

		req, err := http.NewRequest(method, targetURL, body)
		if err != nil {
			c.JSON(502, gin.H{"error": "Failed to create proxy request"})
			return
		}
		if body != nil {
			req.Header.Set("Content-Type", "application/json")
		}

		client := &http.Client{Timeout: 30 * time.Second}
		resp, err := client.Do(req)
		if err != nil {
			c.JSON(502, gin.H{"error": "AI service unavailable", "detail": err.Error()})
			return
		}
		defer resp.Body.Close()

		respBody, _ := io.ReadAll(resp.Body)
		var result interface{}
		json.Unmarshal(respBody, &result)
		c.JSON(resp.StatusCode, result)
	}
}

// proxyToAICapture forwards with path parameter capture
func (s *Server) proxyToAICapture(method string, aiPathPrefix string) gin.HandlerFunc {
	return func(c *gin.Context) {
		param := c.Param("name")
		if param == "" {
			param = c.Param("task_id")
		}
		targetURL := s.config.AIService.BaseURL + aiPathPrefix + param

		var body io.Reader
		if method == "POST" || method == "PUT" {
			bodyBytes, _ := io.ReadAll(c.Request.Body)
			body = bytes.NewReader(bodyBytes)
		}

		req, err := http.NewRequest(method, targetURL, body)
		if err != nil {
			c.JSON(502, gin.H{"error": "Failed to create proxy request"})
			return
		}
		if body != nil {
			req.Header.Set("Content-Type", "application/json")
		}

		client := &http.Client{Timeout: 30 * time.Second}
		resp, err := client.Do(req)
		if err != nil {
			c.JSON(502, gin.H{"error": "AI service unavailable", "detail": err.Error()})
			return
		}
		defer resp.Body.Close()

		respBody, _ := io.ReadAll(resp.Body)
		var result interface{}
		json.Unmarshal(respBody, &result)
		c.JSON(resp.StatusCode, result)
	}
}

// Health check endpoint
func (s *Server) healthCheck(c *gin.Context) {
	c.JSON(200, gin.H{
		"status":  "healthy",
		"service": "auto-lofi-hyper-pop-music-producer-api",
		"version": "1.0.0",
	})
}

// Welcome endpoint
func (s *Server) welcome(c *gin.Context) {
	c.JSON(200, gin.H{
		"message":       "Welcome to Auto LoFi Hyper Pop Music Producer API",
		"version":       "1.0.0",
		"documentation": "/docs",
		"endpoints": gin.H{
			"health":    "/health",
			"music":     "/api/v1/music/genres",
			"generate":  "/api/v1/music/generate",
			"providers": "/api/v1/providers",
		},
	})
}

// Placeholder auth handlers
func (s *Server) register(c *gin.Context) {
	c.JSON(501, gin.H{"error": "Registration not implemented yet", "hint": "Use API directly for now"})
}

func (s *Server) login(c *gin.Context) {
	c.JSON(501, gin.H{"error": "Login not implemented yet", "hint": "Use API directly for now"})
}

func (s *Server) AuthMiddleware() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		c.JSON(401, gin.H{"error": "Authentication required"})
		c.Abort()
	})
}

// Placeholder user/dashboard handlers
func (s *Server) getUserProfile(c *gin.Context)      { c.JSON(501, gin.H{"error": "Not implemented"}) }
func (s *Server) updateUserProfile(c *gin.Context)   { c.JSON(501, gin.H{"error": "Not implemented"}) }
func (s *Server) getDashboardStats(c *gin.Context)   { c.JSON(501, gin.H{"error": "Not implemented"}) }
func (s *Server) getRecentActivity(c *gin.Context)   { c.JSON(501, gin.H{"error": "Not implemented"}) }
