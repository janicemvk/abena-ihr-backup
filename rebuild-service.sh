#!/bin/bash

# Helper script to rebuild and restart Docker services
# Usage: ./rebuild-service.sh <service-name>

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
    echo "❌ Error: Please provide a service name"
    echo "Usage: ./rebuild-service.sh <service-name>"
    echo ""
    echo "Available services:"
    echo "  - telemedicine-platform"
    echo "  - abena-ihr"
    echo "  - background-modules"
    echo "  - provider-dashboard"
    echo "  - patient-dashboard"
    echo "  - unified-integration"
    echo "  - gamification"
    echo "  - ecdome-intelligence"
    echo "  - data-ingestion"
    echo "  - biomarker-gui"
    echo "  - module-registry"
    echo "  - business-rules"
    echo "  - dynamic-learning"
    echo "  - api-gateway"
    exit 1
fi

echo "🔄 Rebuilding and restarting $SERVICE_NAME..."

# Stop the service
echo "⏹️  Stopping $SERVICE_NAME..."
docker-compose -f docker-compose.simple.yml stop $SERVICE_NAME

# Remove the container
echo "🗑️  Removing $SERVICE_NAME container..."
docker-compose -f docker-compose.simple.yml rm -f $SERVICE_NAME

# Build without cache
echo "🔨 Building $SERVICE_NAME without cache..."
docker-compose -f docker-compose.simple.yml build --no-cache $SERVICE_NAME

# Start the service
echo "▶️  Starting $SERVICE_NAME..."
docker-compose -f docker-compose.simple.yml up -d $SERVICE_NAME

echo "✅ $SERVICE_NAME has been rebuilt and restarted!"
echo "🌐 Check the application at the appropriate URL" 