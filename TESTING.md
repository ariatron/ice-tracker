# Testing Guide

Complete testing procedures for the ICE Tracker system.

## Prerequisites

- Docker and Docker Compose installed and running
- `.env` file configured (copy from `.env.example`)
- Ports 5432 and 8080 available

## Quick Test

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
sleep 60

# Check service status
docker-compose ps

# Test API health
curl http://localhost:8080/api/v1/health

# Check if database is accessible
docker exec -it ice-timescaledb psql -U ice_tracker -d ice_activities -c "SELECT COUNT(*) FROM data_source_health;"
```

Expected output:
- All services show "Up" status
- API health returns `{"status":"healthy"}`
- Database query returns a count (at least 1 from initialization)

## Detailed Testing

### 1. Database Testing

**Test 1: Database Connection**
```bash
docker exec -it ice-timescaledb psql -U ice_tracker -d ice_activities
```

Expected: PostgreSQL prompt `ice_activities=#`

**Test 2: Verify Schema**
```sql
-- List all tables
\dt

-- Verify hypertables
SELECT hypertable_name FROM timescaledb_information.hypertables;

-- Check indexes
\di

-- View table structure
\d arrests
\d detentions
\d removals
```

Expected:
- 6 tables: arrests, detentions, removals, community_reports, news_articles, data_source_health
- 6 hypertables listed
- Multiple indexes on timestamp columns

**Test 3: Check Initial Data**
```sql
-- System initialization record
SELECT * FROM data_source_health ORDER BY created_at DESC;

-- Check views
SELECT * FROM arrests_by_state_month LIMIT 5;
SELECT * FROM detention_capacity_utilization LIMIT 5;
SELECT * FROM national_daily_summary LIMIT 5;
```

Expected:
- At least one health record from "system_initialization"
- Views may be empty if no data collected yet

### 2. Python Collector Testing

**Test 1: Check Logs**
```bash
docker logs ice-python-collector
```

Expected output includes:
- "ICE Data Collector Service Starting"
- "Database connection established"
- "Scheduled Jobs:" with cron schedules
- "Starting scheduler..."

**Test 2: Trigger Manual Scrape**
```bash
# Execute Python directly in container
docker exec -it ice-python-collector python -c "
from scrapers.ohss_scraper import OHSSScraper
scraper = OHSSScraper()
result = scraper.scrape()
print(f'Success: {result[\"success\"]}')
print(f'Records: {result[\"records_fetched\"]}')
"
```

Expected:
- Script runs without errors
- May return 0 records if OHSS site structure changed or data not available

**Test 3: Verify Data Import**
```bash
# Check if any arrests were imported
docker exec -it ice-timescaledb psql -U ice_tracker -d ice_activities -c "
  SELECT
    data_source,
    COUNT(*) as records,
    MIN(timestamp) as earliest,
    MAX(timestamp) as latest
  FROM arrests
  GROUP BY data_source;
"
```

Expected:
- If successful scrape: rows with data_source='OHSS'
- If no data yet: "0 rows" (normal for first run before scheduled time)

### 3. Go API Testing

**Test 1: Health Endpoint**
```bash
curl -s http://localhost:8080/api/v1/health | jq
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T...",
  "database": {
    "connected": true,
    "message": "connected"
  },
  "sources": []
}
```

**Test 2: Root Endpoint**
```bash
curl -s http://localhost:8080/ | jq
```

Expected: API information and endpoint list

**Test 3: Arrests Endpoint**
```bash
# Get all arrests (limit 10)
curl -s "http://localhost:8080/api/v1/arrests?limit=10" | jq

# Filter by state
curl -s "http://localhost:8080/api/v1/arrests?state=CA&limit=5" | jq

# Date range
curl -s "http://localhost:8080/api/v1/arrests?start_date=2026-01-01&end_date=2026-02-01&limit=5" | jq
```

Expected:
- JSON response with count and data array
- Empty array if no data imported yet
- Filtered results when data exists

**Test 4: Detentions Endpoint**
```bash
curl -s "http://localhost:8080/api/v1/detentions?limit=10" | jq
```

