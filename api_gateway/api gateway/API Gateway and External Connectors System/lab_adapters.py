"""
Lab System Adapters Module
Handles integration with laboratory information systems
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

import httpx

class LabSystemAdapter(ABC):
    """Abstract base class for lab system integrations"""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        pass
    
    @abstractmethod
    async def fetch_lab_results(self, patient_id: str, order_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def submit_lab_order(self, order_data: Dict[str, Any]) -> str:
        pass

class LabCorpAdapter(LabSystemAdapter):
    def __init__(self, client_id: str, client_secret: str, facility_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.facility_id = facility_id
        self.base_url = "https://api.labcorp.com/v1"
        self.access_token = None
        self.token_expires = None
    
    async def authenticate(self) -> bool:
        """Authenticate with LabCorp API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth/token",
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
            logging.error(f"LabCorp authentication failed: {str(e)}")
            return False
    
    async def fetch_lab_results(self, patient_id: str, order_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch lab results from LabCorp"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                url = f"{self.base_url}/patients/{patient_id}/results"
                
                if order_date:
                    url += f"?from_date={order_date.strftime('%Y-%m-%d')}"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json().get("results", [])
                
                return []
        except Exception as e:
            logging.error(f"Error fetching LabCorp results: {str(e)}")
            return []
    
    async def submit_lab_order(self, order_data: Dict[str, Any]) -> str:
        """Submit a lab order to LabCorp"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                response = await client.post(
                    f"{self.base_url}/orders",
                    headers=headers,
                    json=order_data
                )
                
                if response.status_code == 201:
                    order_response = response.json()
                    return order_response.get("order_id")
                
                return None
        except Exception as e:
            logging.error(f"Error submitting LabCorp order: {str(e)}")
            return None

class QuestAdapter(LabSystemAdapter):
    def __init__(self, client_id: str, client_secret: str, facility_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.facility_id = facility_id
        self.base_url = "https://api.questdiagnostics.com/v1"
        self.access_token = None
        self.token_expires = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Quest API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth/token",
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
            logging.error(f"Quest authentication failed: {str(e)}")
            return False
    
    async def fetch_lab_results(self, patient_id: str, order_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch lab results from Quest"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                url = f"{self.base_url}/patients/{patient_id}/results"
                
                if order_date:
                    url += f"?from_date={order_date.strftime('%Y-%m-%d')}"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json().get("results", [])
                
                return []
        except Exception as e:
            logging.error(f"Error fetching Quest results: {str(e)}")
            return []
    
    async def submit_lab_order(self, order_data: Dict[str, Any]) -> str:
        """Submit a lab order to Quest"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                response = await client.post(
                    f"{self.base_url}/orders",
                    headers=headers,
                    json=order_data
                )
                
                if response.status_code == 201:
                    order_response = response.json()
                    return order_response.get("order_id")
                
                return None
        except Exception as e:
            logging.error(f"Error submitting Quest order: {str(e)}")
            return None

class LabManager:
    def __init__(self):
        self.adapters = {}
    
    def register_adapter(self, name: str, adapter: LabSystemAdapter):
        """Register a lab system adapter"""
        self.adapters[name] = adapter
    
    async def fetch_lab_results(self, lab_system: str, patient_id: str, order_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch lab results from specified lab system"""
        try:
            adapter = self.adapters.get(lab_system)
            if not adapter:
                raise ValueError(f"Unsupported lab system: {lab_system}")
            
            return await adapter.fetch_lab_results(patient_id, order_date)
            
        except Exception as e:
            logging.error(f"Error fetching lab results from {lab_system}: {str(e)}")
            return []
    
    async def submit_lab_order(self, lab_system: str, order_data: Dict[str, Any]) -> str:
        """Submit lab order to specified lab system"""
        try:
            adapter = self.adapters.get(lab_system)
            if not adapter:
                raise ValueError(f"Unsupported lab system: {lab_system}")
            
            return await adapter.submit_lab_order(order_data)
            
        except Exception as e:
            logging.error(f"Error submitting lab order to {lab_system}: {str(e)}")
            return None
    
    async def get_available_tests(self, lab_system: str) -> List[Dict[str, Any]]:
        """Get available lab tests from specified lab system"""
        try:
            adapter = self.adapters.get(lab_system)
            if not adapter:
                raise ValueError(f"Unsupported lab system: {lab_system}")
            
            # This would be implemented in each adapter
            return []
            
        except Exception as e:
            logging.error(f"Error getting available tests from {lab_system}: {str(e)}")
            return [] 