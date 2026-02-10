"""
Clinical Guidelines for Abena IHR
================================

This module provides clinical guidelines and protocols including:
- Evidence-based clinical guidelines
- Treatment protocols
- Clinical recommendations
- Best practice guidelines
- Guideline compliance checking
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import redis
from pydantic import BaseModel, Field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class GuidelineStatus(Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"

class EvidenceLevel(Enum):
    A = "A"  # High quality evidence
    B = "B"  # Moderate quality evidence
    C = "C"  # Low quality evidence
    D = "D"  # Expert opinion

class RecommendationStrength(Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    AGAINST = "against"

# Pydantic models
class ClinicalGuideline(BaseModel):
    """Clinical guideline model"""
    guideline_id: str
    title: str
    description: str
    condition: str
    version: str
    status: GuidelineStatus
    evidence_level: EvidenceLevel
    source: str
    publication_date: datetime
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    recommendations: List[Dict[str, Any]]
    inclusion_criteria: List[Dict[str, Any]]
    exclusion_criteria: List[Dict[str, Any]]
    references: List[str]
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class GuidelineRecommendation(BaseModel):
    """Guideline recommendation model"""
    recommendation_id: str
    guideline_id: str
    title: str
    description: str
    strength: RecommendationStrength
    evidence_level: EvidenceLevel
    rationale: str
    implementation: str
    monitoring: str
    contraindications: List[str] = []
    warnings: List[str] = []
    references: List[str] = []

class GuidelineComplianceRequest(BaseModel):
    """Guideline compliance check request"""
    patient_id: str
    condition: str
    patient_data: Dict[str, Any]
    current_treatment: Dict[str, Any]
    guideline_id: Optional[str] = None

class GuidelineComplianceResult(BaseModel):
    """Guideline compliance result"""
    patient_id: str
    guideline_id: str
    compliant: bool
    compliance_score: float = Field(..., ge=0.0, le=1.0)
    recommendations: List[Dict[str, Any]]
    deviations: List[Dict[str, Any]]
    next_steps: List[str]
    timestamp: datetime

class ClinicalGuidelines:
    """Clinical guidelines management system"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.guidelines = {}
        self.recommendations = {}
        
    async def load_guidelines(self):
        """Load clinical guidelines from storage"""
        try:
            # Load guidelines from Redis or database
            guideline_keys = self.redis_client.keys("guideline:*")
            for key in guideline_keys:
                guideline_data = self.redis_client.get(key)
                if guideline_data:
                    guideline_dict = json.loads(guideline_data)
                    guideline = ClinicalGuideline(**guideline_dict)
                    self.guidelines[guideline.guideline_id] = guideline
                    
            # Load recommendations
            recommendation_keys = self.redis_client.keys("recommendation:*")
            for key in recommendation_keys:
                recommendation_data = self.redis_client.get(key)
                if recommendation_data:
                    recommendation_dict = json.loads(recommendation_data)
                    recommendation = GuidelineRecommendation(**recommendation_dict)
                    self.recommendations[recommendation.recommendation_id] = recommendation
                    
            logger.info(f"Loaded {len(self.guidelines)} guidelines and {len(self.recommendations)} recommendations")
            
        except Exception as e:
            logger.error(f"Error loading guidelines: {e}")
            # Load default guidelines if Redis is not available
            self._load_default_guidelines()
            
    def check_compliance(self, request: GuidelineComplianceRequest) -> GuidelineComplianceResult:
        """Check guideline compliance for a patient"""
        try:
            # Find applicable guidelines
            applicable_guidelines = self._find_applicable_guidelines(request)
            
            if not applicable_guidelines:
                return GuidelineComplianceResult(
                    patient_id=request.patient_id,
                    guideline_id="none",
                    compliant=False,
                    compliance_score=0.0,
                    recommendations=[],
                    deviations=[{"type": "no_guideline", "description": "No applicable guidelines found"}],
                    next_steps=["Consult with specialist for guidance"],
                    timestamp=datetime.now()
                )
                
            # Use specific guideline if provided
            if request.guideline_id and request.guideline_id in applicable_guidelines:
                guideline = applicable_guidelines[request.guideline_id]
            else:
                # Use the most relevant guideline
                guideline = self._select_best_guideline(applicable_guidelines, request)
                
            # Check compliance
            compliance_result = self._evaluate_compliance(guideline, request)
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            raise
            
    def get_guidelines_for_condition(self, condition: str) -> List[ClinicalGuideline]:
        """Get guidelines for a specific condition"""
        guidelines = []
        
        for guideline in self.guidelines.values():
            if (guideline.status == GuidelineStatus.ACTIVE and 
                condition.lower() in guideline.condition.lower()):
                guidelines.append(guideline)
                
        return guidelines
        
    def add_guideline(self, guideline: ClinicalGuideline):
        """Add a new clinical guideline"""
        try:
            self.guidelines[guideline.guideline_id] = guideline
            
            # Store in Redis
            guideline_key = f"guideline:{guideline.guideline_id}"
            self.redis_client.setex(
                guideline_key,
                86400,  # 24 hours TTL
                json.dumps(guideline.dict())
            )
            
            logger.info(f"Added clinical guideline: {guideline.title}")
            
        except Exception as e:
            logger.error(f"Error adding guideline: {e}")
            raise
            
    def add_recommendation(self, recommendation: GuidelineRecommendation):
        """Add a new guideline recommendation"""
        try:
            self.recommendations[recommendation.recommendation_id] = recommendation
            
            # Store in Redis
            recommendation_key = f"recommendation:{recommendation.recommendation_id}"
            self.redis_client.setex(
                recommendation_key,
                86400,  # 24 hours TTL
                json.dumps(recommendation.dict())
            )
            
            logger.info(f"Added recommendation: {recommendation.title}")
            
        except Exception as e:
            logger.error(f"Error adding recommendation: {e}")
            raise
            
    def _find_applicable_guidelines(self, request: GuidelineComplianceRequest) -> Dict[str, ClinicalGuideline]:
        """Find guidelines applicable to the patient"""
        applicable = {}
        
        for guideline in self.guidelines.values():
            if guideline.status != GuidelineStatus.ACTIVE:
                continue
                
            # Check if guideline applies to the condition
            if request.condition.lower() in guideline.condition.lower():
                # Check inclusion/exclusion criteria
                if self._check_inclusion_criteria(guideline, request.patient_data):
                    if not self._check_exclusion_criteria(guideline, request.patient_data):
                        applicable[guideline.guideline_id] = guideline
                        
        return applicable
        
    def _check_inclusion_criteria(self, guideline: ClinicalGuideline, patient_data: Dict[str, Any]) -> bool:
        """Check if patient meets inclusion criteria"""
        for criterion in guideline.inclusion_criteria:
            if not self._evaluate_criterion(criterion, patient_data):
                return False
        return True
        
    def _check_exclusion_criteria(self, guideline: ClinicalGuideline, patient_data: Dict[str, Any]) -> bool:
        """Check if patient meets exclusion criteria"""
        for criterion in guideline.exclusion_criteria:
            if self._evaluate_criterion(criterion, patient_data):
                return True
        return False
        
    def _evaluate_criterion(self, criterion: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate a single criterion"""
        try:
            field = criterion.get('field')
            operator = criterion.get('operator')
            value = criterion.get('value')
            
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
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating criterion: {e}")
            return False
            
    def _select_best_guideline(self, guidelines: Dict[str, ClinicalGuideline], 
                              request: GuidelineComplianceRequest) -> ClinicalGuideline:
        """Select the best guideline from applicable ones"""
        best_guideline = None
        best_score = 0.0
        
        for guideline in guidelines.values():
            score = self._calculate_guideline_relevance_score(guideline, request)
            if score > best_score:
                best_score = score
                best_guideline = guideline
                
        return best_guideline
        
    def _calculate_guideline_relevance_score(self, guideline: ClinicalGuideline, 
                                           request: GuidelineComplianceRequest) -> float:
        """Calculate relevance score for a guideline"""
        score = 0.0
        
        # Evidence level score
        evidence_scores = {EvidenceLevel.A: 1.0, EvidenceLevel.B: 0.8, 
                          EvidenceLevel.C: 0.6, EvidenceLevel.D: 0.4}
        score += evidence_scores.get(guideline.evidence_level, 0.5) * 0.4
        
        # Recency score (newer guidelines preferred)
        days_since_publication = (datetime.now() - guideline.publication_date).days
        recency_score = max(0.5, 1.0 - (days_since_publication / 3650))  # 10 years
        score += recency_score * 0.3
        
        # Condition match score
        condition_match = len(set(request.condition.lower().split()) & 
                            set(guideline.condition.lower().split())) / max(len(request.condition.split()), 1)
        score += condition_match * 0.3
        
        return score
        
    def _evaluate_compliance(self, guideline: ClinicalGuideline, 
                           request: GuidelineComplianceRequest) -> GuidelineComplianceResult:
        """Evaluate compliance with a specific guideline"""
        recommendations = []
        deviations = []
        compliance_score = 1.0
        
        # Check each recommendation
        for rec in guideline.recommendations:
            if self._check_recommendation_compliance(rec, request.current_treatment, request.patient_data):
                recommendations.append({
                    'type': 'compliant',
                    'recommendation': rec.get('title', 'Unknown'),
                    'description': rec.get('description', ''),
                    'strength': rec.get('strength', 'moderate')
                })
            else:
                deviations.append({
                    'type': 'non_compliant',
                    'recommendation': rec.get('title', 'Unknown'),
                    'description': rec.get('description', ''),
                    'severity': 'moderate' if rec.get('strength') == 'strong' else 'low'
                })
                compliance_score -= 0.1
                
        # Generate next steps
        next_steps = self._generate_next_steps(guideline, deviations, request)
        
        return GuidelineComplianceResult(
            patient_id=request.patient_id,
            guideline_id=guideline.guideline_id,
            compliant=compliance_score >= 0.8,
            compliance_score=max(0.0, compliance_score),
            recommendations=recommendations,
            deviations=deviations,
            next_steps=next_steps,
            timestamp=datetime.now()
        )
        
    def _check_recommendation_compliance(self, recommendation: Dict[str, Any], 
                                       current_treatment: Dict[str, Any], 
                                       patient_data: Dict[str, Any]) -> bool:
        """Check if current treatment complies with a recommendation"""
        # This is a simplified check - in practice, this would be more sophisticated
        recommendation_type = recommendation.get('type', '')
        
        if recommendation_type == 'medication':
            return self._check_medication_compliance(recommendation, current_treatment)
        elif recommendation_type == 'monitoring':
            return self._check_monitoring_compliance(recommendation, current_treatment)
        elif recommendation_type == 'lifestyle':
            return self._check_lifestyle_compliance(recommendation, patient_data)
        else:
            return True  # Default to compliant for unknown types
            
    def _check_medication_compliance(self, recommendation: Dict[str, Any], 
                                   current_treatment: Dict[str, Any]) -> bool:
        """Check medication compliance"""
        recommended_meds = recommendation.get('medications', [])
        current_meds = current_treatment.get('medications', [])
        
        for med in recommended_meds:
            if med not in current_meds:
                return False
        return True
        
    def _check_monitoring_compliance(self, recommendation: Dict[str, Any], 
                                   current_treatment: Dict[str, Any]) -> bool:
        """Check monitoring compliance"""
        recommended_monitoring = recommendation.get('monitoring', [])
        current_monitoring = current_treatment.get('monitoring', [])
        
        for monitor in recommended_monitoring:
            if monitor not in current_monitoring:
                return False
        return True
        
    def _check_lifestyle_compliance(self, recommendation: Dict[str, Any], 
                                  patient_data: Dict[str, Any]) -> bool:
        """Check lifestyle compliance"""
        # Simplified check - would be more sophisticated in practice
        return True
        
    def _generate_next_steps(self, guideline: ClinicalGuideline, 
                           deviations: List[Dict[str, Any]], 
                           request: GuidelineComplianceRequest) -> List[str]:
        """Generate next steps based on deviations"""
        next_steps = []
        
        if not deviations:
            next_steps.append("Continue current treatment plan")
            next_steps.append("Schedule follow-up according to guideline")
        else:
            next_steps.append("Review treatment plan for guideline compliance")
            next_steps.append("Implement missing recommendations")
            next_steps.append("Consider specialist consultation if needed")
            
        return next_steps
        
    def _load_default_guidelines(self):
        """Load default clinical guidelines"""
        default_guidelines = [
            ClinicalGuideline(
                guideline_id="guideline_001",
                title="Diabetes Management Guidelines",
                description="Evidence-based guidelines for diabetes management",
                condition="diabetes mellitus",
                version="2023.1",
                status=GuidelineStatus.ACTIVE,
                evidence_level=EvidenceLevel.A,
                source="American Diabetes Association",
                publication_date=datetime(2023, 1, 1),
                effective_date=datetime(2023, 1, 1),
                recommendations=[
                    {
                        "type": "medication",
                        "title": "Metformin as first-line therapy",
                        "description": "Start metformin for type 2 diabetes",
                        "strength": "strong",
                        "medications": ["metformin"]
                    },
                    {
                        "type": "monitoring",
                        "title": "Regular glucose monitoring",
                        "description": "Monitor blood glucose regularly",
                        "strength": "strong",
                        "monitoring": ["glucose", "hba1c"]
                    },
                    {
                        "type": "lifestyle",
                        "title": "Lifestyle modification",
                        "description": "Implement diet and exercise changes",
                        "strength": "moderate"
                    }
                ],
                inclusion_criteria=[
                    {"field": "diagnosis", "operator": "equals", "value": "diabetes"}
                ],
                exclusion_criteria=[
                    {"field": "age", "operator": "less_than", "value": 18}
                ],
                references=["ADA Standards of Care 2023"],
                tags=["diabetes", "endocrinology", "management"]
            ),
            ClinicalGuideline(
                guideline_id="guideline_002",
                title="Hypertension Management Guidelines",
                description="Evidence-based guidelines for hypertension management",
                condition="hypertension",
                version="2023.1",
                status=GuidelineStatus.ACTIVE,
                evidence_level=EvidenceLevel.A,
                source="American Heart Association",
                publication_date=datetime(2023, 1, 1),
                effective_date=datetime(2023, 1, 1),
                recommendations=[
                    {
                        "type": "medication",
                        "title": "ACE inhibitors or ARBs",
                        "description": "Use ACE inhibitors or ARBs as first-line therapy",
                        "strength": "strong",
                        "medications": ["ace_inhibitor", "arb"]
                    },
                    {
                        "type": "monitoring",
                        "title": "Blood pressure monitoring",
                        "description": "Monitor blood pressure regularly",
                        "strength": "strong",
                        "monitoring": ["blood_pressure"]
                    },
                    {
                        "type": "lifestyle",
                        "title": "Sodium restriction",
                        "description": "Limit sodium intake to <2.3g/day",
                        "strength": "moderate"
                    }
                ],
                inclusion_criteria=[
                    {"field": "blood_pressure_systolic", "operator": "greater_than", "value": 140}
                ],
                exclusion_criteria=[
                    {"field": "pregnancy", "operator": "equals", "value": True}
                ],
                references=["AHA Hypertension Guidelines 2023"],
                tags=["hypertension", "cardiovascular", "management"]
            )
        ]
        
        for guideline in default_guidelines:
            self.guidelines[guideline.guideline_id] = guideline
            
        logger.info(f"Loaded {len(default_guidelines)} default clinical guidelines")

# Initialize clinical guidelines
clinical_guidelines = ClinicalGuidelines()

# Example usage functions
async def initialize_guidelines():
    """Initialize the clinical guidelines"""
    await clinical_guidelines.load_guidelines()

def get_diabetes_guidelines() -> List[ClinicalGuideline]:
    """Get diabetes management guidelines"""
    return clinical_guidelines.get_guidelines_for_condition("diabetes")

def check_diabetes_compliance(patient_id: str, patient_data: Dict[str, Any], 
                            current_treatment: Dict[str, Any]) -> GuidelineComplianceResult:
    """Check diabetes guideline compliance"""
    request = GuidelineComplianceRequest(
        patient_id=patient_id,
        condition="diabetes",
        patient_data=patient_data,
        current_treatment=current_treatment
    )
    return clinical_guidelines.check_compliance(request) 