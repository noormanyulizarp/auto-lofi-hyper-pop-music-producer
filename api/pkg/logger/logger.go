package logger

import (
	"os"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

type Logger struct {
	zerolog.Logger
}

func NewLogger() *Logger {
	// Set up zerolog
	log.Logger = zerolog.New(os.Stdout).With().Timestamp().Logger()
	
	// Set log level
	zerolog.SetGlobalLevel(zerolog.InfoLevel)
	
	return &Logger{
		Logger: log.Logger,
	}
}

func (l *Logger) Info(msg string, fields map[string]interface{}) {
	event := l.Info()
	
	for key, value := range fields {
		event = event.Interface(key, value)
	}
	
	event.Msg(msg)
}

func (l *Logger) Error(msg string, fields map[string]interface{}) {
	event := l.Error()
	
	for key, value := range fields {
		event = event.Interface(key, value)
	}
	
	event.Msg(msg)
}

func (l *Logger) Fatal(msg string, fields map[string]interface{}) {
	event := l.Fatal()
	
	for key, value := range fields {
		event = event.Interface(key, value)
	}
	
	event.Msg(msg)
	os.Exit(1)
}

func (l *Logger) Debug(msg string, fields map[string]interface{}) {
	event := l.Debug()
	
	for key, value := range fields {
		event = event.Interface(key, value)
	}
	
	event.Msg(msg)
}