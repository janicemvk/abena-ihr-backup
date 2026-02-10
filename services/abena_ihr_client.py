"""
ABENA IHR Client for Quantum Healthcare Service
Fetches patient data from ABENA IHR Core API
"""

import os
import httpx
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class AbenaIHRClient:
    """Client for interacting with ABENA IHR Core API"""
    
    def __init__(self):
        self.base_url = os.getenv('ABENA_IHR_API', 'http://abena-ihr:4002')
        self.timeout = 30.0
    
    async def get_patient_data(self, patient_id: str, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch patient data from ABENA IHR"""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/patients/{patient_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Patient {patient_id} not found in ABENA IHR")
                    return None
                else:
                    logger.error(f"Error fetching patient data: {response.status_code} - {response.text}")
                    return None
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching patient data for {patient_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching patient data: {e}")
            return None
    
    async def get_patient_prescriptions(self, patient_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch patient prescriptions from ABENA IHR"""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/prescriptions",
                    params={"patient_id": patient_id},
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Handle both list and dict responses
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'prescriptions' in data:
                        return data['prescriptions']
                    elif isinstance(data, dict) and 'data' in data:
                        return data['data']
                    return []
                else:
                    logger.warning(f"Error fetching prescriptions: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching prescriptions: {e}")
            return []
    
    async def get_patient_lab_results(self, patient_id: str, token: str) -> List[Dict[str, Any]]:
        """Fetch patient lab results from ABENA IHR"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/lab-results",
                    params={"patient_id": patient_id},
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'results' in data:
                        return data['results']
                    elif isinstance(data, dict) and 'data' in data:
                        return data['data']
                    return []
                else:
                    logger.warning(f"Error fetching lab results: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching lab results: {e}")
            return []
    
    async def get_patient_documents(self, patient_id: str, token: str) -> List[Dict[str, Any]]:
        """Fetch patient documents from ABENA IHR"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/documents",
                    params={"patient_id": patient_id},
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'documents' in data:
                        return data['documents']
                    elif isinstance(data, dict) and 'data' in data:
                        return data['data']
                    return []
                else:
                    logger.warning(f"Error fetching documents: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            return []
    
    async def get_comprehensive_patient_data(self, patient_id: str, token: str) -> Dict[str, Any]:
        """Fetch all available patient data"""
        patient_data = await self.get_patient_data(patient_id, token)
        prescriptions = await self.get_patient_prescriptions(patient_id, token)
        lab_results = await self.get_patient_lab_results(patient_id, token)
        documents = await self.get_patient_documents(patient_id, token)
        
        return {
            "patient": patient_data,
            "prescriptions": prescriptions,
            "lab_results": lab_results,
            "documents": documents
        }

# Global instance
ihr_client = AbenaIHRClient()



