# main.py - Abena IHR Privacy & Security Service
import asyncio
import os
import logging
import hashlib
import secrets
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
import uuid

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import asyncpg
import redis.asyncio as redis
import httpx
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import numpy as np
from faker import Faker
import hashlib
import hmac

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/abena_ihr_security")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:3001")
    DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://localhost:8001")
    
    # Encryption configuration
    MASTER_KEY = os.getenv("MASTER_KEY", Fernet.generate_key())
    HSM_ENDPOINT = os.getenv("HSM_ENDPOINT", None)  # Hardware Security Module endpoint
    KEY_ROTATION_DAYS = int(os.getenv("KEY_ROTATION_DAYS", "90"))
    
    # Anonymization configuration
    K_ANONYMITY_THRESHOLD = int(os.getenv("K_ANONYMITY_THRESHOLD", "5"))
    DIFFERENTIAL_PRIVACY_EPSILON = float(os.getenv("DIFFERENTIAL_PRIVACY_EPSILON", "1.0"))
    
    # Audit configuration
    AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "2555"))  # 7 years
    
config = Config()

# Initialize FastAPI app
app = FastAPI(
    title="Abena IHR Privacy & Security Service",
    description="Data encryption, anonymization, and privacy protection service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global connections
db_pool = None
redis_client = None
faker = Faker()

# Data Models
class EncryptionRequest(BaseModel):
    data: Union[str, Dict[str, Any]]
    data_type: str = Field(..., description="Type of data being encrypted")
    patient_id: Optional[str] = None
    purpose: str = Field(..., description="Purpose of encryption (storage, transmission, processing)")
    retention_period: Optional[int] = Field(None, description="Data retention period in days")

class DecryptionRequest(BaseModel):
    encrypted_data: str
    encryption_key_id: str
    purpose: str = Field(..., description="Purpose of decryption")

class AnonymizationRequest(BaseModel):
    dataset: List[Dict[str, Any]]
    anonymization_type: str = Field(..., description="k-anonymity, l-diversity, differential-privacy")
    quasi_identifiers: List[str] = Field(..., description="Fields that could identify individuals")
    sensitive_attributes: Optional[List[str]] = Field(None, description="Sensitive fields to protect")
    k_value: Optional[int] = Field(5, description="K value for k-anonymity")
    epsilon: Optional[float] = Field(1.0, description="Epsilon for differential privacy")

class AccessRequest(BaseModel):
    resource_type: str
    resource_id: str
    action: str
    purpose: str
    patient_id: Optional[str] = None
    emergency_access: bool = False

class AuditLogEntry(BaseModel):
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    patient_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    risk_score: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None

# Encryption Manager
class EncryptionManager:
    """Handles all encryption/decryption operations"""
    
    def __init__(self):
        self.master_key = config.MASTER_KEY
        if isinstance(self.master_key, str):
            self.master_key = self.master_key.encode()
        self.cipher_suite = Fernet(self.master_key)
        
        # Generate RSA key pair for asymmetric encryption
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
    
    def generate_data_encryption_key(self) -> str:
        """Generate a new data encryption key"""
        return Fernet.generate_key().decode()
    
    def encrypt_symmetric(self, data: str, key: Optional[str] = None) -> Dict[str, str]:
        """Encrypt data using symmetric encryption"""
        if key is None:
            key = self.generate_data_encryption_key()
        
        cipher_suite = Fernet(key.encode())
        encrypted_data = cipher_suite.encrypt(data.encode())
        
        return {
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "encryption_key": key,
            "algorithm": "AES-256-CBC"
        }
    
    def decrypt_symmetric(self, encrypted_data: str, key: str) -> str:
        """Decrypt data using symmetric encryption"""
        cipher_suite = Fernet(key.encode())
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = cipher_suite.decrypt(decoded_data)
        return decrypted_data.decode()
    
    def encrypt_asymmetric(self, data: str) -> str:
        """Encrypt data using asymmetric encryption"""
        encrypted = self.public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode()
    
    def decrypt_asymmetric(self, encrypted_data: str) -> str:
        """Decrypt data using asymmetric encryption"""
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted = self.private_key.decrypt(
            decoded_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode()
    
    def hash_data(self, data: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Create a cryptographic hash of data"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password-like data, SHA-256 for others
        key = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        hash_value = key.derive(data.encode())
        
        return {
            "hash": base64.b64encode(hash_value).decode(),
            "salt": salt,
            "algorithm": "PBKDF2-SHA256"
        }

# Anonymization Manager
class AnonymizationManager:
    """Handles data anonymization and de-identification"""
    
    def __init__(self):
        self.faker = Faker()
    
    def k_anonymity(self, dataset: List[Dict[str, Any]], quasi_identifiers: List[str], k: int = 5) -> List[Dict[str, Any]]:
        """Apply k-anonymity to dataset"""
        anonymized_dataset = []
        
        # Group records by quasi-identifier combinations
        groups = {}
        for record in dataset:
            key = tuple(str(record.get(qi, '')) for qi in quasi_identifiers)
            if key not in groups:
                groups[key] = []
            groups[key].append(record)
        
        # Process each group
        for group_key, group_records in groups.items():
            if len(group_records) < k:
                # Generalize or suppress data to meet k-anonymity
                generalized_records = self._generalize_group(group_records, quasi_identifiers)
                anonymized_dataset.extend(generalized_records)
            else:
                anonymized_dataset.extend(group_records)
        
        return anonymized_dataset
    
    def _generalize_group(self, records: List[Dict[str, Any]], quasi_identifiers: List[str]) -> List[Dict[str, Any]]:
        """Generalize a group of records to meet k-anonymity"""
        generalized_records = []
        
        for record in records:
            generalized_record = record.copy()
            
            for qi in quasi_identifiers:
                if qi in record:
                    # Apply generalization based on field type
                    if qi.lower() in ['age', 'birth_year']:
                        age = record.get(qi)
                        if isinstance(age, int):
                            # Generalize age to 5-year ranges
                            age_range = f"{(age // 5) * 5}-{((age // 5) * 5) + 4}"
                            generalized_record[qi] = age_range
                    elif qi.lower() in ['zip_code', 'postal_code']:
                        zip_code = str(record.get(qi, ''))
                        if len(zip_code) >= 3:
                            # Generalize to first 3 digits
                            generalized_record[qi] = zip_code[:3] + "XX"
                    else:
                        # Generic generalization - use category or suppress
                        generalized_record[qi] = "*"
            
            generalized_records.append(generalized_record)
        
        return generalized_records
    
    def differential_privacy(self, dataset: List[Dict[str, Any]], epsilon: float = 1.0) -> List[Dict[str, Any]]:
        """Apply differential privacy to numerical data"""
        anonymized_dataset = []
        
        for record in dataset:
            anonymized_record = record.copy()
            
            for key, value in record.items():
                if isinstance(value, (int, float)):
                    # Add Laplace noise for differential privacy
                    sensitivity = 1.0  # Assumed sensitivity
                    scale = sensitivity / epsilon
                    noise = np.random.laplace(0, scale)
                    anonymized_record[key] = value + noise
            
            anonymized_dataset.append(anonymized_record)
        
        return anonymized_dataset
    
    def pseudonymize(self, data: str, patient_id: str) -> str:
        """Create consistent pseudonym for a patient"""
        # Create deterministic pseudonym based on patient ID and secret
        secret_key = config.MASTER_KEY[:32]  # Use first 32 bytes as secret
        pseudonym = hmac.new(
            secret_key,
            (patient_id + data).encode(),
            hashlib.sha256
        ).hexdigest()[:12]  # Use first 12 characters
        
        return f"PSEUDO_{pseudonym}"
    
    def redact_phi(self, text: str) -> str:
        """Redact PHI from free text"""
        import re
        
        # Patterns for common PHI
        patterns = {
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'mrn': r'\bMRN:?\s*\d+\b',
            'address_number': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b'
        }
        
        redacted_text = text
        for phi_type, pattern in patterns.items():
            redacted_text = re.sub(pattern, f'[{phi_type.upper()}_REDACTED]', redacted_text, flags=re.IGNORECASE)
        
        return redacted_text

# Access Control Manager
class AccessControlManager:
    """Manages access control and authorization"""
    
    def __init__(self, db_pool, redis_client):
        self.db_pool = db_pool
        self.redis_client = redis_client
    
    async def check_access(self, user_id: str, resource_type: str, resource_id: str, action: str, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """Check if user has access to perform action on resource"""
        try:
            # Get user permissions from cache or database
            permissions = await self._get_user_permissions(user_id)
            
            # Check specific permission
            permission_key = f"{resource_type}.{action}"
            has_permission = permission_key in permissions
            
            # Check patient-specific access if applicable
            if patient_id and has_permission:
                has_patient_access = await self._check_patient_access(user_id, patient_id)
                has_permission = has_permission and has_patient_access
            
            # Calculate risk score
            risk_score = await self._calculate_risk_score(user_id, resource_type, action)
            
            # Log access attempt
            await self._log_access_attempt(user_id, resource_type, resource_id, action, has_permission, risk_score)
            
            return {
                "granted": has_permission,
                "risk_score": risk_score,
                "conditions": self._get_access_conditions(risk_score),
                "reason": "Access granted" if has_permission else "Insufficient permissions"
            }
            
        except Exception as e:
            logger.error(f"Access check failed: {e}")
            return {
                "granted": False,
                "risk_score": 1.0,
                "conditions": [],
                "reason": "Access check failed"
            }
    
    async def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions from cache or database"""
        cache_key = f"user_permissions:{user_id}"
        
        # Try cache first
        cached_permissions = await self.redis_client.get(cache_key)
        if cached_permissions:
            return json.loads(cached_permissions)
        
        # Get from database
        async with self.db_pool.acquire() as conn:
            result = await conn.fetch("""
                SELECT p.name FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                JOIN user_roles ur ON rp.role_id = ur.role_id
                WHERE ur.user_id = $1 AND ur.is_active = true
            """, user_id)
            
            permissions = [row['name'] for row in result]
            
            # Cache for 5 minutes
            await self.redis_client.setex(cache_key, 300, json.dumps(permissions))
            
            return permissions
    
    async def _check_patient_access(self, user_id: str, patient_id: str) -> bool:
        """Check if user has access to specific patient data"""
        async with self.db_pool.acquire() as conn:
            # Check direct patient-provider relationship
            result = await conn.fetchrow("""
                SELECT EXISTS(
                    SELECT 1 FROM patient_provider_relationships 
                    WHERE patient_id = $1 AND provider_id = $2 AND is_active = true
                )
            """, patient_id, user_id)
            
            if result['exists']:
                return True
            
            # Check emergency access permissions
            result = await conn.fetchrow("""
                SELECT EXISTS(
                    SELECT 1 FROM emergency_access_grants
                    WHERE patient_id = $1 AND provider_id = $2 
                    AND granted_at > NOW() - INTERVAL '24 hours'
                    AND is_active = true
                )
            """, patient_id, user_id)
            
            return result['exists']
    
    async def _calculate_risk_score(self, user_id: str, resource_type: str, action: str) -> float:
        """Calculate risk score for access request"""
        base_risk = 0.1
        
        # Increase risk for sensitive actions
        if action in ['delete', 'export', 'share']:
            base_risk += 0.3
        
        # Increase risk for sensitive resources
        if resource_type in ['patient_data', 'financial_data', 'genetic_data']:
            base_risk += 0.2
        
        # Check recent access patterns
        async with self.db_pool.acquire() as conn:
            # Check for unusual access patterns
            recent_accesses = await conn.fetchval("""
                SELECT COUNT(*) FROM access_audit_log
                WHERE user_id = $1 AND timestamp > NOW() - INTERVAL '1 hour'
            """, user_id)
            
            if recent_accesses > 50:  # Unusual access frequency
                base_risk += 0.4
        
        return min(1.0, base_risk)
    
    def _get_access_conditions(self, risk_score: float) -> List[str]:
        """Get access conditions based on risk score"""
        conditions = []
        
        if risk_score > 0.7:
            conditions.extend(['require_mfa', 'additional_approval', 'time_limited'])
        elif risk_score > 0.5:
            conditions.extend(['require_mfa', 'audit_enhanced'])
        elif risk_score > 0.3:
            conditions.append('audit_standard')
        
        return conditions
    
    async def _log_access_attempt(self, user_id: str, resource_type: str, resource_id: str, action: str, granted: bool, risk_score: float):
        """Log access attempt to audit trail"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO access_audit_log (
                    user_id, resource_type, resource_id, action, granted,
                    risk_score, timestamp, ip_address
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, user_id, resource_type, resource_id, action, granted, risk_score, 
            datetime.now(timezone.utc), None)  # IP would come from request

# Initialize managers
encryption_manager = EncryptionManager()
anonymization_manager = AnonymizationManager()

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token with Auth service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.AUTH_SERVICE_URL}/auth/profile",
                headers={"Authorization": f"Bearer {credentials.credentials}"}
            )
            
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )

