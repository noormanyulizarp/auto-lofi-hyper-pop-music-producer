package logger

import (
	"os"

	"github.com/rs/zerolog"
)

type Logger struct {
	zerolog.Logger
}

func NewLogger() *Logger {
	log := zerolog.New(os.Stdout).With().Timestamp().Logger()
	zerolog.SetGlobalLevel(zerolog.InfoLevel)
	return &Logger{Logger: log}
}

func (l *Logger) Info(msg string, fields ...map[string]interface{}) {
	event := l.Logger.Info()
	if len(fields) > 0 {
		for k, v := range fields[0] {
			event = event.Interface(k, v)
		}
	}
	event.Msg(msg)
}

func (l *Logger) Error(msg string, fields ...map[string]interface{}) {
	event := l.Logger.Error()
	if len(fields) > 0 {
		for k, v := range fields[0] {
			event = event.Interface(k, v)
		}
	}
	event.Msg(msg)
}

func (l *Logger) Fatal(msg string, fields ...map[string]interface{}) {
	event := l.Logger.Fatal()
	if len(fields) > 0 {
		for k, v := range fields[0] {
			event = event.Interface(k, v)
		}
	}
	event.Msg(msg)
	os.Exit(1)
}

func (l *Logger) Debug(msg string, fields ...map[string]interface{}) {
	event := l.Logger.Debug()
	if len(fields) > 0 {
		for k, v := range fields[0] {
			event = event.Interface(k, v)
		}
	}
	event.Msg(msg)
}

func (l *Logger) Warn(msg string, fields ...map[string]interface{}) {
	event := l.Logger.Warn()
	if len(fields) > 0 {
		for k, v := range fields[0] {
			event = event.Interface(k, v)
		}
	}
	event.Msg(msg)
}
