"""
Evidence Base for Abena IHR
==========================

This module provides evidence-based medicine capabilities including:
- Clinical research evidence
- Systematic reviews
- Meta-analyses
- Clinical trials
- Evidence synthesis
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
class StudyType(Enum):
    RANDOMIZED_CONTROLLED_TRIAL = "rct"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    OBSERVATIONAL_STUDY = "observational"
    CASE_CONTROL = "case_control"
    COHORT_STUDY = "cohort"
    CASE_SERIES = "case_series"
    EXPERT_OPINION = "expert_opinion"

class EvidenceQuality(Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"

class PublicationStatus(Enum):
    PUBLISHED = "published"
    PREPRINT = "preprint"
    IN_PRESS = "in_press"
    SUBMITTED = "submitted"

# Pydantic models
class ClinicalStudy(BaseModel):
    """Clinical study model"""
    study_id: str
    title: str
    authors: List[str]
    study_type: StudyType
    evidence_quality: EvidenceQuality
    publication_status: PublicationStatus
    journal: Optional[str] = None
    doi: Optional[str] = None
    pubmed_id: Optional[str] = None
    publication_date: Optional[datetime] = None
    abstract: str
    keywords: List[str] = []
    interventions: List[str] = []
    outcomes: List[str] = []
    population: Dict[str, Any] = {}
    results: Dict[str, Any] = {}
    conclusions: str
    limitations: List[str] = []
    funding_source: Optional[str] = None
    conflicts_of_interest: List[str] = []
    metadata: Dict[str, Any] = {}

class EvidenceSynthesis(BaseModel):
    """Evidence synthesis model"""
    synthesis_id: str
    title: str
    type: str  # systematic_review, meta_analysis, guideline
    condition: str
    interventions: List[str]
    outcomes: List[str]
    included_studies: List[str]
    evidence_quality: EvidenceQuality
    conclusions: str
    recommendations: List[Dict[str, Any]]
    publication_date: datetime
    source: str
    metadata: Dict[str, Any] = {}

class EvidenceQuery(BaseModel):
    """Evidence query model"""
    condition: Optional[str] = None
    intervention: Optional[str] = None
    outcome: Optional[str] = None
    study_types: List[StudyType] = []
    min_quality: EvidenceQuality = EvidenceQuality.LOW
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    max_results: int = 50

class EvidenceResult(BaseModel):
    """Evidence query result"""
    query_id: str
    studies: List[ClinicalStudy]
    syntheses: List[EvidenceSynthesis]
    total_studies: int
    total_syntheses: int
    evidence_summary: Dict[str, Any]
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime

class EvidenceBase:
    """Evidence-based medicine database"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.studies = {}
        self.syntheses = {}
        
    async def load_evidence_base(self):
        """Load evidence base from storage"""
        try:
            # Load studies from Redis or database
            study_keys = self.redis_client.keys("study:*")
            for key in study_keys:
                study_data = self.redis_client.get(key)
                if study_data:
                    study_dict = json.loads(study_data)
                    study = ClinicalStudy(**study_dict)
                    self.studies[study.study_id] = study
                    
            # Load syntheses
            synthesis_keys = self.redis_client.keys("synthesis:*")
            for key in synthesis_keys:
                synthesis_data = self.redis_client.get(key)
                if synthesis_data:
                    synthesis_dict = json.loads(synthesis_data)
                    synthesis = EvidenceSynthesis(**synthesis_dict)
                    self.syntheses[synthesis.synthesis_id] = synthesis
                    
            logger.info(f"Loaded {len(self.studies)} studies and {len(self.syntheses)} syntheses")
            
        except Exception as e:
            logger.error(f"Error loading evidence base: {e}")
            # Load default evidence if Redis is not available
            self._load_default_evidence()
            
    def search_evidence(self, query: EvidenceQuery) -> EvidenceResult:
        """Search for clinical evidence"""
        try:
            query_id = f"evidence_{datetime.now().timestamp()}"
            
            # Filter studies
            filtered_studies = self._filter_studies(query)
            
            # Filter syntheses
            filtered_syntheses = self._filter_syntheses(query)
            
            # Generate evidence summary
            evidence_summary = self._generate_evidence_summary(filtered_studies, filtered_syntheses)
            
            # Calculate confidence
            confidence = self._calculate_evidence_confidence(filtered_studies, filtered_syntheses)
            
            return EvidenceResult(
                query_id=query_id,
                studies=filtered_studies[:query.max_results],
                syntheses=filtered_syntheses[:query.max_results],
                total_studies=len(filtered_studies),
                total_syntheses=len(filtered_syntheses),
                evidence_summary=evidence_summary,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error searching evidence: {e}")
            raise
            
    def add_study(self, study: ClinicalStudy):
        """Add a clinical study to the evidence base"""
        try:
            self.studies[study.study_id] = study
            
            # Store in Redis
            study_key = f"study:{study.study_id}"
            self.redis_client.setex(
                study_key,
                86400,  # 24 hours TTL
                json.dumps(study.dict())
            )
            
            logger.info(f"Added clinical study: {study.title}")
            
        except Exception as e:
            logger.error(f"Error adding study: {e}")
            raise
            
    def add_synthesis(self, synthesis: EvidenceSynthesis):
        """Add an evidence synthesis to the evidence base"""
        try:
            self.syntheses[synthesis.synthesis_id] = synthesis
            
            # Store in Redis
            synthesis_key = f"synthesis:{synthesis.synthesis_id}"
            self.redis_client.setex(
                synthesis_key,
                86400,  # 24 hours TTL
                json.dumps(synthesis.dict())
            )
            
            logger.info(f"Added evidence synthesis: {synthesis.title}")
            
        except Exception as e:
            logger.error(f"Error adding synthesis: {e}")
            raise
            
    def _filter_studies(self, query: EvidenceQuery) -> List[ClinicalStudy]:
        """Filter studies based on query criteria"""
        filtered_studies = []
        
        for study in self.studies.values():
            # Check publication status
            if study.publication_status != PublicationStatus.PUBLISHED:
                continue
                
            # Check condition
            if query.condition and query.condition.lower() not in study.title.lower():
                continue
                
            # Check intervention
            if query.intervention and query.intervention.lower() not in ' '.join(study.interventions).lower():
                continue
                
            # Check outcome
            if query.outcome and query.outcome.lower() not in ' '.join(study.outcomes).lower():
                continue
                
            # Check study type
            if query.study_types and study.study_type not in query.study_types:
                continue
                
            # Check quality
            quality_order = [EvidenceQuality.HIGH, EvidenceQuality.MODERATE, EvidenceQuality.LOW, EvidenceQuality.VERY_LOW]
            min_quality_index = quality_order.index(query.min_quality)
            study_quality_index = quality_order.index(study.evidence_quality)
            if study_quality_index > min_quality_index:
                continue
                
            # Check date range
            if query.date_from and study.publication_date and study.publication_date < query.date_from:
                continue
            if query.date_to and study.publication_date and study.publication_date > query.date_to:
                continue
                
            filtered_studies.append(study)
            
        # Sort by quality and date
        filtered_studies.sort(key=lambda x: (quality_order.index(x.evidence_quality), x.publication_date or datetime.min), reverse=True)
        
        return filtered_studies
        
    def _filter_syntheses(self, query: EvidenceQuery) -> List[EvidenceSynthesis]:
        """Filter syntheses based on query criteria"""
        filtered_syntheses = []
        
        for synthesis in self.syntheses.values():
            # Check condition
            if query.condition and query.condition.lower() not in synthesis.condition.lower():
                continue
                
            # Check intervention
            if query.intervention and query.intervention.lower() not in ' '.join(synthesis.interventions).lower():
                continue
                
            # Check outcome
            if query.outcome and query.outcome.lower() not in ' '.join(synthesis.outcomes).lower():
                continue
                
            # Check quality
            quality_order = [EvidenceQuality.HIGH, EvidenceQuality.MODERATE, EvidenceQuality.LOW, EvidenceQuality.VERY_LOW]
            min_quality_index = quality_order.index(query.min_quality)
            synthesis_quality_index = quality_order.index(synthesis.evidence_quality)
            if synthesis_quality_index > min_quality_index:
                continue
                
            # Check date range
            if query.date_from and synthesis.publication_date < query.date_from:
                continue
            if query.date_to and synthesis.publication_date > query.date_to:
                continue
                
            filtered_syntheses.append(synthesis)
            
        # Sort by quality and date
        filtered_syntheses.sort(key=lambda x: (quality_order.index(x.evidence_quality), x.publication_date), reverse=True)
        
        return filtered_syntheses
        
    def _generate_evidence_summary(self, studies: List[ClinicalStudy], 
                                 syntheses: List[EvidenceSynthesis]) -> Dict[str, Any]:
        """Generate summary of evidence"""
        summary = {
            'total_studies': len(studies),
            'total_syntheses': len(syntheses),
            'study_types': {},
            'evidence_quality': {},
            'interventions': {},
            'outcomes': {},
            'key_findings': [],
            'strength_of_evidence': 'insufficient'
        }
        
        # Count study types
        for study in studies:
            study_type = study.study_type.value
            summary['study_types'][study_type] = summary['study_types'].get(study_type, 0) + 1
            
        # Count evidence quality
        for study in studies:
            quality = study.evidence_quality.value
            summary['evidence_quality'][quality] = summary['evidence_quality'].get(quality, 0) + 1
            
        # Count interventions
        for study in studies:
            for intervention in study.interventions:
                summary['interventions'][intervention] = summary['interventions'].get(intervention, 0) + 1
                
        # Count outcomes
        for study in studies:
            for outcome in study.outcomes:
                summary['outcomes'][outcome] = summary['outcomes'].get(outcome, 0) + 1
                
        # Extract key findings
        for study in studies[:5]:  # Top 5 studies
            summary['key_findings'].append({
                'title': study.title,
                'conclusion': study.conclusions,
                'quality': study.evidence_quality.value
            })
            
        # Determine strength of evidence
        high_quality_count = summary['evidence_quality'].get('high', 0)
        moderate_quality_count = summary['evidence_quality'].get('moderate', 0)
        
        if high_quality_count >= 3:
            summary['strength_of_evidence'] = 'strong'
        elif high_quality_count >= 1 or moderate_quality_count >= 3:
            summary['strength_of_evidence'] = 'moderate'
        elif moderate_quality_count >= 1:
            summary['strength_of_evidence'] = 'weak'
        else:
            summary['strength_of_evidence'] = 'insufficient'
            
        return summary
        
    def _calculate_evidence_confidence(self, studies: List[ClinicalStudy], 
                                     syntheses: List[EvidenceSynthesis]) -> float:
        """Calculate confidence in evidence"""
        if not studies and not syntheses:
            return 0.0
            
        confidence = 0.0
        
        # Base confidence on number of studies
        study_confidence = min(1.0, len(studies) / 10.0)  # Normalize to 10 studies
        confidence += study_confidence * 0.4
        
        # Quality confidence
        quality_scores = {EvidenceQuality.HIGH: 1.0, EvidenceQuality.MODERATE: 0.7, 
                         EvidenceQuality.LOW: 0.4, EvidenceQuality.VERY_LOW: 0.2}
        
        if studies:
            avg_quality = sum(quality_scores[study.evidence_quality] for study in studies) / len(studies)
            confidence += avg_quality * 0.4
        else:
            confidence += 0.2
            
        # Synthesis confidence
        synthesis_confidence = min(1.0, len(syntheses) / 5.0)  # Normalize to 5 syntheses
        confidence += synthesis_confidence * 0.2
        
        return min(1.0, confidence)
        
    def _load_default_evidence(self):
        """Load default clinical evidence"""
        # Default studies
        default_studies = [
            ClinicalStudy(
                study_id="study_001",
                title="Metformin for Type 2 Diabetes: A Systematic Review",
                authors=["Smith J", "Johnson A", "Brown K"],
                study_type=StudyType.SYSTEMATIC_REVIEW,
                evidence_quality=EvidenceQuality.HIGH,
                publication_status=PublicationStatus.PUBLISHED,
                journal="Diabetes Care",
                doi="10.2337/dc23-001",
                pubmed_id="12345678",
                publication_date=datetime(2023, 6, 15),
                abstract="Systematic review of metformin efficacy in type 2 diabetes management",
                keywords=["diabetes", "metformin", "systematic review"],
                interventions=["metformin"],
                outcomes=["glycemic control", "cardiovascular outcomes", "weight loss"],
                population={"age_range": "18-75", "diabetes_type": "type_2"},
                results={"glycemic_control": "significant improvement", "weight_loss": "moderate"},
                conclusions="Metformin is effective for glycemic control and weight management in type 2 diabetes",
                limitations=["heterogeneity in study designs", "limited long-term data"],
                funding_source="National Institutes of Health"
            ),
            ClinicalStudy(
                study_id="study_002",
                title="ACE Inhibitors in Hypertension: Meta-analysis",
                authors=["Davis M", "Wilson P", "Taylor R"],
                study_type=StudyType.META_ANALYSIS,
                evidence_quality=EvidenceQuality.HIGH,
                publication_status=PublicationStatus.PUBLISHED,
                journal="Hypertension",
                doi="10.1161/HYP.2023.001",
                pubmed_id="87654321",
                publication_date=datetime(2023, 3, 20),
                abstract="Meta-analysis of ACE inhibitor effectiveness in hypertension",
                keywords=["hypertension", "ace inhibitors", "meta-analysis"],
                interventions=["ace_inhibitors"],
                outcomes=["blood_pressure_reduction", "cardiovascular_events"],
                population={"age_range": "18-80", "condition": "hypertension"},
                results={"bp_reduction": "15/10 mmHg", "cv_events": "25% reduction"},
                conclusions="ACE inhibitors significantly reduce blood pressure and cardiovascular events",
                limitations=["variation in dosing", "short follow-up periods"],
                funding_source="American Heart Association"
            ),
            ClinicalStudy(
                study_id="study_003",
                title="Lifestyle Modification in Diabetes Prevention",
                authors=["Garcia L", "Martinez S", "Rodriguez M"],
                study_type=StudyType.RANDOMIZED_CONTROLLED_TRIAL,
                evidence_quality=EvidenceQuality.HIGH,
                publication_status=PublicationStatus.PUBLISHED,
                journal="New England Journal of Medicine",
                doi="10.1056/NEJM.2023.001",
                pubmed_id="11223344",
                publication_date=datetime(2023, 1, 10),
                abstract="Randomized trial of lifestyle intervention for diabetes prevention",
                keywords=["diabetes prevention", "lifestyle", "randomized trial"],
                interventions=["diet", "exercise", "weight_loss"],
                outcomes=["diabetes_incidence", "weight_loss", "glucose_levels"],
                population={"age_range": "45-65", "risk": "prediabetes"},
                results={"diabetes_incidence": "58% reduction", "weight_loss": "7% average"},
                conclusions="Lifestyle modification significantly reduces diabetes incidence in high-risk individuals",
                limitations=["intensive intervention", "limited generalizability"],
                funding_source="Centers for Disease Control"
            )
        ]
        
        # Default syntheses
        default_syntheses = [
            EvidenceSynthesis(
                synthesis_id="synthesis_001",
                title="Diabetes Management: Evidence Synthesis",
                type="systematic_review",
                condition="diabetes mellitus",
                interventions=["metformin", "lifestyle", "insulin"],
                outcomes=["glycemic_control", "complications", "quality_of_life"],
                included_studies=["study_001", "study_003"],
                evidence_quality=EvidenceQuality.HIGH,
                conclusions="Comprehensive evidence supports metformin and lifestyle modification for diabetes management",
                recommendations=[
                    {"intervention": "metformin", "strength": "strong", "evidence": "high"},
                    {"intervention": "lifestyle_modification", "strength": "moderate", "evidence": "high"}
                ],
                publication_date=datetime(2023, 8, 1),
                source="Cochrane Collaboration"
            ),
            EvidenceSynthesis(
                synthesis_id="synthesis_002",
                title="Hypertension Treatment: Evidence Summary",
                type="meta_analysis",
                condition="hypertension",
                interventions=["ace_inhibitors", "beta_blockers", "calcium_channel_blockers"],
                outcomes=["blood_pressure", "cardiovascular_events", "mortality"],
                included_studies=["study_002"],
                evidence_quality=EvidenceQuality.HIGH,
                conclusions="ACE inhibitors are effective first-line therapy for hypertension",
                recommendations=[
                    {"intervention": "ace_inhibitors", "strength": "strong", "evidence": "high"},
                    {"intervention": "lifestyle_modification", "strength": "moderate", "evidence": "moderate"}
                ],
                publication_date=datetime(2023, 5, 15),
                source="American College of Cardiology"
            )
        ]
        
        # Add to storage
        for study in default_studies:
            self.studies[study.study_id] = study
            
        for synthesis in default_syntheses:
            self.syntheses[synthesis.synthesis_id] = synthesis
            
        logger.info(f"Loaded {len(default_studies)} default studies and {len(default_syntheses)} syntheses")

# Initialize evidence base
evidence_base = EvidenceBase()

# Example usage functions
async def initialize_evidence_base():
    """Initialize the evidence base"""
    await evidence_base.load_evidence_base()

def search_diabetes_evidence() -> EvidenceResult:
    """Search for diabetes-related evidence"""
    query = EvidenceQuery(
        condition="diabetes",
        min_quality=EvidenceQuality.MODERATE,
        max_results=20
    )
    return evidence_base.search_evidence(query)

def search_hypertension_evidence() -> EvidenceResult:
    """Search for hypertension-related evidence"""
    query = EvidenceQuery(
        condition="hypertension",
        min_quality=EvidenceQuality.MODERATE,
        max_results=20
    )
    return evidence_base.search_evidence(query)

def search_metformin_evidence() -> EvidenceResult:
    """Search for metformin-related evidence"""
    query = EvidenceQuery(
        intervention="metformin",
        min_quality=EvidenceQuality.MODERATE,
        max_results=15
    )
    return evidence_base.search_evidence(query) 