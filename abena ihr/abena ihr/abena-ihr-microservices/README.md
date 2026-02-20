# Abena IHR Microservices Architecture

A comprehensive, enterprise-grade healthcare information system built with microservices architecture, designed to provide holistic patient care through traditional and modern medical approaches.

## 🏗️ Architecture Overview

The Abena IHR system is organized into distinct layers, each serving specific purposes:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  Patient Portal • Provider Dashboard • Mobile App • Admin   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                         │
│  API Gateway • Message Broker • Service Mesh • Event Stream │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 APPLICATION SERVICES LAYER                  │
│  Analytics • Clinical Decision Support • Workflows • Modules│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  FOUNDATIONAL SERVICES                      │
│  Auth • Data • Privacy • Blockchain • Unified Database      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                      │
│  Monitoring • Logging • Security • CI/CD • Kubernetes       │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### 🧠 Intelligence Layer
- **Analytics Engine**: Predictive analytics, population health, real-time insights
- **Clinical Decision Support**: Evidence-based recommendations, drug interactions, risk stratification
- **Science Intelligence**: AI/ML research algorithms, medical NLP, clinical research

### 🏥 Application Layer
- **Provider Workflow**: Task management, notifications, workflow automation
- **Telemedicine**: Video consultations, scheduling, consultation management
- **Patient Engagement**: Patient portal, appointment booking, health tracking

### 🌿 Module Layer
- **Traditional Medicine**: TCM, Ayurveda, Functional Medicine
- **Lab Results**: Processing, interpretation, trend analysis
- **Nutrition**: Dietary analysis, meal planning, nutrition database
- **125+ Specialized Modules**: Comprehensive healthcare coverage

### 🔒 Security & Compliance
- **HIPAA Compliance**: Healthcare data protection standards
- **GDPR Compliance**: European data protection regulations
- **Blockchain Audit**: Immutable audit trails
- **Data Encryption**: End-to-end encryption
- **Access Control**: Role-based and attribute-based access control

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Kubernetes cluster (for production)
- Python 3.8+, Node.js 16+, Go 1.19+
- PostgreSQL 13+, Redis 6+, MongoDB 5+

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd abena-ihr-microservices
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start foundational services**
```bash
docker-compose up -d
```

4. **Start application services**
```bash
# Start analytics engine
cd application-services/analytics-engine-service
docker-compose up -d

# Start clinical decision support
cd ../clinical-decision-support-service
docker-compose up -d
```

5. **Start presentation layer**
```bash
cd ../../presentation-layer/patient-portal
npm install && npm run dev
```

## 📁 Directory Structure

```
abena-ihr-microservices/
├── foundational-services/          # Core infrastructure services
│   ├── unified-data-service/       # Master database & schema
│   ├── auth-service/               # Authentication & authorization
│   ├── data-ingestion-service/     # Real-time data streaming
│   ├── privacy-security-service/   # Encryption & anonymization
│   └── blockchain-service/         # Immutable audit trail
│
├── shared-libraries/               # SDK layer for all services
│   ├── abena-sdk-js/              # JavaScript/TypeScript SDK
│   ├── abena-sdk-python/          # Python SDK
│   └── abena-sdk-go/              # Go SDK
│
├── application-services/           # Business logic services
│   ├── analytics-engine-service/   # Predictive analytics
│   ├── clinical-decision-support-service/ # Clinical recommendations
│   ├── provider-workflow-service/  # Provider workflows
│   ├── telemedicine-service/       # Video consultations
│   ├── patient-engagement-service/ # Patient portal backend
│   └── [125+ module services]/     # Specialized healthcare modules
│
├── presentation-layer/             # User interfaces
│   ├── patient-portal/            # React/Next.js patient app
│   ├── provider-dashboard/        # React/Next.js provider app
│   ├── mobile-app/                # React Native mobile app
│   ├── admin-console/             # System administration
│   └── telemedicine-interface/    # Video consultation UI
│
├── integration-layer/              # API Gateway, messaging
│   ├── api-gateway/               # Kong, NGINX, or Istio
│   ├── message-broker/            # Kafka configuration
│   ├── service-mesh/              # Istio service mesh
│   └── event-streaming/           # Event-driven architecture
│
├── infrastructure/                 # DevOps, monitoring, security
│   ├── monitoring/                # Prometheus, Grafana, Jaeger
│   ├── logging/                   # ELK Stack
│   ├── security/                  # Vault, cert-manager, policies
│   ├── ci-cd/                     # Jenkins, GitLab CI, GitHub Actions
│   └── kubernetes/                # K8s manifests
│
├── docker-compose.yml             # Local development setup
├── docker-compose.prod.yml        # Production setup
├── kubernetes-manifests/          # Production K8s deployment
└── scripts/                       # Deployment and utility scripts
```

