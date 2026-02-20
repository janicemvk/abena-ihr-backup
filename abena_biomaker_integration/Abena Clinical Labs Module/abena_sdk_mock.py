"""
Mock Abena SDK for testing purposes
This module simulates the Abena SDK functionality for development and testing
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
import random

# Mock Abena SDK Models
@dataclass
class AbenaPatient:
    """Abena SDK Patient model"""
    patient_id: str
    name: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    bmi: float
    date_of_birth: datetime
    collection_date: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.bmi == 0:
            self.bmi = self.weight_kg / ((self.height_cm / 100) ** 2)

@dataclass
class AbenaLabResult:
    """Abena SDK Lab Result model"""
    test_name: str
    value: float
    unit: str
    reference_low: float
    reference_high: float
    status: str
    date: datetime
    category: str = ""
    
    def __post_init__(self):
        if self.status == "":
            if self.value < self.reference_low:
                self.status = "low"
            elif self.value > self.reference_high:
                self.status = "high"
            else:
                self.status = "normal"

@dataclass
class AbenaVitalSign:
    """Abena SDK Vital Sign model"""
    measurement_type: str
    value: float
    unit: str
    date: datetime
    notes: str = ""

@dataclass
class AbenaEKGResult:
    """Abena SDK EKG Result model"""
    measurement_type: str
    value: float
    unit: str
    interpretation: str
    date: datetime
    notes: str = ""

@dataclass
class AbenaSmartDeviceData:
    """Abena SDK Smart Device Data model"""
    device_type: str
    metric: str
    value: float
    unit: str
    timestamp: datetime
    quality_score: float = 1.0

# Mock Abena SDK Configuration
@dataclass
class AbenaConfig:
    """Abena SDK Configuration"""
    api_url: str = "https://api.abena.com"
    api_version: str = "v1"
    timeout: int = 30
    retry_attempts: int = 3
    debug_mode: bool = False

# Mock Abena SDK Exceptions
class AbenaAuthenticationError(Exception):
    """Abena SDK Authentication Error"""
    pass

class AbenaAuthorizationError(Exception):
    """Abena SDK Authorization Error"""
    pass

class AbenaDataError(Exception):
    """Abena SDK Data Error"""
    pass

# Mock Abena SDK Authenticator
class AbenaAuthenticator:
    """Mock Abena SDK Authenticator"""
    
    def __init__(self, config: AbenaConfig):
        self.config = config
        self._authenticated = False
        self._session_token = None
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Mock authentication"""
        # Simulate authentication logic
        if credentials.get("username") and credentials.get("password"):
            self._authenticated = True
            self._session_token = f"mock_token_{random.randint(1000, 9999)}"
            return True
        return False
    
    def is_authenticated(self) -> bool:
        """Check if authenticated"""
        return self._authenticated
    
    def get_session_token(self) -> Optional[str]:
        """Get session token"""
        return self._session_token
    
    def logout(self) -> None:
        """Logout"""
        self._authenticated = False
        self._session_token = None

