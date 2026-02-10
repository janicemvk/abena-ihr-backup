# Abena Shared SDK - Universal Service Client

## Overview

The Abena Shared SDK is a universal service client that provides a unified interface for integrating with various healthcare systems, external services, and internal APIs. It's designed to handle authentication, caching, circuit breaking, service discovery, and monitoring in a consistent manner across all service integrations.

## 🏗️ Architecture

### Core Components

1. **Universal Service Client**: Centralized client for all external service interactions
2. **Service Discovery**: Dynamic service registration and discovery
3. **Circuit Breaker**: Fault tolerance and resilience patterns
4. **Caching Layer**: Redis-based caching with TTL and eviction policies
5. **Authentication Manager**: JWT-based authentication with automatic token refresh
6. **Metrics & Monitoring**: Comprehensive observability and performance tracking
7. **Health Checks**: Liveness, readiness, and startup probes

### Service Integrations

- **Healthcare Systems**: FHIR, HL7, Epic, Cerner
- **Communication**: SMS (Twilio), Email (SendGrid)
- **Payments**: Stripe integration
- **Storage**: AWS S3 file management
- **Internal APIs**: Core IHR application services

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Docker and Docker Compose
- Kubernetes cluster (for production)
- Redis instance
- PostgreSQL database

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd infrastructure-and-deployment-configuration
   cp sdk.env.example sdk.env
   # Edit sdk.env with your configuration
   ```

2. **Start SDK service:**
   ```bash
   docker-compose -f docker-compose.production.yml up sdk-service -d
   ```

3. **Verify deployment:**
   ```bash
   curl http://localhost:3001/health
   curl http://localhost:3001/metrics
   ```

### Production Deployment

1. **Deploy to Kubernetes:**
   ```bash
   kubectl apply -f k8s/production/sdk-service.yaml
   kubectl apply -f k8s/security/sdk-network-policy.yaml
   kubectl apply -f k8s/monitoring/sdk-prometheus.yaml
   ```

2. **Run deployment script:**
   ```bash
   chmod +x scripts/deploy-sdk.sh
   ./scripts/deploy-sdk.sh v1.0.0
   ```

## 📋 Configuration

### Environment Variables

Key configuration areas:

```bash
# SDK Service Configuration
SDK_PORT=3001
SDK_ENVIRONMENT=production
SDK_VERSION=1.0.0

# Performance Settings
SDK_TIMEOUT=30000
SDK_RETRY_ATTEMPTS=3
SDK_CACHE_TTL=3600

# Circuit Breaker
SDK_CIRCUIT_BREAKER_ENABLED=true
SDK_CIRCUIT_BREAKER_FAILURE_THRESHOLD=5

# Service Discovery
SDK_DISCOVERY_TYPE=kubernetes
SDK_DISCOVERY_NAMESPACE=abena-ihr

# Authentication
SDK_AUTH_TYPE=jwt
SDK_JWT_SECRET=your-secret-key
```

### Configuration File

The SDK uses `sdk-config.yaml` for service-specific configurations:

```yaml
sdk:
  universal:
    enabled: true
    timeout: 30000
    retryAttempts: 3
    circuitBreaker:
      enabled: true
      failureThreshold: 5

services:
  fhir-server:
    url: "${FHIR_SERVER_URL}"
    timeout: 45000
    retryAttempts: 2
    auth:
      type: "bearer"
      tokenSource: "environment"
```

## 🔌 API Endpoints

### Health & Monitoring

- `GET /health` - Health check endpoint
- `GET /ready` - Readiness probe
- `GET /live` - Liveness probe
- `GET /metrics` - Prometheus metrics

### Universal Service Client

- `GET /api/services/{service}` - Service-specific endpoints
- `POST /api/services/{service}` - Service operations
- `GET /api/services/discovery` - Service discovery status

### SDK Management

- `GET /circuit-breaker/status` - Circuit breaker status
- `GET /cache/status` - Cache performance metrics
- `GET /discovery/services` - Discovered services list

## 🔧 Service Integrations

### FHIR Integration

```javascript
// Using the universal service client
const fhirClient = sdk.getService('fhir-server');
const patients = await fhirClient.get('/Patient?search=john');
```

### HL7 Integration

```javascript
const hl7Client = sdk.getService('hl7-gateway');
const message = await hl7Client.post('/message', {
  messageType: 'ADT^A01',
  patientId: '12345',
  data: { /* HL7 data */ }
});
```

### Epic Integration

```javascript
const epicClient = sdk.getService('epic-integration');
const patient = await epicClient.get('/patient/12345');
```

### Payment Processing

```javascript
const paymentClient = sdk.getService('stripe-payment');
const charge = await paymentClient.post('/charges', {
  amount: 1000,
  currency: 'USD',
  description: 'Medical service'
});
```

## 🛡️ Security Features

### Authentication

- **JWT Tokens**: Automatic token refresh and validation
- **Service-to-Service**: Mutual TLS authentication
- **API Keys**: Secure storage and rotation

### Network Security

- **Network Policies**: Pod-to-pod communication restrictions
- **TLS Encryption**: End-to-end encryption
- **Rate Limiting**: Request throttling and protection

### Data Protection

- **Encryption**: Data encryption at rest and in transit
- **Audit Logging**: Comprehensive activity tracking
- **Compliance**: HIPAA, SOC 2, and healthcare standards

## 📊 Monitoring & Observability

### Metrics Collected

- **Performance**: Response times, throughput, error rates
- **Circuit Breaker**: State changes, failure counts
- **Cache**: Hit/miss ratios, eviction rates
- **Service Discovery**: Service availability, health status
- **Resource Usage**: CPU, memory, network utilization

### Alerting Rules

```yaml
# SDK Service Health
- alert: SDKServiceDown
  expr: up{job="abena-shared-sdk"} == 0
  for: 1m
  severity: critical

