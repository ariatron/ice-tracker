package models

import "time"

type Arrest struct {
	ID                 int       `json:"id"`
	Timestamp          time.Time `json:"timestamp"`
	State              string    `json:"state"`
	County             string    `json:"county"`
	City               string    `json:"city"`
	ArrestCount        int       `json:"arrest_count"`
	CriminalArrests    int       `json:"criminal_arrests"`
	NonCriminalArrests int       `json:"non_criminal_arrests"`
	DataSource         string    `json:"data_source"`
	SourceURL          string    `json:"source_url"`
	CreatedAt          time.Time `json:"created_at"`
}

type Detention struct {
	ID                 int     `json:"id"`
	Timestamp          time.Time `json:"timestamp"`
	FacilityName       string  `json:"facility_name"`
	FacilityID         string  `json:"facility_id"`
	State              string  `json:"state"`
	City               string  `json:"city"`
	DetainedCount      int     `json:"detained_count"`
	Capacity           int     `json:"capacity"`
	AvgDailyPopulation float64 `json:"avg_daily_population"`
	FacilityType       string  `json:"facility_type"`
	DataSource         string  `json:"data_source"`
	CreatedAt          time.Time `json:"created_at"`
}

type Removal struct {
	ID                   int       `json:"id"`
	Timestamp            time.Time `json:"timestamp"`
	State                string    `json:"state"`
	RemovalCount         int       `json:"removal_count"`
	CountryOfCitizenship string    `json:"country_of_citizenship"`
	RemovalType          string    `json:"removal_type"`
	DataSource           string    `json:"data_source"`
	CreatedAt            time.Time `json:"created_at"`
}

type CommunityReport struct {
	ID          int       `json:"id"`
	Timestamp   time.Time `json:"timestamp"`
	ReportType  string    `json:"report_type"`
	Latitude    float64   `json:"latitude"`
	Longitude   float64   `json:"longitude"`
	State       string    `json:"state"`
	City        string    `json:"city"`
	Address     string    `json:"address"`
	Description string    `json:"description"`
	Verified    bool      `json:"verified"`
	DataSource  string    `json:"data_source"`
	SourceURL   string    `json:"source_url"`
	CreatedAt   time.Time `json:"created_at"`
}

type NewsArticle struct {
	ID          int       `json:"id"`
	PublishedAt time.Time `json:"published_at"`
	Title       string    `json:"title"`
	Description string    `json:"description"`
	URL         string    `json:"url"`
	Source      string    `json:"source"`
	State       string    `json:"state"`
	City        string    `json:"city"`
	Sentiment   string    `json:"sentiment"`
	CreatedAt   time.Time `json:"created_at"`
}

type DataSourceHealth struct {
	ID                  int       `json:"id"`
	SourceName          string    `json:"source_name"`
	LastSuccessfulFetch time.Time `json:"last_successful_fetch"`
	LastAttempt         time.Time `json:"last_attempt"`
	Status              string    `json:"status"`
	ErrorMessage        string    `json:"error_message"`
	RecordsFetched      int       `json:"records_fetched"`
	CreatedAt           time.Time `json:"created_at"`
}

type HealthResponse struct {
	Status    string                 `json:"status"`
	Timestamp time.Time              `json:"timestamp"`
	Database  DatabaseHealth         `json:"database"`
	Sources   []DataSourceHealth     `json:"sources,omitempty"`
}

type DatabaseHealth struct {
	Connected bool   `json:"connected"`
	Message   string `json:"message,omitempty"`
}

type NationalAggregate struct {
	TotalArrests    int       `json:"total_arrests"`
	TotalDetentions int       `json:"total_detentions"`
	TotalRemovals   int       `json:"total_removals"`
	Period          string    `json:"period"`
	StartDate       time.Time `json:"start_date"`
	EndDate         time.Time `json:"end_date"`
}
