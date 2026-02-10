from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, time
from enum import Enum
import uuid
from zoneinfo import ZoneInfo

app = FastAPI(title="Patient Appointment Booking Service")

class AppointmentType(str, Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    SPECIALIST = "specialist"
    LAB_WORK = "lab_work"
    IMAGING = "imaging"
    PROCEDURE = "procedure"
    VACCINATION = "vaccination"
    MENTAL_HEALTH = "mental_health"
    PEDIATRIC = "pediatric"

class AppointmentStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

class BookingMethod(str, Enum):
    ONLINE = "online"
    PHONE = "phone"
    WALK_IN = "walk_in"
    REFERRAL = "referral"
    EMERGENCY = "emergency"

class ProviderSpecialty(str, Enum):
    PRIMARY_CARE = "primary_care"
    CARDIOLOGY = "cardiology"
    DERMATOLOGY = "dermatology"
    ENDOCRINOLOGY = "endocrinology"
    GASTROENTEROLOGY = "gastroenterology"
    NEUROLOGY = "neurology"
    ONCOLOGY = "oncology"
    ORTHOPEDICS = "orthopedics"
    PEDIATRICS = "pediatrics"
    PSYCHIATRY = "psychiatry"
    RADIOLOGY = "radiology"
    SURGERY = "surgery"
    UROLOGY = "urology"

class PatientAppointment(BaseModel):
    id: str
    patient_id: str
    provider_id: str
    appointment_type: AppointmentType
    status: AppointmentStatus
    booking_method: BookingMethod
    scheduled_time: datetime
    duration_minutes: int
    timezone: str
    reason: Optional[str] = None
    symptoms: Optional[str] = None
    urgency_level: str = "normal"
    is_telemedicine: bool = False
    video_session_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class ProviderAvailability(BaseModel):
    id: str
    provider_id: str
    specialty: ProviderSpecialty
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    timezone: str
    is_available: bool
    max_appointments_per_day: int
    appointment_duration_minutes: int
    break_duration_minutes: int = 0
    accepts_telemedicine: bool = True
    accepts_new_patients: bool = True
    metadata: Dict[str, Any] = {}

class ProviderInfo(BaseModel):
    id: str
    name: str
    specialty: ProviderSpecialty
    credentials: str
    languages: List[str]
    accepts_telemedicine: bool
    accepts_new_patients: bool
    rating: Optional[float] = None
    review_count: int = 0
    location: str
    timezone: str
    metadata: Dict[str, Any] = {}

class AppointmentBookingService:
    def __init__(self):
        self.appointments: Dict[str, PatientAppointment] = {}
        self.providers: Dict[str, ProviderInfo] = {}
        self.provider_availability: Dict[str, List[ProviderAvailability]] = {}
        self.blocked_times: Dict[str, List[Dict]] = {}

    def create_appointment(self, patient_id: str, provider_id: str, 
                          appointment_type: AppointmentType, scheduled_time: datetime,
                          duration_minutes: int, timezone: str, booking_method: BookingMethod,
                          reason: str = None, symptoms: str = None, urgency_level: str = "normal",
                          is_telemedicine: bool = False, location: str = None) -> PatientAppointment:
        appointment_id = str(uuid.uuid4())
        
        # Validate availability
        if not self._is_time_available(provider_id, scheduled_time, duration_minutes):
            raise ValueError("Requested time is not available")
        
        appointment = PatientAppointment(
            id=appointment_id,
            patient_id=patient_id,
            provider_id=provider_id,
            appointment_type=appointment_type,
            status=AppointmentStatus.REQUESTED,
            booking_method=booking_method,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            timezone=timezone,
            reason=reason,
            symptoms=symptoms,
            urgency_level=urgency_level,
            is_telemedicine=is_telemedicine,
            location=location,
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

    def search_providers(self, specialty: ProviderSpecialty = None, location: str = None,
                        accepts_telemedicine: bool = None, accepts_new_patients: bool = None,
                        date: datetime.date = None, timezone: str = "UTC") -> List[ProviderInfo]:
        providers = list(self.providers.values())
        
        # Filter by criteria
        if specialty:
            providers = [p for p in providers if p.specialty == specialty]
        
        if location:
            providers = [p for p in providers if location.lower() in p.location.lower()]
        
        if accepts_telemedicine is not None:
            providers = [p for p in providers if p.accepts_telemedicine == accepts_telemedicine]
        
        if accepts_new_patients is not None:
            providers = [p for p in providers if p.accepts_new_patients == accepts_new_patients]
        
        # Add availability information if date provided
        if date:
            for provider in providers:
                available_slots = self.get_available_slots(provider.id, date, 30, timezone)
                provider.metadata["available_slots"] = len(available_slots)
                provider.metadata["next_available"] = available_slots[0]["start_time"] if available_slots else None
        
        return sorted(providers, key=lambda x: (x.rating or 0, x.review_count), reverse=True)

    def confirm_appointment(self, appointment_id: str) -> PatientAppointment:
        if appointment_id not in self.appointments:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment = self.appointments[appointment_id]
        appointment.status = AppointmentStatus.CONFIRMED
        appointment.updated_at = datetime.now()
        
        return appointment

    def cancel_appointment(self, appointment_id: str, reason: str = None) -> PatientAppointment:
        if appointment_id not in self.appointments:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment = self.appointments[appointment_id]
        appointment.status = AppointmentStatus.CANCELLED
        appointment.updated_at = datetime.now()
        
        if reason:
            appointment.notes = f"Cancelled: {reason}"
        
        return appointment

    def reschedule_appointment(self, appointment_id: str, new_time: datetime) -> PatientAppointment:
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

    def add_provider(self, provider_data: Dict[str, Any]) -> ProviderInfo:
        provider = ProviderInfo(
            id=str(uuid.uuid4()),
            name=provider_data["name"],
            specialty=ProviderSpecialty(provider_data["specialty"]),
            credentials=provider_data["credentials"],
            languages=provider_data.get("languages", ["English"]),
            accepts_telemedicine=provider_data.get("accepts_telemedicine", True),
            accepts_new_patients=provider_data.get("accepts_new_patients", True),
            rating=provider_data.get("rating"),
            review_count=provider_data.get("review_count", 0),
            location=provider_data["location"],
            timezone=provider_data.get("timezone", "UTC"),
            metadata=provider_data.get("metadata", {})
        )
        
        self.providers[provider.id] = provider
        return provider

    def set_provider_availability(self, provider_id: str, availability: List[Dict]) -> List[ProviderAvailability]:
        provider_availabilities = []
        
        for avail_data in availability:
            avail = ProviderAvailability(
                id=str(uuid.uuid4()),
                provider_id=provider_id,
                specialty=ProviderSpecialty(avail_data["specialty"]),
                day_of_week=avail_data["day_of_week"],
                start_time=time.fromisoformat(avail_data["start_time"]),
                end_time=time.fromisoformat(avail_data["end_time"]),
                timezone=avail_data["timezone"],
                is_available=avail_data.get("is_available", True),
                max_appointments_per_day=avail_data.get("max_appointments_per_day", 10),
                appointment_duration_minutes=avail_data.get("appointment_duration_minutes", 30),
                break_duration_minutes=avail_data.get("break_duration_minutes", 0),
                accepts_telemedicine=avail_data.get("accepts_telemedicine", True),
                accepts_new_patients=avail_data.get("accepts_new_patients", True),
                metadata=avail_data.get("metadata", {})
            )
            provider_availabilities.append(avail)
        
        self.provider_availability[provider_id] = provider_availabilities
        return provider_availabilities

    def get_patient_appointments(self, patient_id: str, status: AppointmentStatus = None) -> List[PatientAppointment]:
        appointments = [appt for appt in self.appointments.values() if appt.patient_id == patient_id]
        
        if status:
            appointments = [appt for appt in appointments if appt.status == status]
        
        return sorted(appointments, key=lambda x: x.scheduled_time)

    def get_provider_appointments(self, provider_id: str, date: datetime.date = None) -> List[PatientAppointment]:
        appointments = [appt for appt in self.appointments.values() if appt.provider_id == provider_id]
        
        if date:
            appointments = [appt for appt in appointments if appt.scheduled_time.date() == date]
        
        return sorted(appointments, key=lambda x: x.scheduled_time)

    def get_upcoming_appointments(self, patient_id: str, days: int = 30) -> List[PatientAppointment]:
        cutoff_date = datetime.now() + timedelta(days=days)
        appointments = [appt for appt in self.appointments.values() 
                       if appt.patient_id == patient_id and 
                       appt.scheduled_time > datetime.now() and
                       appt.scheduled_time <= cutoff_date and
                       appt.status not in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]]
        
        return sorted(appointments, key=lambda x: x.scheduled_time)

    def get_appointment_statistics(self, patient_id: str = None) -> Dict[str, Any]:
        appointments = self.appointments.values()
        if patient_id:
            appointments = [appt for appt in appointments if appt.patient_id == patient_id]
        
        total_appointments = len(appointments)
        confirmed_appointments = len([a for a in appointments if a.status == AppointmentStatus.CONFIRMED])
        completed_appointments = len([a for a in appointments if a.status == AppointmentStatus.COMPLETED])
        cancelled_appointments = len([a for a in appointments if a.status == AppointmentStatus.CANCELLED])
        
        return {
            "total_appointments": total_appointments,
            "confirmed_appointments": confirmed_appointments,
            "completed_appointments": completed_appointments,
            "cancelled_appointments": cancelled_appointments,
            "completion_rate": (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
        }

appointment_booking_service = AppointmentBookingService()

@app.post("/appointments")
async def create_appointment(appointment_data: Dict[str, Any]):
    try:
        appointment = appointment_booking_service.create_appointment(
            patient_id=appointment_data["patient_id"],
            provider_id=appointment_data["provider_id"],
            appointment_type=AppointmentType(appointment_data["appointment_type"]),
            scheduled_time=datetime.fromisoformat(appointment_data["scheduled_time"]),
            duration_minutes=appointment_data["duration_minutes"],
            timezone=appointment_data["timezone"],
            booking_method=BookingMethod(appointment_data["booking_method"]),
            reason=appointment_data.get("reason"),
            symptoms=appointment_data.get("symptoms"),
            urgency_level=appointment_data.get("urgency_level", "normal"),
            is_telemedicine=appointment_data.get("is_telemedicine", False),
            location=appointment_data.get("location")
        )
        return {"appointment": appointment}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/providers/search")
async def search_providers(specialty: ProviderSpecialty = None, location: str = None,
                          accepts_telemedicine: bool = None, accepts_new_patients: bool = None,
                          date: str = None, timezone: str = "UTC"):
    try:
        search_date = datetime.fromisoformat(date).date() if date else None
        providers = appointment_booking_service.search_providers(
            specialty=specialty,
            location=location,
            accepts_telemedicine=accepts_telemedicine,
            accepts_new_patients=accepts_new_patients,
            date=search_date,
            timezone=timezone
        )
        return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/providers/{provider_id}/slots")
async def get_available_slots(provider_id: str, date: str, duration_minutes: int = 30, timezone: str = "UTC"):
    try:
        slot_date = datetime.fromisoformat(date).date()
        slots = appointment_booking_service.get_available_slots(provider_id, slot_date, duration_minutes, timezone)
        return {"slots": slots}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/appointments/{appointment_id}/confirm")
async def confirm_appointment(appointment_id: str):
    try:
        appointment = appointment_booking_service.confirm_appointment(appointment_id)
        return {"appointment": appointment}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: str, reason: str = None):
    try:
        appointment = appointment_booking_service.cancel_appointment(appointment_id, reason)
        return {"appointment": appointment}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/appointments/{appointment_id}/reschedule")
async def reschedule_appointment(appointment_id: str, new_time: str):
    try:
        new_datetime = datetime.fromisoformat(new_time)
        appointment = appointment_booking_service.reschedule_appointment(appointment_id, new_datetime)
        return {"appointment": appointment}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/providers")
async def add_provider(provider_data: Dict[str, Any]):
    try:
        provider = appointment_booking_service.add_provider(provider_data)
        return {"provider": provider}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/providers/{provider_id}/availability")
async def set_provider_availability(provider_id: str, availability_data: List[Dict[str, Any]]):
    try:
        availability = appointment_booking_service.set_provider_availability(provider_id, availability_data)
        return {"availability": availability}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/appointments")
async def get_patient_appointments(patient_id: str, status: AppointmentStatus = None):
    appointments = appointment_booking_service.get_patient_appointments(patient_id, status)
    return {"appointments": appointments}

@app.get("/providers/{provider_id}/appointments")
async def get_provider_appointments(provider_id: str, date: str = None):
    try:
        if date:
            appointment_date = datetime.fromisoformat(date).date()
            appointments = appointment_booking_service.get_provider_appointments(provider_id, appointment_date)
        else:
            appointments = appointment_booking_service.get_provider_appointments(provider_id)
        
        return {"appointments": appointments}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/appointments/upcoming")
async def get_upcoming_appointments(patient_id: str, days: int = 30):
    appointments = appointment_booking_service.get_upcoming_appointments(patient_id, days)
    return {"appointments": appointments}

@app.get("/appointments/{appointment_id}")
async def get_appointment(appointment_id: str):
    appointment = appointment_booking_service.appointments.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"appointment": appointment}

@app.get("/appointments/statistics")
async def get_appointment_statistics(patient_id: str = None):
    stats = appointment_booking_service.get_appointment_statistics(patient_id)
    return {"statistics": stats} 