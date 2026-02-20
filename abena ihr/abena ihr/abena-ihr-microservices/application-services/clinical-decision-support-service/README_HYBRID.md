# Abena IHR Enhanced Clinical Decision Support - Hybrid Architecture

## Overview

This enhanced clinical decision support system combines the best of both worlds:
- **TypeScript Reasoning Engine**: Advanced clinical context analysis, risk stratification, and trajectory prediction
- **Python Service Layer**: FastAPI-based RESTful API with comprehensive decision support capabilities

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enhanced Clinical Decision Support           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Python API    │    │ TypeScript      │                    │
│  │   Service       │◄──►│ Reasoning       │                    │
│  │   Layer         │    │ Engine          │                    │
│  └─────────────────┘    └─────────────────┘                    │
│           │                       │                            │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   FastAPI       │    │ Advanced        │                    │
│  │   Endpoints     │    │ Context         │                    │
│  │   & Models      │    │ Analysis        │                    │
│  └─────────────────┘    └─────────────────┘                    │
│           │                       │                            │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Clinical      │    │ Risk            │                    │
│  │   Decisions     │    │ Stratification  │                    │
│  │   & Rules       │    │ & Trajectory    │                    │
│  └─────────────────┘    │ Prediction      │                    │
│                         └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### 🔄 Hybrid Engine Integration
- **Seamless Integration**: Python service calls TypeScript reasoning engine via HTTP
- **Fallback Mechanism**: Graceful degradation to Python-only analysis if TypeScript engine is unavailable
- **Data Transformation**: Automatic conversion between Python and TypeScript data formats

### 🧠 Advanced Clinical Reasoning
- **Comprehensive Context Analysis**: Multi-dimensional patient context evaluation
- **Risk Stratification**: Advanced risk factor identification and categorization
- **Clinical Trajectory Prediction**: Future clinical scenarios and intervention points
- **Contextual Insights**: Actionable insights based on environmental and social factors

### 🚀 Enhanced API Capabilities
- **New Decision Types**: Contextual analysis and trajectory prediction endpoints
- **Enhanced Models**: Extended patient context with environmental and social factors
- **Comprehensive Responses**: Rich decision objects with contextual analysis and insights

## Components

### 1. TypeScript Reasoning Engine (`shared-libraries/clinical-reasoning-engine/`)

**Purpose**: Advanced clinical reasoning and context analysis

**Key Features**:
- Comprehensive clinical context interfaces
- Advanced risk stratification algorithms
- Clinical trajectory prediction
- Contextual insights generation
- Evidence-based recommendation engine

**Core Interfaces**:
```typescript
interface ClinicalContext {
  patientId: string;
  clinicalSituation: ClinicalSituation;
  patientState: PatientState;
  environmentalFactors: EnvironmentalFactors;
  temporalContext: TemporalContext;
  socialContext: SocialContext;
  riskFactors: RiskFactor[];
  contextualRelevance: number;
  confidenceLevel: number;
}
```

### 2. Enhanced Python Service (`application-services/clinical-decision-support-service/`)

**Purpose**: API service layer with hybrid engine integration

**Key Features**:
- FastAPI-based RESTful API
- Hybrid analysis combining Python and TypeScript engines
- Enhanced decision generation
- Comprehensive error handling and fallback mechanisms

**Enhanced Models**:
```python
class PatientContext(BaseModel):
    # Standard fields
    patient_id: str
    age: int
    gender: str
    # ... existing fields
    
    # Enhanced fields for advanced analysis
    environmental_factors: Optional[Dict[str, Any]] = {}
    temporal_context: Optional[Dict[str, Any]] = {}
    social_context: Optional[Dict[str, Any]] = {}
    psychological_state: Optional[Dict[str, Any]] = {}
    functional_status: Optional[Dict[str, Any]] = {}
```

## API Endpoints

### Core Endpoints

#### 1. Enhanced Context Analysis
```http
POST /analyze-context
Content-Type: application/json

{
  "patient_id": "PAT001",
  "age": 65,
  "gender": "male",
  "vital_signs": {
    "blood_pressure_systolic": 145,
    "heart_rate": 85
  },
  "environmental_factors": {
    "home_safety": "moderate",
    "social_support": "good"
  },
  "temporal_context": {
    "time_of_day": "morning",
    "season": "winter"
  }
}
```

#### 2. Enhanced Clinical Decision
```http
POST /clinical-decision
Content-Type: application/json

{
  "patient_context": { ... },
  "decision_type": "contextual_analysis",
  "clinical_question": "What contextual factors should be considered?",
  "include_contextual_analysis": true,
  "include_trajectory_prediction": true
}
```

#### 3. Contextual Analysis
```http
POST /contextual-analysis
Content-Type: application/json

{
  "patient_context": { ... },
  "analysis_depth": "comprehensive",
  "include_insights": true,
  "include_recommendations": true
}
```

#### 4. Trajectory Prediction
```http
POST /trajectory-prediction
Content-Type: application/json

{
  "patient_context": { ... },
  "time_horizon": "30d",
  "include_scenarios": true,
  "include_interventions": true
}
```

### New Decision Types

1. **`contextual_analysis`**: Deep contextual analysis using TypeScript engine
2. **`trajectory_prediction`**: Clinical trajectory prediction with scenarios

## Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Docker and Docker Compose

### 1. TypeScript Reasoning Engine

```bash
cd shared-libraries/clinical-reasoning-engine

# Install dependencies
npm install

# Build the engine
npm run build

# Start the engine service (optional - can be called directly)
npm run dev
```

### 2. Enhanced Python Service

