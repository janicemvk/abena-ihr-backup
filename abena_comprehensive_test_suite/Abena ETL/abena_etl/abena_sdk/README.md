# Abena SDK - Universal Integration Pattern

The Abena SDK provides a standardized approach to healthcare data integration, analytics, and system interoperability. It implements the **Universal Integration Pattern** where all modules use centralized authentication, authorization, and data handling instead of implementing their own.

## 🎯 Universal Integration Pattern

### Before (❌ Wrong - Custom Implementation)
```python
class SomeModule:
    def __init__(self):
        # Custom database connection
        self.database = new Database();
        # Custom authentication
        self.authSystem = new CustomAuth();
    }
}
```

### After (✅ Correct - Abena SDK)
```python
from abena_sdk import AbenaClient

class SomeModule:
    def __init__(self):
        # Initialize Abena SDK (Universal Integration Pattern)
        self.abena = AbenaClient({
            'api_base_url': 'https://api.abena.com',
            'client_id': os.getenv('ABENA_CLIENT_ID'),
            'client_secret': os.getenv('ABENA_CLIENT_SECRET')
        })
    
    async def someMethod(self, patientId, userId):
        # 1. Auto-handled auth & permissions
        const patientData = await self.abena.getPatientData(patientId, userId, 'module_purpose');
        
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        
        # 4. Focus on your business logic
        return self.processData(patientData);
    }
}
```

## 🚀 Quick Start

### 1. Installation
```bash
pip install abena-sdk
```

### 2. Environment Setup
```bash
# Set your Abena SDK credentials
export ABENA_API_BASE_URL="https://api.abena.com"
export ABENA_CLIENT_ID="your-client-id"
export ABENA_CLIENT_SECRET="your-client-secret"
export ABENA_FHIR_VERSION="R4"
```

### 3. Basic Usage
```python
from abena_sdk import AbenaClient

# Initialize the SDK
client = AbenaClient()

# Get patient data (auto-handles auth, privacy, audit)
patient_data = client.get_patient_data(
    patient_id="PATIENT_123",
    user_id="DR_SMITH",
    purpose="clinical_decision_support"
)

# Get predictions (auto-handles auth, audit)
prediction = client.get_prediction(
    patient_id="PATIENT_123",
    user_id="DR_SMITH",
    model_type="treatment_response",
    input_data={"condition": "diabetes"},
    purpose="treatment_planning"
)
```

## 📚 Core Components

### 1. AbenaClient
The main client that implements the Universal Integration Pattern.

```python
from abena_sdk import AbenaClient

client = AbenaClient({
    'api_base_url': 'https://api.abena.com',
    'client_id': 'your-client-id',
    'client_secret': 'your-client-secret'
})
```

### 2. Authentication & Authorization
Centralized authentication and authorization handling.

```python
# Authenticate
token = client.authenticate()

# Check permissions
has_permission = client.check_permission(
    user_id="DR_SMITH",
    permission="read:patient",
    resource_id="PATIENT_123"
)

# Get user permissions
permissions = client.get_user_permissions("DR_SMITH")
```

### 3. Data Access
Universal data access with automatic privacy and audit handling.

```python
# Get patient data
patient_data = client.get_patient_data(
    patient_id="PATIENT_123",
    user_id="DR_SMITH",
    purpose="clinical_decision_support",
    scope="vitals"
)

# Get observations
observations = client.get_observation_data(
    patient_id="PATIENT_123",
    user_id="DR_SMITH",
    observation_type="glucose"
)
```

### 4. Analytics & Predictions
Centralized analytics and prediction engine.

```python
# Get predictions
prediction = client.get_prediction(
    patient_id="PATIENT_123",
    user_id="DR_SMITH",
    model_type="treatment_response",
    input_data={"condition": "diabetes"},
    purpose="treatment_planning"
)

# Get treatment recommendations
recommendations = client.get_treatment_recommendations(
    patient_id="PATIENT_123",
    user_id="DR_SMITH",
    condition="diabetes"
)

# Get patient insights
insights = client.get_patient_insights(
    patient_id="PATIENT_123",
    user_id="DR_SMITH"
)
```

### 5. Data Transformation
Universal data transformation and FHIR conversion.

```python
# Transform EMR data
transformed_data = client.transform_emr_data(
    source_data=emr_data,
    source_system="Epic",
    user_id="DR_SMITH",
    target_format="FHIR"
)

# Convert to FHIR
fhir_resource = client.convert_to_fhir(
    data=patient_data,
    resource_type="Patient",
    user_id="DR_SMITH"
)
```

## 🔄 Migration Guide

### Step 1: Identify Modules to Migrate
Run the migration helper to identify modules with custom auth/data handling:

```bash
python migrate_to_sdk.py
```

### Step 2: Update Imports
Replace custom imports with Abena SDK:

```python
# BEFORE
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import jwt
import redis
from custom_auth import CustomAuth

# AFTER
from abena_sdk import AbenaClient
import os
```

