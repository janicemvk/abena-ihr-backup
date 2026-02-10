# Abena IHR Blockchain Service

A comprehensive blockchain service for the Abena IHR microservices architecture, providing immutable health record storage, consent management, and data integrity verification using Hyperledger Fabric.

## Features

### 🔗 Blockchain Integration
- **Hyperledger Fabric**: Enterprise-grade blockchain platform for health records
- **Immutable Storage**: Tamper-proof health record storage with cryptographic verification
- **Smart Contracts**: Automated consent and access control enforcement
- **Data Integrity**: Cryptographic hashing and blockchain verification

### 📋 Health Record Management
- **CRUD Operations**: Create, read, update, and delete health records
- **Version Control**: Track record versions with previous hash linking
- **Access Logging**: Comprehensive audit trail for all record access
- **Consent Integration**: Automatic consent verification for data access

### 🔐 Security & Privacy
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Granular permissions based on user roles
- **Consent Management**: Patient consent tracking and enforcement
- **Audit Trail**: Complete audit logging for compliance

### 📊 Analytics & Monitoring
- **Usage Analytics**: Track service usage and performance metrics
- **Compliance Reporting**: Built-in reports for regulatory requirements
- **Health Monitoring**: Service health checks and status monitoring
- **Blockchain Verification**: Real-time data integrity verification

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Blockchain Service                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Health    │  │   Consent   │  │   Access    │        │
│  │   Records   │  │ Management  │  │   Control   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Hyperledger │  │   MongoDB   │  │    Redis    │        │
│  │   Fabric    │  │   Storage   │  │    Cache    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Go 1.21+ (for local development)
- MongoDB 7.0+
- Redis 7.0+
- Hyperledger Fabric 2.5+ (optional for development)

### Environment Setup

1. **Clone the repository**
```bash
cd abena-ihr-microservices/foundational-services/blockchain-service
```

2. **Set environment variables**
```bash
# Create .env file
cp .env.example .env

# Configure environment variables
export PORT=8003
export MONGO_URL=mongodb://localhost:27017
export REDIS_URL=redis://localhost:6379
export AUTH_SERVICE_URL=http://localhost:3001
```

3. **Start the service**
```bash
# Using Docker Compose
docker-compose up -d

# Or run locally
go mod download
go run main.go
```

### Database Setup

The service will automatically create the database schema on first run. For manual setup:

```bash
# Connect to MongoDB
mongo mongodb://localhost:27017/abena_ihr

# Run initialization script
load("init-mongo.js")
```

## API Endpoints

### Health Check
```http
GET /health
```

### Health Records

#### Create Health Record
```http
POST /records
Content-Type: application/json
Authorization: Bearer <token>

{
  "patient_id": "PAT001",
  "provider_id": "PROV001",
  "record_type": "vitals",
  "data_hash": "sha256_hash_of_data",
  "consent_hash": "sha256_hash_of_consent",
  "metadata": {
    "source": "hospital_system",
    "priority": "normal"
  }
}
```

#### Get Health Record
```http
GET /records/{record_id}
Authorization: Bearer <token>
```

#### Update Health Record
```http
PUT /records/{record_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "data_hash": "new_sha256_hash",
  "consent_hash": "updated_consent_hash",
  "metadata": {
    "updated_by": "provider_id",
    "reason": "correction"
  }
}
```

#### Access Health Record
```http
POST /records/{record_id}/access
Content-Type: application/json
Authorization: Bearer <token>

{
  "purpose": "clinical_care",
  "data_fields": ["vitals", "labs"],
  "emergency": false,
  "consent_token": "optional_consent_token"
}
```

### Patient Records
```http
GET /patients/{patient_id}/records
GET /patients/{patient_id}/audit
```

### Consent Management

#### Create Consent
```http
POST /consent
Content-Type: application/json
Authorization: Bearer <token>

{
  "patient_id": "PAT001",
  "provider_id": "PROV001",
  "purpose": "clinical_care",
  "data_types": ["vitals", "labs", "medications"],
  "granted": true,
  "expires_at": "2024-12-31T23:59:59Z",
  "conditions": ["emergency_access_allowed"]
}
```

#### Get Consent
```http
GET /consent/{patient_id}/{provider_id}
```

### Blockchain Operations

#### Verify Transaction
```http
GET /blockchain/verify/{tx_id}
```

#### Get Blockchain Audit
```http
GET /blockchain/audit/{record_id}
```

#### Submit Consensus Vote
```http
POST /blockchain/consensus
Content-Type: application/json

{
  "node_id": "node_001",
  "tx_id": "transaction_id",
  "vote": true,
  "reasoning": "Valid transaction"
}
```

### Analytics
```http
GET /analytics/usage
GET /analytics/compliance
```

## Data Models

