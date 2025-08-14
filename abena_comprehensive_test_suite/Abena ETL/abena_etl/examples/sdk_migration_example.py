#!/usr/bin/env python3
"""
Example: Migrating a Module to Abena SDK

This example shows how to migrate an existing module from custom
authentication and data handling to the Abena SDK Universal Integration Pattern.
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# BEFORE: Custom imports (❌ Remove these)
# import sqlalchemy
# from sqlalchemy.orm import sessionmaker
# import jwt
# import redis
# from custom_auth import CustomAuth
# from custom_database import DatabaseConnection

# AFTER: Abena SDK import (✅ Add this)
from abena_sdk import AbenaClient


# BEFORE: Custom implementation (❌ Remove this)
"""
class PatientDataModule:
    def __init__(self):
        # Custom database connection
        self.engine = sqlalchemy.create_engine('postgresql://user:pass@localhost/db')
        self.Session = sessionmaker(bind=self.engine)
        
        # Custom authentication
        self.auth_system = CustomAuth()
        
        # Custom cache
        self.cache = redis.Redis(host='localhost', port=6379, db=0)
    
    def get_patient_data(self, patient_id: str, user_id: str) -> Dict[str, Any]:
        # Manual permission check
        if not self.auth_system.check_permission(user_id, 'read:patient', patient_id):
            raise PermissionError(f"User {user_id} lacks permission to read patient {patient_id}")
        
        # Manual database query
        session = self.Session()
        try:
            patient = session.query(Patient).filter_by(id=patient_id).first()
            if not patient:
                raise ValueError(f"Patient {patient_id} not found")
            return patient.to_dict()
        finally:
            session.close()
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        # Custom authentication logic
        return self.auth_system.authenticate(username, password)
    
    def check_permission(self, user_id: str, permission: str, resource_id: str = None) -> bool:
        # Custom permission checking
        return self.auth_system.check_permission(user_id, permission, resource_id)
    
    def get_patient_predictions(self, patient_id: str, user_id: str) -> List[Dict[str, Any]]:
        # Manual permission check
        if not self.check_permission(user_id, 'analytics:predict', patient_id):
            raise PermissionError(f"User {user_id} lacks permission for predictions")
        
        # Manual analytics call
        session = self.Session()
        try:
            # Custom prediction logic
            predictions = self._run_custom_prediction_model(patient_id)
            return predictions
        finally:
            session.close()
    
    def _run_custom_prediction_model(self, patient_id: str) -> List[Dict[str, Any]]:
        # Custom ML model implementation
        # ... complex ML logic ...
        return [{"prediction": "sample", "confidence": 0.8}]
