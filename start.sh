#!/bin/bash
# ICE Tracker Quick Start Script

set -e

echo "=================================="
echo "ICE Tracker - Quick Start"
echo "=================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo ""
    echo "Please start Docker Desktop and try again:"
    echo "  - macOS: Open Docker Desktop from Applications"
    echo "  - Linux: sudo systemctl start docker"
    echo "  - Windows: Start Docker Desktop from Start Menu"
    echo ""
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and set TIMESCALE_PASSWORD"
    echo "   Current password: change_this_secure_password"
    echo ""
    read -p "Press Enter to continue with default password (not recommended for production) or Ctrl+C to exit and edit .env file..."
fi

echo "✓ Configuration file exists"
echo ""

# Start services
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "Service Status:"
docker-compose ps

echo ""
echo "=================================="
echo "Services Started!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Check health:"
echo "   curl http://localhost:8080/api/v1/health"
echo ""
echo "2. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "3. Wait for data collection (runs daily at 2 AM CST)"
echo "   Or manually trigger:"
echo "   docker exec -it ice-python-collector python -c \"from scrapers.ohss_scraper import OHSSScraper; print(OHSSScraper().scrape())\""
echo ""
echo "4. Connect Grafana Cloud:"
echo "   See GRAFANA_SETUP.md"
echo ""
echo "5. Full testing:"
echo "   See TESTING.md"
echo ""
echo "To stop services:"
echo "   docker-compose down"
echo ""
echo "To view this project status:"
echo "   cat PROJECT_STATUS.md"
echo ""
echo "=================================="
