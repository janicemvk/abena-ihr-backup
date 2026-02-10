"""
Abena IHR Clinical Outcomes Management System
Main API Application

This module provides the main FastAPI application for the Abena IHR system,
including clinical outcomes management, patient data, and predictive analytics.
"""

import os
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Query, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from .routers import patients, outcomes, predictions, appointments
from src.predictive_analytics.predictive_engine import prediction_router

# Configure logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security Integration
try:
    from src.security_integration import (
        setup_security, 
        secure_login, 
        get_current_user_secure,
        JWTAuth,
        require_role,
        UserRole,
        LoginRequest,
        LoginResponse
    )
    SECURITY_ENABLED = True
    logger.info("✅ Security modules loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Security modules not available: {e}")
    SECURITY_ENABLED = False

# Create FastAPI app
app = FastAPI(
    title="Abena IHR Clinical Outcomes Management System",
    description="Advanced healthcare intelligence platform for clinical outcomes management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Database connection
def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL", "postgresql://abena_user:abena_password@postgres:5432/abena_ihr"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Test database connection
try:
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT NOW()")
        result = cur.fetchone()
        logger.info(f"✅ Database connected successfully: {result}")
    conn.close()
except Exception as e:
    logger.error(f"❌ Database connection test failed: {e}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:4005",  # eCDome Intelligence
        "http://localhost:4006",  # Gamification
        "http://localhost:4007",  # Unified Integration
        "http://localhost:4008",  # Provider Dashboard
        "http://localhost:4009",  # Patient Dashboard
        "http://localhost:4011",  # Data Ingestion
        "http://localhost:4012",  # Biomarker GUI
        "http://localhost:8000",  # Telemedicine Platform
        "http://localhost:8080",  # API Gateway
        "http://138.68.24.154:4005",  # Live eCDome Intelligence System
        "http://138.68.24.154:4006",  # Live Gamification
        "http://138.68.24.154:4007",  # Live Unified Integration
        "http://138.68.24.154:4008",  # Live Provider Dashboard
        "http://138.68.24.154:4009",  # Live Patient Dashboard
        "http://138.68.24.154:4011",  # Live Data Ingestion
        "http://138.68.24.154:4012",  # Live Biomarker GUI
        "http://138.68.24.154:8000",  # Live Telemedicine Platform
        "http://138.68.24.154:8080",  # Live API Gateway
        "https://abena-ihr.com",  # Production domain
        "https://www.abena-ihr.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Enable security middleware if available
if SECURITY_ENABLED:
    app = setup_security(app)
    logger.info("✅ Security middleware enabled (rate limiting, JWT auth)")

# Include routers
app.include_router(patients.router, prefix="/api/v1", tags=["patients"])
app.include_router(outcomes.router, prefix="/api/v1", tags=["outcomes"])
app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
app.include_router(prediction_router, prefix="/api/v1", tags=["predictive-analytics"])
app.include_router(appointments.router, prefix="/api/v1", tags=["appointments"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM patients")
            patient_count = cur.fetchone()['count']
        conn.close()
        
        return {
            "status": "healthy",
            "service": "Abena IHR Clinical Outcomes Management System",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "patient_count": patient_count,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "service": "Abena IHR Clinical Outcomes Management System",
                "timestamp": datetime.now().isoformat(),
                "database": "disconnected",
                "error": str(e)
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Abena IHR Clinical Outcomes Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Helper functions for secure login
async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email from database"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    email,
                    password,
                    hashed_password,
                    first_name,
                    last_name,
                    role
                FROM users 
                WHERE email = %s
            """, (email,))
            user = cur.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None

async def get_user_data(user_id: int, role: str) -> Dict[str, Any]:
    """Get additional user data based on role"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if role == 'provider':
                cur.execute("""
                    SELECT provider_id, specialization, department, npi_number
                    FROM providers 
                    WHERE email = (SELECT email FROM users WHERE id = %s)
                    AND is_active = true
                """, (user_id,))
                data = cur.fetchone()
                return dict(data) if data else {}
            elif role == 'patient':
                cur.execute("""
                    SELECT patient_id, medical_record_number, date_of_birth, gender
                    FROM patients 
                    WHERE email = (SELECT email FROM users WHERE id = %s)
                    AND is_active = true
                """, (user_id,))
                data = cur.fetchone()
                return dict(data) if data else {}
        conn.close()
        return {}
    except Exception as e:
        logger.error(f"Error fetching user data: {e}")
        return {}

# Authentication endpoints - SECURE WITH BCRYPT & JWT
@app.post("/api/v1/auth/login")
async def login(credentials: Dict[str, str]):
    """Secure authentication endpoint with bcrypt password verification and JWT tokens"""
    if SECURITY_ENABLED:
        # Use secure login with bcrypt and JWT
        try:
            login_request = LoginRequest(
                email=credentials.get('email', '').strip(),
                password=credentials.get('password', '').strip()
            )
            result = await secure_login(
                email=login_request.email,
                password=login_request.password,
                get_user_by_email_func=get_user_by_email,
                get_user_data_func=get_user_data
            )
            
            # Get additional user info for backward compatibility
            user = await get_user_by_email(login_request.email)
            user_data = await get_user_data(int(result.user_id), result.role)
            
            # Format response to match existing frontend expectations
            user_name = f"{user['first_name']} {user['last_name']}" if user else ""
            if result.role == 'provider' and not user_name.startswith('Dr.'):
                user_name = f"Dr. {user_name}"
            
            return {
                "success": True,
                "token": result.access_token,
                "access_token": result.access_token,  # Also include for compatibility
                "token_type": result.token_type,
                "userId": result.user_id,
                "userName": user_name,
                "userType": result.role,
                "userRole": result.role,
                "expiresAt": datetime.now().isoformat(),
                "message": "Login successful"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Secure authentication error: {e}")
            raise HTTPException(status_code=500, detail="Authentication failed")
    else:
        # Fallback to old login (not recommended for production)
        logger.warning("⚠️ Using insecure login - security modules not available")
        try:
            email = credentials.get('email', '').strip()
            password = credentials.get('password', '').strip()
            
            if not email or not password:
                raise HTTPException(status_code=400, detail="Email and password are required")
            
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, email, password, hashed_password, first_name, last_name, role
                    FROM users WHERE email = %s
                """, (email,))
                user = cur.fetchone()
                
                if not user:
                    raise HTTPException(status_code=401, detail="Invalid credentials")
                
                # Check hashed_password first, then fallback to password
                if user.get('hashed_password'):
                    # Try bcrypt verification
                    try:
                        import bcrypt
                        if not bcrypt.checkpw(password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
                            raise HTTPException(status_code=401, detail="Invalid password")
                    except:
                        raise HTTPException(status_code=401, detail="Invalid password")
                elif password != user.get('password'):
                    raise HTTPException(status_code=401, detail="Invalid password")
            
            conn.close()
            
            token = f"token_{user['id']}_{int(datetime.now().timestamp())}"
            return {
                "success": True,
                "token": token,
                "userId": str(user['id']),
                "userName": f"{user['first_name']} {user['last_name']}",
                "userType": user['role'],
                "userRole": user['role'],
                "expiresAt": datetime.now().isoformat(),
                "message": "Login successful"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=500, detail="Authentication failed")

# Doctors endpoint - NOW USING REAL DATABASE
@app.get("/api/v1/doctors")
async def get_doctors():
    """Get all doctors from database"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Query providers table for doctors
            cur.execute("""
                SELECT 
                    provider_id,
                    first_name,
                    last_name,
                    specialization as specialty,
                    email,
                    phone,
                    is_active,
                    created_at,
                    updated_at
                FROM providers 
                WHERE is_active = true
                ORDER BY last_name, first_name
            """)
            doctors = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Real doctor data loaded from database: {len(doctors)} doctors")
        return [dict(doctor) for doctor in doctors]
    except Exception as e:
        logger.error(f"❌ Database error fetching doctors: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch doctors from database")

# Appointments endpoint is now handled by the appointments router

# Prescriptions endpoints - NOW USING REAL DATABASE
@app.get("/api/v1/prescriptions")
async def get_prescriptions(patient_id: Optional[str] = None):
    """Get prescriptions with optional patient filter"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if patient_id:
                cur.execute("""
                    SELECT 
                        m.medication_id as id,
                        m.medication_name,
                        m.dosage,
                        m.frequency,
                        m.start_date as prescribed_date,
                        m.status,
                        p.first_name || ' ' || p.last_name as patient_name,
                        COALESCE(pr.first_name || ' ' || pr.last_name, m.prescribing_physician) as provider_name
                    FROM medications m
                    LEFT JOIN patients p ON m.patient_id = p.patient_id
                    LEFT JOIN providers pr ON m.prescribing_physician = pr.provider_id::text
                    WHERE m.patient_id = %s
                    ORDER BY m.start_date DESC
                """, (patient_id,))
            else:
                cur.execute("""
                    SELECT 
                        m.medication_id as id,
                        m.medication_name,
                        m.dosage,
                        m.frequency,
                        m.start_date as prescribed_date,
                        m.status,
                        p.first_name || ' ' || p.last_name as patient_name,
                        COALESCE(pr.first_name || ' ' || pr.last_name, m.prescribing_physician) as provider_name
                    FROM medications m
                    LEFT JOIN patients p ON m.patient_id = p.patient_id
                    LEFT JOIN providers pr ON m.prescribing_physician = pr.provider_id::text
                    ORDER BY m.start_date DESC
                """)
            
            prescriptions = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Retrieved {len(prescriptions)} prescriptions from database")
        return {
            "success": True,
            "prescriptions": [dict(prescription) for prescription in prescriptions]
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching prescriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch prescriptions")

@app.post("/api/v1/prescriptions")
async def create_prescription(prescription_data: Dict[str, Any]):
    """Create a new prescription"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO medications (
                    patient_id, 
                    medication_name, 
                    dosage, 
                    frequency, 
                    start_date,
                    prescribing_physician, 
                    status,
                    pharmacy_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING medication_id
            """, (
                prescription_data.get('patient_id'),
                prescription_data.get('medication_name'),
                prescription_data.get('dosage'),
                prescription_data.get('frequency'),
                prescription_data.get('start_date', datetime.now().date()),
                prescription_data.get('prescribing_physician'),
                prescription_data.get('status', 'active'),
                prescription_data.get('pharmacy_id')
            ))
            prescription_id = cur.fetchone()['medication_id']
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Prescription created in database: {prescription_id}")
        return {
            "success": True,
            "medication_id": prescription_id,
            "message": "Prescription created successfully"
        }
    except Exception as e:
        logger.error(f"❌ Database error creating prescription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create prescription")

# Provider-specific prescription endpoints
@app.get("/api/v1/prescriptions/provider/{provider_id}")
async def get_prescriptions_by_provider(provider_id: str):
    """Get all prescriptions written by a specific provider"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    m.medication_id as id,
                    m.medication_name,
                    m.dosage,
                    m.frequency,
                    m.start_date as prescribed_date,
                    m.end_date,
                    m.status,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.patient_id,
                    ph.pharmacy_name,
                    m.created_at
                FROM medications m
                LEFT JOIN patients p ON m.patient_id = p.patient_id
                LEFT JOIN pharmacies ph ON m.pharmacy_id = ph.id
                WHERE m.prescribing_physician = %s
                ORDER BY m.start_date DESC
            """, (provider_id,))
            
            prescriptions = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Retrieved {len(prescriptions)} prescriptions for provider {provider_id}")
        return {
            "success": True,
            "prescriptions": [dict(prescription) for prescription in prescriptions]
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching provider prescriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch provider prescriptions")

@app.put("/api/v1/prescriptions/{prescription_id}")
async def update_prescription(prescription_id: str, prescription_data: Dict[str, Any]):
    """Update an existing prescription"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE medications 
                SET 
                    medication_name = %s,
                    dosage = %s,
                    frequency = %s,
                    start_date = %s,
                    end_date = %s,
                    status = %s,
                    pharmacy_id = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE medication_id = %s
                RETURNING medication_id
            """, (
                prescription_data.get('medication_name'),
                prescription_data.get('dosage'),
                prescription_data.get('frequency'),
                prescription_data.get('start_date'),
                prescription_data.get('end_date'),
                prescription_data.get('status'),
                prescription_data.get('pharmacy_id'),
                prescription_id
            ))
            
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Prescription not found")
            
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Prescription updated successfully: {prescription_id}")
        return {
            "success": True,
            "medication_id": prescription_id,
            "message": "Prescription updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Database error updating prescription: {e}")
        raise HTTPException(status_code=500, detail="Failed to update prescription")

@app.delete("/api/v1/prescriptions/{prescription_id}")
async def delete_prescription(prescription_id: str):
    """Delete a prescription"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM medications 
                WHERE medication_id = %s
                RETURNING medication_id
            """, (prescription_id,))
            
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Prescription not found")
            
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Prescription deleted successfully: {prescription_id}")
        return {
            "success": True,
            "message": "Prescription deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Database error deleting prescription: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete prescription")

@app.get("/api/v1/pharmacies")
async def get_pharmacies():
    """Get all pharmacies for prescription assignment"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    pharmacy_name,
                    address,
                    phone,
                    email,
                    contact_person,
                    is_active
                FROM pharmacies 
                WHERE is_active = true
                ORDER BY pharmacy_name
            """)
            
            pharmacies = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Retrieved {len(pharmacies)} pharmacies from database")
        return {
            "success": True,
            "pharmacies": [dict(pharmacy) for pharmacy in pharmacies]
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching pharmacies: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pharmacies")

@app.get("/api/v1/providers/{provider_id}/patients")
async def get_provider_patients(provider_id: str):
    """Get all patients associated with a specific provider"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get patients who either:
            # 1. Have appointments with this provider
            # 2. Were directly added by this provider
            cur.execute("""
                SELECT DISTINCT
                    p.patient_id,
                    p.first_name,
                    p.last_name,
                    p.email,
                    p.phone,
                    p.date_of_birth,
                    p.gender,
                    p.address,
                    p.medical_record_number,
                    p.is_active,
                    p.created_at,
                    COALESCE(
                        (SELECT MAX(a.appointment_date) 
                         FROM appointments a 
                         WHERE a.patient_id = p.patient_id 
                         AND a.provider_id = %s), 
                        p.created_at
                    ) as last_visit
                FROM patients p
                WHERE p.is_active = true
                AND (
                    -- Patients who have appointments with this provider
                    EXISTS (
                        SELECT 1 FROM appointments a 
                        WHERE a.patient_id = p.patient_id 
                        AND a.provider_id = %s
                    )
                    OR
                    -- Patients directly added by this provider (if we track this)
                    p.provider_id = %s
                )
                ORDER BY last_visit DESC
            """, (provider_id, provider_id, provider_id))
            
            patients = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Retrieved {len(patients)} patients for provider {provider_id}")
        return {
            "success": True,
            "patients": [dict(patient) for patient in patients]
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching provider patients: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch provider patients")

@app.post("/api/v1/patients")
async def create_patient(patient_data: Dict[str, Any]):
    """Create a new patient with login credentials"""
    try:
        import secrets
        import string
        
        # Generate medical record number if not provided
        if not patient_data.get('medical_record_number'):
            # Generate a unique MRN: MRN + 8 random digits
            mrn_prefix = "MRN"
            random_digits = ''.join(secrets.choice(string.digits) for _ in range(8))
            medical_record_number = f"{mrn_prefix}{random_digits}"
        else:
            medical_record_number = patient_data.get('medical_record_number')
        
        # Generate random password for patient login
        password_length = 12
        password_chars = string.ascii_letters + string.digits + "!@#$%^&*"
        generated_password = ''.join(secrets.choice(password_chars) for _ in range(password_length))
        
        # Generate username (email if provided, otherwise first_name.last_name)
        if patient_data.get('email'):
            username = patient_data.get('email')
        else:
            username = f"{patient_data.get('first_name', '').lower()}.{patient_data.get('last_name', '').lower()}@abena.com"
        
        conn = get_db_connection()
        with conn.cursor() as cur:
            # First, create user account in users table
            cur.execute("""
                INSERT INTO users (
                    email,
                    password,
                    first_name,
                    last_name,
                    role,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                username,
                generated_password,  # In production, hash this password
                patient_data.get('first_name'),
                patient_data.get('last_name'),
                'patient',
                datetime.now(),
                datetime.now()
            ))
            user_id = cur.fetchone()['id']
            
            # Then create patient record
            cur.execute("""
                INSERT INTO patients (
                    patient_id,
                    medical_record_number,
                    first_name,
                    last_name,
                    email,
                    phone,
                    date_of_birth,
                    gender,
                    address,
                    provider_id,
                    is_active,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING patient_id
            """, (
                user_id,  # Use user_id as patient_id for consistency
                medical_record_number,
                patient_data.get('first_name'),
                patient_data.get('last_name'),
                username,
                patient_data.get('phone'),
                patient_data.get('date_of_birth'),
                patient_data.get('gender'),
                patient_data.get('address'),
                patient_data.get('provider_id'),
                True,
                datetime.now(),
                datetime.now()
            ))
            patient_id = cur.fetchone()['patient_id']
            conn.commit()
        conn.close()
        
        # Prepare login credentials for email
        login_credentials = {
            "username": username,
            "password": generated_password,
            "portal_url": "http://localhost:8000/login"
        }
        
        logger.info(f"✅ Patient created successfully: {patient_id}")
        logger.info(f"📧 Login credentials generated: {username}")
        
        # TODO: Send email with login credentials
        # For now, we'll return the credentials in the response
        # In production, send email and don't return password in response
        
        return {
            "success": True,
            "patient_id": str(patient_id),
            "medical_record_number": medical_record_number,
            "message": "Patient created successfully",
            "login_credentials": login_credentials,
            "email_sent": False  # TODO: Implement email sending
        }
    except Exception as e:
        logger.error(f"❌ Database error creating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to create patient")

@app.get("/api/v1/prescriptions/provider/{provider_id}")
async def get_provider_prescriptions(provider_id: str):
    """Get all prescriptions created by a specific provider"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    m.medication_id as id,
                    m.medication_name,
                    m.dosage,
                    m.frequency,
                    m.start_date as prescribed_date,
                    m.end_date,
                    m.status,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.patient_id,
                    ph.pharmacy_name,
                    m.created_at
                FROM medications m
                LEFT JOIN patients p ON m.patient_id = p.patient_id
                LEFT JOIN pharmacies ph ON m.pharmacy_id = ph.id
                WHERE m.prescribing_physician = %s
                ORDER BY m.created_at DESC
            """, (provider_id,))
            
            prescriptions = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Retrieved {len(prescriptions)} prescriptions for provider {provider_id}")
        return {
            "success": True,
            "prescriptions": [dict(prescription) for prescription in prescriptions]
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching provider prescriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch provider prescriptions")

@app.put("/api/v1/prescriptions/{prescription_id}")
async def update_prescription(prescription_id: str, prescription_data: Dict[str, Any]):
    """Update an existing prescription"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Build dynamic update query
            update_fields = []
            values = []
            
            if 'medication_name' in prescription_data:
                update_fields.append("medication_name = %s")
                values.append(prescription_data['medication_name'])
            
            if 'dosage' in prescription_data:
                update_fields.append("dosage = %s")
                values.append(prescription_data['dosage'])
            
            if 'frequency' in prescription_data:
                update_fields.append("frequency = %s")
                values.append(prescription_data['frequency'])
            
            if 'start_date' in prescription_data:
                update_fields.append("start_date = %s")
                values.append(prescription_data['start_date'])
            
            if 'end_date' in prescription_data:
                update_fields.append("end_date = %s")
                values.append(prescription_data['end_date'])
            
            if 'status' in prescription_data:
                update_fields.append("status = %s")
                values.append(prescription_data['status'])
            
            if 'pharmacy_id' in prescription_data:
                update_fields.append("pharmacy_id = %s")
                values.append(prescription_data['pharmacy_id'])
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(prescription_id)
            
            query = f"""
                UPDATE medications 
                SET {', '.join(update_fields)}
                WHERE medication_id = %s
                RETURNING medication_id
            """
            
            cur.execute(query, values)
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Prescription not found")
            
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Prescription updated: {prescription_id}")
        return {
            "success": True,
            "medication_id": prescription_id,
            "message": "Prescription updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Database error updating prescription: {e}")
        raise HTTPException(status_code=500, detail="Failed to update prescription")

@app.delete("/api/v1/prescriptions/{prescription_id}")
async def delete_prescription(prescription_id: str):
    """Delete a prescription (soft delete by setting status to cancelled)"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE medications 
                SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
                WHERE medication_id = %s
                RETURNING medication_id
            """, (prescription_id,))
            
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Prescription not found")
            
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Prescription cancelled: {prescription_id}")
        return {
            "success": True,
            "medication_id": prescription_id,
            "message": "Prescription cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Database error cancelling prescription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel prescription")

@app.get("/api/v1/pharmacies")
async def get_pharmacies():
    """Get all active pharmacies"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    pharmacy_name,
                    address,
                    phone,
                    email,
                    contact_person,
                    is_active
                FROM pharmacies 
                WHERE is_active = true
                ORDER BY pharmacy_name
            """)
            
            pharmacies = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Retrieved {len(pharmacies)} pharmacies from database")
        return {
            "success": True,
            "pharmacies": [dict(pharmacy) for pharmacy in pharmacies]
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching pharmacies: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pharmacies")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from src.config.email_config import EmailConfig

@app.post("/api/v1/prescriptions/{prescription_id}/send")
async def send_prescription(prescription_id: str, pharmacy_data: Dict[str, str]):
    """Send prescription to pharmacy"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # First get prescription details
            cur.execute("""
                SELECT m.*, p.first_name || ' ' || p.last_name as patient_name
                FROM medications m
                LEFT JOIN patients p ON m.patient_id = p.patient_id
                WHERE m.medication_id = %s
            """, (prescription_id,))
            prescription = cur.fetchone()
            
            if not prescription:
                raise HTTPException(status_code=404, detail="Prescription not found")
            
            # Update prescription status
            cur.execute("""
                UPDATE medications 
                SET status = 'sent_to_pharmacy'
                WHERE medication_id = %s
            """, (prescription_id,))
            conn.commit()
        conn.close()
        
        # Get pharmacy contact information
        pharmacy_name = pharmacy_data.get('pharmacyName', 'Unknown Pharmacy')
        pharmacy_contact = pharmacy_data.get('pharmacyContact', 'No contact provided')
        contact_type = pharmacy_data.get('contactType', 'email')
        
        logger.info(f"✅ Prescription {prescription_id} sent to pharmacy: {pharmacy_name}")
        logger.info(f"📧 Contact: {pharmacy_contact} ({contact_type})")
        
        # Send email if contact type is email
        if contact_type == 'email':
            try:
                await send_prescription_email(prescription, pharmacy_contact, pharmacy_name)
                logger.info(f"📧 Email sent successfully to: {pharmacy_contact}")
            except Exception as email_error:
                logger.error(f"❌ Email sending failed: {email_error}")
                # Continue with the process even if email fails
        else:
            logger.info(f"📱 Would send SMS to: {pharmacy_contact}")
            # TODO: Implement SMS sending
        
        return {
            "success": True,
            "prescriptionId": prescription_id,
            "pharmacyName": pharmacy_name,
            "pharmacyContact": pharmacy_contact,
            "contactType": contact_type,
            "status": "sent",
            "sentAt": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Database error sending prescription: {e}")
        raise HTTPException(status_code=500, detail="Failed to send prescription")

async def send_prescription_email(prescription, pharmacy_email: str, pharmacy_name: str):
    """Send prescription email to pharmacy"""
    try:
        # Create email content using template
        subject = EmailConfig.PRESCRIPTION_EMAIL_SUBJECT.format(
            patient_name=prescription['patient_name']
        )
        
        body = EmailConfig.PRESCRIPTION_EMAIL_BODY.format(
            pharmacy_name=pharmacy_name,
            patient_name=prescription['patient_name'],
            patient_id=prescription['patient_id'],
            medication_name=prescription['medication_name'],
            dosage=prescription['dosage'],
            frequency=prescription['frequency'],
            prescribing_physician=prescription['prescribing_physician'],
            prescription_date=prescription['start_date']
        )
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EmailConfig.SENDER_EMAIL
        msg['To'] = pharmacy_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Log the email content
        logger.info(f"📧 EMAIL CONTENT:")
        logger.info(f"To: {pharmacy_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body}")
        
        # Check if email is configured for real sending
        if EmailConfig.is_configured():
            # Send real email
            smtp_config = EmailConfig.get_smtp_config()
            
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            if smtp_config['use_tls']:
                server.starttls()
            
            server.login(smtp_config['username'], smtp_config['password'])
            text = msg.as_string()
            server.sendmail(smtp_config['username'], pharmacy_email, text)
            server.quit()
            
            logger.info(f"📧 Email sent successfully to {pharmacy_email}")
        else:
            # Mock mode - just log
            logger.info(f"📧 Email would be sent to {pharmacy_email} (mock mode - configure SMTP for real sending)")
            logger.info(f"📧 To enable real email sending, set environment variables:")
            logger.info(f"📧 SENDER_EMAIL=your-email@gmail.com")
            logger.info(f"📧 SENDER_PASSWORD=your-app-password")
        
    except Exception as e:
        logger.error(f"❌ Error creating/sending email: {e}")
        raise e

# Lab requests endpoint - NOW USING REAL DATABASE
@app.post("/api/v1/lab-requests")
async def create_lab_request(lab_request_data: Dict[str, Any]):
    """Create a new lab request"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO lab_results (
                    patient_id, 
                    test_name, 
                    test_date, 
                    ordered_by, 
                    status
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                lab_request_data.get('patientId'),
                lab_request_data.get('testName'),
                datetime.now(),
                lab_request_data.get('providerId'),
                'ordered'
            ))
            lab_request_id = cur.fetchone()['id']
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Lab request created in database: {lab_request_id}")
        return {
            "success": True,
            "id": lab_request_id,
            "message": "Lab request created successfully"
        }
    except Exception as e:
        logger.error(f"❌ Database error creating lab request: {e}")
        raise HTTPException(status_code=500, detail="Failed to create lab request")

@app.post("/api/v1/lab-requests/{lab_request_id}/send")
async def send_lab_request(lab_request_id: str, laboratory_data: Dict[str, str]):
    """Send lab request to laboratory"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE lab_results 
                SET status = 'sent_to_lab', 
                    updated_at = %s
                WHERE result_id = %s
            """, (datetime.now(), lab_request_id))
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Lab request {lab_request_id} sent to laboratory")
        return {
            "success": True,
            "labRequestId": lab_request_id,
            "laboratoryName": laboratory_data.get('laboratoryName'),
            "status": "sent",
            "sentAt": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Database error sending lab request: {e}")
        raise HTTPException(status_code=500, detail="Failed to send lab request")

# Lab results endpoints - NOW USING REAL DATABASE
@app.get("/api/v1/lab-results")
async def get_lab_results(patient_id: Optional[str] = None):
    """Get lab results with optional patient filter"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if patient_id:
                cur.execute("""
                    SELECT 
                        lr.result_id as id,
                        lr.test_name,
                        lr.test_code,
                        lr.result_value,
                        lr.result_text,
                        lr.unit,
                        lr.reference_range,
                        lr.abnormal_flag,
                        lr.test_date,
                        lr.lab_name,
                        lr.created_at,
                        p.first_name || ' ' || p.last_name as patient_name
                    FROM lab_results lr
                    LEFT JOIN patients p ON lr.patient_id = p.patient_id
                    WHERE lr.patient_id = %s
                    ORDER BY lr.test_date DESC
                """, (patient_id,))
            else:
                cur.execute("""
                    SELECT 
                        lr.result_id as id,
                        lr.test_name,
                        lr.test_code,
                        lr.result_value,
                        lr.result_text,
                        lr.unit,
                        lr.reference_range,
                        lr.abnormal_flag,
                        lr.test_date,
                        lr.lab_name,
                        lr.created_at,
                        p.first_name || ' ' || p.last_name as patient_name
                    FROM lab_results lr
                    LEFT JOIN patients p ON lr.patient_id = p.patient_id
                    ORDER BY lr.test_date DESC
                """)
            
            lab_results = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Retrieved {len(lab_results)} lab results from database")
        return {
            "success": True,
            "lab_results": [dict(result) for result in lab_results]
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching lab results: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch lab results")

@app.get("/api/v1/lab-results/{result_id}")
async def get_lab_result_details(result_id: str):
    """Get detailed lab result by ID"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    lr.result_id as id,
                    lr.test_name,
                    lr.test_code,
                    lr.result_value,
                    lr.result_text,
                    lr.unit,
                    lr.reference_range,
                    lr.abnormal_flag,
                    lr.test_date,
                    lr.lab_name,
                    lr.created_at,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.patient_id
                FROM lab_results lr
                LEFT JOIN patients p ON lr.patient_id = p.patient_id
                WHERE lr.result_id = %s
            """, (result_id,))
            
            result = cur.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Lab result not found")
        
        logger.info(f"✅ Retrieved lab result details: {result_id}")
        return {
            "success": True,
            "lab_result": dict(result)
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching lab result details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch lab result details")

@app.post("/api/v1/lab-results/upload")
async def upload_lab_result(
    patient_id: str = Form(...),
    test_name: str = Form(...),
    test_code: str = Form(None),
    result_value: str = Form(None),
    result_text: str = Form(None),
    unit: str = Form(None),
    reference_range: str = Form(None),
    abnormal_flag: str = Form("N"),
    lab_name: str = Form(...),
    test_date: str = Form(...),
    report_file: UploadFile = File(None)
):
    """Upload a new lab result with optional file attachment"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Insert lab result
            cur.execute("""
                INSERT INTO lab_results (
                    patient_id, 
                    test_name, 
                    test_code, 
                    result_value, 
                    result_text, 
                    unit, 
                    reference_range, 
                    abnormal_flag, 
                    test_date, 
                    lab_name,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING result_id
            """, (
                patient_id,
                test_name,
                test_code,
                result_value if result_value else None,
                result_text,
                unit,
                reference_range,
                abnormal_flag,
                test_date,
                lab_name,
                datetime.now()
            ))
            
            result_id = cur.fetchone()['result_id']
            
            # Handle file upload if provided
            file_path = None
            if report_file:
                # Create uploads directory if it doesn't exist
                upload_dir = "uploads/lab_reports"
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                file_extension = os.path.splitext(report_file.filename)[1]
                filename = f"lab_report_{result_id}_{int(time.time())}{file_extension}"
                file_path = os.path.join(upload_dir, filename)
                
                # Save file
                with open(file_path, "wb") as buffer:
                    content = await report_file.read()
                    buffer.write(content)
                
                # Update database with file path
                cur.execute("""
                    UPDATE lab_results 
                    SET report_file_path = %s 
                    WHERE result_id = %s
                """, (file_path, result_id))
            
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Lab result uploaded successfully: {result_id}")
        return {
            "success": True,
            "result_id": result_id,
            "message": "Lab result uploaded successfully",
            "file_path": file_path
        }
    except Exception as e:
        logger.error(f"❌ Database error uploading lab result: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload lab result")

# Documents endpoints
@app.get("/api/v1/documents")
async def get_documents(patient_id: Optional[str] = None):
    """Get documents with optional patient filter"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if patient_id:
                cur.execute("""
                    SELECT 
                        pd.document_id as id,
                        pd.document_name,
                        pd.document_type,
                        pd.file_path,
                        pd.file_size,
                        pd.mime_type,
                        pd.upload_date,
                        pd.is_confidential,
                        pd.expiration_date,
                        pd.tags,
                        p.first_name || ' ' || p.last_name as patient_name
                    FROM patient_documents pd
                    LEFT JOIN patients p ON pd.patient_id = p.patient_id
                    WHERE pd.patient_id = %s
                    ORDER BY pd.upload_date DESC
                """, (patient_id,))
            else:
                cur.execute("""
                    SELECT 
                        pd.document_id as id,
                        pd.document_name,
                        pd.document_type,
                        pd.file_path,
                        pd.file_size,
                        pd.mime_type,
                        pd.upload_date,
                        pd.is_confidential,
                        pd.expiration_date,
                        pd.tags,
                        p.first_name || ' ' || p.last_name as patient_name
                    FROM patient_documents pd
                    LEFT JOIN patients p ON pd.patient_id = p.patient_id
                    ORDER BY pd.upload_date DESC
                """)
            
            documents = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Retrieved {len(documents)} documents from database")
        return {
            "success": True,
            "documents": [dict(doc) for doc in documents]
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@app.post("/api/v1/documents/upload")
async def upload_document(
    patient_id: str = Form(...),
    document_name: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    is_confidential: bool = Form(False),
    tags: str = Form(None)
):
    """Upload a new document"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads/documents"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"doc_{int(time.time())}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse tags if provided
        tag_array = None
        if tags:
            tag_array = [tag.strip() for tag in tags.split(',')]
        
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO patient_documents (
                    patient_id,
                    document_name,
                    document_type,
                    file_path,
                    file_size,
                    mime_type,
                    uploaded_by,
                    upload_date,
                    is_confidential,
                    tags
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING document_id
            """, (
                patient_id,
                document_name,
                document_type,
                file_path,
                len(content),
                file.content_type,
                None,  # uploaded_by - could be set from auth token
                datetime.now(),
                is_confidential,
                tag_array
            ))
            
            document_id = cur.fetchone()['document_id']
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Document uploaded successfully: {document_id}")
        return {
            "success": True,
            "document_id": document_id,
            "message": "Document uploaded successfully",
            "file_path": file_path
        }
    except Exception as e:
        logger.error(f"❌ Database error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")

@app.get("/api/v1/documents/{document_id}")
async def get_document_details(document_id: str):
    """Get detailed document information"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    pd.document_id as id,
                    pd.document_name,
                    pd.document_type,
                    pd.file_path,
                    pd.file_size,
                    pd.mime_type,
                    pd.upload_date,
                    pd.is_confidential,
                    pd.expiration_date,
                    pd.tags,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.patient_id
                FROM patient_documents pd
                LEFT JOIN patients p ON pd.patient_id = p.patient_id
                WHERE pd.document_id = %s
            """, (document_id,))
            
            document = cur.fetchone()
        conn.close()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"✅ Retrieved document details: {document_id}")
        return {
            "success": True,
            "document": dict(document)
        }
    except Exception as e:
        logger.error(f"❌ Database error fetching document details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document details")

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get file path before deleting
            cur.execute("SELECT file_path FROM patient_documents WHERE document_id = %s", (document_id,))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Document not found")
            
            file_path = result['file_path']
            
            # Delete from database
            cur.execute("DELETE FROM patient_documents WHERE document_id = %s", (document_id,))
            conn.commit()
        conn.close()
        
        # Delete file from filesystem
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        logger.info(f"✅ Document deleted successfully: {document_id}")
        return {
            "success": True,
            "message": "Document deleted successfully"
        }
    except Exception as e:
        logger.error(f"❌ Database error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")


if __name__ == "__main__":
    # Development server configuration
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    ) 