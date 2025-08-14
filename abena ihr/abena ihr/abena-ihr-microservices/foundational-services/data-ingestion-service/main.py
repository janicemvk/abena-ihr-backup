# main.py - Abena IHR Data Ingestion Service
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import uuid

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ValidationError, Field
import asyncpg
import redis.asyncio as redis
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import httpx
from cryptography.fernet import Fernet
import hashlib
from hl7apy.parser import parse_message as hl7apy_parse_message
from fhirpy import SyncFHIRClient
import jsonschema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/abena_ihr_data")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:3001")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
    MAX_MESSAGE_SIZE = int(os.getenv("MAX_MESSAGE_SIZE", "10485760"))  # 10MB
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
    DUPLICATE_CHECK_WINDOW = int(os.getenv("DUPLICATE_CHECK_WINDOW", "3600"))  # 1 hour

config = Config()

# Initialize FastAPI app
app = FastAPI(
    title="Abena IHR Data Ingestion Service",
    description="Real-time health data streaming and processing service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
cipher_suite = Fernet(config.ENCRYPTION_KEY.encode() if isinstance(config.ENCRYPTION_KEY, str) else config.ENCRYPTION_KEY)

# Global connections
db_pool = None
redis_client = None
kafka_producer = None

# Data Models
class HealthDataBase(BaseModel):
    patient_id: str
    provider_id: Optional[str] = None
    data_type: str = Field(..., description="Type of health data (vitals, labs, medications, etc.)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_system: str = Field(..., description="Source system identifier")
    
class VitalSigns(HealthDataBase):
    data_type: str = "vitals"
    heart_rate: Optional[int] = Field(None, ge=0, le=300)
    blood_pressure_systolic: Optional[int] = Field(None, ge=0, le=300)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=0, le=200)
    temperature: Optional[float] = Field(None, ge=80.0, le=110.0)  # Fahrenheit
    oxygen_saturation: Optional[float] = Field(None, ge=0.0, le=100.0)
    respiratory_rate: Optional[int] = Field(None, ge=0, le=60)
    weight: Optional[float] = Field(None, ge=0.0, le=1000.0)  # lbs
    height: Optional[float] = Field(None, ge=0.0, le=120.0)  # inches

class LabResult(HealthDataBase):
    data_type: str = "lab_result"
    test_name: str
    result_value: str
    reference_range: Optional[str] = None
    units: Optional[str] = None
    status: str = Field(default="final", description="preliminary, final, corrected, etc.")
    lab_id: Optional[str] = None

class Medication(HealthDataBase):
    data_type: str = "medication"
    medication_name: str
    dosage: str
    frequency: str
    start_date: datetime
    end_date: Optional[datetime] = None
    prescriber_id: str
    pharmacy_id: Optional[str] = None
    ndc_code: Optional[str] = None

class HL7Message(BaseModel):
    message_type: str = Field(..., description="HL7 message type (ADT, ORU, etc.)")
    message_control_id: str
    sending_application: str
    receiving_application: str
    timestamp: datetime
    raw_message: str
    patient_id: Optional[str] = None

class FHIRResource(BaseModel):
    resource_type: str = Field(..., description="FHIR resource type")
    resource_id: str
    patient_reference: Optional[str] = None
    raw_resource: Dict[str, Any]
    version: str = Field(default="R4")

class DataValidationError(BaseModel):
    field: str
    error: str
    received_value: Any

class ProcessingResult(BaseModel):
    success: bool
    message_id: str
    patient_id: Optional[str] = None
    processed_at: datetime
    errors: List[DataValidationError] = []
    duplicate: bool = False

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token with Auth service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.AUTH_SERVICE_URL}/auth/profile",
                headers={"Authorization": f"Bearer {credentials.credentials}"}
            )
            
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )

