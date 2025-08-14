# Abena Predictive Analytics Engine (Unified)

A unified healthcare predictive analytics platform that uses **ONLY** the Abena SDK for all authorization, authentication, and data handling.

## 🎯 Key Features

### Unified Architecture (Abena SDK ONLY)
- **Single Abena SDK Integration**: ALL services consolidated through Abena SDK ONLY
- **No Non-Abena Systems**: Removed ALL individual auth, databases, and audit systems
- **Centralized Configuration**: Single configuration file for Abena SDK services ONLY
- **Unified Data Flow**: ALL data processing through Abena services ONLY

### Core Capabilities
- **Patient Risk Prediction**: Readmission, mortality, infection, medication adherence
- **Population Cohort Analysis**: Risk stratification with anonymized data
- **Outbreak Risk Prediction**: Facility-level infection outbreak assessment
- **Treatment Recommendations**: Evidence-based treatment optimization
- **Real-time Deterioration Monitoring**: Early warning systems

### Privacy & Security (Abena SDK ONLY)
- **Abena SDK Authentication**: Single sign-on across all services
- **Unified Data Services**: ALL data access through Abena data service ONLY
- **Centralized Privacy**: K-anonymity and differential privacy through Abena ONLY
- **Blockchain Audit Trail**: Immutable logging through Abena blockchain service ONLY

## 🏗️ Architecture

```
predictive_analysis_engine/
├── application-services/
│   └── predictive-analytics-engine/
│       ├── src/
│       │   └── predictive_analytics_engine.py  # Main engine (Abena SDK ONLY)
│       ├── README.md                           # Engine documentation
│       ├── requirements.txt                    # Engine dependencies (Abena SDK ONLY)
│       └── test_engine.py                      # Test suite (Abena SDK ONLY)
├── config.py                                   # Unified configuration (Abena SDK ONLY)
├── start_app.py                                # Unified startup script
├── requirements.txt                            # Main dependencies (Abena SDK ONLY)
└── README.md                                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies (Abena SDK ONLY)
```bash
pip install -r requirements.txt
```

### 2. Set Abena SDK Environment Variables
```bash
export AUTH_SERVICE_URL=http://localhost:3001
export DATA_SERVICE_URL=http://localhost:8001
export PRIVACY_SERVICE_URL=http://localhost:8002
export BLOCKCHAIN_SERVICE_URL=http://localhost:8003
```

### 3. Run the Application
```bash
python start_app.py
```

### 4. Test the Engine
Select option 1 to run the predictive analytics engine tests.

## 🔧 Unified Configuration (Abena SDK ONLY)

All configuration is centralized in `config.py` and uses ONLY Abena SDK:

```python
from config import get_config, get_service_urls

# Get unified configuration (Abena SDK ONLY)
config = get_config()

# Get Abena SDK service URLs (ONLY source)
services = get_service_urls()
```

## 📊 Usage Examples

### Patient Risk Prediction (Abena SDK ONLY)
```python
import asyncio
from application_services.predictive_analytics_engine.src.predictive_analytics_engine import PredictiveAnalyticsEngine

async def main():
    engine = PredictiveAnalyticsEngine()
    # Authenticate through Abena SDK ONLY
    await engine.authenticate('user@healthcare.org', 'password')
    
    predictions = await engine.predict_patient_risk(
        patient_id='P12345',
        prediction_types=['readmission_risk', 'mortality_risk'],
        timeframe='30d'
    )
    
    for pred in predictions:
        print(f"{pred.prediction_type}: {pred.risk_score:.2f}")

