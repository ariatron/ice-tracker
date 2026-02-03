package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/ice-tracker/api/database"
	"github.com/ice-tracker/api/models"
)

func GetDetentions(c *gin.Context) {
	state := c.Query("state")
	facilityID := c.Query("facility_id")
	startDate := c.Query("start_date")
	endDate := c.Query("end_date")
	limit := c.DefaultQuery("limit", "100")

	query := `
		SELECT
			id, timestamp, facility_name, facility_id, state, city,
			detained_count, capacity, avg_daily_population,
			facility_type, data_source, created_at
		FROM detentions
		WHERE 1=1
	`
	args := []interface{}{}
	argCount := 1

	if state != "" {
		query += ` AND state = $` + string(rune(argCount+'0'))
		args = append(args, state)
		argCount++
	}

	if facilityID != "" {
		query += ` AND facility_id = $` + string(rune(argCount+'0'))
		args = append(args, facilityID)
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

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	rows, err := database.Pool.Query(ctx, query, args...)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":  "Failed to query detentions",
			"detail": err.Error(),
		})
		return
	}
	defer rows.Close()

	detentions := []models.Detention{}
	for rows.Next() {
		var detention models.Detention
		err := rows.Scan(
			&detention.ID,
			&detention.Timestamp,
			&detention.FacilityName,
			&detention.FacilityID,
			&detention.State,
			&detention.City,
			&detention.DetainedCount,
			&detention.Capacity,
			&detention.AvgDailyPopulation,
			&detention.FacilityType,
			&detention.DataSource,
			&detention.CreatedAt,
		)
		if err != nil {
			continue
		}
		detentions = append(detentions, detention)
	}

	c.JSON(http.StatusOK, gin.H{
		"count": len(detentions),
		"data":  detentions,
	})
}
