"""
Alert Generator for Abena IHR
============================

This module provides clinical alert and warning capabilities including:
- Clinical alerts and warnings
- Medication safety alerts
- Lab result alerts
- Vital sign alerts
- Care coordination alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import redis
import httpx
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertCategory(Enum):
    MEDICATION = "medication"
    LAB_RESULT = "lab_result"
    VITAL_SIGN = "vital_sign"
    CLINICAL = "clinical"
    SAFETY = "safety"
    CARE_COORDINATION = "care_coordination"
    SYSTEM = "system"

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Pydantic models
class AlertRule(BaseModel):
    """Alert rule model"""
    rule_id: str
    name: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    priority: AlertPriority
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class ClinicalAlert(BaseModel):
    """Clinical alert model"""
    alert_id: str
    patient_id: str
    rule_id: str
    category: AlertCategory
    severity: AlertSeverity
    priority: AlertPriority
    title: str
    message: str
    details: Dict[str, Any]
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    escalation_level: int = 0
    metadata: Dict[str, Any] = {}

class AlertRequest(BaseModel):
    """Request model for alert generation"""
    patient_id: str
    patient_data: Dict[str, Any]
    alert_categories: List[AlertCategory] = []
    include_acknowledged: bool = False
    include_resolved: bool = False
    max_alerts: int = 50

class AlertResponse(BaseModel):
    """Alert response model"""
    patient_id: str
    generated_alerts: List[ClinicalAlert]
    active_alerts: List[ClinicalAlert]
    total_alerts: int
    critical_alerts: int
    timestamp: datetime

class AlertAcknowledgment(BaseModel):
    """Alert acknowledgment model"""
    alert_id: str
    acknowledged_by: str
    acknowledgment_note: Optional[str] = None

class AlertResolution(BaseModel):
    """Alert resolution model"""
    alert_id: str
    resolved_by: str
    resolution_note: Optional[str] = None
    resolution_action: str

class AlertGenerator:
    """Clinical alert generation engine"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = {}
        
    async def load_alert_rules(self):
        """Load alert rules from storage"""
        try:
            # Load rules from Redis or database
            rule_keys = self.redis_client.keys("alert_rule:*")
            for key in rule_keys:
                rule_data = self.redis_client.get(key)
                if rule_data:
                    rule_dict = json.loads(rule_data)
                    rule = AlertRule(**rule_dict)
                    self.alert_rules[rule.rule_id] = rule
                    
            logger.info(f"Loaded {len(self.alert_rules)} alert rules")
            
        except Exception as e:
            logger.error(f"Error loading alert rules: {e}")
            # Load default rules if Redis is not available
            self._load_default_alert_rules()
            
    def generate_alerts(self, request: AlertRequest) -> AlertResponse:
        """Generate clinical alerts for patient"""
        try:
            patient_data = request.patient_data
            
            # Generate new alerts
            generated_alerts = []
            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue
                    
                if request.alert_categories and rule.category not in request.alert_categories:
                    continue
                    
                if self._evaluate_alert_rule(rule, patient_data):
                    alert = self._create_alert(rule, request.patient_id, patient_data)
                    generated_alerts.append(alert)
                    
                    # Store alert
                    self.active_alerts[alert.alert_id] = alert
                    
            # Get existing active alerts
            active_alerts = self._get_active_alerts(request.patient_id, request.include_acknowledged, request.include_resolved)
            
            # Limit results
            if request.max_alerts:
                generated_alerts = generated_alerts[:request.max_alerts]
                active_alerts = active_alerts[:request.max_alerts]
                
            # Count critical alerts
            critical_alerts = len([alert for alert in active_alerts if alert.severity == AlertSeverity.CRITICAL])
            
            return AlertResponse(
                patient_id=request.patient_id,
                generated_alerts=generated_alerts,
                active_alerts=active_alerts,
                total_alerts=len(active_alerts),
                critical_alerts=critical_alerts,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            raise
            
    def acknowledge_alert(self, acknowledgment: AlertAcknowledgment):
        """Acknowledge an alert"""
        try:
            if acknowledgment.alert_id in self.active_alerts:
                alert = self.active_alerts[acknowledgment.alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = acknowledgment.acknowledged_by
                
                # Store in Redis
                alert_key = f"alert:{alert.alert_id}"
                self.redis_client.setex(
                    alert_key,
                    86400,  # 24 hours TTL
                    json.dumps(alert.dict())
                )
                
                logger.info(f"Alert {alert.alert_id} acknowledged by {acknowledgment.acknowledged_by}")
                
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            raise
            
    def resolve_alert(self, resolution: AlertResolution):
        """Resolve an alert"""
        try:
            if resolution.alert_id in self.active_alerts:
                alert = self.active_alerts[resolution.alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                alert.resolved_by = resolution.resolved_by
                
                # Move to history
                self.alert_history[alert.alert_id] = alert
                del self.active_alerts[alert.alert_id]
                
                # Store in Redis
                alert_key = f"alert_history:{alert.alert_id}"
                self.redis_client.setex(
                    alert_key,
                    604800,  # 7 days TTL
                    json.dumps(alert.dict())
                )
                
                logger.info(f"Alert {alert.alert_id} resolved by {resolution.resolved_by}")
                
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            raise
            
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        try:
            self.alert_rules[rule.rule_id] = rule
            
            # Store in Redis
            rule_key = f"alert_rule:{rule.rule_id}"
            self.redis_client.setex(
                rule_key,
                86400,  # 24 hours TTL
                json.dumps(rule.dict())
            )
            
            logger.info(f"Added alert rule: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error adding alert rule: {e}")
            raise
            
    def _evaluate_alert_rule(self, rule: AlertRule, patient_data: Dict[str, Any]) -> bool:
        """Evaluate if an alert rule should trigger"""
        try:
            for condition in rule.conditions:
                if not self._evaluate_condition(condition, patient_data):
                    return False
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating alert rule: {e}")
            return False
            
    def _evaluate_condition(self, condition: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        try:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if field not in patient_data:
                return False
                
            patient_value = patient_data[field]
            
            # Apply operator
            if operator == 'equals':
                return patient_value == value
            elif operator == 'not_equals':
                return patient_value != value
            elif operator == 'greater_than':
                return patient_value > value
            elif operator == 'less_than':
                return patient_value < value
            elif operator == 'greater_than_or_equal':
                return patient_value >= value
            elif operator == 'less_than_or_equal':
                return patient_value <= value
            elif operator == 'in':
                return patient_value in value
            elif operator == 'not_in':
                return patient_value not in value
            elif operator == 'contains':
                return value in patient_value
            elif operator == 'not_contains':
                return value not in patient_value
            elif operator == 'exists':
                return field in patient_data
            elif operator == 'not_exists':
                return field not in patient_data
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
            
    def _create_alert(self, rule: AlertRule, patient_id: str, patient_data: Dict[str, Any]) -> ClinicalAlert:
        """Create a clinical alert from a rule"""
        try:
            alert_id = f"alert_{datetime.now().timestamp()}_{rule.rule_id}"
            
            # Generate alert details
            details = self._generate_alert_details(rule, patient_data)
            
            # Create alert
            alert = ClinicalAlert(
                alert_id=alert_id,
                patient_id=patient_id,
                rule_id=rule.rule_id,
                category=rule.category,
                severity=rule.severity,
                priority=rule.priority,
                title=rule.name,
                message=rule.description,
                details=details,
                created_at=datetime.now(),
                metadata=rule.metadata
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
            
    def _generate_alert_details(self, rule: AlertRule, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed information for an alert"""
        details = {
            'rule_id': rule.rule_id,
            'category': rule.category.value,
            'severity': rule.severity.value,
            'priority': rule.priority.value,
            'triggered_conditions': [],
            'patient_context': {},
            'recommended_actions': rule.actions
        }
        
        # Add triggered conditions
        for condition in rule.conditions:
            if self._evaluate_condition(condition, patient_data):
                details['triggered_conditions'].append({
                    'field': condition.get('field'),
                    'operator': condition.get('operator'),
                    'value': condition.get('value'),
                    'description': condition.get('description', 'Unknown condition')
                })
                
        # Add relevant patient context
        for condition in rule.conditions:
            field = condition.get('field')
            if field in patient_data:
                details['patient_context'][field] = patient_data[field]
                
        return details
        
    def _get_active_alerts(self, patient_id: str, include_acknowledged: bool, include_resolved: bool) -> List[ClinicalAlert]:
        """Get active alerts for a patient"""
        alerts = []
        
        for alert in self.active_alerts.values():
            if alert.patient_id == patient_id:
                if alert.status == AlertStatus.ACTIVE:
                    alerts.append(alert)
                elif alert.status == AlertStatus.ACKNOWLEDGED and include_acknowledged:
                    alerts.append(alert)
                elif alert.status == AlertStatus.RESOLVED and include_resolved:
                    alerts.append(alert)
                    
        # Sort by priority and creation time
        alerts.sort(key=lambda x: (x.priority.value, x.created_at), reverse=True)
        
        return alerts
        
    def _load_default_alert_rules(self):
        """Load default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="rule_001",
                name="Critical Blood Pressure",
                description="Systolic blood pressure is critically high",
                category=AlertCategory.VITAL_SIGN,
                severity=AlertSeverity.CRITICAL,
                priority=AlertPriority.URGENT,
                conditions=[
                    {
                        "field": "blood_pressure_systolic",
                        "operator": "greater_than",
                        "value": 180,
                        "description": "Systolic BP > 180 mmHg"
                    }
                ],
                actions=[
                    {
                        "action": "immediate_assessment",
                        "description": "Immediate clinical assessment required"
                    },
                    {
                        "action": "medication_review",
                        "description": "Review antihypertensive medications"
                    }
                ],
                enabled=True,
                effective_date=datetime.now(),
                tags=["hypertension", "vital_signs", "critical"]
            ),
            AlertRule(
                rule_id="rule_002",
                name="Elevated Glucose",
                description="Blood glucose level is elevated",
                category=AlertCategory.LAB_RESULT,
                severity=AlertSeverity.WARNING,
                priority=AlertPriority.HIGH,
                conditions=[
                    {
                        "field": "glucose",
                        "operator": "greater_than",
                        "value": 200,
                        "description": "Glucose > 200 mg/dL"
                    }
                ],
                actions=[
                    {
                        "action": "diabetes_management",
                        "description": "Review diabetes management plan"
                    },
                    {
                        "action": "lifestyle_counseling",
                        "description": "Provide lifestyle modification counseling"
                    }
                ],
                enabled=True,
                effective_date=datetime.now(),
                tags=["diabetes", "glucose", "metabolic"]
            ),
            AlertRule(
                rule_id="rule_003",
                name="Polypharmacy Alert",
                description="Patient is taking multiple medications",
                category=AlertCategory.MEDICATION,
                severity=AlertSeverity.WARNING,
                priority=AlertPriority.MEDIUM,
                conditions=[
                    {
                        "field": "medication_count",
                        "operator": "greater_than",
                        "value": 5,
                        "description": "More than 5 medications"
                    }
                ],
                actions=[
                    {
                        "action": "medication_review",
                        "description": "Comprehensive medication review"
                    },
                    {
                        "action": "interaction_check",
                        "description": "Check for drug interactions"
                    }
                ],
                enabled=True,
                effective_date=datetime.now(),
                tags=["medication", "polypharmacy", "safety"]
            ),
            AlertRule(
                rule_id="rule_004",
                name="Low Heart Rate",
                description="Heart rate is below normal range",
                category=AlertCategory.VITAL_SIGN,
                severity=AlertSeverity.WARNING,
                priority=AlertPriority.HIGH,
                conditions=[
                    {
                        "field": "heart_rate",
                        "operator": "less_than",
                        "value": 50,
                        "description": "Heart rate < 50 bpm"
                    }
                ],
                actions=[
                    {
                        "action": "cardiac_assessment",
                        "description": "Cardiac assessment and monitoring"
                    },
                    {
                        "action": "medication_review",
                        "description": "Review medications that may cause bradycardia"
                    }
                ],
                enabled=True,
                effective_date=datetime.now(),
                tags=["cardiac", "vital_signs", "bradycardia"]
            ),
            AlertRule(
                rule_id="rule_005",
                name="High Temperature",
                description="Patient has elevated body temperature",
                category=AlertCategory.VITAL_SIGN,
                severity=AlertSeverity.WARNING,
                priority=AlertPriority.HIGH,
                conditions=[
                    {
                        "field": "temperature",
                        "operator": "greater_than",
                        "value": 38.0,
                        "description": "Temperature > 38.0°C"
                    }
                ],
                actions=[
                    {
                        "action": "infection_assessment",
                        "description": "Assess for infection or fever"
                    },
                    {
                        "action": "symptom_monitoring",
                        "description": "Monitor for additional symptoms"
                    }
                ],
                enabled=True,
                effective_date=datetime.now(),
                tags=["infection", "fever", "vital_signs"]
            ),
            AlertRule(
                rule_id="rule_006",
                name="Low Oxygen Saturation",
                description="Oxygen saturation is below normal",
                category=AlertCategory.VITAL_SIGN,
                severity=AlertSeverity.CRITICAL,
                priority=AlertPriority.URGENT,
                conditions=[
                    {
                        "field": "oxygen_saturation",
                        "operator": "less_than",
                        "value": 90,
                        "description": "Oxygen saturation < 90%"
                    }
                ],
                actions=[
                    {
                        "action": "immediate_assessment",
                        "description": "Immediate respiratory assessment"
                    },
                    {
                        "action": "oxygen_therapy",
                        "description": "Consider oxygen therapy"
                    }
                ],
                enabled=True,
                effective_date=datetime.now(),
                tags=["respiratory", "oxygen", "critical"]
            ),
            AlertRule(
                rule_id="rule_007",
                name="Abnormal Lab Results",
                description="Laboratory results are outside normal range",
                category=AlertCategory.LAB_RESULT,
                severity=AlertSeverity.WARNING,
                priority=AlertPriority.MEDIUM,
                conditions=[
                    {
                        "field": "lab_abnormal_count",
                        "operator": "greater_than",
                        "value": 2,
                        "description": "More than 2 abnormal lab results"
                    }
                ],
                actions=[
                    {
                        "action": "lab_review",
                        "description": "Review all laboratory results"
                    },
                    {
                        "action": "clinical_correlation",
                        "description": "Correlate with clinical presentation"
                    }
                ],
                enabled=True,
                effective_date=datetime.now(),
                tags=["laboratory", "abnormal", "clinical"]
            ),
            AlertRule(
                rule_id="rule_008",
                name="Medication Allergy",
                description="Patient has known allergy to prescribed medication",
                category=AlertCategory.MEDICATION,
                severity=AlertSeverity.CRITICAL,
                priority=AlertPriority.URGENT,
                conditions=[
                    {
                        "field": "allergy_match",
                        "operator": "equals",
                        "value": True,
                        "description": "Medication allergy detected"
                    }
                ],
                actions=[
                    {
                        "action": "immediate_stop",
                        "description": "Immediately discontinue medication"
                    },
                    {
                        "action": "alternative_therapy",
                        "description": "Prescribe alternative medication"
                    }
                ],
                enabled=True,
                effective_date=datetime.now(),
                tags=["allergy", "medication", "safety", "critical"]
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
            
        logger.info(f"Loaded {len(default_rules)} default alert rules")

# Initialize alert generator
alert_generator = AlertGenerator()

# Initialize FastAPI app
app = FastAPI(
    title="Abena IHR Alert Generator",
    description="Clinical alert and warning generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the alert generator on startup"""
    await alert_generator.load_alert_rules()
    logger.info("Alert Generator initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "alert_generator",
        "timestamp": datetime.now(),
        "rules_count": len(alert_generator.alert_rules),
        "active_alerts_count": len(alert_generator.active_alerts)
    }

@app.post("/generate-alerts")
async def generate_alerts(request: AlertRequest):
    """Generate clinical alerts"""
    try:
        result = alert_generator.generate_alerts(request)
        return result
    except Exception as e:
        logger.error(f"Error generating alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/acknowledge-alert")
async def acknowledge_alert(acknowledgment: AlertAcknowledgment):
    """Acknowledge an alert"""
    try:
        alert_generator.acknowledge_alert(acknowledgment)
        return {"message": "Alert acknowledged successfully", "alert_id": acknowledgment.alert_id}
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resolve-alert")
async def resolve_alert(resolution: AlertResolution):
    """Resolve an alert"""
    try:
        alert_generator.resolve_alert(resolution)
        return {"message": "Alert resolved successfully", "alert_id": resolution.alert_id}
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alert-rules")
async def add_alert_rule(rule: AlertRule):
    """Add a new alert rule"""
    try:
        alert_generator.add_alert_rule(rule)
        return {"message": "Alert rule added successfully", "rule_id": rule.rule_id}
    except Exception as e:
        logger.error(f"Error adding alert rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alert-rules")
async def list_alert_rules():
    """List all alert rules"""
    try:
        rules = list(alert_generator.alert_rules.values())
        return {
            "rules": [rule.dict() for rule in rules],
            "count": len(rules)
        }
    except Exception as e:
        logger.error(f"Error listing alert rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts/{patient_id}")
async def get_patient_alerts(patient_id: str, include_acknowledged: bool = False, include_resolved: bool = False):
    """Get alerts for a specific patient"""
    try:
        alerts = alert_generator._get_active_alerts(patient_id, include_acknowledged, include_resolved)
        return {
            "patient_id": patient_id,
            "alerts": [alert.dict() for alert in alerts],
            "count": len(alerts),
            "critical_count": len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
        }
    except Exception as e:
        logger.error(f"Error getting patient alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alert-categories")
async def get_alert_categories():
    """Get available alert categories"""
    return {
        "categories": [cat.value for cat in AlertCategory],
        "severities": [sev.value for sev in AlertSeverity],
        "priorities": [pri.value for pri in AlertPriority],
        "statuses": [status.value for status in AlertStatus]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8024) 