# Mock Abena SDK Authorizer
class AbenaAuthorizer:
    """Mock Abena SDK Authorizer"""
    
    def __init__(self, config: AbenaConfig):
        self.config = config
        self._permissions = {
            "patient_data": ["read", "write"],
            "lab_results": ["read", "write"],
            "vital_signs": ["read", "write"],
            "ekg_results": ["read", "write"],
            "smart_device_data": ["read", "write"]
        }
    
    def authorize(self, resource: str, action: str) -> bool:
        """Mock authorization"""
        # Simulate authorization logic
        if resource in self._permissions:
            return action in self._permissions[resource]
        return False
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has permission"""
        return self.authorize(resource, action)
    
    def get_permissions(self) -> Dict[str, List[str]]:
        """Get user permissions"""
        return self._permissions.copy()

# Mock Abena SDK Data Handler
class AbenaDataHandler:
    """Mock Abena SDK Data Handler"""
    
    def __init__(self, config: AbenaConfig):
        self.config = config
        self._mock_data = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock patient data"""
        # Mock patient data
        self._mock_data["patients"] = {
            "TEST001": AbenaPatient(
                patient_id="TEST001",
                name="John Smith",
                age=45,
                gender="Male",
                height_cm=175,
                weight_kg=85,
                bmi=27.8,
                date_of_birth=datetime(1978, 6, 15)
            )
        }
        
        # Mock lab results
        self._mock_data["lab_results"] = {
            "TEST001": [
                AbenaLabResult("AEA", 1.2, "ng/mL", 0.5, 2.0, "", datetime.now(), "direct_ecs"),
                AbenaLabResult("2-AG", 2.5, "ng/mL", 1.0, 4.0, "", datetime.now(), "direct_ecs"),
                AbenaLabResult("CRP", 2.5, "mg/L", 0.0, 3.0, "", datetime.now(), "inflammation"),
            ]
        }
        
        # Mock vital signs
        self._mock_data["vital_signs"] = {
            "TEST001": [
                AbenaVitalSign("Blood Pressure Systolic", 135, "mmHg", datetime.now()),
                AbenaVitalSign("Heart Rate", 72, "bpm", datetime.now()),
            ]
        }
        
        # Mock EKG results
        self._mock_data["ekg_results"] = {
            "TEST001": [
                AbenaEKGResult("Heart Rate", 72, "bpm", "Normal sinus rhythm", datetime.now()),
                AbenaEKGResult("PR Interval", 160, "ms", "Normal", datetime.now()),
            ]
        }
        
        # Mock smart device data
        self._mock_data["smart_device_data"] = {
            "TEST001": [
                AbenaSmartDeviceData("Apple Watch", "HRV", 45, "ms", datetime.now()),
                AbenaSmartDeviceData("Apple Watch", "Sleep Quality", 75, "%", datetime.now()),
            ]
        }
    
    def get_patient(self, patient_id: str) -> Optional[AbenaPatient]:
        """Get patient data"""
        return self._mock_data["patients"].get(patient_id)
    
    def get_lab_results(self, patient_id: str) -> List[AbenaLabResult]:
        """Get lab results"""
        return self._mock_data["lab_results"].get(patient_id, [])
    
    def get_vital_signs(self, patient_id: str) -> List[AbenaVitalSign]:
        """Get vital signs"""
        return self._mock_data["vital_signs"].get(patient_id, [])
    
    def get_ekg_results(self, patient_id: str) -> List[AbenaEKGResult]:
        """Get EKG results"""
        return self._mock_data["ekg_results"].get(patient_id, [])
    
    def get_smart_device_data(self, patient_id: str) -> List[AbenaSmartDeviceData]:
        """Get smart device data"""
        return self._mock_data["smart_device_data"].get(patient_id, [])
    
    def save_patient(self, patient: AbenaPatient) -> bool:
        """Save patient data"""
        self._mock_data["patients"][patient.patient_id] = patient
        return True
    
    def save_lab_result(self, patient_id: str, result: AbenaLabResult) -> bool:
        """Save lab result"""
        if patient_id not in self._mock_data["lab_results"]:
            self._mock_data["lab_results"][patient_id] = []
        self._mock_data["lab_results"][patient_id].append(result)
        return True
    
    def save_vital_sign(self, patient_id: str, vital_sign: AbenaVitalSign) -> bool:
        """Save vital sign"""
        if patient_id not in self._mock_data["vital_signs"]:
            self._mock_data["vital_signs"][patient_id] = []
        self._mock_data["vital_signs"][patient_id].append(vital_sign)
        return True
    
    def save_ekg_result(self, patient_id: str, ekg_result: AbenaEKGResult) -> bool:
        """Save EKG result"""
        if patient_id not in self._mock_data["ekg_results"]:
            self._mock_data["ekg_results"][patient_id] = []
        self._mock_data["ekg_results"][patient_id].append(ekg_result)
        return True
    
    def save_smart_device_data(self, patient_id: str, data: AbenaSmartDeviceData) -> bool:
        """Save smart device data"""
        if patient_id not in self._mock_data["smart_device_data"]:
            self._mock_data["smart_device_data"][patient_id] = []
        self._mock_data["smart_device_data"][patient_id].append(data)
        return True

# Create mock SDK package structure
class MockAbenaSDK:
    """Mock Abena SDK package"""
    
    def __init__(self):
        self.auth = AbenaAuthenticator
        self.authorization = AbenaAuthorizer
        self.data = AbenaDataHandler
        self.models = {
            'AbenaPatient': AbenaPatient,
            'AbenaLabResult': AbenaLabResult,
            'AbenaVitalSign': AbenaVitalSign,
            'AbenaEKGResult': AbenaEKGResult,
            'AbenaSmartDeviceData': AbenaSmartDeviceData
        }
        self.config = AbenaConfig
        self.exceptions = {
            'AbenaAuthenticationError': AbenaAuthenticationError,
            'AbenaAuthorizationError': AbenaAuthorizationError,
            'AbenaDataError': AbenaDataError
        }

# Create the mock SDK module
mock_sdk = MockAbenaSDK()

# Export all components for easy import
__all__ = [
    'AbenaPatient',
    'AbenaLabResult', 
    'AbenaVitalSign',
    'AbenaEKGResult',
    'AbenaSmartDeviceData',
    'AbenaConfig',
    'AbenaAuthenticator',
    'AbenaAuthorizer',
    'AbenaDataHandler',
    'AbenaAuthenticationError',
    'AbenaAuthorizationError',
    'AbenaDataError'
] 