**Test 5: National Aggregate**
```bash
curl -s "http://localhost:8080/api/v1/aggregates/national" | jq
```

Expected:
```json
{
  "total_arrests": 0,
  "total_detentions": 0,
  "total_removals": 0,
  "period": "custom",
  "start_date": "...",
  "end_date": "..."
}
```

**Test 6: State Aggregate**
```bash
curl -s "http://localhost:8080/api/v1/aggregates/state/CA" | jq
```

### 4. Integration Testing

**Test Full Pipeline:**

```bash
#!/bin/bash
# Save as test-pipeline.sh

echo "=== ICE Tracker Pipeline Test ==="

echo -e "\n1. Testing Database..."
DB_COUNT=$(docker exec ice-timescaledb psql -U ice_tracker -d ice_activities -t -c "SELECT COUNT(*) FROM data_source_health;")
echo "Database health records: $DB_COUNT"

echo -e "\n2. Testing API Health..."
API_STATUS=$(curl -s http://localhost:8080/api/v1/health | jq -r '.status')
echo "API Status: $API_STATUS"

echo -e "\n3. Checking Data..."
ARREST_COUNT=$(curl -s "http://localhost:8080/api/v1/arrests?limit=1" | jq -r '.count')
echo "Arrests in database: $ARREST_COUNT"

echo -e "\n4. Testing Aggregates..."
NATIONAL=$(curl -s http://localhost:8080/api/v1/aggregates/national | jq -r '.total_arrests')
echo "National arrest total: $NATIONAL"

echo -e "\n=== Test Complete ==="

if [ "$API_STATUS" = "healthy" ]; then
  echo "✓ System is operational"
  exit 0
else
  echo "✗ System has issues"
  exit 1
fi
```

Run with:
```bash
chmod +x test-pipeline.sh
./test-pipeline.sh
```

### 5. Performance Testing

**Test 1: Query Performance**
```sql
-- Test time-series query performance
EXPLAIN ANALYZE
SELECT time_bucket('1 day', timestamp) as day, SUM(arrest_count)
FROM arrests
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY day
ORDER BY day DESC;
```

Expected: Query should complete in < 100ms even with thousands of rows

**Test 2: API Response Time**
```bash
# Test API latency
for i in {1..10}; do
  curl -w "@-" -o /dev/null -s http://localhost:8080/api/v1/health <<'EOF'
     time_total:  %{time_total}\n
EOF
done
```

Expected: < 100ms per request

**Test 3: Concurrent Requests**
```bash
# Install apache bench if needed: brew install httpd (macOS)
ab -n 100 -c 10 http://localhost:8080/api/v1/health
```

Expected: All requests succeed, reasonable throughput

### 6. Data Quality Testing

**Test 1: Validate Data Types**
```sql
-- Check for NULL values where not expected
SELECT COUNT(*) FROM arrests WHERE timestamp IS NULL;
SELECT COUNT(*) FROM arrests WHERE arrest_count IS NULL;

-- Check for invalid state codes
SELECT DISTINCT state FROM arrests WHERE LENGTH(state) != 2;

-- Check for future timestamps
SELECT COUNT(*) FROM arrests WHERE timestamp > NOW();
```

Expected: All counts should be 0

**Test 2: Check Data Ranges**
```sql
-- Validate arrest counts are reasonable
SELECT MIN(arrest_count), MAX(arrest_count), AVG(arrest_count)
FROM arrests
WHERE arrest_count > 0;

-- Check timestamp distribution
SELECT
  date_trunc('month', timestamp) as month,
  COUNT(*) as records
FROM arrests
GROUP BY month
ORDER BY month DESC;
```

**Test 3: Cross-Reference Health Data**
```sql
SELECT
  source_name,
  status,
  last_successful_fetch,
  records_fetched,
  error_message
FROM data_source_health
ORDER BY created_at DESC
LIMIT 10;
```

## Troubleshooting Test Failures

### Database Not Responding

```bash
# Check if container is running
docker ps | grep timescaledb

# Check logs
docker logs ice-timescaledb

# Restart database
docker-compose restart timescaledb

# Wait for health check
docker-compose ps timescaledb
```

### Python Collector Errors

