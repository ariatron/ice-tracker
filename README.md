# ICE Activities Tracking Dashboard

A comprehensive monitoring system to track ICE enforcement activities across the United States, combining official government data, independent research, and community reporting through Grafana Cloud dashboards.

## Architecture

- **TimescaleDB**: PostgreSQL with time-series optimization
- **Python Collector**: Scrapes official government data sources
- **Go API Server**: High-performance API for Grafana
- **Go Real-time Collector**: Community reports and news (Phase 3)
- **Grafana Cloud**: Visualization layer

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Grafana Cloud account (free tier works)

### Setup

1. **Clone and configure**

```bash
cd ice-dashboard
cp .env.example .env
```

2. **Edit `.env` file** - Set a secure password:

```bash
TIMESCALE_PASSWORD=your_secure_password_here
```

3. **Start the services**

```bash
docker-compose up -d
```

4. **Check service health**

```bash
# Check logs
docker-compose logs -f

# Check API health
curl http://localhost:8080/api/v1/health
```

5. **Connect Grafana Cloud to TimescaleDB**

In Grafana Cloud:
- Go to Configuration → Data Sources → Add data source
- Select PostgreSQL
- Configure:
  - Host: `your-server-ip:5432`
  - Database: `ice_activities`
  - User: `ice_tracker`
  - Password: (from .env)
  - TLS Mode: disable (enable for production)

## Services

### TimescaleDB (Port 5432)
- PostgreSQL database with TimescaleDB extension
- Stores all collected data in hypertables
- Automatic schema initialization on first run

### Python Collector
- Runs scheduled jobs to collect data
- OHSS scraper: Daily at 2 AM CST
- TRAC scraper: Weekly (Phase 2)
- Stores data in TimescaleDB

### Go API Server (Port 8080)
- REST API for data access
- Used by Grafana for querying data
- Health checks and monitoring

**API Endpoints:**
- `GET /api/v1/health` - Health check
- `GET /api/v1/arrests?state=CA&start_date=2026-01-01&limit=100`
- `GET /api/v1/detentions?state=TX&facility_id=ABC123`
- `GET /api/v1/aggregates/national`
- `GET /api/v1/aggregates/state/:state`

### Go Real-time Collector
- Phase 3 - Not yet implemented
- Will collect community reports and news

## Data Sources

### Phase 1 (Implemented)
- ✅ DHS OHSS Monthly Tables - Official enforcement statistics

### Phase 2 (Coming Soon)
- ⏳ ICE Statistics - Quarterly reports
- ⏳ TRAC Immigration - FOIA data
- ⏳ Deportation Data Project - Historical datasets

### Phase 3 (Coming Soon)
- ⏳ Community reporting platforms
- ⏳ News RSS feeds
- ⏳ Real-time monitoring

## Database Schema

### Core Tables
- `arrests` - Arrest activities by location and time
- `detentions` - Detention facility capacity and population
- `removals` - Removal and deportation statistics
- `community_reports` - Community-reported activities (Phase 3)
- `news_articles` - News coverage (Phase 3)
- `data_source_health` - Data collection monitoring

All tables are TimescaleDB hypertables optimized for time-series queries.

## Grafana Dashboards

### Phase 1 Dashboard
1. **National Overview**
   - Total arrests by month
   - Geographic heat map
   - Data source health

### Phase 2+ Dashboards (Planned)
2. State Deep Dive
3. Detention Facilities
4. Community Reports & Real-time
5. Data Quality & Operations

## Development

### Local Development (without Docker)

**Database:**
```bash
# Start TimescaleDB locally
docker run -d --name timescale \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=ice_activities \
  timescale/timescaledb:latest-pg15

# Run schema
psql -h localhost -U postgres -d ice_activities -f init-scripts/01-schema.sql
```

**Python Collector:**
```bash
cd python-collector
pip install -r requirements.txt
export TIMESCALE_HOST=localhost
export TIMESCALE_PASSWORD=yourpassword
python main.py
```

**Go API:**
```bash
cd go-api
go mod download
go run main.go
```

### Testing the Pipeline

```bash
# 1. Check database
docker exec -it ice-timescaledb psql -U ice_tracker -d ice_activities

# Run queries
SELECT COUNT(*) FROM arrests;
SELECT * FROM data_source_health ORDER BY created_at DESC LIMIT 5;

# 2. Test API
curl http://localhost:8080/api/v1/health
curl http://localhost:8080/api/v1/arrests?limit=10

# 3. Check Python collector logs
docker logs ice-python-collector
```

## Maintenance

### Backup Database
```bash
docker exec ice-timescaledb pg_dump -U ice_tracker ice_activities > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker exec -i ice-timescaledb psql -U ice_tracker ice_activities
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f python-collector
docker-compose logs -f go-api
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart python-collector
```

## Troubleshooting

### Database Connection Issues
- Check `.env` file has correct password
- Verify TimescaleDB is healthy: `docker-compose ps`
- Check logs: `docker-compose logs timescaledb`

### Python Collector Not Running
- Check logs: `docker-compose logs python-collector`
- Verify database connection is working
- Ensure OHSS website is accessible

### API Returns Empty Data
- Check if Python collector has run and imported data
- Query database directly to verify data exists
- Check API logs for errors

### Grafana Can't Connect
- Ensure TimescaleDB port 5432 is accessible from Grafana Cloud
- Check firewall rules if running on a server
- Verify credentials are correct

## Production Deployment

### Security Checklist
- [ ] Set strong database password
- [ ] Enable TLS for database connections
- [ ] Add API authentication
- [ ] Configure firewall rules
- [ ] Enable HTTPS for API server
- [ ] Set up automated backups
- [ ] Configure monitoring alerts

### Resource Requirements
- **Minimum**: 2 vCPU, 4GB RAM, 20GB storage
- **Recommended**: 4 vCPU, 8GB RAM, 50GB storage

### Estimated Costs
- Self-hosted: $10-20/month (VPS)
- Grafana Cloud: Free tier sufficient
- Total: ~$11-31/month

## Project Status

### Phase 1: Foundation ✅
- [x] TimescaleDB setup
- [x] Database schema with hypertables
- [x] Python OHSS scraper
- [x] Go API server
- [x] Docker Compose configuration
- [ ] Basic Grafana dashboard

### Phase 2: Government Data (Next)
- [ ] ICE Statistics scraper
- [ ] TRAC data integration
- [ ] Deportation Data Project import
- [ ] Automated scheduling

### Phase 3: Real-time & Community
- [ ] Community platform scrapers
- [ ] RSS news aggregation
- [ ] Real-time monitoring

## Contributing

This is an open monitoring project. Improvements welcome:
- Additional data sources
- Better scraping logic
- Dashboard designs
- Documentation

## License

MIT License - See LICENSE file

## Disclaimer

This tool aggregates publicly available data for monitoring and research purposes. Data may be incomplete or delayed. Always verify information from official sources.

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review this README
- Check the implementation plan: `plans/ice-dashboard-implementation-plan.md`
