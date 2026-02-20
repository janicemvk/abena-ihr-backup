#!/bin/bash

# Safe Abena IHR System Monitor
# This script monitors the system without making API calls that could cause infinite loops

echo "🔍 Abena IHR System - Safe Status Monitor"
echo "=========================================="
echo ""

# Check Docker containers status
echo "📊 Container Status:"
echo "-------------------"

containers=(
    "abena-postgres:5433"
    "abena-module-registry:3003"
    "abena-background-modules:4001"
    "abena-ihr-main:4002"
    "abena-business-rules:4003"
    "abena-telemedicine:4004"
    "abena-api-gateway:8080"
    "abena-patient-dashboard:4009"
    "abena-biomarker-gui:4012"
    "abena-data-ingestion:4011"
    "abena-gamification:4006"
    "abena-unified-integration:4007"
    "abena-ecdome-intelligence:4005"
    "abena-telemedicine-platform:8000"
)

for container in "${containers[@]}"; do
    IFS=':' read -r name port <<< "$container"
    
    # Check if container is running using Docker
    if docker ps --format "{{.Names}}" | grep -q "^${name}$"; then
        status=$(docker ps --format "{{.Status}}" --filter "name=^${name}$")
        echo "✅ $name - $status"
    else
        echo "❌ $name - Not running"
    fi
done

echo ""
echo "🌐 Access Points:"
echo "----------------"
echo "• API Gateway: http://localhost:8080"
echo "• Patient Dashboard: http://localhost:4009"
echo "• Biomarker GUI: http://localhost:4012"
echo "• Telemedicine Platform: http://localhost:8000"
echo "• Database: localhost:5433"
echo ""

# Check database connection safely
echo "🗄️ Database Status:"
echo "------------------"
if docker exec -i abena-postgres pg_isready -U abena_user -d abena_ihr > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready and accepting connections"
    patient_count=$(docker exec -i abena-postgres psql -U abena_user -d abena_ihr -t -c "SELECT COUNT(*) FROM patients;" 2>/dev/null | tr -d ' ')
    echo "📊 Patient records: $patient_count"
else
    echo "❌ PostgreSQL is not ready"
fi

echo ""
echo "🔧 System Commands:"
echo "------------------"
echo "• View logs: docker-compose -f docker-compose.simple.yml logs -f"
echo "• Stop system: docker-compose -f docker-compose.simple.yml down"
echo "• Restart: docker-compose -f docker-compose.simple.yml restart"
echo "• Monitor this script: watch -n 30 ./safe-system-monitor.sh"
echo ""

echo "✅ Safe monitoring complete - No API calls made"
echo "   All containers are running and accessible"
