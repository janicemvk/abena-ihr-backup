"""
Wearable Device Integration Module
Handles authentication and data fetching from various wearable devices
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

import httpx
import redis
from pydantic import BaseModel

from api_gateway import ObservationData

class DeviceType(Enum):
    FITBIT = "fitbit"
    APPLE_HEALTH = "apple_health"
    GARMIN = "garmin"
    SAMSUNG_HEALTH = "samsung_health"
    GENERIC = "generic"

@dataclass
class DeviceCredentials:
    client_id: str
    client_secret: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None

class DeviceAdapter(ABC):
    """Abstract base class for device adapters"""
    
    @abstractmethod
    async def authenticate(self, credentials: DeviceCredentials) -> bool:
        pass
    
    @abstractmethod
    async def fetch_data(self, patient_id: str, start_date: datetime, end_date: datetime) -> List[ObservationData]:
        pass
    
    @abstractmethod
    async def refresh_token(self, credentials: DeviceCredentials) -> DeviceCredentials:
        pass

class FitbitAdapter(DeviceAdapter):
    def __init__(self):
        self.base_url = "https://api.fitbit.com/1"
        self.auth_url = "https://www.fitbit.com/oauth2/authorize"
        self.token_url = "https://api.fitbit.com/oauth2/token"
        self.credentials = None
    
    async def authenticate(self, credentials: DeviceCredentials) -> bool:
        """Authenticate with Fitbit API"""
        try:
            self.credentials = credentials
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                        "grant_type": "authorization_code",
                        "code": credentials.access_token  # This would be auth code initially
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    credentials.access_token = token_data["access_token"]
                    credentials.refresh_token = token_data["refresh_token"]
                    credentials.expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                    return True
                
                return False
        except Exception as e:
            logging.error(f"Fitbit authentication failed: {str(e)}")
            return False
    
    async def fetch_data(self, patient_id: str, start_date: datetime, end_date: datetime) -> List[ObservationData]:
        """Fetch data from Fitbit API"""
        observations = []
        
        try:
            if not self.credentials or not self.credentials.access_token:
                raise ValueError("Not authenticated with Fitbit")
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
                
                # Fetch heart rate data
                hr_response = await client.get(
                    f"{self.base_url}/user/-/activities/heart/date/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}.json",
                    headers=headers
                )
                
                if hr_response.status_code == 200:
                    hr_data = hr_response.json()
                    for day_data in hr_data.get("activities-heart", []):
                        if "value" in day_data and "restingHeartRate" in day_data["value"]:
                            observations.append(ObservationData(
                                patient_id=patient_id,
                                observation_type="heart_rate",
                                value=float(day_data["value"]["restingHeartRate"]),
                                unit="bpm",
                                timestamp=datetime.strptime(day_data["dateTime"], "%Y-%m-%d"),
                                source_device="fitbit"
                            ))
                
                # Fetch weight data
                weight_response = await client.get(
                    f"{self.base_url}/user/-/body/log/weight/date/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}.json",
                    headers=headers
                )
                
                if weight_response.status_code == 200:
                    weight_data = weight_response.json()
                    for weight_entry in weight_data.get("weight", []):
                        observations.append(ObservationData(
                            patient_id=patient_id,
                            observation_type="weight",
                            value=float(weight_entry["weight"]),
                            unit="kg",
                            timestamp=datetime.strptime(weight_entry["date"], "%Y-%m-%d"),
                            source_device="fitbit"
                        ))
                
        except Exception as e:
            logging.error(f"Error fetching Fitbit data: {str(e)}")
        
        return observations
    
    async def refresh_token(self, credentials: DeviceCredentials) -> DeviceCredentials:
        """Refresh Fitbit access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                        "grant_type": "refresh_token",
                        "refresh_token": credentials.refresh_token
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    credentials.access_token = token_data["access_token"]
                    credentials.refresh_token = token_data.get("refresh_token", credentials.refresh_token)
                    credentials.expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                
        except Exception as e:
            logging.error(f"Token refresh failed: {str(e)}")
        
        return credentials

