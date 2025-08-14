# Predictive Analytics Engine with Abena SDK

This is an enhanced predictive analytics engine that integrates with the Abena SDK for secure, privacy-compliant healthcare analytics.

## Features

### Core Predictive Capabilities
- **Patient Risk Prediction**: Readmission risk, mortality risk, length of stay, infection risk, medication adherence
- **Population Cohort Analysis**: Risk stratification and population health insights
- **Outbreak Risk Prediction**: Facility-level infection outbreak risk assessment
- **Treatment Recommendations**: Evidence-based treatment optimization
- **Real-time Deterioration Monitoring**: Early warning systems for patient safety

### Privacy & Security Features
- **Abena SDK Integration**: Secure authentication and data access
- **Anonymized Data Processing**: K-anonymity and differential privacy support
- **Blockchain Audit Trail**: Immutable logging of all data access and predictions
- **Access Control**: Granular permission validation for all operations

## Architecture

```
application-services/predictive-analytics-engine/
├── src/
│   └── predictive_analytics_engine.py  # Main engine with Abena SDK
├── README.md                           # This file
└── requirements.txt                    # Dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export AUTH_SERVICE_URL=http://localhost:3001
export DATA_SERVICE_URL=http://localhost:8001
export PRIVACY_SERVICE_URL=http://localhost:8002
export BLOCKCHAIN_SERVICE_URL=http://localhost:8003
```

## Usage

### Basic Example

```python
import asyncio
from src.predictive_analytics_engine import PredictiveAnalyticsEngine

async def main():
    # Initialize engine
    engine = PredictiveAnalyticsEngine()
    
    # Authenticate with Abena services
    await engine.authenticate('analyst@healthcare.org', 'secure_password')
    
    # Generate patient risk predictions
    predictions = await engine.predict_patient_risk(
        patient_id='P12345',
        prediction_types=['readmission_risk', 'mortality_risk'],
        timeframe='30d'
    )
    
    # Print results
    for pred in predictions:
        print(f"{pred.prediction_type}: {pred.risk_score:.2f} risk score")
        print(f"Confidence: {pred.confidence:.2f}")
        print(f"Factors: {pred.contributing_factors}")
        print(f"Recommendations: {pred.recommendations}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Population Cohort Analysis

```python
# Analyze a population cohort
cohort_analysis = await engine.analyze_population_cohort(
    cohort_criteria={
        'patients': ['P12345', 'P12346', 'P12347'],
        'age_range': [65, 85],
        'conditions': ['diabetes', 'hypertension']
    },
    analysis_type='risk_stratification'
)

print(f"Cohort ID: {cohort_analysis.cohort_id}")
print(f"Patient Count: {cohort_analysis.patient_count}")
print(f"Risk Distribution: {cohort_analysis.risk_distribution}")
```

### Outbreak Risk Prediction

```python
# Predict facility outbreak risk
outbreak_risk = await engine.predict_outbreak_risk(
    facility_id='FACILITY_001',
    infection_type='general'
)

print(f"Risk Level: {outbreak_risk['risk_level']}")
print(f"Risk Score: {outbreak_risk['risk_score']:.2f}")
print(f"Recommendations: {outbreak_risk['recommendations']}")
```

### Treatment Recommendations

```python
# Generate treatment recommendations
recommendations = await engine.generate_treatment_recommendations(
    patient_id='P12345',
    condition='diabetes',
    current_treatments=['metformin']
)

print(f"Treatments: {recommendations['treatments']}")
print(f"Evidence Level: {recommendations['evidence_level']}")
print(f"Monitoring: {recommendations['monitoring_requirements']}")
```

### Real-time Deterioration Monitoring

```python
# Monitor patient deterioration
monitoring_result = await engine.monitor_patient_deterioration(
    patient_id='P12345',
    monitoring_duration='24h'
)

print(f"Deterioration Score: {monitoring_result['deterioration_score']:.2f}")
print(f"Risk Level: {monitoring_result['risk_level']}")
if monitoring_result['early_warning']:
    print(f"Early Warning: {monitoring_result['early_warning']['message']}")
```

## Data Models

### PredictionResult
```python
@dataclass
class PredictionResult:
    patient_id: str
    prediction_type: str
    risk_score: float
    confidence: float
    contributing_factors: List[str]
    recommendations: List[str]
    timeframe: str
    generated_at: datetime
    model_version: str
```

### CohortAnalysis
```python
@dataclass
class CohortAnalysis:
    cohort_id: str
    patient_count: int
    risk_distribution: Dict[str, int]
    top_risk_factors: List[str]
    population_recommendations: List[str]
    data_quality_score: float
```

## Supported Prediction Types

1. **readmission_risk**: 30-day readmission probability
2. **mortality_risk**: In-hospital mortality risk
3. **length_of_stay**: Expected length of stay
4. **infection_risk**: Healthcare-associated infection risk
5. **medication_adherence**: Medication adherence probability

## Privacy & Compliance

### Data Anonymization
- K-anonymity with configurable k-values
- Differential privacy with epsilon parameter
- Quasi-identifier protection

### Audit Trail
- All data access logged to blockchain
- Immutable transaction records
- Purpose-based access tracking

### Access Control
- Role-based permissions
- Purpose-based data access
- Service-level authorization

## Error Handling

The engine includes comprehensive error handling:

```python
try:
    predictions = await engine.predict_patient_risk(
        patient_id='P12345',
        prediction_types=['readmission_risk']
    )
except PermissionError as e:
    print(f"Access denied: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

### Environment Variables
- `AUTH_SERVICE_URL`: Abena authentication service URL
- `DATA_SERVICE_URL`: Abena data service URL
- `PRIVACY_SERVICE_URL`: Abena privacy service URL
- `BLOCKCHAIN_SERVICE_URL`: Abena blockchain service URL

### Model Configuration
Models can be configured in the engine initialization:

```python
self.models = {
    'readmission_risk': {'version': '1.2.3', 'threshold': 0.6},
    'mortality_risk': {'version': '1.1.1', 'threshold': 0.8},
    # ... other models
}
```

## Testing

Run the example:
```bash
cd application-services/predictive-analytics-engine
python src/predictive_analytics_engine.py
```

## Dependencies

- `httpx`: Async HTTP client for Abena SDK
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computing
- `asyncio`: Asynchronous programming support

## Security Considerations

1. **Authentication**: Always use secure credentials
2. **Network Security**: Use HTTPS for all service communications
3. **Data Privacy**: Ensure proper anonymization before analysis
4. **Access Logging**: All access is logged to blockchain for audit
5. **Error Handling**: Sensitive information is not exposed in error messages

## Contributing

1. Follow the existing code style
2. Add comprehensive error handling
3. Include privacy and security considerations
4. Update documentation for new features
5. Add appropriate logging for audit trails

## License

This project is part of the Abena healthcare analytics platform. 