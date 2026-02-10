#!/bin/bash

# =============================================
# ABENA IHR MICROSERVICES - DEPLOYMENT SCRIPT
# =============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
SERVICE=${2:-all}

echo -e "${BLUE}🚀 Abena IHR Microservices Deployment${NC}"
echo -e "${BLUE}Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "${BLUE}Service: ${YELLOW}$SERVICE${NC}"
echo ""

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp env.example .env
        print_warning "Please edit .env file with your configuration before continuing."
        exit 1
    fi
    
    print_status "Prerequisites check completed."
}

# Function to deploy foundational services
deploy_foundational_services() {
    print_status "Deploying foundational services..."
    
    cd foundational-services
    
    # Deploy each foundational service
    services=("unified-data-service" "auth-service" "data-ingestion-service" "privacy-security-service" "blockchain-service")
    
    for service in "${services[@]}"; do
        if [ -d "$service" ]; then
            print_status "Deploying $service..."
            cd "$service"
            
            if [ -f "docker-compose.yml" ]; then
                docker-compose up -d
                print_status "$service deployed successfully."
            else
                print_warning "No docker-compose.yml found in $service"
            fi
            
            cd ..
        else
            print_warning "Service directory $service not found."
        fi
    done
    
    cd ..
}

# Function to deploy application services
deploy_application_services() {
    print_status "Deploying application services..."
    
    cd application-services
    
    # Deploy each application service
    services=("analytics-engine-service" "clinical-decision-support-service" "provider-workflow-service" "telemedicine-service" "patient-engagement-service")
    
    for service in "${services[@]}"; do
        if [ -d "$service" ]; then
            print_status "Deploying $service..."
            cd "$service"
            
            if [ -f "docker-compose.yml" ]; then
                docker-compose up -d
                print_status "$service deployed successfully."
            else
                print_warning "No docker-compose.yml found in $service"
            fi
            
            cd ..
        else
            print_warning "Service directory $service not found."
        fi
    done
    
    cd ..
}

# Function to deploy infrastructure services
deploy_infrastructure_services() {
    print_status "Deploying infrastructure services..."
    
    # Deploy monitoring stack
    if [ -d "infrastructure/monitoring" ]; then
        print_status "Deploying monitoring stack..."
        cd infrastructure/monitoring
        
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
            print_status "Monitoring stack deployed successfully."
        fi
        
        cd ../..
    fi
    
    # Deploy logging stack
    if [ -d "infrastructure/logging" ]; then
        print_status "Deploying logging stack..."
        cd infrastructure/logging
        
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
            print_status "Logging stack deployed successfully."
        fi
        
        cd ../..
    fi
}

# Function to deploy specific service
deploy_specific_service() {
    local service_name=$1
    print_status "Deploying specific service: $service_name"
    
    # Check if service exists in foundational services
    if [ -d "foundational-services/$service_name" ]; then
        cd "foundational-services/$service_name"
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
            print_status "$service_name deployed successfully."
        else
            print_error "No docker-compose.yml found in $service_name"
        fi
        cd ../..
        return
    fi
    
    # Check if service exists in application services
    if [ -d "application-services/$service_name" ]; then
        cd "application-services/$service_name"
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
            print_status "$service_name deployed successfully."
        else
            print_error "No docker-compose.yml found in $service_name"
        fi
        cd ../..
        return
    fi
    
    print_error "Service $service_name not found."
}

# Function to deploy all services
deploy_all_services() {
    print_status "Deploying all services..."
    
    # Deploy infrastructure first
    deploy_infrastructure_services
    
    # Deploy foundational services
    deploy_foundational_services
    
    # Deploy application services
    deploy_application_services
    
    # Deploy main orchestration
    if [ -f "docker-compose.yml" ]; then
        print_status "Deploying main orchestration..."
        docker-compose up -d
        print_status "Main orchestration deployed successfully."
    fi
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for services to start
    sleep 30
    
    # Check foundational services
    services=(
        "http://localhost:8000/health"  # Blockchain
        "http://localhost:8001/health"  # Data Ingestion
        "http://localhost:8002/health"  # Privacy & Security
        "http://localhost:8003/health"  # Unified Data
        "http://localhost:8004/health"  # Auth
    )
    
    for url in "${services[@]}"; do
        if curl -f -s "$url" > /dev/null; then
            print_status "Service at $url is healthy"
        else
            print_warning "Service at $url is not responding"
        fi
    done
    
    # Check application services
    app_services=(
        "http://localhost:8010/health"  # Analytics Engine
        "http://localhost:8011/health"  # Clinical Decision Support
    )
    
    for url in "${app_services[@]}"; do
        if curl -f -s "$url" > /dev/null; then
            print_status "Service at $url is healthy"
        else
            print_warning "Service at $url is not responding"
        fi
    done
}

# Function to show deployment status
show_status() {
    print_status "Deployment Status:"
    echo ""
    docker-compose ps
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

# Main deployment logic
main() {
    check_prerequisites
    
    case $SERVICE in
        "all")
            deploy_all_services
            ;;
        "foundational")
            deploy_foundational_services
            ;;
        "application")
            deploy_application_services
            ;;
        "infrastructure")
            deploy_infrastructure_services
            ;;
        *)
            if [ "$SERVICE" != "all" ]; then
                deploy_specific_service "$SERVICE"
            else
                deploy_all_services
            fi
            ;;
    esac
    
    check_health
    show_status
    
    print_status "Deployment completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "  1. Configure your environment variables in .env"
    echo "  2. Set up your database schemas"
    echo "  3. Configure your API keys and external services"
    echo "  4. Run health checks: ./scripts/health-check.sh"
    echo "  5. Access the monitoring dashboards"
}

# Run main function
main "$@" 