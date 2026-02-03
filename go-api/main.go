package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/gin-gonic/gin"
	"github.com/ice-tracker/api/config"
	"github.com/ice-tracker/api/database"
	"github.com/ice-tracker/api/handlers"
)

func main() {
	// Load configuration
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	log.Printf("Starting ICE Tracker API Server")
	log.Printf("Database: %s:%s", cfg.TimescaleHost, cfg.TimescalePort)

	// Initialize database
	err = database.InitDB()
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer database.CloseDB()

	// Set up Gin router
	router := gin.Default()

	// Add CORS middleware
	router.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// API routes
	api := router.Group("/api/v1")
	{
		// Health check
		api.GET("/health", handlers.HealthCheck)

		// Data endpoints
		api.GET("/arrests", handlers.GetArrests)
		api.GET("/detentions", handlers.GetDetentions)
		// api.GET("/removals", handlers.GetRemovals)              // TODO: Phase 2
		// api.GET("/community-reports", handlers.GetCommunityReports)  // TODO: Phase 3
		// api.GET("/news", handlers.GetNewsArticles)              // TODO: Phase 3

		// Aggregate endpoints
		api.GET("/aggregates/national", handlers.GetNationalAggregate)
		api.GET("/aggregates/state/:state", handlers.GetStateAggregate)
	}

	// Root endpoint
	router.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"name":    "ICE Tracker API",
			"version": "1.0.0",
			"status":  "running",
			"endpoints": []string{
				"/api/v1/health",
				"/api/v1/arrests",
				"/api/v1/detentions",
				"/api/v1/aggregates/national",
				"/api/v1/aggregates/state/:state",
			},
		})
	})

	// Graceful shutdown
	go func() {
		sigChan := make(chan os.Signal, 1)
		signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
		<-sigChan
		log.Println("Shutting down server...")
		database.CloseDB()
		os.Exit(0)
	}()

	// Start server
	addr := fmt.Sprintf("%s:%s", cfg.APIHost, cfg.APIPort)
	log.Printf("Server listening on %s", addr)
	if err := router.Run(addr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
