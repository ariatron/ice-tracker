# Connect to Grafana Cloud - Quick Start

Your ICE Tracker is running locally. Here are your options to connect Grafana Cloud:

## Current Setup
- Database: `localhost:5432` (TimescaleDB)
- API: `localhost:8081`
- Your Local IP: `192.168.1.187`

---

## Option 1: Quick Test with ngrok (RECOMMENDED for testing)

**Time: 5 minutes** | **Best for: Immediate testing**

### Setup
```bash
# Install ngrok
brew install ngrok

# Sign up for free account at https://ngrok.com
# Get your auth token from dashboard

# Authenticate
ngrok config add-authtoken YOUR_TOKEN

# Expose PostgreSQL port
ngrok tcp 5432
```

ngrok will give you a URL like: `tcp://0.tcp.ngrok.io:12345`

### Grafana Cloud Configuration
1. Go to https://grafana.com (sign in or create free account)
2. Navigate to: Connections → Data Sources → Add data source
3. Select: **PostgreSQL**
4. Configure:
   - **Name**: ICE Tracker TimescaleDB
   - **Host**: `0.tcp.ngrok.io:12345` (from ngrok output)
   - **Database**: `ice_activities`
   - **User**: `ice_tracker`
   - **Password**: `ice_tracker_2026_secure_pass`
   - **TLS/SSL Mode**: `disable`
   - **PostgreSQL Version**: `15`
   - **TimescaleDB**: ✓ (enable)

5. Click **Save & Test**

**Note**: ngrok free tier URLs change each time. This is perfect for testing but not for production.

---

## Option 2: Use Grafana Agent (Permanent local setup)

**Time: 15 minutes** | **Best for: Keeping data local**

Grafana Agent runs locally and sends metrics to Grafana Cloud without exposing your database.

### Setup
```bash
# Install Grafana Agent
brew install grafana-agent

# Create config
cat > grafana-agent.yaml <<'EOF'
server:
  log_level: info

integrations:
  postgres_configs:
    - connection_string: "postgresql://ice_tracker:ice_tracker_2026_secure_pass@localhost:5432/ice_activities"
      database: ice_activities
      enabled: true
      instance: ice-tracker-local

metrics:
  wal_directory: /tmp/grafana-agent-wal
  global:
    scrape_interval: 60s
    remote_write:
      - url: YOUR_GRAFANA_CLOUD_PROMETHEUS_URL
        basic_auth:
          username: YOUR_INSTANCE_ID
          password: YOUR_API_KEY
EOF

# Start agent
grafana-agent -config.file=grafana-agent.yaml
```

Then connect to the metrics in Grafana Cloud.

---

## Option 3: Deploy to Cloud (Production)

**Time: 30-60 minutes** | **Best for: Production deployment**

Deploy your entire stack to a cloud provider:

### Quick Deploy Options

**DigitalOcean ($10/month)**
```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create droplet
doctl compute droplet create ice-tracker \
  --image docker-20-04 \
  --size s-2vcpu-4gb \
  --region nyc3

# Get IP and SSH
doctl compute droplet list
ssh root@YOUR_DROPLET_IP

# Clone and deploy
git clone YOUR_REPO
cd ice-dashboard
docker-compose up -d

# Configure firewall to allow port 5432 from Grafana Cloud IPs only
ufw allow 5432/tcp
```

Then use the droplet's public IP in Grafana Cloud.

---

## Recommended Approach

**For immediate testing (now):**
1. Use **Option 1 (ngrok)** - fastest way to see your dashboards working
2. Follow the steps below

**For long-term (later today/tomorrow):**
1. Deploy to cloud with **Option 3**
2. Set up proper SSL/TLS
3. Restrict firewall to Grafana Cloud IPs only

---

## Step-by-Step: Option 1 (ngrok)

### 1. Install and Setup ngrok

```bash
# Install
brew install ngrok

# Sign up at https://dashboard.ngrok.com/signup
# Copy your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken

# Authenticate (replace with your token)
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### 2. Expose Database

Open a new terminal and run:
```bash
cd /Users/ariatron/.craft-agent/workspaces/my-workspace/sessions/260203-ruby-glen/ice-dashboard
ngrok tcp 5432
```

You'll see output like:
```
Session Status                online
Account                       Your Name (Plan: Free)
Forwarding                    tcp://0.tcp.ngrok.io:12345 -> localhost:5432
```

**Keep this terminal open!** Copy the forwarding address.

### 3. Create Grafana Cloud Account

1. Go to https://grafana.com/auth/sign-up/create-user
2. Sign up for free (no credit card required)
3. Create your stack (pick a name and region)
4. You'll get a URL like: `https://yourusername.grafana.net`

### 4. Add PostgreSQL Data Source

1. In Grafana Cloud, click **Connections** (left sidebar)
2. Click **Data sources**
3. Click **Add data source**
4. Search for and select **PostgreSQL**

