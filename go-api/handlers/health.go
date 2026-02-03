package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/ice-tracker/api/database"
	"github.com/ice-tracker/api/models"
)

func HealthCheck(c *gin.Context) {
	health := models.HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now(),
		Database: models.DatabaseHealth{
			Connected: false,
		},
	}

	// Check database connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	err := database.Pool.Ping(ctx)
	if err != nil {
		health.Status = "unhealthy"
		health.Database.Message = err.Error()
		c.JSON(http.StatusServiceUnavailable, health)
		return
	}

	health.Database.Connected = true
	health.Database.Message = "connected"

	// Optionally, fetch recent data source health
	rows, err := database.Pool.Query(ctx, `
		SELECT DISTINCT ON (source_name)
			source_name,
			last_successful_fetch,
			last_attempt,
			status,
			error_message,
			records_fetched
		FROM data_source_health
		ORDER BY source_name, created_at DESC
		LIMIT 10
	`)
	if err == nil {
		defer rows.Close()

		var sources []models.DataSourceHealth
		for rows.Next() {
			var source models.DataSourceHealth
			err := rows.Scan(
				&source.SourceName,
				&source.LastSuccessfulFetch,
				&source.LastAttempt,
				&source.Status,
				&source.ErrorMessage,
				&source.RecordsFetched,
			)
			if err == nil {
				sources = append(sources, source)
			}
		}
		health.Sources = sources
	}

	c.JSON(http.StatusOK, health)
}
