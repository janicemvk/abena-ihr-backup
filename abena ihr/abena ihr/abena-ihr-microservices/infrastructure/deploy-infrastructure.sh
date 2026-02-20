#!/bin/bash

# Abena IHR Infrastructure Deployment Script
# Complete infrastructure setup for healthcare microservices

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="abena-ihr-cluster"
NAMESPACE="abena-ihr"
MONITORING_NAMESPACE="monitoring"
LOGGING_NAMESPACE="logging"
SECURITY_NAMESPACE="security"

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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed"
        exit 1
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

create_namespaces() {
    log_info "Creating namespaces..."
    
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace $MONITORING_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace $LOGGING_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace $SECURITY_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Namespaces created"
}

install_cert_manager() {
    log_info "Installing cert-manager..."
    
    # Add cert-manager repository
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    
    # Install cert-manager
    helm install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --set installCRDs=true \
        --set global.leaderElection.namespace=cert-manager \
        --wait
    
    # Wait for cert-manager to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
    
    log_success "cert-manager installed"
}

install_nginx_ingress() {
    log_info "Installing NGINX Ingress Controller..."
    
    # Add nginx-ingress repository
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    # Install nginx-ingress
    helm install nginx-ingress ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --set controller.resources.requests.cpu=100m \
        --set controller.resources.requests.memory=128Mi \
        --set controller.resources.limits.cpu=200m \
        --set controller.resources.limits.memory=256Mi \
        --wait
    
    log_success "NGINX Ingress Controller installed"
}

install_monitoring_stack() {
    log_info "Installing monitoring stack..."
    
    # Add Prometheus repository
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    # Install Prometheus
    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace $MONITORING_NAMESPACE \
        --set prometheus.prometheusSpec.retention=15d \
        --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.storageClassName=gp2 \
        --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
        --set grafana.enabled=true \
        --set grafana.adminPassword=admin123 \
        --set grafana.persistence.enabled=true \
        --set grafana.persistence.storageClassName=gp2 \
        --set grafana.persistence.size=10Gi \
        --wait
    
    # Install Jaeger
    helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
    helm repo update
    
    helm install jaeger jaegertracing/jaeger \
        --namespace $MONITORING_NAMESPACE \
        --set storage.type=elasticsearch \
        --set storage.options.es.server-urls=http://elasticsearch:9200 \
        --set storage.options.es.index-prefix=jaeger \
        --wait
    
    log_success "Monitoring stack installed"
}

install_logging_stack() {
    log_info "Installing logging stack..."
    
    # Add Elasticsearch repository
    helm repo add elastic https://helm.elastic.co
    helm repo update
    
    # Install Elasticsearch
    helm install elasticsearch elastic/elasticsearch \
        --namespace $LOGGING_NAMESPACE \
        --set replicas=3 \
        --set minimumMasterNodes=2 \
        --set resources.requests.cpu=500m \
        --set resources.requests.memory=2Gi \
        --set resources.limits.cpu=1000m \
        --set resources.limits.memory=4Gi \
        --set volumeClaimTemplate.storageClassName=gp2 \
        --set volumeClaimTemplate.resources.requests.storage=100Gi \
        --wait
    
    # Install Kibana
    helm install kibana elastic/kibana \
        --namespace $LOGGING_NAMESPACE \
        --set replicas=2 \
        --set resources.requests.cpu=250m \
        --set resources.requests.memory=1Gi \
        --set resources.limits.cpu=500m \
        --set resources.limits.memory=2Gi \
        --set volumeClaimTemplate.storageClassName=gp2 \
        --set volumeClaimTemplate.resources.requests.storage=10Gi \
        --wait
    
    # Install Logstash
    helm install logstash elastic/logstash \
        --namespace $LOGGING_NAMESPACE \
        --set replicas=2 \
        --set resources.requests.cpu=250m \
        --set resources.requests.memory=1Gi \
        --set resources.limits.cpu=500m \
        --set resources.limits.memory=2Gi \
        --wait
    
    log_success "Logging stack installed"
}

install_vault() {
    log_info "Installing Vault..."
    
    # Add HashiCorp repository
    helm repo add hashicorp https://helm.releases.hashicorp.com
    helm repo update
    
    # Install Vault
    helm install vault hashicorp/vault \
        --namespace $SECURITY_NAMESPACE \
        --set server.dev.enabled=true \
        --set server.dev.devRootToken=root-token \
        --set server.resources.requests.cpu=250m \
        --set server.resources.requests.memory=256Mi \
        --set server.resources.limits.cpu=500m \
        --set server.resources.limits.memory=512Mi \
        --wait
    
    log_success "Vault installed"
}

apply_certificates() {
    log_info "Applying certificates..."
    
    # Apply cluster issuers
    kubectl apply -f security/cert-manager/cluster-issuer.yaml
    
    # Wait for certificates to be ready
    sleep 30
    
    log_success "Certificates applied"
}