# Database initialization
async def init_db():
    """Initialize database connection pool"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(config.DATABASE_URL, min_size=5, max_size=20)
        logger.info("Database connection pool created")
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.from_url(config.REDIS_URL)
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

# API Routes
@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    await init_db()
    await init_redis()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Abena IHR Privacy & Security Service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@app.post("/encrypt")
async def encrypt_data(
    request: EncryptionRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Encrypt sensitive data"""
    try:
        # Convert data to string if it's a dict
        data_str = json.dumps(request.data) if isinstance(request.data, dict) else str(request.data)
        
        # Encrypt the data
        encryption_result = encryption_manager.encrypt_symmetric(data_str)
        
        # Store encryption metadata
        key_id = str(uuid.uuid4())
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO encryption_keys (
                    key_id, encrypted_key, algorithm, data_type, purpose,
                    patient_id, created_by, created_at, expires_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
            key_id,
            encryption_manager.encrypt_asymmetric(encryption_result['encryption_key']),
            encryption_result['algorithm'],
            request.data_type,
            request.purpose,
            request.patient_id,
            user['id'],
            datetime.now(timezone.utc),
            datetime.now(timezone.utc) + timedelta(days=request.retention_period) if request.retention_period else None
            )
        
        # Log encryption event
        await log_security_event(
            user['id'], 'ENCRYPTION', 'data', key_id,
            {"data_type": request.data_type, "purpose": request.purpose}
        )
        
        return {
            "encrypted_data": encryption_result['encrypted_data'],
            "key_id": key_id,
            "algorithm": encryption_result['algorithm'],
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption failed: {str(e)}"
        )