# Database functions
async def init_db():
    """Initialize database connection pool"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(config.DATABASE_URL, min_size=5, max_size=20)
        logger.info("Database connection pool created")
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.from_url(config.REDIS_URL)
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

async def init_kafka():
    """Initialize Kafka producer"""
    global kafka_producer
    try:
        kafka_producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8') if k else None,
            max_request_size=config.MAX_MESSAGE_SIZE,
            retries=3,
            acks='all'
        )
        logger.info("Kafka producer initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        raise

# Utility functions
def generate_message_id() -> str:
    """Generate unique message ID"""
    return str(uuid.uuid4())

def calculate_checksum(data: str) -> str:
    """Calculate SHA-256 checksum for duplicate detection"""
    return hashlib.sha256(data.encode()).hexdigest()

async def check_duplicate(checksum: str) -> bool:
    """Check if message is duplicate using Redis"""
    try:
        exists = await redis_client.exists(f"msg_checksum:{checksum}")
        if not exists:
            await redis_client.setex(
                f"msg_checksum:{checksum}", 
                config.DUPLICATE_CHECK_WINDOW, 
                "1"
            )
            return False
        return True
    except Exception as e:
        logger.error(f"Duplicate check failed: {e}")
        return False

async def store_raw_data(data: Dict[str, Any], data_type: str) -> str:
    """Store raw data in database"""
    message_id = generate_message_id()
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO raw_health_data (
                message_id, data_type, raw_data, received_at, 
                source_system, patient_id, processing_status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, 
        message_id, data_type, json.dumps(data), datetime.now(timezone.utc),
        data.get('source_system'), data.get('patient_id'), 'received'
        )
    
    return message_id

async def publish_to_kafka(topic: str, data: Dict[str, Any], key: Optional[str] = None):
    """Publish data to Kafka topic"""
    try:
        future = kafka_producer.send(topic, value=data, key=key)
        kafka_producer.flush()
        logger.info(f"Published message to topic {topic}")
    except KafkaError as e:
        logger.error(f"Failed to publish to Kafka: {e}")
        raise

# HL7 Parser
class HL7Parser:
    """HL7 message parser using hl7apy"""
    @staticmethod
    def parse_message(raw_message: str) -> Dict[str, Any]:
        try:
            msg = hl7apy_parse_message(raw_message, find_groups=False)
            segments = {}
            # Extract MSH
            msh = msg.segment('MSH')
            segments['MSH'] = {
                'sending_application': msh.sending_application.value if hasattr(msh, 'sending_application') else '',
                'receiving_application': msh.receiving_application.value if hasattr(msh, 'receiving_application') else '',
                'timestamp': msh.date_time_of_message.value if hasattr(msh, 'date_time_of_message') else '',
                'message_type': msh.message_type.value if hasattr(msh, 'message_type') else '',
                'control_id': msh.message_control_id.value if hasattr(msh, 'message_control_id') else ''
            }
            # Extract PID
            pid = msg.segment('PID') if msg.children.get('PID') else None
            if pid:
                segments['PID'] = {
                    'patient_id': pid.patient_identifier_list.value if hasattr(pid, 'patient_identifier_list') else '',
                    'patient_name': pid.patient_name.value if hasattr(pid, 'patient_name') else '',
                    'birth_date': pid.date_time_of_birth.value if hasattr(pid, 'date_time_of_birth') else '',
                    'gender': pid.administrative_sex.value if hasattr(pid, 'administrative_sex') else ''
                }
            # Extract OBX segments
            obx_segments = msg.segments('OBX')
            if obx_segments:
                segments['OBX'] = []
                for obx in obx_segments:
                    segments['OBX'].append({
                        'observation_id': obx.observation_identifier.value if hasattr(obx, 'observation_identifier') else '',
                        'observation_value': obx.observation_value.value if hasattr(obx, 'observation_value') else '',
                        'units': obx.units.value if hasattr(obx, 'units') else '',
                        'reference_range': obx.references_range.value if hasattr(obx, 'references_range') else ''
                    })
            return segments
        except Exception as e:
            logger.error(f"HL7 parsing error (hl7apy): {e}")
            raise ValueError(f"Invalid HL7 message format: {e}")

# FHIR Parser
class FHIRParser:
    """FHIR resource parser using fhirpy and jsonschema validation"""
    @staticmethod
    def parse_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Validate FHIR resource using jsonschema (basic check)
            if 'resourceType' not in resource:
                raise ValueError("Missing resourceType in FHIR resource")
            # Optionally, load a FHIR schema and validate here
            # Example: jsonschema.validate(instance=resource, schema=fhir_schema)
            # Use fhirpy for resource handling
            client = SyncFHIRClient('http://example.com/fhir')  # Dummy endpoint for validation only
            fhir_resource = client.resource(resource['resourceType'], **resource)
            # Extract patient reference
            patient_ref = None
            if resource['resourceType'] == 'Patient':
                patient_ref = resource.get('id')
            elif 'subject' in resource:
                ref = resource['subject'].get('reference', '')
                patient_ref = ref.replace('Patient/', '') if ref else None
            elif 'patient' in resource:
                ref = resource['patient'].get('reference', '')
                patient_ref = ref.replace('Patient/', '') if ref else None
            return {
                'resource_type': resource['resourceType'],
                'resource_id': resource.get('id', str(uuid.uuid4())),
                'patient_reference': patient_ref,
                'raw_resource': resource
            }
        except jsonschema.ValidationError as ve:
            logger.error(f"FHIR resource schema validation error: {ve}")
            raise ValueError(f"FHIR resource schema validation error: {ve}")
        except Exception as e:
            logger.error(f"FHIR parsing error (fhirpy): {e}")
            raise ValueError(f"Invalid FHIR resource: {e}")

# API Routes
@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    await init_db()
    await init_redis()
    await init_kafka()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    if kafka_producer:
        kafka_producer.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Abena IHR Data Ingestion Service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@app.post("/ingest/vitals", response_model=ProcessingResult)
async def ingest_vitals(
    vitals: VitalSigns,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Ingest vital signs data"""
    try:
        # Convert to dict and add metadata
        data = vitals.dict()
        data['ingested_by'] = user['id']
        data['ingested_at'] = datetime.now(timezone.utc).isoformat()
        
        # Check for duplicates
        checksum = calculate_checksum(json.dumps(data, sort_keys=True))
        is_duplicate = await check_duplicate(checksum)
        
        # Store raw data
        message_id = await store_raw_data(data, 'vitals')
        
        # Publish to Kafka for further processing
        if not is_duplicate:
            background_tasks.add_task(
                publish_to_kafka, 
                'health-data-vitals', 
                data, 
                vitals.patient_id
            )
        
        return ProcessingResult(
            success=True,
            message_id=message_id,
            patient_id=vitals.patient_id,
            processed_at=datetime.now(timezone.utc),
            duplicate=is_duplicate
        )
        
    except Exception as e:
        logger.error(f"Vitals ingestion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process vitals data: {str(e)}"
        )