5. Fill in the form:
   - **Name**: `ICE Tracker TimescaleDB`
   - **Host**: `0.tcp.ngrok.io:12345` (YOUR ngrok URL)
   - **Database**: `ice_activities`
   - **User**: `ice_tracker`
   - **Password**: `ice_tracker_2026_secure_pass`
   - **TLS/SSL Mode**: `disable` (for testing)
   - **PostgreSQL Version**: `15`
   - **TimescaleDB**: ✓ Check this box
   - **Max open connections**: `5`
   - **Max idle connections**: `2`

6. Scroll down and click **Save & Test**

You should see: ✓ "Database Connection OK"

### 5. Create Your First Dashboard

#### Quick Dashboard with Pre-built Queries

1. Click **+** (Create) → **Dashboard**
2. Click **Add visualization**
3. Select your **ICE Tracker TimescaleDB** data source

#### Panel 1: Total Arrests (Last 30 Days)

- **Visualization**: Stat
- **Query** (switch to Code/Raw SQL):
```sql
SELECT COALESCE(SUM(arrest_count), 0) as value
FROM arrests
WHERE timestamp >= NOW() - INTERVAL '30 days'
```
- **Panel Title**: "Total Arrests (Last 30 Days)"
- Click **Apply**

#### Panel 2: Arrests by State

1. **Add Panel** → **Visualization**
2. **Visualization**: Table
3. **Query**:
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
- **Panel Title**: "Top 10 States by Arrests"
- Click **Apply**

#### Panel 3: Data Source Health

1. **Add Panel** → **Visualization**
2. **Visualization**: Table
3. **Query**:
```sql
SELECT DISTINCT ON (source_name)
  source_name,
  status,
  last_successful_fetch,
  records_fetched,
  CASE
    WHEN last_successful_fetch IS NULL THEN 'Never'
    WHEN last_successful_fetch < NOW() - INTERVAL '48 hours' THEN 'Stale'
    ELSE 'Fresh'
  END as freshness
FROM data_source_health
ORDER BY source_name, created_at DESC
```
- **Panel Title**: "Data Source Status"
- Click **Apply**

6. **Save Dashboard** (top right) → Name it "ICE Tracker - Overview"

### 6. Verify Data

Since the scraper found files but hasn't imported data yet (classification issue), you might see:
- Empty charts for arrests/detentions
- Data source health showing OHSS attempts

This is expected! The system is working; it just needs data to display.

---

## Troubleshooting

### "Connection refused"
- Check Docker is running: `docker-compose ps`
- Check database is accessible: `docker exec ice-timescaledb psql -U ice_tracker -d ice_activities -c "SELECT 1"`
- Verify ngrok is running and showing "online" status

### "Authentication failed"
- Double-check password: `ice_tracker_2026_secure_pass`
- Verify user exists: `docker exec ice-timescaledb psql -U ice_tracker -d ice_activities -c "SELECT current_user"`

### "No data in dashboard"
- Check if data exists:
  ```bash
  docker exec ice-timescaledb psql -U ice_tracker -d ice_activities -c "SELECT COUNT(*) FROM arrests"
  ```
- Check scraper logs: `docker logs ice-python-collector | tail -50`
- The scraper has downloaded files but needs refinement to parse them correctly

### ngrok session expired
- Free tier sessions expire after 2 hours
- Simply restart: `ngrok tcp 5432`
- Update the host in Grafana data source settings with new URL

---

## Next Steps After Connection

1. **Test the connection** - Verify "Database Connection OK"
2. **Create basic dashboard** - Use queries above
3. **Wait for data** - Scraper runs daily at 2 AM CST
4. **Refine scraper** - Update OHSS parser to correctly classify files
5. **Deploy to production** - Move to cloud server with proper security

---

## Security Notes

⚠️ **Important for Production:**
- ngrok exposes your database to the internet
- Free tier ngrok URLs are public
- For production:
  - Deploy to cloud with firewall rules
  - Enable SSL/TLS (require mode)
  - Use strong passwords
  - Restrict access to Grafana Cloud IPs only
  - Set up VPN or SSH tunnel

For now, testing with ngrok is fine since:
- It's temporary
- Your database has no sensitive data yet
- You can stop ngrok anytime

---

## Quick Command Reference

```bash
# Check services
docker-compose ps

# View logs
docker logs ice-python-collector
docker logs ice-go-api

# Test database
docker exec ice-timescaledb psql -U ice_tracker -d ice_activities

# Check for data
docker exec ice-timescaledb psql -U ice_tracker -d ice_activities -c "SELECT COUNT(*) FROM arrests"

# Start ngrok
ngrok tcp 5432

# Stop everything
docker-compose down
# Stop ngrok: Ctrl+C in ngrok terminal
```

---

## Ready to Connect?

1. **Open new terminal** → Start ngrok → Copy forwarding URL
2. **Open Grafana Cloud** → Add data source → Use ngrok URL
3. **Create dashboard** → Add panels with SQL queries above
4. **Celebrate** 🎉 → Your ICE tracker is visualized!

**Have questions?** Check [GRAFANA_SETUP.md](./GRAFANA_SETUP.md) for more details or [TESTING.md](./TESTING.md) for troubleshooting.
