# Abena IHR Infrastructure and Deployment Configuration

This repository contains the complete infrastructure and deployment configuration for the Abena Integrated Health Record (IHR) platform.

## 🏗️ Architecture Overview

The Abena IHR platform is designed as a scalable, secure, and compliant healthcare application with the following components:

- **Application Layer**: Node.js/Express API with TypeScript
- **Database**: PostgreSQL 15 with connection pooling
- **Caching**: Redis 7 for session management and caching
- **Load Balancer**: Nginx with SSL termination and rate limiting
- **Container Orchestration**: Kubernetes with auto-scaling
- **Infrastructure**: AWS EKS with Terraform IaC
- **Monitoring**: Prometheus, Grafana, and comprehensive logging
- **Security**: RBAC, network policies, and security headers

## 📁 Directory Structure

```
├── .env.example                 # Environment configuration template
├── docker-compose.production.yml # Docker Compose for production
├── nginx.conf                   # Nginx configuration
├── k8s/                        # Kubernetes manifests
│   ├── production/             # Production deployments
│   ├── monitoring/             # Monitoring stack
│   ├── security/               # Security policies
│   └── backup/                 # Backup configurations
├── terraform/                  # Infrastructure as Code
├── scripts/                    # Deployment and maintenance scripts
├── k6/                         # Performance testing
└── src/                        # Application source code
    └── health/                 # Health check utilities
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- kubectl (for Kubernetes deployment)
- Terraform (for infrastructure provisioning)
- AWS CLI configured
- Node.js 18+ (for local development)

### Local Development

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd infrastructure-and-deployment-configuration
   cp .env.example .env
   # Edit .env with your local configuration
   ```

2. **Start with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

3. **Access the application:**
   - API: http://localhost:3000
   - Health Check: http://localhost:3000/health

### Production Deployment

1. **Provision Infrastructure:**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

2. **Deploy to Kubernetes:**
   ```bash
   kubectl apply -f k8s/production/
   kubectl apply -f k8s/monitoring/
   kubectl apply -f k8s/security/
   ```

3. **Configure DNS and SSL:**
   - Point your domain to the load balancer
   - Configure SSL certificates in nginx

## 🔧 Configuration

### Environment Variables

Key configuration areas:
- **Database**: PostgreSQL connection and pooling settings
- **Security**: JWT secrets, encryption keys, and session management
- **External Services**: AWS S3, Stripe, Twilio, email providers
- **Healthcare Integration**: FHIR, HL7, Epic, Cerner APIs
- **Monitoring**: Sentry, DataDog, New Relic integration

### Security Features

- **Network Policies**: Pod-to-pod communication restrictions
- **RBAC**: Role-based access control for Kubernetes resources
- **Pod Security Policies**: Non-root containers, privilege restrictions
- **SSL/TLS**: End-to-end encryption with modern cipher suites
- **Rate Limiting**: API and authentication endpoint protection

## 📊 Monitoring and Observability

### Metrics Collected

- **Application Metrics**: Response times, error rates, throughput
- **Infrastructure Metrics**: CPU, memory, disk usage
- **Database Metrics**: Connection pools, query performance
- **Business Metrics**: User activity, feature usage

### Alerting

- **High Error Rates**: >5% HTTP 5xx responses
- **High Latency**: >500ms 95th percentile response time
- **Resource Usage**: >80% CPU or memory utilization
- **Database Issues**: Connection failures, slow queries

## 🔄 Backup and Disaster Recovery

### Automated Backups

- **Database**: Daily PostgreSQL dumps with 30-day retention
- **Redis**: Automated snapshots with point-in-time recovery
- **Application Data**: S3-based file storage with versioning
- **Configuration**: Git-based version control with rollback capability

### Recovery Procedures

1. **Database Recovery**: Point-in-time recovery from S3 backups
2. **Application Rollback**: Kubernetes deployment rollback
3. **Infrastructure Recovery**: Terraform state-based recovery
4. **Data Validation**: Automated integrity checks post-recovery

## 🧪 Testing

### Performance Testing

```bash
# Run load tests with k6
k6 run k6/load-test.js
```

### Security Testing

- **Container Scanning**: Automated vulnerability scanning
- **Network Testing**: Penetration testing procedures
- **Compliance**: HIPAA, SOC 2, and healthcare compliance checks

## 📈 Scaling

### Horizontal Scaling

- **Application**: Kubernetes HPA with CPU/memory metrics
- **Database**: Read replicas for query distribution
- **Caching**: Redis cluster for high availability

### Vertical Scaling

- **Resource Limits**: Configurable CPU and memory limits
- **Instance Types**: Auto-scaling based on workload
- **Storage**: Dynamic volume provisioning

## 🔒 Security Compliance

### Healthcare Standards

- **HIPAA Compliance**: Data encryption, access controls, audit logging
- **SOC 2**: Security controls and monitoring
- **HITECH**: Electronic health record standards
- **FHIR**: Healthcare data interoperability

### Security Measures

- **Data Encryption**: At rest and in transit
- **Access Controls**: Multi-factor authentication
- **Audit Logging**: Comprehensive activity tracking
- **Vulnerability Management**: Regular security updates

## 🛠️ Maintenance

### Regular Tasks

- **Security Updates**: Monthly patch management
- **Backup Verification**: Weekly backup integrity checks
- **Performance Monitoring**: Continuous optimization
- **Compliance Audits**: Quarterly security assessments

### Troubleshooting

- **Health Checks**: Automated monitoring and alerting
- **Log Analysis**: Centralized logging with search capabilities
- **Metrics Dashboard**: Real-time system performance
- **Incident Response**: Documented procedures and escalation

## 📞 Support

For issues and questions:
- **Infrastructure**: Check Terraform state and Kubernetes logs
- **Application**: Review application logs and metrics
- **Security**: Contact security team for compliance issues
- **Performance**: Use monitoring dashboards and load testing

## 📄 License

This project is proprietary and confidential. All rights reserved by Abena Health.

---

**Last Updated**: 2024
**Version**: 1.0.0
**Maintainer**: Abena Health DevOps Team 