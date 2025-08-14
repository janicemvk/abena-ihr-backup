# Abena IHR Module Deployment Guide

This guide explains how to deploy each Abena IHR module separately and connect them through the central API gateway.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │  Module Registry│    │  Auth Service   │
│   (Nginx)       │    │  (Port 3003)    │    │  (Port 3001)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Background      │    │ Abena IHR       │    │ Business Rules  │
│ Modules         │    │ (Port 4002)     │    │ (Port 4003)     │
│ (Port 4001)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Telemedicine    │    │ eCdome          │    │ Biomarker       │
│ (Port 4004)     │    │ Intelligence    │    │ Integration     │
│                 │    │ (Port 4005)     │    │ (Port 4006)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Provider        │    │ Unified         │    │ Shared SDK      │
│ Workflow        │    │ Integration     │    │ (Port 3002)     │
│ (Port 4007)     │    │ (Port 4008)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Deployment Steps

### Step 1: Deploy Core Services

#### 1.1 Authentication Service
```bash
# Navigate to auth service directory
cd auth-service

# Create Docker image
docker build -t abena/auth-service:latest .

# Run container
docker run -d \
  --name auth-service \
  --network abena-network \
  -p 3001:3001 \
  -e JWT_SECRET=your-secret-key \
  -e DATABASE_URL=postgresql://user:pass@db:5432/abena_auth \
  abena/auth-service:latest
```

#### 1.2 Shared SDK Service
```bash
# Navigate to SDK directory
cd abena_unified_integration/Abena Shared SDK -universal Service Client/shared-libraries/abena-sdk

# Create Docker image
docker build -t abena/shared-sdk:latest .

# Run container
docker run -d \
  --name sdk-service \
  --network abena-network \
  -p 3002:3002 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  -e DATA_SERVICE_URL=http://data-service:8001 \
  abena/shared-sdk:latest
```

#### 1.3 Module Registry
```bash
# Navigate to API gateway directory
cd api_gateway

# Create Docker image
docker build -t abena/module-registry:latest .

# Run container
docker run -d \
  --name module-registry \
  --network abena-network \
  -p 3003:3003 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  abena/module-registry:latest
```

### Step 2: Deploy Individual Modules

#### 2.1 12 Core Background Modules
```bash
# Navigate to background modules directory
cd "12 Core Background Modules"

# Create Docker image
docker build -t abena/background-modules:latest .

# Run container
docker run -d \
  --name background-modules \
  --network abena-network \
  -p 4001:4001 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  -e SDK_SERVICE_URL=http://sdk-service:3002 \
  -e MODULE_REGISTRY_URL=http://module-registry:3003 \
  abena/background-modules:latest
```

#### 2.2 Abena IHR Main System
```bash
# Navigate to IHR directory
cd abena_ihr

# Create Docker image
docker build -t abena/abena-ihr:latest .

# Run container
docker run -d \
  --name abena-ihr \
  --network abena-network \
  -p 4002:4002 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  -e SDK_SERVICE_URL=http://sdk-service:3002 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/abena_ihr \
  abena/abena-ihr:latest
```

#### 2.3 Business Rule Engine
```bash
# Navigate to business rules directory
cd business_rule_engine/Business Rule Engine

# Create Docker image
docker build -t abena/business-rules:latest .

# Run container
docker run -d \
  --name business-rules \
  --network abena-network \
  -p 4003:4003 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  -e SDK_SERVICE_URL=http://sdk-service:3002 \
  abena/business-rules:latest
```

#### 2.4 Telemedicine Platform
```bash
# Navigate to telemedicine directory
cd "Telemedicine platform"

# Create Docker image
docker build -t abena/telemedicine:latest .

# Run container
docker run -d \
  --name telemedicine \
  --network abena-network \
  -p 4004:4004 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  -e SDK_SERVICE_URL=http://sdk-service:3002 \
  abena/telemedicine:latest
```

