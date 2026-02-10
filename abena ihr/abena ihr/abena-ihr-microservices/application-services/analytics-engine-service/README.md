# Abena IHR Analytics Engine Service

## Overview

The Analytics Engine Service is a comprehensive healthcare analytics platform that provides advanced predictive analytics, population health insights, and real-time monitoring capabilities for the Abena IHR system.

## Features

### 🧠 Predictive Analytics
- **Disease Risk Prediction**: ML models to predict disease risk based on patient demographics, vital signs, and lab results
- **Treatment Outcome Forecasting**: Predict treatment effectiveness and patient outcomes
- **Readmission Risk Assessment**: Identify patients at high risk of hospital readmission
- **Medication Effectiveness Analysis**: Predict medication response and effectiveness

### 📊 Population Analytics
- **Health Trends Analysis**: Track population health trends over time
- **Risk Factor Analysis**: Identify and analyze risk factors across populations
- **Demographic Health Patterns**: Analyze health patterns across different demographic groups
- **Health Outcome Comparisons**: Compare health outcomes against benchmarks

### ⚡ Real-Time Analytics
- **Live Health Monitoring**: Real-time monitoring of patient vital signs and health metrics
- **Anomaly Detection**: Automatic detection of unusual health patterns
- **Alert Generation**: Configurable alerts for critical health events
- **Performance Metrics**: Real-time tracking of system performance

### 🔧 Data Processing
- **ETL Pipelines**: Extract, Transform, Load processes for healthcare data
- **Feature Engineering**: Advanced feature creation and selection
- **Data Quality Validation**: Comprehensive data quality checks
- **Time Series Processing**: Specialized processing for temporal health data

## Architecture

```
analytics-engine-service/
├── src/
│   ├── predictive_analytics_engine.py    # Main predictive analytics API
│   ├── population_analytics.py           # Population health analytics
│   ├── real_time_analytics.py           # Real-time monitoring
│   ├── ml_models/                        # Machine learning models
│   │   ├── __init__.py
│   │   ├── disease_risk_model.py
│   │   ├── treatment_outcome_model.py
│   │   ├── readmission_risk_model.py
│   │   └── medication_effectiveness_model.py
│   └── data_processing/                  # ETL and feature engineering
│       ├── __init__.py
│       ├── etl_processor.py
│       ├── feature_engineering.py
│       ├── data_cleaner.py
│       ├── data_validator.py
│       └── time_series_processor.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+
- Redis 7+

### Using Docker Compose

1. **Clone and navigate to the service directory:**
   ```bash
   cd abena-ihr-microservices/application-services/analytics-engine-service
   ```

2. **Start the service:**
   ```bash
   docker-compose up -d
   ```

3. **Verify the service is running:**
   ```bash
   curl http://localhost:8010/health
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   export REDIS_HOST=localhost
   export REDIS_PORT=6379
   export DATABASE_URL=postgresql://user:password@localhost/analytics
   ```

3. **Run the service:**
   ```bash
   uvicorn src.predictive_analytics_engine:app --host 0.0.0.0 --port 8010 --reload
   ```

## API Endpoints

### Predictive Analytics Engine (Port 8010)

#### Health Check
```http
GET /health
```

#### Make Predictions
```http
POST /predict
Content-Type: application/json

{
  "patient_data": {
    "patient_id": "P12345",
    "age": 65,
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 85,
    "blood_pressure_systolic": 150,
    "blood_pressure_diastolic": 95,
    "heart_rate": 80,
    "temperature": 36.8,
    "glucose_level": 110,
    "diabetes_status": "type2",
    "smoking_status": "current"
  },
  "prediction_type": "disease_risk",
  "confidence_threshold": 0.7,
  "include_explanations": true
}
```

#### Train Models
```http
POST /train
Content-Type: application/json

{
  "dataset_path": "/data/training_data.csv",
  "target_variable": "disease_risk",
  "model_type": "classification",
  "features": ["age", "bmi", "blood_pressure"],
  "test_size": 0.2
}
```

#### List Models
```http
GET /models
```

#### Model Performance
```http
GET /models/{model_name}/performance
```

### Population Analytics (Port 8011)

#### Analyze Population
```http
POST /analyze
Content-Type: application/json

{
  "population_data": {
    "population_id": "POP001",
    "region": "North Region",
    "age_groups": {"18-30": 1000, "31-50": 2000, "51-70": 1500},
    "gender_distribution": {"male": 2200, "female": 2300},
    "health_metrics": {
      "bmi": [25.5, 26.1, 24.8, 27.2],
      "blood_pressure": [120, 125, 118, 130]
    },
    "disease_prevalence": {
      "diabetes": 12.5,
      "hypertension": 28.3,
      "heart_disease": 8.7
    }
  },
  "analysis_type": "trends",
  "time_period": "1_year",
  "confidence_level": 0.95
}
```

### Real-Time Analytics (Port 8012)

#### Add Metric
```http
POST /metrics
Content-Type: application/json

