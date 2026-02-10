"""
Abena SDK Client

Main client implementing the Abena Universal Integration Pattern.
All modules should use this client instead of implementing their own
authentication, authorization, and data handling.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from .config import AbenaConfig
from .auth import AbenaAuth, AuthToken, UserPermissions
from .data import DataTransformer, FHIRConverter, DataRequest, DataResponse
from .analytics import AnalyticsEngine, PredictionRequest, PredictionResponse, AnalyticsInsight
from .exceptions import AbenaException, AuthenticationError, AuthorizationError


class AbenaClient:
    """
    Abena SDK Client - Universal Integration Pattern Implementation
    
    This client provides a unified interface for all Abena operations:
    - Automatic authentication and authorization
    - Centralized data handling with privacy and encryption
    - Automatic audit logging
    - Business logic focus for modules
    """
    
    def __init__(self, config: Optional[Union[AbenaConfig, Dict[str, Any]]] = None):
        """
        Initialize Abena SDK Client
        
        Args:
            config: AbenaConfig instance or configuration dictionary
        """
        # Initialize configuration
        if isinstance(config, dict):
            self.config = AbenaConfig.from_dict(config)
        elif isinstance(config, AbenaConfig):
            self.config = config
        else:
            self.config = AbenaConfig.from_env()
        
        # Initialize logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format=self.config.log_format
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize SDK components
        self.auth = AbenaAuth(self.config)
        self.data = DataTransformer(self.config)
        self.fhir = FHIRConverter(self.config)
        self.analytics = AnalyticsEngine(self.config)
        
        # Auto-authenticate if credentials are available
        self._auto_authenticate()
    
    def _auto_authenticate(self):
        """Auto-authenticate if credentials are available"""
        try:
            if self.config.access_token:
                self.auth.authenticate_with_token(self.config.access_token)
                self.logger.info("Authenticated with access token")
            elif self.config.client_id and self.config.client_secret:
                self.auth.authenticate()
                self.logger.info("Authenticated with client credentials")
        except Exception as e:
            self.logger.warning(f"Auto-authentication failed: {e}")
    
    # ============================================================================
    # UNIVERSAL DATA ACCESS METHODS
    # ============================================================================
    
    def get_patient_data(self, patient_id: str, user_id: str, 
                        purpose: str, scope: Optional[str] = None,
                        filters: Optional[Dict[str, Any]] = None) -> DataResponse:
        """
        Get patient data with automatic auth, privacy, and audit handling
        
        Args:
            patient_id: Patient identifier
            user_id: User requesting the data
            purpose: Purpose of data access (for audit logging)
            scope: Data scope (e.g., 'vitals', 'medications', 'all')
            filters: Optional filters for data retrieval
            
        Returns:
            DataResponse with patient data and metadata
        """
        # 1. Auto-handled auth & permissions
        if not self.auth.check_permission(user_id, "read:patient", patient_id):
            raise AuthorizationError(f"User {user_id} lacks permission to read patient {patient_id}")
        
        # 2. Create data request
        request = DataRequest(
            resource_type="Patient",
            resource_id=patient_id,
            user_id=user_id,
            purpose=purpose,
            scope=scope,
            filters=filters
        )
        
        # 3. Auto-handled privacy & encryption (handled by data service)
        # 4. Auto-handled audit logging (handled by data service)
        
        # 5. Focus on business logic - get the data
        try:
            # This would call the centralized data service
            # For now, we'll simulate the response
            data = {
                "patient_id": patient_id,
                "data": f"Patient data for {patient_id}",
                "scope": scope or "all",
                "filters": filters
            }
            
            return DataResponse(
                data=data,
                resource_type="Patient",
                resource_id=patient_id,
                timestamp=datetime.now(),
                version="1.0",
                source="abena_sdk",
                audit_trail={
                    "user_id": user_id,
                    "purpose": purpose,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get patient data: {e}")
            raise AbenaException(f"Failed to get patient data: {str(e)}")
    
    def get_observation_data(self, patient_id: str, user_id: str,
                           observation_type: Optional[str] = None,
                           date_range: Optional[Dict[str, str]] = None) -> DataResponse:
        """
        Get observation data with automatic auth and privacy handling
        """
        # Check permissions
        if not self.auth.check_permission(user_id, "read:observations", patient_id):
            raise AuthorizationError(f"User {user_id} lacks permission to read observations for patient {patient_id}")
        
        # Create filters
        filters = {}
        if observation_type:
            filters["type"] = observation_type
        if date_range:
            filters["date_range"] = date_range
        
        return self.get_patient_data(
            patient_id=patient_id,
            user_id=user_id,
            purpose="clinical_decision_support",
            scope="observations",
            filters=filters
        )
    
    # ============================================================================
    # UNIVERSAL ANALYTICS METHODS
    # ============================================================================
    
    def get_prediction(self, patient_id: str, user_id: str, model_type: str,
                      input_data: Dict[str, Any], purpose: str) -> PredictionResponse:
        """
        Get prediction with automatic auth and audit handling
        """
        # Check permissions
        if not self.auth.check_permission(user_id, "analytics:predict", patient_id):
            raise AuthorizationError(f"User {user_id} lacks permission for predictions on patient {patient_id}")
        
        # Create prediction request
        request = PredictionRequest(
            patient_id=patient_id,
            model_type=model_type,
            input_data=input_data,
            user_id=user_id,
            purpose=purpose
        )
        
        # Get prediction from analytics engine
        return self.analytics.get_prediction(request)
    
    def get_treatment_recommendations(self, patient_id: str, user_id: str,
                                    condition: str) -> List[Dict[str, Any]]:
        """
        Get treatment recommendations with automatic auth handling
        """
        # Check permissions
        if not self.auth.check_permission(user_id, "analytics:recommendations", patient_id):
            raise AuthorizationError(f"User {user_id} lacks permission for recommendations on patient {patient_id}")
        
        return self.analytics.get_treatment_recommendations(patient_id, condition, user_id)
    
    def get_patient_insights(self, patient_id: str, user_id: str,
                           insight_types: Optional[List[str]] = None) -> List[AnalyticsInsight]:
        """
        Get patient insights with automatic auth handling
        """
        # Check permissions
        if not self.auth.check_permission(user_id, "analytics:insights", patient_id):
            raise AuthorizationError(f"User {user_id} lacks permission for insights on patient {patient_id}")
        
        return self.analytics.get_patient_insights(patient_id, user_id, insight_types)
    
    # ============================================================================
    # UNIVERSAL DATA TRANSFORMATION METHODS
    # ============================================================================
    
    def transform_emr_data(self, source_data: Dict[str, Any], source_system: str,
                          user_id: str, target_format: str = "FHIR") -> Dict[str, Any]:
        """
        Transform EMR data with automatic auth handling
        """
        # Check permissions
        if not self.auth.check_permission(user_id, "data:transform"):
            raise AuthorizationError(f"User {user_id} lacks permission for data transformation")
        
        return self.data.transform_emr_data(source_data, source_system, target_format)
    
    def convert_to_fhir(self, data: Dict[str, Any], resource_type: str,
                       user_id: str) -> Dict[str, Any]:
        """
        Convert data to FHIR format with automatic auth handling
        """
        # Check permissions
        if not self.auth.check_permission(user_id, "fhir:convert"):
            raise AuthorizationError(f"User {user_id} lacks permission for FHIR conversion")
        
        return self.fhir.convert_to_fhir(data, resource_type)
    
    # ============================================================================
    # AUTHENTICATION AND AUTHORIZATION METHODS
    # ============================================================================
    
    def authenticate(self, client_id: Optional[str] = None,
                    client_secret: Optional[str] = None) -> AuthToken:
        """Authenticate with the Abena system"""
        return self.auth.authenticate(client_id, client_secret)
    
    def get_user_permissions(self, user_id: str) -> UserPermissions:
        """Get user permissions"""
        return self.auth.get_user_permissions(user_id)
    
    def check_permission(self, user_id: str, permission: str,
                        resource_id: Optional[str] = None) -> bool:
        """Check if user has specific permission"""
        return self.auth.check_permission(user_id, permission, resource_id)
    
    def logout(self):
        """Logout and clear authentication state"""
        self.auth.logout()
        self.logger.info("Logged out successfully")
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health information"""
        return {
            "sdk_version": "1.0.0",
            "config": self.config.to_dict(),
            "auth_status": "authenticated" if self.auth._token else "not_authenticated",
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_caches(self):
        """Clear all SDK caches"""
        self.analytics.clear_cache()
        self.data._mapping_cache.clear()
        self.logger.info("All caches cleared") 