"""
Telemedicine Platform Bridges Module
Handles integration with telemedicine platforms
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

import httpx
from jose import jwt

class TelemedicineBridge(ABC):
    """Abstract base class for telemedicine platform integrations"""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        pass
    
    @abstractmethod
    async def create_appointment(self, appointment_data: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    async def get_appointment_recordings(self, appointment_id: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_session_notes(self, appointment_id: str) -> Dict[str, Any]:
        pass

class ZoomHealthBridge(TelemedicineBridge):
    def __init__(self, api_key: str, api_secret: str, account_id: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_id = account_id
        self.base_url = "https://api.zoom.us/v2"
        self.access_token = None
        self.token_expires = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Zoom API using JWT"""
        try:
            # Generate JWT token
            jwt_payload = {
                "iss": self.api_key,
                "exp": int(time.time()) + 3600,
                "iat": int(time.time()),
                "aud": "zoom",
                "appKey": self.api_key,
                "tokenExp": int(time.time()) + 3600,
                "alg": "HS256"
            }
            
            self.access_token = jwt.encode(jwt_payload, self.api_secret, algorithm="HS256")
            self.token_expires = datetime.utcnow() + timedelta(hours=1)
            return True
            
        except Exception as e:
            logging.error(f"Zoom authentication failed: {str(e)}")
            return False
    
    async def create_appointment(self, appointment_data: Dict[str, Any]) -> str:
        """Create a Zoom meeting for telemedicine appointment"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                meeting_data = {
                    "topic": f"Medical Consultation - {appointment_data.get('patient_name')}",
                    "type": 2,  # Scheduled meeting
                    "start_time": appointment_data.get('start_time'),
                    "duration": appointment_data.get('duration', 30),
                    "timezone": "UTC",
                    "settings": {
                        "host_video": True,
                        "participant_video": True,
                        "waiting_room": True,
                        "recording": "cloud",
                        "auto_recording": "cloud"
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/users/{self.account_id}/meetings",
                    headers=headers,
                    json=meeting_data
                )
                
                if response.status_code == 201:
                    meeting_info = response.json()
                    return meeting_info.get("id")
                
                return None
        except Exception as e:
            logging.error(f"Error creating Zoom meeting: {str(e)}")
            return None
    
    async def get_appointment_recordings(self, appointment_id: str) -> List[Dict[str, Any]]:
        """Get recordings from a Zoom meeting"""
        try:
            if not self.access_token or self.token_expires <= datetime.utcnow():
                await self.authenticate()
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                response = await client.get(
                    f"{self.base_url}/meetings/{appointment_id}/recordings",
                    headers=headers
                )
                
                if response.status_code == 200:
                    recordings_data = response.json()
                    return recordings_data.get("recording_files", [])
                
                return []
        except Exception as e:
            logging.error(f"Error fetching Zoom recordings: {str(e)}")
            return []
    
    async def get_session_notes(self, appointment_id: str) -> Dict[str, Any]:
        """Get session notes/transcript from Zoom meeting"""
        # Zoom doesn't provide automatic transcription in basic plans
        # This would integrate with your own transcription service
        return {"notes": "Manual transcription required"}

class DoxyBridge(TelemedicineBridge):
    def __init__(self, api_key: str, clinic_id: str):
        self.api_key = api_key
        self.clinic_id = clinic_id
        self.base_url = "https://api.doxy.me/v1"
    
    async def authenticate(self) -> bool:
        """Doxy.me uses API key authentication"""
        return True  # API key is used directly in headers
    
    async def create_appointment(self, appointment_data: Dict[str, Any]) -> str:
        """Create appointment in Doxy.me"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                appointment = {
                    "provider_id": appointment_data.get("provider_id"),
                    "patient_name": appointment_data.get("patient_name"),
                    "scheduled_time": appointment_data.get("start_time"),
                    "duration": appointment_data.get("duration", 30)
                }
                
                response = await client.post(
                    f"{self.base_url}/appointments",
                    headers=headers,
                    json=appointment
                )
                
                if response.status_code == 201:
                    appt_data = response.json()
                    return appt_data.get("id")
                
                return None
        except Exception as e:
            logging.error(f"Error creating Doxy appointment: {str(e)}")
            return None
    
    async def get_appointment_recordings(self, appointment_id: str) -> List[Dict[str, Any]]:
        """Doxy.me typically doesn't provide recordings through API"""
        return []
    
    async def get_session_notes(self, appointment_id: str) -> Dict[str, Any]:
        """Get session notes from Doxy appointment"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                response = await client.get(
                    f"{self.base_url}/appointments/{appointment_id}/notes",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                
                return {}
        except Exception as e:
            logging.error(f"Error fetching Doxy notes: {str(e)}")
            return {}

class TelemedicineManager:
    def __init__(self):
        self.bridges = {}
    
    def register_bridge(self, name: str, bridge: TelemedicineBridge):
        """Register a telemedicine platform bridge"""
        self.bridges[name] = bridge
    
    async def create_appointment(self, platform: str, appointment_data: Dict[str, Any]) -> str:
        """Create appointment on specified platform"""
        try:
            bridge = self.bridges.get(platform)
            if not bridge:
                raise ValueError(f"Unsupported platform: {platform}")
            
            return await bridge.create_appointment(appointment_data)
            
        except Exception as e:
            logging.error(f"Error creating appointment on {platform}: {str(e)}")
            return None
    
    async def get_appointment_recordings(self, platform: str, appointment_id: str) -> List[Dict[str, Any]]:
        """Get recordings from appointment on specified platform"""
        try:
            bridge = self.bridges.get(platform)
            if not bridge:
                raise ValueError(f"Unsupported platform: {platform}")
            
            return await bridge.get_appointment_recordings(appointment_id)
            
        except Exception as e:
            logging.error(f"Error getting recordings from {platform}: {str(e)}")
            return []
    
    async def get_session_notes(self, platform: str, appointment_id: str) -> Dict[str, Any]:
        """Get session notes from appointment on specified platform"""
        try:
            bridge = self.bridges.get(platform)
            if not bridge:
                raise ValueError(f"Unsupported platform: {platform}")
            
            return await bridge.get_session_notes(appointment_id)
            
        except Exception as e:
            logging.error(f"Error getting session notes from {platform}: {str(e)}")
            return {} 