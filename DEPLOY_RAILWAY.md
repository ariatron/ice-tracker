# Deploy ICE Tracker to Railway (Free Tier)

Railway.app offers a generous free tier perfect for this project. This will give you a public URL for Grafana Cloud to connect to.

## Quick Deploy (10 minutes)

### Prerequisites
- GitHub account
- Railway account (free)

### Step 1: Create GitHub Repository

```bash
cd /Users/ariatron/.craft-agent/workspaces/my-workspace/sessions/260203-ruby-glen/ice-dashboard

# Initialize git if not already done
git init

# Create .gitignore
cat > .gitignore <<'EOF'
.env
data/
logs/
*.log
__pycache__/
*.pyc
.DS_Store
EOF

# Commit all files
git add .
git commit -m "Initial commit - ICE Tracker dashboard"

# Create repo on GitHub (via web or gh CLI)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/ice-tracker.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway

1. **Sign up**: Go to https://railway.app and sign in with GitHub

2. **New Project**: Click "New Project"

3. **Deploy from GitHub**: Select your ice-tracker repository

4. **Railway will detect Docker Compose and offer to deploy all services**

5. **Set Environment Variables**:
   - Click on each service → Variables
   - Add: `TIMESCALE_PASSWORD=your_secure_password_here`

6. **Expose Services**:
   - Click on `go-api` service
   - Go to Settings → Generate Domain
   - You'll get a URL like: `ice-tracker-production.up.railway.app`
   - Click on `timescaledb` service
   - Go to Settings → Networking → Make Public
   - You'll get a public hostname and port

7. **Wait for Deployment** (2-3 minutes)

### Step 3: Get Connection Details

Railway will provide:
- **Database Host**: `something.railway.internal` or public hostname
- **Port**: Usually 5432 (or custom port if public)
- **Public API**: `your-app.up.railway.app`

### Step 4: Connect Grafana Cloud

Use the Railway-provided database connection:
- **Host**: `your-db-host.railway.app:5432`
- **Database**: `ice_activities`
- **User**: `ice_tracker`
- **Password**: (the one you set)
- **SSL Mode**: `require` (Railway enforces SSL)

---

## Alternative: Render.com (Also Free)

If Railway doesn't work, try Render.com:

### Render Setup

1. Sign up at https://render.com

2. Create New → PostgreSQL (Free tier)
   - Database name: `ice_activities`
   - Note the connection details

3. Create New → Web Service (from Docker)
   - Connect your GitHub repo
   - Docker Compose not directly supported, but can deploy individual services

4. You'll need to create separate services for each container

---

## Alternative: DigitalOcean ($6/month, $200 free credit)

### Quick DigitalOcean Setup

```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create droplet with Docker pre-installed
doctl compute droplet create ice-tracker \
  --image docker-20-04 \
  --size s-2vcpu-4gb-120gb-intel \
  --region nyc3 \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header)

# Get IP
doctl compute droplet list

# SSH into droplet
ssh root@YOUR_DROPLET_IP

# Clone your repo
git clone https://github.com/YOUR_USERNAME/ice-tracker.git
cd ice-tracker

# Set environment variables
cp .env.example .env
nano .env  # Edit password

# Start services
docker-compose up -d

# Configure firewall (allow only Grafana Cloud IPs)
ufw allow 22/tcp
ufw allow 5432/tcp
ufw allow 8081/tcp
ufw enable
```

Then use `YOUR_DROPLET_IP:5432` in Grafana Cloud.

---

## Comparison

| Option | Cost | Time | Difficulty | Best For |
|--------|------|------|------------|----------|
| **Railway** | Free* | 10 min | Easy | Quick deployment |
| **Render** | Free* | 15 min | Medium | Alternative to Railway |
| **DigitalOcean** | $6/mo** | 20 min | Medium | Full control |
| **AWS/GCP** | Varies | 30+ min | Hard | Enterprise |

\* Free tier limits: Railway (512MB RAM, $5/month credit), Render (limited uptime)
\*\* $200 free credit for new accounts (60 days)

---

## Which Should You Choose?

**For immediate testing**: **Railway** (easiest, fastest)

**For production**: **DigitalOcean** (full control, predictable costs)

**For zero cost**: **Railway** or **Render** free tiers (with limitations)

---

## Railway Deployment Steps (Detailed)

### 1. Prepare Your Repository

```bash
cd ice-dashboard

# Make sure Docker images are not committed
echo ".env" >> .gitignore
echo "data/" >> .gitignore
echo "logs/" >> .gitignore

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
# (Do this via GitHub website or gh CLI)
```

### 2. Railway Setup

**Create Railway Project:**
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your repo
5. Select your ice-tracker repository

**Configure Services:**

Railway will detect `docker-compose.yml` and create services:

**For TimescaleDB:**
- Railway will create a PostgreSQL service
- Set environment variable: `POSTGRES_PASSWORD=your_password`
- Enable public networking if needed

**For Python Collector:**
- Will build from `python-collector/Dockerfile`
- Add environment variables from your `.env` file

**For Go API:**
- Will build from `go-api/Dockerfile`
- Generate public domain for external access
- Add environment variables

**For Go Realtime:**
- Will build from `go-realtime/Dockerfile`
- This is a placeholder, so it will just run and wait

### 3. Get Connection Info

After deployment completes:

1. Click on **TimescaleDB** service
2. Go to **Connect** tab
3. Copy connection details:
   - Internal URL (for other services)
   - Public URL (for Grafana Cloud)

Example:
```
Internal: timescaledb.railway.internal:5432
Public: monorail.proxy.rlwy.net:12345
```

### 4. Update Grafana Cloud

In Grafana Cloud data source:
- **Host**: `monorail.proxy.rlwy.net:12345`
- **Database**: `ice_activities`
- **User**: `ice_tracker`
- **Password**: (your password)
- **SSL Mode**: `require`
- **PostgreSQL Version**: `15`
- **TimescaleDB**: ✓

### 5. Test Connection

Railway provides logs for each service. Check:
- Database is running
- Python collector is scraping
- API is responsive

---

## Troubleshooting Railway

### Services Won't Start
- Check logs in Railway dashboard
- Verify environment variables are set
- Check build logs for errors

### Database Connection Issues
- Make sure internal URLs are used between services
- Public URL should only be for external connections
- Verify SSL mode is correct

### Out of Memory
- Free tier has 512MB RAM limit
- May need to upgrade for all services
- Consider Render or DigitalOcean for more resources

---

## Ready to Deploy?

**Fastest path**: Railway (10 minutes)
1. Create GitHub repo
2. Push your code
3. Connect Railway to repo
4. Get database public URL
5. Connect Grafana Cloud

**Want me to help you with any specific step?**
