-- ICE Activities Tracking Database Schema
-- TimescaleDB hypertables for time-series optimization

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Arrests table
CREATE TABLE arrests (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    state VARCHAR(2),
    county VARCHAR(100),
    city VARCHAR(100),
    arrest_count INTEGER,
    criminal_arrests INTEGER,
    non_criminal_arrests INTEGER,
    data_source VARCHAR(50),
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Detentions table
CREATE TABLE detentions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    facility_name VARCHAR(255),
    facility_id VARCHAR(50),
    state VARCHAR(2),
    city VARCHAR(100),
    detained_count INTEGER,
    capacity INTEGER,
    avg_daily_population DECIMAL(10,2),
    facility_type VARCHAR(50),
    data_source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Removals/Deportations table
CREATE TABLE removals (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    state VARCHAR(2),
    removal_count INTEGER,
    country_of_citizenship VARCHAR(100),
    removal_type VARCHAR(50), -- removals, returns, repatriations
    data_source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Community reports (raids, sightings)
CREATE TABLE community_reports (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    report_type VARCHAR(50), -- raid, sighting, checkpoint
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    state VARCHAR(2),
    city VARCHAR(100),
    address TEXT,
    description TEXT,
    verified BOOLEAN DEFAULT FALSE,
    data_source VARCHAR(50),
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- News articles
CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    published_at TIMESTAMPTZ NOT NULL,
    title TEXT,
    description TEXT,
    url TEXT UNIQUE,
    source VARCHAR(100),
    state VARCHAR(2),
    city VARCHAR(100),
    sentiment VARCHAR(20), -- extracted via NLP
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data source health monitoring
CREATE TABLE data_source_health (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100),
    last_successful_fetch TIMESTAMPTZ,
    last_attempt TIMESTAMPTZ,
    status VARCHAR(20), -- success, failed, degraded
    error_message TEXT,
    records_fetched INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertables for TimescaleDB optimization
SELECT create_hypertable('arrests', 'timestamp');
SELECT create_hypertable('detentions', 'timestamp');
SELECT create_hypertable('removals', 'timestamp');
SELECT create_hypertable('community_reports', 'timestamp');
SELECT create_hypertable('news_articles', 'published_at');
SELECT create_hypertable('data_source_health', 'created_at');

-- Create indexes for common queries
CREATE INDEX idx_arrests_state_timestamp ON arrests(state, timestamp DESC);
CREATE INDEX idx_arrests_source ON arrests(data_source);
CREATE INDEX idx_detentions_facility_timestamp ON detentions(facility_id, timestamp DESC);
CREATE INDEX idx_detentions_state_timestamp ON detentions(state, timestamp DESC);
CREATE INDEX idx_removals_state_timestamp ON removals(state, timestamp DESC);
CREATE INDEX idx_removals_country ON removals(country_of_citizenship);
CREATE INDEX idx_community_reports_location ON community_reports(latitude, longitude, timestamp DESC);
CREATE INDEX idx_community_reports_state ON community_reports(state, timestamp DESC);
CREATE INDEX idx_community_reports_verified ON community_reports(verified, timestamp DESC);
CREATE INDEX idx_news_articles_state_timestamp ON news_articles(state, published_at DESC);
CREATE INDEX idx_news_articles_source ON news_articles(source);
CREATE INDEX idx_data_source_health_source ON data_source_health(source_name, created_at DESC);

-- Create views for common aggregations
CREATE VIEW arrests_by_state_month AS
SELECT
    date_trunc('month', timestamp) as month,
    state,
    SUM(arrest_count) as total_arrests,
    SUM(criminal_arrests) as total_criminal,
    SUM(non_criminal_arrests) as total_non_criminal
FROM arrests
GROUP BY month, state
ORDER BY month DESC, state;

CREATE VIEW detention_capacity_utilization AS
SELECT
    date_trunc('day', timestamp) as day,
    facility_name,
    facility_id,
    state,
    AVG(detained_count) as avg_detained,
    AVG(capacity) as avg_capacity,
    CASE
        WHEN AVG(capacity) > 0 THEN (AVG(detained_count)::DECIMAL / AVG(capacity)::DECIMAL) * 100
        ELSE 0
    END as utilization_percent
FROM detentions
WHERE capacity IS NOT NULL AND capacity > 0
GROUP BY day, facility_name, facility_id, state
ORDER BY day DESC;

CREATE VIEW national_daily_summary AS
SELECT
    date_trunc('day', timestamp) as day,
    SUM(arrest_count) as total_arrests,
    COUNT(DISTINCT state) as states_with_activity
FROM arrests
GROUP BY day
ORDER BY day DESC;

-- Grant permissions (if needed for read-only users in future)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO readonly_user;

-- Insert initial health check record
INSERT INTO data_source_health (source_name, status, created_at)
VALUES ('system_initialization', 'success', NOW());

COMMENT ON TABLE arrests IS 'ICE arrest activities by location and time';
COMMENT ON TABLE detentions IS 'Detention facility capacity and population data';
COMMENT ON TABLE removals IS 'Removal and deportation statistics';
COMMENT ON TABLE community_reports IS 'Community-reported ICE activities and sightings';
COMMENT ON TABLE news_articles IS 'News articles about ICE enforcement activities';
COMMENT ON TABLE data_source_health IS 'Monitoring health and status of data collection sources';