@app.post("/ingest/lab-results", response_model=ProcessingResult)
async def ingest_lab_results(
    lab_result: LabResult,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Ingest laboratory results"""
    try:
        data = lab_result.dict()
        data['ingested_by'] = user['id']
        data['ingested_at'] = datetime.now(timezone.utc).isoformat()
        
        checksum = calculate_checksum(json.dumps(data, sort_keys=True))
        is_duplicate = await check_duplicate(checksum)
        
        message_id = await store_raw_data(data, 'lab_result')
        
        if not is_duplicate:
            background_tasks.add_task(
                publish_to_kafka, 
                'health-data-labs', 
                data, 
                lab_result.patient_id
            )
        
        return ProcessingResult(
            success=True,
            message_id=message_id,
            patient_id=lab_result.patient_id,
            processed_at=datetime.now(timezone.utc),
            duplicate=is_duplicate
        )
        
    except Exception as e:
        logger.error(f"Lab result ingestion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process lab result: {str(e)}"
        )

@app.post("/ingest/medications", response_model=ProcessingResult)
async def ingest_medications(
    medication: Medication,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Ingest medication data"""
    try:
        data = medication.dict()
        data['ingested_by'] = user['id']
        data['ingested_at'] = datetime.now(timezone.utc).isoformat()
        
        checksum = calculate_checksum(json.dumps(data, sort_keys=True))
        is_duplicate = await check_duplicate(checksum)
        
        message_id = await store_raw_data(data, 'medication')
        
        if not is_duplicate:
            background_tasks.add_task(
                publish_to_kafka, 
                'health-data-medications', 
                data, 
                medication.patient_id
            )
        
        return ProcessingResult(
            success=True,
            message_id=message_id,
            patient_id=medication.patient_id,
            processed_at=datetime.now(timezone.utc),
            duplicate=is_duplicate
        )
        
    except Exception as e:
        logger.error(f"Medication ingestion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process medication data: {str(e)}"
        )

@app.post("/ingest/hl7", response_model=ProcessingResult)
async def ingest_hl7_message(
    hl7_message: HL7Message,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Ingest HL7 message"""
    try:
        # Parse HL7 message
        parsed_data = HL7Parser.parse_message(hl7_message.raw_message)
        
        # Extract patient ID from parsed data
        patient_id = parsed_data.get('PID', {}).get('patient_id') or hl7_message.patient_id
        
        data = {
            **hl7_message.dict(),
            'parsed_data': parsed_data,
            'patient_id': patient_id,
            'ingested_by': user['id'],
            'ingested_at': datetime.now(timezone.utc).isoformat()
        }
        
        checksum = calculate_checksum(hl7_message.raw_message)
        is_duplicate = await check_duplicate(checksum)
        
        message_id = await store_raw_data(data, 'hl7_message')
        
        if not is_duplicate:
            background_tasks.add_task(
                publish_to_kafka, 
                'health-data-hl7', 
                data, 
                patient_id
            )
        
        return ProcessingResult(
            success=True,
            message_id=message_id,
            patient_id=patient_id,
            processed_at=datetime.now(timezone.utc),
            duplicate=is_duplicate
        )
        
    except Exception as e:
        logger.error(f"HL7 ingestion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process HL7 message: {str(e)}"
        )

@app.post("/ingest/fhir", response_model=ProcessingResult)
async def ingest_fhir_resource(
    fhir_resource: FHIRResource,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Ingest FHIR resource"""
    try:
        # Parse and validate FHIR resource
        parsed_data = FHIRParser.parse_resource(fhir_resource.raw_resource)
        
        data = {
            **fhir_resource.dict(),
            'parsed_data': parsed_data,
            'ingested_by': user['id'],
            'ingested_at': datetime.now(timezone.utc).isoformat()
        }
        
        checksum = calculate_checksum(json.dumps(fhir_resource.raw_resource, sort_keys=True))
        is_duplicate = await check_duplicate(checksum)
        
        message_id = await store_raw_data(data, 'fhir_resource')
        
        if not is_duplicate:
            background_tasks.add_task(
                publish_to_kafka, 
                'health-data-fhir', 
                data, 
                parsed_data['patient_reference']
            )
        
        return ProcessingResult(
            success=True,
            message_id=message_id,
            patient_id=parsed_data['patient_reference'],
            processed_at=datetime.now(timezone.utc),
            duplicate=is_duplicate
        )
        
    except Exception as e:
        logger.error(f"FHIR ingestion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process FHIR resource: {str(e)}"
        )

@app.get("/status/{message_id}")
async def get_processing_status(
    message_id: str,
    user: Dict[str, Any] = Depends(verify_token)
):
    """Get processing status of a message"""
    try:
        async with db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT message_id, data_type, processing_status, 
                       received_at, processed_at, error_details
                FROM raw_health_data 
                WHERE message_id = $1
            """, message_id)
            
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
            
        return dict(result)
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get message status: {str(e)}"
        )

@app.get("/metrics")
async def get_metrics(user: Dict[str, Any] = Depends(verify_token)):
    """Get ingestion metrics"""
    try:
        async with db_pool.acquire() as conn:
            # Get daily ingestion counts by type
            daily_counts = await conn.fetch("""
                SELECT data_type, COUNT(*) as count,
                       DATE(received_at) as date
                FROM raw_health_data 
                WHERE received_at >= NOW() - INTERVAL '7 days'
                GROUP BY data_type, DATE(received_at)
                ORDER BY date DESC, data_type
            """)
            
            # Get processing status summary
            status_summary = await conn.fetch("""
                SELECT processing_status, COUNT(*) as count
                FROM raw_health_data
                WHERE received_at >= NOW() - INTERVAL '24 hours'
                GROUP BY processing_status
            """)
            
        return {
            "daily_ingestion_counts": [dict(row) for row in daily_counts],
            "processing_status_summary": [dict(row) for row in status_summary],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 