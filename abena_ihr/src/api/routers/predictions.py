"""
Predictions API Router

This module provides RESTful API endpoints for managing predictions
in the Abena IHR system.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pydantic import BaseModel, Field, validator

from ...core.data_models import Prediction, PredictionConfidence
from ...core.utils import calculate_prediction_confidence

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models for API requests/responses
class PredictionRequest(BaseModel):
    """Request model for creating predictions."""
    patient_id: str = Field(..., description="ID of the patient")
    outcome_name: str = Field(..., description="Name of the outcome to predict")
    predicted_value: Any = Field(..., description="Predicted value")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    model_version: str = Field(..., description="Version of the prediction model")
    features_used: List[str] = Field(default_factory=list, description="Features used for prediction")
    
    @validator('outcome_name')
    def validate_outcome_name(cls, v):
        if not v.strip():
            raise ValueError("Outcome name cannot be empty")
        return v.strip()
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return v


class PredictionResponse(BaseModel):
    """Response model for prediction data."""
    id: str
    patient_id: str
    outcome_name: str
    predicted_value: Any
    confidence: PredictionConfidence
    confidence_score: float
    model_version: str
    features_used: List[str]
    prediction_date: datetime
    created_at: datetime


# Prediction Management Endpoints
@router.get("/predictions", response_model=List[PredictionResponse])
async def list_predictions(
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    outcome_name: Optional[str] = Query(None, description="Filter by outcome name"),
    confidence: Optional[PredictionConfidence] = Query(None, description="Filter by confidence level"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of predictions to return"),
    offset: int = Query(0, ge=0, description="Number of predictions to skip")
) -> List[PredictionResponse]:
    """
    List all predictions with optional filtering.
    
    Args:
        patient_id: Optional filter by patient ID
        outcome_name: Optional filter by outcome name
        confidence: Optional filter by confidence level
        limit: Maximum number of predictions to return
        offset: Number of predictions to skip
        
    Returns:
        List of predictions
    """
    try:
        # In a real app, this would query the database
        # For now, return empty list
        predictions = []
        
        # Apply pagination
        predictions = predictions[offset:offset + limit]
        
        return [
            PredictionResponse(
                id=prediction.id,
                patient_id=prediction.patient_id,
                outcome_name=prediction.outcome_name,
                predicted_value=prediction.predicted_value,
                confidence=prediction.confidence,
                confidence_score=prediction.confidence_score,
                model_version=prediction.model_version,
                features_used=prediction.features_used,
                prediction_date=prediction.prediction_date,
                created_at=prediction.created_at
            )
            for prediction in predictions
        ]
    except Exception as e:
        logger.error(f"Error listing predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list predictions")


@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: str = Path(..., description="ID of the prediction to retrieve")
) -> PredictionResponse:
    """
    Get a specific prediction by ID.
    
    Args:
        prediction_id: ID of the prediction to retrieve
        
    Returns:
        Prediction details
    """
    try:
        # In a real app, this would query the database
        # For now, return 404
        raise HTTPException(status_code=404, detail=f"Prediction '{prediction_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prediction {prediction_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prediction")


@router.post("/predictions", response_model=PredictionResponse, status_code=201)
async def create_prediction(
    prediction_data: PredictionRequest
) -> PredictionResponse:
    """
    Create a new prediction.
    
    Args:
        prediction_data: Prediction data
        
    Returns:
        Created prediction
    """
    try:
        confidence = calculate_prediction_confidence(prediction_data.confidence_score)
        
        prediction = Prediction(
            patient_id=prediction_data.patient_id,
            outcome_name=prediction_data.outcome_name,
            predicted_value=prediction_data.predicted_value,
            confidence=confidence,
            confidence_score=prediction_data.confidence_score,
            model_version=prediction_data.model_version,
            features_used=prediction_data.features_used
        )
        
        # In a real app, this would save to database
        
        return PredictionResponse(
            id=prediction.id,
            patient_id=prediction.patient_id,
            outcome_name=prediction.outcome_name,
            predicted_value=prediction.predicted_value,
            confidence=prediction.confidence,
            confidence_score=prediction.confidence_score,
            model_version=prediction.model_version,
            features_used=prediction.features_used,
            prediction_date=prediction.prediction_date,
            created_at=prediction.created_at
        )
    except Exception as e:
        logger.error(f"Error creating prediction: {e}")
        raise HTTPException(status_code=500, detail="Failed to create prediction")


@router.get("/predictions/patient/{patient_id}", response_model=List[PredictionResponse])
async def get_patient_predictions(
    patient_id: str = Path(..., description="ID of the patient"),
    outcome_name: Optional[str] = Query(None, description="Filter by outcome name"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of predictions to return")
) -> List[PredictionResponse]:
    """
    Get all predictions for a specific patient.
    
    Args:
        patient_id: ID of the patient
        outcome_name: Optional filter by outcome name
        limit: Maximum number of predictions to return
        
    Returns:
        List of predictions for the patient
    """
    try:
        # In a real app, this would query the database
        # For now, return empty list
        predictions = []
        
        # Apply limit
        predictions = predictions[:limit]
        
        return [
            PredictionResponse(
                id=prediction.id,
                patient_id=prediction.patient_id,
                outcome_name=prediction.outcome_name,
                predicted_value=prediction.predicted_value,
                confidence=prediction.confidence,
                confidence_score=prediction.confidence_score,
                model_version=prediction.model_version,
                features_used=prediction.features_used,
                prediction_date=prediction.prediction_date,
                created_at=prediction.created_at
            )
            for prediction in predictions
        ]
    except Exception as e:
        logger.error(f"Error getting predictions for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patient predictions")


@router.delete("/predictions/{prediction_id}")
async def delete_prediction(
    prediction_id: str = Path(..., description="ID of the prediction to delete")
) -> Dict[str, Any]:
    """
    Delete a prediction.
    
    Args:
        prediction_id: ID of the prediction to delete
        
    Returns:
        Deletion confirmation
    """
    try:
        # In a real app, this would delete from database
        # For now, return 404
        raise HTTPException(status_code=404, detail=f"Prediction '{prediction_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prediction {prediction_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete prediction") 