# Quantum Healthcare Integration Plan

**Date:** December 5, 2025  
**Status:** 📋 Planning Phase  
**Priority:** HIGH  
**Estimated Time:** 4-6 hours

---

## 📋 Executive Summary

This document outlines the step-by-step integration of the **Quantum Healthcare Service** into the ABENA ecosystem. The quantum system has its own command center/dashboard but needs to be connected to other ABENA services for data exchange, authentication, and result storage.

**Key Integration Points:**
- ✅ Connect to ABENA IHR Core (patient data)
- ✅ Integrate with eCDome Intelligence (biomarker data)
- ✅ Connect to Provider Dashboard (display results)
- ✅ Add to API Gateway (routing)
- ✅ Secure with ABENA Authentication (JWT)
- ✅ Store results in PostgreSQL database
- ✅ Enable cross-service communication

---

## 🏗️ Architecture Overview

### Current System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  • Provider Dashboard (4009)                                │
│  • Patient Dashboard (4010)                                 │
│  • Admin Dashboard (8080)                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY (8081)                       │
│  Routes requests to appropriate services                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    CORE SERVICES LAYER                      │
│  • ABENA IHR (4002) - Patient records                       │
│  • eCDome Intelligence (4005) - Biomarker analysis          │
│  • Auth Service (3001) - Authentication                     │
│  • Quantum Healthcare (5000) ← NEW INTEGRATION             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
│  • PostgreSQL (5433) - All data storage                     │
│  • Redis (6379) - Caching                                  │
└─────────────────────────────────────────────────────────────┘
```

### Quantum Healthcare Position

The Quantum Healthcare service sits in the **Core Services Layer** and:
- **Receives:** Patient data from ABENA IHR, biomarker data from eCDome
- **Processes:** Quantum circuit-based analysis
- **Sends:** Analysis results to Provider Dashboard, stores in database
- **Accesses:** Via API Gateway or direct service-to-service calls

---

## 📝 Integration Steps

### Phase 1: Docker & Infrastructure Setup

#### Step 1.1: Add Quantum Healthcare to Docker Compose
**File:** `docker-compose.yml`  
**Action:** Add quantum-healthcare service definition

**Location:** After eCDome Intelligence service (around line 254)

**Configuration:**
```yaml
  # Quantum Healthcare Service
  quantum-healthcare:
    build:
      context: ./quantum-healthcare
      dockerfile: Dockerfile
    container_name: abena-quantum-healthcare
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=production
      - PORT=5000
      - ABENA_IHR_API=http://abena-ihr:4002
      - ECDOME_API=http://ecdome-intelligence:4005
      - AUTH_SERVICE_URL=http://auth-service:3001
      - DATABASE_URL=postgresql://abena_user:abena_password@postgres:5432/abena_ihr
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-abena-super-secret-jwt-key-2024}
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - redis
      - auth-service
      - abena-ihr
      - ecdome-intelligence
    networks:
      - abena-network
    volumes:
      - ./quantum-healthcare:/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/demo-results"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Dependencies:**
- ✅ PostgreSQL (for storing quantum analysis results)
- ✅ Redis (for caching quantum computations)
- ✅ Auth Service (for JWT validation)
- ✅ ABENA IHR (for patient data)
- ✅ eCDome Intelligence (for biomarker data)

---

#### Step 1.2: Update API Gateway Routing
**File:** `api_gateway/nginx.conf` or `api_gateway/api gateway/API Gateway and External Connectors System/api_gateway.py`  
**Action:** Add quantum healthcare routes

**For Nginx Configuration:**
```nginx
# Quantum Healthcare Service routes
location /quantum/ {
    limit_req zone=api burst=10 nodelay;
    
    # JWT token validation
    auth_request /auth/validate;
    
    proxy_pass http://quantum-healthcare:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Extended timeout for quantum computations
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

**For Python API Gateway:**
```python
# Add quantum healthcare routes
@app.get("/quantum/demo-results")
async def quantum_demo():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://quantum-healthcare:5000/api/demo-results")
        return response.json()

@app.post("/quantum/analyze")
async def quantum_analyze(request: Request, current_user: dict = Depends(get_current_user_secure)):
    data = await request.json()
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://quantum-healthcare:5000/api/analyze",
            json=data,
            headers={"Authorization": request.headers.get("Authorization")}
        )
        return response.json()
