package config

import (
	"os"
	"strconv"
)

type Config struct {
	Environment string
	Port        int
	DatabaseURL string
	RedisURL    string
	JWTSecret   string
	AIService   AIServiceConfig
}

type AIServiceConfig struct {
	BaseURL    string
	APIKey     string
	Timeout    int
	Model      string
}

func LoadConfig() (*Config, error) {
	cfg := &Config{
		Environment: getEnv("ENVIRONMENT", "development"),
		Port:        getEnvAsInt("PORT", 8080),
		DatabaseURL: getEnv("DATABASE_URL", "postgres://user:password@localhost:5432/musicdb?sslmode=disable"),
		RedisURL:    getEnv("REDIS_URL", "redis://localhost:6379"),
		JWTSecret:   getEnv("JWT_SECRET", "your-secret-key-here"),
		AIService: AIServiceConfig{
			BaseURL: getEnv("AI_SERVICE_URL", "http://localhost:8001"),
			APIKey:  getEnv("AI_SERVICE_API_KEY", ""),
			Timeout: getEnvAsInt("AI_SERVICE_TIMEOUT", 30),
			Model:   getEnv("AI_SERVICE_MODEL", "heartmula"),
		},
	}

	// Validate required configurations
	if cfg.JWTSecret == "your-secret-key-here" && cfg.Environment == "production" {
		panic("JWT_SECRET must be set in production environment")
	}

	return cfg, nil
}

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	if value, exists := os.LookupEnv(key); exists {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}