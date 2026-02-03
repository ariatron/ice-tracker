package config

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	TimescaleHost     string
	TimescalePort     string
	TimescaleUser     string
	TimescalePassword string
	TimescaleDatabase string
	APIPort           string
	APIHost           string
}

var AppConfig *Config

func LoadConfig() (*Config, error) {
	// Load .env file if it exists
	godotenv.Load()

	config := &Config{
		TimescaleHost:     getEnv("TIMESCALE_HOST", "localhost"),
		TimescalePort:     getEnv("TIMESCALE_PORT", "5432"),
		TimescaleUser:     getEnv("TIMESCALE_USER", "ice_tracker"),
		TimescalePassword: getEnv("TIMESCALE_PASSWORD", ""),
		TimescaleDatabase: getEnv("TIMESCALE_DATABASE", "ice_activities"),
		APIPort:           getEnv("API_PORT", "8080"),
		APIHost:           getEnv("API_HOST", "0.0.0.0"),
	}

	AppConfig = config
	return config, nil
}

func (c *Config) GetDatabaseURL() string {
	return fmt.Sprintf(
		"postgres://%s:%s@%s:%s/%s?sslmode=disable",
		c.TimescaleUser,
		c.TimescalePassword,
		c.TimescaleHost,
		c.TimescalePort,
		c.TimescaleDatabase,
	)
}

func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}