```

---

#### Step 1.3: Update Port Documentation
**File:** `ABENA_SYSTEM_PORTS_DOCUMENTATION.md`  
**Action:** Add quantum healthcare service entry

**Add to Core Services Layer section:**
```markdown
| Quantum Healthcare | `abena-quantum-healthcare` | `5000` | `5000` | Quantum Analysis | ⏳ Pending |
```

**Add to Key Access URLs:**
```markdown
- **Quantum Healthcare Dashboard**: http://localhost:5000
- **Quantum Healthcare API**: http://localhost:5000/api
```

---

### Phase 2: Database Integration

#### Step 2.1: Create Quantum Analysis Tables
**File:** Create `quantum-healthcare/database/schema.sql`  
**Action:** Define database schema for storing quantum analysis results

**Schema:**
```sql
-- Quantum Analysis Results Table
CREATE TABLE IF NOT EXISTS quantum_analysis_results (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantum_health_score DECIMAL(5,2),
    system_balance DECIMAL(5,2),
    analysis_data JSONB,
    drug_interactions JSONB,
    herbal_recommendations JSONB,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Quantum Analysis History (for tracking)
CREATE TABLE IF NOT EXISTS quantum_analysis_history (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    analysis_id INTEGER REFERENCES quantum_analysis_results(id),
    analysis_type VARCHAR(50),
    status VARCHAR(20),
    error_message TEXT,
    computation_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_quantum_patient_id ON quantum_analysis_results(patient_id);
CREATE INDEX idx_quantum_timestamp ON quantum_analysis_results(analysis_timestamp);
CREATE INDEX idx_quantum_history_patient ON quantum_analysis_history(patient_id);
```

**Migration Script:** Create `quantum-healthcare/database/migrate.sql` and add to docker-compose init scripts

---

#### Step 2.2: Update Docker Compose Database Init
**File:** `docker-compose.yml` (postgres service)  
**Action:** Add quantum schema SQL to initialization

```yaml
volumes:
  - ./quantum-healthcare/database/schema.sql:/docker-entrypoint-initdb.d/06-quantum-schema.sql
```

---

### Phase 3: Authentication & Security Integration

#### Step 3.1: Add JWT Authentication to Quantum Service
**File:** `quantum-healthcare/app.py` (or create `quantum-healthcare/auth.py`)  
**Action:** Integrate ABENA security package for JWT validation

**Add to requirements.txt:**
```txt
python-jose[cryptography]==3.3.0
httpx==0.25.0
```

**Add authentication middleware:**
```python
from jose import JWTError, jwt
from functools import wraps
from flask import request, jsonify
import os
import httpx

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token with auth service"""
    auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:3001')
    
    try:
        # Option 1: Verify locally with shared secret
        secret_key = os.getenv('JWT_SECRET_KEY')
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
        
        # Option 2: Verify via auth service (more secure)
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"{auth_service_url}/auth/validate",
        #         headers={"Authorization": f"Bearer {token}"}
        #     )
        #     if response.status_code == 200:
        #         return response.json()
    except JWTError:
        return None

def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        user_data = verify_jwt_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user data to request context
        request.current_user = user_data
        return f(*args, **kwargs)
    
    return decorated_function

# Apply to protected endpoints
@app.post('/api/analyze')
@require_auth
def analyze():
    # ... existing code
    pass
```

---

#### Step 3.2: Add Rate Limiting
**File:** `quantum-healthcare/app.py`  
**Action:** Add Redis-based rate limiting

**Add to requirements.txt:**
```txt
redis==5.0.0
```

**Add rate limiting:**
```python
import redis
from functools import wraps
from flask import request, jsonify

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))

def rate_limit(max_requests=10, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user ID from token or IP
            user_id = getattr(request, 'current_user', {}).get('user_id', request.remote_addr)
            key = f"rate_limit:quantum:{user_id}"
            
            current = redis_client.incr(key)
            if current == 1:
                redis_client.expire(key, window)
            
            if current > max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': redis_client.ttl(key)
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Apply to endpoints
@app.post('/api/analyze')
@require_auth
@rate_limit(max_requests=5, window=300)  # 5 requests per 5 minutes
def analyze():
    # ... existing code
    pass
```

---

### Phase 4: Service Integration

#### Step 4.1: Create ABENA IHR Client
**File:** `quantum-healthcare/services/abena_ihr_client.py`  
**Action:** Create client to fetch patient data from ABENA IHR

```python
import httpx
import os
from typing import Optional, Dict, Any

class AbenaIHRClient:
    def __init__(self):
        self.base_url = os.getenv('ABENA_IHR_API', 'http://abena-ihr:4002')
        self.timeout = 30.0
    
    async def get_patient_data(self, patient_id: str, token: str) -> Optional[Dict[str, Any]]:
        """Fetch patient data from ABENA IHR"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/patients/{patient_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error fetching patient data: {e}")
                return None
    
    async def get_patient_prescriptions(self, patient_id: str, token: str) -> list:
        """Fetch patient prescriptions"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/prescriptions",
                    params={"patient_id": patient_id},
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    return response.json()
                return []
            except Exception as e:
                print(f"Error fetching prescriptions: {e}")
                return []
```

---

#### Step 4.2: Create eCDome Intelligence Client
**File:** `quantum-healthcare/services/ecdome_client.py`  
**Action:** Create client to fetch biomarker data from eCDome

```python
import httpx
import os
from typing import Optional, Dict, Any

class ECDomeClient:
    def __init__(self):
        self.base_url = os.getenv('ECDOME_API', 'http://ecdome-intelligence:4005')
        self.timeout = 30.0
    
    async def get_biomarkers(self, patient_id: str, token: str) -> Optional[Dict[str, Any]]:
        """Fetch eCDome biomarker data"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/biomarkers/{patient_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error fetching biomarkers: {e}")
                return None
