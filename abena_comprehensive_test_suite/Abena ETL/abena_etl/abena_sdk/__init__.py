"""
Abena SDK - Healthcare Data Integration and Analytics

A comprehensive SDK for healthcare data transformation, analytics, and integration
with EMR systems using FHIR standards.

This SDK provides:
- Secure authentication and authorization
- FHIR-compliant data transformation
- Real-time analytics and predictions
- EMR system integration
- Unit conversion and data mapping
"""

from .client import AbenaClient
from .auth import AbenaAuth
from .data import DataTransformer, FHIRConverter
from .analytics import AnalyticsEngine
from .config import AbenaConfig
from .exceptions import AbenaException, AuthenticationError, AuthorizationError

__version__ = "1.0.0"
__author__ = "Abena Development Team"
__description__ = "Healthcare Data Integration and Analytics SDK"

__all__ = [
    'AbenaClient',
    'AbenaAuth', 
    'DataTransformer',
    'FHIRConverter',
    'AnalyticsEngine',
    'AbenaConfig',
    'AbenaException',
    'AuthenticationError',
    'AuthorizationError'
] 