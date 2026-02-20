from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, time
from enum import Enum
import uuid
import pytz
from zoneinfo import ZoneInfo

app = FastAPI(title="Telemedicine Scheduling Service")

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

class AppointmentType(str, Enum):
    INITIAL_CONSULTATION = "initial_consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    SPECIALIST_CONSULTATION = "specialist_consultation"
    MENTAL_HEALTH = "mental_health"
    PEDIATRIC = "pediatric"

class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BUSY = "busy"
    BREAK = "break"

class TelemedicineAppointment(BaseModel):
    id: str
    patient_id: str
    provider_id: str
    appointment_type: AppointmentType
    status: AppointmentStatus
    scheduled_time: datetime
    duration_minutes: int
    timezone: str
    video_session_id: Optional[str] = None
    notes: Optional[str] = None
    symptoms: Optional[str] = None
    urgency_level: str = "normal"
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class ProviderAvailability(BaseModel):
    id: str
    provider_id: str
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    timezone: str
    is_available: bool
    max_appointments_per_day: int
    appointment_duration_minutes: int
    break_duration_minutes: int = 0
    metadata: Dict[str, Any] = {}

class SchedulingEngine:
    def __init__(self):
        self.appointments: Dict[str, TelemedicineAppointment] = {}
        self.provider_availability: Dict[str, List[ProviderAvailability]] = {}
        self.blocked_times: Dict[str, List[Dict]] = {}

    def create_appointment(self, patient_id: str, provider_id: str, 
                          appointment_type: AppointmentType, scheduled_time: datetime,
                          duration_minutes: int, timezone: str, symptoms: str = None,
                          urgency_level: str = "normal") -> TelemedicineAppointment:
        appointment_id = str(uuid.uuid4())
        
        # Validate availability
        if not self._is_time_available(provider_id, scheduled_time, duration_minutes):
            raise ValueError("Requested time is not available")
        
        appointment = TelemedicineAppointment(
            id=appointment_id,
            patient_id=patient_id,
            provider_id=provider_id,
            appointment_type=appointment_type,
            status=AppointmentStatus.SCHEDULED,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            timezone=timezone,
            symptoms=symptoms,
            urgency_level=urgency_level,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        self.appointments[appointment_id] = appointment
        return appointment

    def _is_time_available(self, provider_id: str, start_time: datetime, duration_minutes: int) -> bool:
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check provider availability for the day
        day_of_week = start_time.weekday()
        provider_schedule = self.provider_availability.get(provider_id, [])
        
        # Find matching availability
        available_slot = None
        for availability in provider_schedule:
            if availability.day_of_week == day_of_week and availability.is_available:
                # Convert to provider's timezone
                provider_tz = ZoneInfo(availability.timezone)
                local_start = start_time.astimezone(provider_tz)
                local_end = end_time.astimezone(provider_tz)
                
                # Check if appointment fits within availability window
                availability_start = datetime.combine(local_start.date(), availability.start_time, tzinfo=provider_tz)
                availability_end = datetime.combine(local_start.date(), availability.end_time, tzinfo=provider_tz)
                
                if availability_start <= local_start and local_end <= availability_end:
                    available_slot = availability
                    break
        
        if not available_slot:
            return False
        
        # Check for conflicts with existing appointments
        for appointment in self.appointments.values():
            if (appointment.provider_id == provider_id and 
                appointment.status not in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]):
                
                appt_start = appointment.scheduled_time
                appt_end = appt_start + timedelta(minutes=appointment.duration_minutes)
                
                # Check for overlap
                if (start_time < appt_end and end_time > appt_start):
                    return False
        
        # Check for blocked times
        blocked_times = self.blocked_times.get(provider_id, [])
        for blocked in blocked_times:
            blocked_start = datetime.fromisoformat(blocked["start_time"])
            blocked_end = datetime.fromisoformat(blocked["end_time"])
            
            if (start_time < blocked_end and end_time > blocked_start):
                return False
        
        return True

    def get_available_slots(self, provider_id: str, date: datetime.date, 
                           duration_minutes: int, timezone: str) -> List[Dict[str, Any]]:
        slots = []
        provider_schedule = self.provider_availability.get(provider_id, [])
        
        # Find availability for the requested date
        day_of_week = date.weekday()
        availability = None
        for avail in provider_schedule:
            if avail.day_of_week == day_of_week and avail.is_available:
                availability = avail
                break
        
        if not availability:
            return slots
        
        # Generate time slots
        provider_tz = ZoneInfo(availability.timezone)
        request_tz = ZoneInfo(timezone)
        
        start_time = datetime.combine(date, availability.start_time, tzinfo=provider_tz)
        end_time = datetime.combine(date, availability.end_time, tzinfo=provider_tz)
        
        current_time = start_time
        slot_interval = max(duration_minutes, availability.appointment_duration_minutes)
        
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if slot is available
            if self._is_time_available(provider_id, current_time, duration_minutes):
                # Convert to request timezone
                slot_start_local = current_time.astimezone(request_tz)
                slot_end_local = slot_end.astimezone(request_tz)
                
                slots.append({
                    "start_time": slot_start_local.isoformat(),
                    "end_time": slot_end_local.isoformat(),
                    "duration_minutes": duration_minutes,
                    "timezone": timezone
                })
            
            # Move to next slot
            current_time += timedelta(minutes=slot_interval)
            
            # Add break if configured
            if availability.break_duration_minutes > 0:
                current_time += timedelta(minutes=availability.break_duration_minutes)
        
        return slots

    def confirm_appointment(self, appointment_id: str) -> TelemedicineAppointment:
        if appointment_id not in self.appointments:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment = self.appointments[appointment_id]
        appointment.status = AppointmentStatus.CONFIRMED
        appointment.updated_at = datetime.now()
        
        return appointment

    def cancel_appointment(self, appointment_id: str, reason: str = None) -> TelemedicineAppointment:
        if appointment_id not in self.appointments:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment = self.appointments[appointment_id]
        appointment.status = AppointmentStatus.CANCELLED
        appointment.updated_at = datetime.now()
        
        if reason:
            appointment.notes = f"Cancelled: {reason}"
        
        return appointment

    def reschedule_appointment(self, appointment_id: str, new_time: datetime) -> TelemedicineAppointment:
        if appointment_id not in self.appointments:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment = self.appointments[appointment_id]
        
        # Check if new time is available
        if not self._is_time_available(appointment.provider_id, new_time, appointment.duration_minutes):
            raise ValueError("New time is not available")
        
        appointment.scheduled_time = new_time
        appointment.status = AppointmentStatus.RESCHEDULED
        appointment.updated_at = datetime.now()
        
        return appointment

    def set_provider_availability(self, provider_id: str, availability: List[Dict]) -> List[ProviderAvailability]:
        provider_availabilities = []
        
        for avail_data in availability:
            avail = ProviderAvailability(
                id=str(uuid.uuid4()),
                provider_id=provider_id,
                day_of_week=avail_data["day_of_week"],
                start_time=time.fromisoformat(avail_data["start_time"]),
                end_time=time.fromisoformat(avail_data["end_time"]),
                timezone=avail_data["timezone"],
                is_available=avail_data.get("is_available", True),
                max_appointments_per_day=avail_data.get("max_appointments_per_day", 10),
                appointment_duration_minutes=avail_data.get("appointment_duration_minutes", 30),
                break_duration_minutes=avail_data.get("break_duration_minutes", 0),
                metadata=avail_data.get("metadata", {})
            )
            provider_availabilities.append(avail)
        
        self.provider_availability[provider_id] = provider_availabilities
        return provider_availabilities

    def block_time(self, provider_id: str, start_time: datetime, end_time: datetime, reason: str = None):
        if provider_id not in self.blocked_times:
            self.blocked_times[provider_id] = []
        
        self.blocked_times[provider_id].append({
            "id": str(uuid.uuid4()),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "reason": reason,
            "created_at": datetime.now().isoformat()
        })

    def get_provider_appointments(self, provider_id: str, date: datetime.date = None) -> List[TelemedicineAppointment]:
        appointments = [appt for appt in self.appointments.values() 
                       if appt.provider_id == provider_id]
        
        if date:
            appointments = [appt for appt in appointments 
                          if appt.scheduled_time.date() == date]
        
        return sorted(appointments, key=lambda x: x.scheduled_time)

    def get_patient_appointments(self, patient_id: str) -> List[TelemedicineAppointment]:
        appointments = [appt for appt in self.appointments.values() 
                       if appt.patient_id == patient_id]
        return sorted(appointments, key=lambda x: x.scheduled_time)