### Health Record
```go
type HealthRecord struct {
    ID                string                 `json:"id"`
    PatientID         string                 `json:"patient_id"`
    ProviderID        string                 `json:"provider_id"`
    RecordType        string                 `json:"record_type"`
    DataHash          string                 `json:"data_hash"`
    Timestamp         time.Time              `json:"timestamp"`
    BlockchainTxID    string                 `json:"blockchain_tx_id"`
    ConsentHash       string                 `json:"consent_hash"`
    AccessLog         []AccessLogEntry       `json:"access_log"`
    Metadata          map[string]interface{} `json:"metadata"`
    Version           int                    `json:"version"`
    PreviousHash      string                 `json:"previous_hash"`
    IsDeleted         bool                   `json:"is_deleted"`
    CreatedAt         time.Time              `json:"created_at"`
    UpdatedAt         time.Time              `json:"updated_at"`
}
```

### Access Log Entry
```go
type AccessLogEntry struct {
    UserID         string                 `json:"user_id"`
    Action         string                 `json:"action"`
    Timestamp      time.Time              `json:"timestamp"`
    IPAddress      string                 `json:"ip_address"`
    ConsentGiven   bool                   `json:"consent_given"`
    Purpose        string                 `json:"purpose"`
    DataAccessed   []string               `json:"data_accessed"`
    AdditionalData map[string]interface{} `json:"additional_data"`
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8003` | Service port |
| `MONGO_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `AUTH_SERVICE_URL` | `http://localhost:3001` | Authentication service URL |
| `FABRIC_CONFIG_PATH` | `./config/connection.yaml` | Hyperledger Fabric config path |
| `CHANNEL_NAME` | `healthchannel` | Fabric channel name |
| `CHAINCODE_NAME` | `healthrecords` | Fabric chaincode name |
| `ORGANIZATION` | `Org1MSP` | Fabric organization |
| `USER_NAME` | `User1` | Fabric user name |

### Database Collections

- **health_records**: Main health record storage
- **access_audit**: Access audit trail
- **consents**: Patient consent records
- **blockchain_transactions**: Blockchain transaction records
- **consensus_votes**: Consensus voting records
- **patient_provider_relationships**: Patient-provider relationships
- **data_integrity_checks**: Data integrity verification records
- **analytics**: Analytics and metrics data

## Development

### Local Development Setup

1. **Install dependencies**
```bash
go mod download
```

2. **Set up database**
```bash
# Start MongoDB and Redis
docker-compose up mongo redis -d

# Run initialization script
mongo mongodb://localhost:27017/abena_ihr init-mongo.js
```

3. **Run tests**
```bash
go test ./...
```

4. **Code formatting**
```bash
go fmt ./...
go vet ./...
```

### Testing

```bash
# Run all tests
go test

# Run with coverage
go test -cover

# Run specific test categories
go test -v ./handlers
go test -v ./models
```

## Production Deployment

### Security Considerations

1. **Authentication**
   - Use proper JWT secret keys
   - Implement token rotation
   - Enable HTTPS for all communications

2. **Database Security**
   - Enable MongoDB authentication
   - Use connection pooling
   - Implement proper backup encryption

3. **Blockchain Security**
   - Use proper Fabric certificates
   - Enable TLS for all Fabric communications
   - Implement proper key management

4. **Network Security**
   - Use proper firewall rules
   - Implement VPN for administrative access
   - Monitor network traffic

### Docker Deployment

```bash
# Build production image
docker build -t abena-blockchain:latest .

# Run with production settings
docker run -d \
  --name blockchain-service \
  -p 8003:8003 \
  -e MONGO_URL=$MONGO_URL \
  -e REDIS_URL=$REDIS_URL \
  -e AUTH_SERVICE_URL=$AUTH_SERVICE_URL \
  abena-blockchain:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blockchain-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: blockchain-service
  template:
    metadata:
      labels:
        app: blockchain-service
    spec:
      containers:
      - name: blockchain-service
        image: abena-blockchain:latest
        ports:
        - containerPort: 8003
        env:
        - name: MONGO_URL
          valueFrom:
            secretKeyRef:
              name: blockchain-secrets
              key: mongo-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: blockchain-secrets
              key: redis-url
```

## Monitoring & Observability

### Health Checks
- **Service Health**: `/health` endpoint
- **Database Connectivity**: Automatic connection monitoring
- **Redis Connectivity**: Cache availability monitoring
- **Fabric Connection**: Blockchain network connectivity

### Metrics
- Health record operations per minute
- Blockchain transaction success rates
- Access audit log entries
- Consent verification success rates
- Average response times

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with stack traces
- Performance metrics

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check MongoDB is running
   - Verify connection string format
   - Ensure database exists and collections are created

2. **Blockchain Connection Errors**
   - Verify Fabric network is running
   - Check certificate paths
   - Ensure proper network configuration

3. **Authentication Errors**
   - Verify JWT token format
   - Check auth service connectivity
   - Ensure proper token validation

4. **Performance Issues**
   - Monitor database connection pool
   - Check Redis cache hit rates
   - Review query performance

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
go run main.go
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Review the documentation and troubleshooting guide 