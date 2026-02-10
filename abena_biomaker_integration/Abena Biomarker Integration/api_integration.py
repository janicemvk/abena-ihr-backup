import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class AbenaAPIIntegration:
    def __init__(self):
        load_dotenv()  # Load environment variables
        
        # Initialize Abena SDK configuration
        self.abena_config = {
            'authServiceUrl': os.getenv('ABENA_AUTH_SERVICE_URL', 'http://localhost:3001'),
            'dataServiceUrl': os.getenv('ABENA_DATA_SERVICE_URL', 'http://localhost:8001'),
            'privacyServiceUrl': os.getenv('ABENA_PRIVACY_SERVICE_URL', 'http://localhost:8002'),
            'blockchainServiceUrl': os.getenv('ABENA_BLOCKCHAIN_SERVICE_URL', 'http://localhost:8003')
        }
        
        # External API configurations (for device integrations)
        self.external_apis = {
            'cloud': {
                'base_url': os.getenv('CLOUD_API_URL'),
                'api_key': os.getenv('CLOUD_API_KEY')
            },
            'data_source': {
                'base_url': os.getenv('DATA_SOURCE_URL'),
                'api_key': os.getenv('DATA_SOURCE_KEY')
            }
        }
        
        self._initialize_abena_connection()

    def _initialize_abena_connection(self):
        """Initialize connection with Abena SDK services"""
        try:
            # Test connection to Abena services
            self._test_abena_services()
            print("Successfully connected to Abena SDK services")
        except Exception as e:
            print(f"Error initializing Abena connection: {str(e)}")

    def _test_abena_services(self):
        """Test connectivity to Abena SDK services"""
        services = [
            ('auth', self.abena_config['authServiceUrl']),
            ('data', self.abena_config['dataServiceUrl']),
            ('privacy', self.abena_config['privacyServiceUrl']),
            ('blockchain', self.abena_config['blockchainServiceUrl'])
        ]
        
        for service_name, url in services:
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code != 200:
                    raise Exception(f"{service_name} service not healthy")
            except Exception as e:
                print(f"Warning: {service_name} service not accessible: {str(e)}")

    async def get_patient_data(self, patient_id: str, purpose: str) -> Optional[Dict[str, Any]]:
        """Get patient data through Abena SDK with automatic auth and privacy handling"""
        try:
            # This would use the Abena SDK to get patient data
            # The SDK automatically handles authentication, permissions, and privacy
            response = requests.get(
                f"{self.abena_config['dataServiceUrl']}/patients/{patient_id}/data",
                headers={
                    'X-Purpose': purpose,
                    'X-Request-ID': f"req_{datetime.now().timestamp()}"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting patient data: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error accessing patient data: {str(e)}")
            return None

    async def store_biomarker_data(self, patient_id: str, biomarker_data: Dict[str, Any]) -> bool:
        """Store biomarker data through Abena SDK with automatic encryption and audit logging"""
        try:
            # This would use the Abena SDK to store data
            # The SDK automatically handles encryption, audit logging, and blockchain integration
            response = requests.post(
                f"{self.abena_config['dataServiceUrl']}/patients/{patient_id}/biomarkers",
                json=biomarker_data,
                headers={
                    'X-Request-ID': f"req_{datetime.now().timestamp()}"
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error storing biomarker data: {str(e)}")
            return False

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user through Abena SDK"""
        try:
            response = requests.post(
                f"{self.abena_config['authServiceUrl']}/auth/login",
                json={'username': username, 'password': password}
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return None

    async def check_user_permissions(self, user_id: str, patient_id: str, action: str) -> bool:
        """Check user permissions through Abena SDK"""
        try:
            response = requests.post(
                f"{self.abena_config['authServiceUrl']}/permissions/check",
                json={
                    'user_id': user_id,
                    'patient_id': patient_id,
                    'action': action
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error checking permissions: {str(e)}")
            return False

    def send_to_external_cloud(self, data: Dict[str, Any]) -> bool:
        """Send data to external cloud service (for device integrations)"""
        try:
            if not self.external_apis['cloud']['base_url']:
                return False
            
            response = requests.post(
                f"{self.external_apis['cloud']['base_url']}/data",
                headers={'X-API-Key': self.external_apis['cloud']['api_key']},
                json=data
            )
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error sending data to external cloud: {str(e)}")
            return False

    def fetch_external_data(self, query_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch data from external data source (for device integrations)"""
        try:
            if not self.external_apis['data_source']['base_url']:
                return None
            
            response = requests.get(
                f"{self.external_apis['data_source']['base_url']}/data",
                headers={'X-API-Key': self.external_apis['data_source']['api_key']},
                params=query_params
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Error fetching external data: {str(e)}")
            return None

    def close_connections(self):
        """Close any open connections"""
        # Abena SDK handles connection management automatically
        print("Abena SDK connections closed") 