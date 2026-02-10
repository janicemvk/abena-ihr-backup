"""
Realtime Biomarker Integration

This module provides realtime biomarker data integration, monitoring,
and analysis capabilities for the Abena IHR Clinical Outcomes Management System.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.data_models import BiomarkerData
from ..core.utils import generate_uuid

# Configure logging
logger = logging.getLogger(__name__)

class RealtimeBiomarkerIntegration:
    """Realtime biomarker integration and monitoring."""
    def __init__(self):
        self.biomarker_streams: Dict[str, List[BiomarkerData]] = {}

    def ingest_biomarker(self, patient_id: str, biomarker_name: str, value: Any, unit: Optional[str] = None, source: str = "", is_realtime: bool = True) -> BiomarkerData:
        """Ingest a new biomarker reading for a patient."""
        biomarker = BiomarkerData(
            patient_id=patient_id,
            biomarker_name=biomarker_name,
            value=value,
            unit=unit,
            measurement_date=datetime.now(),
            source=source,
            is_realtime=is_realtime
        )
        if patient_id not in self.biomarker_streams:
            self.biomarker_streams[patient_id] = []
        self.biomarker_streams[patient_id].append(biomarker)
        logger.info(f"Ingested biomarker {biomarker_name} for patient {patient_id}")
        return biomarker

    def get_patient_biomarkers(self, patient_id: str) -> List[BiomarkerData]:
        """Get all biomarker readings for a patient."""
        return self.biomarker_streams.get(patient_id, [])

    def get_latest_biomarker(self, patient_id: str, biomarker_name: str) -> Optional[BiomarkerData]:
        """Get the latest reading for a specific biomarker."""
        readings = [b for b in self.biomarker_streams.get(patient_id, []) if b.biomarker_name == biomarker_name]
        if readings:
            return sorted(readings, key=lambda b: b.measurement_date, reverse=True)[0]
        return None

# Global instance
realtime_biomarker_integration = RealtimeBiomarkerIntegration()

def get_realtime_biomarker_integration() -> RealtimeBiomarkerIntegration:
    """Get the global realtime biomarker integration instance."""
    return realtime_biomarker_integration 