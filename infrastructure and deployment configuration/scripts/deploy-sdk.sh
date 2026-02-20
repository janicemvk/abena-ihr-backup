#!/bin/bash

set -euo pipefail

# =====================================================
# ABENA SHARED SDK DEPLOYMENT SCRIPT
# =====================================================

# Configuration
NAMESPACE="abena-ihr"
SDK_IMAGE="abena-shared-sdk"
SDK_VERSION="${1:-latest}"
DEPLOYMENT_NAME="abena-shared-sdk"
SERVICE_NAME="sdk-service"
HEALTH_ENDPOINT="/health"
READY_ENDPOINT="/ready"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "docker is not installed"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_info "Creating namespace $NAMESPACE..."
        kubectl create namespace $NAMESPACE
    fi
    
    log_success "Prerequisites check passed"
}

# Build and push SDK image
build_sdk_image() {
    log_info "Building SDK image..."
    
    # Build the SDK image
    docker build -t $SDK_IMAGE:$SDK_VERSION -f Dockerfile.sdk .
    
    # Tag for registry (adjust registry URL as needed)
    docker tag $SDK_IMAGE:$SDK_VERSION registry.abena-health.com/$SDK_IMAGE:$SDK_VERSION
    
    # Push to registry
    docker push registry.abena-health.com/$SDK_IMAGE:$SDK_VERSION
    
    log_success "SDK image built and pushed successfully"
}

# Deploy SDK service
deploy_sdk() {
    log_info "Deploying SDK service..."
    
    # Update the image tag in the deployment
    kubectl set image deployment/$DEPLOYMENT_NAME sdk-service=registry.abena-health.com/$SDK_IMAGE:$SDK_VERSION -n $NAMESPACE
    
    # Wait for rollout to complete
    kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=300s
    
    log_success "SDK service deployed successfully"
}

# Health check function
health_check() {
    log_info "Performing health checks..."
    
    # Get the service URL
    SERVICE_URL=$(kubectl get service $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$SERVICE_URL" ]; then
        # Try to get the service URL from port-forward for local testing
        SERVICE_URL="localhost:3001"
    fi
    
    # Health check
    for i in {1..30}; do
        if curl -f -s "http://$SERVICE_URL$HEALTH_ENDPOINT" > /dev/null; then
            log_success "Health check passed"
            return 0
        fi
        
        log_info "Health check attempt $i/30 - waiting..."
        sleep 10
    done
    
    log_error "Health check failed after 30 attempts"
    return 1
}

# Readiness check function
readiness_check() {
    log_info "Performing readiness checks..."
    
    # Get the service URL
    SERVICE_URL=$(kubectl get service $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$SERVICE_URL" ]; then
        SERVICE_URL="localhost:3001"
    fi
    
    # Readiness check
    for i in {1..20}; do
        if curl -f -s "http://$SERVICE_URL$READY_ENDPOINT" > /dev/null; then
            log_success "Readiness check passed"
            return 0
        fi
        
        log_info "Readiness check attempt $i/20 - waiting..."
        sleep 5
    done
    
    log_error "Readiness check failed after 20 attempts"
    return 1
}

# Performance test
performance_test() {
    log_info "Running performance tests..."
    
    # Run k6 performance test
    if command -v k6 &> /dev/null; then
        k6 run k6/sdk-load-test.js --out json=results/sdk-performance-$(date +%Y%m%d_%H%M%S).json
        log_success "Performance test completed"
    else
        log_warning "k6 not found, skipping performance test"
    fi
}

# Rollback function
rollback() {
    log_warning "Rolling back deployment..."
    
    # Rollback to previous version
    kubectl rollout undo deployment/$DEPLOYMENT_NAME -n $NAMESPACE
    
    # Wait for rollback to complete
    kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=300s
    
    log_success "Rollback completed"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up old images..."
    
    # Remove old Docker images (keep last 5)
    docker images $SDK_IMAGE --format "table {{.Repository}}:{{.Tag}}" | tail -n +6 | awk '{print $1}' | xargs -r docker rmi
    
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    log_info "Starting SDK deployment..."
    
    # Check prerequisites
    check_prerequisites
    
    # Build and push image
    build_sdk_image
    
    # Deploy SDK service
    deploy_sdk
    
    # Health checks
    if ! health_check; then
        log_error "Health check failed, rolling back..."
        rollback
        exit 1
    fi
    
    if ! readiness_check; then
        log_error "Readiness check failed, rolling back..."
        rollback
        exit 1
    fi
    
    # Performance test
    performance_test
    
    # Cleanup
    cleanup
    
    log_success "SDK deployment completed successfully!"
}

# Error handling
trap 'log_error "Deployment failed with error code $?"' ERR

# Run main function
main "$@" 