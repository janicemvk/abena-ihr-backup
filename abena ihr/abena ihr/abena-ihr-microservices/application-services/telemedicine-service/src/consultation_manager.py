from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

app = FastAPI(title="Telemedicine Consultation Manager")

class ConsultationStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class ConsultationType(str, Enum):
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    SPECIALIST = "specialist"
    MENTAL_HEALTH = "mental_health"
    PEDIATRIC = "pediatric"

class PrescriptionStatus(str, Enum):
    DRAFT = "draft"
    PRESCRIBED = "prescribed"
    DISPENSED = "dispensed"
    CANCELLED = "cancelled"

class ClinicalNote(BaseModel):
    id: str
    consultation_id: str
    provider_id: str
    note_type: str  # subjective, objective, assessment, plan
    content: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class Prescription(BaseModel):
    id: str
    consultation_id: str
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str
    status: PrescriptionStatus
    prescribed_by: str
    prescribed_at: datetime
    dispensed_at: Optional[datetime] = None
    pharmacy_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class Consultation(BaseModel):
    id: str
    patient_id: str
    provider_id: str
    appointment_id: str
    video_session_id: Optional[str] = None
    consultation_type: ConsultationType
    status: ConsultationStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class ConsultationManager:
    def __init__(self):
        self.consultations: Dict[str, Consultation] = {}
        self.clinical_notes: Dict[str, List[ClinicalNote]] = {}
        self.prescriptions: Dict[str, List[Prescription]] = {}
        self.follow_ups: Dict[str, List[Dict]] = {}

    def create_consultation(self, patient_id: str, provider_id: str, 
                          appointment_id: str, consultation_type: ConsultationType,
                          duration_minutes: int = 30) -> Consultation:
        consultation_id = str(uuid.uuid4())
        
        consultation = Consultation(
            id=consultation_id,
            patient_id=patient_id,
            provider_id=provider_id,
            appointment_id=appointment_id,
            consultation_type=consultation_type,
            status=ConsultationStatus.SCHEDULED,
            duration_minutes=duration_minutes,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        self.consultations[consultation_id] = consultation
        self.clinical_notes[consultation_id] = []
        self.prescriptions[consultation_id] = []
        
        return consultation

    def start_consultation(self, consultation_id: str, video_session_id: str = None) -> Consultation:
        if consultation_id not in self.consultations:
            raise ValueError(f"Consultation {consultation_id} not found")
        
        consultation = self.consultations[consultation_id]
        consultation.status = ConsultationStatus.IN_PROGRESS
        consultation.start_time = datetime.now()
        consultation.video_session_id = video_session_id
        consultation.updated_at = datetime.now()
        
        return consultation

    def complete_consultation(self, consultation_id: str, diagnosis: str = None,
                            treatment_plan: str = None, follow_up_required: bool = False,
                            follow_up_date: datetime = None) -> Consultation:
        if consultation_id not in self.consultations:
            raise ValueError(f"Consultation {consultation_id} not found")
        
        consultation = self.consultations[consultation_id]
        consultation.status = ConsultationStatus.COMPLETED
        consultation.end_time = datetime.now()
        consultation.diagnosis = diagnosis
        consultation.treatment_plan = treatment_plan
        consultation.follow_up_required = follow_up_required
        consultation.follow_up_date = follow_up_date
        consultation.updated_at = datetime.now()
        
        # Schedule follow-up if required
        if follow_up_required and follow_up_date:
            self._schedule_follow_up(consultation_id, follow_up_date)
        
        return consultation

    def _schedule_follow_up(self, consultation_id: str, follow_up_date: datetime):
        if consultation_id not in self.follow_ups:
            self.follow_ups[consultation_id] = []
        
        follow_up = {
            "id": str(uuid.uuid4()),
            "consultation_id": consultation_id,
            "scheduled_date": follow_up_date,
            "status": "scheduled",
            "created_at": datetime.now()
        }
        
        self.follow_ups[consultation_id].append(follow_up)

    def add_clinical_note(self, consultation_id: str, provider_id: str, 
                         note_type: str, content: str) -> ClinicalNote:
        if consultation_id not in self.consultations:
            raise ValueError(f"Consultation {consultation_id} not found")
        
        note = ClinicalNote(
            id=str(uuid.uuid4()),
            consultation_id=consultation_id,
            provider_id=provider_id,
            note_type=note_type,
            content=content,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        self.clinical_notes[consultation_id].append(note)
        return note

    def create_prescription(self, consultation_id: str, medication_name: str,
                          dosage: str, frequency: str, duration: str,
                          instructions: str, prescribed_by: str) -> Prescription:
        if consultation_id not in self.consultations:
            raise ValueError(f"Consultation {consultation_id} not found")
        
        prescription = Prescription(
            id=str(uuid.uuid4()),
            consultation_id=consultation_id,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            duration=duration,
            instructions=instructions,
            status=PrescriptionStatus.PRESCRIBED,
            prescribed_by=prescribed_by,
            prescribed_at=datetime.now(),
            metadata={}
        )
        
        self.prescriptions[consultation_id].append(prescription)
        return prescription

    def update_prescription_status(self, prescription_id: str, status: PrescriptionStatus,
                                 pharmacy_id: str = None) -> Prescription:
        # Find prescription across all consultations
        for prescriptions in self.prescriptions.values():
            for prescription in prescriptions:
                if prescription.id == prescription_id:
                    prescription.status = status
                    prescription.updated_at = datetime.now()
                    
                    if status == PrescriptionStatus.DISPENSED:
                        prescription.dispensed_at = datetime.now()
                        prescription.pharmacy_id = pharmacy_id
                    
                    return prescription
        
        raise ValueError(f"Prescription {prescription_id} not found")

    def get_consultation(self, consultation_id: str) -> Optional[Consultation]:
        return self.consultations.get(consultation_id)

    def get_consultation_notes(self, consultation_id: str) -> List[ClinicalNote]:
        return self.clinical_notes.get(consultation_id, [])

    def get_consultation_prescriptions(self, consultation_id: str) -> List[Prescription]:
        return self.prescriptions.get(consultation_id, [])

    def get_patient_consultations(self, patient_id: str) -> List[Consultation]:
        consultations = [consultation for consultation in self.consultations.values() 
                        if consultation.patient_id == patient_id]
        return sorted(consultations, key=lambda x: x.created_at, reverse=True)

    def get_provider_consultations(self, provider_id: str) -> List[Consultation]:
        consultations = [consultation for consultation in self.consultations.values() 
                        if consultation.provider_id == provider_id]
        return sorted(consultations, key=lambda x: x.created_at, reverse=True)

    def get_active_consultations(self) -> List[Consultation]:
        active_consultations = [consultation for consultation in self.consultations.values() 
                              if consultation.status == ConsultationStatus.IN_PROGRESS]
        return sorted(active_consultations, key=lambda x: x.start_time)

    def get_follow_ups(self, consultation_id: str) -> List[Dict]:
        return self.follow_ups.get(consultation_id, [])

    def update_consultation_metadata(self, consultation_id: str, metadata: Dict[str, Any]) -> Consultation:
        if consultation_id not in self.consultations:
            raise ValueError(f"Consultation {consultation_id} not found")
        
        consultation = self.consultations[consultation_id]
        consultation.metadata.update(metadata)
        consultation.updated_at = datetime.now()
        
        return consultation

consultation_manager = ConsultationManager()

@app.post("/consultations")
async def create_consultation(consultation_data: Dict[str, Any]):
    try:
        consultation = consultation_manager.create_consultation(
            patient_id=consultation_data["patient_id"],
            provider_id=consultation_data["provider_id"],
            appointment_id=consultation_data["appointment_id"],
            consultation_type=ConsultationType(consultation_data["consultation_type"]),
            duration_minutes=consultation_data.get("duration_minutes", 30)
        )
        return {"consultation": consultation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/consultations/{consultation_id}/start")
async def start_consultation(consultation_id: str, video_session_id: str = None):
    try:
        consultation = consultation_manager.start_consultation(consultation_id, video_session_id)
        return {"consultation": consultation}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/consultations/{consultation_id}/complete")
async def complete_consultation(consultation_id: str, completion_data: Dict[str, Any]):
    try:
        consultation = consultation_manager.complete_consultation(
            consultation_id=consultation_id,
            diagnosis=completion_data.get("diagnosis"),
            treatment_plan=completion_data.get("treatment_plan"),
            follow_up_required=completion_data.get("follow_up_required", False),
            follow_up_date=datetime.fromisoformat(completion_data["follow_up_date"]) if completion_data.get("follow_up_date") else None
        )
        return {"consultation": consultation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/consultations/{consultation_id}/notes")
async def add_clinical_note(consultation_id: str, note_data: Dict[str, Any]):
    try:
        note = consultation_manager.add_clinical_note(
            consultation_id=consultation_id,
            provider_id=note_data["provider_id"],
            note_type=note_data["note_type"],
            content=note_data["content"]
        )
        return {"note": note}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/consultations/{consultation_id}/prescriptions")
async def create_prescription(consultation_id: str, prescription_data: Dict[str, Any]):
    try:
        prescription = consultation_manager.create_prescription(
            consultation_id=consultation_id,
            medication_name=prescription_data["medication_name"],
            dosage=prescription_data["dosage"],
            frequency=prescription_data["frequency"],
            duration=prescription_data["duration"],
            instructions=prescription_data["instructions"],
            prescribed_by=prescription_data["prescribed_by"]
        )
        return {"prescription": prescription}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/prescriptions/{prescription_id}/status")
async def update_prescription_status(prescription_id: str, status: PrescriptionStatus, pharmacy_id: str = None):
    try:
        prescription = consultation_manager.update_prescription_status(prescription_id, status, pharmacy_id)
        return {"prescription": prescription}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/consultations/{consultation_id}")
async def get_consultation(consultation_id: str):
    consultation = consultation_manager.get_consultation(consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return {"consultation": consultation}

@app.get("/consultations/{consultation_id}/notes")
async def get_consultation_notes(consultation_id: str):
    notes = consultation_manager.get_consultation_notes(consultation_id)
    return {"notes": notes}

@app.get("/consultations/{consultation_id}/prescriptions")
async def get_consultation_prescriptions(consultation_id: str):
    prescriptions = consultation_manager.get_consultation_prescriptions(consultation_id)
    return {"prescriptions": prescriptions}

@app.get("/patients/{patient_id}/consultations")
async def get_patient_consultations(patient_id: str):
    consultations = consultation_manager.get_patient_consultations(patient_id)
    return {"consultations": consultations}

@app.get("/providers/{provider_id}/consultations")
async def get_provider_consultations(provider_id: str):
    consultations = consultation_manager.get_provider_consultations(provider_id)
    return {"consultations": consultations}

@app.get("/consultations/active")
async def get_active_consultations():
    consultations = consultation_manager.get_active_consultations()
    return {"consultations": consultations}

@app.get("/consultations/{consultation_id}/follow-ups")
async def get_follow_ups(consultation_id: str):
    follow_ups = consultation_manager.get_follow_ups(consultation_id)
    return {"follow_ups": follow_ups}

@app.put("/consultations/{consultation_id}/metadata")
async def update_consultation_metadata(consultation_id: str, metadata: Dict[str, Any]):
    try:
        consultation = consultation_manager.update_consultation_metadata(consultation_id, metadata)
        return {"consultation": consultation}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 