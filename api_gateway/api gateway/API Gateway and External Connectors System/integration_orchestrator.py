"""
Integration Orchestrator Module
Coordinates data synchronization between different systems
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import redis

from device_adapters import DeviceManager, DeviceType
from emr_connectors import EMRConnector

class IntegrationOrchestrator:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.device_manager = DeviceManager(redis_client)
        self.emr_connectors = {}
        self.sync_scheduler = {}
    
    def register_emr_connector(self, name: str, connector: EMRConnector):
        """Register an EMR connector"""
        self.emr_connectors[name] = connector
    
    async def schedule_sync(self, patient_id: str, sync_type: str, interval_hours: int = 24):
        """Schedule regular data synchronization"""
        sync_key = f"sync_schedule:{patient_id}:{sync_type}"
        next_sync = datetime.utcnow() + timedelta(hours=interval_hours)
        
        self.redis_client.setex(sync_key, interval_hours * 3600, next_sync.isoformat())
    
    async def process_sync_queue(self):
        """Process queued synchronization tasks"""
        while True:
            try:
                # Get next sync task
                task = self.redis_client.brpop("sync_queue", timeout=30)
                if task:
                    task_data = json.loads(task[1])
                    await self._process_sync_task(task_data)
                
            except Exception as e:
                logging.error(f"Error processing sync queue: {str(e)}")
                await asyncio.sleep(5)
    
    async def _process_sync_task(self, task_data: Dict[str, Any]):
        """Process individual sync task"""
        task_type = task_data.get("type")
        patient_id = task_data.get("patient_id")
        
        if task_type == "device_sync":
            device_type = DeviceType(task_data.get("device_type"))
            observations = await self.device_manager.sync_device_data(patient_id, device_type)
            
            # Queue observations for processing through ETL pipeline
            for obs in observations:
                self.redis_client.lpush("observation_queue", json.dumps(obs.dict()))
        
        elif task_type == "emr_sync":
            emr_name = task_data.get("emr_name")
            connector = self.emr_connectors.get(emr_name)
            
            if connector:
                # Fetch new/updated data
                last_sync = task_data.get("last_sync")
                last_updated = datetime.fromisoformat(last_sync) if last_sync else None
                
                patients = await connector.fetch_patients(last_updated)
                for patient_entry in patients:
                    # Queue patient data for ETL processing
                    self.redis_client.lpush("patient_queue", json.dumps(patient_entry))
                
                observations = await connector.fetch_observations(patient_id, last_updated)
                for obs_entry in observations:
                    # Queue observation data for ETL processing
                    self.redis_client.lpush("observation_queue", json.dumps(obs_entry))
    
    async def sync_all_devices(self, patient_id: str):
        """Sync data from all registered devices for a patient"""
        try:
            # Get all registered devices for patient
            device_keys = self.redis_client.keys(f"device:{patient_id}:*")
            
            for device_key in device_keys:
                device_type_str = device_key.decode().split(":")[-1]
                device_type = DeviceType(device_type_str)
                
                # Queue device sync
                sync_task = {
                    "type": "device_sync",
                    "patient_id": patient_id,
                    "device_type": device_type.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                self.redis_client.lpush("sync_queue", json.dumps(sync_task))
                
        except Exception as e:
            logging.error(f"Error syncing all devices for patient {patient_id}: {str(e)}")
    
    async def sync_all_emrs(self, patient_id: Optional[str] = None):
        """Sync data from all registered EMR systems"""
        try:
            for emr_name, connector in self.emr_connectors.items():
                sync_task = {
                    "type": "emr_sync",
                    "emr_name": emr_name,
                    "patient_id": patient_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                self.redis_client.lpush("sync_queue", json.dumps(sync_task))
                
        except Exception as e:
            logging.error(f"Error syncing EMRs: {str(e)}")
    
    async def get_sync_status(self, patient_id: str) -> Dict[str, Any]:
        """Get synchronization status for a patient"""
        try:
            status = {
                "patient_id": patient_id,
                "last_device_sync": None,
                "last_emr_sync": None,
                "registered_devices": [],
                "sync_errors": []
            }
            
            # Get last sync times
            device_sync_key = f"sync_schedule:{patient_id}:device_sync"
            emr_sync_key = f"sync_schedule:{patient_id}:emr_sync"
            
            device_sync = self.redis_client.get(device_sync_key)
            emr_sync = self.redis_client.get(emr_sync_key)
            
            if device_sync:
                status["last_device_sync"] = device_sync.decode()
            if emr_sync:
                status["last_emr_sync"] = emr_sync.decode()
            
            # Get registered devices
            device_keys = self.redis_client.keys(f"device:{patient_id}:*")
            for device_key in device_keys:
                device_type = device_key.decode().split(":")[-1]
                status["registered_devices"].append(device_type)
            
            return status
            
        except Exception as e:
            logging.error(f"Error getting sync status: {str(e)}")
            return {"error": str(e)}
    
    async def process_observation_queue(self):
        """Process queued observations through ETL pipeline"""
        while True:
            try:
                # Get next observation
                observation_data = self.redis_client.brpop("observation_queue", timeout=30)
                if observation_data:
                    observation = json.loads(observation_data[1])
                    await self._process_observation(observation)
                
            except Exception as e:
                logging.error(f"Error processing observation queue: {str(e)}")
                await asyncio.sleep(5)
    
    async def _process_observation(self, observation: Dict[str, Any]):
        """Process individual observation through ETL pipeline"""
        try:
            # Apply data transformations
            transformed_obs = await self._transform_observation(observation)
            
            # Validate data
            if await self._validate_observation(transformed_obs):
                # Store in database
                await self._store_observation(transformed_obs)
                
                # Trigger alerts if needed
                await self._check_alerts(transformed_obs)
            
        except Exception as e:
            logging.error(f"Error processing observation: {str(e)}")
    
    async def _transform_observation(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Transform observation data (unit conversion, normalization, etc.)"""
        # Implement data transformation logic
        # This could include unit conversion, data normalization, etc.
        return observation
    
    async def _validate_observation(self, observation: Dict[str, Any]) -> bool:
        """Validate observation data"""
        # Implement validation logic
        # Check for reasonable ranges, required fields, etc.
        return True
    
    async def _store_observation(self, observation: Dict[str, Any]):
        """Store observation in database"""
        # Implement database storage logic
        pass
    
    async def _check_alerts(self, observation: Dict[str, Any]):
        """Check if observation triggers any alerts"""
        # Implement alert logic
        # Check for abnormal values, trends, etc.
        pass 