```bash
# Check full logs
docker logs ice-python-collector --tail 100

# Check if scheduler is running
docker exec ice-python-collector ps aux | grep python

# Restart collector
docker-compose restart python-collector
```

### API Not Responding

```bash
# Check if container is running
docker ps | grep go-api

# Check logs
docker logs ice-go-api

# Test database connection from API container
docker exec ice-go-api curl http://localhost:8080/api/v1/health

# Restart API
docker-compose restart go-api
```

### No Data After Scraping

1. Check OHSS website is accessible:
   ```bash
   curl -I https://ohss.dhs.gov/topics/immigration/immigration-enforcement/monthly-tables
   ```

2. Check Python logs for scraping errors:
   ```bash
   docker logs ice-python-collector | grep ERROR
   ```

3. Manually trigger scraper with debug logging:
   ```bash
   docker exec -it ice-python-collector python -c "
   import logging
   logging.basicConfig(level=logging.DEBUG)
   from scrapers.ohss_scraper import OHSSScraper
   scraper = OHSSScraper()
   result = scraper.scrape()
   print(result)
   "
   ```

## Continuous Monitoring

**Set up periodic health checks:**

```bash
# Create monitor script
cat > monitor.sh <<'EOF'
#!/bin/bash
while true; do
  STATUS=$(curl -s http://localhost:8080/api/v1/health | jq -r '.status')
  echo "$(date): API Status = $STATUS"
  sleep 300  # Check every 5 minutes
done
EOF

chmod +x monitor.sh
./monitor.sh &
```

**Check logs regularly:**
```bash
# Watch all logs
docker-compose logs -f

# Watch specific service
docker-compose logs -f python-collector
```

## Test Data Generation (Optional)

If you want to test with sample data before OHSS scraper runs:

```sql
-- Insert sample arrest data
INSERT INTO arrests (timestamp, state, arrest_count, criminal_arrests, non_criminal_arrests, data_source)
VALUES
  (NOW() - INTERVAL '1 day', 'CA', 150, 80, 70, 'TEST'),
  (NOW() - INTERVAL '2 days', 'TX', 200, 120, 80, 'TEST'),
  (NOW() - INTERVAL '3 days', 'FL', 100, 60, 40, 'TEST'),
  (NOW() - INTERVAL '1 week', 'CA', 140, 75, 65, 'TEST');

-- Insert sample detention data
INSERT INTO detentions (timestamp, facility_name, state, detained_count, capacity, data_source)
VALUES
  (NOW() - INTERVAL '1 day', 'Test Facility A', 'CA', 500, 600, 'TEST'),
  (NOW() - INTERVAL '1 day', 'Test Facility B', 'TX', 800, 1000, 'TEST');

-- Insert sample removal data
INSERT INTO removals (timestamp, state, removal_count, country_of_citizenship, removal_type, data_source)
VALUES
  (NOW() - INTERVAL '1 day', 'CA', 50, 'Mexico', 'removal', 'TEST'),
  (NOW() - INTERVAL '1 day', 'TX', 80, 'Mexico', 'removal', 'TEST');
```

Then verify in API:
```bash
curl -s "http://localhost:8080/api/v1/arrests?limit=10" | jq
curl -s "http://localhost:8080/api/v1/aggregates/national" | jq
```

## Clean Up Test Data

```sql
-- Remove test data
DELETE FROM arrests WHERE data_source = 'TEST';
DELETE FROM detentions WHERE data_source = 'TEST';
DELETE FROM removals WHERE data_source = 'TEST';
```

## Next Steps

After successful testing:

1. ✅ Verify all services are running
2. ✅ Confirm database schema is correct
3. ✅ Test API endpoints return valid responses
4. ⏳ Wait for scheduled data collection (2 AM CST daily)
5. ⏳ Connect Grafana Cloud (see GRAFANA_SETUP.md)
6. ⏳ Create dashboards and visualizations
7. ⏳ Monitor system health regularly

## Automated Testing (Future)

Consider adding:
- Unit tests for Python scrapers
- Integration tests for API endpoints
- Load testing for production deployment
- Automated health checks with alerts
- CI/CD pipeline for deployments
