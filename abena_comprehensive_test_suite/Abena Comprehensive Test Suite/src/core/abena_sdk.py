# Mock Abena SDK for testing
# This represents the centralized SDK that all modules should use
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

class AbenaSDK:
    """Centralized Abena SDK that handles auth, data, privacy, and blockchain"""
    
    def __init__(self, config: Dict[str, str]):
        self.auth_service_url = config.get('authServiceUrl', 'http://localhost:3001')
        self.data_service_url = config.get('dataServiceUrl', 'http://localhost:8001')
        self.privacy_service_url = config.get('privacyServiceUrl', 'http://localhost:8002')
        self.blockchain_service_url = config.get('blockchainServiceUrl', 'http://localhost:8003')
        
        # Mock internal state
        self._auth_token = None
        self._audit_log = []
        self._encrypted_data_cache = {}
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Mock authentication"""
        # Simulate async auth
        await asyncio.sleep(0.01)
        self._auth_token = f"mock_token_{credentials.get('username', 'user')}"
        return True
    
    async def get_patient_data(self, patient_id: str, purpose: str) -> Dict[str, Any]:
        """Get patient data with auto-handled auth, privacy, and audit"""
        # Auto-handled auth & permissions
        if not self._auth_token:
            raise ValueError("Authentication required")
        
        # Auto-handled privacy & encryption
        encrypted_data = await self._get_encrypted_patient_data(patient_id)
        
        # Auto-handled audit logging
        self._audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'get_patient_data',
            'patient_id': patient_id,
            'purpose': purpose,
            'user': 'mock_user'
        })
        
        return encrypted_data
    
    async def save_treatment_plan(self, patient_id: str, treatment_plan: Dict[str, Any]) -> bool:
        """Save treatment plan with auto-handled privacy and blockchain"""
        # Auto-handled privacy & encryption
        encrypted_plan = await self._encrypt_data(treatment_plan)
        
        # Auto-handled blockchain recording
        await self._record_on_blockchain('treatment_plan_saved', {
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # Auto-handled audit logging
        self._audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'save_treatment_plan',
            'patient_id': patient_id,
            'user': 'mock_user'
        })
        
        return True
    
    async def get_clinical_notes(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get clinical notes with auto-handled auth and privacy"""
        if not self._auth_token:
            raise ValueError("Authentication required")
        
        # Mock clinical notes
        notes = [
            {
                'id': f'note_{patient_id}_001',
                'timestamp': datetime.now().isoformat(),
                'content': 'Mock clinical note content',
                'author': 'Dr. Smith'
            }
        ]
        
        self._audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'get_clinical_notes',
            'patient_id': patient_id,
            'user': 'mock_user'
        })
        
        return notes
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> str:
        """Create alert with auto-handled blockchain recording"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Auto-handled blockchain recording
        await self._record_on_blockchain('alert_created', {
            'alert_id': alert_id,
            'timestamp': datetime.now().isoformat()
        })
        
        self._audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'create_alert',
            'alert_id': alert_id,
            'user': 'mock_user'
        })
        
        return alert_id
    
    async def _get_encrypted_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Mock encrypted patient data retrieval"""
        # Simulate async data retrieval
        await asyncio.sleep(0.01)
        
        return {
            'patient_id': patient_id,
            'encrypted_data': f"encrypted_data_for_{patient_id}",
            'decryption_key': 'mock_key',
            'data_type': 'patient_profile'
        }
    
    async def _encrypt_data(self, data: Dict[str, Any]) -> str:
        """Mock data encryption"""
        await asyncio.sleep(0.01)
        return f"encrypted_{json.dumps(data)}"
    
    async def _record_on_blockchain(self, action: str, data: Dict[str, Any]) -> bool:
        """Mock blockchain recording"""
        await asyncio.sleep(0.01)
        return True
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log for compliance"""
        return self._audit_log.copy() 