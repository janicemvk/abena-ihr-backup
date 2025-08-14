# Abena SDK Refactoring Guide

This document explains how to refactor your code to use the Abena SDK instead of implementing your own authentication and data access systems.

## Overview

The Abena SDK provides centralized access to:
- **Authentication & Authorization** - Automatic user permission checks
- **Data Access** - Secure patient data retrieval with privacy controls
- **Privacy & Encryption** - Automatic data encryption and privacy compliance
- **Audit Logging** - Comprehensive audit trails for compliance
- **Blockchain Verification** - Data integrity verification

## Before vs After Pattern

### ❌ WRONG - Has its own auth/data:

```python
class SomeModule:
    def __init__(self):
        # Custom database connection
        self.database = Database()
        
        # Custom authentication system
        self.auth_system = CustomAuth()
        
        # Custom encryption
        self.encryption = CustomEncryption()
        
        # Custom audit logging
        self.audit_logger = CustomAuditLogger()

    async def some_method(self, patient_id, user_id):
        # Manual authentication
        if not self.auth_system.authenticate(user_id):
            raise Exception("Authentication failed")
        
        # Manual permission check
        if not self.auth_system.check_permissions(user_id, patient_id, "read"):
            raise Exception("Insufficient permissions")
        
        # Manual data retrieval
        patient_data = self.database.get_patient_data(patient_id)
        
        # Manual encryption/decryption
        decrypted_data = self.encryption.decrypt(patient_data)
        
        # Manual audit logging
        self.audit_logger.log_access(user_id, patient_id, "read")
        
        # Business logic
        return self.process_data(decrypted_data)
```

### ✅ CORRECT - Uses Abena SDK:

```python
from src.abena_sdk import AbenaSDK, AbenaSDKConfig

class SomeModule:
    def __init__(self):
        # Initialize Abena SDK for centralized services
        self.abena = AbenaSDK(AbenaSDKConfig(
            auth_service_url='http://localhost:3001',
            data_service_url='http://localhost:8001',
            privacy_service_url='http://localhost:8002',
            blockchain_service_url='http://localhost:8003'
        ))

    async def some_method(self, patient_id, user_id):
        # 1. Auto-handled auth & permissions
        patient_data = await self.abena.get_patient_data(patient_id, 'module_purpose')
        
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        
        # 4. Focus on your business logic
        return self.process_data(patient_data)
```

## Key Benefits

### 1. **Simplified Code**
- No need to implement authentication, encryption, or audit logging
- Focus on business logic instead of infrastructure concerns
- Reduced code complexity and maintenance burden

### 2. **Centralized Security**
- All security logic handled by the Abena SDK
- Consistent security policies across all modules
- Automatic updates to security features

### 3. **Compliance Ready**
- Built-in audit logging for regulatory compliance
- Automatic privacy controls (HIPAA, GDPR, etc.)
- Blockchain verification for data integrity

### 4. **Better Performance**
- Connection pooling and caching
- Optimized data access patterns
- Reduced network overhead

## Refactored Modules

The following modules have been completely refactored to use the Abena SDK:

### 1. OutcomeCollectionService (`src/clinical_outcomes/data_collection.py`)
**Before:** Had its own database connections, in-memory storage, and authentication logic
**After:** Uses Abena SDK for all data access and security

```python
# Before
def __init__(self):
    self.outcome_records = {}  # In-memory storage
    self.collection_schedules = {}
    # Custom database connections
    # Custom authentication logic

# After
def __init__(self):
    self.abena = AbenaSDK(AbenaSDKConfig(...))
    self.collection_schedules = {}  # Still needed for business logic
```

### 2. APIGateway (`API Gateway and External Connectors System/api_gateway.py`)
**Before:** Custom JWT authentication, API key management, database models, and permission checking
**After:** Delegates all security to Abena SDK

```python
# Before
class APIKey(Base):
    __tablename__ = 'api_keys'
    # Custom database models

async def verify_api_key(self, authorization):
    # Custom JWT validation
    # Custom rate limiting
    # Custom permission checking

# After
async def verify_user_permissions(self, user_id, patient_id, action):
    return await self.abena.check_permissions(user_id, patient_id, action)
```

### 3. IntelligenceLayer (`Intel layer Monitoring, Alert and DQA/main_orchestrator.py`)
**Before:** Direct database and Redis connections, custom data access
**After:** Uses Abena SDK for all data operations

