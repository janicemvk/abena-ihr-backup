from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

app = FastAPI(title="Provider Scheduling Service")

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class AppointmentType(str, Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    PROCEDURE = "procedure"
    LAB_WORK = "lab_work"

class Appointment(BaseModel):
    id: str
    patient_id: str
    provider_id: str
    appointment_type: AppointmentType
    status: AppointmentStatus
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class Schedule(BaseModel):
    id: str
    provider_id: str
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    appointments: List[Appointment]
    is_available: bool
    metadata: Dict[str, Any] = {}

class SchedulingEngine:
    def __init__(self):
        self.appointments: Dict[str, Appointment] = {}
        self.schedules: Dict[str, Schedule] = {}

    def create_appointment(self, patient_id: str, provider_id: str, 
                          appointment_type: AppointmentType, start_time: datetime, 
                          duration_minutes: int, notes: str = None) -> Appointment:
        appointment_id = str(uuid.uuid4())
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check for conflicts
        if self._has_conflict(provider_id, start_time, end_time):
            raise ValueError("Appointment conflicts with existing schedule")
        
        appointment = Appointment(
            id=appointment_id,
            patient_id=patient_id,
            provider_id=provider_id,
            appointment_type=appointment_type,
            status=AppointmentStatus.SCHEDULED,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            notes=notes,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        self.appointments[appointment_id] = appointment
        return appointment

    def _has_conflict(self, provider_id: str, start_time: datetime, end_time: datetime) -> bool:
        for appointment in self.appointments.values():
            if appointment.provider_id == provider_id and appointment.status != AppointmentStatus.CANCELLED:
                if (start_time < appointment.end_time and end_time > appointment.start_time):
                    return True
        return False

    def get_provider_schedule(self, provider_id: str, date: datetime.date) -> List[Appointment]:
        appointments = []
        for appointment in self.appointments.values():
            if (appointment.provider_id == provider_id and 
                appointment.start_time.date() == date and
                appointment.status != AppointmentStatus.CANCELLED):
                appointments.append(appointment)
        return sorted(appointments, key=lambda x: x.start_time)

    def update_appointment_status(self, appointment_id: str, status: AppointmentStatus) -> Appointment:
        if appointment_id not in self.appointments:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment = self.appointments[appointment_id]
        appointment.status = status
        appointment.updated_at = datetime.now()
        return appointment

    def cancel_appointment(self, appointment_id: str, reason: str = None) -> Appointment:
        appointment = self.update_appointment_status(appointment_id, AppointmentStatus.CANCELLED)
        if reason:
            appointment.notes = f"Cancelled: {reason}"
        return appointment

    def get_available_slots(self, provider_id: str, date: datetime.date, 
                           duration_minutes: int) -> List[Dict[str, datetime]]:
        # Simple implementation - in practice, you'd check provider availability
        slots = []
        start_hour = 9  # 9 AM
        end_hour = 17   # 5 PM
        
        current_time = datetime.combine(date, datetime.min.time().replace(hour=start_hour))
        end_time = datetime.combine(date, datetime.min.time().replace(hour=end_hour))
        
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            if not self._has_conflict(provider_id, current_time, slot_end):
                slots.append({
                    "start_time": current_time,
                    "end_time": slot_end
                })
            current_time += timedelta(minutes=30)  # 30-minute intervals
        
        return slots

    def get_patient_appointments(self, patient_id: str) -> List[Appointment]:
        return [appointment for appointment in self.appointments.values() 
                if appointment.patient_id == patient_id]

scheduling_engine = SchedulingEngine()

@app.post("/appointments")
async def create_appointment(appointment_data: Dict[str, Any]):
    try:
        appointment = scheduling_engine.create_appointment(
            patient_id=appointment_data["patient_id"],
            provider_id=appointment_data["provider_id"],
            appointment_type=AppointmentType(appointment_data["appointment_type"]),
            start_time=datetime.fromisoformat(appointment_data["start_time"]),
            duration_minutes=appointment_data["duration_minutes"],
            notes=appointment_data.get("notes")
        )
        return {"appointment": appointment}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/providers/{provider_id}/schedule/{date}")
async def get_provider_schedule(provider_id: str, date: str):
    try:
        schedule_date = datetime.fromisoformat(date).date()
        appointments = scheduling_engine.get_provider_schedule(provider_id, schedule_date)
        return {"appointments": appointments}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/appointments/{appointment_id}/status")
async def update_appointment_status(appointment_id: str, status: AppointmentStatus):
    try:
        appointment = scheduling_engine.update_appointment_status(appointment_id, status)
        return {"appointment": appointment}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: str, reason: str = None):
    try:
        appointment = scheduling_engine.cancel_appointment(appointment_id, reason)
        return {"appointment": appointment}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/providers/{provider_id}/slots/{date}")
async def get_available_slots(provider_id: str, date: str, duration_minutes: int = 30):
    try:
        schedule_date = datetime.fromisoformat(date).date()
        slots = scheduling_engine.get_available_slots(provider_id, schedule_date, duration_minutes)
        return {"slots": slots}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/appointments")
async def get_patient_appointments(patient_id: str):
    appointments = scheduling_engine.get_patient_appointments(patient_id)
    return {"appointments": appointments} 