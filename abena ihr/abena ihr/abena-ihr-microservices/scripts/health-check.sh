#!/bin/bash

# =============================================
# ABENA IHR MICROSERVICES - HEALTH CHECK SCRIPT
# =============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}🔍 $1${NC}"
}

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local service_name=$2
    local timeout=${3:-10}
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        print_status "$service_name is healthy"
        return 0
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

# Function to check Docker container
check_container() {
    local container_name=$1
    local service_name=$2
    
    if docker ps --format "table {{.Names}}" | grep -q "^$container_name$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
        if [ "$status" = "running" ]; then
            print_status "$service_name container is running"
            return 0
        else
            print_warning "$service_name container is not running (status: $status)"
            return 1
        fi
    else
        print_error "$service_name container is not found"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    local db_type=$1
    local container_name=$2
    
    case $db_type in
        "postgres")
            if docker exec -it "$container_name" pg_isready -U abena_user > /dev/null 2>&1; then
                print_status "PostgreSQL database is healthy"
                return 0
            else
                print_error "PostgreSQL database is not responding"
                return 1
            fi
            ;;
        "mongodb")
            if docker exec -it "$container_name" mongosh --eval "db.runCommand('ping')" > /dev/null 2>&1; then
                print_status "MongoDB database is healthy"
                return 0
            else
                print_error "MongoDB database is not responding"
                return 1
            fi
            ;;
        "redis")
            if docker exec -it "$container_name" redis-cli ping > /dev/null 2>&1; then
                print_status "Redis cache is healthy"
                return 0
            else
                print_error "Redis cache is not responding"
                return 1
            fi
            ;;
    esac
}

# Function to check Kafka
check_kafka() {
    if docker exec -it abena-kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
        print_status "Kafka is healthy"
        return 0
    else
        print_error "Kafka is not responding"
        return 1
    fi
}

# Function to check monitoring services
check_monitoring() {
    print_header "Checking Monitoring Services"
    
    # Check Prometheus
    check_endpoint "http://localhost:9090/-/healthy" "Prometheus" 5
    
    # Check Grafana
    check_endpoint "http://localhost:3000/api/health" "Grafana" 5
    
    # Check Jaeger
    check_endpoint "http://localhost:16686/api/services" "Jaeger" 5
    
    # Check Kibana
    check_endpoint "http://localhost:5601/api/status" "Kibana" 5
    
    # Check Elasticsearch
    check_endpoint "http://localhost:9200/_cluster/health" "Elasticsearch" 5
}

# Function to check foundational services
check_foundational_services() {
    print_header "Checking Foundational Services"
    
    # Check service containers
    check_container "abena-blockchain-service" "Blockchain Service"
    check_container "abena-data-ingestion-service" "Data Ingestion Service"
    check_container "abena-privacy-security-service" "Privacy & Security Service"
    check_container "abena-unified-data-service" "Unified Data Service"
    check_container "abena-auth-service" "Auth Service"
    
    # Check service endpoints
    check_endpoint "http://localhost:8000/health" "Blockchain Service API"
    check_endpoint "http://localhost:8001/health" "Data Ingestion Service API"
    check_endpoint "http://localhost:8002/health" "Privacy & Security Service API"
    check_endpoint "http://localhost:8003/health" "Unified Data Service API"
    check_endpoint "http://localhost:8004/health" "Auth Service API"
}

# Function to check application services
check_application_services() {
    print_header "Checking Application Services"
    
    # Check service containers
    check_container "abena-analytics-engine-service" "Analytics Engine Service"
    check_container "abena-clinical-decision-support-service" "Clinical Decision Support Service"
    
    # Check service endpoints
    check_endpoint "http://localhost:8010/health" "Analytics Engine Service API"
    check_endpoint "http://localhost:8011/health" "Clinical Decision Support Service API"
}

# Function to check infrastructure services
check_infrastructure_services() {
    print_header "Checking Infrastructure Services"
    
    # Check databases
    check_database "postgres" "abena-postgres"
    check_database "mongodb" "abena-mongodb"
    check_database "redis" "abena-redis"
    
    # Check message broker
    check_kafka
    
    # Check API Gateway
    check_container "abena-kong" "Kong API Gateway"
    check_endpoint "http://localhost:8005/status" "Kong API Gateway"
}

# Function to check system resources
check_system_resources() {
    print_header "Checking System Resources"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_status "Docker is installed"
        docker --version
    else
        print_error "Docker is not installed"
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_status "Docker Compose is installed"
        docker-compose --version
    else
        print_error "Docker Compose is not installed"
    fi
    
    # Check disk space
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 90 ]; then
        print_status "Disk space is adequate ($disk_usage% used)"
    else
        print_warning "Disk space is running low ($disk_usage% used)"
    fi
    
    # Check memory usage
    local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$mem_usage" -lt 90 ]; then
        print_status "Memory usage is normal ($mem_usage% used)"
    else
        print_warning "Memory usage is high ($mem_usage% used)"
    fi
}

# Function to generate health report
generate_report() {
    local report_file="health-report-$(date +%Y%m%d-%H%M%S).txt"
    
    print_header "Generating Health Report: $report_file"
    
    {
        echo "Abena IHR Microservices Health Report"
        echo "Generated: $(date)"
        echo "======================================"
        echo ""
        
        echo "System Resources:"
        echo "================="
        docker --version
        docker-compose --version
        echo "Disk Usage: $(df -h / | awk 'NR==2 {print $5}')"
        echo "Memory Usage: $(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
        echo ""
        
        echo "Container Status:"
        echo "================="
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        
        echo "Service Health:"
        echo "==============="
        # This would be populated with actual health check results
        echo "Health checks completed"
        
    } > "$report_file"
    
    print_status "Health report saved to: $report_file"
}

# Main health check function
main() {
    echo -e "${BLUE}🏥 Abena IHR Microservices Health Check${NC}"
    echo "=============================================="
    echo ""
    
    # Check system resources
    check_system_resources
    echo ""
    
    # Check infrastructure services
    check_infrastructure_services
    echo ""
    
    # Check foundational services
    check_foundational_services
    echo ""
    
    # Check application services
    check_application_services
    echo ""
    
    # Check monitoring services
    check_monitoring
    echo ""
    
    # Generate report
    generate_report
    echo ""
    
    print_status "Health check completed!"
    echo ""
    print_status "Service URLs:"
    echo "  Blockchain Service: http://localhost:8000"
    echo "  Data Ingestion Service: http://localhost:8001"
    echo "  Privacy & Security Service: http://localhost:8002"
    echo "  Unified Data Service: http://localhost:8003"
    echo "  Auth Service: http://localhost:8004"
    echo "  Analytics Engine Service: http://localhost:8010"
    echo "  Clinical Decision Support Service: http://localhost:8011"
    echo "  Kong API Gateway: http://localhost:8005"
    echo "  Grafana: http://localhost:3000 (admin/admin)"
    echo "  Prometheus: http://localhost:9090"
    echo "  Kibana: http://localhost:5601"
    echo "  Jaeger: http://localhost:16686"
}

# Run main function
main "$@" 