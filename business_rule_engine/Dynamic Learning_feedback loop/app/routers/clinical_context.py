# app/routers/clinical_context.py - Clinical Context with Abena SDK Integration
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from pydantic import BaseModel

# Import Abena SDK
from abena_sdk import AbenaSDK
from abena_sdk.exceptions import AbenaSDKError

router = APIRouter()

class ClinicalContextRequest(BaseModel):
    patient_id: str
    context_types: List[str] = ["medical_history", "current_treatments", "risk_factors"]
    include_genomics: bool = True
    include_social_determinants: bool = True

class ClinicalContextResponse(BaseModel):
    patient_id: str
    context_data: Dict[str, Any]
    risk_assessment: Dict[str, float]
    recommendations: List[str]
    generated_at: datetime

# Get SDK instance from main app
def get_abena_sdk() -> AbenaSDK:
    from app.main import abena_sdk
    if not abena_sdk:
        raise HTTPException(status_code=503, detail="Abena SDK not available")
    return abena_sdk

@router.post("/context", response_model=ClinicalContextResponse)
async def get_clinical_context(
    request: ClinicalContextRequest,
    user_info: dict = Depends(lambda: {}),
    sdk: AbenaSDK = Depends(get_abena_sdk)
):
    """
    Get comprehensive clinical context using Abena SDK data integration
    """
    try:
        # Get clinical context via SDK with privacy controls
        context_data = await sdk.get_clinical_context(
            patient_id=request.patient_id,
            context_types=request.context_types,
            include_genomics=request.include_genomics,
            include_social_determinants=request.include_social_determinants,
            user_id=user_info.get('user_id'),
            purpose='clinical_decision_support'
        )
        
        # Generate risk assessment via SDK
        risk_assessment = await sdk.generate_risk_assessment(
            patient_id=request.patient_id,
            context_data=context_data,
            user_id=user_info.get('user_id')
        )
        
        # Get contextual recommendations via SDK
        recommendations = await sdk.get_contextual_recommendations(
            patient_id=request.patient_id,
            context_data=context_data,
            risk_assessment=risk_assessment,
            user_id=user_info.get('user_id')
        )
        
        return ClinicalContextResponse(
            patient_id=request.patient_id,
            context_data=context_data,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        logging.error(f"Clinical context error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve clinical context: {str(e)}")

@router.get("/risk-factors/{patient_id}", response_model=Dict[str, Any])
async def get_risk_factors(
    patient_id: str,
    include_genetic: bool = True,
    include_environmental: bool = True,
    user_info: dict = Depends(lambda: {}),
    sdk: AbenaSDK = Depends(get_abena_sdk)
):
    """
    Get patient risk factors using Abena SDK risk analysis
    """
    try:
        # Get comprehensive risk factors via SDK
        risk_factors = await sdk.get_patient_risk_factors(
            patient_id=patient_id,
            include_genetic=include_genetic,
            include_environmental=include_environmental,
            user_id=user_info.get('user_id')
        )
        
        return {
            "patient_id": patient_id,
            "risk_factors": risk_factors,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Risk factors error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk factors: {str(e)}") 