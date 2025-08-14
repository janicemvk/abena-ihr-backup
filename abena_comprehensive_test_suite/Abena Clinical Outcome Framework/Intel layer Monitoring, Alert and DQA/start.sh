#!/bin/bash

# Abena IHR Intelligence Layer Startup Script

echo "🚀 Starting Abena IHR Intelligence Layer..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs grafana/dashboards grafana/datasources

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp config.env.example .env
    echo "⚠️  Please edit .env file with your configuration before starting services."
    echo "   Press Enter to continue or Ctrl+C to exit and configure .env first..."
    read
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check API server
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API Server is running at http://localhost:8000"
else
    echo "❌ API Server is not responding"
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅ Prometheus is running at http://localhost:9090"
else
    echo "❌ Prometheus is not responding"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Grafana is running at http://localhost:3000"
else
    echo "❌ Grafana is not responding"
fi

echo ""
echo "🎉 Abena IHR Intelligence Layer is ready!"
echo ""
echo "📊 Access Points:"
echo "   • API Server: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "📚 Next Steps:"
echo "   1. Configure your notification channels in .env"
echo "   2. Set up Grafana dashboards"
echo "   3. Run example usage: python example_usage.py"
echo ""
echo "🛑 To stop services: docker-compose down" 