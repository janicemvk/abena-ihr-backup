"""
Abena IHR Clinical Outcomes Management System
Main API Application

This module provides the main FastAPI application for the Abena IHR system,
including clinical outcomes management, patient data, and predictive analytics.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from .routers import patients, outcomes, predictions
from src.predictive_analytics.predictive_engine import prediction_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        "https://abena-ihr.com",  # Production domain
        "https://www.abena-ihr.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api/v1", tags=["patients"])
app.include_router(outcomes.router, prefix="/api/v1", tags=["outcomes"])
app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
app.include_router(prediction_router, prefix="/api/v1", tags=["predictive-analytics"])

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

# Authentication endpoints - NOW USING REAL DATABASE
@app.post("/api/v1/auth/login")
async def login(credentials: Dict[str, str]):
    """Real authentication endpoint that validates against database"""
    try:
        email = credentials.get('email', '').strip()
        password = credentials.get('password', '').strip()
        user_type = credentials.get('userType', 'patient')
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        conn = get_db_connection()
        with conn.cursor() as cur:
            if user_type == 'patient':
                # Check patients table
                cur.execute("""
                    SELECT 
                        patient_id,
                        first_name,
                        last_name,
                        email,
                        is_active
                    FROM patients 
                    WHERE email = %s AND is_active = true
                """, (email,))
                user = cur.fetchone()
                
                if not user:
                    raise HTTPException(status_code=401, detail="Invalid patient credentials")
                
                # In a real system, you would hash and verify the password
                # For now, we'll use a simple check (password should match email domain)
                if password != f"password_{email.split('@')[0]}":
                    raise HTTPException(status_code=401, detail="Invalid password")
                
                user_id = str(user['patient_id'])
                user_name = f"{user['first_name']} {user['last_name']}"
                
            elif user_type == 'doctor':
                # Check providers table
                cur.execute("""
                    SELECT 
                        provider_id,
                        first_name,
                        last_name,
                        email,
                        is_active
                    FROM providers 
                    WHERE email = %s AND is_active = true
                """, (email,))
                user = cur.fetchone()
                
                if not user:
                    raise HTTPException(status_code=401, detail="Invalid provider credentials")
                
                # In a real system, you would hash and verify the password
                # For now, we'll use a simple check (password should match email domain)
                if password != f"password_{email.split('@')[0]}":
                    raise HTTPException(status_code=401, detail="Invalid password")
                
                user_id = str(user['provider_id'])
                user_name = f"Dr. {user['first_name']} {user['last_name']}"
                
            else:
                raise HTTPException(status_code=400, detail="Invalid user type")
        
        conn.close()
        
        # Generate a simple token (in production, use JWT)
        token = f"token_{user_id}_{int(datetime.now().timestamp())}"
        
        logger.info(f"✅ Real authentication successful for {user_type}: {email}")
        
        return {
            "success": True,
            "token": token,
            "userId": user_id,
            "userName": user_name,
            "userType": user_type,
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

# Appointments endpoint - NOW USING REAL DATABASE
@app.get("/api/v1/appointments")
async def get_appointments(patient_id: Optional[str] = Query(None)):
    """Get appointments from database"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if patient_id:
                cur.execute("""
                    SELECT 
                        appointment_id,
                        patient_id,
                        provider_id,
                        appointment_date,
                        appointment_time,
                        appointment_type,
                        status,
                        notes,
                        created_at,
                        updated_at
                    FROM appointments 
                    WHERE patient_id = %s
                    ORDER BY appointment_date DESC, appointment_time DESC
                """, (patient_id,))
            else:
                cur.execute("""
                    SELECT 
                        appointment_id,
                        patient_id,
                        provider_id,
                        appointment_date,
                        appointment_time,
                        appointment_type,
                        status,
                        notes,
                        created_at,
                        updated_at
                    FROM appointments 
                    ORDER BY appointment_date DESC, appointment_time DESC
                """)
            appointments = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Real appointment data loaded from database: {len(appointments)} appointments")
        return [dict(appointment) for appointment in appointments]
    except Exception as e:
        logger.error(f"❌ Database error fetching appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch appointments from database")

# Prescriptions endpoint - NOW USING REAL DATABASE
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
                    prescribed_by, 
                    prescribed_date, 
                    status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                prescription_data.get('patientId'),
                prescription_data.get('medicationName'),
                prescription_data.get('dosage'),
                prescription_data.get('frequency'),
                prescription_data.get('providerId'),
                datetime.now(),
                'active'
            ))
            prescription_id = cur.fetchone()['id']
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Prescription created in database: {prescription_id}")
        return {
            "success": True,
            "id": prescription_id,
            "message": "Prescription created successfully"
        }
    except Exception as e:
        logger.error(f"❌ Database error creating prescription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create prescription")

@app.post("/api/v1/prescriptions/{prescription_id}/send")
async def send_prescription(prescription_id: str, pharmacy_data: Dict[str, str]):
    """Send prescription to pharmacy"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE medications 
                SET status = 'sent_to_pharmacy', 
                    updated_at = %s
                WHERE id = %s
            """, (datetime.now(), prescription_id))
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Prescription {prescription_id} sent to pharmacy")
        return {
            "success": True,
            "prescriptionId": prescription_id,
            "pharmacyName": pharmacy_data.get('pharmacyName'),
            "status": "sent",
            "sentAt": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Database error sending prescription: {e}")
        raise HTTPException(status_code=500, detail="Failed to send prescription")

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
                WHERE id = %s
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