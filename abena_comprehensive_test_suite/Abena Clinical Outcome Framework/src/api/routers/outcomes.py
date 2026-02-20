from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime

from src.clinical_outcomes.data_collection import outcome_router

# Create main router
router = APIRouter()

# Include the outcome collection router
router.include_router(
    outcome_router,
    prefix="/clinical-outcomes",
    tags=["clinical-outcomes"]
)

# Add any additional outcome-related endpoints here
@router.get("/health")
async def health_check():
    """Health check endpoint for the clinical outcomes API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "clinical-outcomes-api"
    } 