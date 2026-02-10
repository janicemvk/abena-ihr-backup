# Abena IHR - Machine Learning Feedback Pipeline

An advanced ML pipeline for continuous learning and model improvement in healthcare, featuring automated retraining, performance monitoring, and clinical insights generation.

## Features

1. **ModelRegistry**: Version control and deployment management for ML models
2. **OutcomeAnalyzer**: Comprehensive analysis of treatment outcomes and prediction accuracy
3. **AutoMLOptimizer**: Automated hyperparameter optimization using Optuna
4. **ModelRetrainingPipeline**: Automated model retraining based on performance degradation
5. **ContinuousLearningOrchestrator**: Main orchestrator for continuous learning cycles
6. **AbenaSDK Integration**: Unified authentication, data access, privacy, and audit logging via Abena SDK

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Setup

```python
from ml_feedback_pipeline import ContinuousLearningOrchestrator, ModelRegistry

# Initialize model registry
model_registry = ModelRegistry()

# Initialize continuous learning orchestrator
continuous_learning = ContinuousLearningOrchestrator(model_registry)
```

### Abena SDK Integration Setup

```python
# Abena SDK configuration
abena_config = {
    'authServiceUrl': 'http://localhost:3001',
    'dataServiceUrl': 'http://localhost:8001',
    'privacyServiceUrl': 'http://localhost:8002', 
    'blockchainServiceUrl': 'http://localhost:8003',
    'auto_push_to_emr': True
}

# Initialize with Abena SDK integration
continuous_learning = ContinuousLearningOrchestrator(model_registry, abena_config)
```

### Adding Outcome Data

```python
from ml_feedback_pipeline import OutcomeData
from datetime import datetime

# Create outcome data
outcome = OutcomeData(
    patient_id="PATIENT_001",
    treatment_id="TX_001",
    prediction_id="PRED_001",
    actual_outcome=0.75,
    outcome_date=datetime.now(),
    time_to_outcome=30,
    adverse_events=[],
    side_effects=["mild_nausea"],
    patient_satisfaction=8.5,
    provider_assessment="good_response",
    pain_reduction=3.2,
    functional_improvement=15.0,
    medication_adherence=0.95,
    quality_of_life_change=2.1,
    healthcare_utilization={"office_visits": 2, "er_visits": 0},
    cost_effectiveness=0.8
)

# Add to learning system
continuous_learning.add_outcome_data(outcome)
```

### Running Analysis

```python
# Run daily analysis
analysis_result = continuous_learning.run_daily_analysis()
print(f"Analysis status: {analysis_result['status']}")

# Generate learning report
learning_report = continuous_learning.generate_learning_report(30)
print(f"Total outcomes analyzed: {learning_report['data_summary']['total_outcomes']}")
```

### Automated Learning Cycle

```python
# Execute complete automated learning cycle
cycle_results = continuous_learning.execute_automated_learning_cycle()
print(f"Cycle status: {cycle_results['status']}")
```

### Abena SDK Integration

```python
# Push insights to EMR for a specific patient via Abena SDK
emr_result = continuous_learning.push_insights_to_emr("PATIENT_001")
print(f"EMR push success: {emr_result['success']}")

# Create clinical summary via Abena SDK
summary_result = continuous_learning.create_patient_clinical_summary("PATIENT_001")
print(f"Clinical summary created: {summary_result['success']}")

# Get patient history via Abena SDK
history_result = continuous_learning.get_patient_emr_history("PATIENT_001", 30)
print(f"Patient history retrieved: {history_result['success']}")

# Auto-push high priority insights via Abena SDK
auto_push_result = continuous_learning.auto_push_high_priority_insights()
print(f"Auto-push completed: {auto_push_result['success']}")
```

## Architecture

The pipeline consists of several key components:

- **ModelRegistry**: Manages model versions, deployments, and metadata
- **OutcomeAnalyzer**: Analyzes prediction accuracy and identifies patterns
- **AutoMLOptimizer**: Optimizes model hyperparameters using Optuna
- **ModelRetrainingPipeline**: Handles automated model retraining
- **ContinuousLearningOrchestrator**: Orchestrates the entire learning process
- **AbenaSDK**: Provides unified authentication, data access, privacy controls, and audit logging

## Abena SDK Benefits

The integration with Abena SDK provides:

1. **Unified Authentication**: Automatic authentication and session management
2. **Privacy Controls**: Automatic data encryption and privacy filtering
3. **Audit Logging**: Comprehensive audit trail for compliance
4. **Data Access**: Secure patient and treatment data access
5. **EMR Integration**: Seamless integration with Electronic Medical Records
6. **Permission Management**: Role-based access control

## Configuration

### Abena SDK Configuration

```python
abena_config = {
    'authServiceUrl': 'http://localhost:3001',      # Authentication service
    'dataServiceUrl': 'http://localhost:8001',      # Data service
    'privacyServiceUrl': 'http://localhost:8002',   # Privacy service
    'blockchainServiceUrl': 'http://localhost:8003', # Blockchain audit service
    'auto_push_to_emr': True                        # Enable auto EMR integration
}
```

### Learning Configuration

The pipeline automatically configures:
- Daily analysis frequency
- Weekly retraining checks
- Monthly insight validation
- Performance monitoring windows
- Auto-retraining thresholds

## Data Models

The pipeline uses structured data models for:
- Patient profiles and treatment plans
- Prediction results and outcomes
- Learning insights and recommendations
- Model performance metrics

## Security & Compliance

- All data access is logged and audited
- Privacy controls are automatically applied
- Authentication is handled by Abena SDK
- Data encryption is managed centrally
- HIPAA compliance is maintained through Abena SDK

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please contact the development team or create an issue in the repository. 