apply_security_policies() {
    log_info "Applying security policies..."
    
    kubectl apply -f security/security-policies/pod-security-policies.yaml
    
    log_success "Security policies applied"
}

apply_monitoring_config() {
    log_info "Applying monitoring configuration..."
    
    # Apply Prometheus configuration
    kubectl create configmap prometheus-config -n $MONITORING_NAMESPACE \
        --from-file=monitoring/prometheus/prometheus.yml \
        --from-file=monitoring/prometheus/alert_rules.yml \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Grafana dashboards
    kubectl create configmap grafana-dashboards -n $MONITORING_NAMESPACE \
        --from-file=monitoring/grafana/dashboards/ \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Jaeger configuration
    kubectl apply -f monitoring/jaeger/jaeger-config.yml
    
    log_success "Monitoring configuration applied"
}

apply_logging_config() {
    log_info "Applying logging configuration..."
    
    # Apply Elasticsearch configuration
    kubectl create configmap elasticsearch-config -n $LOGGING_NAMESPACE \
        --from-file=logging/elasticsearch/elasticsearch.yml \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Logstash configuration
    kubectl create configmap logstash-config -n $LOGGING_NAMESPACE \
        --from-file=logging/logstash/logstash.conf \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Kibana configuration
    kubectl create configmap kibana-config -n $LOGGING_NAMESPACE \
        --from-file=logging/kibana/kibana.yml \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Logging configuration applied"
}

apply_vault_config() {
    log_info "Applying Vault configuration..."
    
    kubectl create configmap vault-config -n $SECURITY_NAMESPACE \
        --from-file=security/vault/vault-config.hcl \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Vault configuration applied"
}

apply_kubernetes_resources() {
    log_info "Applying Kubernetes resources..."
    
    # Apply services
    kubectl apply -f kubernetes/services/
    
    # Apply ingress
    kubectl apply -f kubernetes/ingress/
    
    # Apply configmaps
    kubectl apply -f kubernetes/configmaps/
    
    # Apply deployments (if they exist)
    if [ -d "kubernetes/deployments" ]; then
        kubectl apply -f kubernetes/deployments/
    fi
    
    log_success "Kubernetes resources applied"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check namespaces
    kubectl get namespaces | grep -E "($NAMESPACE|$MONITORING_NAMESPACE|$LOGGING_NAMESPACE|$SECURITY_NAMESPACE)"
    
    # Check pods
    kubectl get pods -n $MONITORING_NAMESPACE
    kubectl get pods -n $LOGGING_NAMESPACE
    kubectl get pods -n $SECURITY_NAMESPACE
    
    # Check services
    kubectl get services -n $NAMESPACE
    kubectl get ingress -n $NAMESPACE
    
    log_success "Deployment verification completed"
}

setup_backup() {
    log_info "Setting up backup configuration..."
    
    # Create backup namespace
    kubectl create namespace backup --dry-run=client -o yaml | kubectl apply -f -
    
    # Install Velero for backup
    helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
    helm repo update
    
    helm install velero vmware-tanzu/velero \
        --namespace backup \
        --set configuration.provider=aws \
        --set configuration.backupStorageLocation.name=default \
        --set configuration.backupStorageLocation.bucket=abena-ihr-backups \
        --set configuration.volumeSnapshotLocation.name=default \
        --set configuration.volumeSnapshotLocation.config.region=us-east-1 \
        --set credentials.useSecret=false \
        --wait
    
    log_success "Backup configuration completed"
}

main() {
    log_info "Starting Abena IHR infrastructure deployment..."
    
    check_prerequisites
    create_namespaces
    install_cert_manager
    install_nginx_ingress
    install_monitoring_stack
    install_logging_stack
    install_vault
    apply_certificates
    apply_security_policies
    apply_monitoring_config
    apply_logging_config
    apply_vault_config
    apply_kubernetes_resources
    setup_backup
    verify_deployment
    
    log_success "Infrastructure deployment completed successfully!"
    
    echo ""
    echo "Access URLs:"
    echo "- API Gateway: https://api.abena-ihr.com"
    echo "- Monitoring: https://monitoring.abena-ihr.com"
    echo "- Grafana: https://monitoring.abena-ihr.com/grafana (admin/admin123)"
    echo "- Kibana: https://logging.abena-ihr.com"
    echo "- Vault: https://vault.abena-ihr.com"
    echo ""
    echo "Next steps:"
    echo "1. Configure DNS records to point to your ingress controller"
    echo "2. Update secrets in Vault"
    echo "3. Deploy your microservices"
    echo "4. Configure monitoring alerts"
    echo "5. Set up backup schedules"
}

# Run main function
main "$@" 