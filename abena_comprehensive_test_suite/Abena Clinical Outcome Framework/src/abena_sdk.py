"""
Abena SDK - Centralized Service Integration Layer
Provides unified access to authentication, data access, privacy, and blockchain services
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import httpx
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

@dataclass
class AbenaSDKConfig:
    """Configuration for Abena SDK services"""
    auth_service_url: str = "http://localhost:3001"
    data_service_url: str = "http://localhost:8001"
    privacy_service_url: str = "http://localhost:8002"
    blockchain_service_url: str = "http://localhost:8003"
    timeout_seconds: int = 30
    retry_attempts: int = 3

class AbenaSDK:
    """
    Abena SDK - Centralized service integration layer
    
    Provides unified access to:
    - Authentication & authorization
    - Data access with automatic privacy controls
    - Audit logging
    - Blockchain verification
    """
    
    def __init__(self, config: Optional[AbenaSDKConfig] = None):
        self.config = config or AbenaSDKConfig()
        self.logger = logging.getLogger(__name__)
        self._auth_token = None
        self._token_expires = None
        
        # Initialize HTTP client with connection pooling
        self.http_client = httpx.AsyncClient(
            timeout=self.config.timeout_seconds,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid authentication token"""
        if (self._auth_token and self._token_expires and 
            datetime.utcnow() < self._token_expires):
            return True
        
        try:
            # Get service-to-service token
            response = await self.http_client.post(
                f"{self.config.auth_service_url}/auth/service-token",
                json={
                    "service_name": "clinical_outcomes_framework",
                    "permissions": ["read_patient_data", "write_outcomes", "audit_access"]
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self._auth_token = token_data["access_token"]
                self._token_expires = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                return True
            else:
                self.logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False
    
    async def _make_authenticated_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make an authenticated HTTP request with retry logic"""
        if not await self._ensure_authenticated():
            raise Exception("Failed to authenticate with Abena services")
        
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self._auth_token}"
        kwargs["headers"] = headers
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = await self.http_client.request(method, url, **kwargs)
                if response.status_code < 500:  # Don't retry client errors
                    return response
                
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                if attempt == self.config.retry_attempts - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)
        
        return response
    
    async def get_patient_data(self, patient_id: str, purpose: str, 
                             data_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get patient data with automatic privacy controls and audit logging
        
        Args:
            patient_id: Patient identifier
            purpose: Purpose of data access (e.g., 'clinical_assessment', 'research')
            data_types: Specific data types to retrieve (optional)
        
        Returns:
            Patient data with privacy controls applied
        """
        try:
            # Request data through privacy service
            response = await self._make_authenticated_request(
                "POST",
                f"{self.config.privacy_service_url}/data/patient/{patient_id}",
                json={
                    "purpose": purpose,
                    "data_types": data_types or ["demographics", "clinical_history", "medications"],
                    "request_timestamp": datetime.utcnow().isoformat(),
                    "access_level": "clinical_care"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Log audit trail
                await self._log_audit_event(
                    "data_access",
                    patient_id=patient_id,
                    purpose=purpose,
                    data_types=data_types,
                    success=True
                )
                
                return data["patient_data"]
            else:
                await self._log_audit_event(
                    "data_access",
                    patient_id=patient_id,
                    purpose=purpose,
                    data_types=data_types,
                    success=False,
                    error=response.text
                )
                raise Exception(f"Failed to get patient data: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error getting patient data: {str(e)}")
            raise
    
    async def save_outcome_data(self, patient_id: str, outcome_data: Dict[str, Any],
                              purpose: str = "clinical_assessment") -> str:
        """
        Save outcome data with privacy controls and blockchain verification
        
        Args:
            patient_id: Patient identifier
            outcome_data: Clinical outcome data to save
            purpose: Purpose of data storage
        
        Returns:
            Record ID of saved data
        """
        try:
            # Save through data service with privacy controls
            response = await self._make_authenticated_request(
                "POST",
                f"{self.config.data_service_url}/outcomes/{patient_id}",
                json={
                    "outcome_data": outcome_data,
                    "purpose": purpose,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data_quality": outcome_data.get("data_quality", "complete")
                }
            )
            
            if response.status_code == 201:
                result = response.json()
                record_id = result["record_id"]
                
                # Verify on blockchain
                await self._verify_on_blockchain(record_id, outcome_data)
                
                # Log audit trail
                await self._log_audit_event(
                    "data_save",
                    patient_id=patient_id,
                    record_id=record_id,
                    purpose=purpose,
                    success=True
                )
                
                return record_id
            else:
                await self._log_audit_event(
                    "data_save",
                    patient_id=patient_id,
                    purpose=purpose,
                    success=False,
                    error=response.text
                )
                raise Exception(f"Failed to save outcome data: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error saving outcome data: {str(e)}")
            raise
    
    async def get_outcome_history(self, patient_id: str, 
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get patient outcome history with privacy controls
        
        Args:
            patient_id: Patient identifier
            start_date: Start date for history (optional)
            end_date: End date for history (optional)
        
        Returns:
            List of outcome records
        """
        try:
            params = {"purpose": "clinical_care"}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            
            response = await self._make_authenticated_request(
                "GET",
                f"{self.config.data_service_url}/outcomes/{patient_id}/history",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                await self._log_audit_event(
                    "data_access",
                    patient_id=patient_id,
                    purpose="clinical_care",
                    data_types=["outcome_history"],
                    success=True
                )
                
                return data["outcomes"]
            else:
                await self._log_audit_event(
                    "data_access",
                    patient_id=patient_id,
                    purpose="clinical_care",
                    data_types=["outcome_history"],
                    success=False,
                    error=response.text
                )
                raise Exception(f"Failed to get outcome history: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error getting outcome history: {str(e)}")
            raise
    
    async def _verify_on_blockchain(self, record_id: str, data_hash: str) -> bool:
        """Verify data integrity on blockchain"""
        try:
            response = await self._make_authenticated_request(
                "POST",
                f"{self.config.blockchain_service_url}/verify",
                json={
                    "record_id": record_id,
                    "data_hash": data_hash,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("verified", False)
            else:
                self.logger.warning(f"Blockchain verification failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Blockchain verification error: {str(e)}")
            return False
    
    async def _log_audit_event(self, event_type: str, **kwargs) -> None:
        """Log audit event for compliance and security"""
        try:
            audit_data = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "clinical_outcomes_framework",
                **kwargs
            }
            
            await self._make_authenticated_request(
                "POST",
                f"{self.config.auth_service_url}/audit/log",
                json=audit_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {str(e)}")
    
    async def check_permissions(self, user_id: str, patient_id: str, 
                              action: str) -> bool:
        """
        Check if user has permission to perform action on patient data
        
        Args:
            user_id: User identifier
            patient_id: Patient identifier
            action: Action to perform (e.g., 'read', 'write', 'delete')
        
        Returns:
            True if user has permission
        """
        try:
            response = await self._make_authenticated_request(
                "POST",
                f"{self.config.auth_service_url}/permissions/check",
                json={
                    "user_id": user_id,
                    "patient_id": patient_id,
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("authorized", False)
            else:
                self.logger.warning(f"Permission check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Permission check error: {str(e)}")
            return False
    
    async def get_data_quality_metrics(self, patient_id: str) -> Dict[str, Any]:
        """
        Get data quality metrics for patient
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Data quality metrics
        """
        try:
            response = await self._make_authenticated_request(
                "GET",
                f"{self.config.data_service_url}/quality/{patient_id}/metrics"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get quality metrics: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error getting quality metrics: {str(e)}")
            raise
    
    async def validate_data_integrity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data integrity and quality
        
        Args:
            data: Data to validate
        
        Returns:
            Validation results
        """
        try:
            response = await self._make_authenticated_request(
                "POST",
                f"{self.config.data_service_url}/validate",
                json={
                    "data": data,
                    "validation_rules": ["completeness", "consistency", "accuracy"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Data validation failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Data validation error: {str(e)}")
            raise 