# Abena IHR - API Gateway and External Connectors System

A comprehensive integration layer for the Abena Intelligent Health Records (IHR) system, providing seamless connectivity with wearable devices, EMR systems, telemedicine platforms, and laboratory systems.

## 🏗️ Architecture Overview

The system consists of several key components:

- **API Gateway**: Central entry point with authentication, rate limiting, and request routing
- **Device Adapters**: Integration with wearable devices (Fitbit, Apple Health, Garmin)
- **EMR Connectors**: FHIR-based connectors for Epic, Cerner, and other EMR systems
- **Telemedicine Bridges**: Integration with Zoom, Doxy.me, and other telemedicine platforms
- **Lab System Adapters**: Connectors for LabCorp, Quest, and other laboratory systems
- **Webhook Handler**: Real-time data processing from external systems
- **Integration Orchestrator**: Coordinates data synchronization and ETL processes

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd abena-ihr-integration
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 📋 API Endpoints

### Health Check
- `GET /health` - System health status

### Patient Management
- `POST /api/v1/patients` - Create new patient record
- `GET /api/v1/patients/{patient_id}` - Get patient information
- `PUT /api/v1/patients/{patient_id}` - Update patient record

### Observations
- `POST /api/v1/observations` - Create new observation
- `GET /api/v1/observations/{patient_id}` - Get patient observations

### Device Integration
- `POST /api/v1/devices/sync` - Sync device data
- `POST /api/v1/devices/register` - Register new device

### Webhooks
- `POST /webhooks/{source}` - Receive webhooks from external systems

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/abena_ihr

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO

# External API Keys
FITBIT_CLIENT_ID=your_fitbit_client_id
FITBIT_CLIENT_SECRET=your_fitbit_client_secret
EPIC_CLIENT_ID=your_epic_client_id
EPIC_PRIVATE_KEY=your_epic_private_key
ZOOM_API_KEY=your_zoom_api_key
ZOOM_API_SECRET=your_zoom_api_secret
```

### Supported Integrations

#### Wearable Devices
- **Fitbit**: Heart rate, weight, activity data
- **Apple Health**: HealthKit integration
- **Garmin**: Activity and wellness data
- **Samsung Health**: Health and fitness data

#### EMR Systems
- **Epic**: FHIR R4 API integration
- **Cerner**: FHIR R4 API integration
- **Allscripts**: Custom API integration

#### Telemedicine Platforms
- **Zoom**: Meeting creation and recording access
- **Doxy.me**: Appointment management

#### Laboratory Systems
- **LabCorp**: Lab orders and results
- **Quest Diagnostics**: Lab orders and results

## 🔐 Security Features

- **JWT Authentication**: Secure API key management
- **Rate Limiting**: Sliding window rate limiting per API key
- **CORS Protection**: Configured for specific domains
- **Request Validation**: Pydantic-based data validation
- **Encryption**: Sensitive data encryption at rest
- **Webhook Verification**: HMAC signature verification

## 📊 Monitoring and Observability

### Health Checks
- Application health endpoint
- Database connectivity checks
- Redis connectivity checks
- External service health monitoring

### Metrics
- API request/response metrics
- Rate limiting statistics
- Error rates and response times
- Queue processing metrics

### Logging
- Structured logging with correlation IDs
- Request/response logging
- Error tracking and alerting
- Performance monitoring

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_api_gateway.py
```

### Test Structure
```
tests/
├── test_api_gateway.py
├── test_device_adapters.py
├── test_emr_connectors.py
├── test_telemedicine_bridges.py
├── test_lab_adapters.py
└── test_webhook_handler.py
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f integration-api

# Scale services
docker-compose up -d --scale integration-api=3
```

### Production Considerations

1. **Environment Variables**: Use secure environment variable management
2. **SSL/TLS**: Configure HTTPS with proper certificates
3. **Load Balancing**: Use nginx or similar for load balancing
4. **Monitoring**: Set up Prometheus and Grafana for monitoring
5. **Backup**: Configure database and Redis backups
6. **Security**: Implement proper firewall rules and network security

## 📈 Performance Optimization

### Caching Strategy
- Redis caching for frequently accessed data
- API response caching
- Database query result caching

### Queue Processing
- Asynchronous processing of device sync
- Background ETL pipeline processing
- Webhook queue management

### Database Optimization
- Connection pooling
- Query optimization
- Indexing strategy

## 🔄 Data Flow

1. **Device Data**: Wearable devices → Webhook/API → Queue → ETL → Database
2. **EMR Data**: EMR Systems → FHIR API → Queue → ETL → Database
3. **Lab Results**: Lab Systems → API → Queue → ETL → Database
4. **Telemedicine**: Platforms → API → Appointment Management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔮 Roadmap

- [ ] Additional EMR system integrations
- [ ] Real-time data streaming
- [ ] Advanced analytics and reporting
- [ ] Machine learning integration
- [ ] Mobile app SDK
- [ ] Advanced security features
- [ ] Multi-tenant support 