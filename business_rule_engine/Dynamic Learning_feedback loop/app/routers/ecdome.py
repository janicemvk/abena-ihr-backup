# app/routers/ecdome.py - eCdome Integration with Abena SDK
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import uuid
from pydantic import BaseModel, Field

# Import Abena SDK
from abena_sdk import AbenaSDK
from abena_sdk.exceptions import AbenaSDKError

router = APIRouter()

class EcdomeAnalysisRequest(BaseModel):
    patient_id: str
    analysis_type: str = Field(..., description="Type: pharmacogenomics, drug_interactions, dosing_optimization")
    medications: List[str] = []
    genetic_variants: Optional[Dict[str, Any]] = None
    clinical_parameters: Optional[Dict[str, Any]] = None

class EcdomeResponse(BaseModel):
    analysis_id: str
    patient_id: str
    analysis_type: str
    recommendations: List[Dict[str, Any]]
    drug_interactions: List[Dict[str, Any]]
    dosing_adjustments: List[Dict[str, Any]]
    confidence_score: float
    generated_at: datetime

# Get SDK instance from main app
def get_abena_sdk() -> AbenaSDK:
    from app.main import abena_sdk
    if not abena_sdk:
        raise HTTPException(status_code=503, detail="Abena SDK not available")
    return abena_sdk

@router.post("/analyze", response_model=EcdomeResponse)
async def ecdome_analysis(
    request: EcdomeAnalysisRequest,
    background_tasks: BackgroundTasks,
    user_info: dict = Depends(lambda: {}),
    sdk: AbenaSDK = Depends(get_abena_sdk)
):
    """
    Perform eCdome pharmacogenomic analysis using Abena SDK
    """
    try:
        analysis_id = str(uuid.uuid4())
        
        # Perform eCdome analysis via SDK with genomic integration
        analysis_result = await sdk.perform_pharmacogenomic_analysis(
            patient_id=request.patient_id,
            analysis_type=request.analysis_type,
            medications=request.medications,
            genetic_variants=request.genetic_variants,
            clinical_parameters=request.clinical_parameters,
            user_id=user_info.get('user_id')
        )
        
        # Store analysis results via SDK
        await sdk.store_ecdome_analysis(
            analysis_id=analysis_id,
            patient_id=request.patient_id,
            analysis_data=analysis_result,
            user_id=user_info.get('user_id')
        )
        
        # Background task for clinical validation
        background_tasks.add_task(validate_ecdome_analysis, analysis_id, analysis_result)
        
        return EcdomeResponse(
            analysis_id=analysis_id,
            patient_id=request.patient_id,
            analysis_type=request.analysis_type,
            recommendations=analysis_result.get('recommendations', []),
            drug_interactions=analysis_result.get('drug_interactions', []),
            dosing_adjustments=analysis_result.get('dosing_adjustments', []),
            confidence_score=analysis_result.get('confidence_score', 0.0),
            generated_at=datetime.now()
        )
        
    except Exception as e:
        logging.error(f"eCdome analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to perform eCdome analysis: {str(e)}")

@router.get("/drug-interactions/{patient_id}", response_model=Dict[str, Any])
async def get_drug_interactions(
    patient_id: str,
    current_medications: Optional[str] = None,
    user_info: dict = Depends(lambda: {}),
    sdk: AbenaSDK = Depends(get_abena_sdk)
):
    """
    Get drug interactions using Abena SDK pharmacovigilance capabilities
    """
    try:
        medications_list = current_medications.split(',') if current_medications else []
        
        # Get drug interactions via SDK
        interactions = await sdk.get_drug_interactions(
            patient_id=patient_id,
            medications=medications_list,
            include_genetic_factors=True,
            user_id=user_info.get('user_id')
        )
        
        return {
            "patient_id": patient_id,
            "interactions": interactions,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Drug interactions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve drug interactions: {str(e)}")

async def validate_ecdome_analysis(analysis_id: str, analysis_data: Dict):
    """Background validation of eCdome analysis results"""
    try:
        sdk = get_abena_sdk()
        
        # Validate eCdome analysis using SDK clinical validation
        validation_result = await sdk.validate_ecdome_analysis(
            analysis_id=analysis_id,
            analysis_data=analysis_data,
            validation_methods=['clinical_guidelines', 'peer_review', 'literature_review']
        )
        
        logging.info(f"eCdome analysis validation completed for {analysis_id}: {validation_result['status']}")
        
    except Exception as e:
        logging.error(f"eCdome validation error: {str(e)}") 