{
  "metric_id": "M001",
  "patient_id": "P12345",
  "metric_type": "vital_signs",
  "metric_name": "heart_rate",
  "value": 85,
  "unit": "bpm",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "monitor_device",
  "confidence": 0.95
}
```

#### Get Dashboard
```http
GET /dashboard
```

#### Get Alerts
```http
GET /alerts
```

#### WebSocket for Real-time Updates
```javascript
const ws = new WebSocket('ws://localhost:8012/ws');
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

## Machine Learning Models

### Disease Risk Model
- **Purpose**: Predict disease risk categories (low, moderate, high)
- **Features**: Demographics, vital signs, lab results, risk factors
- **Output**: Risk category with confidence score and contributing factors

### Treatment Outcome Model
- **Purpose**: Predict treatment effectiveness (poor, fair, good, excellent)
- **Features**: Patient characteristics, treatment details, clinical factors
- **Output**: Outcome prediction with success probability

### Readmission Risk Model
- **Purpose**: Predict readmission risk (low, medium, high)
- **Features**: Patient data, admission details, clinical factors
- **Output**: Risk assessment with prevention recommendations

### Medication Effectiveness Model
- **Purpose**: Predict medication effectiveness
- **Features**: Patient data, medication details, compliance
- **Output**: Effectiveness prediction with optimization suggestions

## Data Processing

### ETL Processor
- **Extract**: From APIs, databases, files (CSV, JSON, Excel, Parquet)
- **Transform**: Data cleaning, standardization, feature engineering
- **Load**: To databases, Redis cache, files

### Feature Engineering
- **Demographic Features**: Age, gender, BMI calculations
- **Clinical Features**: Vital signs, lab results, risk factors
- **Temporal Features**: Time-based patterns and trends
- **Interaction Features**: Cross-feature relationships

### Data Quality Validation
- **Missing Value Analysis**: Identify and handle missing data
- **Data Type Validation**: Ensure correct data types
- **Range Validation**: Check for out-of-range values
- **Quality Scoring**: Overall data quality assessment

## Monitoring and Observability

### Prometheus Metrics
- **Request Count**: Total API requests
- **Response Time**: API response latency
- **Error Rate**: Failed request percentage
- **Model Performance**: ML model accuracy and metrics

### Grafana Dashboards
- **Service Health**: Overall service status
- **Performance Metrics**: Response times and throughput
- **ML Model Metrics**: Model performance over time
- **Data Quality**: Data validation results

### Health Checks
- **Service Health**: `/health` endpoint
- **Database Connectivity**: PostgreSQL connection status
- **Redis Connectivity**: Cache connection status
- **Model Status**: ML model availability

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/analytics

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Logging
LOG_LEVEL=INFO

# Model Configuration
MODEL_CACHE_TTL=3600
PREDICTION_CACHE_TTL=1800

# Security
API_KEY=your_api_key
JWT_SECRET=your_jwt_secret
```

### Docker Configuration

The service includes:
- **PostgreSQL**: Primary database for analytics data
- **Redis**: Caching and real-time data storage
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Visualization and dashboards

## Development

### Code Structure
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM
- **Scikit-learn**: Machine learning models
- **Pandas**: Data manipulation and analysis

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_predictive_analytics.py
```

### Code Quality
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Deployment

### Production Deployment
1. **Build the image:**
   ```bash
   docker build -t abena-analytics-engine .
   ```

2. **Deploy with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Monitor deployment:**
   ```bash
   docker-compose logs -f analytics-engine
   ```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: analytics-engine
  template:
    metadata:
      labels:
        app: analytics-engine
    spec:
      containers:
      - name: analytics-engine
        image: abena-analytics-engine:latest
        ports:
        - containerPort: 8010
```

## Security

### Authentication
- JWT-based authentication
- API key validation
- Role-based access control

### Data Protection
- Data encryption at rest and in transit
- PII (Personally Identifiable Information) handling
- HIPAA compliance considerations

### Network Security
- HTTPS/TLS encryption
- Network segmentation
- Firewall rules

## Troubleshooting

### Common Issues

1. **Service won't start:**
   - Check database connectivity
   - Verify Redis connection
   - Check log files

2. **Model predictions failing:**
   - Ensure models are trained
   - Check input data format
   - Verify feature names

3. **High response times:**
   - Check database performance
   - Monitor Redis cache hit rate
   - Review model complexity

### Logs
```bash
# View service logs
docker-compose logs analytics-engine

# View specific service logs
docker-compose logs -f analytics-engine

# View all logs
docker-compose logs -f
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Roadmap

### Upcoming Features
- **Advanced ML Models**: Deep learning models for complex predictions
- **Natural Language Processing**: Text analysis of medical notes
- **Federated Learning**: Privacy-preserving distributed learning
- **Real-time Streaming**: Apache Kafka integration
- **Advanced Visualizations**: Interactive dashboards
- **Mobile API**: Optimized endpoints for mobile applications

### Performance Improvements
- **Model Optimization**: Faster inference times
- **Caching Strategy**: Improved cache hit rates
- **Database Optimization**: Query performance improvements
- **Horizontal Scaling**: Load balancing and auto-scaling 