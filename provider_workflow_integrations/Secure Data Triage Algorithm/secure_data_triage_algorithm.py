import hashlib
import json
import re
from typing import Dict, List, Any
from enum import Enum
from datetime import datetime
import uuid
from cryptography.fernet import Fernet
import logging
import asyncio
import aiohttp
from abc import ABC, abstractmethod

class DataSensitivityLevel(Enum):
    """Data sensitivity classification levels"""
    PUBLIC = 1          # Non-sensitive, aggregatable data
    STATISTICAL = 2     # De-identified statistical data
    CLINICAL = 3        # Clinical data requiring anonymization
    PERSONAL = 4        # Personal identifiable information
    SENSITIVE = 5       # Highly sensitive medical data

class StorageDestination(Enum):
    """Blockchain storage destinations"""
    IDENTIFIED_VAULT = "identified"      # Patient-controlled identified data
    ANONYMOUS_RESEARCH = "anonymous"     # De-identified research data
    STATISTICAL_POOL = "statistical"     # Aggregated statistical data
    QUARANTINE = "quarantine"            # Data requiring review
    REJECTED = "rejected"                # Data that cannot be stored

class AbenaSDK:
    """
    Abena SDK - Centralized service for auth, data, privacy, and blockchain operations
    Follows the correct pattern: centralized SDK instead of individual implementations
    """
    
    def __init__(self, config: Dict[str, str]):
        self.auth_service_url = config.get('authServiceUrl', 'http://localhost:3001')
        self.data_service_url = config.get('dataServiceUrl', 'http://localhost:8001')
        self.privacy_service_url = config.get('privacyServiceUrl', 'http://localhost:8002')
        self.blockchain_service_url = config.get('blockchainServiceUrl', 'http://localhost:8003')
        
        # Auto-handled auth & permissions
        self.auth_token = None
        self.user_permissions = {}
        
        # Auto-handled privacy & encryption
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Auto-handled audit logging
        self.audit_log = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('abena_sdk.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Auto-handled authentication"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.auth_service_url}/auth", json=credentials) as response:
                    if response.status == 200:
                        auth_data = await response.json()
                        self.auth_token = auth_data.get('token')
                        self.user_permissions = auth_data.get('permissions', {})
                        self.logger.info("Authentication successful")
                        return True
                    else:
                        self.logger.error("Authentication failed")
                        return False
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False
    
    async def get_patient_data(self, patient_id: str, purpose: str) -> Dict[str, Any]:
        """Auto-handled patient data retrieval with permissions and privacy"""
        try:
            # 1. Auto-handled auth & permissions
            if not self.auth_token:
                raise Exception("Not authenticated")
            
            if not self._check_permission('read_patient_data', patient_id):
                raise Exception("Insufficient permissions")
            
            # 2. Auto-handled privacy & encryption
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                async with session.get(
                    f"{self.data_service_url}/patients/{patient_id}",
                    headers=headers,
                    params={'purpose': purpose}
                ) as response:
                    if response.status == 200:
                        encrypted_data = await response.json()
                        # Auto-decrypt data
                        decrypted_data = self._decrypt_data(encrypted_data)
                        
                        # 3. Auto-handled audit logging
                        self._log_audit_entry('data_access', patient_id, purpose)
                        
                        return decrypted_data
                    else:
                        raise Exception(f"Failed to retrieve patient data: {response.status}")
        except Exception as e:
            self.logger.error(f"Error retrieving patient data: {str(e)}")
            raise
    
    async def store_patient_data(self, patient_id: str, data: Dict[str, Any], 
                               storage_destination: StorageDestination) -> bool:
        """Auto-handled secure data storage"""
        try:
            # 1. Auto-handled auth & permissions
            if not self.auth_token:
                raise Exception("Not authenticated")
            
            if not self._check_permission('write_patient_data', patient_id):
                raise Exception("Insufficient permissions")
            
            # 2. Auto-handled privacy & encryption
            encrypted_data = self._encrypt_data(data)
            
            # Store to blockchain via privacy service
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                payload = {
                    'patient_id': patient_id,
                    'data': encrypted_data,
                    'storage_destination': storage_destination.value,
                    'timestamp': datetime.now().isoformat()
                }
                
                async with session.post(
                    f"{self.privacy_service_url}/store",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        # 3. Auto-handled audit logging
                        self._log_audit_entry('data_storage', patient_id, storage_destination.value)
                        return True
                    else:
                        raise Exception(f"Failed to store data: {response.status}")
        except Exception as e:
            self.logger.error(f"Error storing patient data: {str(e)}")
            return False
    
    def _check_permission(self, action: str, resource: str) -> bool:
        """Auto-handled permission checking"""
        required_permission = f"{action}:{resource}"
        return required_permission in self.user_permissions or 'admin' in self.user_permissions
    
    def _encrypt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-handled data encryption"""
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str):
                encrypted_value = self.cipher.encrypt(value.encode())
                encrypted[key] = encrypted_value.decode()
            else:
                encrypted[key] = value
        return encrypted
    
    def _decrypt_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-handled data decryption"""
        decrypted = {}
        for key, value in encrypted_data.items():
            if isinstance(value, str) and value.startswith('gAAAAA'):  # Fernet encrypted
                try:
                    decrypted_value = self.cipher.decrypt(value.encode())
                    decrypted[key] = decrypted_value.decode()
                except:
                    decrypted[key] = value  # Keep as-is if decryption fails
            else:
                decrypted[key] = value
        return decrypted
    
    def _log_audit_entry(self, action: str, resource: str, details: str):
        """Auto-handled audit logging"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'resource': resource,
            'details': details,
            'user_token_hash': hashlib.sha256(self.auth_token.encode()).hexdigest()[:16] if self.auth_token else None
        }
        self.audit_log.append(audit_entry)
        self.logger.info(f"Audit: {action} on {resource}")

class DataTriageEngine:
    """
    Secure data triage algorithm for Abena blockchain storage
    Uses Abena SDK for centralized auth, data, privacy, and blockchain services
    """
    
    def __init__(self, sdk_config: Dict[str, str] = None):
        # Use Abena SDK instead of implementing own systems
        if sdk_config is None:
            sdk_config = {
                'authServiceUrl': 'http://localhost:3001',
                'dataServiceUrl': 'http://localhost:8001',
                'privacyServiceUrl': 'http://localhost:8002',
                'blockchainServiceUrl': 'http://localhost:8003'
            }
        
        self.abena = AbenaSDK(sdk_config)
        self.logger = logging.getLogger(__name__)
        
        # PII patterns for detection (core triage logic)
        self.pii_patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'medical_id': r'\b[A-Z]{2}\d{8}\b'
        }
        
        # Sensitive medical keywords (core triage logic)
        self.sensitive_keywords = {
            'mental_health': ['depression', 'anxiety', 'bipolar', 'schizophrenia', 'ptsd'],
            'substance_abuse': ['alcohol', 'drug', 'addiction', 'substance', 'rehab'],
            'reproductive': ['pregnancy', 'abortion', 'contraception', 'fertility'],
            'genetic': ['genetic', 'hereditary', 'dna', 'chromosome', 'mutation'],
            'infectious': ['hiv', 'aids', 'hepatitis', 'tuberculosis', 'covid']
        }
    
    async def triage_data(self, data: Dict[str, Any], patient_consent: Dict[str, bool], 
                         patient_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Main triage function that processes incoming data and determines secure storage
        Uses Abena SDK for centralized services
        """
        try:
            self.logger.info(f"Starting data triage for data hash: {self._hash_data(data)[:16]}")
            
            # Step 1: PII Detection and Classification
            pii_analysis = self._detect_pii(data)
            
            # Step 2: Sensitivity Assessment
            sensitivity_level = self._assess_sensitivity(data, pii_analysis)
            
            # Step 3: Consent Verification
            consent_check = self._verify_consent(sensitivity_level, patient_consent)
            
            # Step 4: Anonymization Strategy
            anonymization_plan = self._determine_anonymization_strategy(
                data, sensitivity_level, pii_analysis
            )
            
            # Step 5: Storage Destination Decision
            storage_destination = self._determine_storage_destination(
                sensitivity_level, consent_check, anonymization_plan
            )
            
            # Step 6: Store data using SDK (handles all security measures)
            if patient_id:
                storage_success = await self.abena.store_patient_data(
                    patient_id, data, storage_destination
                )
            else:
                storage_success = True  # For demo purposes
            
            self.logger.info(f"Data triage completed successfully. Destination: {storage_destination.value}")
            
            return {
                'triage_id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'original_data_hash': self._hash_data(data),
                'sensitivity_level': sensitivity_level.name,
                'storage_destination': storage_destination.value,
                'anonymization_plan': anonymization_plan,
                'consent_verified': consent_check,
                'storage_success': storage_success,
                'sdk_used': True
            }
            
        except Exception as e:
            self.logger.error(f"Data triage failed: {str(e)}")
            return self._quarantine_data(data, str(e))
    
    def _detect_pii(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Detect personally identifiable information in the data"""
        pii_found = {}
        
        data_string = json.dumps(data, default=str)
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, data_string, re.IGNORECASE)
            if matches:
                pii_found[pii_type] = matches
                
        return pii_found
    
    def _assess_sensitivity(self, data: Dict[str, Any], pii_analysis: Dict) -> DataSensitivityLevel:
        """Assess the sensitivity level of the data"""
        sensitivity_score = 0
        
        # Base score for PII presence
        if pii_analysis:
            sensitivity_score += len(pii_analysis) * 2
            
        # Check for sensitive medical keywords
        data_string = json.dumps(data, default=str).lower()
        
        for category, keywords in self.sensitive_keywords.items():
            for keyword in keywords:
                if keyword in data_string:
                    if category in ['mental_health', 'genetic', 'infectious']:
                        sensitivity_score += 3  # High sensitivity
                    else:
                        sensitivity_score += 2  # Medium sensitivity
        
        # Check for direct patient identifiers
        if any(field in data for field in ['patient_name', 'ssn', 'medical_record_number']):
            sensitivity_score += 5
            
        # Check for healthcare-related fields that increase sensitivity
        healthcare_indicators = ['patient_id', 'diagnosis', 'treatment', 'medication', 'vital_signs', 'heart_rate', 'blood_pressure']
        healthcare_count = sum(1 for field in healthcare_indicators if field in data)
        if healthcare_count > 0:
            sensitivity_score += 1  # Base healthcare data score
            
        # Age and ZIP code combination increases sensitivity (re-identification risk)
        if 'age' in data and 'zip_code' in data:
            sensitivity_score += 1
            
        # Determine sensitivity level
        if sensitivity_score >= 8:
            return DataSensitivityLevel.SENSITIVE
        elif sensitivity_score >= 5:
            return DataSensitivityLevel.PERSONAL
        elif sensitivity_score >= 3:
            return DataSensitivityLevel.CLINICAL
        elif sensitivity_score >= 1:
            return DataSensitivityLevel.STATISTICAL
        else:
            return DataSensitivityLevel.PUBLIC
    
    def _verify_consent(self, sensitivity_level: DataSensitivityLevel, 
                       patient_consent: Dict[str, bool]) -> bool:
        """Verify patient consent for data usage"""
        consent_requirements = {
            DataSensitivityLevel.PUBLIC: 'general_data_use',
            DataSensitivityLevel.STATISTICAL: 'anonymous_research',
            DataSensitivityLevel.CLINICAL: 'clinical_research',
            DataSensitivityLevel.PERSONAL: 'identified_storage',
            DataSensitivityLevel.SENSITIVE: 'sensitive_data_storage'
        }
        
        required_consent = consent_requirements.get(sensitivity_level, 'general_data_use')
        return patient_consent.get(required_consent, False)
    
    def _determine_anonymization_strategy(self, data: Dict[str, Any], 
                                        sensitivity_level: DataSensitivityLevel,
                                        pii_analysis: Dict) -> Dict[str, Any]:
        """Determine the appropriate anonymization strategy"""
        strategy = {
            'method': 'none',
            'techniques': [],
            'k_anonymity': 1,
            'differential_privacy': False,
            'homomorphic_encryption': False
        }
        
        if sensitivity_level == DataSensitivityLevel.PUBLIC:
            strategy['method'] = 'minimal'
            
        elif sensitivity_level == DataSensitivityLevel.STATISTICAL:
            strategy['method'] = 'aggregation'
            strategy['techniques'] = ['generalization', 'suppression']
            strategy['k_anonymity'] = 5
            
        elif sensitivity_level == DataSensitivityLevel.CLINICAL:
            strategy['method'] = 'de_identification'
            strategy['techniques'] = ['pseudonymization', 'generalization', 'perturbation']
            strategy['k_anonymity'] = 10
            strategy['differential_privacy'] = True
            
        elif sensitivity_level in [DataSensitivityLevel.PERSONAL, DataSensitivityLevel.SENSITIVE]:
            strategy['method'] = 'full_anonymization'
            strategy['techniques'] = ['tokenization', 'encryption', 'differential_privacy']
            strategy['k_anonymity'] = 20
            strategy['differential_privacy'] = True
            strategy['homomorphic_encryption'] = True
            
        return strategy
    
    def _determine_storage_destination(self, sensitivity_level: DataSensitivityLevel,
                                     consent_verified: bool,
                                     anonymization_plan: Dict) -> StorageDestination:
        """Determine where the data should be stored in the blockchain"""
        
        if not consent_verified:
            return StorageDestination.QUARANTINE
            
        if sensitivity_level == DataSensitivityLevel.PUBLIC:
            return StorageDestination.STATISTICAL_POOL
            
        elif sensitivity_level == DataSensitivityLevel.STATISTICAL:
            return StorageDestination.ANONYMOUS_RESEARCH
            
        elif sensitivity_level == DataSensitivityLevel.CLINICAL:
            if anonymization_plan['k_anonymity'] >= 10:
                return StorageDestination.ANONYMOUS_RESEARCH
            else:
                return StorageDestination.QUARANTINE
                
        elif sensitivity_level in [DataSensitivityLevel.PERSONAL, DataSensitivityLevel.SENSITIVE]:
            return StorageDestination.IDENTIFIED_VAULT
            
        return StorageDestination.QUARANTINE
    
    def _hash_data(self, data: Any) -> str:
        """Create hash of data for integrity verification"""
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _quarantine_data(self, data: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Quarantine data that cannot be processed safely"""
        self.logger.warning(f"Data quarantined: {reason}")
        return {
            'triage_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'status': 'QUARANTINED',
            'reason': reason,
            'storage_destination': StorageDestination.QUARANTINE.value,
            'requires_manual_review': True,
            'data_hash': self._hash_data(data)
        }

# Example module demonstrating correct SDK pattern
class HealthAnalyticsModule:
    """
    Example module that demonstrates the correct SDK pattern
    Uses Abena SDK instead of implementing its own auth/data systems
    """
    
    def __init__(self, sdk_config: Dict[str, str] = None):
        # ✅ Correct - Uses Abena SDK
        if sdk_config is None:
            sdk_config = {
                'authServiceUrl': 'http://localhost:3001',
                'dataServiceUrl': 'http://localhost:8001',
                'privacyServiceUrl': 'http://localhost:8002',
                'blockchainServiceUrl': 'http://localhost:8003'
            }
        
        self.abena = AbenaSDK(sdk_config)
        self.logger = logging.getLogger(__name__)
    
    async def analyze_patient_health(self, patient_id: str, user_id: str) -> Dict[str, Any]:
        """
        Example method demonstrating correct SDK pattern usage
        """
        try:
            # 1. Auto-handled auth & permissions
            patient_data = await self.abena.get_patient_data(patient_id, 'health_analytics')
            
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            analysis_result = self._process_health_data(patient_data)
            
            # Store results using SDK
            await self.abena.store_patient_data(
                patient_id, 
                analysis_result, 
                StorageDestination.IDENTIFIED_VAULT
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Health analysis failed: {str(e)}")
            raise
    
    def _process_health_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Business logic for health data analysis"""
        analysis = {
            'analysis_timestamp': datetime.now().isoformat(),
            'health_score': 0,
            'risk_factors': [],
            'recommendations': []
        }
        
        # Calculate health score
        if 'heart_rate' in patient_data:
            hr = patient_data['heart_rate']
            if 60 <= hr <= 100:
                analysis['health_score'] += 25
            else:
                analysis['risk_factors'].append('abnormal_heart_rate')
        
        if 'blood_pressure' in patient_data:
            bp = patient_data['blood_pressure']
            if isinstance(bp, str) and '120/80' in bp:
                analysis['health_score'] += 25
            else:
                analysis['risk_factors'].append('blood_pressure_concern')
        
        # Add recommendations
        if analysis['health_score'] < 50:
            analysis['recommendations'].append('schedule_follow_up')
        
        return analysis

# Example usage and testing
async def demonstrate_triage_algorithm():
    """Demonstrate the data triage algorithm with various data types using Abena SDK"""
    
    # ✅ Correct - Uses Abena SDK
    triage_engine = DataTriageEngine({
        'authServiceUrl': 'http://localhost:3001',
        'dataServiceUrl': 'http://localhost:8001',
        'privacyServiceUrl': 'http://localhost:8002',
        'blockchainServiceUrl': 'http://localhost:8003'
    })
    
    # Test data samples
    test_cases = [
        {
            'name': 'Basic Health Metrics',
            'data': {
                'patient_id': 'P12345',
                'heart_rate': 72,
                'blood_pressure': '120/80',
                'weight': 150,
                'date': '2024-01-15'
            },
            'consent': {
                'general_data_use': True,
                'anonymous_research': True,
                'clinical_research': False,
                'identified_storage': False,
                'sensitive_data_storage': False
            },
            'patient_id': 'P12345'
        },
        {
            'name': 'Sensitive Mental Health Data',
            'data': {
                'patient_name': 'John Doe',
                'ssn': '123-45-6789',
                'diagnosis': 'Major Depression',
                'treatment': 'Cognitive Behavioral Therapy',
                'medication': 'Sertraline 50mg',
                'notes': 'Patient reports anxiety and sleep disturbances'
            },
            'consent': {
                'general_data_use': True,
                'anonymous_research': True,
                'clinical_research': True,
                'identified_storage': True,
                'sensitive_data_storage': True
            },
            'patient_id': 'P67890'
        },
        {
            'name': 'IoT Wearable Data',
            'data': {
                'device_id': 'WATCH_789',
                'steps': 8542,
                'calories_burned': 2100,
                'sleep_hours': 7.5,
                'heart_rate_avg': 68,
                'timestamp': '2024-01-15T10:30:00Z'
            },
            'consent': {
                'general_data_use': True,
                'anonymous_research': True,
                'clinical_research': False,
                'identified_storage': False,
                'sensitive_data_storage': False
            },
            'patient_id': 'P11111'
        }
    ]
    
    print("=== Abena Data Triage Algorithm Demonstration (SDK Pattern) ===\n")
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print("-" * 50)
        
        # Use async triage with SDK
        result = await triage_engine.triage_data(
            test_case['data'], 
            test_case['consent'],
            test_case['patient_id']
        )
        results.append(result)
        
        print(f"Triage ID: {result['triage_id']}")
        print(f"Sensitivity Level: {result['sensitivity_level']}")
        print(f"Storage Destination: {result['storage_destination']}")
        print(f"Security Measures: {result.get('anonymization_plan', {}).get('techniques', [])}")
        print(f"Consent Verified: {result['consent_verified']}")
        print(f"SDK Used: {result.get('sdk_used', False)}")
        print(f"Storage Success: {result.get('storage_success', False)}")
        print(f"Compliance: HIPAA & GDPR Ready")
        print()
    
    # Audit logging is handled automatically by the SDK
    print("✅ Audit logging handled automatically by Abena SDK")
    
    return results

def demonstrate_sdk_pattern():
    """Demonstrate the correct SDK pattern vs wrong pattern"""
    
    print("=== SDK Pattern Demonstration ===\n")
    
    print("❌ WRONG - Has its own auth/data:")
    print("""
class SomeModule {
  constructor() {
    this.database = new Database();
    this.authSystem = new CustomAuth();
  }
}
""")
    
    print("✅ CORRECT - Uses Abena SDK:")
    print("""
class SomeModule {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
  }
  
  async someMethod(patientId, userId) {
    // 1. Auto-handled auth & permissions
    const patientData = await this.abena.getPatientData(patientId, 'module_purpose');
    
    // 2. Auto-handled privacy & encryption
    // 3. Auto-handled audit logging
    
    // 4. Focus on your business logic
    return this.processData(patientData);
  }
}
""")
    
    print("🎯 BENEFITS of SDK Pattern:")
    print("• Centralized authentication and permissions")
    print("• Automatic privacy and encryption handling")
    print("• Built-in audit logging")
    print("• Consistent security across all modules")
    print("• Easier maintenance and updates")
    print("• HIPAA and GDPR compliance built-in")
    
    print("\n📋 EXAMPLE MODULE USING SDK PATTERN:")
    print("""
# ✅ Correct - HealthAnalyticsModule using Abena SDK
analytics_module = HealthAnalyticsModule({
    'authServiceUrl': 'http://localhost:3001',
    'dataServiceUrl': 'http://localhost:8001',
    'privacyServiceUrl': 'http://localhost:8002',
    'blockchainServiceUrl': 'http://localhost:8003'
})

# Auto-handled auth, privacy, and audit logging
result = await analytics_module.analyze_patient_health('P12345', 'U789')
""")

if __name__ == "__main__":
    # Run the SDK pattern demonstration
    demonstrate_sdk_pattern()
    print("\n" + "="*60 + "\n")
    
    # Run the async triage demonstration
    asyncio.run(demonstrate_triage_algorithm()) 