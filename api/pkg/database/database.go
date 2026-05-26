package database

import (
	"database/sql"
	"fmt"
	"time"
	
	_ "github.com/lib/pq"
)

type Database struct {
	*sql.DB
}

func NewDatabase(dataSourceName string) (*Database, error) {
	db, err := sql.Open("postgres", dataSourceName)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// Configure connection pool
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(5 * time.Minute)

	// Verify connection
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &Database{DB: db}, nil
}

// CreateUsersTable creates the users table if it doesn't exist
func (db *Database) CreateUsersTable() error {
	query := `
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

	if _, err := db.Exec(query); err != nil {
		return fmt.Errorf("failed to create users table: %w", err)
	}

	return nil
}

// CreateMusicGenerationsTable creates the music generations table
func (db *Database) CreateMusicGenerationsTable() error {
	query := `
		CREATE TABLE IF NOT EXISTS music_generations (
			id SERIAL PRIMARY KEY,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			title VARCHAR(255) NOT NULL,
			genre VARCHAR(100) NOT NULL,
			mood VARCHAR(100),
			duration INTEGER DEFAULT 180, -- 3 minutes default
			prompt TEXT,
			status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
			output_file_url TEXT,
			created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
			completed_at TIMESTAMP WITH TIME ZONE,
			error_message TEXT
		);
		
		CREATE INDEX IF NOT EXISTS idx_music_generations_user_id ON music_generations(user_id);
		CREATE INDEX IF NOT EXISTS idx_music_generations_status ON music_generations(status);
	`

	if _, err := db.Exec(query); err != nil {
		return fmt.Errorf("failed to create music_generations table: %w", err)
	}

	return nil
}

// CreateLearningSessionsTable creates the learning sessions table
func (db *Database) CreateLearningSessionsTable() error {
	query := `
		CREATE TABLE IF NOT EXISTS learning_sessions (
			id SERIAL PRIMARY KEY,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			video_url TEXT NOT NULL,
			video_title VARCHAR(500),
			extracted_patterns JSONB,
			learned_model_id INTEGER,
			status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
			created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
			completed_at TIMESTAMP WITH TIME ZONE,
			error_message TEXT
		);
		
		CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_id ON learning_sessions(user_id);
		CREATE INDEX IF NOT EXISTS idx_learning_sessions_status ON learning_sessions(status);
	`

	if _, err := db.Exec(query); err != nil {
		return fmt.Errorf("failed to create learning_sessions table: %w", err)
	}

	return nil
}

// InitializeDatabase creates all tables needed for the application
func (db *Database) InitializeDatabase() error {
	tables := []func() error{
		db.CreateUsersTable,
		db.CreateMusicGenerationsTable,
		db.CreateLearningSessionsTable,
	}

	for _, createTable := range tables {
		if err := createTable(); err != nil {
			return err
		}
	}

	return nil
}