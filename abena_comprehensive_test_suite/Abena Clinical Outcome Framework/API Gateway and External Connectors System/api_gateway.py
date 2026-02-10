"""
API Gateway & Management Module
Handles authentication, rate limiting, and core API endpoints
"""

import asyncio
import json
import uuid
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from abc import ABC, abstractmethod

from fastapi import FastAPI, HTTPException, Depends, Request, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ValidationError
import httpx
import redis
from jose import JWTError, jwt

# Import Abena SDK
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from abena_sdk import AbenaSDK, AbenaSDKConfig

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

# Rate Limiting
class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def is_allowed(self, key: str, limit: int, window: int = 3600) -> bool:
        """Check if request is within rate limit (sliding window)"""
        current_time = int(time.time())
        pipeline = self.redis.pipeline()
        
        # Remove old entries
        pipeline.zremrangebyscore(f"rate_limit:{key}", 0, current_time - window)
        
        # Count current requests
        pipeline.zcard(f"rate_limit:{key}")
        
        # Add current request
        pipeline.zadd(f"rate_limit:{key}", {str(uuid.uuid4()): current_time})
        
        # Set expiration
        pipeline.expire(f"rate_limit:{key}", window)
        
        results = pipeline.execute()
        request_count = results[1]
        
        return request_count < limit

# API Gateway Class
class APIGateway:
    def __init__(self, db_url: str, redis_url: str = "redis://localhost:6379", enable_trusted_hosts: bool = True):
        self.app = FastAPI(title="Abena IHR API Gateway", version="1.0.0")
        
        # Initialize Abena SDK for centralized services
        self.abena = AbenaSDK(AbenaSDKConfig(
            auth_service_url='http://localhost:3001',
            data_service_url='http://localhost:8001',
            privacy_service_url='http://localhost:8002',
            blockchain_service_url='http://localhost:8003'
        ))
        
        self.setup_middleware(enable_trusted_hosts)
        self.setup_redis(redis_url)
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
    
    def setup_redis(self, redis_url: str):
        """Initialize Redis connection for caching and rate limiting"""
        self.redis_client = redis.from_url(redis_url)
        self.rate_limiter = RateLimiter(self.redis_client)
    
    async def verify_user_permissions(self, user_id: str, patient_id: str, action: str) -> bool:
        """Verify user permissions using Abena SDK"""
        try:
            # 1. Auto-handled auth & permissions
            return await self.abena.check_permissions(user_id, patient_id, action)
        except Exception as e:
            logging.error(f"Permission check failed: {str(e)}")
            return False
    
    async def get_patient_data_secure(self, patient_id: str, user_id: str, purpose: str) -> Dict[str, Any]:
        """Get patient data with automatic privacy controls"""
        try:
            # 1. Auto-handled auth & permissions
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            return await self.abena.get_patient_data(patient_id, purpose)
        except Exception as e:
            logging.error(f"Failed to get patient data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve patient data")
    
    async def save_outcome_data_secure(self, patient_id: str, user_id: str, 
                                     outcome_data: Dict[str, Any], purpose: str = "clinical_assessment") -> str:
        """Save outcome data with privacy controls and blockchain verification"""
        try:
            # 1. Auto-handled auth & permissions
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            return await self.abena.save_outcome_data(patient_id, outcome_data, purpose)
        except Exception as e:
            logging.error(f"Failed to save outcome data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save outcome data")
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            }
        
        @self.app.get("/patients/{patient_id}/data")
        async def get_patient_data_endpoint(
            patient_id: str,
            user_id: str = Header(..., alias="X-User-ID"),
            purpose: str = "clinical_care"
        ):
            """Get patient data with privacy controls"""
            try:
                # Verify user permissions using Abena SDK
                if not await self.verify_user_permissions(user_id, patient_id, "read"):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
                
                # Get patient data through Abena SDK
                patient_data = await self.get_patient_data_secure(patient_id, user_id, purpose)
                
                return {
                    "patient_id": patient_id,
                    "data": patient_data,
                    "retrieved_at": datetime.now(timezone.utc).isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"Error in get_patient_data_endpoint: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.post("/patients/{patient_id}/outcomes")
        async def save_outcome_endpoint(
            patient_id: str,
            outcome_data: Dict[str, Any],
            user_id: str = Header(..., alias="X-User-ID"),
            purpose: str = "clinical_assessment"
        ):
            """Save outcome data with privacy controls"""
            try:
                # Verify user permissions using Abena SDK
                if not await self.verify_user_permissions(user_id, patient_id, "write"):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
                
                # Save outcome data through Abena SDK
                record_id = await self.save_outcome_data_secure(patient_id, user_id, outcome_data, purpose)
                
                return {
                    "patient_id": patient_id,
                    "record_id": record_id,
                    "saved_at": datetime.now(timezone.utc).isoformat(),
                    "status": "success"
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"Error in save_outcome_endpoint: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/patients/{patient_id}/outcomes/history")
        async def get_outcome_history_endpoint(
            patient_id: str,
            user_id: str = Header(..., alias="X-User-ID"),
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
        ):
            """Get patient outcome history"""
            try:
                # Verify user permissions using Abena SDK
                if not await self.verify_user_permissions(user_id, patient_id, "read"):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
                
                # Get outcome history through Abena SDK
                outcome_history = await self.abena.get_outcome_history(patient_id, start_date, end_date)
                
                return {
                    "patient_id": patient_id,
                    "outcomes": outcome_history,
                    "retrieved_at": datetime.now(timezone.utc).isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"Error in get_outcome_history_endpoint: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/patients/{patient_id}/quality-metrics")
        async def get_quality_metrics_endpoint(
            patient_id: str,
            user_id: str = Header(..., alias="X-User-ID")
        ):
            """Get data quality metrics for patient"""
            try:
                # Verify user permissions using Abena SDK
                if not await self.verify_user_permissions(user_id, patient_id, "read"):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
                
                # Get quality metrics through Abena SDK
                quality_metrics = await self.abena.get_data_quality_metrics(patient_id)
                
                return {
                    "patient_id": patient_id,
                    "quality_metrics": quality_metrics,
                    "retrieved_at": datetime.now(timezone.utc).isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"Error in get_quality_metrics_endpoint: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            """Middleware to log all requests"""
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log to Redis for real-time monitoring
            log_data = {
                "endpoint": str(request.url.path),
                "method": request.method,
                "processing_time": process_time,
                "status_code": response.status_code,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.redis_client.lpush("api_logs", json.dumps(log_data))
            self.redis_client.ltrim("api_logs", 0, 999)  # Keep last 1000 logs
            
            return response 