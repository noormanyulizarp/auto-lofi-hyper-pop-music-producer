package database

import (
	"database/sql"
	"fmt"

	_ "modernc.org/sqlite"
)

type Database struct {
	*sql.DB
}

func NewDatabase(dataSourceName string) (*Database, error) {
	if dataSourceName == "" {
		dataSourceName = "file:api.db?cache=shared&_journal_mode=WAL"
	}

	db, err := sql.Open("sqlite", dataSourceName)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// SQLite-friendly pool settings
	db.SetMaxOpenConns(1)
	db.SetMaxIdleConns(1)
	db.SetConnMaxLifetime(0)

	// Enable WAL mode and foreign keys
	if _, err := db.Exec("PRAGMA journal_mode=WAL"); err != nil {
		return nil, fmt.Errorf("failed to set WAL mode: %w", err)
	}
	if _, err := db.Exec("PRAGMA foreign_keys=ON"); err != nil {
		return nil, fmt.Errorf("failed to enable foreign keys: %w", err)
	}

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &Database{DB: db}, nil
}

// CreateUsersTable creates the users table
func (db *Database) CreateUsersTable() error {
	query := `
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			email TEXT UNIQUE NOT NULL,
			username TEXT UNIQUE NOT NULL,
			password_hash TEXT NOT NULL,
			full_name TEXT,
			plan_type TEXT DEFAULT 'free',
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		);
		CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
		CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
	`
	if _, err := db.Exec(query); err != nil {
		return fmt.Errorf("failed to create users table: %w", err)
	}
	return nil
}

// CreateMusicGenerationsTable creates the music_generations table
func (db *Database) CreateMusicGenerationsTable() error {
	query := `
		CREATE TABLE IF NOT EXISTS music_generations (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			title TEXT NOT NULL,
			genre TEXT NOT NULL,
			mood TEXT,
			duration INTEGER DEFAULT 30,
			prompt TEXT,
			tags TEXT,
			lyrics TEXT,
			status TEXT DEFAULT 'pending',
			output_file_url TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			completed_at DATETIME,
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

// CreateLearningSessionsTable creates the learning_sessions table
func (db *Database) CreateLearningSessionsTable() error {
	query := `
		CREATE TABLE IF NOT EXISTS learning_sessions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			video_url TEXT NOT NULL,
			video_title TEXT,
			extracted_patterns TEXT,
			status TEXT DEFAULT 'pending',
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			completed_at DATETIME,
			error_message TEXT
		);
		CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_id ON learning_sessions(user_id);
	`
	if _, err := db.Exec(query); err != nil {
		return fmt.Errorf("failed to create learning_sessions table: %w", err)
	}
	return nil
}

// InitializeDatabase creates all tables
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
