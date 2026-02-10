"""
Knowledge Base Package for Abena IHR Clinical Decision Support
=============================================================

This package provides medical knowledge graph capabilities including:
- Medical knowledge graphs
- Clinical guidelines
- Evidence-based medicine
- Medical ontologies
- Clinical reasoning
"""

from .medical_knowledge_graph import MedicalKnowledgeGraph
from .clinical_guidelines import ClinicalGuidelines
from .evidence_base import EvidenceBase
from .medical_ontologies import MedicalOntologies

__all__ = [
    'MedicalKnowledgeGraph',
    'ClinicalGuidelines', 
    'EvidenceBase',
    'MedicalOntologies'
]

__version__ = "1.0.0"
__author__ = "Abena IHR Team"
__description__ = "Medical knowledge base for clinical decision support" 