```

---

#### Step 4.3: Update Analyze Endpoint
**File:** `quantum-healthcare/app.py`  
**Action:** Integrate data fetching from ABENA IHR and eCDome

```python
from services.abena_ihr_client import AbenaIHRClient
from services.ecdome_client import ECDomeClient

ihr_client = AbenaIHRClient()
ecdome_client = ECDomeClient()

@app.post('/api/analyze')
@require_auth
@rate_limit(max_requests=5, window=300)
async def analyze():
    data = request.get_json()
    patient_id = data.get('patient_id')
    token = request.headers.get('Authorization', '').split(' ')[1]
    
    # Fetch patient data from ABENA IHR
    patient_data = await ihr_client.get_patient_data(patient_id, token)
    if not patient_data:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Fetch biomarker data from eCDome
    biomarkers = await ecdome_client.get_biomarkers(patient_id, token)
    
    # Fetch prescriptions
    prescriptions = await ihr_client.get_patient_prescriptions(patient_id, token)
    
    # Prepare quantum analysis input
    analysis_input = {
        'patient_id': patient_id,
        'symptoms': data.get('symptoms', []),
        'biomarkers': biomarkers or data.get('biomarkers', {}),
        'medications': [p.get('medication') for p in prescriptions],
        'recommended_herbs': data.get('recommended_herbs', [])
    }
    
    # Run quantum analysis
    results = run_quantum_analysis(analysis_input)
    
    # Store results in database
    store_analysis_results(patient_id, results, request.current_user.get('user_id'))
    
    return jsonify({
        'success': True,
        'results': results
    })
```

---

### Phase 5: Provider Dashboard Integration

#### Step 5.1: Add Quantum Results Display Component
**File:** Provider Dashboard (port 4009)  
**Action:** Add component to display quantum analysis results

**Create:** `ECDome material 3 folders/Provider interface eCDome Monitoring Dashboard/src/components/QuantumResults.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

const QuantumResults = ({ patientId }) => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    if (patientId) {
      fetchQuantumResults(patientId);
    }
  }, [patientId]);

  const fetchQuantumResults = async (patientId) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:5000/api/analyze`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ patient_id: patientId })
        }
      );
      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error('Error fetching quantum results:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading quantum analysis...</div>;
  if (!results) return null;

  return (
    <div className="quantum-results">
      <h3>Quantum Health Analysis</h3>
      <div className="score">
        <span>Quantum Health Score: {results.quantum_health_score}</span>
      </div>
      <div className="balance">
        <span>System Balance: {results.system_balance}</span>
      </div>
      {/* More results display */}
    </div>
  );
};

export default QuantumResults;
```

---

#### Step 5.2: Add API Gateway Route for Provider Dashboard
**File:** API Gateway configuration  
**Action:** Ensure provider dashboard can access quantum service

Already handled in Step 1.2, but verify CORS settings allow provider dashboard origin.

---

### Phase 6: Testing & Validation

#### Step 6.1: Create Integration Test Script
**File:** `quantum-healthcare/tests/test_integration.py`  
**Action:** Create tests for all integration points

```python
import pytest
import httpx
import asyncio

BASE_URL = "http://localhost:5000"
IHR_URL = "http://localhost:4002"
AUTH_URL = "http://localhost:3001"

@pytest.mark.asyncio
async def test_quantum_service_health():
    """Test quantum service is running"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/demo-results")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_quantum_analyze_with_auth():
    """Test quantum analysis with authentication"""
    # First, get auth token
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{AUTH_URL}/api/v1/auth/login",
            json={"email": "dr.johnson@abena.com", "password": "SecureP@ss123"}
        )
        token = login_response.json()["access_token"]
        
        # Then test quantum analysis
        analyze_response = await client.post(
            f"{BASE_URL}/api/analyze",
            json={"patient_id": "123"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert analyze_response.status_code == 200
        assert "results" in analyze_response.json()
```

---

#### Step 6.2: Create Manual Test Checklist
**File:** `QUANTUM_INTEGRATION_TEST_CHECKLIST.md`  
**Action:** Create checklist for manual testing

