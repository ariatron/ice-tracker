# Railway Build Fix Guide

## The Problem

Railway doesn't handle docker-compose.yml multi-service deployments the same way as local Docker. It tries to deploy each service independently but fails because:

1. Build contexts don't work (`build: ./python-collector`)
2. Service dependencies aren't resolved
3. Docker Compose version warning

## Solution: Use Railway's Service-per-Directory Approach

### Option 1: Use Railway PostgreSQL Plugin (RECOMMENDED - Easiest)

Instead of deploying TimescaleDB yourself, use Railway's managed PostgreSQL:

1. **In your Railway project**:
   - Click **"+ New"**
   - Select **"Database"** → **"Add PostgreSQL"**
   - Railway will create a managed PostgreSQL instance

2. **Get Connection Details**:
   - Click the PostgreSQL service
   - Copy the connection string
   - Note: `DATABASE_URL` environment variable is auto-created

3. **Deploy other services**:
   - **New Service** → **"GitHub Repo"**
   - Configure each service separately:

#### Python Collector Service:
   - **Root Directory**: `/python-collector`
   - **Dockerfile Path**: `python-collector/Dockerfile`
   - **Environment Variables**:
     ```
     TIMESCALE_HOST=<postgres-host-from-railway>
     TIMESCALE_PORT=5432
     TIMESCALE_USER=postgres
     TIMESCALE_PASSWORD=<from-railway-postgres>
     TIMESCALE_DATABASE=railway
     SCHEDULER_TIMEZONE=America/Chicago
     LOG_LEVEL=INFO
     SCRAPER_ENABLED=true
     ```

#### Go API Service:
   - **Root Directory**: `/go-api`
   - **Dockerfile Path**: `go-api/Dockerfile`
   - **Environment Variables**: (same as above)
   - **Generate Domain** for public access

#### Go Realtime Service:
   - **Root Directory**: `/go-realtime`
   - **Dockerfile Path**: `go-realtime/Dockerfile`
   - **Environment Variables**: (same as above)

4. **Run Database Schema**:
   After PostgreSQL is created, you need to initialize it:
   - Download `init-scripts/01-schema.sql` from your repo
   - Connect to Railway PostgreSQL using their SQL editor or `psql`
   - Run the schema script

---

### Option 2: Deploy Each Service Individually (Alternative)

Instead of using docker-compose, deploy 4 separate services pointing to different directories:

1. **Create 4 Railway Services**:
   - Service 1: Python Collector (root: `/python-collector`)
   - Service 2: Go API (root: `/go-api`)
   - Service 3: Go Realtime (root: `/go-realtime`)
   - Service 4: Use Railway PostgreSQL Plugin

2. **For each service**, set the build configuration:
   - **Builder**: Dockerfile
   - **Dockerfile Path**: `Dockerfile` (relative to root directory)

---

### Option 3: Create Individual Railway Config Files (Manual)

Create Railway config for each service:

**python-collector/railway.toml**:
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "python main.py"
```

**go-api/railway.toml**:
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "./api"
```

**go-realtime/railway.toml**:
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "./realtime"
```

---

## Quick Fix Right Now

**In your Railway dashboard**:

1. **Delete the current deployment** (if it's failing)

2. **Add Railway PostgreSQL**:
   - Click **"+ New"** → **"Database"** → **"PostgreSQL"**
   - Wait for it to provision
   - Note the connection details

3. **Add Python Collector Service**:
   - Click **"+ New"** → **"GitHub Repo"**
   - Select `ariatron/ice-tracker`
   - **Settings** → **Root Directory**: `python-collector`
   - **Settings** → **Build**: Dockerfile
   - **Variables**: Add all TIMESCALE_* variables
   - Deploy

4. **Add Go API Service**:
   - Click **"+ New"** → **"GitHub Repo"**
   - Select `ariatron/ice-tracker`
   - **Settings** → **Root Directory**: `go-api`
   - **Variables**: Add all TIMESCALE_* variables
   - **Settings** → Generate Domain (for public access)
   - Deploy

5. **Add Go Realtime Service**:
   - Click **"+ New"** → **"GitHub Repo"**
   - Select `ariatron/ice-tracker`
   - **Settings** → **Root Directory**: `go-realtime`
   - **Variables**: Add all TIMESCALE_* variables
   - Deploy

6. **Initialize Database Schema**:
   - Go to Railway PostgreSQL service
   - Click **"Connect"** → **"SQL Client"**
   - Copy contents of `init-scripts/01-schema.sql`
   - Paste and execute

---

## What's the Actual Error?

Can you copy/paste the build logs from Railway? It will help me give you a more specific fix.

Look for:
- Red error messages in the build logs
- "failed to build" messages
- Missing dependency errors
- Context errors

The error message will tell us exactly what Railway is struggling with.

---

## Alternative: Deploy to Different Platform

If Railway continues to be difficult, we can quickly switch to:

**Render.com** (also free):
- Better docker-compose support
- Easier multi-service apps
- Takes 15 minutes

**DigitalOcean App Platform** ($5/month):
- Good docker-compose support
- More straightforward
- Takes 20 minutes

Let me know the error and I'll help you fix it! 🔧