scheduling_engine = SchedulingEngine()

@app.post("/appointments")
async def create_appointment(appointment_data: Dict[str, Any]):
    try:
        appointment = scheduling_engine.create_appointment(
            patient_id=appointment_data["patient_id"],
            provider_id=appointment_data["provider_id"],
            appointment_type=AppointmentType(appointment_data["appointment_type"]),
            scheduled_time=datetime.fromisoformat(appointment_data["scheduled_time"]),
            duration_minutes=appointment_data["duration_minutes"],
            timezone=appointment_data["timezone"],
            symptoms=appointment_data.get("symptoms"),
            urgency_level=appointment_data.get("urgency_level", "normal")
        )
        return {"appointment": appointment}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/providers/{provider_id}/slots")
async def get_available_slots(provider_id: str, date: str, duration_minutes: int = 30, timezone: str = "UTC"):
    try:
        slot_date = datetime.fromisoformat(date).date()
        slots = scheduling_engine.get_available_slots(provider_id, slot_date, duration_minutes, timezone)
        return {"slots": slots}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/appointments/{appointment_id}/confirm")
async def confirm_appointment(appointment_id: str):
    try:
        appointment = scheduling_engine.confirm_appointment(appointment_id)
        return {"appointment": appointment}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: str, reason: str = None):
    try:
        appointment = scheduling_engine.cancel_appointment(appointment_id, reason)
        return {"appointment": appointment}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/appointments/{appointment_id}/reschedule")
