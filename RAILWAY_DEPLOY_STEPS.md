# Railway Deployment - Next Steps

✅ **Repository Ready**: https://github.com/ariatron/ice-tracker

Your code is now on GitHub and ready to deploy to Railway!

---

## Step 1: Sign Up for Railway

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign in with your **GitHub account** (ariatron)
4. Authorize Railway to access your repositories

---

## Step 2: Deploy Your Project

1. **Create New Project**
   - Click **"New Project"** button
   - Select **"Deploy from GitHub repo"**
   - Find and select: **ariatron/ice-tracker**

2. **Railway will automatically detect**:
   - Docker Compose configuration
   - Multiple services (timescaledb, python-collector, go-api, go-realtime)
   - It will create a service for each

3. **Wait for initial setup** (~30 seconds)
   - Railway will prepare your project
   - Don't worry about errors yet - we need to configure first

---

## Step 3: Configure Services

Railway will create 4 services. Configure each one:

### 🗄️ TimescaleDB Service

1. Click on the **timescaledb** service
2. Go to **Variables** tab
3. Add these environment variables:
   ```
   POSTGRES_USER=ice_tracker
   POSTGRES_PASSWORD=your_secure_password_here
   POSTGRES_DB=ice_activities
   ```
   ⚠️ **Important**: Choose a secure password (not the default)

4. Go to **Settings** tab
5. Scroll to **Networking** section
6. Click **Generate Domain** (if you want public access for Grafana)
   - This creates a public URL like: `timescaledb-production-1234.up.railway.app`
   - Note: Railway uses TCP proxying for databases

### 🐍 Python Collector Service

1. Click on the **python-collector** service
2. Go to **Variables** tab
3. Add these:
   ```
   TIMESCALE_HOST=timescaledb.railway.internal
   TIMESCALE_PORT=5432
   TIMESCALE_USER=ice_tracker
   TIMESCALE_PASSWORD=<same as above>
   TIMESCALE_DATABASE=ice_activities
   SCHEDULER_TIMEZONE=America/Chicago
   LOG_LEVEL=INFO
   SCRAPER_ENABLED=true
   ```

### 🚀 Go API Service

1. Click on the **go-api** service
2. Go to **Variables** tab
3. Add these:
   ```
   TIMESCALE_HOST=timescaledb.railway.internal
   TIMESCALE_PORT=5432
   TIMESCALE_USER=ice_tracker
   TIMESCALE_PASSWORD=<same as above>
   TIMESCALE_DATABASE=ice_activities
   API_PORT=8080
   API_HOST=0.0.0.0
   ```

4. Go to **Settings** tab
5. Click **Generate Domain**
   - This creates public API URL: `ice-tracker-production-1234.up.railway.app`
   - You can test it later: `https://your-url.up.railway.app/api/v1/health`

### ⏱️ Go Realtime Service

1. Click on the **go-realtime** service
2. Go to **Variables** tab
3. Add these:
   ```
   TIMESCALE_HOST=timescaledb.railway.internal
   TIMESCALE_PORT=5432
   TIMESCALE_USER=ice_tracker
   TIMESCALE_PASSWORD=<same as above>
   TIMESCALE_DATABASE=ice_activities
   POLL_INTERVAL_MINUTES=30
   ```

---

## Step 4: Deploy Services

After configuring variables:

1. Railway will automatically start building
2. Check **Deployments** tab for each service
3. Wait for all services to show ✓ **Active**
4. This takes 5-10 minutes for first deployment

**Check logs if any service fails**:
- Click service → **Deployments** → Latest deployment → **View Logs**

---

## Step 5: Get Database Connection Details

### For Internal Services (Python, Go API)
They use: `timescaledb.railway.internal:5432`

### For Grafana Cloud (External)

**Option A: Public TCP Proxy** (if you generated domain)
1. Click **timescaledb** service
2. Go to **Settings** → **Networking**
3. Note the **Public Domain** and **Port**
4. Format: `your-db.railway.app:port`

**Option B: Use Railway Plugin**
Railway has a PostgreSQL plugin that's easier:
1. In your project, click **+ New**
2. Select **Database** → **Add PostgreSQL**
3. This creates a managed PostgreSQL instance
4. You'll get connection URL directly
5. Use this instead of TimescaleDB service

