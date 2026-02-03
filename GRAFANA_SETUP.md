# Grafana Cloud Setup Guide

This guide will help you connect your ICE Tracker backend to Grafana Cloud and create your first dashboard.

## Prerequisites

- Grafana Cloud account (sign up at https://grafana.com/auth/sign-up/create-user)
- ICE Tracker services running (TimescaleDB and API)
- Database accessible from the internet (if running on a server) OR using Grafana Agent for local setup

## Step 1: Add PostgreSQL Data Source

1. **Log in to Grafana Cloud**
   - Go to your Grafana Cloud instance: `https://your-org.grafana.net`

2. **Navigate to Data Sources**
   - Click the menu icon (☰) → Configuration → Data Sources
   - Click "Add data source"
   - Search for and select "PostgreSQL"

3. **Configure Connection**

   Fill in the following details:

   ```
   Name: ICE Tracker TimescaleDB

   Host: <your-server-ip>:5432
   (If running locally, use localhost:5432 or set up SSH tunnel)

   Database: ice_activities
   User: ice_tracker
   Password: <from your .env file>

   TLS/SSL Mode: disable (for testing)
                 require (for production)

   PostgreSQL Version: 15
   TimescaleDB: enabled ✓
   ```

4. **Test Connection**
   - Click "Save & Test"
   - You should see: "Database Connection OK"

## Step 2: Create Your First Dashboard

### Option A: Import Pre-built Dashboard

1. **Create JSON file** `grafana-dashboard-phase1.json`:

```json
{
  "dashboard": {
    "title": "ICE Tracker - National Overview",
    "tags": ["ice", "enforcement", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Total Arrests (Last 30 Days)",
        "type": "stat",
        "targets": [
          {
            "datasource": "ICE Tracker TimescaleDB",
            "rawSql": "SELECT COALESCE(SUM(arrest_count), 0) as total FROM arrests WHERE timestamp >= NOW() - INTERVAL '30 days'",
            "format": "table"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Arrests by State (Last 30 Days)",
        "type": "table",
        "targets": [
          {
            "datasource": "ICE Tracker TimescaleDB",
            "rawSql": "SELECT state, SUM(arrest_count) as total_arrests FROM arrests WHERE timestamp >= NOW() - INTERVAL '30 days' GROUP BY state ORDER BY total_arrests DESC LIMIT 10",
            "format": "table"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Arrests Over Time",
        "type": "timeseries",
        "targets": [
          {
            "datasource": "ICE Tracker TimescaleDB",
            "rawSql": "SELECT time_bucket('1 day', timestamp) as time, SUM(arrest_count) as arrests FROM arrests WHERE $__timeFilter(timestamp) GROUP BY time ORDER BY time",
            "format": "time_series"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Data Source Health",
        "type": "table",
        "targets": [
          {
            "datasource": "ICE Tracker TimescaleDB",
            "rawSql": "SELECT DISTINCT ON (source_name) source_name, status, last_successful_fetch, records_fetched FROM data_source_health ORDER BY source_name, created_at DESC",
            "format": "table"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      }
    ],
    "refresh": "5m",
    "time": {
      "from": "now-30d",
      "to": "now"
    }
  }
}
```

2. **Import Dashboard**
   - In Grafana, click (+) → Import
   - Upload the JSON file or paste the JSON
   - Select your "ICE Tracker TimescaleDB" data source
   - Click "Import"

### Option B: Build Dashboard Manually

1. **Create New Dashboard**
   - Click (+) → Dashboard → Add new panel

2. **Panel 1: Total Arrests**
   - Visualization: Stat
   - Query:
     ```sql
     SELECT COALESCE(SUM(arrest_count), 0) as total
     FROM arrests
     WHERE timestamp >= NOW() - INTERVAL '30 days'
     ```
   - Title: "Total Arrests (Last 30 Days)"
   - Unit: Number
   - Color mode: Value

3. **Panel 2: Arrests by State**
   - Visualization: Table
   - Query:
     ```sql
     SELECT
       state,
       SUM(arrest_count) as total_arrests,
       SUM(criminal_arrests) as criminal,
       SUM(non_criminal_arrests) as non_criminal
     FROM arrests
     WHERE timestamp >= NOW() - INTERVAL '30 days'
     GROUP BY state
     ORDER BY total_arrests DESC
     LIMIT 10
     ```
   - Title: "Top 10 States by Arrests"

4. **Panel 3: Arrests Over Time**
   - Visualization: Time series
   - Query:
     ```sql
     SELECT
       time_bucket('1 day', timestamp) as time,
       SUM(arrest_count) as arrests
     FROM arrests
     WHERE $__timeFilter(timestamp)
     GROUP BY time
     ORDER BY time
     ```
   - Title: "Daily Arrests Trend"
   - Legend: Show
   - Fill opacity: 10

5. **Panel 4: Detention Capacity**
   - Visualization: Time series
   - Query:
     ```sql
     SELECT
       time_bucket('1 day', timestamp) as time,
       AVG(detained_count) as detained,
       AVG(capacity) as capacity
     FROM detentions
     WHERE $__timeFilter(timestamp)
     GROUP BY time
     ORDER BY time
     ```
   - Title: "Detention Facility Utilization"
   - Multiple series: detained, capacity

6. **Panel 5: Geographic Heatmap**
   - Visualization: Geomap
   - Query:
     ```sql
     SELECT
       state,
       SUM(arrest_count) as value,
       MAX(timestamp) as last_updated
     FROM arrests
     WHERE timestamp >= NOW() - INTERVAL '30 days'
     GROUP BY state
     ```
   - Map type: USA States
   - Color scheme: By value

7. **Panel 6: Data Source Health**
   - Visualization: Table
   - Query:
     ```sql
     SELECT DISTINCT ON (source_name)
       source_name,
       status,
       last_successful_fetch,
       last_attempt,
       records_fetched,
       error_message
     FROM data_source_health
     ORDER BY source_name, created_at DESC
     ```
   - Title: "Data Collection Status"

## Step 3: Configure Variables (Optional)

Add dashboard variables for filtering:

1. **State Variable**
   - Name: `state`
   - Type: Query
   - Query: `SELECT DISTINCT state FROM arrests ORDER BY state`
   - Multi-value: Yes
   - Include All option: Yes

2. **Time Range Presets**
   - Quick ranges: Last 7 days, Last 30 days, Last 90 days, Last 1 year

## Step 4: Set Up Alerts (Optional)

1. **Alert for Data Freshness**
   - Panel: Data Source Health
   - Condition: When last_successful_fetch is older than 48 hours
   - Notification: Email or Slack

2. **Alert for Unusual Activity**
   - Panel: Daily Arrests
   - Condition: When arrests > 2x 30-day average
   - Notification: Email or Slack

## Step 5: Share Dashboard

1. **Make Dashboard Public** (Optional)
   - Dashboard Settings → General
   - Enable "Public dashboard"
   - Share the public link

2. **Embed in Website** (Optional)
   - Dashboard Settings → Sharing
   - Copy embed code

3. **Schedule Reports** (Grafana Pro)
   - Dashboard → Share → Schedule PDF report
   - Set frequency (daily, weekly, monthly)

## Useful Queries

### Arrests by Month
```sql
SELECT
  date_trunc('month', timestamp) as month,
  SUM(arrest_count) as total_arrests,
  SUM(criminal_arrests) as criminal,
  SUM(non_criminal_arrests) as non_criminal
FROM arrests
WHERE $__timeFilter(timestamp)
GROUP BY month
ORDER BY month DESC
```

### Top Counties
```sql
SELECT
  state,
  county,
  SUM(arrest_count) as arrests
FROM arrests
WHERE timestamp >= NOW() - INTERVAL '30 days'
  AND county IS NOT NULL
GROUP BY state, county
ORDER BY arrests DESC
LIMIT 20
```

### Facility Capacity Utilization
```sql
SELECT
  facility_name,
  state,
  AVG(detained_count) as avg_detained,
  AVG(capacity) as avg_capacity,
  CASE
    WHEN AVG(capacity) > 0 THEN (AVG(detained_count) / AVG(capacity)) * 100
    ELSE 0
  END as utilization_percent
FROM detentions
WHERE timestamp >= NOW() - INTERVAL '30 days'
  AND capacity IS NOT NULL
  AND capacity > 0
GROUP BY facility_name, state
ORDER BY utilization_percent DESC
```

### Monthly Trend Comparison
```sql
SELECT
  date_trunc('month', timestamp) as month,
  SUM(arrest_count) as arrests,
  LAG(SUM(arrest_count)) OVER (ORDER BY date_trunc('month', timestamp)) as prev_month,
  CASE
    WHEN LAG(SUM(arrest_count)) OVER (ORDER BY date_trunc('month', timestamp)) IS NOT NULL
    THEN ((SUM(arrest_count) - LAG(SUM(arrest_count)) OVER (ORDER BY date_trunc('month', timestamp)))::float /
          LAG(SUM(arrest_count)) OVER (ORDER BY date_trunc('month', timestamp))) * 100
    ELSE 0
  END as percent_change
FROM arrests
WHERE timestamp >= NOW() - INTERVAL '12 months'
GROUP BY month
ORDER BY month DESC
```

## Troubleshooting

### Can't Connect to Database

**From Local Machine:**
- Grafana Cloud can't reach localhost
- Options:
  1. Deploy database to a server with public IP
  2. Use Grafana Agent with SSH tunnel
  3. Use ngrok or similar tunneling service

**From Server:**
- Check firewall allows connections on port 5432
- Verify PostgreSQL accepts external connections
- Test with: `psql -h your-server-ip -U ice_tracker -d ice_activities`

### No Data Showing

1. **Check if data exists:**
   ```sql
   SELECT COUNT(*) FROM arrests;
   SELECT * FROM data_source_health ORDER BY created_at DESC;
   ```

2. **Check Python collector logs:**
   ```bash
   docker logs ice-python-collector
   ```

3. **Verify time range:**
   - Grafana dashboard time range matches your data
   - Data may be historical (1-3 month lag from OHSS)

### Query Performance Issues

1. **Add indexes** (if not already present):
   ```sql
   CREATE INDEX IF NOT EXISTS idx_arrests_timestamp ON arrests(timestamp DESC);
   CREATE INDEX IF NOT EXISTS idx_detentions_timestamp ON detentions(timestamp DESC);
   ```

2. **Limit query time ranges:**
   - Use relative time ranges (Last 30 days) instead of absolute
   - Add LIMIT clauses to large queries

3. **Use time_bucket for aggregations:**
   ```sql
   SELECT time_bucket('1 day', timestamp), COUNT(*)
   FROM arrests
   GROUP BY 1
   ORDER BY 1 DESC
   ```

## Next Steps

1. ✅ Connect TimescaleDB to Grafana Cloud
2. ✅ Create basic dashboard
3. ⏳ Wait for first data collection (OHSS scraper runs daily at 2 AM CST)
4. ⏳ Refine dashboard based on actual data
5. ⏳ Add more data sources (Phase 2)
6. ⏳ Build advanced dashboards (Phase 3)

## Resources

- [Grafana PostgreSQL Documentation](https://grafana.com/docs/grafana/latest/datasources/postgres/)
- [TimescaleDB Query Optimization](https://docs.timescale.com/timescaledb/latest/how-to-guides/query-data/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/)

## Support

If you encounter issues:
1. Check the main README.md for troubleshooting
2. Review Docker logs: `docker-compose logs`
3. Test database connection directly with psql
4. Verify API is responding: `curl http://localhost:8080/api/v1/health`
