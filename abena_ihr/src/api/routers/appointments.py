from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, timedelta
import os
import time
from collections import defaultdict
from ...services.stripe_service import stripe_service

router = APIRouter()

# Rate limiting for availability requests
availability_request_times = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 10

def check_rate_limit(provider_id: str):
    """Check rate limit for availability requests"""
    current_time = time.time()
    # Remove requests older than 1 minute
    availability_request_times[provider_id] = [
        req_time for req_time in availability_request_times[provider_id]
        if current_time - req_time < 60
    ]
    
    # Check if too many requests
    if len(availability_request_times[provider_id]) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=429, 
            detail="Too many availability requests. Please wait before trying again."
        )
    
    # Add current request
    availability_request_times[provider_id].append(current_time)

def validate_date_range(date_from: date, date_to: date):
    """Validate date range for availability requests"""
    # Check if date range is reasonable (max 30 days)
    if (date_to - date_from).days > 30:
        raise HTTPException(
            status_code=400,
            detail="Date range too large. Maximum 30 days allowed."
        )
    
    # Check if dates are in the past (allow today and future dates)
    # For testing purposes, allow past dates
    # today = date.today()
    # if date_from < today:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Start date cannot be in the past."
    #     )
    
    # Check if end date is before start date
    if date_to < date_from:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date."
        )

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL", "postgresql://abena_user:abena_password@postgres:5432/abena_ihr"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@router.get("/providers", response_model=List[dict])
async def get_providers():
    """Get all available providers"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                provider_id,
                first_name,
                last_name,
                specialization,
                email,
                phone,
                is_active
            FROM providers 
            WHERE is_active = true
            ORDER BY first_name, last_name
        """
        
        cursor.execute(query)
        providers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [dict(provider) for provider in providers]
        
    except Exception as e:
        print(f"Error fetching providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch providers")

