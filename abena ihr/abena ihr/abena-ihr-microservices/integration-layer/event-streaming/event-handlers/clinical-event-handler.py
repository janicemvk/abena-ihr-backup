#!/usr/bin/env python3
"""
Clinical Event Handler for Abena IHR
Handles processing, validation, and routing of clinical events
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

import aioredis
import asyncpg
from confluent_kafka import Consumer, Producer, KafkaError
from pydantic import BaseModel, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClinicalEvent(BaseModel):
    """Base model for clinical events"""
    event_id: str
    event_type: str
    patient_id: str
    provider_id: str
    timestamp: datetime
    metadata: Dict[str, Any]

class ClinicalEncounterEvent(ClinicalEvent):
    """Clinical encounter event model"""
    encounter_id: str
    location: Optional[str] = None
    event_data: Dict[str, Any]

class ClinicalAlertEvent(ClinicalEvent):
    """Clinical alert event model"""
    alert_id: str
    alert_type: str
    severity: str
    alert_message: str
    alert_data: Dict[str, Any]
    status: str

class ClinicalDecisionEvent(ClinicalEvent):
    """Clinical decision event model"""
    decision_id: str
    decision_type: str
    encounter_id: Optional[str] = None
    confidence_score: float
    decision_data: Dict[str, Any]
    accepted: Optional[bool] = None
    reasoning: Optional[str] = None

class ClinicalEventHandler:
    """Handler for clinical events"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis = None
        self.db_pool = None
        self.consumer = None
        self.producer = None
        self.running = False
        
        # Event type handlers
        self.event_handlers = {
            'ENCOUNTER_STARTED': self.handle_encounter_started,
            'ENCOUNTER_COMPLETED': self.handle_encounter_completed,
            'ENCOUNTER_CANCELLED': self.handle_encounter_cancelled,
            'VITALS_RECORDED': self.handle_vitals_recorded,
            'DIAGNOSIS_ADDED': self.handle_diagnosis_added,
            'MEDICATION_PRESCRIBED': self.handle_medication_prescribed,
            'LAB_ORDERED': self.handle_lab_ordered,
            'PROCEDURE_SCHEDULED': self.handle_procedure_scheduled,
            'CRITICAL_VITAL': self.handle_critical_vital,
            'DRUG_INTERACTION': self.handle_drug_interaction,
            'ALLERGY_ALERT': self.handle_allergy_alert,
            'ABNORMAL_LAB': self.handle_abnormal_lab,
            'MEDICATION_DUE': self.handle_medication_due,
            'FOLLOW_UP_REQUIRED': self.handle_follow_up_required,
            'EMERGENCY_ALERT': self.handle_emergency_alert,
            'DIAGNOSIS_SUGGESTION': self.handle_diagnosis_suggestion,
            'TREATMENT_RECOMMENDATION': self.handle_treatment_recommendation,
            'MEDICATION_SUGGESTION': self.handle_medication_suggestion,
            'TEST_RECOMMENDATION': self.handle_test_recommendation,
            'REFERRAL_SUGGESTION': self.handle_referral_suggestion,
            'RISK_ASSESSMENT': self.handle_risk_assessment
        }

    async def initialize(self):
        """Initialize connections and resources"""
        try:
            # Initialize Redis connection
            self.redis = await aioredis.from_url(
                self.config['redis_url'],
                encoding='utf-8',
                decode_responses=True
            )
            
            # Initialize database connection pool
            self.db_pool = await asyncpg.create_pool(
                self.config['database_url'],
                min_size=5,
                max_size=20
            )
            
            # Initialize Kafka consumer
            self.consumer = Consumer({
                'bootstrap.servers': self.config['kafka_bootstrap_servers'],
                'group.id': 'clinical-event-handler',
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False
            })
            self.consumer.subscribe(['clinical.decision.events', 'clinical.alerts'])
            
            # Initialize Kafka producer
            self.producer = Producer({
                'bootstrap.servers': self.config['kafka_bootstrap_servers'],
                'client.id': 'clinical-event-handler-producer'
            })
            
            logger.info("Clinical event handler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize clinical event handler: {e}")
            raise

    async def start(self):
        """Start processing events"""
        self.running = True
        logger.info("Starting clinical event handler")
        
        try:
            while self.running:
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    continue
                    
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        continue
                
                await self.process_event(msg)
                
        except KeyboardInterrupt:
            logger.info("Shutting down clinical event handler")
        except Exception as e:
            logger.error(f"Error in event processing loop: {e}")
        finally:
            await self.cleanup()

    async def process_event(self, msg):
        """Process a single event"""
        try:
            # Parse event data
            event_data = json.loads(msg.value().decode('utf-8'))
            event_type = event_data.get('event_type')
            
            logger.info(f"Processing event: {event_type}")
            
            # Validate event data
            event = await self.validate_event(event_data)
            if not event:
                logger.warning(f"Invalid event data: {event_data}")
                return
            
            # Route to appropriate handler
            handler = self.event_handlers.get(event_type)
            if handler:
                await handler(event)
            else:
                logger.warning(f"No handler found for event type: {event_type}")
            
            # Commit offset
            self.consumer.commit(msg)
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            # Send to dead letter queue
            await self.send_to_dlq(msg.value(), str(e))

    async def validate_event(self, event_data: Dict[str, Any]) -> Optional[ClinicalEvent]:
        """Validate event data"""
        try:
            event_type = event_data.get('event_type')
            
            if 'ENCOUNTER' in event_type:
                return ClinicalEncounterEvent(**event_data)
            elif 'ALERT' in event_type:
                return ClinicalAlertEvent(**event_data)
            elif 'DECISION' in event_type or 'SUGGESTION' in event_type or 'RECOMMENDATION' in event_type:
                return ClinicalDecisionEvent(**event_data)
            else:
                return ClinicalEvent(**event_data)
                
        except ValidationError as e:
            logger.error(f"Event validation error: {e}")
            return None

    # Encounter event handlers
    async def handle_encounter_started(self, event: ClinicalEncounterEvent):
        """Handle encounter started event"""
        try:
            # Update encounter status in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE encounters 
                    SET status = 'IN_PROGRESS', 
                        started_at = $1,
                        updated_at = $2
                    WHERE encounter_id = $3
                """, event.timestamp, datetime.utcnow(), event.encounter_id)
            
            # Send notification to provider
            await self.send_provider_notification(
                event.provider_id,
                f"Encounter started for patient {event.patient_id}"
            )
            
            # Publish to analytics topic
            await self.publish_analytics_event(event)
            
            logger.info(f"Encounter started: {event.encounter_id}")
            
        except Exception as e:
            logger.error(f"Error handling encounter started: {e}")

    async def handle_encounter_completed(self, event: ClinicalEncounterEvent):
        """Handle encounter completed event"""
        try:
            # Update encounter status in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE encounters 
                    SET status = 'COMPLETED', 
                        completed_at = $1,
                        updated_at = $2
                    WHERE encounter_id = $3
                """, event.timestamp, datetime.utcnow(), event.encounter_id)
            
            # Trigger follow-up scheduling if needed
            await self.check_follow_up_needed(event)
            
            # Publish to analytics topic
            await self.publish_analytics_event(event)
            
            logger.info(f"Encounter completed: {event.encounter_id}")
            
        except Exception as e:
            logger.error(f"Error handling encounter completed: {e}")

    async def handle_vitals_recorded(self, event: ClinicalEncounterEvent):
        """Handle vitals recorded event"""
        try:
            vitals_data = event.event_data.get('vitals')
            if not vitals_data:
                return
            
            # Store vitals in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO patient_vitals (
                        vital_id, patient_id, encounter_id, timestamp,
                        blood_pressure_systolic, blood_pressure_diastolic,
                        heart_rate, temperature, respiratory_rate,
                        oxygen_saturation, weight, height, source, provider_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """, 
                vitals_data.get('vital_id'), event.patient_id, event.encounter_id,
                event.timestamp, vitals_data.get('blood_pressure', {}).get('systolic'),
                vitals_data.get('blood_pressure', {}).get('diastolic'),
                vitals_data.get('heart_rate', {}).get('value'),
                vitals_data.get('temperature', {}).get('value'),
                vitals_data.get('respiratory_rate', {}).get('value'),
                vitals_data.get('oxygen_saturation', {}).get('value'),
                vitals_data.get('weight', {}).get('value'),
                vitals_data.get('height', {}).get('value'),
                vitals_data.get('source'), event.provider_id)
            
            # Check for critical vitals
            await self.check_critical_vitals(event.patient_id, vitals_data)
            
            # Publish to analytics topic
            await self.publish_analytics_event(event)
            
            logger.info(f"Vitals recorded for patient: {event.patient_id}")
            
        except Exception as e:
            logger.error(f"Error handling vitals recorded: {e}")

    # Alert event handlers
    async def handle_critical_vital(self, event: ClinicalAlertEvent):
        """Handle critical vital alert"""
        try:
            # Send immediate notification to provider
            await self.send_urgent_notification(
                event.provider_id,
                f"CRITICAL: {event.alert_message}",
                priority='high'
            )
            
            # Log alert in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO clinical_alerts (
                        alert_id, patient_id, provider_id, alert_type,
                        severity, alert_message, alert_data, status,
                        triggered_at, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, event.alert_id, event.patient_id, event.provider_id,
                event.alert_type, event.severity, event.alert_message,
                json.dumps(event.alert_data), event.status,
                event.triggered_at, datetime.utcnow())
            
            # Escalate if critical
            if event.severity == 'CRITICAL':
                await self.escalate_alert(event)
            
            logger.info(f"Critical vital alert: {event.alert_id}")
            
        except Exception as e:
            logger.error(f"Error handling critical vital alert: {e}")

    async def handle_drug_interaction(self, event: ClinicalAlertEvent):
        """Handle drug interaction alert"""
        try:
            # Send notification to provider
            await self.send_provider_notification(
                event.provider_id,
                f"DRUG INTERACTION: {event.alert_message}"
            )
            
            # Log alert in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO clinical_alerts (
                        alert_id, patient_id, provider_id, alert_type,
                        severity, alert_message, alert_data, status,
                        triggered_at, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, event.alert_id, event.patient_id, event.provider_id,
                event.alert_type, event.severity, event.alert_message,
                json.dumps(event.alert_data), event.status,
                event.triggered_at, datetime.utcnow())
            
            logger.info(f"Drug interaction alert: {event.alert_id}")
            
        except Exception as e:
            logger.error(f"Error handling drug interaction alert: {e}")

    # Decision event handlers
    async def handle_diagnosis_suggestion(self, event: ClinicalDecisionEvent):
        """Handle diagnosis suggestion"""
        try:
            # Store decision in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO clinical_decisions (
                        decision_id, patient_id, provider_id, encounter_id,
                        decision_type, confidence_score, decision_data,
                        accepted, reasoning, triggered_at, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, event.decision_id, event.patient_id, event.provider_id,
                event.encounter_id, event.decision_type, event.confidence_score,
                json.dumps(event.decision_data), event.accepted, event.reasoning,
                event.triggered_at, datetime.utcnow())
            
            # Send suggestion to provider
            await self.send_decision_suggestion(event)
            
            logger.info(f"Diagnosis suggestion: {event.decision_id}")
            
        except Exception as e:
            logger.error(f"Error handling diagnosis suggestion: {e}")

    # Helper methods
    async def send_provider_notification(self, provider_id: str, message: str):
        """Send notification to provider"""
        notification = {
            'notification_id': str(uuid.uuid4()),
            'provider_id': provider_id,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'CLINICAL_ALERT'
        }
        
        self.producer.produce(
            'provider.notifications',
            json.dumps(notification).encode('utf-8'),
            callback=self.delivery_report
        )
        self.producer.flush()

    async def send_urgent_notification(self, provider_id: str, message: str, priority: str = 'normal'):
        """Send urgent notification to provider"""
        notification = {
            'notification_id': str(uuid.uuid4()),
            'provider_id': provider_id,
            'message': message,
            'priority': priority,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'URGENT_ALERT'
        }
        
        self.producer.produce(
            'provider.notifications',
            json.dumps(notification).encode('utf-8'),
            callback=self.delivery_report
        )
        self.producer.flush()

    async def publish_analytics_event(self, event: ClinicalEvent):
        """Publish event to analytics topic"""
        analytics_event = {
            'event_id': str(uuid.uuid4()),
            'source_event_id': event.event_id,
            'event_type': event.event_type,
            'patient_id': event.patient_id,
            'provider_id': event.provider_id,
            'timestamp': event.timestamp.isoformat(),
            'data': event.dict()
        }
        
        self.producer.produce(
            'analytics.health.metrics',
            json.dumps(analytics_event).encode('utf-8'),
            callback=self.delivery_report
        )
        self.producer.flush()

    async def send_to_dlq(self, message: bytes, error: str):
        """Send failed message to dead letter queue"""
        dlq_message = {
            'original_message': message.decode('utf-8'),
            'error': error,
            'timestamp': datetime.utcnow().isoformat(),
            'handler': 'clinical-event-handler'
        }
        
        self.producer.produce(
            'dlq.processing.errors',
            json.dumps(dlq_message).encode('utf-8'),
            callback=self.delivery_report
        )
        self.producer.flush()

    def delivery_report(self, err, msg):
        """Kafka delivery report callback"""
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    async def cleanup(self):
        """Cleanup resources"""
        self.running = False
        
        if self.consumer:
            self.consumer.close()
        
        if self.producer:
            self.producer.flush()
        
        if self.redis:
            await self.redis.close()
        
        if self.db_pool:
            await self.db_pool.close()
        
        logger.info("Clinical event handler cleanup completed")

# Main execution
async def main():
    """Main function"""
    config = {
        'redis_url': 'redis://localhost:6379',
        'database_url': 'postgresql://user:password@localhost/abena_ihr',
        'kafka_bootstrap_servers': 'localhost:9092'
    }
    
    handler = ClinicalEventHandler(config)
    await handler.initialize()
    await handler.start()

if __name__ == "__main__":
    asyncio.run(main()) 