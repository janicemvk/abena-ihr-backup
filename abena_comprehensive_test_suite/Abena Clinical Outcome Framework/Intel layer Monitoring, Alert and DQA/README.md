# Abena IHR Intelligence Layer

A comprehensive monitoring, alerting, and data quality analytics system for healthcare integration platforms.

## 🚀 Features

### 📊 **Integration Monitoring**
- Real-time tracking of API calls and system integrations
- Response time monitoring and performance analytics
- Error rate tracking and failure pattern detection
- Success/failure rate analysis by source system

### 🔍 **Data Quality Analytics**
- Multi-dimensional data quality assessment (Completeness, Accuracy, Consistency, Timeliness)
- Automated anomaly detection using machine learning
- Custom quality rules for different data types
- Detailed quality reports with actionable recommendations

### 🚨 **Alerting System**
- Configurable alert rules with severity levels
- Multiple notification channels (Email, Slack)
- Alert cooldown periods to prevent spam
- Alert resolution tracking

### 📈 **Performance Monitoring**
- System health monitoring (CPU, Memory, Disk)
- Real-time health scoring
- Performance trend analysis
- Resource utilization tracking

### 📋 **Reporting & Dashboards**
- Comprehensive dashboard with real-time metrics
- Interactive charts and visualizations
- Automated report generation
- Historical trend analysis

