# Abena SDK Integration for ML Feedback Pipeline
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import requests
from dataclasses import asdict

class AbenaSDK:
    """Abena SDK for unified authentication, data access, privacy, and audit logging"""
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize Abena SDK with service URLs
        
        Args:
            config: Dictionary containing service URLs
                - authServiceUrl: Authentication service URL
                - dataServiceUrl: Data service URL  
                - privacyServiceUrl: Privacy service URL
                - blockchainServiceUrl: Blockchain service URL
        """
        self.logger = logging.getLogger(__name__)
        
        # Service URLs
        self.auth_service_url = config.get('authServiceUrl', 'http://localhost:3001')
        self.data_service_url = config.get('dataServiceUrl', 'http://localhost:8001')
        self.privacy_service_url = config.get('privacyServiceUrl', 'http://localhost:8002')
        self.blockchain_service_url = config.get('blockchainServiceUrl', 'http://localhost:8003')
        
        # Session management
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.permissions = []
        
        # Module configuration
        self.module_name = 'ml_feedback_pipeline'
        self.module_purpose = 'continuous_learning_and_model_improvement'
        
        self.logger.info(f"Abena SDK initialized for {self.module_name}")
    
    def authenticate(self, username: str = None, password: str = None, api_key: str = None) -> bool:
        """Authenticate with Abena authentication service"""
        try:
            auth_payload = {
                'module_name': self.module_name,
                'module_purpose': self.module_purpose
            }
            
            if username and password:
                auth_payload.update({
                    'username': username,
                    'password': password
                })
            elif api_key:
                auth_payload.update({
                    'api_key': api_key
                })
            else:
                # Try to use stored credentials or environment variables
                auth_payload.update({
                    'auto_auth': True
                })
            
            response = self.session.post(
                f"{self.auth_service_url}/authenticate",
                json=auth_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data.get('token')
                self.user_id = auth_data.get('user_id')
                self.permissions = auth_data.get('permissions', [])
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.logger.info(f"Authentication successful for user {self.user_id}")
                return True
            else:
                self.logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def get_patient_data(self, patient_id: str, purpose: str = None) -> Dict[str, Any]:
        """
        Get patient data with automatic privacy and permission handling
        
        Args:
            patient_id: Patient identifier
            purpose: Purpose for data access (defaults to module purpose)
        
        Returns:
            Patient data dictionary
        """
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        purpose = purpose or self.module_purpose
        
        try:
            # Request patient data with privacy controls
            response = self.session.get(
                f"{self.data_service_url}/patients/{patient_id}",
                params={
                    'purpose': purpose,
                    'module': self.module_name,
                    'user_id': self.user_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                patient_data = response.json()
                
                # Log data access for audit
                self._log_data_access('read', 'patient_data', patient_id, purpose)
                
                return patient_data
            else:
                self.logger.error(f"Failed to get patient data: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting patient data: {e}")
            return {}
    
    def get_treatment_data(self, treatment_id: str, purpose: str = None) -> Dict[str, Any]:
        """Get treatment data with automatic privacy handling"""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        purpose = purpose or self.module_purpose
        
        try:
            response = self.session.get(
                f"{self.data_service_url}/treatments/{treatment_id}",
                params={
                    'purpose': purpose,
                    'module': self.module_name,
                    'user_id': self.user_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                treatment_data = response.json()
                self._log_data_access('read', 'treatment_data', treatment_id, purpose)
                return treatment_data
            else:
                self.logger.error(f"Failed to get treatment data: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting treatment data: {e}")
            return {}
    
    def get_outcome_data(self, patient_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get outcome data for a patient with privacy controls"""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.session.get(
                f"{self.data_service_url}/outcomes",
                params={
                    'patient_id': patient_id,
                    'from_date': cutoff_date,
                    'purpose': self.module_purpose,
                    'module': self.module_name,
                    'user_id': self.user_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                outcomes = response.json()
                self._log_data_access('read', 'outcome_data', patient_id, f'last_{days}_days')
                return outcomes
            else:
                self.logger.error(f"Failed to get outcome data: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting outcome data: {e}")
            return []
    
    def save_model_data(self, model_id: str, model_data: Dict[str, Any], 
                       purpose: str = None) -> bool:
        """Save model data with encryption and audit logging"""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        purpose = purpose or self.module_purpose
        
        try:
            # Encrypt sensitive model data
            encrypted_data = self._encrypt_model_data(model_data)
            
            response = self.session.post(
                f"{self.data_service_url}/models",
                json={
                    'model_id': model_id,
                    'data': encrypted_data,
                    'purpose': purpose,
                    'module': self.module_name,
                    'user_id': self.user_id,
                    'metadata': {
                        'created_at': datetime.now().isoformat(),
                        'model_type': model_data.get('model_type', 'unknown'),
                        'version': model_data.get('version', '1.0')
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self._log_data_access('write', 'model_data', model_id, purpose)
                return True
            else:
                self.logger.error(f"Failed to save model data: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saving model data: {e}")
            return False
    
    def get_model_data(self, model_id: str, purpose: str = None) -> Dict[str, Any]:
        """Get model data with decryption and audit logging"""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        purpose = purpose or self.module_purpose
        
        try:
            response = self.session.get(
                f"{self.data_service_url}/models/{model_id}",
                params={
                    'purpose': purpose,
                    'module': self.module_name,
                    'user_id': self.user_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                model_data = response.json()
                decrypted_data = self._decrypt_model_data(model_data.get('data', {}))
                self._log_data_access('read', 'model_data', model_id, purpose)
                return decrypted_data
            else:
                self.logger.error(f"Failed to get model data: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting model data: {e}")
            return {}
    
    def save_insights(self, insights: List[Dict[str, Any]], 
                     patient_id: str = None, purpose: str = None) -> bool:
        """Save insights with privacy controls and audit logging"""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        purpose = purpose or self.module_purpose
        
        try:
            # Apply privacy controls to insights
            privacy_filtered_insights = self._apply_privacy_controls(insights, patient_id)
            
            response = self.session.post(
                f"{self.data_service_url}/insights",
                json={
                    'insights': privacy_filtered_insights,
                    'patient_id': patient_id,
                    'purpose': purpose,
                    'module': self.module_name,
                    'user_id': self.user_id,
                    'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'insight_count': len(insights)
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self._log_data_access('write', 'insights', patient_id or 'batch', purpose)
                return True
            else:
                self.logger.error(f"Failed to save insights: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saving insights: {e}")
            return False
    
    def push_to_emr(self, patient_id: str, data: Dict[str, Any], 
                   data_type: str = 'insights') -> Dict[str, Any]:
        """Push data to EMR with privacy and audit controls"""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            # Apply EMR-specific privacy controls
            emr_data = self._prepare_emr_data(data, data_type, patient_id)
            
            response = self.session.post(
                f"{self.data_service_url}/emr/push",
                json={
                    'patient_id': patient_id,
                    'data': emr_data,
                    'data_type': data_type,
                    'module': self.module_name,
                    'user_id': self.user_id,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self._log_data_access('write', f'emr_{data_type}', patient_id, 'emr_integration')
                return {
                    'success': True,
                    'emr_id': result.get('emr_id'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.logger.error(f"Failed to push to EMR: {response.status_code}")
                return {
                    'success': False,
                    'error': f"EMR push failed: {response.status_code}"
                }
                
        except Exception as e:
            self.logger.error(f"Error pushing to EMR: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_audit_log(self, entity_id: str = None, action: str = None, 
                     days: int = 30) -> List[Dict[str, Any]]:
        """Get audit log for compliance and monitoring"""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            params = {
                'from_date': cutoff_date,
                'module': self.module_name,
                'user_id': self.user_id
            }
            
            if entity_id:
                params['entity_id'] = entity_id
            if action:
                params['action'] = action
            
            response = self.session.get(
                f"{self.blockchain_service_url}/audit",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get audit log: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting audit log: {e}")
            return []
    
    def _log_data_access(self, action: str, data_type: str, entity_id: str, purpose: str):
        """Log data access for audit trail"""
        try:
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'data_type': data_type,
                'entity_id': entity_id,
                'purpose': purpose,
                'module': self.module_name,
                'user_id': self.user_id,
                'session_id': self.auth_token[:10] if self.auth_token else None
            }
            
            # Send to blockchain audit service
            self.session.post(
                f"{self.blockchain_service_url}/audit",
                json=audit_entry,
                timeout=10
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to log audit entry: {e}")
    
    def _encrypt_model_data(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive model data"""
        try:
            # Request encryption from privacy service
            response = self.session.post(
                f"{self.privacy_service_url}/encrypt",
                json={
                    'data': model_data,
                    'data_type': 'model_data',
                    'module': self.module_name
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning("Encryption failed, storing as-is")
                return model_data
                
        except Exception as e:
            self.logger.warning(f"Encryption error: {e}, storing as-is")
            return model_data
    
    def _decrypt_model_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt model data"""
        try:
            # Request decryption from privacy service
            response = self.session.post(
                f"{self.privacy_service_url}/decrypt",
                json={
                    'data': encrypted_data,
                    'data_type': 'model_data',
                    'module': self.module_name
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning("Decryption failed, returning encrypted data")
                return encrypted_data
                
        except Exception as e:
            self.logger.warning(f"Decryption error: {e}, returning encrypted data")
            return encrypted_data
    
    def _apply_privacy_controls(self, insights: List[Dict[str, Any]], 
                               patient_id: str = None) -> List[Dict[str, Any]]:
        """Apply privacy controls to insights"""
        try:
            # Request privacy filtering from privacy service
            response = self.session.post(
                f"{self.privacy_service_url}/filter",
                json={
                    'data': insights,
                    'data_type': 'insights',
                    'patient_id': patient_id,
                    'module': self.module_name,
                    'user_id': self.user_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning("Privacy filtering failed, returning original data")
                return insights
                
        except Exception as e:
            self.logger.warning(f"Privacy filtering error: {e}, returning original data")
            return insights
    
    def _prepare_emr_data(self, data: Dict[str, Any], data_type: str, 
                         patient_id: str) -> Dict[str, Any]:
        """Prepare data for EMR integration with privacy controls"""
        try:
            # Request EMR formatting from privacy service
            response = self.session.post(
                f"{self.privacy_service_url}/emr-format",
                json={
                    'data': data,
                    'data_type': data_type,
                    'patient_id': patient_id,
                    'module': self.module_name,
                    'user_id': self.user_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning("EMR formatting failed, returning original data")
                return data
                
        except Exception as e:
            self.logger.warning(f"EMR formatting error: {e}, returning original data")
            return data
    
    def check_permissions(self, required_permissions: List[str]) -> bool:
        """Check if user has required permissions"""
        if not self.permissions:
            return False
        
        return all(perm in self.permissions for perm in required_permissions)
    
    def logout(self):
        """Logout and clear session"""
        try:
            if self.auth_token:
                self.session.post(
                    f"{self.auth_service_url}/logout",
                    json={'token': self.auth_token},
                    timeout=10
                )
        except Exception as e:
            self.logger.warning(f"Logout error: {e}")
        finally:
            self.auth_token = None
            self.user_id = None
            self.permissions = []
            self.session.headers.pop('Authorization', None)
            self.logger.info("Logged out successfully") 