#!/usr/bin/env python3
"""
Abena IHR - Integration Layer
Complete implementation with API Gateway, Device Adapters, EMR Connectors
"""

import asyncio
import logging
from fastapi import FastAPI
import uvicorn

from api_gateway import APIGateway
from integration_orchestrator import IntegrationOrchestrator
from webhook_handler import WebhookHandler
from emr_connectors import EpicConnector, CernerConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_integration_app():
    """Create the complete integration application"""
    
    # Initialize API Gateway
    api_gateway = APIGateway(
        db_url="postgresql://user:pass@localhost/abena_ihr",
        redis_url="redis://localhost:6379"
    )
    
    # Initialize Integration Orchestrator
    orchestrator = IntegrationOrchestrator(api_gateway.redis_client)
    
    # Register EMR connectors
    epic_connector = EpicConnector(
        base_url="https://fhir.epic.com",
        client_id="your_epic_client_id",
        private_key="your_epic_private_key"
    )
    orchestrator.register_emr_connector("epic", epic_connector)
    
    cerner_connector = CernerConnector(
        base_url="https://fhir-open.cerner.com",
        client_id="your_cerner_client_id",
        client_secret="your_cerner_client_secret"
    )
    orchestrator.register_emr_connector("cerner", cerner_connector)
    
    # Initialize Webhook Handler
    webhook_handler = WebhookHandler(api_gateway.redis_client)
    webhook_handler.register_webhook_secret("fitbit", "your_fitbit_webhook_secret")
    webhook_handler.register_webhook_secret("epic", "your_epic_webhook_secret")
    
    # Add webhook endpoints to API Gateway
    @api_gateway.app.post("/webhooks/{source}")
    async def handle_webhook(source: str, request):
        """Generic webhook endpoint"""
        try:
            payload = await request.body()
            signature = request.headers.get("X-Signature", "")
            
            # Verify signature
            if not webhook_handler.verify_webhook_signature(source, payload, signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            # Parse payload
            data = json.loads(payload)
            
            # Route to appropriate handler
            if source in ["fitbit", "garmin", "apple_health"]:
                success = await webhook_handler.handle_device_webhook(source, data)
            elif source in ["epic", "cerner"]:
                success = await webhook_handler.handle_emr_webhook(source, data)
            else:
                raise HTTPException(status_code=400, detail="Unknown webhook source")
            
            if success:
                return {"status": "received"}
            else:
                raise HTTPException(status_code=500, detail="Processing failed")
                
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    # Add background task for processing sync queue
    @api_gateway.app.on_event("startup")
    async def startup_event():
        """Start background tasks"""
        asyncio.create_task(orchestrator.process_sync_queue())
    
    return api_gateway.app

if __name__ == "__main__":
    # Run the FastAPI application
    app = create_integration_app()
    uvicorn.run(app, host="0.0.0.0", port=8000) 