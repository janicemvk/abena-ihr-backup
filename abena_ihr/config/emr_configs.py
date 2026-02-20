"""
EMR Configurations

This module contains configuration for EMR (Electronic Medical Record) integrations.
"""

EMR_CONFIGS = {
    "default": {
        "provider": "GenericEMR",
        "api_url": "https://emr.example.com/api",
        "api_key": "your_api_key_here",
        "timeout": 30,
        "features": ["patient_sync", "lab_results", "clinical_notes"]
    }
} 