"""
Unified Configuration for Abena Predictive Analytics Engine
All systems consolidated through Abena SDK services only
"""

import os
from pathlib import Path
from typing import Dict, List

# Base paths
BASE_DIR = Path(__file__).parent
APPLICATION_SERVICES_DIR = BASE_DIR / "application-services"

# Application settings
APP_CONFIG = {
    "name": "Abena Predictive Analytics Engine",
    "version": "2.0.0",
    "description": "Unified AI-Powered Healthcare Analytics with Abena SDK",
    "author": "Abena Development Team",
    "license": "MIT",
    "environment": os.getenv("ENVIRONMENT", "development"),
    "debug": os.getenv("DEBUG", "False").lower() == "true"
}

# Abena SDK Service Configuration (ONLY source for auth, data, and audit)
ABENA_CONFIG = {
    "auth_service_url": os.getenv("AUTH_SERVICE_URL", "http://localhost:3001"),
    "data_service_url": os.getenv("DATA_SERVICE_URL", "http://localhost:8001"),
    "privacy_service_url": os.getenv("PRIVACY_SERVICE_URL", "http://localhost:8002"),
    "blockchain_service_url": os.getenv("BLOCKCHAIN_SERVICE_URL", "http://localhost:8003"),
    "analytics_service_url": os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8004")
}

# Model configurations (unified through Abena SDK)
MODEL_CONFIG = {
    'readmission_risk': {'version': '1.2.3', 'threshold': 0.6},
    'mortality_risk': {'version': '1.1.1', 'threshold': 0.8},
    'length_of_stay': {'version': '1.0.5', 'threshold': 0.5},
    'infection_risk': {'version': '1.3.2', 'threshold': 0.7},
    'medication_adherence': {'version': '1.1.8', 'threshold': 0.6},
    'treatment_response': {'version': '1.4.0', 'threshold': 0.5},
    'adverse_events': {'version': '1.2.1', 'threshold': 0.3}
}

# Clinical thresholds (unified)
CLINICAL_THRESHOLDS = {
    "risk_levels": {
        "critical": 0.8,
        "high": 0.6,
        "moderate": 0.4,
        "low": 0.2
    },
    "prediction_confidence": {
        "high": 0.8,
        "moderate": 0.6,
        "low": 0.4
    },
    "data_quality": {
        "excellent": 0.9,
        "good": 0.7,
        "acceptable": 0.5,
        "poor": 0.3
    }
}

# Privacy and Security Settings (ONLY through Abena SDK)
PRIVACY_CONFIG = {
    "anonymization": {
        "k_anonymity": 5,
        "differential_privacy_epsilon": 1.0,
        "quasi_identifiers": ["age", "gender", "zip_code", "diagnosis"]
    },
    "access_control": {
        "role_based": True,
        "purpose_based": True,
        "time_based": True
    },
    "audit": {
        "blockchain_logging": True,
        "immutable_records": True,
        "access_tracking": True
    }
}

# Feature configurations (unified)
FEATURE_CONFIG = {
    "patient_features": [
        "age", "gender", "chronic_conditions", "medications",
        "vital_signs", "lab_values", "encounters", "devices"
    ],
    "prediction_features": [
        "readmission_risk", "mortality_risk", "length_of_stay",
        "infection_risk", "medication_adherence", "treatment_response"
    ],
    "cohort_features": [
        "population_metrics", "risk_distribution", "quality_indicators"
    ]
}

# Logging configuration (ONLY through Abena SDK)
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console", "blockchain"],
    "blockchain_logging": True
}

# API Configuration (unified)
API_CONFIG = {
    "timeout": 30.0,
    "retry_attempts": 3,
    "rate_limiting": True,
    "caching": True
}

# Validation rules (unified)
VALIDATION_RULES = {
    "patient_id": r"^[A-Z0-9]{6,12}$",
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "date_format": "%Y-%m-%d",
    "datetime_format": "%Y-%m-%dT%H:%M:%S"
}

# Error messages (unified - Abena SDK only)
ERROR_MESSAGES = {
    "authentication_failed": "Abena SDK authentication failed. Please check credentials.",
    "access_denied": "Abena SDK access denied. Insufficient permissions.",
    "data_not_found": "Requested data not found in Abena data service.",
    "validation_error": "Data validation failed.",
    "service_unavailable": "Abena service temporarily unavailable.",
    "privacy_violation": "Privacy policy violation detected."
}

# Success messages (unified - Abena SDK only)
SUCCESS_MESSAGES = {
    "prediction_generated": "Prediction generated successfully through Abena SDK.",
    "cohort_analyzed": "Cohort analysis completed with anonymized data.",
    "recommendations_created": "Treatment recommendations created.",
    "audit_logged": "Action logged to Abena blockchain audit trail."
}

def get_config() -> Dict:
    """Get unified configuration (Abena SDK only)"""
    return {
        "app": APP_CONFIG,
        "abena": ABENA_CONFIG,
        "models": MODEL_CONFIG,
        "clinical": CLINICAL_THRESHOLDS,
        "privacy": PRIVACY_CONFIG,
        "features": FEATURE_CONFIG,
        "logging": LOGGING_CONFIG,
        "api": API_CONFIG,
        "validation": VALIDATION_RULES,
        "messages": {
            "errors": ERROR_MESSAGES,
            "success": SUCCESS_MESSAGES
        }
    }

def validate_environment() -> bool:
    """Validate that all required Abena SDK environment variables are set"""
    required_vars = [
        "AUTH_SERVICE_URL",
        "DATA_SERVICE_URL", 
        "PRIVACY_SERVICE_URL",
        "BLOCKCHAIN_SERVICE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing Abena SDK environment variables: {missing_vars}")
        print("💡 Set these variables or use default localhost URLs")
        return False
    
    return True

def get_service_urls() -> Dict[str, str]:
    """Get Abena SDK service URLs (ONLY source for services)"""
    return ABENA_CONFIG

def get_model_config(prediction_type: str) -> Dict:
    """Get configuration for specific prediction model"""
    return MODEL_CONFIG.get(prediction_type, {})

def get_privacy_settings() -> Dict:
    """Get privacy and security settings (Abena SDK only)"""
    return PRIVACY_CONFIG 