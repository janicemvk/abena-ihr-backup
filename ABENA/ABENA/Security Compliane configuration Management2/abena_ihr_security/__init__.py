"""
Abena IHR Security, Compliance & Configuration Management Module

This module provides comprehensive security,
compliance, and configuration management
for the Abena IHR (Integrated Health Records) system.
It follows the Abena SDK structure and implements HIPAA compliance,
data encryption, audit trails, and business rules processing.

Key Components:
- Data Masking & Anonymization
- Audit Trail Generation
- Encryption/Decryption Services
- HIPAA Compliance Validation
- Configuration Management
- Business Rules Engine
- Module Layer Orchestrator

Author: Abena Development Team
Version: 1.0.0
License: Proprietary - Abena Healthcare Solutions
"""

from .core.module_layer import ModuleLayer
from .core.encryption_service import EncryptionService
from .core.audit_generator import AuditTrailGenerator
from .core.data_masking import DataMaskingService
from .compliance.hipaa_validator import HIPAAComplianceValidator
from .config.manager import ConfigurationManager
from .rules.engine import BusinessRulesEngine

__version__ = "1.0.0"
__author__ = "Abena Development Team"
__license__ = "Proprietary"

__all__ = [
    "ModuleLayer",
    "EncryptionService",
    "AuditTrailGenerator",
    "DataMaskingService",
    "HIPAAComplianceValidator",
    "ConfigurationManager",
    "BusinessRulesEngine",
]
