# Abena IHR ECS Lab Analysis Module

A comprehensive Endocannabinoid System (ECS) analysis module for the Abena Intelligent Health Records (IHR) system. This module analyzes clinical laboratory data, smart device biometrics, and EKG results to assess ECS dysfunction and generate personalized health reports.

## Features

### 🔐 **Abena SDK Integration**
- **Authentication**: Secure user authentication using Abena SDK
- **Authorization**: Role-based access control for patient data
- **Data Handling**: Seamless integration with Abena IHR data systems
- **Standard Models**: Uses Abena SDK data models for consistency

### 📊 **Comprehensive Lab Analysis**
- **123 Lab Tests**: Complete blood count, metabolic panel, liver function, thyroid, hormones, and more
- **ECS-Specific Markers**: Direct ECS biomarkers (AEA, 2-AG, FAAH activity)
- **Inflammatory Markers**: CRP, ESR, IL-6, TNF-α analysis
- **Cardiovascular Health**: Homocysteine, lipid profiles, omega ratios
- **Stress Markers**: Cortisol, DHEA-S, adrenal function
- **Neurotransmitters**: Serotonin, GABA, dopamine levels

### 🧠 **ECS Scoring Algorithm**
- **Weighted Categories**: Direct ECS (40%), Inflammation (25%), Cardiovascular (15%), Stress (20%), Neurotransmitters (15%)
- **Dysfunction Classification**: Optimal, Mild, Moderate, Severe
- **Personalized Scoring**: Age, gender, and health status considerations

### 📈 **Advanced Visualizations**
- **Radar Charts**: ECS component breakdown
- **Biomarker Analysis**: Key marker visualization with color coding
- **Temporal Analysis**: 30-day health trends
- **Correlation Heatmaps**: ECS-health relationships
- **Interactive Charts**: Plotly-based interactive visualizations

### 💡 **Personalized Recommendations**
- **Supplementation**: Evidence-based supplement recommendations
- **Lifestyle Modifications**: Stress management, sleep optimization
- **Dietary Guidance**: Anti-inflammatory nutrition plans
- **Monitoring Protocols**: Follow-up testing schedules

### 📋 **Professional Reports**
- **Comprehensive HTML Reports**: 10-section detailed analysis
- **Clinical Decision Support**: Evidence-based recommendations
- **Patient Education**: Clear explanations and next steps
- **Professional Styling**: Medical-grade report formatting

## Installation

### Prerequisites
```bash
pip install pandas numpy plotly scipy
```

### Abena SDK Setup
```bash
# For production use with real Abena SDK
pip install abena-sdk

# For development/testing (uses mock SDK)
# No additional installation required - mock SDK included
```

## Quick Start

### Basic Usage
```python
from ecs_analyzer import ECSAnalyzer
from abena.sdk.config import AbenaConfig

# Initialize with Abena SDK
config = AbenaConfig()
analyzer = ECSAnalyzer(config)

# Authenticate
credentials = {
    "username": "your_username",
    "password": "your_password",
    "api_key": "your_api_key"
}
analyzer.authenticate(credentials)

# Load patient data
if analyzer.load_patient_data("PATIENT_ID"):
    # Calculate ECS score
    ecs_score = analyzer.calculate_ecs_score()
    print(f"ECS Score: {ecs_score['total_score']}")
    print(f"Classification: {ecs_score['classification']}")
    
    # Generate report
    html_report = analyzer.create_html_report()
    with open("ecs_report.html", "w") as f:
        f.write(html_report)
```

### Testing with Mock Data
```python
from ecs_analyzer import ECSAnalyzer
from abena_sdk_mock import AbenaConfig

# Initialize with mock SDK
config = AbenaConfig()
analyzer = ECSAnalyzer(config)

# Load test scenarios
scenarios = ["healthy_baseline", "mild_dysfunction", "moderate_dysfunction", "severe_dysfunction"]
for scenario in scenarios:
    analyzer.load_test_patient_data(scenario)
    ecs_score = analyzer.calculate_ecs_score()
    print(f"{scenario}: {ecs_score['total_score']} - {ecs_score['classification']}")
```

## API Reference

### Core Methods