**Checklist:**
- [ ] Quantum service starts successfully
- [ ] Can access dashboard at "C:\Users\Jan Marie\Documents\Python Development Files\abena-backup"
- [ ] Can authenticate with JWT token
- [ ] Can fetch patient data from ABENA IHR
- [ ] Can fetch biomarker data from eCDome
- [ ] Can run quantum analysis
- [ ] Results stored in database
- [ ] Results displayed in Provider Dashboard
- [ ] Rate limiting works
- [ ] API Gateway routes correctly

---

### Phase 7: Documentation & Deployment

#### Step 7.1: Update Main Documentation
**File:** `COMPREHENSIVE_FOLDER_ANALYSIS.md`  
**Action:** Add quantum healthcare to system overview

#### Step 7.2: Create Quantum Healthcare API Documentation
**File:** `QUANTUM_HEALTHCARE_API_DOCUMENTATION.md`  
**Action:** Document all endpoints, authentication, and usage

#### Step 7.3: Update Integration Plan
**File:** `INTEGRATION_PLAN_QUANTUM_SECURITY.md`  
**Action:** Mark quantum integration as complete

---

## 🔄 Integration Flow Diagram

```
┌─────────────────┐
│ Provider        │
│ Dashboard       │
│ (4009)          │
└────────┬────────┘
         │
         │ 1. Request Analysis
         ↓
┌─────────────────┐
│ API Gateway      │
│ (8081)           │
└────────┬────────┘
         │
         │ 2. Route to Quantum
         ↓
┌─────────────────┐
│ Quantum         │
│ Healthcare      │
│ (5000)          │
└────────┬────────┘
         │
         ├─→ 3a. Fetch Patient Data
         │   └─→ ABENA IHR (4002)
         │
         ├─→ 3b. Fetch Biomarkers
         │   └─→ eCDome (4005)
         │
         ├─→ 4. Run Quantum Analysis
         │
         ├─→ 5. Store Results
         │   └─→ PostgreSQL (5433)
         │
         └─→ 6. Return Results
             └─→ Provider Dashboard
```

---

## ⚠️ Important Considerations

### 1. **Port Conflicts**
- ✅ Port 5000 is available (not used by other services)
- ⚠️ Ensure Flask default port doesn't conflict

### 2. **Performance**
- Quantum computations can take 10-30 seconds
- Set appropriate timeouts in API Gateway (60s)
- Consider async processing for long-running analyses

### 3. **Security**
- All endpoints must require JWT authentication
- Rate limiting is critical (quantum computations are expensive)
- Validate all inputs before processing

### 4. **Error Handling**
- Handle service unavailability gracefully
- Provide fallback when eCDome or ABENA IHR is down
- Log all errors for debugging

### 5. **Data Privacy**
- Quantum analysis results contain PHI (Protected Health Information)
- Ensure HIPAA compliance
- Encrypt sensitive data in transit and at rest

---

## 📋 Execution Order

**Recommended execution sequence:**

1. ✅ **Phase 1** - Docker & Infrastructure (Steps 1.1-1.3)
2. ✅ **Phase 2** - Database Integration (Steps 2.1-2.2)
3. ✅ **Phase 3** - Authentication & Security (Steps 3.1-3.2)
4. ✅ **Phase 4** - Service Integration (Steps 4.1-4.3)
5. ✅ **Phase 5** - Provider Dashboard (Steps 5.1-5.2)
6. ✅ **Phase 6** - Testing (Steps 6.1-6.2)
7. ✅ **Phase 7** - Documentation (Steps 7.1-7.3)

**Total Estimated Time:** 4-6 hours

---

## 🎯 Success Criteria

Integration is complete when:

- ✅ Quantum service runs in Docker container
- ✅ Accessible via API Gateway at `/quantum/*`
- ✅ Authenticates with ABENA JWT tokens
- ✅ Fetches data from ABENA IHR and eCDome
- ✅ Stores results in PostgreSQL
- ✅ Results displayed in Provider Dashboard
- ✅ Rate limiting active
- ✅ All tests passing
- ✅ Documentation complete

---

## 🆘 Troubleshooting

### Common Issues

1. **Service won't start**
   - Check Docker logs: `docker logs abena-quantum-healthcare`
   - Verify dependencies in requirements.txt
   - Check port 5000 availability

2. **Authentication fails**
   - Verify JWT_SECRET_KEY matches auth service
   - Check token format (Bearer <token>)
   - Verify auth service is running

3. **Can't connect to ABENA IHR**
   - Verify service name in docker network: `abena-ihr`
   - Check network: `docker network inspect abena-network`
   - Verify ABENA IHR is running: `docker ps | grep abena-ihr`

4. **Database connection fails**
   - Verify DATABASE_URL format
   - Check PostgreSQL is running
   - Verify network connectivity

---

**Last Updated:** December 5, 2025  
**Status:** Ready for Execution  
**Next Step:** Begin Phase 1 - Docker & Infrastructure Setup