#### 2.5 eCdome Intelligence System
```bash
# Navigate to eCdome directory
cd abena_ecdome_intelligence_sys

# Create Docker image
docker build -t abena/ecdome-intelligence:latest .

# Run container
docker run -d \
  --name ecdome-intelligence \
  --network abena-network \
  -p 4005:4005 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  -e SDK_SERVICE_URL=http://sdk-service:3002 \
  abena/ecdome-intelligence:latest
```

#### 2.6 Biomarker Integration
```bash
# Navigate to biomarker directory
cd abena_biomaker_integration

# Create Docker image
docker build -t abena/biomarker-integration:latest .

# Run container
docker run -d \
  --name biomarker-integration \
  --network abena-network \
  -p 4006:4006 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  -e SDK_SERVICE_URL=http://sdk-service:3002 \
  abena/biomarker-integration:latest
```

#### 2.7 Provider Workflow Integration
```bash
# Navigate to provider workflow directory
cd provider_workflow_integrations

# Create Docker image
docker build -t abena/provider-workflow:latest .

# Run container
docker run -d \
  --name provider-workflow \
  --network abena-network \
  -p 4007:4007 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  -e SDK_SERVICE_URL=http://sdk-service:3002 \
  abena/provider-workflow:latest
```

#### 2.8 Unified Integration Layer
```bash
# Navigate to unified integration directory
cd abena_unified_integration

# Create Docker image
docker build -t abena/unified-integration:latest .

# Run container
docker run -d \
  --name unified-integration \
  --network abena-network \
  -p 4008:4008 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  -e SDK_SERVICE_URL=http://sdk-service:3002 \
  -e MODULE_REGISTRY_URL=http://module-registry:3003 \
  abena/unified-integration:latest
```

### Step 3: Deploy API Gateway

```bash
# Navigate to API gateway directory
cd api_gateway

# Create Docker image
docker build -t abena/api-gateway:latest .

# Run container
docker run -d \
  --name api-gateway \
  --network abena-network \
  -p 80:80 \
  -p 443:443 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v $(pwd)/ssl:/etc/nginx/ssl:ro \
  abena/api-gateway:latest
```

## 🔧 Module Configuration

### Environment Variables

Each module should use these standard environment variables:

```bash
# Core Services
AUTH_SERVICE_URL=http://auth-service:3001
SDK_SERVICE_URL=http://sdk-service:3002
MODULE_REGISTRY_URL=http://module-registry:3003

# Database
DATABASE_URL=postgresql://user:pass@db:5432/module_name

# Security
JWT_SECRET=your-secret-key
API_KEY=your-api-key

# Logging
LOG_LEVEL=info
LOG_FORMAT=json

# Module Specific
MODULE_ID=module-name
MODULE_PORT=4001
```

### Health Check Implementation

Each module must implement a health check endpoint:

```javascript
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        module: process.env.MODULE_ID,
        version: process.env.MODULE_VERSION || '1.0.0',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});
```

### Module Registration

Each module should register itself with the module registry on startup:

```javascript
const registerModule = async () => {
    try {
        const response = await fetch(`${process.env.MODULE_REGISTRY_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.API_KEY}`
            },
            body: JSON.stringify({
                moduleId: process.env.MODULE_ID,
                name: 'Module Name',
                version: process.env.MODULE_VERSION || '1.0.0',
                endpoints: {
                    baseUrl: `http://${process.env.MODULE_ID}:${process.env.MODULE_PORT}`,
                    healthCheck: `http://${process.env.MODULE_ID}:${process.env.MODULE_PORT}/health`,
                    api: `http://${process.env.MODULE_ID}:${process.env.MODULE_PORT}/api/v1`
                },
                metadata: {
                    description: 'Module description',
                    category: 'module-category',
                    dependencies: ['sdk-service']
                }
            })
        });

        if (response.ok) {
            console.log('Module registered successfully');
        }
    } catch (error) {
        console.error('Failed to register module:', error);
    }
};