class AppleHealthAdapter(DeviceAdapter):
    def __init__(self):
        self.base_url = "https://developer.apple.com/health-records"
    
    async def authenticate(self, credentials: DeviceCredentials) -> bool:
        """Apple Health uses different authentication (HealthKit on device)"""
        # This would typically be handled by the mobile app
        return True
    
    async def fetch_data(self, patient_id: str, start_date: datetime, end_date: datetime) -> List[ObservationData]:
        """Fetch data from Apple Health (via mobile app API)"""
        # Implementation would depend on your mobile app's API
        return []
    
    async def refresh_token(self, credentials: DeviceCredentials) -> DeviceCredentials:
        """Apple Health doesn't use traditional OAuth tokens"""
        return credentials

class GarminAdapter(DeviceAdapter):
    def __init__(self):
        self.base_url = "https://apis.garmin.com/wellness-api/rest"
    
    async def authenticate(self, credentials: DeviceCredentials) -> bool:
        """Authenticate with Garmin API"""
        # Garmin uses OAuth 1.0a - implementation would be more complex
        return True
    
    async def fetch_data(self, patient_id: str, start_date: datetime, end_date: datetime) -> List[ObservationData]:
        """Fetch data from Garmin API"""
        # Implementation for Garmin API
        return []
    
    async def refresh_token(self, credentials: DeviceCredentials) -> DeviceCredentials:
        """Refresh Garmin token"""
        return credentials

class DeviceManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.adapters = {
            DeviceType.FITBIT: FitbitAdapter(),
            DeviceType.APPLE_HEALTH: AppleHealthAdapter(),
            DeviceType.GARMIN: GarminAdapter(),
        }
    
    async def register_device(self, patient_id: str, device_type: DeviceType, 
                            credentials: DeviceCredentials) -> bool:
        """Register a new device for a patient"""
        try:
            adapter = self.adapters.get(device_type)
            if not adapter:
                raise ValueError(f"Unsupported device type: {device_type}")
            
            # Authenticate with device API
            if await adapter.authenticate(credentials):
                # Store encrypted credentials
                device_key = f"device:{patient_id}:{device_type.value}"
                encrypted_creds = self._encrypt_credentials(credentials)
                self.redis_client.setex(device_key, 86400, json.dumps(encrypted_creds))
                return True
            
            return False
        except Exception as e:
            logging.error(f"Device registration failed: {str(e)}")
            return False
    
    async def sync_device_data(self, patient_id: str, device_type: DeviceType) -> List[ObservationData]:
        """Sync data from a specific device"""
        try:
            adapter = self.adapters.get(device_type)
            if not adapter:
                raise ValueError(f"Unsupported device type: {device_type}")
            
            # Get stored credentials
            device_key = f"device:{patient_id}:{device_type.value}"
            encrypted_creds = self.redis_client.get(device_key)
            
            if not encrypted_creds:
                raise ValueError("Device not registered")
            
            credentials = self._decrypt_credentials(json.loads(encrypted_creds))
            
            # Check if token needs refresh
            if credentials.expires_at and credentials.expires_at <= datetime.utcnow():
                credentials = await adapter.refresh_token(credentials)
                # Update stored credentials
                encrypted_creds = self._encrypt_credentials(credentials)
                self.redis_client.setex(device_key, 86400, json.dumps(encrypted_creds))
            
            # Fetch data for last 7 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            return await adapter.fetch_data(patient_id, start_date, end_date)
            
        except Exception as e:
            logging.error(f"Device sync failed: {str(e)}")
            return []
    
    def _encrypt_credentials(self, credentials: DeviceCredentials) -> Dict[str, Any]:
        """Encrypt sensitive credential data"""
        # In production, use proper encryption
        return asdict(credentials)
    
    def _decrypt_credentials(self, encrypted_data: Dict[str, Any]) -> DeviceCredentials:
        """Decrypt credential data"""
        # In production, use proper decryption
        return DeviceCredentials(**encrypted_data) 