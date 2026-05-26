package models

import (
	"time"
	"database/sql/driver"
	"encoding/json"
	"errors"
)

type User struct {
	ID           int       `json:"id" db:"id"`
	Email        string    `json:"email" db:"email"`
	Username     string    `json:"username" db:"username"`
	FullName     string    `json:"full_name" db:"full_name"`
	PlanType     string    `json:"plan_type" db:"plan_type"`
	CreatedAt    time.Time `json:"created_at" db:"created_at"`
	UpdatedAt    time.Time `json:"updated_at" db:"updated_at"`
}

type MusicGeneration struct {
	ID             int       `json:"id" db:"id"`
	UserID         int       `json:"user_id" db:"user_id"`
	Title          string    `json:"title" db:"title"`
	Genre          string    `json:"genre" db:"genre"`
	Mood           string    `json:"mood" db:"mood"`
	Duration      int       `json:"duration" db:"duration"`
	Prompt         string    `json:"prompt" db:"prompt"`
	Status         string    `json:"status" db:"status"`
	OutputFileURL  string    `json:"output_file_url" db:"output_file_url"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
	CompletedAt    *time.Time `json:"completed_at" db:"completed_at"`
	ErrorMessage   string    `json:"error_message" db:"error_message"`
}

type LearningSession struct {
	ID                int            `json:"id" db:"id"`
	UserID            int            `json:"user_id" db:"user_id"`
	VideoURL          string         `json:"video_url" db:"video_url"`
	VideoTitle        string         `json:"video_title" db:"video_title"`
	ExtractedPatterns JSONB          `json:"extracted_patterns" db:"extracted_patterns"`
	LearnedModelID    *int           `json:"learned_model_id" db:"learned_model_id"`
	Status            string         `json:"status" db:"status"`
	CreatedAt         time.Time      `json:"created_at" db:"created_at"`
	CompletedAt       *time.Time     `json:"completed_at" db:"completed_at"`
	ErrorMessage      string         `json:"error_message" db:"error_message"`
}

// JSONB type for PostgreSQL JSONB support
type JSONB map[string]interface{}

// Value implements the driver.Valuer interface for JSONB
func (j JSONB) Value() (driver.Value, error) {
	if j == nil {
		return nil, nil
	}
	return json.Marshal(j)
}

// Scan implements the sql.Scanner interface for JSONB
func (j *JSONB) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("type assertion to []byte failed")
	}

	return json.Unmarshal(bytes, &j)
}

// User registration request
type RegisterRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Username string `json:"username" binding:"required,min=3,max=100"`
	Password string `json:"password" binding:"required,min=8"`
	FullName string `json:"full_name,omitempty"`
}

// User login request
type LoginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
}

// Login response with JWT token
type LoginResponse struct {
	Token string `json:"token"`
	User  *User  `json:"user"`
}

// Music generation request
type GenerateMusicRequest struct {
	Title     string `json:"title" binding:"required,min=1,max=255"`
	Genre     string `json:"genre" binding:"required,min=1,max=100"`
	Mood      string `json:"mood,omitempty"`
	Duration  int    `json:"duration,omitempty" binding:"min=10,max=600"`
	Prompt    string `json:"prompt,omitempty"`
	Model     string `json:"model,omitempty"` // "heartmula" or "suno"
}

// Video analysis request
type AnalyzeVideoRequest struct {
	VideoURL  string `json:"video_url" binding:"required,url"`
	Title     string `json:"title,omitempty"`
	FocusType string `json:"focus_type,omitempty"` // "rhythm", "melody", "harmony", "all"
}

// API response wrapper
type APIResponse struct {
	Success bool        `json:"success"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// Pagination request parameters
type PaginationRequest struct {
	Page     int `form:"page" binding:"min=1"`
	PageSize int `form:"page_size" binding:"min=1,max=100"`
}

// Paginated response
type PaginatedResponse struct {
	Data       interface{} `json:"data"`
	Total      int64       `json:"total"`
	Page       int         `json:"page"`
	PageSize   int         `json:"page_size"`
	TotalPages int        `json:"total_pages"`
}

// Dashboard statistics
type DashboardStats struct {
	TotalGenerations    int64 `json:"total_generations"`
	TotalLearningSessions int64 `json:"total_learning_sessions"`
	CompletedGenerations int64 `json:"completed_generations"`
	PendingGenerations  int64 `json:"pending_generations"`
	FailedGenerations   int64 `json:"failed_generations"`
}

// Recent activity
type RecentActivity struct {
	Type      string    `json:"type"`
	Title     string    `json:"title"`
	Status    string    `json:"status"`
	CreatedAt time.Time `json:"created_at"`
}