asyncio.run(main())
```

### Population Cohort Analysis (Abena SDK ONLY)
```python
cohort_analysis = await engine.analyze_population_cohort(
    cohort_criteria={
        'patients': ['P12345', 'P12346', 'P12347'],
        'age_range': [65, 85],
        'conditions': ['diabetes', 'hypertension']
    }
)
```

## 🔒 Security & Privacy (Abena SDK ONLY)

### Unified Access Control (Abena SDK ONLY)
- **Single Authentication**: ALL access through Abena auth service ONLY
- **Role-based Permissions**: Centralized permission management through Abena SDK
- **Purpose-based Access**: Data access tied to specific purposes through Abena SDK

### Unified Data Privacy (Abena SDK ONLY)
- **K-anonymity**: Configurable k-values for anonymization through Abena SDK
- **Differential Privacy**: Epsilon parameter control through Abena SDK
- **Quasi-identifier Protection**: Automatic PII protection through Abena SDK

### Unified Audit Trail (Abena SDK ONLY)
- **Blockchain Logging**: ALL actions logged to Abena blockchain ONLY
- **Access Tracking**: Complete audit trail through Abena SDK ONLY
- **Compliance Ready**: HIPAA, GDPR, and other compliance frameworks through Abena SDK

## 🧪 Testing

### Run Engine Tests (Abena SDK ONLY)
```bash
cd application-services/predictive-analytics-engine
python test_engine.py
```

### Test Coverage
- ✅ Patient risk prediction (Abena SDK ONLY)
- ✅ Population cohort analysis (Abena SDK ONLY)
- ✅ Outbreak risk prediction (Abena SDK ONLY)
- ✅ Treatment recommendations (Abena SDK ONLY)
- ✅ Deterioration monitoring (Abena SDK ONLY)
- ✅ Abena SDK integration (ONLY)
- ✅ Privacy and security features (Abena SDK ONLY)

## 📦 Dependencies (Abena SDK ONLY)

### Core Dependencies
- `httpx>=0.24.0`: Async HTTP client for Abena SDK ONLY
- `pandas>=2.1.0`: Data manipulation
- `numpy>=1.26.0`: Numerical computing
- `asyncio`: Asynchronous programming

### Optional Dependencies
- `streamlit>=1.25.0`: Web interface
- `plotly>=5.15.0`: Data visualization
- `scikit-learn>=1.3.0`: Machine learning

## 🔄 Migration from Old System

### What Was Removed (ALL Non-Abena SDK)
- ❌ Individual authentication systems → ✅ **Abena SDK ONLY**
- ❌ Duplicate database configurations → ✅ **Abena SDK ONLY**
- ❌ Separate audit logging systems → ✅ **Abena SDK ONLY**
- ❌ Multiple configuration files → ✅ **Abena SDK ONLY**
- ❌ Standalone applications → ✅ **Abena SDK ONLY**

### What Was Consolidated (Abena SDK ONLY)
- ✅ ALL auth through Abena SDK ONLY
- ✅ ALL data through Abena services ONLY
- ✅ ALL audit through Abena blockchain ONLY
- ✅ Single configuration file (Abena SDK ONLY)
- ✅ Unified application structure (Abena SDK ONLY)

## 🛠️ Development

### Adding New Features (Abena SDK ONLY)
1. Extend the Abena SDK integration ONLY
2. Add new prediction models to the engine
3. Update unified configuration (Abena SDK ONLY)
4. Add tests to the test suite (Abena SDK ONLY)

### Code Style (Abena SDK ONLY)
- Follow async/await patterns
- Use type hints throughout
- Include comprehensive error handling
- Add Abena SDK blockchain audit logging ONLY

## 📈 Performance

### Optimizations (Abena SDK ONLY)
- **Async Operations**: All I/O operations are asynchronous through Abena SDK
- **Connection Pooling**: HTTP client connection reuse for Abena SDK
- **Caching**: Configurable caching for repeated Abena SDK requests
- **Batch Processing**: Efficient cohort analysis through Abena SDK

### Monitoring (Abena SDK ONLY)
- **Service Health Checks**: Automatic Abena service availability monitoring
- **Performance Metrics**: Response time and throughput tracking for Abena SDK
- **Error Tracking**: Comprehensive error logging through Abena SDK

## 🤝 Contributing

1. **Follow Abena SDK Architecture**: ALL changes must use Abena SDK ONLY
2. **Update Configuration**: Modify `config.py` for new Abena SDK settings
3. **Add Tests**: Include tests in `test_engine.py` (Abena SDK ONLY)
4. **Document Changes**: Update relevant documentation
5. **Audit Compliance**: Ensure all changes are logged to Abena blockchain ONLY

## 📄 License

This project is part of the Abena healthcare analytics platform.

## 🆘 Support

For issues and questions:
1. Check the unified configuration in `config.py` (Abena SDK ONLY)
2. Verify Abena service connectivity
3. Review the test suite for examples (Abena SDK ONLY)
4. Check Abena blockchain audit logs for debugging

---

**Note**: This is a unified system where ALL functionality is consolidated through the Abena SDK ONLY. NO non-Abena SDK systems exist for authorization, authentication, or data handling. 