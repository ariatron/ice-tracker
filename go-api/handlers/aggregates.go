package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/ice-tracker/api/database"
	"github.com/ice-tracker/api/models"
)

func GetNationalAggregate(c *gin.Context) {
	startDate := c.DefaultQuery("start_date", time.Now().AddDate(0, -1, 0).Format("2006-01-02"))
	endDate := c.DefaultQuery("end_date", time.Now().Format("2006-01-02"))

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var aggregate models.NationalAggregate
	aggregate.Period = "custom"

	// Get total arrests
	err := database.Pool.QueryRow(ctx, `
		SELECT COALESCE(SUM(arrest_count), 0)
		FROM arrests
		WHERE timestamp >= $1 AND timestamp <= $2
	`, startDate, endDate).Scan(&aggregate.TotalArrests)
	if err != nil {
		aggregate.TotalArrests = 0
	}

	// Get total detentions (average daily population)
	err = database.Pool.QueryRow(ctx, `
		SELECT COALESCE(AVG(detained_count), 0)
		FROM detentions
		WHERE timestamp >= $1 AND timestamp <= $2
	`, startDate, endDate).Scan(&aggregate.TotalDetentions)
	if err != nil {
		aggregate.TotalDetentions = 0
	}

	// Get total removals
	err = database.Pool.QueryRow(ctx, `
		SELECT COALESCE(SUM(removal_count), 0)
		FROM removals
		WHERE timestamp >= $1 AND timestamp <= $2
	`, startDate, endDate).Scan(&aggregate.TotalRemovals)
	if err != nil {
		aggregate.TotalRemovals = 0
	}

	start, _ := time.Parse("2006-01-02", startDate)
	end, _ := time.Parse("2006-01-02", endDate)
	aggregate.StartDate = start
	aggregate.EndDate = end

	c.JSON(http.StatusOK, aggregate)
}

func GetStateAggregate(c *gin.Context) {
	state := c.Param("state")
	startDate := c.DefaultQuery("start_date", time.Now().AddDate(0, -1, 0).Format("2006-01-02"))
	endDate := c.DefaultQuery("end_date", time.Now().Format("2006-01-02"))

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var aggregate models.NationalAggregate
	aggregate.Period = state

	// Get arrests for state
	err := database.Pool.QueryRow(ctx, `
		SELECT COALESCE(SUM(arrest_count), 0)
		FROM arrests
		WHERE state = $1 AND timestamp >= $2 AND timestamp <= $3
	`, state, startDate, endDate).Scan(&aggregate.TotalArrests)
	if err != nil {
		aggregate.TotalArrests = 0
	}

	// Get detentions for state
	err = database.Pool.QueryRow(ctx, `
		SELECT COALESCE(AVG(detained_count), 0)
		FROM detentions
		WHERE state = $1 AND timestamp >= $2 AND timestamp <= $3
	`, state, startDate, endDate).Scan(&aggregate.TotalDetentions)
	if err != nil {
		aggregate.TotalDetentions = 0
	}

	// Get removals for state
	err = database.Pool.QueryRow(ctx, `
		SELECT COALESCE(SUM(removal_count), 0)
		FROM removals
		WHERE state = $1 AND timestamp >= $2 AND timestamp <= $3
	`, state, startDate, endDate).Scan(&aggregate.TotalRemovals)
	if err != nil {
		aggregate.TotalRemovals = 0
	}

	start, _ := time.Parse("2006-01-02", startDate)
	end, _ := time.Parse("2006-01-02", endDate)
	aggregate.StartDate = start
	aggregate.EndDate = end

	c.JSON(http.StatusOK, aggregate)
}
