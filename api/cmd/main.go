package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
	
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"auto-lofi-hyper-pop-music-producer/api/internal/config"
	"auto-lofi-hyper-pop-music-producer/api/internal/api"
	"auto-lofi-hyper-pop-music-producer/api/internal/middleware"
	"auto-lofi-hyper-pop-music-producer/api/pkg/logger"
	"auto-lofi-hyper-pop-music-producer/api/pkg/database"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found, using system environment")
	}

	// Initialize logger
	appLogger := logger.NewLogger()
	appLogger.Info("Starting Auto Music Producer API Server")

	// Load configuration
	cfg, err := config.LoadConfig()
	if err != nil {
		appLogger.Fatal("Failed to load configuration", map[string]interface{}{
			"error": err.Error(),
		})
	}

	// Set Gin mode
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	} else {
		gin.SetMode(gin.DebugMode)
	}

	// Initialize database
	db, err := database.NewDatabase(cfg.DatabaseURL)
	if err != nil {
		appLogger.Fatal("Failed to connect to database", map[string]interface{}{
			"error": err.Error(),
		})
	}
	defer db.Close()

	// Create router
	router := gin.Default()

	// Apply middleware
	router.Use(middleware.CORS())
	router.Use(middleware.Logger(appLogger))
	router.Use(middleware.Recovery(appLogger))

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
			"service": "auto-lofi-hyper-pop-music-producer-api",
			"version": "1.0.0",
		})
	})

	// Setup API routes
	api.SetupRoutes(router, db, cfg, appLogger)

	// Create HTTP server
	srv := &http.Server{
		Addr:           fmt.Sprintf(":%d", cfg.Port),
		Handler:        router,
		ReadTimeout:    15 * time.Second,
		WriteTimeout:   15 * time.Second,
		IdleTimeout:    60 * time.Second,
		MaxHeaderBytes: 1 << 20, // 1MB
	}

	// Start server in a goroutine
	go func() {
		appLogger.Info("Server starting", map[string]interface{}{
			"port": cfg.Port,
			"environment": cfg.Environment,
		})
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			appLogger.Fatal("Server failed to start", map[string]interface{}{
				"error": err.Error(),
			})
		}
	}()

	// Graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	appLogger.Info("Server shutting down...")
	
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		appLogger.Error("Server forced to shutdown", map[string]interface{}{
			"error": err.Error(),
		})
	}

	appLogger.Info("Server exited successfully")
}