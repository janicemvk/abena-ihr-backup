"""
Abena IHR System - Main Package

This is the main package for the Abena Intelligent Health Recommendation System.
It provides a comprehensive healthcare decision support platform that integrates
clinical expertise with advanced predictive analytics and continuous learning.

Modules:
    core: Core system components including conflict resolution, model management,
          integrated architecture, and system reconciliation
    api: REST API endpoints and web service interfaces
    clinical_context: Clinical decision support and guidelines integration
    predictive_analytics: Machine learning models and prediction engines
    feedback_loop: Continuous learning and outcome tracking
    integration: External system integration components
    workflow_integration: Clinical workflow integration tools
"""

from . import core

__version__ = "1.0.0"
__author__ = "Abena IHR Development Team"
__description__ = "Intelligent Health Recommendation System"

# Main system components
__all__ = [
    'core',
    'api',
    'clinical_context', 
    'predictive_analytics',
    'feedback_loop',
    'integration',
    'workflow_integration'
] 