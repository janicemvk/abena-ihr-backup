"""
Drug Interaction Checker for Abena IHR
=====================================

This module provides medication safety capabilities including:
- Drug interaction checking
- Contraindication detection
- Dosing recommendations
- Medication safety alerts
- Drug allergy checking
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
class InteractionSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CONTRAINDICATED = "contraindicated"

class AlertType(Enum):
    INTERACTION = "interaction"
    CONTRAINDICATION = "contraindication"
    ALLERGY = "allergy"
    DOSING = "dosing"
    MONITORING = "monitoring"

class MedicationStatus(Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"

# Pydantic models
class Medication(BaseModel):
    """Medication model"""
    medication_id: str
    name: str
    generic_name: str
    drug_class: str
    dosage_form: str
    strength: str
    route: str
    frequency: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: MedicationStatus = MedicationStatus.ACTIVE
    prescribed_by: str
    instructions: str
    quantity: int
    refills: int = 0
    metadata: Dict[str, Any] = {}

class DrugInteraction(BaseModel):
    """Drug interaction model"""
    interaction_id: str
    drug1: str
    drug2: str
    severity: InteractionSeverity
    description: str
    mechanism: str
    clinical_effects: List[str]
    management: str
    evidence_level: str = Field(..., regex="^(A|B|C|D)$")
    source: str
    last_updated: datetime

class InteractionCheckRequest(BaseModel):
    """Request model for interaction checking"""
    patient_id: str
    current_medications: List[Medication]
    new_medication: Optional[Medication] = None
    allergies: List[str] = []
    lab_results: Dict[str, float] = {}
    vital_signs: Dict[str, float] = {}
    age: int
    gender: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    renal_function: Optional[str] = None
    hepatic_function: Optional[str] = None

class InteractionCheckResult(BaseModel):
    """Interaction check result model"""
    patient_id: str
    check_id: str
    interactions_found: List[DrugInteraction]
    contraindications: List[Dict[str, Any]]
    allergies: List[Dict[str, Any]]
    dosing_recommendations: List[Dict[str, Any]]
    monitoring_recommendations: List[Dict[str, Any]]
    safety_score: float = Field(..., ge=0.0, le=1.0)
    alerts: List[Dict[str, Any]]
    timestamp: datetime

class DrugInteractionChecker:
    """Drug interaction and safety checker"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.interaction_database = {}
        self.contraindication_database = {}
        self.allergy_database = {}
        self.dosing_database = {}
        
    async def load_interaction_data(self):
        """Load drug interaction data from storage"""
        try:
            # Load interactions from Redis or database
            interaction_keys = self.redis_client.keys("interaction:*")
            for key in interaction_keys:
                interaction_data = self.redis_client.get(key)
                if interaction_data:
                    interaction_dict = json.loads(interaction_data)
                    interaction = DrugInteraction(**interaction_dict)
                    self.interaction_database[interaction.interaction_id] = interaction
                    
            logger.info(f"Loaded {len(self.interaction_database)} drug interactions")
            
        except Exception as e:
            logger.error(f"Error loading interaction data: {e}")
            # Load default interactions if Redis is not available
            self._load_default_interactions()
            
    def check_interactions(self, request: InteractionCheckRequest) -> InteractionCheckResult:
        """Check for drug interactions and safety issues"""
        try:
            check_id = f"check_{datetime.now().timestamp()}"
            
            # Get all medications to check
            medications = request.current_medications.copy()
            if request.new_medication:
                medications.append(request.new_medication)
                
            # Check for interactions
            interactions_found = self._find_interactions(medications)
            
            # Check for contraindications
            contraindications = self._check_contraindications(request)
            
            # Check for allergies
            allergies = self._check_allergies(request)
            
            # Generate dosing recommendations
            dosing_recommendations = self._generate_dosing_recommendations(request)
            
            # Generate monitoring recommendations
            monitoring_recommendations = self._generate_monitoring_recommendations(request)
            
            # Calculate safety score
            safety_score = self._calculate_safety_score(interactions_found, contraindications, allergies)
            
            # Generate alerts
            alerts = self._generate_alerts(interactions_found, contraindications, allergies, dosing_recommendations)
            
            return InteractionCheckResult(
                patient_id=request.patient_id,
                check_id=check_id,
                interactions_found=interactions_found,
                contraindications=contraindications,
                allergies=allergies,
                dosing_recommendations=dosing_recommendations,
                monitoring_recommendations=monitoring_recommendations,
                safety_score=safety_score,
                alerts=alerts,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error checking interactions: {e}")
            raise
            
    def add_interaction(self, interaction: DrugInteraction):
        """Add a new drug interaction"""
        try:
            self.interaction_database[interaction.interaction_id] = interaction
            
            # Store in Redis
            interaction_key = f"interaction:{interaction.interaction_id}"
            self.redis_client.setex(
                interaction_key,
                86400,  # 24 hours TTL
                json.dumps(interaction.dict())
            )
            
            logger.info(f"Added drug interaction: {interaction.drug1} + {interaction.drug2}")
            
        except Exception as e:
            logger.error(f"Error adding interaction: {e}")
            raise
            
    def _find_interactions(self, medications: List[Medication]) -> List[DrugInteraction]:
        """Find interactions between medications"""
        interactions = []
        
        # Check each pair of medications
        for i, med1 in enumerate(medications):
            for j, med2 in enumerate(medications[i+1:], i+1):
                # Check for interactions in database
                found_interactions = self._check_medication_pair(med1, med2)
                interactions.extend(found_interactions)
                
        return interactions
        
    def _check_medication_pair(self, med1: Medication, med2: Medication) -> List[DrugInteraction]:
        """Check for interactions between two medications"""
        interactions = []
        
        # Check by generic names
        for interaction in self.interaction_database.values():
            if ((interaction.drug1.lower() in med1.generic_name.lower() and 
                 interaction.drug2.lower() in med2.generic_name.lower()) or
                (interaction.drug1.lower() in med2.generic_name.lower() and 
                 interaction.drug2.lower() in med1.generic_name.lower())):
                interactions.append(interaction)
                
        # Check by drug class
        for interaction in self.interaction_database.values():
            if ((interaction.drug1.lower() in med1.drug_class.lower() and 
                 interaction.drug2.lower() in med2.drug_class.lower()) or
                (interaction.drug1.lower() in med2.drug_class.lower() and 
                 interaction.drug2.lower() in med1.drug_class.lower())):
                interactions.append(interaction)
                
        return interactions
        
    def _check_contraindications(self, request: InteractionCheckRequest) -> List[Dict[str, Any]]:
        """Check for contraindications"""
        contraindications = []
        
        # Check age-related contraindications
        if request.age < 18:
            contraindications.append({
                'type': 'age',
                'medication': 'general',
                'description': 'Patient is under 18, review pediatric dosing',
                'severity': 'moderate'
            })
            
        # Check renal function contraindications
        if request.renal_function == 'severe' and any('renal' in med.drug_class.lower() for med in request.current_medications):
            contraindications.append({
                'type': 'renal_function',
                'medication': 'renal_clearance_medications',
                'description': 'Severe renal impairment - adjust dosing',
                'severity': 'major'
            })
            
        # Check hepatic function contraindications
        if request.hepatic_function == 'severe' and any('hepatic' in med.drug_class.lower() for med in request.current_medications):
            contraindications.append({
                'type': 'hepatic_function',
                'medication': 'hepatic_clearance_medications',
                'description': 'Severe hepatic impairment - adjust dosing',
                'severity': 'major'
            })
            
        # Check pregnancy contraindications
        if request.gender == 'female' and request.age < 50:
            # This would typically check pregnancy status
            contraindications.append({
                'type': 'pregnancy',
                'medication': 'teratogenic_medications',
                'description': 'Consider pregnancy status for teratogenic medications',
                'severity': 'moderate'
            })
            
        return contraindications
        
    def _check_allergies(self, request: InteractionCheckRequest) -> List[Dict[str, Any]]:
        """Check for drug allergies"""
        allergies = []
        
        for allergy in request.allergies:
            for medication in request.current_medications:
                if self._check_allergy_match(allergy, medication):
                    allergies.append({
                        'allergy': allergy,
                        'medication': medication.name,
                        'severity': 'severe',
                        'description': f'Patient has allergy to {allergy}'
                    })
                    
        return allergies
        
    def _check_allergy_match(self, allergy: str, medication: Medication) -> bool:
        """Check if medication matches allergy"""
        allergy_lower = allergy.lower()
        
        # Check medication name
        if allergy_lower in medication.name.lower():
            return True
            
        # Check generic name
        if allergy_lower in medication.generic_name.lower():
            return True
            
        # Check drug class
        if allergy_lower in medication.drug_class.lower():
            return True
            
        return False
        
    def _generate_dosing_recommendations(self, request: InteractionCheckRequest) -> List[Dict[str, Any]]:
        """Generate dosing recommendations"""
        recommendations = []
        
        # Age-based dosing
        if request.age > 65:
            recommendations.append({
                'type': 'age_based',
                'medication': 'general',
                'recommendation': 'Consider reduced dosing for elderly patients',
                'reason': 'Age-related pharmacokinetic changes',
                'priority': 'medium'
            })
            
        # Weight-based dosing
        if request.weight_kg:
            for medication in request.current_medications:
                if 'weight_based' in medication.metadata.get('dosing_type', ''):
                    recommendations.append({
                        'type': 'weight_based',
                        'medication': medication.name,
                        'recommendation': f'Verify weight-based dosing for {medication.name}',
                        'reason': f'Patient weight: {request.weight_kg} kg',
                        'priority': 'high'
                    })
                    
        # Renal function dosing
        if request.renal_function == 'moderate':
            recommendations.append({
                'type': 'renal_function',
                'medication': 'renal_clearance_medications',
                'recommendation': 'Consider dose reduction for renal impairment',
                'reason': 'Moderate renal impairment detected',
                'priority': 'high'
            })
            
        # Hepatic function dosing
        if request.hepatic_function == 'moderate':
            recommendations.append({
                'type': 'hepatic_function',
                'medication': 'hepatic_clearance_medications',
                'recommendation': 'Consider dose reduction for hepatic impairment',
                'reason': 'Moderate hepatic impairment detected',
                'priority': 'high'
            })
            
        return recommendations
        
    def _generate_monitoring_recommendations(self, request: InteractionCheckRequest) -> List[Dict[str, Any]]:
        """Generate monitoring recommendations"""
        recommendations = []
        
        # High-risk medications
        high_risk_medications = ['warfarin', 'digoxin', 'lithium', 'theophylline']
        for medication in request.current_medications:
            if any(hr_med in medication.generic_name.lower() for hr_med in high_risk_medications):
                recommendations.append({
                    'type': 'therapeutic_monitoring',
                    'medication': medication.name,
                    'recommendation': f'Monitor {medication.name} levels',
                    'frequency': 'weekly',
                    'priority': 'high'
                })
                
        # Drug interactions requiring monitoring
        for medication in request.current_medications:
            if 'interaction_monitoring' in medication.metadata:
                recommendations.append({
                    'type': 'interaction_monitoring',
                    'medication': medication.name,
                    'recommendation': f'Monitor for interaction effects with {medication.name}',
                    'frequency': 'as_needed',
                    'priority': 'medium'
                })
                
        # Lab monitoring
        if any('renal' in med.drug_class.lower() for med in request.current_medications):
            recommendations.append({
                'type': 'lab_monitoring',
                'medication': 'renal_medications',
                'recommendation': 'Monitor renal function',
                'frequency': 'monthly',
                'priority': 'medium'
            })
            
        if any('hepatic' in med.drug_class.lower() for med in request.current_medications):
            recommendations.append({
                'type': 'lab_monitoring',
                'medication': 'hepatic_medications',
                'recommendation': 'Monitor liver function',
                'frequency': 'monthly',
                'priority': 'medium'
            })
            
        return recommendations
        
    def _calculate_safety_score(self, interactions: List[DrugInteraction], 
                               contraindications: List[Dict[str, Any]], 
                               allergies: List[Dict[str, Any]]) -> float:
        """Calculate medication safety score"""
        score = 1.0
        
        # Deduct for interactions
        for interaction in interactions:
            if interaction.severity == InteractionSeverity.CONTRAINDICATED:
                score -= 0.5
            elif interaction.severity == InteractionSeverity.MAJOR:
                score -= 0.3
            elif interaction.severity == InteractionSeverity.MODERATE:
                score -= 0.2
            elif interaction.severity == InteractionSeverity.MINOR:
                score -= 0.1
                
        # Deduct for contraindications
        for contraindication in contraindications:
            if contraindication['severity'] == 'major':
                score -= 0.3
            elif contraindication['severity'] == 'moderate':
                score -= 0.2
            else:
                score -= 0.1
                
        # Deduct for allergies
        for allergy in allergies:
            score -= 0.4  # Allergies are serious
            
        return max(0.0, score)
        
    def _generate_alerts(self, interactions: List[DrugInteraction], 
                        contraindications: List[Dict[str, Any]], 
                        allergies: List[Dict[str, Any]], 
                        dosing_recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate safety alerts"""
        alerts = []
        
        # Interaction alerts
        for interaction in interactions:
            if interaction.severity in [InteractionSeverity.MAJOR, InteractionSeverity.CONTRAINDICATED]:
                alerts.append({
                    'type': AlertType.INTERACTION,
                    'severity': interaction.severity.value,
                    'title': f'Drug Interaction: {interaction.drug1} + {interaction.drug2}',
                    'message': interaction.description,
                    'recommendation': interaction.management
                })
                
        # Contraindication alerts
        for contraindication in contraindications:
            if contraindication['severity'] in ['major', 'moderate']:
                alerts.append({
                    'type': AlertType.CONTRAINDICATION,
                    'severity': contraindication['severity'],
                    'title': f'Contraindication: {contraindication["type"]}',
                    'message': contraindication['description'],
                    'recommendation': 'Review medication appropriateness'
                })
                
        # Allergy alerts
        for allergy in allergies:
            alerts.append({
                'type': AlertType.ALLERGY,
                'severity': 'critical',
                'title': f'Drug Allergy: {allergy["allergy"]}',
                'message': f'Patient allergic to {allergy["medication"]}',
                'recommendation': 'Discontinue medication immediately'
            })
            
        # Dosing alerts
        for recommendation in dosing_recommendations:
            if recommendation['priority'] == 'high':
                alerts.append({
                    'type': AlertType.DOSING,
                    'severity': 'moderate',
                    'title': f'Dosing Alert: {recommendation["medication"]}',
                    'message': recommendation['recommendation'],
                    'recommendation': recommendation['reason']
                })
                
        return alerts
        
    def _load_default_interactions(self):
        """Load default drug interactions"""
        default_interactions = [
            DrugInteraction(
                interaction_id="int_001",
                drug1="warfarin",
                drug2="aspirin",
                severity=InteractionSeverity.MAJOR,
                description="Increased risk of bleeding when combining warfarin and aspirin",
                mechanism="Additive anticoagulant effect",
                clinical_effects=["Increased bleeding risk", "Bruising", "Gastrointestinal bleeding"],
                management="Monitor INR closely, consider alternative antiplatelet therapy",
                evidence_level="A",
                source="Drug Interaction Database",
                last_updated=datetime.now()
            ),
            DrugInteraction(
                interaction_id="int_002",
                drug1="simvastatin",
                drug2="amiodarone",
                severity=InteractionSeverity.MAJOR,
                description="Increased risk of myopathy when combining simvastatin and amiodarone",
                mechanism="Inhibition of simvastatin metabolism",
                clinical_effects=["Muscle pain", "Weakness", "Rhabdomyolysis"],
                management="Limit simvastatin dose to 20mg daily, monitor for muscle symptoms",
                evidence_level="A",
                source="Drug Interaction Database",
                last_updated=datetime.now()
            ),
            DrugInteraction(
                interaction_id="int_003",
                drug1="digoxin",
                drug2="amiodarone",
                severity=InteractionSeverity.MAJOR,
                description="Increased digoxin levels when combining with amiodarone",
                mechanism="Inhibition of digoxin clearance",
                clinical_effects=["Digoxin toxicity", "Nausea", "Bradycardia"],
                management="Reduce digoxin dose by 50%, monitor digoxin levels",
                evidence_level="A",
                source="Drug Interaction Database",
                last_updated=datetime.now()
            ),
            DrugInteraction(
                interaction_id="int_004",
                drug1="metformin",
                drug2="furosemide",
                severity=InteractionSeverity.MODERATE,
                description="Potential for reduced metformin efficacy with furosemide",
                mechanism="Competitive renal tubular secretion",
                clinical_effects=["Reduced glycemic control", "Increased glucose levels"],
                management="Monitor blood glucose, adjust metformin dose if needed",
                evidence_level="B",
                source="Drug Interaction Database",
                last_updated=datetime.now()
            ),
            DrugInteraction(
                interaction_id="int_005",
                drug1="levothyroxine",
                drug2="calcium",
                severity=InteractionSeverity.MODERATE,
                description="Reduced levothyroxine absorption with calcium supplements",
                mechanism="Chelation in gastrointestinal tract",
                clinical_effects=["Reduced thyroid hormone levels", "Hypothyroid symptoms"],
                management="Separate administration by 4 hours",
                evidence_level="A",
                source="Drug Interaction Database",
                last_updated=datetime.now()
            )
        ]
        
        for interaction in default_interactions:
            self.interaction_database[interaction.interaction_id] = interaction
            
        logger.info(f"Loaded {len(default_interactions)} default drug interactions")

# Initialize drug interaction checker
interaction_checker = DrugInteractionChecker()

# Initialize FastAPI app
app = FastAPI(
    title="Abena IHR Drug Interaction Checker",
    description="Medication safety and interaction checking",
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
    """Initialize the interaction checker on startup"""
    await interaction_checker.load_interaction_data()
    logger.info("Drug Interaction Checker initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "drug_interaction_checker",
        "timestamp": datetime.now(),
        "interactions_count": len(interaction_checker.interaction_database)
    }

@app.post("/check-interactions")
async def check_interactions(request: InteractionCheckRequest):
    """Check for drug interactions and safety issues"""
    try:
        result = interaction_checker.check_interactions(request)
        return result
    except Exception as e:
        logger.error(f"Error checking interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interactions")
async def add_interaction(interaction: DrugInteraction):
    """Add a new drug interaction"""
    try:
        interaction_checker.add_interaction(interaction)
        return {"message": "Interaction added successfully", "interaction_id": interaction.interaction_id}
    except Exception as e:
        logger.error(f"Error adding interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interactions")
async def list_interactions():
    """List all drug interactions"""
    try:
        interactions = list(interaction_checker.interaction_database.values())
        return {
            "interactions": [interaction.dict() for interaction in interactions],
            "count": len(interactions)
        }
    except Exception as e:
        logger.error(f"Error listing interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interactions/{drug_name}")
async def search_interactions(drug_name: str):
    """Search for interactions by drug name"""
    try:
        matching_interactions = []
        for interaction in interaction_checker.interaction_database.values():
            if (drug_name.lower() in interaction.drug1.lower() or 
                drug_name.lower() in interaction.drug2.lower()):
                matching_interactions.append(interaction)
                
        return {
            "drug_name": drug_name,
            "interactions": [interaction.dict() for interaction in matching_interactions],
            "count": len(matching_interactions)
        }
    except Exception as e:
        logger.error(f"Error searching interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8022) 