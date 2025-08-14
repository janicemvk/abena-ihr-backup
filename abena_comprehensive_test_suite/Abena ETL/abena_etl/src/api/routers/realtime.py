from typing import List, Dict
from fastapi import APIRouter
from src.realtime_biomarkers.realtime_biomarker_integration import RealTimeBiomarkerIntegration

router = APIRouter()
biomarker_system = RealTimeBiomarkerIntegration()

@router.get("/realtime/{patient_id}")
async def get_realtime_data(patient_id: str):
    """Get current real-time biomarker data"""
    return biomarker_system.get_real_time_patient_data(patient_id)

@router.get("/alerts/{patient_id}")
async def get_recent_alerts(patient_id: str, hours: int = 24):
    """Get recent biomarker alerts"""
    return biomarker_system.get_biomarker_alerts(patient_id, hours)

@router.post("/configure/{patient_id}")
async def configure_monitoring(patient_id: str, device_configs: List[Dict]):
    """Configure real-time monitoring for patient"""
    success = await biomarker_system.configure_patient_monitoring(patient_id, device_configs)
    return {"success": success} 