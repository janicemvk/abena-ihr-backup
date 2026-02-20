# kafka_consumer.py - Abena IHR Kafka Consumer for Data Processing
import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid

import asyncpg
import redis.asyncio as redis
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
from cryptography.fernet import Fernet

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

class DataProcessor:
    """Processes different types of health data"""
    
    def __init__(self, db_pool, redis_client):
        self.db_pool = db_pool
        self.redis_client = redis_client
        self.cipher_suite = Fernet(os.getenv("ENCRYPTION_KEY", Fernet.generate_key()))
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_vitals(self, data: Dict[str, Any]) -> bool:
        """Process vital signs data"""
        try:
            message_id = data.get('message_id')
            if not message_id:
                message_id = str(uuid.uuid4())
            
            # Extract vital signs values
            vitals_data = {
                'message_id': message_id,
                'patient_id': data['patient_id'],
                'provider_id': data.get('provider_id'),
                'measurement_timestamp': data['timestamp'],
                'heart_rate': data.get('heart_rate'),
                'blood_pressure_systolic': data.get('blood_pressure_systolic'),
                'blood_pressure_diastolic': data.get('blood_pressure_diastolic'),
                'temperature': data.get('temperature'),
                'oxygen_saturation': data.get('oxygen_saturation'),
                'respiratory_rate': data.get('respiratory_rate'),
                'weight': data.get('weight'),
                'height': data.get('height'),
                'source_system': data.get('source_system', 'unknown')
            }
            
            # Insert into structured table
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO vital_signs (
                        message_id, patient_id, provider_id, measurement_timestamp,
                        heart_rate, blood_pressure_systolic, blood_pressure_diastolic,
                        temperature, oxygen_saturation, respiratory_rate, weight, height,
                        source_system
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    ON CONFLICT (message_id) DO UPDATE SET
                        heart_rate = EXCLUDED.heart_rate,
                        blood_pressure_systolic = EXCLUDED.blood_pressure_systolic,
                        blood_pressure_diastolic = EXCLUDED.blood_pressure_diastolic,
                        temperature = EXCLUDED.temperature,
                        oxygen_saturation = EXCLUDED.oxygen_saturation,
                        respiratory_rate = EXCLUDED.respiratory_rate,
                        weight = EXCLUDED.weight,
                        height = EXCLUDED.height,
                        updated_at = NOW()
                """, *vitals_data.values())
                
                # Update processing status
                await conn.execute("""
                    UPDATE raw_health_data 
                    SET processing_status = 'processed', processed_at = NOW()
                    WHERE message_id = $1
                """, message_id)
            
            # Calculate quality score
            quality_score = self._calculate_vitals_quality(vitals_data)
            await self._store_quality_metrics(message_id, quality_score)
            
            logger.info("Vitals processed successfully", 
                       message_id=message_id, patient_id=data['patient_id'])
            return True
            
        except Exception as e:
            logger.error("Failed to process vitals", 
                        error=str(e), message_id=message_id)
            await self._mark_processing_failed(message_id, str(e))
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_lab_results(self, data: Dict[str, Any]) -> bool:
        """Process laboratory results"""
        try:
            message_id = data.get('message_id', str(uuid.uuid4()))
            
            # Extract numeric value if possible
            numeric_value = None
            try:
                result_value = data.get('result_value', '')
                # Simple numeric extraction (can be enhanced)
                import re
                numeric_match = re.search(r'[\d.]+', str(result_value))
                if numeric_match:
                    numeric_value = float(numeric_match.group())
            except (ValueError, TypeError):
                pass
            
            lab_data = {
                'message_id': message_id,
                'patient_id': data['patient_id'],
                'provider_id': data.get('provider_id'),
                'test_name': data['test_name'],
                'test_code': data.get('test_code'),
                'result_value': data['result_value'],
                'numeric_value': numeric_value,
                'reference_range': data.get('reference_range'),
                'units': data.get('units'),
                'status': data.get('status', 'final'),
                'abnormal_flag': self._determine_abnormal_flag(numeric_value, data.get('reference_range')),
                'lab_id': data.get('lab_id'),
                'specimen_type': data.get('specimen_type'),
                'collection_timestamp': data.get('collection_timestamp'),
                'result_timestamp': data['timestamp'],
                'source_system': data.get('source_system', 'unknown')
            }
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO lab_results (
                        message_id, patient_id, provider_id, test_name, test_code,
                        result_value, numeric_value, reference_range, units, status,
                        abnormal_flag, lab_id, specimen_type, collection_timestamp,
                        result_timestamp, source_system
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    ON CONFLICT (message_id) DO UPDATE SET
                        result_value = EXCLUDED.result_value,
                        numeric_value = EXCLUDED.numeric_value,
                        status = EXCLUDED.status,
                        updated_at = NOW()
                """, *lab_data.values())
                
                await conn.execute("""
                    UPDATE raw_health_data 
                    SET processing_status = 'processed', processed_at = NOW()
                    WHERE message_id = $1
                """, message_id)
            
            quality_score = self._calculate_lab_quality(lab_data)
            await self._store_quality_metrics(message_id, quality_score)
            
            logger.info("Lab result processed successfully", 
                       message_id=message_id, test_name=data['test_name'])
            return True
            
        except Exception as e:
            logger.error("Failed to process lab result", 
                        error=str(e), message_id=message_id)
            await self._mark_processing_failed(message_id, str(e))
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_medications(self, data: Dict[str, Any]) -> bool:
        """Process medication data"""
        try:
            message_id = data.get('message_id', str(uuid.uuid4()))
            
            medication_data = {
                'message_id': message_id,
                'patient_id': data['patient_id'],
                'provider_id': data.get('provider_id'),
                'prescriber_id': data['prescriber_id'],
                'medication_name': data['medication_name'],
                'generic_name': data.get('generic_name'),
                'dosage': data['dosage'],
                'dosage_form': data.get('dosage_form'),
                'strength': data.get('strength'),
                'frequency': data['frequency'],
                'route': data.get('route'),
                'start_date': data['start_date'],
                'end_date': data.get('end_date'),
                'pharmacy_id': data.get('pharmacy_id'),
                'ndc_code': data.get('ndc_code'),
                'rxnorm_code': data.get('rxnorm_code'),
                'indication': data.get('indication'),
                'instructions': data.get('instructions'),
                'quantity_prescribed': data.get('quantity_prescribed'),
                'refills_remaining': data.get('refills_remaining'),
                'status': data.get('status', 'active'),
                'source_system': data.get('source_system', 'unknown')
            }
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO medications (
                        message_id, patient_id, provider_id, prescriber_id, medication_name,
                        generic_name, dosage, dosage_form, strength, frequency, route,
                        start_date, end_date, pharmacy_id, ndc_code, rxnorm_code,
                        indication, instructions, quantity_prescribed, refills_remaining,
                        status, source_system
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
                    ON CONFLICT (message_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        end_date = EXCLUDED.end_date,
                        updated_at = NOW()
                """, *medication_data.values())
                
                await conn.execute("""
                    UPDATE raw_health_data 
                    SET processing_status = 'processed', processed_at = NOW()
                    WHERE message_id = $1
                """, message_id)
            
            quality_score = self._calculate_medication_quality(medication_data)
            await self._store_quality_metrics(message_id, quality_score)
            
            logger.info("Medication processed successfully", 
                       message_id=message_id, medication=data['medication_name'])
            return True
            
        except Exception as e:
            logger.error("Failed to process medication", 
                        error=str(e), message_id=message_id)
            await self._mark_processing_failed(message_id, str(e))
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_hl7_message(self, data: Dict[str, Any]) -> bool:
        """Process HL7 message"""
        try:
            message_id = data.get('message_id', str(uuid.uuid4()))
            parsed_data = data.get('parsed_data', {})
            
            hl7_data = {
                'message_id': message_id,
                'message_type': data['message_type'],
                'message_control_id': data['message_control_id'],
                'sending_application': data['sending_application'],
                'receiving_application': data['receiving_application'],
                'sending_facility': parsed_data.get('MSH', {}).get('sending_facility'),
                'receiving_facility': parsed_data.get('MSH', {}).get('receiving_facility'),
                'message_timestamp': data['timestamp'],
                'patient_id': data.get('patient_id'),
                'parsed_segments': json.dumps(parsed_data),
                'processing_notes': f"Processed at {datetime.now(timezone.utc).isoformat()}",
                'source_system': data.get('source_system', 'unknown')
            }
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO hl7_messages (
                        message_id, message_type, message_control_id, sending_application,
                        receiving_application, sending_facility, receiving_facility,
                        message_timestamp, patient_id, parsed_segments, processing_notes,
                        source_system
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT (message_id) DO UPDATE SET
                        parsed_segments = EXCLUDED.parsed_segments,
                        processing_notes = EXCLUDED.processing_notes,
                        updated_at = NOW()
                """, *hl7_data.values())
                
                await conn.execute("""
                    UPDATE raw_health_data 
                    SET processing_status = 'processed', processed_at = NOW()
                    WHERE message_id = $1
                """, message_id)
            
            # Extract specific data types from HL7 message for further processing
            await self._extract_hl7_observations(message_id, parsed_data)
            
            logger.info("HL7 message processed successfully", 
                       message_id=message_id, message_type=data['message_type'])
            return True
            
        except Exception as e:
            logger.error("Failed to process HL7 message", 
                        error=str(e), message_id=message_id)
            await self._mark_processing_failed(message_id, str(e))
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_fhir_resource(self, data: Dict[str, Any]) -> bool:
        """Process FHIR resource"""
        try:
            message_id = data.get('message_id', str(uuid.uuid4()))
            parsed_data = data.get('parsed_data', {})
            
            fhir_data = {
                'message_id': message_id,
                'resource_type': data['resource_type'],
                'resource_id': data['resource_id'],
                'patient_reference': data.get('patient_reference'),
                'fhir_version': data.get('version', 'R4'),
                'resource_data': json.dumps(data['raw_resource']),
                'extracted_data': json.dumps(parsed_data),
                'validation_status': 'valid',  # Would be determined by FHIR validation
                'validation_issues': None,
                'source_system': data.get('source_system', 'unknown')
            }
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO fhir_resources (
                        message_id, resource_type, resource_id, patient_reference,
                        fhir_version, resource_data, extracted_data, validation_status,
                        validation_issues, source_system
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (message_id) DO UPDATE SET
                        resource_data = EXCLUDED.resource_data,
                        extracted_data = EXCLUDED.extracted_data,
                        validation_status = EXCLUDED.validation_status,
                        updated_at = NOW()
                """, *fhir_data.values())
                
                await conn.execute("""
                    UPDATE raw_health_data 
                    SET processing_status = 'processed', processed_at = NOW()
                    WHERE message_id = $1
                """, message_id)
            
            # Convert FHIR resources to structured data types
            await self._convert_fhir_to_structured(message_id, data)
            
            logger.info("FHIR resource processed successfully", 
                       message_id=message_id, resource_type=data['resource_type'])
            return True
            
        except Exception as e:
            logger.error("Failed to process FHIR resource", 
                        error=str(e), message_id=message_id)
            await self._mark_processing_failed(message_id, str(e))
            return False
    
    # Helper methods
    def _calculate_vitals_quality(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for vital signs"""
        completeness = 0.0
        accuracy = 1.0  # Assume accurate unless validation fails
        validity = 1.0
        
        # Count non-null vital sign fields
        vital_fields = ['heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                       'temperature', 'oxygen_saturation', 'respiratory_rate', 'weight', 'height']
        non_null_count = sum(1 for field in vital_fields if data.get(field) is not None)
        completeness = non_null_count / len(vital_fields)
        
        # Basic range validation
        if data.get('heart_rate') and not (30 <= data['heart_rate'] <= 200):
            validity -= 0.2
        if data.get('temperature') and not (95.0 <= data['temperature'] <= 105.0):
            validity -= 0.2
        if data.get('oxygen_saturation') and not (70.0 <= data['oxygen_saturation'] <= 100.0):
            validity -= 0.2
        
        overall_score = (completeness * 0.4 + accuracy * 0.3 + validity * 0.3)
        
        return {
            'completeness_score': round(completeness, 2),
            'accuracy_score': round(accuracy, 2),
            'validity_score': round(max(0.0, validity), 2),
            'overall_quality_score': round(overall_score, 2)
        }
    
    def _calculate_lab_quality(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for lab results"""
        completeness = 0.0
        accuracy = 1.0
        validity = 1.0
        
        required_fields = ['test_name', 'result_value', 'status']
        non_null_count = sum(1 for field in required_fields if data.get(field))
        completeness = non_null_count / len(required_fields)
        
        # Additional completeness for optional but important fields
        optional_fields = ['reference_range', 'units', 'test_code']
        optional_count = sum(1 for field in optional_fields if data.get(field))
        completeness += (optional_count / len(optional_fields)) * 0.3
        completeness = min(1.0, completeness)
        
        overall_score = (completeness * 0.5 + accuracy * 0.3 + validity * 0.2)
        
        return {
            'completeness_score': round(completeness, 2),
            'accuracy_score': round(accuracy, 2),
            'validity_score': round(validity, 2),
            'overall_quality_score': round(overall_score, 2)
        }
    
    def _calculate_medication_quality(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for medications"""
        completeness = 0.0
        accuracy = 1.0
        validity = 1.0
        
        required_fields = ['medication_name', 'dosage', 'frequency', 'prescriber_id']
        non_null_count = sum(1 for field in required_fields if data.get(field))
        completeness = non_null_count / len(required_fields)
        
        overall_score = (completeness * 0.6 + accuracy * 0.2 + validity * 0.2)
        
        return {
            'completeness_score': round(completeness, 2),
            'accuracy_score': round(accuracy, 2),
            'validity_score': round(validity, 2),
            'overall_quality_score': round(overall_score, 2)
        }
    
    def _determine_abnormal_flag(self, numeric_value: Optional[float], reference_range: Optional[str]) -> Optional[str]:
        """Determine if lab value is abnormal based on reference range"""
        if not numeric_value or not reference_range:
            return None
        
        try:
            # Simple parsing of reference ranges like "10-20" or "<5" or ">100"
            import re
            if '-' in reference_range:
                parts = reference_range.split('-')
                if len(parts) == 2:
                    low = float(parts[0].strip())
                    high = float(parts[1].strip())
                    if numeric_value < low:
                        return 'L'
                    elif numeric_value > high:
                        return 'H'
                    else:
                        return 'N'
            elif reference_range.startswith('<'):
                threshold = float(reference_range[1:].strip())
                return 'N' if numeric_value < threshold else 'H'
            elif reference_range.startswith('>'):
                threshold = float(reference_range[1:].strip())
                return 'N' if numeric_value > threshold else 'L'
        except (ValueError, IndexError):
            pass
        
        return None
    
    async def _extract_hl7_observations(self, message_id: str, parsed_data: Dict[str, Any]):
        """Extract observations from HL7 OBX segments and store as lab results"""
        obx_segments = parsed_data.get('OBX', [])
        if not isinstance(obx_segments, list):
            obx_segments = [obx_segments]
        
        for obx in obx_segments:
            try:
                lab_data = {
                    'message_id': f"{message_id}_obx_{obx.get('observation_id', 'unknown')}",
                    'patient_id': parsed_data.get('PID', {}).get('patient_id'),
                    'provider_id': None,
                    'test_name': obx.get('observation_id', ''),
                    'test_code': obx.get('observation_id', ''),
                    'result_value': obx.get('observation_value', ''),
                    'numeric_value': None,
                    'reference_range': obx.get('reference_range'),
                    'units': obx.get('units'),
                    'status': 'final',
                    'abnormal_flag': None,
                    'lab_id': None,
                    'specimen_type': None,
                    'collection_timestamp': None,
                    'result_timestamp': datetime.now(timezone.utc),
                    'source_system': 'hl7_extraction'
                }
                
                # Try to extract numeric value
                try:
                    import re
                    numeric_match = re.search(r'[\d.]+', str(lab_data['result_value']))
                    if numeric_match:
                        lab_data['numeric_value'] = float(numeric_match.group())
                        lab_data['abnormal_flag'] = self._determine_abnormal_flag(
                            lab_data['numeric_value'], lab_data['reference_range']
                        )
                except (ValueError, TypeError):
                    pass
                
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO lab_results (
                            message_id, patient_id, provider_id, test_name, test_code,
                            result_value, numeric_value, reference_range, units, status,
                            abnormal_flag, lab_id, specimen_type, collection_timestamp,
                            result_timestamp, source_system
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                        ON CONFLICT (message_id) DO NOTHING
                    """, *lab_data.values())
                
            except Exception as e:
                logger.warning("Failed to extract HL7 observation", 
                              error=str(e), message_id=message_id)
    
    async def _convert_fhir_to_structured(self, message_id: str, data: Dict[str, Any]):
        """Convert FHIR resources to structured data tables"""
        resource_type = data.get('resource_type')
        raw_resource = data.get('raw_resource', {})
        patient_ref = data.get('patient_reference')
        
        try:
            if resource_type == 'Observation':
                await self._convert_fhir_observation(message_id, raw_resource, patient_ref)
            elif resource_type == 'MedicationRequest':
                await self._convert_fhir_medication(message_id, raw_resource, patient_ref)
            # Add more resource type conversions as needed
                
        except Exception as e:
            logger.warning("Failed to convert FHIR resource", 
                          error=str(e), resource_type=resource_type)
    
    async def _convert_fhir_observation(self, message_id: str, observation: Dict[str, Any], patient_ref: str):
        """Convert FHIR Observation to lab result"""
        try:
            code = observation.get('code', {})
            value = observation.get('valueQuantity', {})
            
            lab_data = {
                'message_id': f"{message_id}_fhir_obs",
                'patient_id': patient_ref,
                'provider_id': None,
                'test_name': code.get('text', ''),
                'test_code': code.get('coding', [{}])[0].get('code', '') if code.get('coding') else '',
                'result_value': str(value.get('value', '')),
                'numeric_value': value.get('value') if isinstance(value.get('value'), (int, float)) else None,
                'reference_range': None,  # Would need to parse from referenceRange
                'units': value.get('unit', ''),
                'status': observation.get('status', 'final'),
                'abnormal_flag': None,
                'lab_id': None,
                'specimen_type': None,
                'collection_timestamp': observation.get('effectiveDateTime'),
                'result_timestamp': datetime.now(timezone.utc),
                'source_system': 'fhir_conversion'
            }
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO lab_results (
                        message_id, patient_id, provider_id, test_name, test_code,
                        result_value, numeric_value, reference_range, units, status,
                        abnormal_flag, lab_id, specimen_type, collection_timestamp,
                        result_timestamp, source_system
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    ON CONFLICT (message_id) DO NOTHING
                """, *lab_data.values())
                
        except Exception as e:
            logger.warning("Failed to convert FHIR observation", error=str(e))
    
    async def _convert_fhir_medication(self, message_id: str, medication_request: Dict[str, Any], patient_ref: str):
        """Convert FHIR MedicationRequest to medication record"""
        try:
            medication = medication_request.get('medicationCodeableConcept', {})
            dosage = medication_request.get('dosageInstruction', [{}])[0] if medication_request.get('dosageInstruction') else {}
            
            med_data = {
                'message_id': f"{message_id}_fhir_med",
                'patient_id': patient_ref,
                'provider_id': None,
                'prescriber_id': medication_request.get('requester', {}).get('reference', '').replace('Practitioner/', ''),
                'medication_name': medication.get('text', ''),
                'generic_name': None,
                'dosage': dosage.get('text', ''),
                'dosage_form': None,
                'strength': None,
                'frequency': dosage.get('timing', {}).get('code', {}).get('text', ''),
                'route': dosage.get('route', {}).get('text', ''),
                'start_date': medication_request.get('authoredOn'),
                'end_date': None,
                'pharmacy_id': None,
                'ndc_code': None,
                'rxnorm_code': medication.get('coding', [{}])[0].get('code', '') if medication.get('coding') else None,
                'indication': None,
                'instructions': dosage.get('patientInstruction', ''),
                'quantity_prescribed': None,
                'refills_remaining': None,
                'status': medication_request.get('status', 'active'),
                'source_system': 'fhir_conversion'
            }
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO medications (
                        message_id, patient_id, provider_id, prescriber_id, medication_name,
                        generic_name, dosage, dosage_form, strength, frequency, route,
                        start_date, end_date, pharmacy_id, ndc_code, rxnorm_code,
                        indication, instructions, quantity_prescribed, refills_remaining,
                        status, source_system
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
                    ON CONFLICT (message_id) DO NOTHING
                """, *med_data.values())
                
        except Exception as e:
            logger.warning("Failed to convert FHIR medication", error=str(e))
    
    async def _store_quality_metrics(self, message_id: str, quality_scores: Dict[str, float]):
        """Store data quality metrics"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO data_quality_metrics (
                        message_id, completeness_score, accuracy_score, 
                        consistency_score, timeliness_score, validity_score,
                        overall_quality_score
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (message_id) DO UPDATE SET
                        completeness_score = EXCLUDED.completeness_score,
                        accuracy_score = EXCLUDED.accuracy_score,
                        validity_score = EXCLUDED.validity_score,
                        overall_quality_score = EXCLUDED.overall_quality_score,
                        assessment_timestamp = NOW()
                """, 
                message_id,
                quality_scores.get('completeness_score'),
                quality_scores.get('accuracy_score'),
                quality_scores.get('consistency_score', 1.0),
                quality_scores.get('timeliness_score', 1.0),
                quality_scores.get('validity_score'),
                quality_scores.get('overall_quality_score')
                )
        except Exception as e:
            logger.warning("Failed to store quality metrics", error=str(e))
    
    async def _mark_processing_failed(self, message_id: str, error_message: str):
        """Mark message processing as failed"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE raw_health_data 
                    SET processing_status = 'failed', 
                        error_details = $2,
                        retry_count = retry_count + 1,
                        last_retry_at = NOW()
                    WHERE message_id = $1
                """, message_id, error_message)
        except Exception as e:
            logger.error("Failed to mark processing as failed", error=str(e))


class KafkaDataConsumer:
    """Main Kafka consumer for health data processing"""
    
    def __init__(self):
        self.db_pool = None
        self.redis_client = None
        self.processor = None
        self.consumers = {}
        self.running = False
    
    async def initialize(self):
        """Initialize database and Redis connections"""
        # Database connection
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/abena_ihr_data")
        self.db_pool = await asyncpg.create_pool(database_url, min_size=5, max_size=20)
        
        # Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url)
        
        # Initialize processor
        self.processor = DataProcessor(self.db_pool, self.redis_client)
        
        logger.info("Kafka consumer initialized")
    
    def create_consumer(self, topic: str, group_id: str) -> KafkaConsumer:
        """Create Kafka consumer for specific topic"""
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(',')
        
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=1000
        )
        
        return consumer
    
    async def consume_vitals(self):
        """Consume vital signs data"""
        consumer = self.create_consumer('health-data-vitals', 'vitals-processor')
        
        while self.running:
            try:
                for message in consumer:
                    if not self.running:
                        break
                    
                    data = message.value
                    await self.processor.process_vitals(data)
                    
            except Exception as e:
                logger.error("Error in vitals consumer", error=str(e))
                await asyncio.sleep(5)
        
        consumer.close()
    
    async def consume_lab_results(self):
        """Consume lab results data"""
        consumer = self.create_consumer('health-data-labs', 'labs-processor')
        
        while self.running:
            try:
                for message in consumer:
                    if not self.running:
                        break
                    
                    data = message.value
                    await self.processor.process_lab_results(data)
                    
            except Exception as e:
                logger.error("Error in labs consumer", error=str(e))
                await asyncio.sleep(5)
        
        consumer.close()
    
    async def consume_medications(self):
        """Consume medication data"""
        consumer = self.create_consumer('health-data-medications', 'medications-processor')
        
        while self.running:
            try:
                for message in consumer:
                    if not self.running:
                        break
                    
                    data = message.value
                    await self.processor.process_medications(data)
                    
            except Exception as e:
                logger.error("Error in medications consumer", error=str(e))
                await asyncio.sleep(5)
        
        consumer.close()
    
    async def consume_hl7(self):
        """Consume HL7 messages"""
        consumer = self.create_consumer('health-data-hl7', 'hl7-processor')
        
        while self.running:
            try:
                for message in consumer:
                    if not self.running:
                        break
                    
                    data = message.value
                    await self.processor.process_hl7_message(data)
                    
            except Exception as e:
                logger.error("Error in HL7 consumer", error=str(e))
                await asyncio.sleep(5)
        
        consumer.close()
    
    async def consume_fhir(self):
        """Consume FHIR resources"""
        consumer = self.create_consumer('health-data-fhir', 'fhir-processor')
        
        while self.running:
            try:
                for message in consumer:
                    if not self.running:
                        break
                    
                    data = message.value
                    await self.processor.process_fhir_resource(data)
                    
            except Exception as e:
                logger.error("Error in FHIR consumer", error=str(e))
                await asyncio.sleep(5)
        
        consumer.close()
    
    async def start(self):
        """Start all consumers"""
        self.running = True
        
        # Start consumer tasks
        tasks = [
            asyncio.create_task(self.consume_vitals()),
            asyncio.create_task(self.consume_lab_results()),
            asyncio.create_task(self.consume_medications()),
            asyncio.create_task(self.consume_hl7()),
            asyncio.create_task(self.consume_fhir())
        ]
        
        logger.info("All Kafka consumers started")
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop all consumers"""
        self.running = False
        
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Kafka consumer stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


async def main():
    """Main function"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start consumer
    consumer = KafkaDataConsumer()
    await consumer.initialize()
    await consumer.start()


if __name__ == "__main__":
    asyncio.run(main()) 