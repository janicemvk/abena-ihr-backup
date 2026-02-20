# Abena IHR - Data Transformation Layer (ETL)
# Complete implementation with Spark, FHIR conversion, mapping, and unit conversion

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os
from dotenv import load_dotenv

# Required dependencies (add to requirements.txt):
# pyspark==3.5.0
# fhir.resources==7.0.2
# sqlalchemy==2.0.23
# redis==5.0.1

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, when, regexp_replace, split, trim, lower, upper
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.identifier import Identifier
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

# Load environment variables
load_dotenv()

# Logging configuration
LOG_LEVEL = os.environ.get('ABENA_LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
LOG_FILE = os.environ.get('ABENA_LOG_FILE', 'abena_etl.log')

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    ]
)

# =============================================================================
# 1. MAPPING REPOSITORY - Store and manage data mapping configurations
# =============================================================================

Base = declarative_base()

class DataMappingConfig(Base):
    __tablename__ = 'data_mapping_configs'
    
    id = Column(Integer, primary_key=True)
    source_system = Column(String(100), nullable=False)
    target_system = Column(String(100), nullable=False)
    mapping_version = Column(String(20), nullable=False)
    mapping_config = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1)

class MappingRepository:
    def __init__(self, db_url: str = None):
        db_url = db_url or os.environ.get('ABENA_DB_URL', 'postgresql://user:pass@localhost/abena_ihr')
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Redis for caching frequently used mappings
        redis_host = os.environ.get('ABENA_REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('ABENA_REDIS_PORT', 6379))
        redis_db = int(os.environ.get('ABENA_REDIS_DB', 1))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    
    def create_mapping(self, source_system: str, target_system: str, 
                      mapping_config: Dict[str, Any], version: str = "1.0") -> int:
        """Create a new data mapping configuration"""
        mapping = DataMappingConfig(
            source_system=source_system,
            target_system=target_system,
            mapping_version=version,
            mapping_config=json.dumps(mapping_config)
        )
        self.session.add(mapping)
        self.session.commit()
        
        # Cache the mapping
        cache_key = f"mapping:{source_system}:{target_system}:{version}"
        self.redis_client.setex(cache_key, 3600, json.dumps(mapping_config))
        
        return mapping.id
    
    def get_mapping(self, source_system: str, target_system: str, 
                   version: str = "1.0") -> Optional[Dict[str, Any]]:
        """Retrieve mapping configuration with caching"""
        cache_key = f"mapping:{source_system}:{target_system}:{version}"
        
        # Try cache first
        cached_mapping = self.redis_client.get(cache_key)
        if cached_mapping:
            return json.loads(cached_mapping)
        
        # Query database
        mapping = self.session.query(DataMappingConfig).filter_by(
            source_system=source_system,
            target_system=target_system,
            mapping_version=version,
            is_active=1
        ).first()
        
        if mapping:
            config = json.loads(mapping.mapping_config)
            # Cache for 1 hour
            self.redis_client.setex(cache_key, 3600, mapping.mapping_config)
            return config
        
        return None

# =============================================================================
# 2. UNIT CONVERSION SERVICE - Handle different measurement systems
# =============================================================================

class UnitType(Enum):
    WEIGHT = "weight"
    HEIGHT = "height"
    TEMPERATURE = "temperature"
    BLOOD_PRESSURE = "blood_pressure"
    GLUCOSE = "glucose"
    HEART_RATE = "heart_rate"

@dataclass
class ConversionRule:
    from_unit: str
    to_unit: str
    factor: float
    offset: float = 0.0
    
    def convert(self, value: float) -> float:
        return (value * self.factor) + self.offset

class UnitConversionService:
    def __init__(self):
        self.conversion_rules = self._initialize_conversion_rules()
    
    def _initialize_conversion_rules(self) -> Dict[UnitType, List[ConversionRule]]:
        """Initialize all conversion rules for different unit types"""
        return {
            UnitType.WEIGHT: [
                ConversionRule("lb", "kg", 0.453592),
                ConversionRule("kg", "lb", 2.20462),
                ConversionRule("oz", "g", 28.3495),
                ConversionRule("g", "oz", 0.035274)
            ],
            UnitType.HEIGHT: [
                ConversionRule("ft", "cm", 30.48),
                ConversionRule("in", "cm", 2.54),
                ConversionRule("cm", "in", 0.393701),
                ConversionRule("cm", "ft", 0.0328084)
            ],
            UnitType.TEMPERATURE: [
                ConversionRule("F", "C", 5/9, -32 * 5/9),
                ConversionRule("C", "F", 9/5, 32),
                ConversionRule("K", "C", 1.0, -273.15),
                ConversionRule("C", "K", 1.0, 273.15)
            ],
            UnitType.GLUCOSE: [
                ConversionRule("mg/dL", "mmol/L", 0.0555),
                ConversionRule("mmol/L", "mg/dL", 18.0182)
            ]
        }
    
    def convert_value(self, value: float, from_unit: str, to_unit: str, 
                     unit_type: UnitType) -> Optional[float]:
        """Convert a value from one unit to another"""
        if from_unit == to_unit:
            return value
        
        rules = self.conversion_rules.get(unit_type, [])
        for rule in rules:
            if rule.from_unit == from_unit and rule.to_unit == to_unit:
                return rule.convert(value)
        
        logging.warning(f"No conversion rule found for {from_unit} to {to_unit}")
        return None
    
    def get_standard_unit(self, unit_type: UnitType) -> str:
        """Get the standard unit for a given unit type (for FHIR compliance)"""
        standard_units = {
            UnitType.WEIGHT: "kg",
            UnitType.HEIGHT: "cm",
            UnitType.TEMPERATURE: "C",
            UnitType.GLUCOSE: "mg/dL",
            UnitType.HEART_RATE: "bpm"
        }
        return standard_units.get(unit_type, "")

# =============================================================================
# 3. FHIR CONVERTER - Transform proprietary formats to FHIR standard
# =============================================================================

class FHIRConverter:
    def __init__(self, unit_service: UnitConversionService):
        self.unit_service = unit_service
        self.loinc_codes = self._initialize_loinc_codes()
    
    def _initialize_loinc_codes(self) -> Dict[str, str]:
        """Initialize common LOINC codes for observations"""
        return {
            "weight": "29463-7",
            "height": "8302-2",
            "temperature": "8310-5",
            "heart_rate": "8867-4",
            "blood_pressure_systolic": "8480-6",
            "blood_pressure_diastolic": "8462-4",
            "glucose": "2339-0",
            "oxygen_saturation": "2708-6"
        }
    
    def create_patient_resource(self, patient_data: Dict[str, Any]) -> Patient:
        """Convert patient data to FHIR Patient resource"""
        identifiers = []
        if patient_data.get('mrn'):
            identifiers.append(Identifier(
                system="http://hospital.example.org/mrn",
                value=patient_data['mrn']
            ))
        
        patient = Patient(
            id=str(uuid.uuid4()),
            identifier=identifiers,
            name=[{
                "given": [patient_data.get('first_name', '')],
                "family": patient_data.get('last_name', '')
            }],
            gender=patient_data.get('gender', '').lower(),
            birthDate=patient_data.get('birth_date')
        )
        
        return patient
    
    def create_observation_resource(self, obs_data: Dict[str, Any], 
                                  patient_id: str) -> Observation:
        """Convert observation data to FHIR Observation resource"""
        observation_type = obs_data.get('type', '').lower()
        loinc_code = self.loinc_codes.get(observation_type)
        
        if not loinc_code:
            raise ValueError(f"Unknown observation type: {observation_type}")
        
        # Convert units to standard if needed
        value = obs_data.get('value')
        unit = obs_data.get('unit', '')
        
        if observation_type == 'weight':
            standard_value = self.unit_service.convert_value(
                value, unit, 'kg', UnitType.WEIGHT
            )
            standard_unit = 'kg'
        elif observation_type == 'height':
            standard_value = self.unit_service.convert_value(
                value, unit, 'cm', UnitType.HEIGHT
            )
            standard_unit = 'cm'
        elif observation_type == 'temperature':
            standard_value = self.unit_service.convert_value(
                value, unit, 'C', UnitType.TEMPERATURE
            )
            standard_unit = 'C'
        else:
            standard_value = value
            standard_unit = unit
        
        observation = Observation(
            id=str(uuid.uuid4()),
            status="final",
            code=CodeableConcept(
                coding=[Coding(
                    system="http://loinc.org",
                    code=loinc_code,
                    display=observation_type.replace('_', ' ').title()
                )]
            ),
            subject={"reference": f"Patient/{patient_id}"},
            effectiveDateTime=obs_data.get('timestamp', datetime.now(timezone.utc).isoformat()),
            valueQuantity=Quantity(
                value=standard_value,
                unit=standard_unit,
                system="http://unitsofmeasure.org",
                code=standard_unit
            )
        )
        
        return observation

# =============================================================================
# 4. TRANSFORMATION ENGINE - Apache Spark for large-scale processing
# =============================================================================

class TransformationEngine:
    def __init__(self, app_name: str = "AbenaIHR-ETL"):
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        self.mapping_repo = MappingRepository()
        self.unit_service = UnitConversionService()
        self.fhir_converter = FHIRConverter(self.unit_service)
    
    def create_patient_schema(self) -> StructType:
        """Define schema for patient data"""
        return StructType([
            StructField("mrn", StringType(), True),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("gender", StringType(), True),
            StructField("birth_date", StringType(), True),
            StructField("email", StringType(), True),
            StructField("phone", StringType(), True)
        ])
    
    def create_observation_schema(self) -> StructType:
        """Define schema for observation data"""
        return StructType([
            StructField("patient_id", StringType(), False),
            StructField("type", StringType(), False),
            StructField("value", DoubleType(), False),
            StructField("unit", StringType(), True),
            StructField("timestamp", TimestampType(), False),
            StructField("source_system", StringType(), True)
        ])
    
    def clean_patient_data(self, df: DataFrame) -> DataFrame:
        """Clean and standardize patient data"""
        return df \
            .withColumn("first_name", trim(col("first_name"))) \
            .withColumn("last_name", trim(col("last_name"))) \
            .withColumn("gender", 
                       when(col("gender").isin(["M", "Male", "MALE"]), "male")
                       .when(col("gender").isin(["F", "Female", "FEMALE"]), "female")
                       .otherwise("unknown")) \
            .withColumn("phone", regexp_replace(col("phone"), "[^0-9]", "")) \
            .filter(col("mrn").isNotNull() & (col("mrn") != ""))
    
    def clean_observation_data(self, df: DataFrame) -> DataFrame:
        """Clean and standardize observation data"""
        return df \
            .withColumn("type", lower(trim(col("type")))) \
            .filter(col("value").isNotNull() & (col("value") > 0)) \
            .filter(col("patient_id").isNotNull() & (col("patient_id") != ""))
    
    def transform_emr_data(self, source_path: str, source_system: str) -> Dict[str, Any]:
        """Transform EMR data using configured mappings"""
        # Get mapping configuration
        mapping_config = self.mapping_repo.get_mapping(source_system, "FHIR")
        if not mapping_config:
            raise ValueError(f"No mapping found for {source_system} to FHIR")
        
        # Read source data
        raw_df = self.spark.read.csv(source_path, header=True, inferSchema=True)
        
        # Apply field mappings
        patient_mappings = mapping_config.get('patient_mappings', {})
        observation_mappings = mapping_config.get('observation_mappings', {})
        
        # Transform patient data
        patient_df = raw_df.select([
            col(source_field).alias(target_field) 
            for source_field, target_field in patient_mappings.items()
            if source_field in raw_df.columns
        ])
        
        patient_df = self.clean_patient_data(patient_df)
        
        # Transform observation data
        observation_df = raw_df.select([
            col(source_field).alias(target_field)
            for source_field, target_field in observation_mappings.items()
            if source_field in raw_df.columns
        ])
        
        observation_df = self.clean_observation_data(observation_df)
        
        return {
            'patients': patient_df,
            'observations': observation_df,
            'record_count': {
                'patients': patient_df.count(),
                'observations': observation_df.count()
            }
        }
    
    def convert_to_fhir(self, transformed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert transformed data to FHIR resources"""
        fhir_resources = []
        
        # Convert patients
        patients_data = transformed_data['patients'].collect()
        for patient_row in patients_data:
            patient_dict = patient_row.asDict()
            fhir_patient = self.fhir_converter.create_patient_resource(patient_dict)
            fhir_resources.append({
                'resourceType': 'Patient',
                'resource': fhir_patient.dict()
            })
        
        # Convert observations
        observations_data = transformed_data['observations'].collect()
        for obs_row in observations_data:
            obs_dict = obs_row.asDict()
            try:
                fhir_observation = self.fhir_converter.create_observation_resource(
                    obs_dict, obs_dict['patient_id']
                )
                fhir_resources.append({
                    'resourceType': 'Observation',
                    'resource': fhir_observation.dict()
                })
            except ValueError as e:
                logging.warning(f"Skipping observation: {e}")
        
        return fhir_resources
    
    def process_batch(self, source_path: str, source_system: str, 
                     output_path: str) -> Dict[str, Any]:
        """Complete ETL pipeline for batch processing"""
        def default_serializer(obj):
            import datetime as dt
            if isinstance(obj, (dt.datetime, dt.date)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        try:
            # Transform data
            transformed_data = self.transform_emr_data(source_path, source_system)
            
            # Convert to FHIR
            fhir_resources = self.convert_to_fhir(transformed_data)
            
            # Save FHIR resources
            fhir_df = self.spark.createDataFrame([
                (resource['resourceType'], json.dumps(resource['resource'], default=default_serializer))
                for resource in fhir_resources
            ], ["resourceType", "resource"])
            
            fhir_df.write.mode("overwrite").parquet(output_path)
            
            # Return processing summary
            return {
                'status': 'success',
                'records_processed': transformed_data['record_count'],
                'fhir_resources_created': len(fhir_resources),
                'output_path': output_path,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logging.error(f"ETL processing failed: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def stop(self):
        """Clean up Spark session"""
        self.spark.stop()

# =============================================================================
# 5. EXAMPLE USAGE AND CONFIGURATION
# =============================================================================

def setup_sample_mappings():
    """Set up sample mapping configurations for common EMR systems"""
    repo = MappingRepository()
    
    # Epic EMR mapping
    epic_mapping = {
        'patient_mappings': {
            'MRN': 'mrn',
            'FirstName': 'first_name',
            'LastName': 'last_name',
            'Sex': 'gender',
            'DOB': 'birth_date',
            'EmailAddress': 'email',
            'HomePhone': 'phone'
        },
        'observation_mappings': {
            'PatientMRN': 'patient_id',
            'ObservationType': 'type',
            'ObservationValue': 'value',
            'ObservationUnit': 'unit',
            'ObservationDateTime': 'timestamp',
            'SourceSystem': 'source_system'
        }
    }
    
    repo.create_mapping("Epic", "FHIR", epic_mapping, "1.0")
    
    # Cerner mapping
    cerner_mapping = {
        'patient_mappings': {
            'PERSON_ID': 'mrn',
            'NAME_FIRST': 'first_name',
            'NAME_LAST': 'last_name',
            'SEX_CD': 'gender',
            'BIRTH_DT_TM': 'birth_date',
            'EMAIL_ADDR': 'email',
            'PHONE_NBR': 'phone'
        },
        'observation_mappings': {
            'PERSON_ID': 'patient_id',
            'RESULT_TYPE': 'type',
            'RESULT_VAL': 'value',
            'RESULT_UNITS': 'unit',
            'RESULT_DT_TM': 'timestamp',
            'SOURCE': 'source_system'
        }
    }
    
    repo.create_mapping("Cerner", "FHIR", cerner_mapping, "1.0")

def main():
    """Example usage of the ETL system"""
    # Set up sample mappings
    setup_sample_mappings()
    
    # Initialize transformation engine
    engine = TransformationEngine()
    
    try:
        # Process Epic EMR data
        result = engine.process_batch(
            source_path="/data/epic_export.csv",
            source_system="Epic",
            output_path="/data/fhir_output/epic_transformed"
        )
        
        print("ETL Processing Result:")
        print(json.dumps(result, indent=2))
        
    finally:
        engine.stop()

if __name__ == "__main__":
    main()

# =============================================================================
# DEPLOYMENT CONFIGURATION
# =============================================================================

# requirements.txt content:
"""
pyspark==3.5.0
fhir.resources==7.0.2
sqlalchemy==2.0.23
redis==5.0.1
psycopg2-binary==2.9.9
"""

# docker-compose.yml for supporting services:
"""
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: abena_ihr
      POSTGRES_USER: abena_user
      POSTGRES_PASSWORD: abena_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  spark-master:
    image: bitnami/spark:3.5
    environment:
      - SPARK_MODE=master
    ports:
      - "8080:8080"
      - "7077:7077"

  spark-worker:
    image: bitnami/spark:3.5
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
    depends_on:
      - spark-master

volumes:
  postgres_data:
  redis_data:
""" 