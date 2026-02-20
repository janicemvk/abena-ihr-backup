"""
Webhook Handler Module
Handles real-time updates from external systems via webhooks
"""

import asyncio
import json
import hashlib
import hmac
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import redis

class WebhookHandler:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.webhook_secrets = {}  # Store webhook secrets for verification
    
    def register_webhook_secret(self, source: str, secret: str):
        """Register webhook secret for signature verification"""
        self.webhook_secrets[source] = secret
    
    def verify_webhook_signature(self, source: str, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        secret = self.webhook_secrets.get(source)
        if not secret:
            return False
        
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    async def handle_device_webhook(self, source: str, payload: Dict[str, Any]) -> bool:
        """Handle webhook from wearable device platforms"""
        try:
            # Queue webhook data for processing
            webhook_data = {
                "source": source,
                "type": "device_update",
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.redis_client.lpush("webhook_queue", json.dumps(webhook_data))
            return True
            
        except Exception as e:
            logging.error(f"Error handling device webhook: {str(e)}")
            return False
    
    async def handle_emr_webhook(self, source: str, payload: Dict[str, Any]) -> bool:
        """Handle webhook from EMR systems"""
        try:
            # Queue EMR webhook for processing
            webhook_data = {
                "source": source,
                "type": "emr_update",
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.redis_client.lpush("webhook_queue", json.dumps(webhook_data))
            return True
            
        except Exception as e:
            logging.error(f"Error handling EMR webhook: {str(e)}")
            return False
    
    async def handle_lab_webhook(self, source: str, payload: Dict[str, Any]) -> bool:
        """Handle webhook from lab systems"""
        try:
            # Queue lab webhook for processing
            webhook_data = {
                "source": source,
                "type": "lab_update",
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.redis_client.lpush("webhook_queue", json.dumps(webhook_data))
            return True
            
        except Exception as e:
            logging.error(f"Error handling lab webhook: {str(e)}")
            return False
    
    async def process_webhook_queue(self):
        """Process queued webhook data"""
        while True:
            try:
                # Get next webhook
                webhook_data = self.redis_client.brpop("webhook_queue", timeout=30)
                if webhook_data:
                    webhook = json.loads(webhook_data[1])
                    await self._process_webhook(webhook)
                
            except Exception as e:
                logging.error(f"Error processing webhook queue: {str(e)}")
                await asyncio.sleep(5)
    
    async def _process_webhook(self, webhook: Dict[str, Any]):
        """Process individual webhook"""
        try:
            webhook_type = webhook.get("type")
            source = webhook.get("source")
            payload = webhook.get("payload")
            
            if webhook_type == "device_update":
                await self._process_device_webhook(source, payload)
            elif webhook_type == "emr_update":
                await self._process_emr_webhook(source, payload)
            elif webhook_type == "lab_update":
                await self._process_lab_webhook(source, payload)
            else:
                logging.warning(f"Unknown webhook type: {webhook_type}")
                
        except Exception as e:
            logging.error(f"Error processing webhook: {str(e)}")
    
    async def _process_device_webhook(self, source: str, payload: Dict[str, Any]):
        """Process device webhook data"""
        try:
            # Extract patient and device data
            patient_id = payload.get("patient_id")
            device_data = payload.get("data", {})
            
            if patient_id and device_data:
                # Queue for device sync processing
                sync_task = {
                    "type": "device_sync",
                    "patient_id": patient_id,
                    "device_type": source,
                    "data": device_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                self.redis_client.lpush("sync_queue", json.dumps(sync_task))
                
        except Exception as e:
            logging.error(f"Error processing device webhook: {str(e)}")
    
    async def _process_emr_webhook(self, source: str, payload: Dict[str, Any]):
        """Process EMR webhook data"""
        try:
            # Extract patient and clinical data
            patient_id = payload.get("patient_id")
            clinical_data = payload.get("data", {})
            
            if patient_id and clinical_data:
                # Queue for EMR sync processing
                sync_task = {
                    "type": "emr_sync",
                    "emr_name": source,
                    "patient_id": patient_id,
                    "data": clinical_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                self.redis_client.lpush("sync_queue", json.dumps(sync_task))
                
        except Exception as e:
            logging.error(f"Error processing EMR webhook: {str(e)}")
    
    async def _process_lab_webhook(self, source: str, payload: Dict[str, Any]):
        """Process lab webhook data"""
        try:
            # Extract lab results
            patient_id = payload.get("patient_id")
            lab_results = payload.get("results", [])
            
            if patient_id and lab_results:
                # Queue lab results for processing
                for result in lab_results:
                    result["patient_id"] = patient_id
                    result["source"] = source
                    self.redis_client.lpush("lab_results_queue", json.dumps(result))
                
        except Exception as e:
            logging.error(f"Error processing lab webhook: {str(e)}")
    
    async def get_webhook_stats(self) -> Dict[str, Any]:
        """Get webhook processing statistics"""
        try:
            stats = {
                "total_webhooks_processed": 0,
                "webhooks_by_source": {},
                "webhooks_by_type": {},
                "last_webhook_time": None,
                "error_count": 0
            }
            
            # Get webhook logs from Redis
            webhook_logs = self.redis_client.lrange("webhook_logs", 0, -1)
            
            for log_entry in webhook_logs:
                log_data = json.loads(log_entry)
                stats["total_webhooks_processed"] += 1
                
                source = log_data.get("source", "unknown")
                webhook_type = log_data.get("type", "unknown")
                
                stats["webhooks_by_source"][source] = stats["webhooks_by_source"].get(source, 0) + 1
                stats["webhooks_by_type"][webhook_type] = stats["webhooks_by_type"].get(webhook_type, 0) + 1
                
                if log_data.get("error"):
                    stats["error_count"] += 1
                
                # Update last webhook time
                webhook_time = log_data.get("timestamp")
                if webhook_time and (not stats["last_webhook_time"] or webhook_time > stats["last_webhook_time"]):
                    stats["last_webhook_time"] = webhook_time
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting webhook stats: {str(e)}")
            return {"error": str(e)} 