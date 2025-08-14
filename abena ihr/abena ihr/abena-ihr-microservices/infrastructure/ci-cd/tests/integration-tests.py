#!/usr/bin/env python3
"""
Abena IHR Integration Tests
Healthcare microservices integration testing
"""

import pytest
import requests
import json
import time
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "https://api.abena-ihr.com")
API_VERSION = "v1"
TIMEOUT = 30

@dataclass
class TestUser:
    """Test user configuration"""
    email: str
    password: str
    role: str
    token: str = None

class AbenaIHRIntegrationTests:
    """Integration tests for Abena IHR microservices"""
    
    def __init__(self):
        self.base_url = f"{BASE_URL}/api/{API_VERSION}"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Test users
        self.test_users = {
            "patient": TestUser(
                email="patient.test@abena-ihr.com",
                password="TestPassword123!",
                role="patient"
            ),
            "provider": TestUser(
                email="provider.test@abena-ihr.com",
                password="TestPassword123!",
                role="provider"
            ),
            "admin": TestUser(
                email="admin.test@abena-ihr.com",
                password="TestPassword123!",
                role="admin"
            )
        }
    
    def setup_method(self):
        """Setup method for each test"""
        # Authenticate test users
        for user_type, user in self.test_users.items():
            user.token = self._authenticate_user(user.email, user.password)
    
    def _authenticate_user(self, email: str, password: str) -> str:
        """Authenticate user and return token"""
        auth_data = {
            "email": email,
            "password": password
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json=auth_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"Authentication failed: {response.text}")
    
    def _get_auth_headers(self, user_type: str = "patient") -> Dict[str, str]:
        """Get authenticated headers for user"""
        user = self.test_users[user_type]
        return {"Authorization": f"Bearer {user.token}"}
    
    # Health Check Tests
    def test_health_check(self):
        """Test health check endpoints"""
        services = [
            "patient-engagement",
            "data-ingestion", 
            "clinical-decision-support",
            "privacy-security",
            "blockchain",
            "auth"
        ]
        
        for service in services:
            response = self.session.get(
                f"{self.base_url}/{service}/health",
                timeout=TIMEOUT
            )
            assert response.status_code == 200, f"Health check failed for {service}"
            
            health_data = response.json()
            assert health_data["status"] == "healthy", f"Service {service} not healthy"
    
    # Authentication Tests
    def test_user_authentication(self):
        """Test user authentication flow"""
        # Test login
        auth_data = {
            "email": self.test_users["patient"].email,
            "password": self.test_users["patient"].password
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json=auth_data,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        auth_response = response.json()
        assert "access_token" in auth_response
        assert "refresh_token" in auth_response
        
        # Test token refresh
        refresh_data = {
            "refresh_token": auth_response["refresh_token"]
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/refresh",
            json=refresh_data,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        refresh_response = response.json()
        assert "access_token" in refresh_response
    
    def test_authentication_failure(self):
        """Test authentication failure scenarios"""
        # Test invalid credentials
        auth_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json=auth_data,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 401
    
    # Patient Management Tests
    def test_patient_registration(self):
        """Test patient registration"""
        patient_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john.doe.{int(time.time())}@example.com",
            "password": "SecurePassword123!",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "phone": "+1234567890",
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345"
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/patient-engagement/patients/register",
            json=patient_data,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 201
        patient_response = response.json()
        assert "patient_id" in patient_response
        assert patient_response["email"] == patient_data["email"]
    
    def test_patient_profile_retrieval(self):
        """Test patient profile retrieval"""
        headers = self._get_auth_headers("patient")
        
        response = self.session.get(
            f"{self.base_url}/patient-engagement/patients/profile",
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert "patient_id" in profile
        assert "first_name" in profile
        assert "last_name" in profile
    
    # Appointment Tests
    def test_appointment_booking(self):
        """Test appointment booking"""
        headers = self._get_auth_headers("patient")
        
        appointment_data = {
            "provider_id": "test-provider-123",
            "appointment_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "appointment_type": "consultation",
            "reason": "Annual checkup",
            "preferred_time": "09:00"
        }
        
        response = self.session.post(
            f"{self.base_url}/patient-engagement/appointments",
            json=appointment_data,
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 201
        appointment = response.json()
        assert "appointment_id" in appointment
        assert appointment["status"] == "scheduled"
    
    def test_appointment_retrieval(self):
        """Test appointment retrieval"""
        headers = self._get_auth_headers("patient")
        
        response = self.session.get(
            f"{self.base_url}/patient-engagement/appointments",
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        appointments = response.json()
        assert isinstance(appointments, list)
    
    # Clinical Decision Support Tests
    def test_clinical_decision_support(self):
        """Test clinical decision support"""
        headers = self._get_auth_headers("provider")
        
        clinical_data = {
            "patient_id": "test-patient-123",
            "symptoms": ["fever", "cough", "fatigue"],
            "vital_signs": {
                "temperature": 38.5,
                "blood_pressure": "120/80",
                "heart_rate": 85,
                "oxygen_saturation": 98
            },
            "medical_history": {
                "allergies": ["penicillin"],
                "chronic_conditions": ["hypertension"],
                "medications": ["lisinopril"]
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/clinical-decision-support/analyze",
            json=clinical_data,
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        analysis = response.json()
        assert "recommendations" in analysis
        assert "risk_score" in analysis
        assert "confidence" in analysis
    
    # Data Ingestion Tests
    def test_hl7_data_ingestion(self):
        """Test HL7 data ingestion"""
        headers = self._get_auth_headers("provider")
        
        hl7_message = """MSH|^~\\&|EPIC|EPICADT|ABENA_IHR|ABENA_IHR|20231201120000||ADT^A01|MSG00001|P|2.5
PID|||12345^^^MRN||DOE^JOHN^^^^||19900101|M|||123 MAIN ST^^ANYTOWN^CA^12345
PV1||I|2000^2012^01||||123456^SMITH^JANE^^^^^^^MD"""
        
        response = self.session.post(
            f"{self.base_url}/data-ingestion/hl7",
            data=hl7_message,
            headers={"Content-Type": "text/plain", **headers},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        ingestion_response = response.json()
        assert "status" in ingestion_response
        assert "message_id" in ingestion_response
    
    def test_fhir_data_ingestion(self):
        """Test FHIR data ingestion"""
        headers = self._get_auth_headers("provider")
        
        fhir_patient = {
            "resourceType": "Patient",
            "id": "test-patient-123",
            "identifier": [
                {
                    "system": "https://abena-ihr.com/patient",
                    "value": "12345"
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": "Doe",
                    "given": ["John"]
                }
            ],
            "gender": "male",
            "birthDate": "1990-01-01"
        }
        
        response = self.session.post(
            f"{self.base_url}/data-ingestion/fhir/Patient",
            json=fhir_patient,
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        fhir_response = response.json()
        assert "status" in fhir_response
        assert "resource_id" in fhir_response
    
    # Privacy and Security Tests
    def test_data_encryption(self):
        """Test data encryption"""
        headers = self._get_auth_headers("provider")
        
        sensitive_data = {
            "patient_id": "test-patient-123",
            "ssn": "123-45-6789",
            "medical_record": "Patient has diabetes and hypertension"
        }
        
        response = self.session.post(
            f"{self.base_url}/privacy-security/encrypt",
            json=sensitive_data,
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        encrypted_response = response.json()
        assert "encrypted_data" in encrypted_response
        assert encrypted_response["encrypted_data"] != sensitive_data["ssn"]
    
    def test_data_anonymization(self):
        """Test data anonymization"""
        headers = self._get_auth_headers("admin")
        
        patient_data = {
            "patient_id": "test-patient-123",
            "first_name": "John",
            "last_name": "Doe",
            "ssn": "123-45-6789",
            "date_of_birth": "1990-01-01",
            "address": "123 Main St, Anytown, CA 12345"
        }
        
        response = self.session.post(
            f"{self.base_url}/privacy-security/anonymize",
            json=patient_data,
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        anonymized_response = response.json()
        assert "anonymized_data" in anonymized_response
        
        anonymized = anonymized_response["anonymized_data"]
        assert anonymized["first_name"] != patient_data["first_name"]
        assert anonymized["last_name"] != patient_data["last_name"]
        assert "ssn" not in anonymized
    
    # Blockchain Tests
    def test_health_record_creation(self):
        """Test health record creation on blockchain"""
        headers = self._get_auth_headers("provider")
        
        health_record = {
            "patient_id": "test-patient-123",
            "record_type": "lab_result",
            "data": {
                "test_name": "Complete Blood Count",
                "results": {
                    "wbc": 7.5,
                    "rbc": 4.8,
                    "hemoglobin": 14.2,
                    "platelets": 250
                },
                "reference_range": "Normal",
                "date": datetime.now().isoformat()
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/blockchain/health-records",
            json=health_record,
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 201
        blockchain_response = response.json()
        assert "transaction_hash" in blockchain_response
        assert "block_number" in blockchain_response
    
    def test_consent_management(self):
        """Test consent management on blockchain"""
        headers = self._get_auth_headers("patient")
        
        consent_data = {
            "patient_id": "test-patient-123",
            "provider_id": "test-provider-123",
            "consent_type": "data_sharing",
            "permissions": ["read", "write"],
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "revocable": True
        }
        
        response = self.session.post(
            f"{self.base_url}/blockchain/consents",
            json=consent_data,
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 201
        consent_response = response.json()
        assert "consent_id" in consent_response
        assert "transaction_hash" in consent_response
    
    # Performance Tests
    def test_api_response_time(self):
        """Test API response times"""
        headers = self._get_auth_headers("patient")
        
        endpoints = [
            "/patient-engagement/patients/profile",
            "/patient-engagement/appointments",
            "/clinical-decision-support/analyze"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                timeout=TIMEOUT
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 2.0, f"Response time {response_time}s exceeds 2s for {endpoint}"
            assert response.status_code in [200, 404], f"Unexpected status code {response.status_code} for {endpoint}"
    
    # Error Handling Tests
    def test_invalid_endpoint(self):
        """Test invalid endpoint handling"""
        response = self.session.get(
            f"{self.base_url}/invalid-endpoint",
            timeout=TIMEOUT
        )
        
        assert response.status_code == 404
    
    def test_unauthorized_access(self):
        """Test unauthorized access handling"""
        response = self.session.get(
            f"{self.base_url}/patient-engagement/patients/profile",
            timeout=TIMEOUT
        )
        
        assert response.status_code == 401
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        headers = self._get_auth_headers("patient")
        
        # Make multiple rapid requests
        for i in range(10):
            response = self.session.get(
                f"{self.base_url}/patient-engagement/patients/profile",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 429:
                # Rate limit hit
                break
        
        # Should not get rate limited for normal usage
        assert response.status_code != 429, "Rate limiting triggered too early"

# Test runner
if __name__ == "__main__":
    # Run tests
    test_suite = AbenaIHRIntegrationTests()
    
    # Run all tests
    test_methods = [method for method in dir(test_suite) if method.startswith('test_')]
    
    print(f"Running {len(test_methods)} integration tests...")
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            test_method = getattr(test_suite, method_name)
            test_suite.setup_method()
            test_method()
            print(f"✅ {method_name} - PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {method_name} - FAILED: {str(e)}")
            failed += 1
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        exit(1)
    else:
        print("🎉 All integration tests passed!") 