// Register on startup
registerModule();
```

## 📊 Monitoring & Health Checks

### Health Check Script

Create a health check script to monitor all modules:

```bash
#!/bin/bash

MODULES=(
    "auth-service:3001"
    "sdk-service:3002"
    "module-registry:3003"
    "background-modules:4001"
    "abena-ihr:4002"
    "business-rules:4003"
    "telemedicine:4004"
    "ecdome-intelligence:4005"
    "biomarker-integration:4006"
    "provider-workflow:4007"
    "unified-integration:4008"
)

for module in "${MODULES[@]}"; do
    IFS=':' read -r name port <<< "$module"
    
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name is down"
    fi
done
```

### Docker Compose for Development

Create a `docker-compose.dev.yml` for local development:

```yaml
version: '3.8'

services:
  api-gateway:
    build: ./api_gateway
    ports:
      - "80:80"
    depends_on:
      - auth-service
      - sdk-service
      - module-registry
    networks:
      - abena-network

  auth-service:
    build: ./auth-service
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  sdk-service:
    build: ./abena_unified_integration/Abena Shared SDK -universal Service Client/shared-libraries/abena-sdk
    ports:
      - "3002:3002"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  module-registry:
    build: ./api_gateway
    ports:
      - "3003:3003"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  background-modules:
    build: ./12 Core Background Modules
    ports:
      - "4001:4001"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  abena-ihr:
    build: ./abena_ihr
    ports:
      - "4002:4002"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  business-rules:
    build: ./business_rule_engine/Business Rule Engine
    ports:
      - "4003:4003"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  telemedicine:
    build: ./Telemedicine platform
    ports:
      - "4004:4004"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  ecdome-intelligence:
    build: ./abena_ecdome_intelligence_sys
    ports:
      - "4005:4005"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  biomarker-integration:
    build: ./abena_biomaker_integration
    ports:
      - "4006:4006"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  provider-workflow:
    build: ./provider_workflow_integrations
    ports:
      - "4007:4007"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

  unified-integration:
    build: ./abena_unified_integration
    ports:
      - "4008:4008"
    environment:
      - NODE_ENV=development
    networks:
      - abena-network

networks:
  abena-network:
    driver: bridge
```

## 🚀 Production Deployment

### Kubernetes Deployment

For production, use Kubernetes:

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: abena-api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: abena-api-gateway
  template:
    metadata:
      labels:
        app: abena-api-gateway
    spec:
      containers:
      - name: api-gateway
        image: abena/api-gateway:latest
        ports:
        - containerPort: 80
        - containerPort: 443
        env:
        - name: AUTH_SERVICE_URL
          value: "http://auth-service:3001"
        - name: SDK_SERVICE_URL
          value: "http://sdk-service:3002"
```

### Load Balancer

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: abena-api-gateway-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: abena-api-gateway
```

## 🔍 Troubleshooting

### Common Issues

1. **Module not registering**: Check MODULE_REGISTRY_URL and API_KEY
2. **Authentication failures**: Verify AUTH_SERVICE_URL and JWT_SECRET
3. **Network connectivity**: Ensure all containers are on the same network
4. **Port conflicts**: Verify port assignments in docker-compose files

### Debug Commands

```bash
# Check container logs
docker logs <container-name>

# Check network connectivity
docker exec <container-name> ping <other-container>

# Check health endpoints
curl http://localhost:<port>/health

# Check module registry
curl http://localhost:3003/modules
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale individual modules
docker-compose up -d --scale background-modules=3
docker-compose up -d --scale abena-ihr=2
docker-compose up -d --scale telemedicine=2
```

### Load Balancing

The nginx configuration automatically load balances requests across multiple instances of each module.

## 🔐 Security Considerations

1. **Use HTTPS** in production
2. **Implement rate limiting** per module
3. **Use secrets management** for sensitive data
4. **Regular security updates** for all containers
5. **Network segmentation** for sensitive modules 