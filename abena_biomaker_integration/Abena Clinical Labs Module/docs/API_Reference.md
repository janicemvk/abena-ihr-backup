# ECS Analyzer API Reference

## Overview

The ECS Analyzer module provides comprehensive analysis of Endocannabinoid System (ECS) health through laboratory data, smart device metrics, and clinical assessments.

## Core Classes

### ECSAnalyzer

The main analysis engine that processes patient data and generates comprehensive health reports.

#### Constructor
```python
ECSAnalyzer()
```

#### Methods

##### load_test_patient_data(scenario: str) -> None
Loads simulated patient data for testing and demonstration.

**Parameters:**
- `scenario` (str): Patient scenario to load
  - `"healthy_baseline"`: Optimal ECS function
  - `"mild_dysfunction"`: Early ECS imbalance
  - `"moderate_dysfunction"`: Clear ECS deficiency
  - `"severe_dysfunction"`: Multiple system involvement
  - `"mixed_patterns"`: Complex multi-factor dysfunction

**Example:**
```python
analyzer = ECSAnalyzer()
analyzer.load_test_patient_data("moderate_dysfunction")
```

##### calculate_ecs_score() -> Dict[str, Any]
Calculates comprehensive ECS dysfunction score and classification.

**Returns:**
```python
{
    'total_score': float,           # Overall ECS score (0-100)
    'classification': str,          # Dysfunction classification
    'severity': str,               # Severity level
    'category_scores': dict,       # Individual category scores
    'weights': dict               # Scoring weights used
}
```

**Example:**
```python
score = analyzer.calculate_ecs_score()
print(f"ECS Score: {score['total_score']}")
print(f"Classification: {score['classification']}")
```

##### analyze_correlations() -> Dict[str, float]
Analyzes correlations between different health metrics.

**Returns:**
```python
{
    'hrv_sleep': float,      # HRV vs Sleep Quality correlation
    'stress_sleep': float    # Stress vs Sleep Quality correlation
}
```

##### create_radar_chart() -> str
Generates radar chart showing ECS component breakdown.

**Returns:** HTML string containing Plotly radar chart

##### create_biomarker_chart() -> str
Generates bar chart of key biomarkers with color coding.

**Returns:** HTML string containing Plotly bar chart

##### create_temporal_analysis() -> str
Generates multi-panel time series of 30-day health trends.

**Returns:** HTML string containing Plotly subplot charts

##### create_correlation_heatmap() -> str
Generates correlation matrix heatmap.

**Returns:** HTML string containing Plotly heatmap

##### generate_recommendations() -> Dict[str, List[str]]
Generates personalized treatment recommendations.

**Returns:**
```python
{
    'supplements': List[str],      # Supplement recommendations
    'lifestyle': List[str],        # Lifestyle modifications
    'dietary': List[str],          # Dietary recommendations
    'monitoring': List[str]        # Monitoring protocols
}
```

##### create_html_report() -> str
Generates comprehensive HTML health report.

**Returns:** Complete HTML string with embedded charts and styling

## Data Classes

### PatientData
```python
@dataclass
class PatientData:
    patient_id: str
    name: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    bmi: float
    date_of_birth: datetime
    collection_date: datetime
```

### LabResult
```python
@dataclass
class LabResult:
    test_name: str
    value: float
    unit: str
    reference_low: float
    reference_high: float
    status: str  # 'normal', 'low', 'high', 'critical'
    date: datetime
    category: str  # ECS category
```

### VitalSign
```python
@dataclass
class VitalSign:
    measurement_type: str
    value: float
    unit: str
    date: datetime
    notes: str
```

### EKGResult
```python
@dataclass
class EKGResult:
    measurement_type: str
    value: float
    unit: str
    interpretation: str
    date: datetime
    notes: str
```

### SmartDeviceData
```python
@dataclass
class SmartDeviceData:
    device_type: str
    metric: str
    value: float
    unit: str
    timestamp: datetime
    quality_score: float
```

## Scoring System

### ECS Component Weights
- **Direct ECS Markers**: 40%
- **Inflammatory Markers**: 25%
- **Cardiovascular Markers**: 15%
- **Stress Markers**: 20%
- **Neurotransmitter Markers**: 15%

### Classification Ranges
- **Optimal ECS Function**: 0-20 points
- **Mild ECS Dysfunction**: 21-40 points
- **Moderate ECS Dysfunction**: 41-60 points
- **Severe ECS Dysfunction**: 61-100 points

## Biomarker Categories

### Direct ECS Markers
- Anandamide (AEA)
- 2-Arachidonoylglycerol (2-AG)
- Fatty Acid Amide Hydrolase (FAAH) Activity

### Inflammatory Markers
- C-Reactive Protein (CRP)
- Erythrocyte Sedimentation Rate (ESR)
- Interleukin-6 (IL-6)
- Tumor Necrosis Factor-alpha (TNF-α)

### Cardiovascular Markers
- Homocysteine
- BUN/Creatinine Ratio
- Omega-6/Omega-3 Ratio

### Stress Markers
- Cortisol (Morning/Evening)
- Dehydroepiandrosterone Sulfate (DHEA-S)

### Neurotransmitter Markers
- Serotonin
- Gamma-Aminobutyric Acid (GABA)
- Dopamine

## Error Handling

The module includes comprehensive error handling for:
- Missing or invalid patient data
- Empty lab result sets
- Invalid biomarker values
- Chart generation failures
- File I/O operations

## Performance Characteristics

- **Report Generation**: <10 seconds
- **Memory Usage**: <100MB for typical patient data
- **Data Handling**: Supports 50+ lab results per patient
- **Chart Rendering**: All charts render in <2 seconds

## Usage Examples

### Basic Analysis
```python
from ecs_analyzer import ECSAnalyzer

# Initialize and load data
analyzer = ECSAnalyzer()
analyzer.load_test_patient_data("moderate_dysfunction")

# Calculate score
score = analyzer.calculate_ecs_score()
print(f"ECS Score: {score['total_score']}")

# Generate report
html_report = analyzer.create_html_report()
```

### Custom Analysis
```python
# Analyze correlations
correlations = analyzer.analyze_correlations()
print(f"HRV-Sleep correlation: {correlations.get('hrv_sleep', 0):.3f}")

# Generate recommendations
recommendations = analyzer.generate_recommendations()
for category, recs in recommendations.items():
    print(f"\n{category.title()}:")
    for rec in recs:
        print(f"  - {rec}")
```

### Chart Generation
```python
# Generate individual charts
radar_chart = analyzer.create_radar_chart()
biomarker_chart = analyzer.create_biomarker_chart()
temporal_chart = analyzer.create_temporal_analysis()
correlation_chart = analyzer.create_correlation_heatmap()
```

## Integration Notes

- All charts are generated as HTML strings with embedded Plotly
- Reports are self-contained with inline CSS and JavaScript
- No external dependencies required for report viewing
- Compatible with web browsers and PDF generation tools 