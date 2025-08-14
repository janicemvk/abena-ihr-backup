"""
Medical Knowledge Graph for Abena IHR
====================================

This module provides medical knowledge graph capabilities including:
- Medical knowledge representation
- Clinical reasoning
- Knowledge graph queries
- Medical concept relationships
- Semantic medical search
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import redis
import networkx as nx
from pydantic import BaseModel, Field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class ConceptType(Enum):
    DISEASE = "disease"
    SYMPTOM = "symptom"
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    LAB_TEST = "lab_test"
    VITAL_SIGN = "vital_sign"
    ANATOMY = "anatomy"
    PHYSIOLOGY = "physiology"
    TREATMENT = "treatment"
    DIAGNOSIS = "diagnosis"

class RelationshipType(Enum):
    CAUSES = "causes"
    TREATS = "treats"
    INDICATES = "indicates"
    CONTRAINDICATES = "contraindicates"
    INTERACTS_WITH = "interacts_with"
    LOCATED_IN = "located_in"
    PART_OF = "part_of"
    ASSOCIATED_WITH = "associated_with"
    PREDISPOSES_TO = "predisposes_to"
    MANIFESTS_AS = "manifests_as"

# Pydantic models
class MedicalConcept(BaseModel):
    """Medical concept model"""
    concept_id: str
    name: str
    concept_type: ConceptType
    description: str
    synonyms: List[str] = []
    icd10_codes: List[str] = []
    snomed_codes: List[str] = []
    evidence_level: str = Field(..., regex="^(A|B|C|D)$")
    source: str
    last_updated: datetime
    metadata: Dict[str, Any] = {}

class ConceptRelationship(BaseModel):
    """Concept relationship model"""
    relationship_id: str
    source_concept: str
    target_concept: str
    relationship_type: RelationshipType
    strength: float = Field(..., ge=0.0, le=1.0)
    evidence_level: str = Field(..., regex="^(A|B|C|D)$")
    source: str
    description: str
    last_updated: datetime
    metadata: Dict[str, Any] = {}

class KnowledgeQuery(BaseModel):
    """Knowledge query model"""
    query_type: str
    concept_id: Optional[str] = None
    concept_name: Optional[str] = None
    relationship_type: Optional[RelationshipType] = None
    max_depth: int = 3
    max_results: int = 50
    filters: Dict[str, Any] = {}

class KnowledgeResult(BaseModel):
    """Knowledge query result model"""
    query_id: str
    results: List[Dict[str, Any]]
    total_results: int
    execution_time: float
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime

class MedicalKnowledgeGraph:
    """Medical knowledge graph engine"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.graph = nx.DiGraph()
        self.concepts = {}
        self.relationships = {}
        
    async def load_knowledge_graph(self):
        """Load medical knowledge graph from storage"""
        try:
            # Load concepts from Redis or database
            concept_keys = self.redis_client.keys("concept:*")
            for key in concept_keys:
                concept_data = self.redis_client.get(key)
                if concept_data:
                    concept_dict = json.loads(concept_data)
                    concept = MedicalConcept(**concept_dict)
                    self.concepts[concept.concept_id] = concept
                    
            # Load relationships
            relationship_keys = self.redis_client.keys("relationship:*")
            for key in relationship_keys:
                relationship_data = self.redis_client.get(key)
                if relationship_data:
                    relationship_dict = json.loads(relationship_data)
                    relationship = ConceptRelationship(**relationship_dict)
                    self.relationships[relationship.relationship_id] = relationship
                    
            # Build graph
            self._build_graph()
                    
            logger.info(f"Loaded {len(self.concepts)} concepts and {len(self.relationships)} relationships")
            
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {e}")
            # Load default knowledge if Redis is not available
            self._load_default_knowledge()
            
    def query_knowledge(self, query: KnowledgeQuery) -> KnowledgeResult:
        """Query the medical knowledge graph"""
        try:
            start_time = datetime.now()
            query_id = f"query_{start_time.timestamp()}"
            
            results = []
            
            if query.query_type == "concept_search":
                results = self._search_concepts(query)
            elif query.query_type == "relationship_search":
                results = self._search_relationships(query)
            elif query.query_type == "path_search":
                results = self._search_paths(query)
            elif query.query_type == "neighborhood_search":
                results = self._search_neighborhood(query)
            else:
                raise ValueError(f"Unknown query type: {query.query_type}")
                
            execution_time = (datetime.now() - start_time).total_seconds()
            confidence = self._calculate_query_confidence(query, results)
            
            return KnowledgeResult(
                query_id=query_id,
                results=results[:query.max_results],
                total_results=len(results),
                execution_time=execution_time,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error querying knowledge graph: {e}")
            raise
            
    def add_concept(self, concept: MedicalConcept):
        """Add a medical concept to the knowledge graph"""
        try:
            self.concepts[concept.concept_id] = concept
            
            # Add to graph
            self.graph.add_node(concept.concept_id, **concept.dict())
            
            # Store in Redis
            concept_key = f"concept:{concept.concept_id}"
            self.redis_client.setex(
                concept_key,
                86400,  # 24 hours TTL
                json.dumps(concept.dict())
            )
            
            logger.info(f"Added medical concept: {concept.name}")
            
        except Exception as e:
            logger.error(f"Error adding concept: {e}")
            raise
            
    def add_relationship(self, relationship: ConceptRelationship):
        """Add a relationship to the knowledge graph"""
        try:
            self.relationships[relationship.relationship_id] = relationship
            
            # Add to graph
            self.graph.add_edge(
                relationship.source_concept,
                relationship.target_concept,
                **relationship.dict()
            )
            
            # Store in Redis
            relationship_key = f"relationship:{relationship.relationship_id}"
            self.redis_client.setex(
                relationship_key,
                86400,  # 24 hours TTL
                json.dumps(relationship.dict())
            )
            
            logger.info(f"Added relationship: {relationship.source_concept} -> {relationship.target_concept}")
            
        except Exception as e:
            logger.error(f"Error adding relationship: {e}")
            raise
            
    def _build_graph(self):
        """Build the knowledge graph from concepts and relationships"""
        try:
            # Clear existing graph
            self.graph.clear()
            
            # Add nodes (concepts)
            for concept in self.concepts.values():
                self.graph.add_node(concept.concept_id, **concept.dict())
                
            # Add edges (relationships)
            for relationship in self.relationships.values():
                self.graph.add_edge(
                    relationship.source_concept,
                    relationship.target_concept,
                    **relationship.dict()
                )
                
            logger.info(f"Built knowledge graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            
        except Exception as e:
            logger.error(f"Error building graph: {e}")
            raise
            
    def _search_concepts(self, query: KnowledgeQuery) -> List[Dict[str, Any]]:
        """Search for concepts"""
        results = []
        
        if query.concept_id:
            if query.concept_id in self.concepts:
                concept = self.concepts[query.concept_id]
                results.append({
                    'type': 'concept',
                    'data': concept.dict(),
                    'score': 1.0
                })
        elif query.concept_name:
            # Fuzzy search by name
            for concept in self.concepts.values():
                if query.concept_name.lower() in concept.name.lower():
                    score = len(query.concept_name) / len(concept.name)
                    results.append({
                        'type': 'concept',
                        'data': concept.dict(),
                        'score': score
                    })
                    
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
        
    def _search_relationships(self, query: KnowledgeQuery) -> List[Dict[str, Any]]:
        """Search for relationships"""
        results = []
        
        if query.concept_id:
            # Find relationships involving this concept
            for relationship in self.relationships.values():
                if (relationship.source_concept == query.concept_id or 
                    relationship.target_concept == query.concept_id):
                    results.append({
                        'type': 'relationship',
                        'data': relationship.dict(),
                        'score': relationship.strength
                    })
                    
        if query.relationship_type:
            # Filter by relationship type
            filtered_results = []
            for result in results:
                if result['data']['relationship_type'] == query.relationship_type.value:
                    filtered_results.append(result)
            results = filtered_results
            
        # Sort by strength
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
        
    def _search_paths(self, query: KnowledgeQuery) -> List[Dict[str, Any]]:
        """Search for paths between concepts"""
        results = []
        
        if query.concept_id:
            # Find paths from this concept
            try:
                paths = nx.single_source_shortest_path(
                    self.graph, 
                    query.concept_id, 
                    cutoff=query.max_depth
                )
                
                for target, path in paths.items():
                    if target != query.concept_id:
                        path_strength = self._calculate_path_strength(path)
                        results.append({
                            'type': 'path',
                            'source': query.concept_id,
                            'target': target,
                            'path': path,
                            'length': len(path) - 1,
                            'strength': path_strength,
                            'score': path_strength / len(path)
                        })
                        
            except nx.NetworkXNoPath:
                pass
                
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
        
    def _search_neighborhood(self, query: KnowledgeQuery) -> List[Dict[str, Any]]:
        """Search for concept neighborhood"""
        results = []
        
        if query.concept_id and query.concept_id in self.graph:
            # Get neighbors
            neighbors = list(self.graph.neighbors(query.concept_id))
            predecessors = list(self.graph.predecessors(query.concept_id))
            
            # Add neighbors
            for neighbor in neighbors:
                if neighbor in self.concepts:
                    concept = self.concepts[neighbor]
                    edge_data = self.graph.get_edge_data(query.concept_id, neighbor)
                    results.append({
                        'type': 'neighbor',
                        'relationship': 'outgoing',
                        'concept': concept.dict(),
                        'relationship_data': edge_data,
                        'score': edge_data.get('strength', 0.5) if edge_data else 0.5
                    })
                    
            # Add predecessors
            for predecessor in predecessors:
                if predecessor in self.concepts:
                    concept = self.concepts[predecessor]
                    edge_data = self.graph.get_edge_data(predecessor, query.concept_id)
                    results.append({
                        'type': 'neighbor',
                        'relationship': 'incoming',
                        'concept': concept.dict(),
                        'relationship_data': edge_data,
                        'score': edge_data.get('strength', 0.5) if edge_data else 0.5
                    })
                    
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
        
    def _calculate_path_strength(self, path: List[str]) -> float:
        """Calculate the strength of a path"""
        if len(path) < 2:
            return 0.0
            
        strength = 1.0
        for i in range(len(path) - 1):
            edge_data = self.graph.get_edge_data(path[i], path[i + 1])
            if edge_data and 'strength' in edge_data:
                strength *= edge_data['strength']
            else:
                strength *= 0.5  # Default strength
                
        return strength
        
    def _calculate_query_confidence(self, query: KnowledgeQuery, results: List[Dict[str, Any]]) -> float:
        """Calculate confidence in query results"""
        if not results:
            return 0.0
            
        # Base confidence on result quality
        avg_score = sum(result.get('score', 0.0) for result in results) / len(results)
        
        # Adjust for query complexity
        complexity_factor = 1.0
        if query.max_depth > 2:
            complexity_factor = 0.9
        if query.filters:
            complexity_factor *= 0.95
            
        return min(1.0, avg_score * complexity_factor)
        
    def _load_default_knowledge(self):
        """Load default medical knowledge"""
        # Default concepts
        default_concepts = [
            MedicalConcept(
                concept_id="diabetes_mellitus",
                name="Diabetes Mellitus",
                concept_type=ConceptType.DISEASE,
                description="A group of metabolic disorders characterized by high blood sugar",
                synonyms=["DM", "Diabetes", "Sugar diabetes"],
                icd10_codes=["E11", "E10", "E13"],
                snomed_codes=["73211009"],
                evidence_level="A",
                source="ICD-10",
                last_updated=datetime.now()
            ),
            MedicalConcept(
                concept_id="hypertension",
                name="Hypertension",
                concept_type=ConceptType.DISEASE,
                description="High blood pressure",
                synonyms=["HTN", "High blood pressure"],
                icd10_codes=["I10", "I11", "I12", "I13"],
                snomed_codes=["38341003"],
                evidence_level="A",
                source="ICD-10",
                last_updated=datetime.now()
            ),
            MedicalConcept(
                concept_id="metformin",
                name="Metformin",
                concept_type=ConceptType.MEDICATION,
                description="Oral diabetes medication",
                synonyms=["Glucophage", "Fortamet"],
                icd10_codes=[],
                snomed_codes=["430193006"],
                evidence_level="A",
                source="FDA",
                last_updated=datetime.now()
            ),
            MedicalConcept(
                concept_id="elevated_glucose",
                name="Elevated Blood Glucose",
                concept_type=ConceptType.LAB_TEST,
                description="High blood sugar levels",
                synonyms=["Hyperglycemia", "High glucose"],
                icd10_codes=["R73.9"],
                snomed_codes=["386661006"],
                evidence_level="A",
                source="Lab Standards",
                last_updated=datetime.now()
            ),
            MedicalConcept(
                concept_id="weight_loss",
                name="Weight Loss",
                concept_type=ConceptType.SYMPTOM,
                description="Unintentional weight loss",
                synonyms=["Unintentional weight loss"],
                icd10_codes=["R63.4"],
                snomed_codes=["248336005"],
                evidence_level="B",
                source="ICD-10",
                last_updated=datetime.now()
            )
        ]
        
        # Default relationships
        default_relationships = [
            ConceptRelationship(
                relationship_id="rel_001",
                source_concept="diabetes_mellitus",
                target_concept="elevated_glucose",
                relationship_type=RelationshipType.CAUSES,
                strength=0.9,
                evidence_level="A",
                source="Clinical Guidelines",
                description="Diabetes causes elevated blood glucose",
                last_updated=datetime.now()
            ),
            ConceptRelationship(
                relationship_id="rel_002",
                source_concept="metformin",
                target_concept="diabetes_mellitus",
                relationship_type=RelationshipType.TREATS,
                strength=0.8,
                evidence_level="A",
                source="Clinical Trials",
                description="Metformin treats diabetes mellitus",
                last_updated=datetime.now()
            ),
            ConceptRelationship(
                relationship_id="rel_003",
                source_concept="diabetes_mellitus",
                target_concept="weight_loss",
                relationship_type=RelationshipType.MANIFESTS_AS,
                strength=0.6,
                evidence_level="B",
                source="Clinical Studies",
                description="Diabetes can manifest as weight loss",
                last_updated=datetime.now()
            ),
            ConceptRelationship(
                relationship_id="rel_004",
                source_concept="hypertension",
                target_concept="diabetes_mellitus",
                relationship_type=RelationshipType.ASSOCIATED_WITH,
                strength=0.7,
                evidence_level="A",
                source="Epidemiological Studies",
                description="Hypertension is associated with diabetes",
                last_updated=datetime.now()
            )
        ]
        
        # Add to storage
        for concept in default_concepts:
            self.concepts[concept.concept_id] = concept
            
        for relationship in default_relationships:
            self.relationships[relationship.relationship_id] = relationship
            
        # Build graph
        self._build_graph()
        
        logger.info(f"Loaded {len(default_concepts)} default concepts and {len(default_relationships)} relationships")

# Initialize medical knowledge graph
knowledge_graph = MedicalKnowledgeGraph()

# Example usage functions
async def initialize_knowledge_graph():
    """Initialize the knowledge graph"""
    await knowledge_graph.load_knowledge_graph()

def search_medical_concepts(query_text: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search for medical concepts"""
    query = KnowledgeQuery(
        query_type="concept_search",
        concept_name=query_text,
        max_results=max_results
    )
    result = knowledge_graph.query_knowledge(query)
    return result.results

def find_treatments_for_disease(disease_id: str) -> List[Dict[str, Any]]:
    """Find treatments for a disease"""
    query = KnowledgeQuery(
        query_type="relationship_search",
        concept_id=disease_id,
        relationship_type=RelationshipType.TREATS,
        max_results=20
    )
    result = knowledge_graph.query_knowledge(query)
    return result.results

def find_disease_symptoms(disease_id: str) -> List[Dict[str, Any]]:
    """Find symptoms of a disease"""
    query = KnowledgeQuery(
        query_type="relationship_search",
        concept_id=disease_id,
        relationship_type=RelationshipType.MANIFESTS_AS,
        max_results=20
    )
    result = knowledge_graph.query_knowledge(query)
    return result.results 