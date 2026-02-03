package database

import (
	"context"
	"fmt"
	"log"

	"github.com/ice-tracker/api/config"
	"github.com/jackc/pgx/v5/pgxpool"
)

var Pool *pgxpool.Pool

func InitDB() error {
	cfg := config.AppConfig
	dbURL := cfg.GetDatabaseURL()

	poolConfig, err := pgxpool.ParseConfig(dbURL)
	if err != nil {
		return fmt.Errorf("unable to parse database URL: %w", err)
	}

	// Configure connection pool
	poolConfig.MaxConns = 25
	poolConfig.MinConns = 5

	pool, err := pgxpool.NewWithConfig(context.Background(), poolConfig)
	if err != nil {
		return fmt.Errorf("unable to create connection pool: %w", err)
	}

	// Test the connection
	err = pool.Ping(context.Background())
	if err != nil {
		return fmt.Errorf("unable to ping database: %w", err)
	}

	Pool = pool
	log.Printf("Database connection pool established: %s:%s", cfg.TimescaleHost, cfg.TimescalePort)
	return nil
}

func CloseDB() {
	if Pool != nil {
		Pool.Close()
		log.Println("Database connection pool closed")
	}
}