### 🔧 **Prometheus Integration**
- Built-in Prometheus metrics
- Real-time metric collection
- Integration with Grafana for advanced visualizations

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Prometheus    │    │   Grafana       │
│   API Server    │    │   Metrics       │    │   Dashboards    │
│   (Port 8000)   │    │   (Port 8001)   │    │   (Port 3000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │           Intelligence Layer Core               │
         │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
         │  │Integration  │ │Data Quality │ │Performance  │ │
         │  │Monitor      │ │Analyzer     │ │Monitor      │ │
         │  └─────────────┘ └─────────────┘ └─────────────┘ │
         └─────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │              Data Storage                      │
         │  ┌─────────────┐ ┌─────────────┐              │
         │  │PostgreSQL   │ │Redis Cache  │              │
         │  │Database     │ │             │              │
         │  └─────────────┘ └─────────────┘              │
         └─────────────────────────────────────────────────┘
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd abena-ihr-intelligence-layer
   ```

2. **Configure the system**
   ```bash
   # Interactive configuration setup
   python setup_config.py
   
   # Or test existing configuration
   python test_config.py
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the services**
   - API Server: http://localhost:8000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb abena_ihr
   
   # The tables will be created automatically on first run
   ```

3. **Configure the system**
   ```bash
   # Interactive configuration setup
   python setup_config.py
   ```

4. **Run the application**
   ```bash
   python api_server.py
   ```

## ⚙️ Configuration

### Quick Configuration Setup

The easiest way to configure the system is using the interactive setup script:

```bash
python setup_config.py
```

This script will guide you through configuring:
- Database connection (PostgreSQL)
- Redis connection
- Email notifications (SMTP)
- Slack notifications
- Security settings (API keys)
- Monitoring thresholds
- Logging preferences

### Manual Configuration

If you prefer to configure manually, create a `.env` file based on `config.env.example`:

```bash
cp config.env.example .env
```

Then edit the `.env` file with your settings:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/abena_ihr
REDIS_URL=redis://localhost:6379

# Email Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@yourdomain.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=alerts@yourdomain.com
TO_EMAILS=admin@yourdomain.com,ops@yourdomain.com

# Slack Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Security
API_KEY_VALUE=your_secure_api_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Alert Thresholds
HIGH_ERROR_RATE_THRESHOLD=0.05
SLOW_RESPONSE_TIME_THRESHOLD=30.0
LOW_DATA_QUALITY_THRESHOLD=0.7
```

### Configuration Validation

Test your configuration:

```bash
python test_config.py
```

This will validate all settings and show you what's configured correctly.

### Configuration Categories

#### 🔐 **Security Configuration**
- **API Key Authentication**: Set `API_KEY_VALUE` for secure API access
- **CORS Origins**: Configure allowed origins for web access
- **Database Security**: Use strong passwords and SSL connections

#### 📧 **Email Notifications**
- **SMTP Server**: Gmail, Outlook, or your own SMTP server
- **App Passwords**: For Gmail, use app-specific passwords
- **Recipient Lists**: Comma-separated list of email addresses

#### 💬 **Slack Notifications**
- **Webhook URL**: Create a Slack app and get the webhook URL
- **Channel Configuration**: Messages will be sent to the configured channel

#### 🚨 **Alert Configuration**
- **Error Rate Threshold**: Default 5% (0.05)
- **Response Time Threshold**: Default 30 seconds
- **Data Quality Threshold**: Default 70% (0.7)
- **Cooldown Periods**: Prevent alert spam

#### 📊 **Monitoring Configuration**
- **Health Check Interval**: How often to check system health
- **Failure Detection**: Pattern detection intervals
- **System Thresholds**: CPU, memory, disk usage limits

#### 🔍 **Data Quality Configuration**
- **Anomaly Detection**: Machine learning sensitivity
- **Batch Processing**: Data analysis batch sizes
- **Quality Rules**: Custom rules for different data types

### Environment-Specific Configuration

#### Development
```env
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
API_KEY_VALUE=dev_api_key_123
```

#### Production
```env
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
API_KEY_VALUE=your_secure_production_key
SMTP_PASSWORD=your_secure_smtp_password
```

#### Testing
```env
DATABASE_URL=postgresql://test_user:test_pass@localhost/test_db
REDIS_URL=redis://localhost:6380
LOG_LEVEL=DEBUG
```

### Configuration Best Practices

1. **Never commit sensitive data** to version control
2. **Use environment-specific** `.env` files
3. **Rotate API keys** regularly
4. **Use strong passwords** for all services
5. **Enable SSL/TLS** for production databases
6. **Monitor configuration** changes
7. **Backup configuration** files

## 📖 Usage

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Record Integration Event
```bash
POST /integration/record
{
  "source_system": "Epic",
  "endpoint": "/api/patients",
  "response_time": 1.5,
  "status_code": 200,
  "success": true,
  "records_processed": 150
}
```

#### Analyze Data Quality
```bash
POST /data-quality/analyze
{
  "data_type": "patient",
  "source_system": "Epic",
  "data": [
    {
      "mrn": "MRN001",
      "first_name": "John",
      "email": "john@email.com"
    }
  ]
}
```

#### Get Dashboard Data
```bash
GET /dashboard?hours=24
```

#### Get Alerts
```bash
GET /alerts?resolved=false&limit=100
```

### Example Usage

```python
import asyncio
from main_orchestrator import IntelligenceLayer

async def main():
    # Initialize Intelligence Layer
    intelligence = IntelligenceLayer()
    
    # Record integration event
    await intelligence.record_integration_event(
        source_system="Epic",
        endpoint="/api/patients",
        response_time=1.5,
        status_code=200,
        success=True,
        records_processed=150
    )
    
    # Analyze data quality
    import pandas as pd
    data = pd.DataFrame({
        'mrn': ['MRN001', 'MRN002'],
        'first_name': ['John', 'Jane'],
        'email': ['john@email.com', 'jane@test.com']
    })
    
    quality_result = await intelligence.analyze_data_quality(
        data, "patient", "Epic"
    )
    
    print(f"Quality Score: {quality_result['overall_score']:.2%}")

asyncio.run(main())
```

## 🔧 Configuration

### Alert Rules

Configure alert rules in `main_orchestrator.py`:

```python
# High error rate alert
self.alert_manager.add_alert_rule(
    "high_error_rate",
    lambda m: m.get('error_rate', 0) > 0.05,  # 5% error rate
    AlertSeverity.HIGH,
    cooldown_minutes=10
)
```

### Notification Channels

Configure email notifications:

```python
email_channel = EmailNotificationChannel(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="alerts@abena-ihr.com",
    password="your_app_password",
    from_email="alerts@abena-ihr.com",
    to_emails=["admin@abena-ihr.com"]
)
```

### Data Quality Rules

Add custom quality rules:

```python
from data_quality_analyzer import QualityRule, DataQualityDimension

custom_rules = [
    QualityRule(DataQualityDimension.COMPLETENESS, "mrn", "required", {}),
    QualityRule(DataQualityDimension.VALIDITY, "email", "email_format", {}),
]

intelligence.data_quality_analyzer.add_quality_rules("patient", custom_rules)
```

## 📊 Monitoring & Visualization

### Prometheus Metrics

The system exposes the following Prometheus metrics:

- `abena_integration_requests_total` - Total integration requests
- `abena_integration_response_time_seconds` - Response time histogram
- `abena_integration_errors_total` - Total integration errors
- `abena_data_quality_score` - Data quality scores
- `abena_system_health_score` - System health score
- `abena_active_alerts` - Number of active alerts

### Grafana Dashboards

Pre-configured dashboards are available for:
- Integration monitoring
- Data quality analytics
- System health monitoring
- Alert management

## 🔒 Security

### Environment Variables

Set secure environment variables:

```bash
export DATABASE_URL="postgresql://user:secure_password@localhost/abena_ihr"
export REDIS_URL="redis://localhost:6379"
export SMTP_PASSWORD="your_secure_smtp_password"
export SLACK_WEBHOOK_URL="your_slack_webhook_url"
```

### API Security

- Use HTTPS in production
- Implement API key authentication
- Configure CORS properly
- Rate limiting recommended

## 🧪 Testing

Run the example usage:

```bash
python example_usage.py
```

This will:
1. Create sample data files
2. Record integration events
3. Perform data quality analysis
4. Generate dashboard data
5. Demonstrate anomaly detection

## 📝 API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Changelog

### v1.0.0
- Initial release
- Integration monitoring
- Data quality analytics
- Alerting system
- Performance monitoring
- API server
- Docker support
- Configuration management system 