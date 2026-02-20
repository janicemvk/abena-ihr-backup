# Mock FastAPI app for testing - Updated to use Abena SDK
from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from typing import Dict, Any
from src.core.abena_sdk import AbenaSDK

# Initialize Abena SDK
abena_sdk = AbenaSDK({
    'authServiceUrl': 'http://localhost:3001',
    'dataServiceUrl': 'http://localhost:8001',
    'privacyServiceUrl': 'http://localhost:8002',
    'blockchainServiceUrl': 'http://localhost:8003'
})

app = FastAPI(title="Abena IHR System", version="2.0.0")

async def get_abena_sdk() -> AbenaSDK:
    """Dependency to get Abena SDK instance"""
    return abena_sdk

@app.get("/")
async def root():
    return {
        "message": "Abena IHR System",
        "version": "2.0.0",
        "integration_pattern": "Universal Abena SDK"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sdk_status": "connected"
    }

@app.post("/api/v1/predictions/treatment-response")
async def predict_treatment_response(
    patient: dict, 
    treatment: dict, 
    abena: AbenaSDK = Depends(get_abena_sdk)
):
    """Predict treatment response using Abena SDK"""
    try:
        patient_id = patient.get("patient_id")
        treatment_id = treatment.get("treatment_id")
        
        if not patient_id or not treatment_id:
            raise HTTPException(status_code=400, detail="Missing patient_id or treatment_id")
        
        # Get patient data through Abena SDK (handles auth, privacy, audit)
        patient_data = await abena.get_patient_data(patient_id, 'treatment_prediction')
        
        # Mock prediction logic
        success_probability = 0.75
        risk_score = 0.25
        
        # Save prediction result using Abena SDK
        await abena.save_treatment_plan(patient_id, {
            'prediction_type': 'treatment_response',
            'treatment_id': treatment_id,
            'success_probability': success_probability,
            'risk_score': risk_score,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            "patient_id": patient_id,
            "treatment_id": treatment_id,
            "success_probability": success_probability,
            "risk_score": risk_score,
            "key_factors": ["Test factor"],
            "warnings": ["Test warning"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Log error through Abena SDK
        await abena.create_alert({
            'type': 'prediction_failure',
            'message': f'Treatment response prediction failed: {str(e)}',
            'severity': 'high'
        })
        raise HTTPException(status_code=500, detail="Prediction failed")

@app.get("/api/v1/patients/{patient_id}/data")
async def get_patient_data(
    patient_id: str, 
    abena: AbenaSDK = Depends(get_abena_sdk)
):
    """Get patient data using Abena SDK"""
    try:
        # Get patient data through Abena SDK (handles auth, privacy, audit)
        patient_data = await abena.get_patient_data(patient_id, 'api_data_access')
        
        return {
            "patient_id": patient_id,
            "data": patient_data,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Log error through Abena SDK
        await abena.create_alert({
            'type': 'data_access_failure',
            'message': f'Patient data access failed: {str(e)}',
            'severity': 'medium'
        })
        raise HTTPException(status_code=500, detail="Data access failed")

@app.post("/api/v1/alerts")
async def create_alert(
    alert_data: Dict[str, Any], 
    abena: AbenaSDK = Depends(get_abena_sdk)
):
    """Create alert using Abena SDK"""
    try:
        # Create alert through Abena SDK (handles blockchain and audit)
        alert_id = await abena.create_alert(alert_data)
        
        return {
            "alert_id": alert_id,
            "status": "created",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Log error through Abena SDK
        await abena.create_alert({
            'type': 'alert_creation_failure',
            'message': f'Alert creation failed: {str(e)}',
            'severity': 'high'
        })
        raise HTTPException(status_code=500, detail="Alert creation failed") 