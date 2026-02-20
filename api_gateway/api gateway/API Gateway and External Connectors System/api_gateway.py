"""
API Gateway & Management Module
Handles core API endpoints using Abena SDK for auth, data, and privacy
"""

import asyncio
import json
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from abc import ABC, abstractmethod

from fastapi import FastAPI, HTTPException, Depends, Request, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ValidationError
import httpx

# Abena SDK Integration
from abena_sdk import AbenaSDK

# Pydantic Models
class PatientData(BaseModel):
    mrn: str
    first_name: str
    last_name: str
    gender: str
    birth_date: str
    email: Optional[str] = None
    phone: Optional[str] = None

class ObservationData(BaseModel):
    patient_id: str
    observation_type: str
    value: float
    unit: str
    timestamp: datetime
    source_device: Optional[str] = None

class DeviceData(BaseModel):
    device_id: str
    patient_id: str
    device_type: str
    measurements: List[ObservationData]
    sync_timestamp: datetime

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

# API Gateway Class
class APIGateway:
    def __init__(self, enable_trusted_hosts: bool = True):
        self.app = FastAPI(title="Abena IHR API Gateway", version="1.0.0")
        self.setup_middleware(enable_trusted_hosts)
        self.setup_abena_sdk()
        self.setup_routes()
    
    def setup_middleware(self, enable_trusted_hosts: bool = True):
        """Configure middleware for security and CORS"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://app.abena-ihr.com", "https://admin.abena-ihr.com"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
        
        if enable_trusted_hosts:
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["api.abena-ihr.com", "localhost", "127.0.0.1"]
            )
    
    def setup_abena_sdk(self):
        """Initialize Abena SDK for auth, data, and privacy services"""
        self.abena = AbenaSDK({
            'authServiceUrl': 'http://localhost:3001',
            'dataServiceUrl': 'http://localhost:8001',
            'privacyServiceUrl': 'http://localhost:8002',
            'blockchainServiceUrl': 'http://localhost:8003'
        })
    
    async def verify_request(self, request: Request):
        """Verify request using Abena SDK - auto-handles auth & permissions"""
        # Extract authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        try:
            # Abena SDK auto-handles token validation and permissions
            # This replaces all custom JWT and API key logic
            await self.abena.verifyRequest(request)
            
        except Exception as e:
            logging.error(f"Request verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid authorization")
    
    def setup_routes(self):
        """Define API routes"""
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            """Middleware to log all requests"""
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Abena SDK auto-handles audit logging
            await self.abena.logAuditEvent({
                'endpoint': str(request.url.path),
                'method': request.method,
                'processing_time': process_time,
                'status_code': response.status_code,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            return response
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        @self.app.post("/api/v1/patients", response_model=APIResponse)
        async def create_patient(patient: PatientData, request: Request):
            """Create a new patient record"""
            # Auto-handled auth & permissions via Abena SDK
            await self.verify_request(request)
            
            try:
                patient_id = str(uuid.uuid4())
                
                # Auto-handled privacy & encryption via Abena SDK
                await self.abena.storePatientData(patient_id, patient.model_dump(), 'patient_creation')
                
                return APIResponse(
                    success=True,
                    message="Patient created successfully",
                    data={"patient_id": patient_id}
                )
            except Exception as e:
                logging.error(f"Error creating patient: {str(e)}")
                return APIResponse(
                    success=False,
                    message="Failed to create patient",
                    errors=[str(e)]
                )
        
        @self.app.post("/api/v1/observations", response_model=APIResponse)
        async def create_observation(observation: ObservationData, request: Request):
            """Create a new observation record"""
            # Auto-handled auth & permissions via Abena SDK
            await self.verify_request(request)
            
            try:
                observation_id = str(uuid.uuid4())
                
                # Auto-handled privacy & encryption via Abena SDK
                await self.abena.storeObservationData(observation_id, observation.model_dump(), 'observation_creation')
                
                return APIResponse(
                    success=True,
                    message="Observation created successfully",
                    data={"observation_id": observation_id}
                )
            except Exception as e:
                logging.error(f"Error creating observation: {str(e)}")
                return APIResponse(
                    success=False,
                    message="Failed to create observation",
                    errors=[str(e)]
                )
        
        @self.app.post("/api/v1/devices/sync", response_model=APIResponse)
        async def sync_device_data(device_data: DeviceData, request: Request):
            """Sync data from wearable devices"""
            # Auto-handled auth & permissions via Abena SDK
            await self.verify_request(request)
            
            try:
                sync_id = str(uuid.uuid4())
                
                # Auto-handled privacy & encryption via Abena SDK
                await self.abena.storeDeviceData(sync_id, device_data.model_dump(), 'device_sync')
                
                return APIResponse(
                    success=True,
                    message="Device data synced successfully",
                    data={"sync_id": sync_id}
                )
            except Exception as e:
                logging.error(f"Error syncing device data: {str(e)}")
                return APIResponse(
                    success=False,
                    message="Failed to sync device data",
                    errors=[str(e)]
                )
        
        @self.app.get("/api/v1/patients/{patient_id}", response_model=APIResponse)
        async def get_patient(patient_id: str, request: Request):
            """Get patient data with auto-handled privacy controls"""
            # Auto-handled auth & permissions via Abena SDK
            await self.verify_request(request)
            
            try:
                # Auto-handled privacy & encryption via Abena SDK
                patient_data = await self.abena.getPatientData(patient_id, 'patient_retrieval')
                
                return APIResponse(
                    success=True,
                    message="Patient data retrieved successfully",
                    data=patient_data
                )
            except Exception as e:
                logging.error(f"Error retrieving patient: {str(e)}")
                return APIResponse(
                    success=False,
                    message="Failed to retrieve patient data",
                    errors=[str(e)]
                )
        
        @self.app.get("/api/v1/observations/{patient_id}", response_model=APIResponse)
        async def get_observations(patient_id: str, request: Request):
            """Get patient observations with auto-handled privacy controls"""
            # Auto-handled auth & permissions via Abena SDK
            await self.verify_request(request)
            
            try:
                # Auto-handled privacy & encryption via Abena SDK
                observations = await self.abena.getPatientObservations(patient_id, 'observation_retrieval')
                
                return APIResponse(
                    success=True,
                    message="Observations retrieved successfully",
                    data={"observations": observations}
                )
            except Exception as e:
                logging.error(f"Error retrieving observations: {str(e)}")
                return APIResponse(
                    success=False,
                    message="Failed to retrieve observations",
                    errors=[str(e)]
                )

# Create and configure the API Gateway
def create_api_gateway(enable_trusted_hosts: bool = True) -> APIGateway:
    """Factory function to create configured API Gateway"""
    return APIGateway(enable_trusted_hosts=enable_trusted_hosts)

# For direct execution
if __name__ == "__main__":
    import uvicorn
    
    # Create API Gateway instance
    gateway = create_api_gateway()
    
    # Run the server
    uvicorn.run(
        gateway.app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 