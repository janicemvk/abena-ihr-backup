"""
Medical Ontologies for Abena IHR
================================

This module provides medical ontology and terminology capabilities including:
- Medical terminology standards
- Classification systems
- Ontology mapping
- Semantic medical search
- Terminology validation
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
class OntologyType(Enum):
    ICD10 = "icd10"
    SNOMED_CT = "snomed_ct"
    LOINC = "loinc"
    RX_NORM = "rx_norm"
    UMLS = "umls"
    CUSTOM = "custom"

class ConceptStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    DRAFT = "draft"

class RelationshipType(Enum):
    IS_A = "is_a"
    PART_OF = "part_of"
    LOCATED_IN = "located_in"
    CAUSES = "causes"
    TREATS = "treats"
    INDICATES = "indicates"
    SYNONYM = "synonym"
    TRANSLATION = "translation"

# Pydantic models
class OntologyConcept(BaseModel):
    """Ontology concept model"""
    concept_id: str
    ontology_type: OntologyType
    code: str
    name: str
    description: str
    status: ConceptStatus
    synonyms: List[str] = []
    parent_concepts: List[str] = []
    child_concepts: List[str] = []
    relationships: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    last_updated: datetime

class OntologyMapping(BaseModel):
    """Ontology mapping model"""
    mapping_id: str
    source_concept: str
    target_concept: str
    source_ontology: OntologyType
    target_ontology: OntologyType
    relationship_type: RelationshipType
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: str
    created_by: str
    created_at: datetime
    last_updated: datetime

class TerminologyQuery(BaseModel):
    """Terminology query model"""
    query_text: str
    ontology_types: List[OntologyType] = []
    include_synonyms: bool = True
    include_relationships: bool = False
    max_results: int = 20
    min_confidence: float = 0.5

class TerminologyResult(BaseModel):
    """Terminology query result"""
    query_id: str
    concepts: List[OntologyConcept]
    mappings: List[OntologyMapping]
    total_concepts: int
    total_mappings: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime

class MedicalOntologies:
    """Medical ontologies management system"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.concepts = {}
        self.mappings = {}
        self.ontologies = {}
        
    async def load_ontologies(self):
        """Load medical ontologies from storage"""
        try:
            # Load concepts from Redis or database
            concept_keys = self.redis_client.keys("concept:*")
            for key in concept_keys:
                concept_data = self.redis_client.get(key)
                if concept_data:
                    concept_dict = json.loads(concept_data)
                    concept = OntologyConcept(**concept_dict)
                    self.concepts[concept.concept_id] = concept
                    
            # Load mappings
            mapping_keys = self.redis_client.keys("mapping:*")
            for key in mapping_keys:
                mapping_data = self.redis_client.get(key)
                if mapping_data:
                    mapping_dict = json.loads(mapping_data)
                    mapping = OntologyMapping(**mapping_dict)
                    self.mappings[mapping.mapping_id] = mapping
                    
            logger.info(f"Loaded {len(self.concepts)} concepts and {len(self.mappings)} mappings")
            
        except Exception as e:
            logger.error(f"Error loading ontologies: {e}")
            # Load default ontologies if Redis is not available
            self._load_default_ontologies()
            
    def search_terminology(self, query: TerminologyQuery) -> TerminologyResult:
        """Search medical terminology"""
        try:
            query_id = f"terminology_{datetime.now().timestamp()}"
            
            # Search concepts
            concepts = self._search_concepts(query)
            
            # Search mappings
            mappings = self._search_mappings(query)
            
            # Calculate confidence
            confidence = self._calculate_terminology_confidence(concepts, mappings, query)
            
            return TerminologyResult(
                query_id=query_id,
                concepts=concepts[:query.max_results],
                mappings=mappings[:query.max_results],
                total_concepts=len(concepts),
                total_mappings=len(mappings),
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error searching terminology: {e}")
            raise
            
    def add_concept(self, concept: OntologyConcept):
        """Add an ontology concept"""
        try:
            self.concepts[concept.concept_id] = concept
            
            # Store in Redis
            concept_key = f"concept:{concept.concept_id}"
            self.redis_client.setex(
                concept_key,
                86400,  # 24 hours TTL
                json.dumps(concept.dict())
            )
            
            logger.info(f"Added ontology concept: {concept.name}")
            
        except Exception as e:
            logger.error(f"Error adding concept: {e}")
            raise
            
    def add_mapping(self, mapping: OntologyMapping):
        """Add an ontology mapping"""
        try:
            self.mappings[mapping.mapping_id] = mapping
            
            # Store in Redis
            mapping_key = f"mapping:{mapping.mapping_id}"
            self.redis_client.setex(
                mapping_key,
                86400,  # 24 hours TTL
                json.dumps(mapping.dict())
            )
            
            logger.info(f"Added ontology mapping: {mapping.source_concept} -> {mapping.target_concept}")
            
        except Exception as e:
            logger.error(f"Error adding mapping: {e}")
            raise
            
    def get_concept_by_code(self, code: str, ontology_type: OntologyType) -> Optional[OntologyConcept]:
        """Get concept by code and ontology type"""
        for concept in self.concepts.values():
            if concept.code == code and concept.ontology_type == ontology_type:
                return concept
        return None
        
    def get_concept_relationships(self, concept_id: str) -> List[Dict[str, Any]]:
        """Get relationships for a concept"""
        if concept_id not in self.concepts:
            return []
            
        concept = self.concepts[concept_id]
        relationships = []
        
        # Add direct relationships
        relationships.extend(concept.relationships)
        
        # Add parent relationships
        for parent_id in concept.parent_concepts:
            if parent_id in self.concepts:
                parent = self.concepts[parent_id]
                relationships.append({
                    'type': 'parent',
                    'target_concept': parent_id,
                    'target_name': parent.name,
                    'ontology_type': parent.ontology_type.value
                })
                
        # Add child relationships
        for child_id in concept.child_concepts:
            if child_id in self.concepts:
                child = self.concepts[child_id]
                relationships.append({
                    'type': 'child',
                    'target_concept': child_id,
                    'target_name': child.name,
                    'ontology_type': child.ontology_type.value
                })
                
        return relationships
        
    def map_between_ontologies(self, source_code: str, source_ontology: OntologyType, 
                              target_ontology: OntologyType) -> List[OntologyMapping]:
        """Map concepts between ontologies"""
        mappings = []
        
        for mapping in self.mappings.values():
            if (mapping.source_ontology == source_ontology and 
                mapping.target_ontology == target_ontology and
                mapping.source_concept == source_code):
                mappings.append(mapping)
                
        return mappings
        
    def validate_terminology(self, text: str, ontology_type: OntologyType) -> List[Dict[str, Any]]:
        """Validate terminology against ontology"""
        results = []
        
        # Simple tokenization (in practice, would use more sophisticated NLP)
        tokens = text.lower().split()
        
        for concept in self.concepts.values():
            if concept.ontology_type != ontology_type:
                continue
                
            # Check exact match
            if concept.name.lower() in text.lower():
                results.append({
                    'concept_id': concept.concept_id,
                    'code': concept.code,
                    'name': concept.name,
                    'match_type': 'exact',
                    'confidence': 1.0
                })
                continue
                
            # Check synonym matches
            for synonym in concept.synonyms:
                if synonym.lower() in text.lower():
                    results.append({
                        'concept_id': concept.concept_id,
                        'code': concept.code,
                        'name': concept.name,
                        'match_type': 'synonym',
                        'confidence': 0.8
                    })
                    break
                    
            # Check partial matches
            for token in tokens:
                if token in concept.name.lower():
                    results.append({
                        'concept_id': concept.concept_id,
                        'code': concept.code,
                        'name': concept.name,
                        'match_type': 'partial',
                        'confidence': 0.6
                    })
                    break
                    
        return results
        
    def _search_concepts(self, query: TerminologyQuery) -> List[OntologyConcept]:
        """Search for concepts"""
        results = []
        
        for concept in self.concepts.values():
            if concept.status != ConceptStatus.ACTIVE:
                continue
                
            # Filter by ontology type
            if query.ontology_types and concept.ontology_type not in query.ontology_types:
                continue
                
            # Check name match
            if query.query_text.lower() in concept.name.lower():
                results.append(concept)
                continue
                
            # Check synonym matches
            if query.include_synonyms:
                for synonym in concept.synonyms:
                    if query.query_text.lower() in synonym.lower():
                        results.append(concept)
                        break
                        
        # Sort by relevance (simplified)
        results.sort(key=lambda x: len(x.name), reverse=False)
        
        return results
        
    def _search_mappings(self, query: TerminologyQuery) -> List[OntologyMapping]:
        """Search for mappings"""
        results = []
        
        for mapping in self.mappings.values():
            if mapping.confidence < query.min_confidence:
                continue
                
            # Check if mapping involves concepts matching the query
            source_concept = self.concepts.get(mapping.source_concept)
            target_concept = self.concepts.get(mapping.target_concept)
            
            if source_concept and query.query_text.lower() in source_concept.name.lower():
                results.append(mapping)
            elif target_concept and query.query_text.lower() in target_concept.name.lower():
                results.append(mapping)
                
        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        return results
        
    def _calculate_terminology_confidence(self, concepts: List[OntologyConcept], 
                                        mappings: List[OntologyMapping], 
                                        query: TerminologyQuery) -> float:
        """Calculate confidence in terminology search results"""
        if not concepts and not mappings:
            return 0.0
            
        confidence = 0.0
        
        # Concept confidence
        if concepts:
            concept_confidence = min(1.0, len(concepts) / 10.0)  # Normalize to 10 concepts
            confidence += concept_confidence * 0.6
            
        # Mapping confidence
        if mappings:
            avg_mapping_confidence = sum(m.confidence for m in mappings) / len(mappings)
            confidence += avg_mapping_confidence * 0.4
            
        return min(1.0, confidence)
        
    def _load_default_ontologies(self):
        """Load default medical ontologies"""
        # Default concepts
        default_concepts = [
            OntologyConcept(
                concept_id="icd10_e11",
                ontology_type=OntologyType.ICD10,
                code="E11",
                name="Type 2 diabetes mellitus",
                description="Diabetes mellitus due to insulin resistance",
                status=ConceptStatus.ACTIVE,
                synonyms=["T2DM", "Non-insulin dependent diabetes", "Adult-onset diabetes"],
                parent_concepts=["icd10_e10_e14"],
                child_concepts=["icd10_e11_9"],
                relationships=[
                    {"type": "causes", "target": "complications", "description": "Can cause various complications"}
                ],
                last_updated=datetime.now()
            ),
            OntologyConcept(
                concept_id="icd10_i10",
                ontology_type=OntologyType.ICD10,
                code="I10",
                name="Essential (primary) hypertension",
                description="High blood pressure without identifiable cause",
                status=ConceptStatus.ACTIVE,
                synonyms=["HTN", "High blood pressure", "Primary hypertension"],
                parent_concepts=["icd10_i10_i15"],
                child_concepts=[],
                relationships=[
                    {"type": "risk_factor", "target": "cardiovascular_disease", "description": "Risk factor for CVD"}
                ],
                last_updated=datetime.now()
            ),
            OntologyConcept(
                concept_id="snomed_73211009",
                ontology_type=OntologyType.SNOMED_CT,
                code="73211009",
                name="Diabetes mellitus",
                description="Disorder of carbohydrate metabolism",
                status=ConceptStatus.ACTIVE,
                synonyms=["DM", "Diabetes", "Sugar diabetes"],
                parent_concepts=["snomed_disorder"],
                child_concepts=["snomed_type1_diabetes", "snomed_type2_diabetes"],
                relationships=[
                    {"type": "has_finding", "target": "elevated_glucose", "description": "Associated with high glucose"}
                ],
                last_updated=datetime.now()
            ),
            OntologyConcept(
                concept_id="loinc_2345_7",
                ontology_type=OntologyType.LOINC,
                code="2345-7",
                name="Glucose [Mass/volume] in Serum or Plasma",
                description="Glucose measurement in blood",
                status=ConceptStatus.ACTIVE,
                synonyms=["Blood glucose", "Serum glucose", "Plasma glucose"],
                parent_concepts=["loinc_chemistry"],
                child_concepts=[],
                relationships=[
                    {"type": "measures", "target": "glucose_metabolism", "description": "Measures glucose levels"}
                ],
                last_updated=datetime.now()
            ),
            OntologyConcept(
                concept_id="rxnorm_6809",
                ontology_type=OntologyType.RX_NORM,
                code="6809",
                name="Metformin 500 MG Oral Tablet",
                description="Metformin tablet for diabetes treatment",
                status=ConceptStatus.ACTIVE,
                synonyms=["Glucophage", "Fortamet", "Metformin tablet"],
                parent_concepts=["rxnorm_metformin"],
                child_concepts=[],
                relationships=[
                    {"type": "treats", "target": "diabetes_mellitus", "description": "Treats type 2 diabetes"}
                ],
                last_updated=datetime.now()
            )
        ]
        
        # Default mappings
        default_mappings = [
            OntologyMapping(
                mapping_id="map_001",
                source_concept="icd10_e11",
                target_concept="snomed_73211009",
                source_ontology=OntologyType.ICD10,
                target_ontology=OntologyType.SNOMED_CT,
                relationship_type=RelationshipType.IS_A,
                confidence=0.9,
                evidence="Standard mapping",
                created_by="system",
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            OntologyMapping(
                mapping_id="map_002",
                source_concept="snomed_73211009",
                target_concept="rxnorm_6809",
                source_ontology=OntologyType.SNOMED_CT,
                target_ontology=OntologyType.RX_NORM,
                relationship_type=RelationshipType.TREATS,
                confidence=0.8,
                evidence="Clinical guidelines",
                created_by="system",
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            OntologyMapping(
                mapping_id="map_003",
                source_concept="loinc_2345_7",
                target_concept="snomed_73211009",
                source_ontology=OntologyType.LOINC,
                target_ontology=OntologyType.SNOMED_CT,
                relationship_type=RelationshipType.INDICATES,
                confidence=0.7,
                evidence="Clinical correlation",
                created_by="system",
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
        ]
        
        # Add to storage
        for concept in default_concepts:
            self.concepts[concept.concept_id] = concept
            
        for mapping in default_mappings:
            self.mappings[mapping.mapping_id] = mapping
            
        logger.info(f"Loaded {len(default_concepts)} default concepts and {len(default_mappings)} mappings")

# Initialize medical ontologies
medical_ontologies = MedicalOntologies()

# Example usage functions
async def initialize_ontologies():
    """Initialize the medical ontologies"""
    await medical_ontologies.load_ontologies()

def search_diabetes_terminology() -> TerminologyResult:
    """Search for diabetes-related terminology"""
    query = TerminologyQuery(
        query_text="diabetes",
        ontology_types=[OntologyType.ICD10, OntologyType.SNOMED_CT],
        include_synonyms=True,
        max_results=10
    )
    return medical_ontologies.search_terminology(query)

def validate_medical_text(text: str) -> List[Dict[str, Any]]:
    """Validate medical text against ontologies"""
    results = []
    for ontology_type in OntologyType:
        ontology_results = medical_ontologies.validate_terminology(text, ontology_type)
        results.extend(ontology_results)
    return results

def map_icd10_to_snomed(icd10_code: str) -> List[OntologyMapping]:
    """Map ICD-10 codes to SNOMED CT"""
    return medical_ontologies.map_between_ontologies(
        icd10_code, 
        OntologyType.ICD10, 
        OntologyType.SNOMED_CT
    ) 