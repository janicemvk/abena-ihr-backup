"""
Mock Abena SDK for development and testing
This provides the interface expected by the API Gateway
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

class AbenaSDK:
    """
    Mock Abena SDK that provides authentication, data management, and privacy controls
    """
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize the Abena SDK with service URLs
        
        Args:
            config: Dictionary containing service URLs
                - authServiceUrl: Authentication service URL
                - dataServiceUrl: Data service URL  
                - privacyServiceUrl: Privacy service URL
                - blockchainServiceUrl: Blockchain service URL
        """
        self.auth_service_url = config.get('authServiceUrl', 'http://localhost:3001')
        self.data_service_url = config.get('dataServiceUrl', 'http://localhost:8001')
        self.privacy_service_url = config.get('privacyServiceUrl', 'http://localhost:8002')
        self.blockchain_service_url = config.get('blockchainServiceUrl', 'http://localhost:8003')
        
        # Mock storage for development
        self._mock_patients = {}
        self._mock_observations = {}
        self._mock_device_data = {}
        self._mock_audit_logs = []
        
        logging.info(f"Abena SDK initialized with services: {config}")
    
    async def verifyRequest(self, request) -> bool:
        """
        Verify request authentication and permissions
        
        Args:
            request: FastAPI request object
            
        Returns:
            bool: True if request is authenticated and authorized
            
        Raises:
            Exception: If authentication fails
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise Exception("Authorization header required")
        
        if not auth_header.startswith('Bearer '):
            raise Exception("Invalid authorization format")
        
        token = auth_header.split(' ')[1]
        
        # Mock token validation - in production this would call the auth service
        if token == 'test-token' or token.startswith('valid-'):
            return True
        else:
            raise Exception("Invalid token")
    
    async def storePatientData(self, patient_id: str, data: Dict[str, Any], purpose: str) -> bool:
        """
        Store patient data with privacy controls
        
        Args:
            patient_id: Unique patient identifier
            data: Patient data to store
            purpose: Purpose of data access
            
        Returns:
            bool: True if data was stored successfully
        """
        # Mock privacy controls and encryption
        encrypted_data = self._mock_encrypt_data(data)
        
        self._mock_patients[patient_id] = {
            'data': encrypted_data,
            'purpose': purpose,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'audit_id': str(uuid.uuid4())
        }
        
        # Mock audit logging
        await self.logAuditEvent({
            'action': 'store_patient_data',
            'patient_id': patient_id,
            'purpose': purpose,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        return True
    
    async def storeObservationData(self, observation_id: str, data: Dict[str, Any], purpose: str) -> bool:
        """
        Store observation data with privacy controls
        
        Args:
            observation_id: Unique observation identifier
            data: Observation data to store
            purpose: Purpose of data access
            
        Returns:
            bool: True if data was stored successfully
        """
        # Mock privacy controls and encryption
        encrypted_data = self._mock_encrypt_data(data)
        
        self._mock_observations[observation_id] = {
            'data': encrypted_data,
            'purpose': purpose,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'audit_id': str(uuid.uuid4())
        }
        
        # Mock audit logging
        await self.logAuditEvent({
            'action': 'store_observation_data',
            'observation_id': observation_id,
            'purpose': purpose,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        return True
    
    async def storeDeviceData(self, sync_id: str, data: Dict[str, Any], purpose: str) -> bool:
        """
        Store device data with privacy controls
        
        Args:
            sync_id: Unique sync identifier
            data: Device data to store
            purpose: Purpose of data access
            
        Returns:
            bool: True if data was stored successfully
        """
        # Mock privacy controls and encryption
        encrypted_data = self._mock_encrypt_data(data)
        
        self._mock_device_data[sync_id] = {
            'data': encrypted_data,
            'purpose': purpose,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'audit_id': str(uuid.uuid4())
        }
        
        # Mock audit logging
        await self.logAuditEvent({
            'action': 'store_device_data',
            'sync_id': sync_id,
            'purpose': purpose,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        return True
    
    async def getPatientData(self, patient_id: str, purpose: str) -> Dict[str, Any]:
        """
        Retrieve patient data with privacy controls
        
        Args:
            patient_id: Unique patient identifier
            purpose: Purpose of data access
            
        Returns:
            Dict: Patient data
            
        Raises:
            Exception: If patient not found or access denied
        """
        if patient_id not in self._mock_patients:
            raise Exception(f"Patient {patient_id} not found")
        
        patient_record = self._mock_patients[patient_id]
        
        # Mock privacy controls and decryption
        decrypted_data = self._mock_decrypt_data(patient_record['data'])
        
        # Mock audit logging
        await self.logAuditEvent({
            'action': 'get_patient_data',
            'patient_id': patient_id,
            'purpose': purpose,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        return decrypted_data
    
    async def getPatientObservations(self, patient_id: str, purpose: str) -> List[Dict[str, Any]]:
        """
        Retrieve patient observations with privacy controls
        
        Args:
            patient_id: Unique patient identifier
            purpose: Purpose of data access
            
        Returns:
            List: Patient observations
            
        Raises:
            Exception: If patient not found or access denied
        """
        # Mock filtering observations by patient_id
        patient_observations = []
        
        for obs_id, obs_record in self._mock_observations.items():
            decrypted_data = self._mock_decrypt_data(obs_record['data'])
            if decrypted_data.get('patient_id') == patient_id:
                patient_observations.append(decrypted_data)
        
        # Mock audit logging
        await self.logAuditEvent({
            'action': 'get_patient_observations',
            'patient_id': patient_id,
            'purpose': purpose,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        return patient_observations
    
    async def logAuditEvent(self, event_data: Dict[str, Any]) -> bool:
        """
        Log audit event for compliance and monitoring
        
        Args:
            event_data: Event data to log
            
        Returns:
            bool: True if event was logged successfully
        """
        audit_event = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            **event_data
        }
        
        self._mock_audit_logs.append(audit_event)
        
        # Keep only last 1000 audit events in mock storage
        if len(self._mock_audit_logs) > 1000:
            self._mock_audit_logs = self._mock_audit_logs[-1000:]
        
        logging.info(f"Audit event logged: {audit_event}")
        return True
    
    def _mock_encrypt_data(self, data: Dict[str, Any]) -> str:
        """
        Mock data encryption - in production this would use proper encryption
        
        Args:
            data: Data to encrypt
            
        Returns:
            str: Mock encrypted data
        """
        # In production, this would use proper encryption
        return f"ENCRYPTED:{json.dumps(data)}"
    
    def _mock_decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Mock data decryption - in production this would use proper decryption
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Dict: Decrypted data
        """
        # In production, this would use proper decryption
        if encrypted_data.startswith("ENCRYPTED:"):
            data_str = encrypted_data[10:]  # Remove "ENCRYPTED:" prefix
            return json.loads(data_str)
        else:
            raise Exception("Invalid encrypted data format")
    
    # Utility methods for testing
    def get_mock_patients(self) -> Dict[str, Any]:
        """Get all mock patient data for testing"""
        return self._mock_patients
    
    def get_mock_observations(self) -> Dict[str, Any]:
        """Get all mock observation data for testing"""
        return self._mock_observations
    
    def get_mock_audit_logs(self) -> List[Dict[str, Any]]:
        """Get all mock audit logs for testing"""
        return self._mock_audit_logs
    
    def clear_mock_data(self):
        """Clear all mock data for testing"""
        self._mock_patients.clear()
        self._mock_observations.clear()
        self._mock_device_data.clear()
        self._mock_audit_logs.clear() 