# High Error Rate
- alert: SDKHighErrorRate
  expr: rate(http_requests_total{job="abena-shared-sdk", status=~"5.."}[5m]) > 0.05
  for: 2m
  severity: warning

# Circuit Breaker Open
- alert: SDKCircuitBreakerOpen
  expr: sdk_circuit_breaker_state{job="abena-shared-sdk"} == 1
  for: 1m
  severity: warning
```

### Dashboards

- **SDK Overview**: Service health, performance, and usage
- **Circuit Breaker**: State monitoring and failure analysis
- **Cache Performance**: Hit rates and eviction patterns
- **Service Discovery**: Service availability and health

## 🔄 Circuit Breaker Pattern

### States

1. **Closed**: Normal operation, requests pass through
2. **Open**: Service is failing, requests are rejected
3. **Half-Open**: Testing if service has recovered

### Configuration

```yaml
circuitBreaker:
  enabled: true
  failureThreshold: 5
  recoveryTimeout: 60000
  monitoringWindow: 60000
```

### Implementation

```javascript
// Automatic circuit breaker for all service calls
const result = await sdk.getService('external-api').get('/data');

// Manual circuit breaker control
const circuitBreaker = sdk.getCircuitBreaker('external-api');
if (circuitBreaker.isOpen()) {
  // Handle fallback logic
}
```

## 💾 Caching Strategy

### Cache Types

- **Redis**: Distributed caching with persistence
- **Memory**: Local in-memory caching
- **None**: No caching (for sensitive data)

### Configuration

```yaml
cache:
  type: "redis"
  ttl: 3600
  maxSize: 1000
  evictionPolicy: "lru"
```

### Usage

```javascript
// Automatic caching for GET requests
const data = await sdk.getService('api').get('/cached-data');

// Manual cache control
const cache = sdk.getCache();
await cache.set('key', 'value', 3600);
const value = await cache.get('key');
```

## 🔍 Service Discovery

### Discovery Methods

- **Kubernetes**: Automatic service discovery in K8s
- **Consul**: Service mesh integration
- **Static**: Manual service configuration

### Health Checks

```yaml
discovery:
  type: "kubernetes"
  namespace: "abena-ihr"
  refreshInterval: 30000
  healthCheckInterval: 10000
```

### Service Registration

```javascript
// Register a new service
await sdk.registerService('new-service', {
  url: 'https://api.newservice.com',
  timeout: 30000,
  retryAttempts: 3
});

// Discover available services
const services = await sdk.discoverServices();
```

## 🧪 Testing

### Unit Tests

```bash
npm test
npm run test:coverage
```

### Integration Tests

```bash
npm run test:integration
```

### Load Testing

```bash
# Run SDK-specific load tests
k6 run k6/sdk-load-test.js

# Run comprehensive load tests
k6 run k6/load-test.js
```

### Performance Testing

```bash
# Run performance benchmarks
npm run test:performance

# Generate performance reports
npm run test:benchmark
```

## 🚀 Deployment

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3001
CMD ["npm", "start"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: abena-shared-sdk
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: sdk-service
        image: abena-shared-sdk:latest
        ports:
        - containerPort: 3001
        env:
        - name: NODE_ENV
          value: "production"
```

### Helm Chart

```bash
# Install SDK with Helm
helm install sdk ./helm/sdk --namespace abena-ihr

# Upgrade SDK
helm upgrade sdk ./helm/sdk --namespace abena-ihr
```

## 🔧 Troubleshooting

### Common Issues

1. **Service Discovery Failures**
   ```bash
   kubectl logs -f deployment/abena-shared-sdk -n abena-ihr
   ```

2. **Circuit Breaker Issues**
   ```bash
   curl http://localhost:3001/circuit-breaker/status
   ```

3. **Cache Problems**
   ```bash
   curl http://localhost:3001/cache/status
   ```

4. **Authentication Errors**
   ```bash
   kubectl get secrets -n abena-ihr
   kubectl describe secret sdk-secrets -n abena-ihr
   ```

### Debug Mode

```bash
# Enable debug logging
export SDK_LOG_LEVEL=debug
export SDK_ENABLE_REQUEST_LOGGING=true

# Restart SDK service
kubectl rollout restart deployment/abena-shared-sdk -n abena-ihr
```

## 📚 API Reference

### SDK Client

```javascript
const sdk = new AbenaSDK({
  environment: 'production',
  timeout: 30000,
  retryAttempts: 3
});

// Get a service client
const service = sdk.getService('service-name');

// Make requests
const response = await service.get('/endpoint');
```

### Service Configuration

```javascript
const serviceConfig = {
  url: 'https://api.service.com',
  timeout: 30000,
  retryAttempts: 3,
  circuitBreaker: {
    failureThreshold: 5,
    recoveryTimeout: 60000
  },
  auth: {
    type: 'bearer',
    token: 'your-token'
  }
};
```

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

### Code Standards

- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting
- **TypeScript**: Type safety
- **Jest**: Unit testing
- **k6**: Performance testing

### Testing Guidelines

- **Unit Tests**: 90%+ coverage required
- **Integration Tests**: All service integrations
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability scanning

## 📄 License

This project is proprietary and confidential. All rights reserved by Abena Health.

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: Abena Health DevOps Team 