#### `authenticate(credentials: Dict[str, str]) -> bool`
Authenticate with Abena IHR system using provided credentials.

#### `authorize_access(resource: str, action: str) -> bool`
Check if user has permission to perform action on resource.

#### `load_patient_data(patient_id: str) -> bool`
Load patient data from Abena IHR system using Abena SDK.

#### `calculate_ecs_score() -> Dict[str, Any]`
Calculate comprehensive ECS dysfunction score with category breakdown.

#### `generate_recommendations() -> Dict[str, List[str]]`
Generate personalized treatment recommendations based on ECS analysis.

#### `create_html_report() -> str`
Generate comprehensive HTML report with visualizations and recommendations.

### Visualization Methods

#### `create_radar_chart() -> str`
Create radar chart showing ECS component breakdown.

#### `create_biomarker_chart() -> str`
Create bar chart of key ECS-relevant biomarkers.

#### `create_temporal_analysis() -> str`
Create time series analysis of smart device data.

#### `create_correlation_heatmap() -> str`
Create correlation matrix of ECS-health relationships.

## Data Models

### Abena SDK Models
The module uses Abena SDK data models for consistency:

- `AbenaPatient`: Patient demographic and basic information
- `AbenaLabResult`: Laboratory test results with reference ranges
- `AbenaVitalSign`: Vital sign measurements
- `AbenaEKGResult`: EKG/ECG measurement results
- `AbenaSmartDeviceData`: Smart device biometric data

### Lab Test Categories
- **Direct ECS**: AEA, 2-AG, FAAH activity
- **Inflammation**: CRP, ESR, IL-6, TNF-α
- **Cardiovascular**: Homocysteine, lipid profiles
- **Stress**: Cortisol, DHEA-S, adrenal hormones
- **Neurotransmitters**: Serotonin, GABA, dopamine
- **CBC**: Complete blood count (13 tests)
- **Metabolic**: Comprehensive metabolic panel (16 tests)
- **Liver Function**: Complete liver panel (12 tests)
- **Thyroid**: Thyroid function tests (9 tests)
- **Micronutrients**: Vitamins and minerals (13 tests)
- **Sex Hormones**: Male and female hormone panels (15 tests)
- **Adrenal**: Adrenal gland hormones (11 tests)
- **Insulin Metabolism**: Glucose and insulin markers (10 tests)
- **Lung Function**: Pulmonary function tests (8 tests)

## Testing

### Run Test Suite
```bash
python test_ecs_analyzer.py
```

### Test Scenarios
- **Healthy Baseline**: Optimal ECS function
- **Mild Dysfunction**: Slight ECS impairment
- **Moderate Dysfunction**: Moderate ECS issues
- **Severe Dysfunction**: Significant ECS problems
- **Mixed Patterns**: Complex dysfunction patterns

### Test Coverage
- ✅ Abena SDK integration
- ✅ Authentication and authorization
- ✅ Data loading and processing
- ✅ ECS scoring algorithm
- ✅ Visualization generation
- ✅ Report creation
- ✅ Performance testing

## Security Features

### Authentication
- Secure credential validation
- Session token management
- Automatic token refresh

### Authorization
- Role-based access control
- Resource-level permissions
- Action-based authorization

### Data Protection
- Encrypted data transmission
- Secure data storage
- HIPAA compliance ready

## Clinical Applications

### Primary Use Cases
1. **Preventive Medicine**: Early detection of ECS dysfunction
2. **Chronic Disease Management**: Monitoring ECS in chronic conditions
3. **Wellness Optimization**: Personalized health optimization
4. **Research Applications**: Clinical research and data analysis

### Target Populations
- Adults seeking health optimization
- Patients with chronic inflammatory conditions
- Individuals with stress-related health issues
- Research participants in ECS studies

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Use mock SDK for development: `from abena_sdk_mock import *`
4. Run tests: `python test_ecs_analyzer.py`

### Code Standards
- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Add unit tests for new features
- Update documentation for API changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support or questions about the Abena SDK integration, please contact the Abena development team.

---

**Note**: This module is designed for educational and research purposes. All clinical recommendations should be reviewed by qualified healthcare providers before implementation. 