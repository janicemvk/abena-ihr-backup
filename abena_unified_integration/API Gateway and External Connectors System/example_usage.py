#!/usr/bin/env python3
"""
Example Usage Script for Abena IHR Integration Layer
Demonstrates how to use the various components of the system
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Import the integration components
from api_gateway import APIGateway, PatientData, ObservationData, DeviceData
from device_adapters import DeviceManager, DeviceType, DeviceCredentials
from emr_connectors import EpicConnector, CernerConnector
from telemedicine_bridges import ZoomHealthBridge, TelemedicineManager
from lab_adapters import LabCorpAdapter, LabManager
from integration_orchestrator import IntegrationOrchestrator
from webhook_handler import WebhookHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_device_integration():
    """Example of integrating with wearable devices"""
    print("\n=== Device Integration Example ===")
    
    # Initialize Redis client (in production, use proper connection)
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    # Initialize device manager
    device_manager = DeviceManager(redis_client)
    
    # Example: Register a Fitbit device for a patient
    fitbit_credentials = DeviceCredentials(
        client_id="your_fitbit_client_id",
        client_secret="your_fitbit_client_secret",
        access_token="authorization_code_from_fitbit"
    )
    
    success = await device_manager.register_device(
        patient_id="patient_123",
        device_type=DeviceType.FITBIT,
        credentials=fitbit_credentials
    )
    
    if success:
        print("✅ Fitbit device registered successfully")
        
        # Sync data from the device
        observations = await device_manager.sync_device_data(
            patient_id="patient_123",
            device_type=DeviceType.FITBIT
        )
        
        print(f"📊 Synced {len(observations)} observations from Fitbit")
        for obs in observations[:3]:  # Show first 3 observations
            print(f"  - {obs.observation_type}: {obs.value} {obs.unit}")
    else:
        print("❌ Failed to register Fitbit device")

async def example_emr_integration():
    """Example of integrating with EMR systems"""
    print("\n=== EMR Integration Example ===")
    
    # Initialize Epic connector
    epic_connector = EpicConnector(
        base_url="https://fhir.epic.com",
        client_id="your_epic_client_id",
        private_key="your_epic_private_key"
    )
    
    # Authenticate with Epic
    if await epic_connector.authenticate():
        print("✅ Authenticated with Epic successfully")
        
        # Fetch patients from Epic
        patients = await epic_connector.fetch_patients()
        print(f"📋 Fetched {len(patients)} patients from Epic")
        
        # Fetch observations for a specific patient
        if patients:
            patient_id = patients[0].get("resource", {}).get("id")
            observations = await epic_connector.fetch_observations(patient_id)
            print(f"📊 Fetched {len(observations)} observations for patient {patient_id}")
    else:
        print("❌ Failed to authenticate with Epic")

async def example_telemedicine_integration():
    """Example of integrating with telemedicine platforms"""
    print("\n=== Telemedicine Integration Example ===")
    
    # Initialize telemedicine manager
    telemedicine_manager = TelemedicineManager()
    
    # Register Zoom bridge
    zoom_bridge = ZoomHealthBridge(
        api_key="your_zoom_api_key",
        api_secret="your_zoom_api_secret",
        account_id="your_zoom_account_id"
    )
    telemedicine_manager.register_bridge("zoom", zoom_bridge)
    
    # Create a telemedicine appointment
    appointment_data = {
        "patient_name": "John Doe",
        "start_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "duration": 30,
        "provider_id": "provider_123"
    }
    
    appointment_id = await telemedicine_manager.create_appointment("zoom", appointment_data)
    
    if appointment_id:
        print(f"✅ Created Zoom appointment: {appointment_id}")
        
        # Get session notes (would be available after the appointment)
        notes = await telemedicine_manager.get_session_notes("zoom", appointment_id)
        print(f"📝 Session notes: {notes}")
    else:
        print("❌ Failed to create Zoom appointment")

async def example_lab_integration():
    """Example of integrating with lab systems"""
    print("\n=== Lab Integration Example ===")
    
    # Initialize lab manager
    lab_manager = LabManager()
    
    # Register LabCorp adapter
    labcorp_adapter = LabCorpAdapter(
        client_id="your_labcorp_client_id",
        client_secret="your_labcorp_client_secret",
        facility_id="your_facility_id"
    )
    lab_manager.register_adapter("labcorp", labcorp_adapter)
    
    # Submit a lab order
    order_data = {
        "patient_id": "patient_123",
        "tests": ["CBC", "CMP", "Lipid Panel"],
        "ordering_provider": "provider_123",
        "facility_id": "facility_123"
    }
    
    order_id = await lab_manager.submit_lab_order("labcorp", order_data)
    
    if order_id:
        print(f"✅ Submitted lab order: {order_id}")
        
        # Fetch lab results
        results = await lab_manager.fetch_lab_results("labcorp", "patient_123")
        print(f"📊 Fetched {len(results)} lab results")
    else:
        print("❌ Failed to submit lab order")

async def example_api_gateway_usage():
    """Example of using the API Gateway"""
    print("\n=== API Gateway Example ===")
    
    # Initialize API Gateway
    api_gateway = APIGateway(
        db_url="postgresql://user:pass@localhost/abena_ihr",
        redis_url="redis://localhost:6379"
    )
    
    # Example: Create a patient
    patient_data = PatientData(
        mrn="MRN123456",
        first_name="John",
        last_name="Doe",
        gender="M",
        birth_date="1990-01-01",
        email="john.doe@example.com",
        phone="+1234567890"
    )
    
    print(f"👤 Creating patient: {patient_data.first_name} {patient_data.last_name}")
    
    # Example: Create an observation
    observation_data = ObservationData(
        patient_id="patient_123",
        observation_type="blood_pressure",
        value=120.0,
        unit="mmHg",
        timestamp=datetime.utcnow(),
        source_device="manual_entry"
    )
    
    print(f"📊 Creating observation: {observation_data.observation_type}")

async def example_webhook_processing():
    """Example of webhook processing"""
    print("\n=== Webhook Processing Example ===")
    
    # Initialize Redis client
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    # Initialize webhook handler
    webhook_handler = WebhookHandler(redis_client)
    webhook_handler.register_webhook_secret("fitbit", "your_fitbit_webhook_secret")
    
    # Example webhook payload from Fitbit
    webhook_payload = {
        "patient_id": "patient_123",
        "data": {
            "heart_rate": 75,
            "steps": 8500,
            "calories": 2100,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # Process the webhook
    success = await webhook_handler.handle_device_webhook("fitbit", webhook_payload)
    
    if success:
        print("✅ Webhook processed successfully")
    else:
        print("❌ Failed to process webhook")

async def example_integration_orchestrator():
    """Example of using the integration orchestrator"""
    print("\n=== Integration Orchestrator Example ===")
    
    # Initialize Redis client
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    # Initialize orchestrator
    orchestrator = IntegrationOrchestrator(redis_client)
    
    # Register EMR connectors
    epic_connector = EpicConnector(
        base_url="https://fhir.epic.com",
        client_id="your_epic_client_id",
        private_key="your_epic_private_key"
    )
    orchestrator.register_emr_connector("epic", epic_connector)
    
    # Schedule regular sync for a patient
    await orchestrator.schedule_sync(
        patient_id="patient_123",
        sync_type="device_sync",
        interval_hours=24
    )
    
    print("✅ Scheduled daily device sync for patient_123")
    
    # Get sync status
    status = await orchestrator.get_sync_status("patient_123")
    print(f"📊 Sync status: {status}")

async def main():
    """Main function to run all examples"""
    print("🚀 Abena IHR Integration Layer - Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        await example_device_integration()
        await example_emr_integration()
        await example_telemedicine_integration()
        await example_lab_integration()
        await example_api_gateway_usage()
        await example_webhook_processing()
        await example_integration_orchestrator()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}")
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    # Run the examples
    asyncio.run(main()) 