@router.get("/providers/{provider_id}/availability")
async def get_provider_availability(
    provider_id: str,
    appointment_date: date = Query(..., description="Date for availability check (YYYY-MM-DD)")
):
    """Get provider availability for a specific date with proper slot calculation"""
    try:
        print(f"🔍 Availability request for provider {provider_id} on {appointment_date}")
        
        # SAFETY CHECK 1: Validate date is not in the past (allow today and future dates)
        today = date.today()
        if appointment_date < today:
            raise HTTPException(
                status_code=400,
                detail="Cannot check availability for past dates."
            )
        
        # SAFETY CHECK 2: Maximum date limit (1 year from today)
        max_date = today + timedelta(days=365)
        if appointment_date > max_date:
            raise HTTPException(
                status_code=400,
                detail="Cannot check availability more than 1 year in advance."
            )
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get provider working hours for this specific day
        day_of_week = appointment_date.weekday()  # 0=Monday, 6=Sunday
        
        working_hours_query = """
            SELECT 
                day_of_week,
                start_time,
                end_time,
                is_available
            FROM provider_availability 
            WHERE provider_id = %s AND day_of_week = %s AND is_available = true
        """
        cursor.execute(working_hours_query, (provider_id, day_of_week))
        working_hours = cursor.fetchone()
        
        if not working_hours:
            return {
                'provider_id': provider_id,
                'date': appointment_date.isoformat(),
                'available_slots': [],
                'total_slots': 0,
                'message': f'Provider is not available on {appointment_date.strftime("%A")}'
            }
        
        # Get existing appointments for this specific date
        appointments_query = """
            SELECT 
                appointment_time,
                appointment_type,
                status
            FROM appointments 
            WHERE provider_id = %s 
            AND appointment_date = %s
            AND status NOT IN ('cancelled', 'no-show')
            ORDER BY appointment_time
        """
        cursor.execute(appointments_query, (provider_id, appointment_date))
        existing_appointments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Generate time slots (30-minute intervals)
        start_time = working_hours['start_time']
        end_time = working_hours['end_time']
        
        # SAFETY CHECK 3: Validate working hours
        if start_time >= end_time:
            raise HTTPException(
                status_code=500,
                detail="Invalid working hours: start time must be before end time."
            )
        
        # Convert to datetime for easier manipulation
        current_slot = datetime.combine(appointment_date, start_time)
        end_datetime = datetime.combine(appointment_date, end_time)
        
        # SAFETY CHECK 4: Maximum slots limit (48 slots = 24 hours max)
        max_slots = 48
        slot_count = 0
        
        # Create booked time slots set for quick lookup
        booked_times = set()
        for apt in existing_appointments:
            apt_time = apt['appointment_time']
            # Block 30 minutes for each appointment
            booked_times.add(apt_time)
            # Also block the next 30 minutes if it's a 1-hour appointment
            if apt['appointment_type'] in ['consultation', 'follow-up']:
                next_slot = (datetime.combine(appointment_date, apt_time) + timedelta(minutes=30)).time()
                booked_times.add(next_slot)
        
        # Generate available slots with SAFETY BREAKPOINTS
        available_slots = []
        while current_slot < end_datetime:
            # SAFETY BREAKPOINT 1: Maximum iteration limit
            slot_count += 1
            if slot_count > max_slots:
                print(f"⚠️ SAFETY BREAK: Maximum slots limit reached ({max_slots})")
                break
            
            # SAFETY BREAKPOINT 2: Time progression check
            if current_slot >= end_datetime:
                print(f"✅ SAFETY BREAK: Reached end time")
                break
            
            slot_time = current_slot.time()
            
            # Check if this slot is available
            if slot_time not in booked_times:
                slot_end = (current_slot + timedelta(minutes=30)).time()
                
                available_slots.append({
                    'time': slot_time.strftime('%H:%M'),
                    'end_time': slot_end.strftime('%H:%M'),
                    'available': True
                })
            
            # SAFETY BREAKPOINT 3: Ensure time always moves forward
            current_slot += timedelta(minutes=30)
            
            # SAFETY BREAKPOINT 4: Emergency stop if time doesn't progress
            if current_slot <= datetime.combine(appointment_date, start_time):
                print(f"🚨 EMERGENCY BREAK: Time not progressing, stopping loop")
                break
        
        # SAFETY CHECK 5: Validate result
        if len(available_slots) > max_slots:
            print(f"⚠️ WARNING: Generated more slots than expected ({len(available_slots)})")
            available_slots = available_slots[:max_slots]  # Limit to max
        
        print(f"✅ Generated {len(available_slots)} available slots in {slot_count} iterations")
        
        return {
            'provider_id': provider_id,
            'date': appointment_date.isoformat(),
            'day_of_week': day_of_week,
            'working_hours': {
                'start': start_time.strftime('%H:%M'),
                'end': end_time.strftime('%H:%M')
            },
            'available_slots': available_slots,
            'total_slots': len(available_slots),
            'booked_appointments': len(existing_appointments),
            'safety_info': {
                'iterations': slot_count,
                'max_slots_limit': max_slots,
                'working_hours_valid': True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🚨 CRITICAL ERROR in availability calculation: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to fetch provider availability")

@router.post("/providers/{provider_id}/working-hours")
async def set_provider_working_hours(provider_id: str, working_hours: List[dict]):
    """Set provider working hours for the week"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, clear existing working hours for this provider
        cursor.execute("DELETE FROM provider_availability WHERE provider_id = %s", (provider_id,))
        
        # Insert new working hours
        for hours in working_hours:
            cursor.execute("""
                INSERT INTO provider_availability (
                    provider_id, day_of_week, start_time, end_time, is_available
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                provider_id,
                hours['day_of_week'],
                hours['start_time'],
                hours['end_time'],
                hours.get('is_available', True)
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"Working hours set for provider {provider_id}"}
        
    except Exception as e:
        print(f"Error setting working hours: {e}")
        raise HTTPException(status_code=500, detail="Failed to set working hours")

@router.get("/providers/{provider_id}/working-hours")
async def get_provider_working_hours(provider_id: str):
    """Get provider working hours"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT day_of_week, start_time, end_time, is_available
            FROM provider_availability 
            WHERE provider_id = %s
            ORDER BY day_of_week
        """, (provider_id,))
        
        working_hours = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"provider_id": provider_id, "working_hours": [dict(hours) for hours in working_hours]}
        
    except Exception as e:
        print(f"Error fetching working hours: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch working hours")