@app.post("/decrypt")
async def decrypt_data(
    request: DecryptionRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Decrypt sensitive data"""
    try:
        # Get encryption key
        async with db_pool.acquire() as conn:
            key_record = await conn.fetchrow("""
                SELECT encrypted_key, data_type, purpose, patient_id, expires_at
                FROM encryption_keys
                WHERE key_id = $1
            """, request.encryption_key_id)
        
        if not key_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Encryption key not found"
            )
        
        # Check if key has expired
        if key_record['expires_at'] and key_record['expires_at'] < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Encryption key has expired"
            )
        
        # Check access permissions
        access_control = AccessControlManager(db_pool, redis_client)
        access_result = await access_control.check_access(
            user['id'], 'encrypted_data', request.encryption_key_id, 'decrypt',
            key_record['patient_id']
        )
        
        if not access_result['granted']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=access_result['reason']
            )
        
        # Decrypt the key and then the data
        encryption_key = encryption_manager.decrypt_asymmetric(key_record['encrypted_key'])
        decrypted_data = encryption_manager.decrypt_symmetric(request.encrypted_data, encryption_key)
        
        # Log decryption event
        await log_security_event(
            user['id'], 'DECRYPTION', 'data', request.encryption_key_id,
            {"purpose": request.purpose, "risk_score": access_result['risk_score']}
        )
        
        return {
            "decrypted_data": decrypted_data,
            "data_type": key_record['data_type'],
            "conditions": access_result['conditions'],
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decryption failed: {str(e)}"
        )

@app.post("/anonymize")
async def anonymize_data(
    request: AnonymizationRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Anonymize dataset for research or analytics"""
    try:
        if request.anonymization_type == "k-anonymity":
            anonymized_data = anonymization_manager.k_anonymity(
                request.dataset, request.quasi_identifiers, request.k_value
            )
        elif request.anonymization_type == "differential-privacy":
            anonymized_data = anonymization_manager.differential_privacy(
                request.dataset, request.epsilon
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported anonymization type: {request.anonymization_type}"
            )
        
        # Log anonymization event
        await log_security_event(
            user['id'], 'ANONYMIZATION', 'dataset', None,
            {
                "anonymization_type": request.anonymization_type,
                "record_count": len(request.dataset),
                "k_value": request.k_value,
                "epsilon": request.epsilon
            }
        )
        
        return {
            "anonymized_data": anonymized_data,
            "anonymization_type": request.anonymization_type,
            "parameters": {
                "k_value": request.k_value,
                "epsilon": request.epsilon
            },
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anonymization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anonymization failed: {str(e)}"
        )

@app.post("/pseudonymize")
async def pseudonymize_data(
    data: str,
    patient_id: str,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Create pseudonym for patient data"""
    try:
        pseudonym = anonymization_manager.pseudonymize(data, patient_id)
        
        # Store pseudonym mapping securely
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO pseudonym_mappings (
                    patient_id, pseudonym, created_by, created_at
                ) VALUES ($1, $2, $3, $4)
                ON CONFLICT (patient_id) DO UPDATE SET
                    last_used = NOW()
            """, patient_id, pseudonym, user['id'], datetime.now(timezone.utc))
        
        return {
            "pseudonym": pseudonym,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Pseudonymization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pseudonymization failed: {str(e)}"
        )

@app.post("/redact-phi")
async def redact_phi_text(
    text: str,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Redact PHI from free text"""
    try:
        redacted_text = anonymization_manager.redact_phi(text)
        
        return {
            "original_length": len(text),
            "redacted_text": redacted_text,
            "redacted_length": len(redacted_text),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"PHI redaction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PHI redaction failed: {str(e)}"
        )

@app.post("/check-access")
async def check_access(
    request: AccessRequest,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Check access permissions for a resource"""
    try:
        access_control = AccessControlManager(db_pool, redis_client)
        access_result = await access_control.check_access(
            user['id'], request.resource_type, request.resource_id,
            request.action, request.patient_id
        )
        
        return access_result
        
    except Exception as e:
        logger.error(f"Access check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Access check failed: {str(e)}"
        )

@app.get("/audit-log")
async def get_audit_log(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Get audit log entries"""
    try:
        # Check if user has audit access
        if user['role'] not in ['admin', 'security_officer']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access audit logs"
            )
        
        # Build query conditions
        conditions = []
        params = []
        param_count = 0
        
        if start_date:
            param_count += 1
            conditions.append(f"timestamp >= ${param_count}")
            params.append(datetime.fromisoformat(start_date))
        
        if end_date:
            param_count += 1
            conditions.append(f"timestamp <= ${param_count}")
            params.append(datetime.fromisoformat(end_date))
        
        if user_id:
            param_count += 1
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)
        
        if action:
            param_count += 1
            conditions.append(f"action = ${param_count}")
            params.append(action)
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        async with db_pool.acquire() as conn:
            query = f"""
                SELECT * FROM security_audit_log
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT {limit} OFFSET {offset}
            """
            
            result = await conn.fetch(query, *params)
            
            # Count total records
            count_query = f"SELECT COUNT(*) as total FROM security_audit_log {where_clause}"
            total_count = await conn.fetchval(count_query, *params)
        
        return {
            "audit_logs": [dict(row) for row in result],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audit log retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit log retrieval failed: {str(e)}"
        )

@app.post("/rotate-keys")
async def rotate_encryption_keys(
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Rotate encryption keys"""
    try:
        if user['role'] not in ['admin', 'security_officer']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to rotate keys"
            )
        
        # Add key rotation task to background
        background_tasks.add_task(perform_key_rotation, user['id'])
        
        return {
            "message": "Key rotation initiated",
            "initiated_by": user['id'],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Key rotation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key rotation failed: {str(e)}"
        )

# Helper functions
async def log_security_event(user_id: str, action: str, resource_type: str, resource_id: Optional[str], additional_data: Optional[Dict[str, Any]] = None):
    """Log security event to audit trail"""
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO security_audit_log (
                    user_id, action, resource_type, resource_id, timestamp,
                    additional_data, ip_address
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
            user_id, action, resource_type, resource_id, 
            datetime.now(timezone.utc), json.dumps(additional_data) if additional_data else None,
            None  # IP would come from request context
            )
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")

async def perform_key_rotation(initiated_by: str):
    """Perform encryption key rotation"""
    try:
        # Get keys that need rotation
        async with db_pool.acquire() as conn:
            old_keys = await conn.fetch("""
                SELECT key_id, encrypted_key FROM encryption_keys
                WHERE created_at < NOW() - INTERVAL '%s days'
                AND rotated_at IS NULL
            """, config.KEY_ROTATION_DAYS)
            
            for key_record in old_keys:
                # Generate new key
                new_key = encryption_manager.generate_data_encryption_key()
                encrypted_new_key = encryption_manager.encrypt_asymmetric(new_key)
                
                # Update key record
                await conn.execute("""
                    UPDATE encryption_keys
                    SET encrypted_key = $1, rotated_at = NOW(), rotated_by = $2
                    WHERE key_id = $3
                """, encrypted_new_key, initiated_by, key_record['key_id'])
                
                # Log rotation
                await log_security_event(
                    initiated_by, 'KEY_ROTATION', 'encryption_key', key_record['key_id']
                )
        
        logger.info(f"Key rotation completed for {len(old_keys)} keys")
        
    except Exception as e:
        logger.error(f"Key rotation failed: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    ) 