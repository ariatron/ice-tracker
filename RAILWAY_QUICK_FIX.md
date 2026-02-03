# Railway "Can't Find Dockerfile" - Quick Fix

## The Problem

Railway is looking for a Dockerfile in the root directory, but your Dockerfiles are in subdirectories:
- `python-collector/Dockerfile`
- `go-api/Dockerfile`
- `go-realtime/Dockerfile`

## Solution: Set Root Directory for Each Service

### Step-by-Step Fix

#### 1. Delete Failed Deployments (Optional)

In Railway dashboard, if you have failing services:
- Click the service → Settings → Danger Zone → Remove Service

#### 2. Add PostgreSQL Database First

**Important**: Do this first!

1. Click **"+ New"** in your Railway project
2. Select **"Database"** → **"Add PostgreSQL"**
3. Wait for it to provision (~30 seconds)
4. Click the PostgreSQL service
5. Go to **"Variables"** tab
6. Note these values (you'll need them):
   - `PGHOST`
   - `PGPORT` (usually 5432)
   - `PGDATABASE` (usually "railway")
   - `PGUSER` (usually "postgres")
   - `PGPASSWORD`

#### 3. Add Python Collector Service

1. Click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose **"ariatron/ice-tracker"**
4. Railway will create a new service

**Configure the service**:

1. **Click the new service** → **Settings** tab
2. **Under "Source" section**:
   - Find **"Root Directory"** field
   - Enter: `python-collector`
   - Click checkmark to save

3. **Under "Build" section**:
   - **Dockerfile Path**: `Dockerfile`
   - **Watch Paths**: `/python-collector/**`

4. **Go to "Variables" tab**:
   - Click **"New Variable"** and add these:
   ```
   TIMESCALE_HOST = <value from PGHOST above>
   TIMESCALE_PORT = 5432
   TIMESCALE_USER = <value from PGUSER above>
   TIMESCALE_PASSWORD = <value from PGPASSWORD above>
   TIMESCALE_DATABASE = <value from PGDATABASE above>
   SCHEDULER_TIMEZONE = America/Chicago
   LOG_LEVEL = INFO
   SCRAPER_ENABLED = true
   ```

5. **Click "Deploy"** (top right) or it will auto-deploy

#### 4. Add Go API Service

1. Click **"+ New"** → **"GitHub Repo"**
2. Select **"ariatron/ice-tracker"**

**Configure**:

1. **Settings** → **Source**:
   - **Root Directory**: `go-api`

2. **Settings** → **Build**:
   - **Dockerfile Path**: `Dockerfile`

3. **Variables** tab - Add same database vars as Python service:
   ```
   TIMESCALE_HOST = <same as above>
   TIMESCALE_PORT = 5432
   TIMESCALE_USER = <same as above>
   TIMESCALE_PASSWORD = <same as above>
   TIMESCALE_DATABASE = <same as above>
   API_PORT = 8080
   API_HOST = 0.0.0.0
   ```

4. **Settings** → **Networking**:
   - Click **"Generate Domain"**
   - You'll get a public URL like: `go-api-production.up.railway.app`
   - Save this URL - you'll need it for testing

5. **Deploy**

#### 5. Add Go Realtime Service (Optional for now)

Same steps as Go API:
- **Root Directory**: `go-realtime`
- **Dockerfile Path**: `Dockerfile`
- Same database variables
- No need for public domain

#### 6. Initialize Database Schema

After PostgreSQL is running, you need to run the schema:

**Option A: Using Railway SQL Console** (easiest):
1. Click your **PostgreSQL service**
2. Click **"Data"** tab (or "Query" if available)
3. Copy the entire contents of `init-scripts/01-schema.sql` from your repo
4. Paste and execute

**Option B: Using psql locally**:
1. Click PostgreSQL service → **"Connect"** tab
2. Copy the connection string
3. On your Mac:
   ```bash
   psql "postgresql://postgres:password@host:port/railway" \
     -f /path/to/ice-dashboard/init-scripts/01-schema.sql
   ```

#### 7. Verify Everything Works

**Check Python Collector**:
- Click service → **"Deployments"** → View latest logs
- Look for: "Starting scheduler..."

**Check Go API**:
- Test the public URL:
  ```bash
  curl https://your-go-api-url.up.railway.app/api/v1/health
  ```
- Should return JSON with `"status": "healthy"`

**Check Database**:
- Click PostgreSQL → **"Data"** tab
- Should see 6 tables: arrests, detentions, removals, community_reports, news_articles, data_source_health

---

## Visual Guide

```
Your Railway Project Structure:
├── PostgreSQL Database (Railway managed)
│   ├── Connection info in Variables
│   └── Schema initialized with 01-schema.sql
│
├── Python Collector Service
│   ├── Root Directory: python-collector
│   ├── Dockerfile Path: Dockerfile
│   └── Variables: DATABASE_* configured
│
├── Go API Service
│   ├── Root Directory: go-api
│   ├── Dockerfile Path: Dockerfile
│   ├── Variables: DATABASE_* configured
│   └── Public Domain: Generated
│
└── Go Realtime Service (optional)
    ├── Root Directory: go-realtime
    ├── Dockerfile Path: Dockerfile
    └── Variables: DATABASE_* configured
```

---

## Common Errors & Fixes

### "Failed to find build source"
- Make sure Root Directory is set correctly
- Check it matches the folder name exactly (case-sensitive)

### "Could not build image"
- Check build logs for specific error
- Usually means missing dependencies or wrong Dockerfile path

### "Connection refused" to database
- Make sure PostgreSQL service is running (green checkmark)
- Use internal hostname (from PGHOST variable) not external
- Railway services use internal networking

### Services deploy but crash immediately
- Check logs for errors
- Usually database connection issues
- Verify all TIMESCALE_* variables are set correctly

---

## Quick Checklist

- [ ] PostgreSQL database added and running
- [ ] Database connection info copied from PostgreSQL variables
- [ ] Python collector service created with `python-collector` root directory
- [ ] Python collector variables configured
- [ ] Go API service created with `go-api` root directory
- [ ] Go API variables configured
- [ ] Go API public domain generated
- [ ] Database schema initialized with 01-schema.sql
- [ ] All services showing green "Active" status
- [ ] Go API health endpoint responding

---

## After Deployment

Once everything is running:

1. **Get your Go API URL**:
   - Click Go API service → Settings → Public Networking
   - Copy the domain

2. **Test it**:
   ```bash
   curl https://your-url.up.railway.app/api/v1/health
   ```

3. **Get PostgreSQL connection for Grafana**:
   - Click PostgreSQL → Connect
   - Copy the **public** connection string
   - Use this in Grafana Cloud

4. **Connect Grafana Cloud**:
   - Host: From PostgreSQL public connection
   - Database: railway
   - User: postgres
   - Password: From PostgreSQL variables
   - SSL Mode: require

---

## Need Help?

If you're still stuck, tell me:
1. Which service is failing?
2. What does the error log say exactly?
3. Screenshot of the Settings page showing Root Directory

I'll help you debug it! 🔧