```bash
cd application-services/clinical-decision-support-service

# Install dependencies
pip install -r requirements.txt

# Add httpx for HTTP client
pip install httpx

# Start the service
python src/enhanced_clinical_engine.py
```

### 3. Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: '3.8'

services:
  clinical-reasoning-engine:
    build: ./shared-libraries/clinical-reasoning-engine
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production

  enhanced-clinical-service:
    build: ./application-services/clinical-decision-support-service
    ports:
      - "8020:8020"
    environment:
      - REASONING_ENGINE_URL=http://clinical-reasoning-engine:3000
    depends_on:
      - clinical-reasoning-engine
```

## Usage Examples

### Basic Context Analysis

```python
import httpx
import asyncio

async def analyze_patient_context():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8020/analyze-context",
            json={
                "patient_id": "PAT001",
                "age": 65,
                "gender": "male",
                "vital_signs": {"blood_pressure_systolic": 145},
                "environmental_factors": {"home_safety": "moderate"}
            }
        )
        return response.json()

# Run analysis
result = asyncio.run(analyze_patient_context())
print(result)
```

### Advanced Clinical Decision

```python
async def get_clinical_decision():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8020/clinical-decision",
            json={
                "patient_context": {
                    "patient_id": "PAT001",
                    "age": 65,
                    "gender": "male",
                    "symptoms": ["chest_pain", "shortness_of_breath"]
                },
                "decision_type": "contextual_analysis",
                "clinical_question": "What contextual factors should be considered?",
                "include_contextual_analysis": True,
                "include_trajectory_prediction": True
            }
        )
        return response.json()

# Get decision
decision = asyncio.run(get_clinical_decision())
print(f"Recommendation: {decision['recommendation']}")
print(f"Confidence: {decision['confidence']}")
print(f"Contextual Insights: {len(decision['contextual_insights'])}")
```

## Benefits of Hybrid Approach

### 1. **Best of Both Worlds**
- **TypeScript**: Strong typing, advanced algorithms, sophisticated reasoning
- **Python**: FastAPI ecosystem, data science libraries, easy deployment

### 2. **Scalability**
- **Independent Scaling**: Scale TypeScript engine and Python service separately
- **Load Distribution**: Distribute computational load across different engines
- **Microservice Architecture**: Each component can be deployed independently

### 3. **Flexibility**
- **Fallback Mechanism**: Continue operation if one engine fails
- **Gradual Migration**: Migrate features from Python to TypeScript incrementally
- **Technology Choice**: Use best technology for each specific task

### 4. **Maintainability**
- **Clear Separation**: Distinct responsibilities for each component
- **Modular Design**: Easy to update or replace individual components
- **Testing**: Test each engine independently

## Performance Considerations

### 1. **Latency Management**
- **HTTP Overhead**: TypeScript engine calls add ~10-50ms latency
- **Caching**: Implement Redis caching for frequently accessed analyses
- **Async Processing**: Use background tasks for non-critical analyses

### 2. **Error Handling**
- **Graceful Degradation**: Fallback to Python-only analysis if TypeScript engine fails
- **Circuit Breaker**: Implement circuit breaker pattern for TypeScript engine calls
- **Retry Logic**: Automatic retry for transient failures

### 3. **Monitoring**
- **Health Checks**: Monitor both engines independently
- **Performance Metrics**: Track response times and success rates
- **Error Tracking**: Log and alert on engine failures

## Development Workflow

### 1. **Local Development**
```bash
# Terminal 1: TypeScript Engine
cd shared-libraries/clinical-reasoning-engine
npm run dev

# Terminal 2: Python Service
cd application-services/clinical-decision-support-service
python src/enhanced_clinical_engine.py
```

### 2. **Testing**
```bash
# Test TypeScript Engine
cd shared-libraries/clinical-reasoning-engine
npm test

# Test Python Service
cd application-services/clinical-decision-support-service
pytest tests/
```

### 3. **Integration Testing**
```bash
# Test hybrid functionality
python -m pytest tests/test_hybrid_integration.py
```

## Future Enhancements

### 1. **Real-time Collaboration**
- WebSocket integration for real-time clinical decision updates
- Collaborative decision-making interfaces

### 2. **Machine Learning Integration**
- ML model integration in TypeScript engine
- Predictive analytics for clinical outcomes

### 3. **Advanced Analytics**
- Clinical pathway optimization
- Resource utilization analytics
- Quality metrics and benchmarking

### 4. **Interoperability**
- FHIR integration for standardized data exchange
- HL7 integration for legacy system compatibility

## Troubleshooting

### Common Issues

1. **TypeScript Engine Unavailable**
   - Check if engine is running on port 3000
   - Verify network connectivity
   - Check engine logs for errors

2. **Data Format Mismatch**
   - Verify data transformation between Python and TypeScript
   - Check field naming conventions
   - Validate data types

3. **Performance Issues**
   - Monitor response times
   - Check resource utilization
   - Implement caching strategies

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export REASONING_ENGINE_DEBUG=true

# Start services with debug output
python src/enhanced_clinical_engine.py --debug
```

## Contributing

1. **TypeScript Engine**: Add new interfaces and algorithms in `shared-libraries/clinical-reasoning-engine/`
2. **Python Service**: Enhance API endpoints and models in `application-services/clinical-decision-support-service/`
3. **Integration**: Update data transformation and error handling logic
4. **Testing**: Add comprehensive tests for both engines and integration

## Support

For technical support and questions:
- Review the troubleshooting guide
- Check service logs and health endpoints
- Contact the development team
- Create an issue in the repository

---

This hybrid architecture provides a powerful, scalable, and maintainable solution for advanced clinical decision support, combining the strengths of both TypeScript and Python ecosystems. 