async def reschedule_appointment(appointment_id: str, new_time: str):
    try:
        new_datetime = datetime.fromisoformat(new_time)
        appointment = scheduling_engine.reschedule_appointment(appointment_id, new_datetime)
        return {"appointment": appointment}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/providers/{provider_id}/availability")
async def set_provider_availability(provider_id: str, availability_data: List[Dict[str, Any]]):
    try:
        availability = scheduling_engine.set_provider_availability(provider_id, availability_data)
        return {"availability": availability}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/providers/{provider_id}/block-time")
async def block_time(provider_id: str, block_data: Dict[str, Any]):
    try:
        start_time = datetime.fromisoformat(block_data["start_time"])
        end_time = datetime.fromisoformat(block_data["end_time"])
        reason = block_data.get("reason")
        
        scheduling_engine.block_time(provider_id, start_time, end_time, reason)
        return {"message": "Time blocked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/providers/{provider_id}/appointments")
async def get_provider_appointments(provider_id: str, date: str = None):
    try:
        if date:
            appointment_date = datetime.fromisoformat(date).date()
            appointments = scheduling_engine.get_provider_appointments(provider_id, appointment_date)
        else:
            appointments = scheduling_engine.get_provider_appointments(provider_id)
        
        return {"appointments": appointments}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/appointments")
async def get_patient_appointments(patient_id: str):
    appointments = scheduling_engine.get_patient_appointments(patient_id)
    return {"appointments": appointments}

@app.get("/appointments/{appointment_id}")
async def get_appointment(appointment_id: str):
    appointment = scheduling_engine.appointments.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"appointment": appointment} 