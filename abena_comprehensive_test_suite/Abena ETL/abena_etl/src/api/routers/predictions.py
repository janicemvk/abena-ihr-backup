from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult
from src.integration.system_orchestrator import AbenaIntegratedSystem

router = APIRouter()

@router.post("/treatment-response", response_model=PredictionResult)
async def predict_treatment_response(
    patient: PatientProfile,
    treatment: TreatmentPlan,
    system: AbenaIntegratedSystem = Depends()
):
    """Predict treatment response for a patient"""
    try:
        result = system.predictive_engine.predict_treatment_response(patient, treatment)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-plan")
async def generate_treatment_plan(
    patient_id: str,
    system: AbenaIntegratedSystem = Depends()
):
    """Generate comprehensive treatment plan using all modules"""
    try:
        plan = system.generate_treatment_plan(patient_id)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))