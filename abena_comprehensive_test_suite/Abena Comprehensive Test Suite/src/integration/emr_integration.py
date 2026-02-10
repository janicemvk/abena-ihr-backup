# Mock EMR Integration Manager - Updated to use Abena SDK
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.core.abena_sdk import AbenaSDK

class EMRIntegrationManager:
    """EMR Integration Manager using Abena SDK for auth and data access"""
    
    def __init__(self, abena_sdk: AbenaSDK, emr_config: Dict[str, str]):
        self.abena = abena_sdk
        self.emr_type = emr_config.get('emr_type', 'epic')
        self.base_url = emr_config.get('base_url', 'https://mock-epic.com')
        self.fhir_version = emr_config.get('fhir_version', 'R4')
        
        # Mock EMR session state
        self._session_token = None
        self._last_sync = None
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with EMR using Abena SDK for credential management"""
        try:
            # Use Abena SDK for authentication
            auth_success = await self.abena.authenticate(credentials)
            
            if auth_success:
                # Mock EMR-specific token
                self._session_token = f"emr_token_{credentials.get('username', 'user')}"
                return True
            return False
        except Exception as e:
            # Log authentication failure through Abena SDK audit
            await self.abena.create_alert({
                'type': 'authentication_failure',
                'message': f'EMR authentication failed: {str(e)}',
                'severity': 'high'
            })
            return False
    
    async def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Get patient data from EMR using Abena SDK for data access"""
        try:
            # Use Abena SDK to get patient data (which handles privacy/encryption)
            patient_data = await self.abena.get_patient_data(patient_id, 'emr_integration')
            
            # Mock EMR-specific data structure
            emr_patient_data = {
                'patient_id': patient_id,
                'emr_source': self.emr_type,
                'fhir_version': self.fhir_version,
                'last_updated': datetime.now().isoformat(),
                'demographics': {
                    'name': 'Mock Patient',
                    'age': 45,
                    'gender': 'female'
                },
                'vital_signs': {
                    'blood_pressure': '120/80',
                    'heart_rate': 72,
                    'temperature': 98.6
                },
                'medications': ['aspirin', 'metformin'],
                'allergies': ['penicillin'],
                'conditions': ['diabetes', 'hypertension']
            }
            
            # Update last sync timestamp
            self._last_sync = datetime.now()
            
            return emr_patient_data
            
        except Exception as e:
            # Log data retrieval failure through Abena SDK
            await self.abena.create_alert({
                'type': 'data_retrieval_failure',
                'message': f'EMR data retrieval failed for patient {patient_id}: {str(e)}',
                'severity': 'medium'
            })
            return {}
    
    async def get_observations(self, patient_id: str, observation_type: str = None) -> List[Dict[str, Any]]:
        """Get patient observations from EMR using Abena SDK"""
        try:
            # Use Abena SDK to get patient data
            patient_data = await self.abena.get_patient_data(patient_id, 'emr_observations')
            
            # Mock observations data
            observations = [
                {
                    'id': f'obs_{patient_id}_001',
                    'type': 'vital_signs',
                    'value': '120/80',
                    'unit': 'mmHg',
                    'date': datetime.now().isoformat()
                },
                {
                    'id': f'obs_{patient_id}_002',
                    'type': 'lab_result',
                    'value': '7.2',
                    'unit': 'mmol/L',
                    'date': datetime.now().isoformat()
                }
            ]
            
            if observation_type:
                observations = [obs for obs in observations if obs['type'] == observation_type]
            
            return observations
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'observation_retrieval_failure',
                'message': f'EMR observation retrieval failed: {str(e)}',
                'severity': 'medium'
            })
            return []
    
    async def save_clinical_note(self, patient_id: str, note_content: str, note_type: str = 'progress') -> str:
        """Save clinical note to EMR using Abena SDK for audit logging"""
        try:
            note_id = f"note_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            note_data = {
                'note_id': note_id,
                'patient_id': patient_id,
                'content': note_content,
                'type': note_type,
                'author': 'Dr. Smith',
                'timestamp': datetime.now().isoformat()
            }
            
            # Use Abena SDK to save note (handles privacy and blockchain)
            await self.abena.save_treatment_plan(patient_id, note_data)
            
            return note_id
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'note_save_failure',
                'message': f'EMR note save failed: {str(e)}',
                'severity': 'medium'
            })
            return ""
    
    async def get_clinical_notes(self, patient_id: str, note_type: str = None) -> List[Dict[str, Any]]:
        """Get clinical notes from EMR using Abena SDK"""
        try:
            # Use Abena SDK to get clinical notes
            notes = await self.abena.get_clinical_notes(patient_id)
            
            if note_type:
                notes = [note for note in notes if note.get('type') == note_type]
            
            return notes
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'note_retrieval_failure',
                'message': f'EMR note retrieval failed: {str(e)}',
                'severity': 'medium'
            })
            return []
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get EMR connection status"""
        return {
            'connected': self._session_token is not None,
            'emr_type': self.emr_type,
            'last_sync': self._last_sync.isoformat() if self._last_sync else None,
            'fhir_version': self.fhir_version
        } 