```python
# Before
def __init__(self, db_url, redis_url):
    self.engine = create_engine(db_url)
    self.redis_client = redis.from_url(redis_url)
    # Custom database queries

# After
def __init__(self):
    self.abena = AbenaSDK(AbenaSDKConfig(...))
```

## Removed Dependencies

The following dependencies have been removed as they're no longer needed:

### Removed from `requirements.txt`:
- `psycopg2==2.9.9` - No longer using direct PostgreSQL connections
- `sqlalchemy` - No longer using ORM for database access
- `cryptography` - Encryption handled by Abena SDK

### Kept in `requirements.txt`:
- `httpx==0.27.0` - Required for Abena SDK HTTP client
- `redis==5.0.1` - Still needed for rate limiting and caching
- `python-jose[cryptography]==3.3.0` - Still needed for JWT handling
- `fastapi==0.110.2` - Web framework
- `uvicorn==0.29.0` - ASGI server
- `python-dotenv==1.0.0` - Environment configuration

## Example Module

See `src/example_module.py` for a complete example of how to use the Abena SDK:

```python
class ExampleModule:
    def __init__(self):
        self.abena = AbenaSDK(AbenaSDKConfig(...))
    
    async def some_method(self, patient_id, user_id):
        # 1. Auto-handled auth & permissions
        patient_data = await self.abena.get_patient_data(patient_id, 'module_purpose')
        
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        
        # 4. Focus on your business logic
        return self.process_data(patient_data)
```

## Migration Steps

1. **Add Abena SDK dependency**
   ```bash
   pip install httpx==0.27.0
   ```

2. **Import Abena SDK**
   ```python
   from src.abena_sdk import AbenaSDK, AbenaSDKConfig
   ```

3. **Initialize SDK in constructor**
   ```python
   def __init__(self):
       self.abena = AbenaSDK(AbenaSDKConfig(...))
   ```

4. **Replace custom auth/data logic**
   - Replace `self.database.get_data()` with `await self.abena.get_patient_data()`
   - Replace `self.auth.check_permissions()` with `await self.abena.check_permissions()`
   - Remove custom encryption/audit code
   - Remove database models and connections

5. **Update method signatures**
   - Make methods `async` where they use Abena SDK
   - Update callers to use `await`

6. **Remove unused dependencies**
   - Remove database drivers (psycopg2, sqlalchemy)
   - Remove custom encryption libraries
   - Keep only Abena SDK dependencies

## Configuration

The Abena SDK requires configuration for the service endpoints:

```python
AbenaSDKConfig(
    auth_service_url='http://localhost:3001',
    data_service_url='http://localhost:8001',
    privacy_service_url='http://localhost:8002',
    blockchain_service_url='http://localhost:8003'
)
```

## Best Practices

1. **Always use async/await** when calling Abena SDK methods
2. **Handle exceptions** from SDK calls appropriately
3. **Use meaningful purposes** when calling `get_patient_data()` (e.g., 'clinical_assessment', 'research')
4. **Don't store sensitive data** in memory - let the SDK handle it
5. **Focus on business logic** - let the SDK handle infrastructure concerns
6. **Remove all custom authentication code** - rely entirely on Abena SDK
7. **Remove all custom database connections** - use Abena SDK data access

## Testing

When testing modules that use the Abena SDK:

1. **Mock the SDK** for unit tests
2. **Use test configuration** for integration tests
3. **Verify business logic** without testing SDK functionality
4. **Test error handling** for SDK failures

## Support

For questions about the Abena SDK integration:
- Check the example module in `src/example_module.py`
- Review the SDK implementation in `src/abena_sdk.py`
- Consult the API documentation for available methods

## Complete Refactoring Status

✅ **OutcomeCollectionService** - Fully refactored to use Abena SDK
✅ **APIGateway** - Fully refactored to use Abena SDK  
✅ **IntelligenceLayer** - Fully refactored to use Abena SDK
✅ **Dependencies** - Cleaned up to remove unused packages
✅ **Documentation** - Updated to reflect complete refactoring

All modules now use the Abena SDK pattern:
1. Auto-handled auth & permissions
2. Auto-handled privacy & encryption
3. Auto-handled audit logging
4. Focus on business logic 