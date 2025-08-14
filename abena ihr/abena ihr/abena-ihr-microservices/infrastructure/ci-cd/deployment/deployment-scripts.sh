#!/bin/bash

# Abena IHR Deployment Scripts
# Healthcare microservices deployment automation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-"staging"}
NAMESPACE="abena-ihr"
REGISTRY="registry.abena-ihr.com"
VERSION=${VERSION:-"latest"}

# Functions
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

# Validate environment
validate_environment() {
    log_info "Validating deployment environment..."
    
    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT. Must be dev, staging, or production"
        exit 1
    fi
    
    # Check kubectl access
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check namespace exists
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_error "Namespace $NAMESPACE does not exist"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

# Deploy database services
deploy_database() {
    log_info "Deploying database services..."
    
    # Apply database configurations
    kubectl apply -f kubernetes/configmaps/database-config.yaml -n $NAMESPACE
    kubectl apply -f kubernetes/secrets/database-secrets.yaml -n $NAMESPACE
    
    # Deploy PostgreSQL
    kubectl apply -f kubernetes/deployments/database-deployment.yaml -n $NAMESPACE
    
    # Wait for database to be ready
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
    
    # Deploy Redis
    kubectl apply -f kubernetes/deployments/database-deployment.yaml -n $NAMESPACE
    
    # Wait for Redis to be ready
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s
    
    log_success "Database services deployed"
}

# Deploy application services
deploy_applications() {
    log_info "Deploying application services..."
    
    # List of services to deploy
    services=(
        "patient-engagement"
        "data-ingestion"
        "clinical-decision-support"
        "privacy-security"
        "blockchain"
        "auth"
    )
    
    for service in "${services[@]}"; do
        log_info "Deploying $service..."
        
        # Update image tag
        kubectl set image deployment/$service $service=$REGISTRY/$service:$VERSION -n $NAMESPACE
        
        # Wait for rollout
        kubectl rollout status deployment/$service -n $NAMESPACE --timeout=300s
        
        log_success "$service deployed successfully"
    done
}

# Deploy monitoring and logging
deploy_monitoring() {
    log_info "Deploying monitoring and logging..."
    
    # Apply monitoring configurations
    kubectl apply -f monitoring/ -n monitoring
    kubectl apply -f logging/ -n logging
    
    # Wait for monitoring to be ready
    kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=300s
    kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=300s
    
    log_success "Monitoring and logging deployed"
}

# Deploy security components
deploy_security() {
    log_info "Deploying security components..."
    
    # Apply security configurations
    kubectl apply -f security/ -n security
    
    # Wait for Vault to be ready
    kubectl wait --for=condition=ready pod -l app=vault -n security --timeout=300s
    
    log_success "Security components deployed"
}

# Deploy network policies
deploy_network_policies() {
    log_info "Deploying network policies..."
    
    kubectl apply -f kubernetes/network-policies/ -n $NAMESPACE
    
    log_success "Network policies deployed"
}

# Deploy autoscaling
deploy_autoscaling() {
    log_info "Deploying autoscaling configurations..."
    
    kubectl apply -f kubernetes/autoscaling/ -n $NAMESPACE
    
    log_success "Autoscaling configurations deployed"
}

# Deploy backup jobs
deploy_backup() {
    log_info "Deploying backup configurations..."
    
    kubectl apply -f kubernetes/backup/ -n $NAMESPACE
    
    log_success "Backup configurations deployed"
}

# Health check
health_check() {
    log_info "Performing health checks..."
    
    # Check all pods are running
    failed_pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running -o jsonpath='{.items[*].metadata.name}')
    
    if [[ -n "$failed_pods" ]]; then
        log_error "Failed pods found: $failed_pods"
        kubectl describe pods -n $NAMESPACE --field-selector=status.phase!=Running
        exit 1
    fi
    
    # Check services are accessible
    services=(
        "patient-engagement-service:8000"
        "data-ingestion-service:8000"
        "clinical-decision-support-service:8000"
        "privacy-security-service:8000"
        "blockchain-service:8080"
        "auth-service:3000"
    )
    
    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if kubectl exec -n $NAMESPACE deployment/$(echo $service_name | sed 's/-service//') -- curl -f http://localhost:$port/health &> /dev/null; then
            log_success "$service_name health check passed"
        else
            log_error "$service_name health check failed"
            exit 1
        fi
    done
    
    log_success "All health checks passed"
}

# Rollback deployment
rollback() {
    log_warning "Rolling back deployment..."
    
    services=(
        "patient-engagement"
        "data-ingestion"
        "clinical-decision-support"
        "privacy-security"
        "blockchain"
        "auth"
    )
    
    for service in "${services[@]}"; do
        kubectl rollout undo deployment/$service -n $NAMESPACE
        kubectl rollout status deployment/$service -n $NAMESPACE --timeout=300s
    done
    
    log_success "Rollback completed"
}

# Main deployment function
deploy() {
    log_info "Starting deployment to $ENVIRONMENT environment..."
    
    validate_environment
    deploy_database
    deploy_applications
    deploy_monitoring
    deploy_security
    deploy_network_policies
    deploy_autoscaling
    deploy_backup
    health_check
    
    log_success "Deployment to $ENVIRONMENT completed successfully!"
}

# Parse command line arguments
case "$1" in
    "deploy")
        deploy
        ;;
    "rollback")
        rollback
        ;;
    "health-check")
        health_check
        ;;
    "validate")
        validate_environment
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health-check|validate}"
        echo "Environment variables:"
        echo "  ENVIRONMENT: dev|staging|production (default: staging)"
        echo "  VERSION: image version (default: latest)"
        exit 1
        ;;
esac 