⚠️ **Note**: If using Railway PostgreSQL, you need to:
- Run init scripts manually
- Or migrate your schema to the new database

---

## Step 6: Connect Grafana Cloud

1. **Sign up for Grafana Cloud**: https://grafana.com/auth/sign-up
2. **Add PostgreSQL Data Source**:
   - Go to **Connections** → **Data sources** → **Add data source**
   - Select **PostgreSQL**

3. **Configure** (using Railway database):
   ```
   Name: ICE Tracker TimescaleDB
   Host: <your-railway-db-host>:<port>
   Database: ice_activities
   User: ice_tracker
   Password: <your password>
   TLS/SSL Mode: require (Railway enforces SSL)
   PostgreSQL Version: 15
   TimescaleDB: ✓ (check this box)
   ```

4. Click **Save & Test**
   - Should show: ✓ "Database Connection OK"

---

## Step 7: Verify Deployment

### Check API is working:
```bash
curl https://your-go-api-url.up.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T...",
  "database": {
    "connected": true,
    "message": "connected"
  }
}
```

### Check database has tables:
In Railway dashboard:
1. Click **timescaledb** service
2. Click **Connect**
3. Use connection string with `psql` or database tool
4. Run: `\dt` to list tables

Should see: arrests, detentions, removals, community_reports, news_articles, data_source_health

### Check Python collector is running:
1. Click **python-collector** service
2. Go to **Deployments** → **View Logs**
3. Look for: "Starting scheduler..."

---

## Step 8: Create Grafana Dashboard

Once connected, create your first dashboard:

1. In Grafana, click **+** → **Dashboard**
2. **Add visualization**
3. Select **ICE Tracker TimescaleDB** data source

### Sample Panel Query:
```sql
SELECT
  date_trunc('day', timestamp) as time,
  SUM(arrest_count) as arrests
FROM arrests
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY time
ORDER BY time
```

---

## Costs

**Railway Free Tier**:
- $5 usage credit per month
- 512MB RAM per service
- Shared CPU

**Your app will use approximately**:
- TimescaleDB: ~200MB RAM
- Python Collector: ~150MB RAM
- Go API: ~50MB RAM
- Go Realtime: ~50MB RAM
- **Total: ~450MB** (within free tier)

**Estimated monthly cost**: $0-5 (should fit free tier)

If you exceed free tier:
- Upgrade to Hobby plan: $5/month
- Or optimize services (reduce memory)

---

## Troubleshooting

### Services won't start
- Check **Logs** in each service
- Verify environment variables are set correctly
- Check database is running first (others depend on it)

### Database connection refused
- Use `timescaledb.railway.internal` for internal connections
- Use public domain only for external (Grafana)
- Check password matches everywhere

### Out of memory
- Free tier has 512MB RAM per service limit
- Reduce Python worker threads if needed
- Consider upgrading to Hobby plan

### Build failures
- Check **Build Logs** in deployment
- Go build might need more dependencies
- Python might be missing packages

---

## Next Steps

1. ✅ Deploy to Railway (follow steps above)
2. ✅ Configure all services
3. ✅ Get database connection URL
4. ✅ Connect Grafana Cloud
5. ⏳ Create dashboards
6. ⏳ Wait for data (scraper runs daily 2 AM CST)
7. ⏳ Refine OHSS scraper to parse files correctly

---

## Alternative: Railway CLI (Advanced)

If you prefer command line:

```bash
# Install Railway CLI
brew install railway

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Run commands in Railway environment
railway run node script.js
```

---

## Support Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Your Repo**: https://github.com/ariatron/ice-tracker
- **Project Docs**: See README.md, TESTING.md, GRAFANA_SETUP.md

---

## Quick Links

- 📦 **GitHub Repo**: https://github.com/ariatron/ice-tracker
- 🚂 **Railway Dashboard**: https://railway.app/dashboard
- 📊 **Grafana Cloud**: https://grafana.com/auth/sign-in
- 📚 **Railway Deploy Guide**: https://docs.railway.app/deploy/deployments

---

**Ready to deploy? Go to https://railway.app and follow Step 1!** 🚀
