"""
Example Module - Demonstrating Abena SDK Integration Pattern
This module shows the correct way to use the Abena SDK instead of implementing
your own authentication and data access systems.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from abena_sdk import AbenaSDK, AbenaSDKConfig

logger = logging.getLogger(__name__)

class ExampleModule:
    """
    Example module demonstrating Abena SDK integration
    
    BEFORE (❌ Wrong - has its own auth/data):
    class SomeModule {
      constructor() {
        this.database = new Database();
        this.authSystem = new CustomAuth();
      }
    }
    
    AFTER (✅ Correct - uses Abena SDK):
    """
    
    def __init__(self):
        # Initialize Abena SDK for centralized services
        self.abena = AbenaSDK(AbenaSDKConfig(
            auth_service_url='http://localhost:3001',
            data_service_url='http://localhost:8001',
            privacy_service_url='http://localhost:8002',
            blockchain_service_url='http://localhost:8003'
        ))
        
        self.logger = logging.getLogger(__name__)
    
    async def some_method(self, patient_id: str, user_id: str) -> Dict[str, Any]:
        """
        Example method demonstrating Abena SDK usage
        
        This method shows how to:
        1. Auto-handled auth & permissions
        2. Auto-handled privacy & encryption  
        3. Auto-handled audit logging
        4. Focus on your business logic
        """
        try:
            # 1. Auto-handled auth & permissions
            patient_data = await self.abena.get_patient_data(patient_id, 'module_purpose')
            
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            return self.process_data(patient_data)
            
        except Exception as e:
            self.logger.error(f"Error in some_method: {str(e)}")
            raise
    
    def process_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process patient data - focus on business logic"""
        # Your business logic here
        processed_result = {
            'patient_id': patient_data.get('patient_id'),
            'processed_at': datetime.now().isoformat(),
            'data_summary': {
                'total_records': len(patient_data.get('records', [])),
                'last_updated': patient_data.get('last_updated'),
                'data_quality': patient_data.get('data_quality', 'unknown')
            }
        }
        
        return processed_result
    
    async def save_analysis_result(self, patient_id: str, analysis_data: Dict[str, Any]) -> str:
        """
        Save analysis results using Abena SDK
        
        Demonstrates:
        - Automatic privacy controls
        - Blockchain verification
        - Audit logging
        """
        try:
            # 1. Auto-handled auth & permissions
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            record_id = await self.abena.save_outcome_data(
                patient_id, 
                analysis_data, 
                'analysis_result'
            )
            
            self.logger.info(f"Analysis result saved with record ID: {record_id}")
            return record_id
            
        except Exception as e:
            self.logger.error(f"Error saving analysis result: {str(e)}")
            raise
    
    async def get_patient_history(self, patient_id: str, 
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> list:
        """
        Get patient history with privacy controls
        """
        try:
            # 1. Auto-handled auth & permissions
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            history = await self.abena.get_outcome_history(patient_id, start_date, end_date)
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting patient history: {str(e)}")
            raise
    
    async def validate_user_permissions(self, user_id: str, patient_id: str, action: str) -> bool:
        """
        Validate user permissions using Abena SDK
        """
        try:
            # 1. Auto-handled auth & permissions
            return await self.abena.check_permissions(user_id, patient_id, action)
            
        except Exception as e:
            self.logger.error(f"Error checking permissions: {str(e)}")
            return False
    
    async def get_data_quality_report(self, patient_id: str) -> Dict[str, Any]:
        """
        Get data quality metrics using Abena SDK
        """
        try:
            # 1. Auto-handled auth & permissions
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            quality_metrics = await self.abena.get_data_quality_metrics(patient_id)
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting quality metrics: {str(e)}")
            raise

# Example usage
async def main():
    """Example usage of the module"""
    
    # Create module instance
    module = ExampleModule()
    
    # Example patient and user IDs
    patient_id = "patient_123"
    user_id = "user_456"
    
    try:
        # Use the module methods
        result = await module.some_method(patient_id, user_id)
        print(f"Processed result: {result}")
        
        # Check permissions
        has_permission = await module.validate_user_permissions(user_id, patient_id, "read")
        print(f"User has read permission: {has_permission}")
        
        # Get data quality report
        quality_report = await module.get_data_quality_report(patient_id)
        print(f"Quality report: {quality_report}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 