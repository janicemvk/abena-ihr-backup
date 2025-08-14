"""
Clinical Rules Engine for Abena IHR
===================================

This module provides clinical rules and protocols management including:
- Medical rules and protocols
- Clinical guidelines
- Decision trees
- Rule evaluation engine
- Protocol compliance checking
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
class RuleType(Enum):
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    MEDICATION = "medication"
    MONITORING = "monitoring"
    PREVENTION = "prevention"
    ALERT = "alert"

class RuleSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ProtocolStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"

# Pydantic models
class ClinicalRule(BaseModel):
    """Clinical rule model"""
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    severity: RuleSeverity
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    evidence_level: str = Field(..., regex="^(A|B|C|D)$")
    source: str
    version: str
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class ClinicalProtocol(BaseModel):
    """Clinical protocol model"""
    protocol_id: str
    name: str
    description: str
    condition: str
    steps: List[Dict[str, Any]]
    decision_points: List[Dict[str, Any]]
    outcomes: List[Dict[str, Any]]
    evidence_level: str = Field(..., regex="^(A|B|C|D)$")
    source: str
    version: str
    status: ProtocolStatus
    effective_date: datetime
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class RuleEvaluationRequest(BaseModel):
    """Request model for rule evaluation"""
    patient_data: Dict[str, Any]
    rule_ids: Optional[List[str]] = None
    rule_types: Optional[List[RuleType]] = None
    include_inactive: bool = False

class RuleEvaluationResult(BaseModel):
    """Rule evaluation result model"""
    rule_id: str
    rule_name: str
    triggered: bool
    severity: RuleSeverity
    message: str
    conditions_met: List[str]
    actions: List[Dict[str, Any]]
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime

class ProtocolComplianceRequest(BaseModel):
    """Request model for protocol compliance check"""
    patient_data: Dict[str, Any]
    protocol_id: str
    current_step: Optional[str] = None

class ProtocolComplianceResult(BaseModel):
    """Protocol compliance result model"""
    protocol_id: str
    protocol_name: str
    compliant: bool
    current_step: str
    next_steps: List[Dict[str, Any]]
    deviations: List[Dict[str, Any]]
    recommendations: List[str]
    compliance_score: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime

class ClinicalRulesEngine:
    """Clinical rules and protocols engine"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.rules = {}
        self.protocols = {}
        self.rule_cache = {}
        
    async def load_rules(self):
        """Load clinical rules from storage"""
        try:
            # Load rules from Redis or database
            rule_keys = self.redis_client.keys("rule:*")
            for key in rule_keys:
                rule_data = self.redis_client.get(key)
                if rule_data:
                    rule_dict = json.loads(rule_data)
                    rule = ClinicalRule(**rule_dict)
                    self.rules[rule.rule_id] = rule
                    
            logger.info(f"Loaded {len(self.rules)} clinical rules")
            
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            # Load default rules if Redis is not available
            self._load_default_rules()
            
    async def load_protocols(self):
        """Load clinical protocols from storage"""
        try:
            # Load protocols from Redis or database
            protocol_keys = self.redis_client.keys("protocol:*")
            for key in protocol_keys:
                protocol_data = self.redis_client.get(key)
                if protocol_data:
                    protocol_dict = json.loads(protocol_data)
                    protocol = ClinicalProtocol(**protocol_dict)
                    self.protocols[protocol.protocol_id] = protocol
                    
            logger.info(f"Loaded {len(self.protocols)} clinical protocols")
            
        except Exception as e:
            logger.error(f"Error loading protocols: {e}")
            # Load default protocols if Redis is not available
            self._load_default_protocols()
            
    def evaluate_rules(self, request: RuleEvaluationRequest) -> List[RuleEvaluationResult]:
        """Evaluate clinical rules against patient data"""
        try:
            results = []
            patient_data = request.patient_data
            
            # Determine which rules to evaluate
            rules_to_evaluate = []
            if request.rule_ids:
                rules_to_evaluate = [self.rules[rid] for rid in request.rule_ids if rid in self.rules]
            elif request.rule_types:
                rules_to_evaluate = [rule for rule in self.rules.values() 
                                   if rule.rule_type in request.rule_types]
            else:
                rules_to_evaluate = list(self.rules.values())
                
            # Filter by active status
            if not request.include_inactive:
                current_time = datetime.now()
                rules_to_evaluate = [rule for rule in rules_to_evaluate 
                                   if rule.effective_date <= current_time and 
                                   (rule.expiry_date is None or rule.expiry_date > current_time)]
                
            # Evaluate each rule
            for rule in rules_to_evaluate:
                result = self._evaluate_single_rule(rule, patient_data)
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"Error evaluating rules: {e}")
            raise
            
    def check_protocol_compliance(self, request: ProtocolComplianceRequest) -> ProtocolComplianceResult:
        """Check protocol compliance for patient"""
        try:
            if request.protocol_id not in self.protocols:
                raise ValueError(f"Protocol {request.protocol_id} not found")
                
            protocol = self.protocols[request.protocol_id]
            patient_data = request.patient_data
            
            # Evaluate protocol compliance
            compliance_result = self._evaluate_protocol_compliance(protocol, patient_data, request.current_step)
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error checking protocol compliance: {e}")
            raise
            
    def add_rule(self, rule: ClinicalRule):
        """Add a new clinical rule"""
        try:
            self.rules[rule.rule_id] = rule
            
            # Store in Redis
            rule_key = f"rule:{rule.rule_id}"
            self.redis_client.setex(
                rule_key,
                86400,  # 24 hours TTL
                json.dumps(rule.dict())
            )
            
            logger.info(f"Added clinical rule: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error adding rule: {e}")
            raise
            
    def update_rule(self, rule_id: str, rule: ClinicalRule):
        """Update an existing clinical rule"""
        try:
            if rule_id not in self.rules:
                raise ValueError(f"Rule {rule_id} not found")
                
            self.rules[rule_id] = rule
            
            # Update in Redis
            rule_key = f"rule:{rule_id}"
            self.redis_client.setex(
                rule_key,
                86400,  # 24 hours TTL
                json.dumps(rule.dict())
            )
            
            logger.info(f"Updated clinical rule: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error updating rule: {e}")
            raise
            
    def delete_rule(self, rule_id: str):
        """Delete a clinical rule"""
        try:
            if rule_id in self.rules:
                del self.rules[rule_id]
                
                # Remove from Redis
                rule_key = f"rule:{rule_id}"
                self.redis_client.delete(rule_key)
                
                logger.info(f"Deleted clinical rule: {rule_id}")
                
        except Exception as e:
            logger.error(f"Error deleting rule: {e}")
            raise
            
    def add_protocol(self, protocol: ClinicalProtocol):
        """Add a new clinical protocol"""
        try:
            self.protocols[protocol.protocol_id] = protocol
            
            # Store in Redis
            protocol_key = f"protocol:{protocol.protocol_id}"
            self.redis_client.setex(
                protocol_key,
                86400,  # 24 hours TTL
                json.dumps(protocol.dict())
            )
            
            logger.info(f"Added clinical protocol: {protocol.name}")
            
        except Exception as e:
            logger.error(f"Error adding protocol: {e}")
            raise
            
    def _evaluate_single_rule(self, rule: ClinicalRule, patient_data: Dict[str, Any]) -> RuleEvaluationResult:
        """Evaluate a single clinical rule"""
        try:
            conditions_met = []
            triggered = True
            
            # Evaluate each condition
            for condition in rule.conditions:
                if self._evaluate_condition(condition, patient_data):
                    conditions_met.append(condition.get('description', 'Unknown condition'))
                else:
                    triggered = False
                    
            # Generate result
            if triggered:
                message = f"Rule '{rule.name}' triggered: {', '.join(conditions_met)}"
                confidence = 0.9  # High confidence for triggered rules
            else:
                message = f"Rule '{rule.name}' not triggered"
                confidence = 0.1  # Low confidence for non-triggered rules
                
            return RuleEvaluationResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                triggered=triggered,
                severity=rule.severity,
                message=message,
                conditions_met=conditions_met if triggered else [],
                actions=rule.actions if triggered else [],
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
            return RuleEvaluationResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                triggered=False,
                severity=RuleSeverity.ERROR,
                message=f"Error evaluating rule: {str(e)}",
                conditions_met=[],
                actions=[],
                confidence=0.0,
                timestamp=datetime.now()
            )
            
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
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
            
    def _evaluate_protocol_compliance(self, protocol: ClinicalProtocol, 
                                    patient_data: Dict[str, Any], 
                                    current_step: Optional[str]) -> ProtocolComplianceResult:
        """Evaluate protocol compliance"""
        try:
            deviations = []
            recommendations = []
            compliance_score = 1.0
            
            # Determine current step
            if not current_step:
                current_step = protocol.steps[0]['step_id'] if protocol.steps else 'start'
                
            # Find current step in protocol
            current_step_data = None
            for step in protocol.steps:
                if step['step_id'] == current_step:
                    current_step_data = step
                    break
                    
            if not current_step_data:
                deviations.append({
                    'type': 'invalid_step',
                    'description': f"Invalid step: {current_step}",
                    'severity': 'error'
                })
                compliance_score = 0.0
                
            # Check step requirements
            if current_step_data:
                step_requirements = current_step_data.get('requirements', [])
                for requirement in step_requirements:
                    if not self._evaluate_condition(requirement, patient_data):
                        deviations.append({
                            'type': 'requirement_not_met',
                            'description': f"Requirement not met: {requirement.get('description', 'Unknown')}",
                            'severity': 'warning'
                        })
                        compliance_score -= 0.1
                        
            # Determine next steps
            next_steps = []
            if current_step_data:
                next_steps = current_step_data.get('next_steps', [])
                
            # Generate recommendations
            if deviations:
                recommendations.append("Address protocol deviations before proceeding")
            if compliance_score < 0.8:
                recommendations.append("Review protocol compliance")
                
            return ProtocolComplianceResult(
                protocol_id=protocol.protocol_id,
                protocol_name=protocol.name,
                compliant=compliance_score >= 0.8,
                current_step=current_step,
                next_steps=next_steps,
                deviations=deviations,
                recommendations=recommendations,
                compliance_score=max(0.0, compliance_score),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error evaluating protocol compliance: {e}")
            raise
            
    def _load_default_rules(self):
        """Load default clinical rules"""
        default_rules = [
            ClinicalRule(
                rule_id="rule_001",
                name="Hypertension Alert",
                description="Alert for elevated blood pressure",
                rule_type=RuleType.ALERT,
                severity=RuleSeverity.WARNING,
                conditions=[
                    {
                        "field": "blood_pressure_systolic",
                        "operator": "greater_than",
                        "value": 140,
                        "description": "Systolic BP > 140"
                    }
                ],
                actions=[
                    {
                        "action": "alert",
                        "message": "Elevated blood pressure detected"
                    }
                ],
                evidence_level="A",
                source="JNC 8 Guidelines",
                version="1.0",
                effective_date=datetime.now(),
                tags=["hypertension", "cardiovascular"]
            ),
            ClinicalRule(
                rule_id="rule_002",
                name="Diabetes Screening",
                description="Recommend diabetes screening for high-risk patients",
                rule_type=RuleType.PREVENTION,
                severity=RuleSeverity.INFO,
                conditions=[
                    {
                        "field": "age",
                        "operator": "greater_than",
                        "value": 45,
                        "description": "Age > 45"
                    },
                    {
                        "field": "bmi",
                        "operator": "greater_than",
                        "value": 25,
                        "description": "BMI > 25"
                    }
                ],
                actions=[
                    {
                        "action": "recommend",
                        "message": "Consider diabetes screening"
                    }
                ],
                evidence_level="B",
                source="ADA Guidelines",
                version="1.0",
                effective_date=datetime.now(),
                tags=["diabetes", "screening", "prevention"]
            ),
            ClinicalRule(
                rule_id="rule_003",
                name="Medication Interaction Check",
                description="Check for potential drug interactions",
                rule_type=RuleType.MEDICATION,
                severity=RuleSeverity.ERROR,
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
                        "action": "review",
                        "message": "Review medication list for interactions"
                    }
                ],
                evidence_level="A",
                source="Drug Interaction Database",
                version="1.0",
                effective_date=datetime.now(),
                tags=["medication", "safety", "interactions"]
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
            
        logger.info(f"Loaded {len(default_rules)} default rules")
        
    def _load_default_protocols(self):
        """Load default clinical protocols"""
        default_protocols = [
            ClinicalProtocol(
                protocol_id="protocol_001",
                name="Hypertension Management",
                description="Standard protocol for hypertension management",
                condition="hypertension",
                steps=[
                    {
                        "step_id": "initial_assessment",
                        "name": "Initial Assessment",
                        "requirements": [
                            {
                                "field": "blood_pressure_systolic",
                                "operator": "greater_than",
                                "value": 140,
                                "description": "Confirmed hypertension"
                            }
                        ],
                        "next_steps": ["lifestyle_modification", "medication_consideration"]
                    },
                    {
                        "step_id": "lifestyle_modification",
                        "name": "Lifestyle Modification",
                        "requirements": [],
                        "next_steps": ["medication_consideration", "monitoring"]
                    },
                    {
                        "step_id": "medication_consideration",
                        "name": "Medication Consideration",
                        "requirements": [
                            {
                                "field": "blood_pressure_systolic",
                                "operator": "greater_than",
                                "value": 160,
                                "description": "Severe hypertension"
                            }
                        ],
                        "next_steps": ["medication_prescription", "monitoring"]
                    }
                ],
                decision_points=[
                    {
                        "point_id": "dp_001",
                        "name": "Medication Decision",
                        "condition": "blood_pressure_systolic > 160",
                        "options": ["prescribe_medication", "continue_monitoring"]
                    }
                ],
                outcomes=[
                    {
                        "outcome_id": "out_001",
                        "name": "Blood Pressure Control",
                        "target": "blood_pressure_systolic < 140"
                    }
                ],
                evidence_level="A",
                source="JNC 8 Guidelines",
                version="1.0",
                status=ProtocolStatus.ACTIVE,
                effective_date=datetime.now(),
                tags=["hypertension", "cardiovascular", "management"]
            ),
            ClinicalProtocol(
                protocol_id="protocol_002",
                name="Diabetes Management",
                description="Standard protocol for diabetes management",
                condition="diabetes",
                steps=[
                    {
                        "step_id": "diagnosis_confirmation",
                        "name": "Diagnosis Confirmation",
                        "requirements": [
                            {
                                "field": "glucose",
                                "operator": "greater_than",
                                "value": 126,
                                "description": "Elevated glucose"
                            }
                        ],
                        "next_steps": ["lifestyle_counseling", "medication_management"]
                    },
                    {
                        "step_id": "lifestyle_counseling",
                        "name": "Lifestyle Counseling",
                        "requirements": [],
                        "next_steps": ["medication_management", "monitoring"]
                    },
                    {
                        "step_id": "medication_management",
                        "name": "Medication Management",
                        "requirements": [
                            {
                                "field": "glucose",
                                "operator": "greater_than",
                                "value": 200,
                                "description": "Poor glucose control"
                            }
                        ],
                        "next_steps": ["medication_adjustment", "monitoring"]
                    }
                ],
                decision_points=[
                    {
                        "point_id": "dp_001",
                        "name": "Medication Decision",
                        "condition": "glucose > 200",
                        "options": ["add_medication", "adjust_dose"]
                    }
                ],
                outcomes=[
                    {
                        "outcome_id": "out_001",
                        "name": "Glucose Control",
                        "target": "glucose < 126"
                    }
                ],
                evidence_level="A",
                source="ADA Guidelines",
                version="1.0",
                status=ProtocolStatus.ACTIVE,
                effective_date=datetime.now(),
                tags=["diabetes", "endocrinology", "management"]
            )
        ]
        
        for protocol in default_protocols:
            self.protocols[protocol.protocol_id] = protocol
            
        logger.info(f"Loaded {len(default_protocols)} default protocols")

# Initialize clinical rules engine
rules_engine = ClinicalRulesEngine()

# Initialize FastAPI app
app = FastAPI(
    title="Abena IHR Clinical Rules Engine",
    description="Clinical rules and protocols management",
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
    """Initialize the rules engine on startup"""
    await rules_engine.load_rules()
    await rules_engine.load_protocols()
    logger.info("Clinical Rules Engine initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "clinical_rules_engine",
        "timestamp": datetime.now(),
        "rules_count": len(rules_engine.rules),
        "protocols_count": len(rules_engine.protocols)
    }

@app.post("/evaluate-rules")
async def evaluate_rules(request: RuleEvaluationRequest):
    """Evaluate clinical rules"""
    try:
        results = rules_engine.evaluate_rules(request)
        return {
            "results": [result.dict() for result in results],
            "total_rules": len(results),
            "triggered_rules": len([r for r in results if r.triggered]),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error evaluating rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-protocol-compliance")
async def check_protocol_compliance(request: ProtocolComplianceRequest):
    """Check protocol compliance"""
    try:
        result = rules_engine.check_protocol_compliance(request)
        return result
    except Exception as e:
        logger.error(f"Error checking protocol compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rules")
async def add_rule(rule: ClinicalRule):
    """Add a new clinical rule"""
    try:
        rules_engine.add_rule(rule)
        return {"message": "Rule added successfully", "rule_id": rule.rule_id}
    except Exception as e:
        logger.error(f"Error adding rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/rules/{rule_id}")
async def update_rule(rule_id: str, rule: ClinicalRule):
    """Update a clinical rule"""
    try:
        rules_engine.update_rule(rule_id, rule)
        return {"message": "Rule updated successfully", "rule_id": rule_id}
    except Exception as e:
        logger.error(f"Error updating rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    """Delete a clinical rule"""
    try:
        rules_engine.delete_rule(rule_id)
        return {"message": "Rule deleted successfully", "rule_id": rule_id}
    except Exception as e:
        logger.error(f"Error deleting rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules")
async def list_rules():
    """List all clinical rules"""
    try:
        rules = list(rules_engine.rules.values())
        return {
            "rules": [rule.dict() for rule in rules],
            "count": len(rules)
        }
    except Exception as e:
        logger.error(f"Error listing rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/protocols")
async def add_protocol(protocol: ClinicalProtocol):
    """Add a new clinical protocol"""
    try:
        rules_engine.add_protocol(protocol)
        return {"message": "Protocol added successfully", "protocol_id": protocol.protocol_id}
    except Exception as e:
        logger.error(f"Error adding protocol: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/protocols")
async def list_protocols():
    """List all clinical protocols"""
    try:
        protocols = list(rules_engine.protocols.values())
        return {
            "protocols": [protocol.dict() for protocol in protocols],
            "count": len(protocols)
        }
    except Exception as e:
        logger.error(f"Error listing protocols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021) 