## 🔄 Service Communication Flow

```
Frontend Applications (Presentation Layer)
    ↓ HTTP/REST APIs
API Gateway (Integration Layer)
    ↓ Load Balancing & Routing
Application Services (Business Logic)
    ↓ Uses SDK to communicate with
Foundational Services (Infrastructure)
    ↓ Stores data in
Unified Database & Message Queues
```

## 🏥 Healthcare Modules

### Traditional Medicine
- **TCM Service**: Traditional Chinese Medicine diagnostics, herb interactions
- **Ayurveda Service**: Dosha analysis, Ayurvedic treatments
- **Functional Medicine Service**: Root cause analysis, functional protocols

### Modern Medicine
- **Lab Results Service**: Lab processing, interpretation, trend analysis
- **Nutrition Service**: Dietary analysis, meal planning, nutrition database
- **Clinical Decision Support**: Evidence-based recommendations

### Patient Care
- **Telemedicine Service**: Video consultations, remote care
- **Patient Engagement**: Patient portal, health tracking
- **Provider Workflow**: Task management, notifications

## 🔧 Technology Stack

### Backend Services
- **Python**: FastAPI for application services
- **Node.js**: Authentication service
- **Go**: Blockchain service
- **PostgreSQL**: Primary database
- **MongoDB**: Document storage
- **Redis**: Caching and sessions

### Frontend Applications
- **React/Next.js**: Patient portal, provider dashboard
- **React Native**: Mobile application
- **TypeScript**: Type-safe development

### Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **Kafka**: Message streaming
- **Prometheus/Grafana**: Monitoring
- **ELK Stack**: Logging
- **Vault**: Secrets management

### Security & Compliance
- **JWT**: Authentication
- **OAuth2**: Authorization
- **AES-256**: Encryption
- **Blockchain**: Audit trails
- **HIPAA/GDPR**: Compliance

## 🚀 Deployment

### Local Development
```bash
# Start all services
docker-compose up -d

# Start specific service
cd application-services/analytics-engine-service
docker-compose up -d
```

### Production Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f kubernetes-manifests/

# Deploy specific service
kubectl apply -f kubernetes-manifests/analytics-engine-service/
```

### Monitoring
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **Jaeger**: http://localhost:16686

## 📊 Health Checks

### Service Health
```bash
# Check all services
./scripts/health-check.sh

# Check specific service
curl http://localhost:8000/health
```

### Database Health
```bash
# PostgreSQL
docker exec -it abena-postgres psql -U postgres -c "SELECT 1;"

# MongoDB
docker exec -it abena-mongodb mongosh --eval "db.runCommand('ping')"

# Redis
docker exec -it abena-redis redis-cli ping
```

## 🔒 Security Considerations

### Data Protection
- All data encrypted at rest and in transit
- PII data automatically anonymized
- Blockchain-based audit trails
- Role-based access control

### Compliance
- HIPAA compliance built-in
- GDPR compliance features
- Regular security audits
- Automated compliance reporting

### Access Control
- Multi-factor authentication
- Session management
- API rate limiting
- IP whitelisting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow the established architecture patterns
- Add comprehensive tests
- Update documentation
- Follow security best practices
- Ensure HIPAA/GDPR compliance

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support

For support and questions:
- Documentation: [Link to docs]
- Issues: [GitHub Issues]
- Email: support@abena-ihr.com

## 🏥 About Abena IHR

Abena IHR is a comprehensive healthcare information system designed to bridge traditional and modern medicine, providing holistic patient care through advanced technology and evidence-based practices.

---

**Built with ❤️ for better healthcare** 