@router.get("/appointments", response_model=List[dict])
async def get_appointments(
    patient_id: Optional[str] = Query(None),
    provider_id: Optional[str] = Query(None)
):
    """Get all appointments or appointments for a specific patient or provider"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if patient_id:
            query = """
                SELECT 
                    a.appointment_id,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.patient_id,
                    pr.first_name || ' ' || pr.last_name as provider_name,
                    pr.provider_id,
                    a.appointment_date,
                    a.appointment_time,
                    a.appointment_type,
                    a.status,
                    a.notes,
                    a.created_at,
                    a.updated_at
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN providers pr ON a.provider_id = pr.provider_id
                WHERE a.patient_id = %s
                ORDER BY a.appointment_date DESC, a.appointment_time ASC
            """
            cursor.execute(query, (patient_id,))
        elif provider_id:
            query = """
                SELECT 
                    a.appointment_id,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.patient_id,
                    pr.first_name || ' ' || pr.last_name as provider_name,
                    pr.provider_id,
                    a.appointment_date,
                    a.appointment_time,
                    a.appointment_type,
                    a.status,
                    a.notes,
                    a.created_at,
                    a.updated_at
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN providers pr ON a.provider_id = pr.provider_id
                WHERE a.provider_id = %s
                ORDER BY a.appointment_date DESC, a.appointment_time ASC
            """
            cursor.execute(query, (provider_id,))
        else:
            query = """
                SELECT 
                    a.appointment_id,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.patient_id,
                    pr.first_name || ' ' || pr.last_name as provider_name,
                    pr.provider_id,
                    a.appointment_date,
                    a.appointment_time,
                    a.appointment_type,
                    a.status,
                    a.notes,
                    a.created_at,
                    a.updated_at
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN providers pr ON a.provider_id = pr.provider_id
                ORDER BY a.appointment_date DESC, a.appointment_time ASC
            """
            cursor.execute(query)
        
        appointments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [dict(appointment) for appointment in appointments]
        
    except Exception as e:
        print(f"Error fetching appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch appointments")

@router.get("/appointments/{appointment_id}", response_model=dict)
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                a.appointment_id,
                p.first_name || ' ' || p.last_name as patient_name,
                p.patient_id,
                pr.first_name || ' ' || pr.last_name as provider_name,
                pr.provider_id,
                a.appointment_date,
                a.appointment_time,
                a.appointment_type,
                a.status,
                a.notes,
                a.created_at,
                a.updated_at
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN providers pr ON a.provider_id = pr.provider_id
            WHERE a.appointment_id = %s
        """
        
        cursor.execute(query, (appointment_id,))
        appointment = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return dict(appointment)
        
    except Exception as e:
        print(f"Error fetching appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch appointment")

