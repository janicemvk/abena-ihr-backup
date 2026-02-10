# Abena IHR Data Ingestion Service

A real-time health data streaming and processing service for the Abena IHR microservices architecture. This service handles ingestion of various health data formats including vital signs, lab results, medications, HL7 messages, and FHIR resources.

## Features

- **Multi-format Data Ingestion**: Support for vital signs, lab results, medications, HL7, and FHIR
- **Real-time Processing**: Asynchronous processing with Kafka message queuing
- **Duplicate Detection**: SHA-256 checksum-based duplicate prevention
- **Data Validation**: Comprehensive validation with Pydantic models
- **Authentication**: JWT token-based authentication with Auth service
- **Monitoring**: Health checks, metrics, and processing status tracking
- **Scalable Architecture**: PostgreSQL for persistence, Redis for caching, Kafka for messaging

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │───▶│  Data Ingestion │───▶│   PostgreSQL    │
│                 │    │     Service     │    │   (Raw Data)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │      Kafka      │
                       │   (Messaging)   │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │      Redis      │
                       │   (Caching)     │
                       └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+
- Redis 7+
- Apache Kafka

### Using Docker Compose

1. **Clone the repository**
   ```bash
   cd abena-ihr-microservices/foundational-services/data-ingestion-service
   ```

2. **Set environment variables**
   ```bash
   export ENCRYPTION_KEY="your-secret-encryption-key-here"
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Verify the service is running**
   ```bash
   curl http://localhost:8001/health
   ```

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up the database**
   ```bash
   # Create database
   createdb abena_ihr_data
   
   # Run schema
   psql -d abena_ihr_data -f schema.sql
   ```

3. **Start Redis and Kafka**
   ```bash
   # Start Redis
   redis-server --requirepass password
   
   # Start Kafka (using docker-compose for dependencies)
   docker-compose up -d zookeeper kafka redis postgres
   ```

4. **Run the service**
   ```bash
   python main.py
   ```

## API Endpoints

### Health Check
```http
GET /health
```

### Ingest Vital Signs
```http
POST /ingest/vitals
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "patient_id": "PAT123",
  "provider_id": "PROV456",
  "source_system": "EMR_SYSTEM",
  "heart_rate": 72,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "temperature": 98.6,
  "oxygen_saturation": 98.0,
  "respiratory_rate": 16,
  "weight": 150.5,
  "height": 68.0
}
```

### Ingest Lab Results
```http
POST /ingest/lab-results
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "patient_id": "PAT123",
  "provider_id": "PROV456",
  "source_system": "LAB_SYSTEM",
  "test_name": "Complete Blood Count",
  "result_value": "12.5",
  "reference_range": "11.0-15.0",
  "units": "g/dL",
  "status": "final",
  "lab_id": "LAB789"
}
```

### Ingest Medications
```http
POST /ingest/medications
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "patient_id": "PAT123",
  "provider_id": "PROV456",
  "source_system": "PHARMACY_SYSTEM",
  "medication_name": "Lisinopril",
  "dosage": "10mg",
  "frequency": "once daily",
  "start_date": "2024-01-01T00:00:00Z",
  "prescriber_id": "DOC123"
}
```

### Ingest HL7 Message
```http
POST /ingest/hl7
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "message_type": "ORU",
  "message_control_id": "MSG001",
  "sending_application": "LAB_SYSTEM",
  "receiving_application": "EMR_SYSTEM",
  "timestamp": "2024-01-01T12:00:00Z",
  "raw_message": "MSH|^~\\&|LAB_SYSTEM|HOSPITAL|EMR_SYSTEM|HOSPITAL|20240101120000||ORU^R01|MSG001|P|2.5\rPID|||PAT123||DOE^JOHN||19800101|M\rOBX|1|NM|789-8^Hemoglobin||12.5|g/dL|11.0-15.0|N|||F"
}
```

### Ingest FHIR Resource
```http
POST /ingest/fhir
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "resource_type": "Observation",
  "resource_id": "obs-123",
  "patient_reference": "PAT123",
  "raw_resource": {
    "resourceType": "Observation",
    "id": "obs-123",
    "subject": {
      "reference": "Patient/PAT123"
    },
    "code": {
      "coding": [{
        "system": "http://loinc.org",
        "code": "789-8",
        "display": "Hemoglobin"
      }]
    },
    "valueQuantity": {
      "value": 12.5,
      "unit": "g/dL",
      "system": "http://unitsofmeasure.org",
      "code": "g/dL"
    }
  }
}
```

### Get Processing Status
```http
GET /status/{message_id}
Authorization: Bearer <jwt-token>
```

### Get Metrics
```http
GET /metrics
Authorization: Bearer <jwt-token>
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/abena_ihr_data` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka bootstrap servers | `localhost:9092` |
| `AUTH_SERVICE_URL` | Auth service URL | `http://localhost:3001` |
| `ENCRYPTION_KEY` | Encryption key for sensitive data | Auto-generated |
| `MAX_MESSAGE_SIZE` | Maximum message size in bytes | `10485760` (10MB) |
| `BATCH_SIZE` | Processing batch size | `100` |
| `DUPLICATE_CHECK_WINDOW` | Duplicate check window in seconds | `3600` (1 hour) |

## Database Schema

The service uses PostgreSQL with the following main tables:

- `raw_health_data`: Raw incoming data storage
- `processed_health_data`: Normalized and validated data
- `vital_signs`: Structured vital signs data
- `lab_results`: Laboratory results
- `medications`: Medication data
- `hl7_messages`: Parsed HL7 messages
- `fhir_resources`: Parsed FHIR resources
- `imaging_studies`: Imaging study data
- `clinical_notes`: Clinical documentation
- `data_quality_metrics`: Data quality tracking
- `processing_errors`: Error logging
- `data_lineage`: Data transformation tracking

## Monitoring

### Health Checks
- Service health: `GET /health`
- Database connectivity
- Redis connectivity
- Kafka connectivity

### Metrics
- Daily ingestion counts by data type
- Processing status summary
- Error rates and types
- Processing time statistics

### Logging
- Structured logging with correlation IDs
- Error tracking and alerting
- Performance monitoring

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

### Linting
```bash
flake8 .
```

## Deployment

### Production Considerations

1. **Security**
   - Use strong encryption keys
   - Enable HTTPS/TLS
   - Implement proper authentication
   - Secure database connections

2. **Scalability**
   - Use connection pooling
   - Implement horizontal scaling
   - Configure proper resource limits
   - Use load balancers

3. **Monitoring**
   - Set up Prometheus metrics
   - Configure Grafana dashboards
   - Implement alerting
   - Monitor resource usage

4. **Backup and Recovery**
   - Regular database backups
   - Message queue persistence
   - Disaster recovery procedures

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check PostgreSQL is running
   - Verify connection string
   - Check network connectivity

2. **Redis Connection Errors**
   - Verify Redis is running
   - Check authentication
   - Validate connection string

3. **Kafka Connection Errors**
   - Ensure Zookeeper is running
   - Check Kafka broker configuration
   - Verify network connectivity

4. **Authentication Errors**
   - Verify Auth service is running
   - Check JWT token validity
   - Validate service URLs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is part of the Abena IHR microservices architecture. 