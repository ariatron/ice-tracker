package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/ice-tracker/api/database"
	"github.com/ice-tracker/api/models"
)

func GetArrests(c *gin.Context) {
	// Query parameters
	state := c.Query("state")
	startDate := c.Query("start_date")
	endDate := c.Query("end_date")
	limit := c.DefaultQuery("limit", "100")

	// Build query
	query := `
		SELECT
			id, timestamp, state, county, city,
			arrest_count, criminal_arrests, non_criminal_arrests,
			data_source, source_url, created_at
		FROM arrests
		WHERE 1=1
	`
	args := []interface{}{}
	argCount := 1

	if state != "" {
		query += ` AND state = $` + string(rune(argCount+'0'))
		args = append(args, state)
		argCount++
	}

	if startDate != "" {
		query += ` AND timestamp >= $` + string(rune(argCount+'0'))
		args = append(args, startDate)
		argCount++
	}

	if endDate != "" {
		query += ` AND timestamp <= $` + string(rune(argCount+'0'))
		args = append(args, endDate)
		argCount++
	}

	query += ` ORDER BY timestamp DESC LIMIT $` + string(rune(argCount+'0'))
	args = append(args, limit)

	// Execute query
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	rows, err := database.Pool.Query(ctx, query, args...)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to query arrests",
			"detail": err.Error(),
		})
		return
	}
	defer rows.Close()

	// Parse results
	arrests := []models.Arrest{}
	for rows.Next() {
		var arrest models.Arrest
		err := rows.Scan(
			&arrest.ID,
			&arrest.Timestamp,
			&arrest.State,
			&arrest.County,
			&arrest.City,
			&arrest.ArrestCount,
			&arrest.CriminalArrests,
			&arrest.NonCriminalArrests,
			&arrest.DataSource,
			&arrest.SourceURL,
			&arrest.CreatedAt,
		)
		if err != nil {
			continue
		}
		arrests = append(arrests, arrest)
	}

	c.JSON(http.StatusOK, gin.H{
		"count": len(arrests),
		"data":  arrests,
	})
}