"""


# AFTER: Abena SDK implementation (✅ Use this)
class PatientDataModule:
    """
    Patient Data Module using Abena SDK Universal Integration Pattern
    
    Benefits:
    - Automatic authentication and authorization
    - Centralized data handling with privacy and encryption
    - Automatic audit logging
    - Focus on business logic instead of infrastructure
    """
    
    def __init__(self):
        # Initialize Abena SDK (Universal Integration Pattern)
        self.abena = AbenaClient({
            'api_base_url': 'https://api.abena.com',
            'client_id': os.getenv('ABENA_CLIENT_ID'),
            'client_secret': os.getenv('ABENA_CLIENT_SECRET')
        })
    
    def get_patient_data(self, patient_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get patient data with automatic auth, privacy, and audit handling
        
        Args:
            patient_id: Patient identifier
            user_id: User requesting the data
            
        Returns:
            Patient data with metadata
        """
        # 1. Auto-handled auth & permissions
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        patient_data = self.abena.get_patient_data(
            patient_id=patient_id,
            user_id=user_id,
            purpose='clinical_decision_support'
        )
        
        # 4. Focus on your business logic
        return self._process_patient_data(patient_data.data)
    
    def get_patient_observations(self, patient_id: str, user_id: str,
                                observation_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get patient observations with automatic auth handling
        """
        # Auto-handled auth & permissions
        observation_data = self.abena.get_observation_data(
            patient_id=patient_id,
            user_id=user_id,
            observation_type=observation_type
        )
        
        # Focus on business logic
        return self._process_observations(observation_data.data)
    
    def get_patient_predictions(self, patient_id: str, user_id: str,
                               model_type: str = "treatment_response") -> List[Dict[str, Any]]:
        """
        Get patient predictions with automatic auth and audit handling
        """
        # Prepare input data for prediction
        input_data = {
            "patient_id": patient_id,
            "model_type": model_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Auto-handled auth & permissions
        prediction_response = self.abena.get_prediction(
            patient_id=patient_id,
            user_id=user_id,
            model_type=model_type,
            input_data=input_data,
            purpose='treatment_planning'
        )
        
        # Focus on business logic
        return self._process_predictions(prediction_response)
    
    def get_treatment_recommendations(self, patient_id: str, user_id: str,
                                    condition: str) -> List[Dict[str, Any]]:
        """
        Get treatment recommendations with automatic auth handling
        """
        # Auto-handled auth & permissions
        recommendations = self.abena.get_treatment_recommendations(
            patient_id=patient_id,
            user_id=user_id,
            condition=condition
        )
        
        # Focus on business logic
        return self._process_recommendations(recommendations)
    
    def get_patient_insights(self, patient_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get patient insights with automatic auth handling
        """
        # Auto-handled auth & permissions
        insights = self.abena.get_patient_insights(
            patient_id=patient_id,
            user_id=user_id,
            insight_types=['trends', 'anomalies', 'correlations']
        )
        
        # Focus on business logic
        return self._process_insights(insights)
    
    def transform_emr_data(self, source_data: Dict[str, Any], source_system: str,
                          user_id: str) -> Dict[str, Any]:
        """
        Transform EMR data with automatic auth handling
        """
        # Auto-handled auth & permissions
        transformed_data = self.abena.transform_emr_data(
            source_data=source_data,
            source_system=source_system,
            user_id=user_id,
            target_format="FHIR"
        )
        
        # Focus on business logic
        return self._process_transformed_data(transformed_data)
    
    # Business logic methods (focus on these instead of infrastructure)
    def _process_patient_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process patient data for business requirements"""
        # Add business-specific processing
        processed_data = {
            "patient_info": data,
            "processed_at": datetime.now().isoformat(),
            "business_rules_applied": True
        }
        return processed_data
    
    def _process_observations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process observation data for business requirements"""
        # Add business-specific processing
        return {
            "observations": data,
            "analysis_complete": True
        }
    
    def _process_predictions(self, prediction_response) -> List[Dict[str, Any]]:
        """Process prediction response for business requirements"""
        # Add business-specific processing
        return [{
            "prediction": prediction_response.prediction,
            "confidence": prediction_response.confidence,
            "model_version": prediction_response.model_version,
            "business_interpretation": "High confidence prediction"
        }]
    
    def _process_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process recommendations for business requirements"""
        # Add business-specific processing
        return [{
            **rec,
            "business_priority": "high" if rec.get("confidence", 0) > 0.8 else "medium"
        } for rec in recommendations]
    
    def _process_insights(self, insights) -> List[Dict[str, Any]]:
        """Process insights for business requirements"""
        # Add business-specific processing
        return [{
            "insight_type": insight.insight_type,
            "value": insight.value,
            "confidence": insight.confidence,
            "business_impact": "high" if insight.confidence > 0.7 else "medium"
        } for insight in insights]
    
    def _process_transformed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process transformed data for business requirements"""
        # Add business-specific processing
        return {
            "transformed_data": data,
            "validation_status": "passed",
            "business_ready": True
        }


# Example usage
def main():
    """Example usage of the migrated module"""
    print("🏥 Abena SDK Migration Example")
    print("=" * 50)
    
    # Initialize the module
    module = PatientDataModule()
    
    # Example: Get patient data
    try:
        patient_data = module.get_patient_data(
            patient_id="PATIENT_123",
            user_id="DR_SMITH"
        )
        print(f"✅ Retrieved patient data: {patient_data}")
        
        # Example: Get predictions
        predictions = module.get_patient_predictions(
            patient_id="PATIENT_123",
            user_id="DR_SMITH",
            model_type="treatment_response"
        )
        print(f"✅ Retrieved predictions: {predictions}")
        
        # Example: Get treatment recommendations
        recommendations = module.get_treatment_recommendations(
            patient_id="PATIENT_123",
            user_id="DR_SMITH",
            condition="diabetes"
        )
        print(f"✅ Retrieved recommendations: {recommendations}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 