"""
EMR Connectors Module
Handles integration with Electronic Medical Record systems
"""

import asyncio
import json
import uuid
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

import httpx
from jose import jwt

class EMRConnector(ABC):
    """Abstract base class for EMR connectors"""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        pass
    
    @abstractmethod
    async def fetch_patients(self, last_updated: Optional[datetime] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def fetch_observations(self, patient_id: str, last_updated: Optional[datetime] = None) -> List[Dict[str, Any]]:
        pass

class EpicConnector(EMRConnector):
    def __init__(self, base_url: str, client_id: str, private_key: str):
        self.base_url = base_url
        self.client_id = client_id
        self.private_key = private_key
        self.access_token = None
        self.token_expires = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Epic using JWT"""
        try:
            # Create JWT assertion
            jwt_payload = {
                "iss": self.client_id,
                "sub": self.client_id,
                "aud": f"{self.base_url}/oauth2/token",
                "exp": int(time.time()) + 300,  # 5 minutes
                "iat": int(time.time()),
                "jti": str(uuid.uuid4())
            }
            
            assertion = jwt.encode(jwt_payload, self.private_key, algorithm="RS256")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                        "client_assertion": assertion
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    self.token_expires = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                    return True
                
                return False
        except Exception as e:
            logging.error(f"Epic authentication failed: {str(e)}")
            return False
    
    async def fetch_patients(self, last_updated: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch patient data from Epic FHIR API"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                url = f"{self.base_url}/api/FHIR/R4/Patient"
                
                if last_updated:
                    url += f"?_lastUpdated=gt{last_updated.isoformat()}"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    fhir_bundle = response.json()
                    return fhir_bundle.get("entry", [])
                
                return []
        except Exception as e:
            logging.error(f"Error fetching Epic patients: {str(e)}")
            return []
    
    async def fetch_observations(self, patient_id: str, last_updated: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch observation data for a patient from Epic"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                url = f"{self.base_url}/api/FHIR/R4/Observation?patient={patient_id}"
                
                if last_updated:
                    url += f"&_lastUpdated=gt{last_updated.isoformat()}"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    fhir_bundle = response.json()
                    return fhir_bundle.get("entry", [])
                
                return []
        except Exception as e:
            logging.error(f"Error fetching Epic observations: {str(e)}")
            return []

class CernerConnector(EMRConnector):
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Cerner using OAuth2"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/authorization/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    self.token_expires = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                    return True
                
                return False
        except Exception as e:
            logging.error(f"Cerner authentication failed: {str(e)}")
            return False
    
    async def fetch_patients(self, last_updated: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch patient data from Cerner FHIR API"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                url = f"{self.base_url}/api/FHIR/R4/Patient"
                
                if last_updated:
                    url += f"?_lastUpdated=gt{last_updated.isoformat()}"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    fhir_bundle = response.json()
                    return fhir_bundle.get("entry", [])
                
                return []
        except Exception as e:
            logging.error(f"Error fetching Cerner patients: {str(e)}")
            return []
    
    async def fetch_observations(self, patient_id: str, last_updated: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch observation data from Cerner"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                url = f"{self.base_url}/api/FHIR/R4/Observation?patient={patient_id}"
                
                if last_updated:
                    url += f"&_lastUpdated=gt{last_updated.isoformat()}"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    fhir_bundle = response.json()
                    return fhir_bundle.get("entry", [])
                
                return []
        except Exception as e:
            logging.error(f"Error fetching Cerner observations: {str(e)}")
            return []

class AllscriptsConnector(EMRConnector):
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Allscripts API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    self.token_expires = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                    return True
                
                return False
        except Exception as e:
            logging.error(f"Allscripts authentication failed: {str(e)}")
            return False
    
    async def fetch_patients(self, last_updated: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch patient data from Allscripts"""
        # Implementation would depend on Allscripts API structure
        return []
    
    async def fetch_observations(self, patient_id: str, last_updated: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch observation data from Allscripts"""
        # Implementation would depend on Allscripts API structure
        return [] 