### Step 3: Update Constructor
Replace custom initialization with Abena SDK:

```python
# BEFORE
def __init__(self):
    self.engine = sqlalchemy.create_engine('postgresql://...')
    self.auth_system = CustomAuth()
    self.cache = redis.Redis()

# AFTER
def __init__(self):
    self.abena = AbenaClient({
        'api_base_url': 'https://api.abena.com',
        'client_id': os.getenv('ABENA_CLIENT_ID'),
        'client_secret': os.getenv('ABENA_CLIENT_SECRET')
    })
```

### Step 4: Replace Data Access Methods
Replace custom data access with SDK methods:

```python
# BEFORE
def get_patient_data(self, patient_id):
    if not self.auth_system.check_permission(user_id, 'read:patient'):
        raise PermissionError()
    session = self.Session()
    patient = session.query(Patient).filter_by(id=patient_id).first()
    session.close()
    return patient

# AFTER
def get_patient_data(self, patient_id, user_id):
    patient_data = self.abena.get_patient_data(patient_id, user_id, 'module_purpose')
    return patient_data.data
```

## 🛡️ Security Features

### Automatic Authentication
- Client credentials flow
- Token refresh handling
- Secure credential management

### Automatic Authorization
- Role-based access control
- Resource-level permissions
- Permission caching

### Privacy & Encryption
- Automatic data encryption
- Privacy compliance (HIPAA, GDPR)
- Secure data transmission

### Audit Logging
- Automatic audit trail
- Access logging
- Compliance reporting

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
ABENA_API_BASE_URL=https://api.abena.com
ABENA_API_VERSION=v1
ABENA_TIMEOUT=30

# Authentication
ABENA_CLIENT_ID=your-client-id
ABENA_CLIENT_SECRET=your-client-secret
ABENA_ACCESS_TOKEN=your-access-token

# FHIR Configuration
ABENA_FHIR_VERSION=R4

# Analytics Configuration
ABENA_ANALYTICS_ENABLED=true
ABENA_PREDICTION_CONFIDENCE_THRESHOLD=0.6

# Cache Configuration
ABENA_CACHE_ENABLED=true
ABENA_CACHE_TTL=3600

# Logging Configuration
ABENA_LOG_LEVEL=INFO
ABENA_LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Configuration Object
```python
from abena_sdk import AbenaConfig

config = AbenaConfig(
    api_base_url="https://api.abena.com",
    client_id="your-client-id",
    client_secret="your-client-secret",
    fhir_version="R4",
    analytics_enabled=True
)

client = AbenaClient(config)
```

## 📊 Error Handling

The SDK provides comprehensive error handling with custom exceptions:

```python
from abena_sdk import (
    AbenaException, AuthenticationError, AuthorizationError,
    DataTransformationError, FHIRConversionError, AnalyticsError
)

try:
    patient_data = client.get_patient_data("PATIENT_123", "DR_SMITH")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except AuthorizationError as e:
    print(f"Authorization failed: {e}")
except AbenaException as e:
    print(f"SDK error: {e}")
```

## 🧪 Testing

### Unit Testing
```python
import pytest
from unittest.mock import Mock, patch
from abena_sdk import AbenaClient

def test_get_patient_data():
    with patch('abena_sdk.requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "data": {"patient_id": "123", "name": "John Doe"}
        }
        mock_post.return_value.raise_for_status.return_value = None
        
        client = AbenaClient()
        result = client.get_patient_data("123", "DR_SMITH", "test")
        
        assert result.data["patient_id"] == "123"
```

### Integration Testing
```python
def test_integration():
    client = AbenaClient()
    
    # Test authentication
    token = client.authenticate()
    assert token.access_token is not None
    
    # Test data access
    patient_data = client.get_patient_data("TEST_PATIENT", "TEST_USER", "test")
    assert patient_data is not None
```

## 📈 Benefits

### For Developers
- **Focus on Business Logic**: No need to implement auth, data handling, or privacy
- **Consistent API**: Standardized interface across all modules
- **Reduced Complexity**: Less boilerplate code
- **Better Testing**: Centralized components are easier to test

### For Organizations
- **Security**: Centralized security controls
- **Compliance**: Built-in privacy and audit features
- **Maintainability**: Single source of truth for auth and data
- **Scalability**: Optimized caching and performance

### For Healthcare
- **Interoperability**: FHIR-compliant data exchange
- **Privacy**: HIPAA and GDPR compliance
- **Audit Trail**: Complete access logging
- **Clinical Decision Support**: Integrated analytics

## 🤝 Contributing

1. Follow the Universal Integration Pattern
2. Use the Abena SDK for all auth, data, and analytics operations
3. Write comprehensive tests
4. Update documentation

## 📄 License

This SDK is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

For support and questions:
- Documentation: [docs.abena.com](https://docs.abena.com)
- Issues: [GitHub Issues](https://github.com/abena/sdk/issues)
- Email: support@abena.com 