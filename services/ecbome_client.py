"""
eCBome Client for Quantum Healthcare Service
Fetches eCBome biomarker data from eCBome Intelligence API
"""

import os
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ECBomeClient:
    """Client for interacting with eCBome Intelligence API"""
    
    def __init__(self):
        self.base_url = os.getenv('ECBOME_API', os.getenv('ECDOME_API', 'http://abena-ecdome-intelligence:4005'))
        self.timeout = 30.0
    
    async def get_latest_biomarkers(self, patient_id: str, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch latest eCBome biomarkers for a patient"""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try different endpoint variations
                endpoints = [
                    f"{self.base_url}/api/patients/{patient_id}/biomarkers",
                    f"{self.base_url}/api/ecbome/patients/{patient_id}/biomarkers",
                    f"{self.base_url}/api/v1/patients/{patient_id}/ecbome",
                ]
                
                for endpoint in endpoints:
                    try:
                        response = await client.get(endpoint, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            # Extract biomarkers if nested
                            if isinstance(data, dict) and 'biomarkers' in data:
                                return data['biomarkers']
                            elif isinstance(data, dict) and 'data' in data:
                                return data['data']
                            return data
                    except Exception as e:
                        logger.debug(f"Endpoint {endpoint} failed: {e}")
                        continue
                
                logger.warning(f"No eCBome biomarkers found for patient {patient_id}")
                return None
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching eCBome biomarkers for {patient_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching eCBome biomarkers: {e}")
            return None
    
    async def get_ecbome_analysis(self, patient_id: str, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch eCBome analysis for a patient"""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                endpoints = [
                    f"{self.base_url}/api/patients/{patient_id}/analysis",
                    f"{self.base_url}/api/ecbome/patients/{patient_id}/analysis",
                ]
                
                for endpoint in endpoints:
                    try:
                        response = await client.get(endpoint, headers=headers)
                        if response.status_code == 200:
                            return response.json()
                    except Exception:
                        continue
                
                return None
        except Exception as e:
            logger.error(f"Error fetching eCBome analysis: {e}")
            return None

# Create singleton instance
ecbome_client = ECBomeClient()

# For backward compatibility
ECDomeClient = ECBomeClient
ecdome_client = ecbome_client








