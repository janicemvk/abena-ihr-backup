# ABENA Quantum Healthcare Service

## 📋 Overview

The ABENA Quantum Healthcare Service provides quantum computing-based analysis for patient health data, integrated with the main ABENA IHR system.

## 🎯 Key Features

- **Quantum Analysis:** Uses quantum circuits for complex health data analysis
- **eCDome Integration:** Enhanced endocannabinoid system monitoring
- **Drug Interaction:** Quantum modeling of medication interactions
- **Herbal Medicine:** Compatibility analysis for herbal supplements
- **Blockchain Records:** Smart contract-backed quantum health records
- **REST API:** Easy integration with existing ABENA services

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask server
python app.py

# Access at http://localhost:5000
```

### Docker Deployment

```bash
# Build Docker image
docker build -t abena-quantum-healthcare .

# Run container
docker run -p 5000:5000 abena-quantum-healthcare

# Or use docker-compose (from main abena-backup directory)
docker-compose up quantum-healthcare
```

## 📡 API Endpoints

### GET /
Returns the quantum analysis dashboard

### GET /api/demo-results
Returns demo quantum analysis results
```json
{
  "patient_id": "DEMO_001",
  "quantum_health_score": 0.78,
  "system_balance": 0.65,
  "drug_interactions": [...],
  "recommendations": [...]
}
```

### POST /api/analyze
Analyze patient data with quantum circuits

**Request:**
```json
{
  "patient_id": "PAT_001",
  "symptoms": [1, 0, 1, 0, 1],
  "biomarkers": {
    "anandamide": 0.45,
    "2AG": 2.1,
    "cb1_density": 85,
    "cb2_activity": 78
  },
  "medications": ["sertraline", "metformin"],
  "recommended_herbs": ["ginseng", "turmeric"]
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "quantum_health_score": 0.78,
    "system_balance": 0.65,
    "analysis_timestamp": "2025-12-05T10:30:00Z",
    ...
  }
}
```

## 🔗 Integration with ABENA IHR

The quantum service is integrated with ABENA IHR through:

1. **API Gateway** (Port 8081) - Routes requests to quantum service
2. **ABENA IHR Core** (Port 4002) - Calls quantum analysis API
3. **eCDome Intelligence** (Port 4005) - Uses quantum-enhanced analysis
4. **Provider Dashboard** (Port 4009) - Displays quantum results

### Example Integration (Python/FastAPI)

```python
import httpx

class QuantumService:
    def __init__(self):
        self.quantum_url = "http://quantum-healthcare:5000"
    
    async def analyze_patient(self, patient_data):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.quantum_url}/api/analyze",
                json=patient_data,
                timeout=30.0
            )
            return response.json()
```

## 🧪 Testing

```bash
# Test demo endpoint
curl http://localhost:5000/api/demo-results

# Test analysis endpoint
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "TEST_001",
    "symptoms": [1, 0, 1],
    "biomarkers": {"anandamide": 0.45, "2AG": 2.1}
  }'
```

## 📊 Performance

- **Analysis Time:** < 30 seconds per patient
- **Memory Usage:** ~500MB
- **CPU Usage:** Moderate (quantum simulation)
- **Concurrent Requests:** Up to 10 simultaneous analyses

## ⚙️ Configuration

Environment variables:

```env
FLASK_APP=app.py
FLASK_ENV=production
PORT=5000
ABENA_IHR_API=http://abena-ihr:4002
AUTH_SERVICE_URL=http://auth-service:3001
DATABASE_URL=postgresql://user:pass@postgres:5432/abena_ihr
```

## 🔒 Security

- Integrates with ABENA authentication service
- JWT token validation for protected endpoints
- Rate limiting applied
- Input validation on all endpoints

## 📦 Dependencies

- Flask 2.3.3 - Web framework
- flask-cors 4.0.0 - CORS support
- numpy 1.24.3 - Numerical computing
- scipy 1.11.1 - Scientific computing
- qiskit 0.44.1 - Quantum computing framework
- matplotlib 3.7.2 - Visualization

## 🐛 Troubleshooting

### Common Issues

**1. Qiskit import error:**
```bash
pip install --upgrade qiskit
```

**2. Port 5000 already in use:**
```bash
# Find process
netstat -ano | findstr :5000
# Kill process or change PORT environment variable
```

**3. Quantum analysis timeout:**
- Increase timeout in client configuration
- Check quantum simulator resources
- Reduce analysis complexity

## 📚 Documentation

- **Integration Guide:** See `INTEGRATION_PLAN_QUANTUM_SECURITY.md` in main directory
- **API Documentation:** http://localhost:5000/api/docs (when running)
- **Quantum Analysis:** See `enhanced_quantum_analyzer.py` for implementation details

## 🆘 Support

For issues or questions:
- Check logs: `docker logs abena-quantum-healthcare`
- Review integration guide
- Contact: ABENA IHR support team

## 📝 Version

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** December 5, 2025