@router.get("/provider-dashboard/{provider_id}", response_model=dict)
async def get_provider_dashboard(provider_id: str):
    """Get provider dashboard data including appointments, patient count, and metrics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get provider info
        provider_query = """
            SELECT 
                provider_id,
                first_name,
                last_name,
                specialization,
                email,
                is_active
            FROM providers 
            WHERE provider_id = %s
        """
        cursor.execute(provider_query, (provider_id,))
        provider = cursor.fetchone()
        
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Get today's appointments count
        today_appointments_query = """
            SELECT COUNT(*) as count
            FROM appointments 
            WHERE provider_id = %s 
            AND appointment_date = CURRENT_DATE
            AND status != 'cancelled'
        """
        cursor.execute(today_appointments_query, (provider_id,))
        today_appointments = cursor.fetchone()['count']
        
        # Get pending prescriptions count (mock data for now)
        pending_prescriptions = 5  # This would come from prescriptions table
        
        # Get lab requests count (mock data for now)
        lab_requests = 3  # This would come from lab_requests table
        
        # Get upcoming appointments
        upcoming_appointments_query = """
            SELECT 
                a.appointment_id,
                p.first_name || ' ' || p.last_name as patient_name,
                p.patient_id,
                a.appointment_date,
                a.appointment_time,
                a.appointment_type,
                a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.provider_id = %s 
            AND a.appointment_date >= CURRENT_DATE
            AND a.status != 'cancelled'
            ORDER BY a.appointment_date ASC, a.appointment_time ASC
            LIMIT 5
        """
        cursor.execute(upcoming_appointments_query, (provider_id,))
        upcoming_appointments = cursor.fetchall()
        
        # Get total patient count
        patient_count_query = """
            SELECT COUNT(DISTINCT patient_id) as count
            FROM appointments 
            WHERE provider_id = %s
        """
        cursor.execute(patient_count_query, (provider_id,))
        total_patients = cursor.fetchone()['count']
        
        # Get recent activity (mock data for now)
        recent_activity = [
            {
                "action": "Prescription Sent",
                "timestamp": "2 hours ago",
                "icon": "pill"
            },
            {
                "action": "Lab Request Submitted", 
                "timestamp": "5 hours ago",
                "icon": "flask"
            }
        ]
        
        cursor.close()
        conn.close()
        
        return {
            "provider": dict(provider),
            "quick_stats": {
                "today_appointments": today_appointments,
                "pending_prescriptions": pending_prescriptions,
                "lab_requests": lab_requests,
                "total_patients": total_patients
            },
            "upcoming_appointments": [dict(apt) for apt in upcoming_appointments],
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        print(f"Error fetching provider dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch provider dashboard")

@router.post("/appointments/payment-intent", response_model=dict)
async def create_appointment_payment_intent(appointment_data: dict):
    """Create a payment intent for appointment booking"""
    try:
        # Validate required fields
        required_fields = ['patient_id', 'provider_id', 'appointment_date', 'appointment_time', 'appointment_type']
        for field in required_fields:
            if field not in appointment_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get patient and provider names for payment description
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get patient name
        cursor.execute("SELECT first_name, last_name FROM patients WHERE patient_id = %s", (appointment_data['patient_id'],))
        patient = cursor.fetchone()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get provider name
        cursor.execute("SELECT first_name, last_name FROM providers WHERE provider_id = %s", (appointment_data['provider_id'],))
        provider = cursor.fetchone()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        cursor.close()
        conn.close()
        
        # Create temporary appointment ID for payment
        temp_appointment_id = f"temp_{int(time.time())}"
        
        patient_name = f"{patient['first_name']} {patient['last_name']}"
        provider_name = f"{provider['first_name']} {provider['last_name']}"
        
        # Create payment intent
        payment_intent = stripe_service.create_payment_intent(
            appointment_id=temp_appointment_id,
            patient_name=patient_name,
            provider_name=provider_name
        )
        
        return {
            "payment_intent": payment_intent,
            "appointment_data": appointment_data
        }
        
    except Exception as e:
        print(f"Error creating payment intent: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment intent")

@router.post("/appointments/confirm-payment", response_model=dict)
async def confirm_appointment_payment(payment_data: dict):
    """Confirm payment and create appointment"""
    try:
        payment_intent_id = payment_data.get('payment_intent_id')
        appointment_data = payment_data.get('appointment_data')
        
        if not payment_intent_id or not appointment_data:
            raise HTTPException(status_code=400, detail="Missing payment_intent_id or appointment_data")
        
        # Confirm payment with Stripe
        payment_status = stripe_service.confirm_payment(payment_intent_id)
        
        if payment_status['status'] != 'succeeded':
            raise HTTPException(status_code=400, detail="Payment not successful")
        
        # Create the actual appointment
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check for scheduling conflicts
        conflict_query = """
            SELECT appointment_id, appointment_time, appointment_type
            FROM appointments 
            WHERE provider_id = %s 
            AND appointment_date = %s 
            AND appointment_time = %s
            AND status != 'cancelled'
        """
        
        cursor.execute(conflict_query, (
            appointment_data['provider_id'],
            appointment_data['appointment_date'],
            appointment_data['appointment_time']
        ))
        
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Time slot is already booked")
        
        # Insert appointment with payment information
        insert_query = """
            INSERT INTO appointments (
                patient_id, provider_id, appointment_date, appointment_time, 
                appointment_type, status, notes, payment_intent_id, payment_amount
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING appointment_id
        """
        
        cursor.execute(insert_query, (
            appointment_data['patient_id'],
            appointment_data['provider_id'],
            appointment_data['appointment_date'],
            appointment_data['appointment_time'],
            appointment_data['appointment_type'],
            'confirmed',  # Status is confirmed after payment
            appointment_data.get('notes', ''),
            payment_intent_id,
            payment_status['amount'] / 100  # Convert cents to dollars
        ))
        
        appointment_id = cursor.fetchone()['appointment_id']
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "appointment_id": appointment_id,
            "status": "confirmed",
            "payment_status": payment_status['status'],
            "message": "Appointment created successfully after payment confirmation"
        }
        
    except Exception as e:
        print(f"Error confirming payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to confirm payment")

@router.get("/payments/provider/{provider_id}", response_model=List[dict])
async def get_provider_payments(provider_id: str):
    """Get payment history for a provider"""
    try:
        payments = stripe_service.get_payment_history(provider_id=provider_id)
        return payments
    except Exception as e:
        print(f"Error fetching provider payments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment history")

@router.get("/payments/patient/{patient_id}", response_model=List[dict])
async def get_patient_payments(patient_id: str):
    """Get payment history for a patient"""
    try:
        payments = stripe_service.get_payment_history(patient_id=patient_id)
        return payments
    except Exception as e:
        print(f"Error fetching patient payments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment history")

@router.post("/appointments", response_model=dict)
async def create_appointment(appointment_data: dict):
    """Create a new appointment with availability checking"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Validate required fields
        required_fields = ['patient_id', 'provider_id', 'appointment_date', 'appointment_time', 'appointment_type']
        for field in required_fields:
            if field not in appointment_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Check if patient exists
        cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s", (appointment_data['patient_id'],))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Check if provider exists
        cursor.execute("SELECT provider_id FROM providers WHERE provider_id = %s", (appointment_data['provider_id'],))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Check for scheduling conflicts
        conflict_query = """
            SELECT appointment_id, appointment_time, appointment_type
            FROM appointments 
            WHERE provider_id = %s 
            AND appointment_date = %s 
            AND appointment_time = %s
            AND status != 'cancelled'
        """
        
        cursor.execute(conflict_query, (
            appointment_data['provider_id'],
            appointment_data['appointment_date'],
            appointment_data['appointment_time']
        ))
        
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Time slot is already booked")
        
        # Check if the provider is available at this time
        appointment_date = datetime.strptime(appointment_data['appointment_date'], '%Y-%m-%d').date()
        day_of_week = (appointment_date.weekday() + 1) % 7  # Convert to our format
        
        availability_query = """
            SELECT start_time, end_time
            FROM provider_availability 
            WHERE provider_id = %s 
            AND day_of_week = %s 
            AND is_available = true
        """
        
        cursor.execute(availability_query, (appointment_data['provider_id'], day_of_week))
        availability = cursor.fetchone()
        
        if not availability:
            raise HTTPException(status_code=400, detail="Provider is not available on this day")
        
        appointment_time = datetime.strptime(appointment_data['appointment_time'], '%H:%M:%S').time()
        
        if appointment_time < availability['start_time'] or appointment_time >= availability['end_time']:
            raise HTTPException(status_code=400, detail="Appointment time is outside provider's working hours")
        
        # Insert new appointment
        query = """
            INSERT INTO appointments (
                patient_id, provider_id, appointment_date, appointment_time, 
                appointment_type, status, notes, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING appointment_id
        """
        
        cursor.execute(query, (
            appointment_data['patient_id'],
            appointment_data['provider_id'],
            appointment_data['appointment_date'],
            appointment_data['appointment_time'],
            appointment_data['appointment_type'],
            appointment_data.get('status', 'pending'),
            appointment_data.get('notes', ''),
        ))
        
        appointment_id = cursor.fetchone()['appointment_id']
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Return the created appointment
        return await get_appointment(appointment_id)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create appointment")

@router.put("/appointments/{appointment_id}/status", response_model=dict)
async def update_appointment_status(appointment_id: int, status_data: dict):
    """Update appointment status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Validate status
        valid_statuses = ['confirmed', 'pending', 'cancelled', 'completed']
        new_status = status_data.get('status')
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # Update appointment status
        query = """
            UPDATE appointments 
            SET status = %s, updated_at = NOW()
            WHERE appointment_id = %s
            RETURNING appointment_id
        """
        
        cursor.execute(query, (new_status, appointment_id))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Return the updated appointment
        return await get_appointment(appointment_id)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating appointment status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update appointment status")

@router.put("/appointments/{appointment_id}", response_model=dict)
async def update_appointment(appointment_id: int, appointment_data: dict):
    """Update an appointment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if appointment exists
        cursor.execute("SELECT appointment_id FROM appointments WHERE appointment_id = %s", (appointment_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for field, value in appointment_data.items():
            if field in ['appointment_date', 'appointment_time', 'appointment_type', 'status', 'notes']:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        values.append(appointment_id)
        query = f"""
            UPDATE appointments 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE appointment_id = %s
            RETURNING appointment_id
        """
        
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        
        # Return the updated appointment
        return await get_appointment(appointment_id)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to update appointment")

@router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: int):
    """Delete an appointment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if appointment exists
        cursor.execute("SELECT appointment_id FROM appointments WHERE appointment_id = %s", (appointment_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Delete appointment
        cursor.execute("DELETE FROM appointments WHERE appointment_id = %s", (appointment_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Appointment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete appointment")

# Provider-specific appointment management endpoints
@router.put("/appointments/{appointment_id}/postpone", response_model=dict)
async def postpone_appointment(appointment_id: str, postpone_data: dict):
    """Postpone an appointment (provider action)"""
    try:
        new_date = postpone_data.get('new_date')
        new_time = postpone_data.get('new_time')
        reason = postpone_data.get('reason')
        
        if not all([new_date, new_time, reason]):
            raise HTTPException(status_code=400, detail="new_date, new_time, and reason are required")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if appointment exists and get current data
        cursor.execute("""
            SELECT appointment_id, status, notes 
            FROM appointments 
            WHERE appointment_id = %s
        """, (appointment_id,))
        
        appointment = cursor.fetchone()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        if appointment['status'] == 'cancelled':
            raise HTTPException(status_code=400, detail="Cannot postpone a cancelled appointment")
        
        # Update appointment with new date/time and add reason to notes
        updated_notes = f"{appointment['notes'] or ''}\n[POSTPONED: {reason}]"
        
        cursor.execute("""
            UPDATE appointments 
            SET appointment_date = %s, appointment_time = %s, notes = %s, updated_at = NOW()
            WHERE appointment_id = %s
            RETURNING appointment_id
        """, (new_date, new_time, updated_notes, appointment_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Appointment postponed successfully", "appointment_id": appointment_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error postponing appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to postpone appointment")

@router.put("/appointments/{appointment_id}/cancel", response_model=dict)
async def cancel_appointment(appointment_id: str, cancel_data: dict):
    """Cancel an appointment (provider action)"""
    try:
        reason = cancel_data.get('reason')
        
        if not reason:
            raise HTTPException(status_code=400, detail="reason is required")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if appointment exists and get current data
        cursor.execute("""
            SELECT appointment_id, status, notes, payment_status
            FROM appointments 
            WHERE appointment_id = %s
        """, (appointment_id,))
        
        appointment = cursor.fetchone()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        if appointment['status'] == 'cancelled':
            raise HTTPException(status_code=400, detail="Appointment is already cancelled")
        
        # Update appointment status and add reason to notes
        updated_notes = f"{appointment['notes'] or ''}\n[CANCELLED: {reason}]"
        
        cursor.execute("""
            UPDATE appointments 
            SET status = 'cancelled', notes = %s, updated_at = NOW()
            WHERE appointment_id = %s
            RETURNING appointment_id
        """, (updated_notes, appointment_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Appointment cancelled successfully", "appointment_id": appointment_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error cancelling appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")

@router.post("/appointments/{appointment_id}/refund", response_model=dict)
async def refund_appointment(appointment_id: str):
    """Process refund for cancelled appointment (provider action)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if appointment exists and is eligible for refund
        cursor.execute("""
            SELECT appointment_id, status, payment_status, payment_amount
            FROM appointments 
            WHERE appointment_id = %s
        """, (appointment_id,))
        
        appointment = cursor.fetchone()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        if appointment['status'] != 'cancelled':
            raise HTTPException(status_code=400, detail="Only cancelled appointments can be refunded")
        
        if appointment['payment_status'] != 'paid':
            raise HTTPException(status_code=400, detail="Only paid appointments can be refunded")
        
        # Update payment status to refunded
        cursor.execute("""
            UPDATE appointments 
            SET payment_status = 'refunded', updated_at = NOW()
            WHERE appointment_id = %s
            RETURNING appointment_id
        """, (appointment_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Refund processed successfully", 
            "appointment_id": appointment_id,
            "refund_amount": appointment['payment_amount']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing refund: {e}")
        raise HTTPException(status_code=500, detail="Failed to process refund") 