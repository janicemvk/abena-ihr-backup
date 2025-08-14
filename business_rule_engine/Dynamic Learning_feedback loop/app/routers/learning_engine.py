# app/routers/learning_engine.py - Learning Engine with Abena SDK Integration
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging
from pydantic import BaseModel, Field

# Import Abena SDK
from abena_sdk import AbenaSDK
from abena_sdk.exceptions import AbenaSDKError

router = APIRouter()

# Enhanced data models
class LearningRequest(BaseModel):
    patient_id: str
    learning_type: str = Field(..., description="Type of learning: outcome_prediction, treatment_optimization, etc.")
    data_sources: List[str] = Field(default=["clinical_data", "feedback", "outcomes"])
    time_horizon: Optional[int] = Field(default=30, description="Days to consider for learning")

class LearningResponse(BaseModel):
    learning_id: str
    patient_id: str
    insights: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    recommendations: List[str]
    generated_at: datetime
    expires_at: datetime

# Get SDK instance from main app
def get_abena_sdk() -> AbenaSDK:
    from app.main import abena_sdk
    if not abena_sdk:
        raise HTTPException(status_code=503, detail="Abena SDK not available")
    return abena_sdk

@router.post("/generate-insights", response_model=LearningResponse)
async def generate_learning_insights(
    request: LearningRequest,
    background_tasks: BackgroundTasks,
    user_info: dict = Depends(lambda: {}),  # User dependency from main app
    sdk: AbenaSDK = Depends(get_abena_sdk)
):
    """
    Generate learning insights using Abena SDK machine learning capabilities
    """
    try:
        # Use SDK to generate insights with automatic learning
        insights_result = await sdk.generate_learning_insights(
            patient_id=request.patient_id,
            learning_type=request.learning_type,
            data_sources=request.data_sources,
            time_horizon_days=request.time_horizon,
            user_id=user_info.get('user_id')
        )
        
        learning_id = str(uuid.uuid4())
        
        # Store insights via SDK with automatic versioning
        await sdk.store_learning_insights(
            learning_id=learning_id,
            patient_id=request.patient_id,
            insights_data=insights_result,
            user_id=user_info.get('user_id')
        )
        
        # Background task to validate insights
        background_tasks.add_task(validate_insights_background, learning_id, insights_result)
        
        return LearningResponse(
            learning_id=learning_id,
            patient_id=request.patient_id,
            insights=insights_result.get('insights', []),
            confidence_scores=insights_result.get('confidence_scores', {}),
            recommendations=insights_result.get('recommendations', []),
            generated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=30)
        )
        
    except Exception as e:
        logging.error(f"Learning insights generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@router.get("/model-performance", response_model=Dict[str, Any])
async def get_model_performance(
    model_type: Optional[str] = None,
    user_info: dict = Depends(lambda: {}),
    sdk: AbenaSDK = Depends(get_abena_sdk)
):
    """
    Get learning model performance metrics using Abena SDK
    """
    try:
        # Get model performance via SDK
        performance_data = await sdk.get_model_performance_metrics(
            model_type=model_type,
            user_id=user_info.get('user_id'),
            include_historical=True
        )
        
        return {
            "performance_metrics": performance_data,
            "model_type": model_type or "all",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Model performance error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve model performance: {str(e)}")

async def validate_insights_background(learning_id: str, insights_data: Dict):
    """Background validation of generated insights"""
    try:
        sdk = get_abena_sdk()
        
        # Validate insights using SDK validation algorithms
        validation_result = await sdk.validate_generated_insights(
            learning_id=learning_id,
            insights_data=insights_data,
            validation_methods=['clinical_guidelines', 'peer_review', 'outcome_correlation']
        )
        
        logging.info(f"Insights validation completed for {learning_id}: {validation_result['status']}")
        
    except Exception as e:
        logging.error(f"Background validation error: {str(e)}") 