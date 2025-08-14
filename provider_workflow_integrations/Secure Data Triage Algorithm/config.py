"""
Configuration settings for Abena Secure Data Triage Algorithm
"""

import os
from typing import Dict, List

class AbenaConfig:
    """Configuration class for the Abena Data Triage Algorithm"""
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('ABENA_LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('ABENA_LOG_FILE', 'abena_triage.log')
    
    # Security Configuration
    ENCRYPTION_KEY_PATH = os.getenv('ABENA_ENCRYPTION_KEY_PATH', 'encryption.key')
    
    # Privacy Parameters
    DIFFERENTIAL_PRIVACY_EPSILON = float(os.getenv('ABENA_DP_EPSILON', '0.1'))
    DEFAULT_K_ANONYMITY = {
        'PUBLIC': 1,
        'STATISTICAL': 5,
        'CLINICAL': 10,
        'PERSONAL': 20,
        'SENSITIVE': 20
    }
    
    # Sensitivity Scoring Thresholds
    SENSITIVITY_THRESHOLDS = {
        'SENSITIVE': 8,
        'PERSONAL': 5,
        'CLINICAL': 3,
        'STATISTICAL': 1
    }
    
    # PII Detection Patterns (can be extended)
    ADDITIONAL_PII_PATTERNS = {
        'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
        'driver_license': r'\b[A-Z]{1,2}\d{6,8}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    }
    
    # Medical Keywords for Enhanced Detection
    ADDITIONAL_SENSITIVE_KEYWORDS = {
        'chronic_conditions': ['diabetes', 'hypertension', 'cancer', 'heart disease'],
        'medications': ['morphine', 'oxycodone', 'adderall', 'xanax'],
        'procedures': ['surgery', 'biopsy', 'chemotherapy', 'radiation']
    }
    
    # Compliance Settings
    COMPLIANCE_REQUIREMENTS = {
        'HIPAA_ENABLED': True,
        'GDPR_ENABLED': True,
        'CONSENT_REQUIRED': True,
        'AUDIT_RETENTION_DAYS': 2555  # 7 years
    }
    
    # Blockchain Storage Configuration
    STORAGE_DESTINATIONS = {
        'IDENTIFIED_VAULT': {
            'encryption_required': True,
            'access_control': 'patient_controlled',
            'retention_policy': 'indefinite'
        },
        'ANONYMOUS_RESEARCH': {
            'encryption_required': True,
            'access_control': 'researcher_approved',
            'retention_policy': '10_years'
        },
        'STATISTICAL_POOL': {
            'encryption_required': False,
            'access_control': 'public_aggregated',
            'retention_policy': '5_years'
        },
        'QUARANTINE': {
            'encryption_required': True,
            'access_control': 'admin_only',
            'retention_policy': '30_days'
        }
    }
    
    # Data Processing Rules
    PROCESSING_RULES = {
        'max_processing_time_seconds': 30,
        'max_data_size_mb': 100,
        'enable_batch_processing': True,
        'batch_size': 1000
    }
    
    @classmethod
    def get_config(cls) -> Dict:
        """Get all configuration settings as a dictionary"""
        return {
            'log_level': cls.LOG_LEVEL,
            'log_file': cls.LOG_FILE,
            'encryption_key_path': cls.ENCRYPTION_KEY_PATH,
            'differential_privacy_epsilon': cls.DIFFERENTIAL_PRIVACY_EPSILON,
            'k_anonymity_levels': cls.DEFAULT_K_ANONYMITY,
            'sensitivity_thresholds': cls.SENSITIVITY_THRESHOLDS,
            'additional_pii_patterns': cls.ADDITIONAL_PII_PATTERNS,
            'additional_sensitive_keywords': cls.ADDITIONAL_SENSITIVE_KEYWORDS,
            'compliance_requirements': cls.COMPLIANCE_REQUIREMENTS,
            'storage_destinations': cls.STORAGE_DESTINATIONS,
            'processing_rules': cls.PROCESSING_RULES
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        try:
            # Validate epsilon value
            if not 0 < cls.DIFFERENTIAL_PRIVACY_EPSILON <= 1:
                raise ValueError("Differential privacy epsilon must be between 0 and 1")
            
            # Validate k-anonymity values
            for level, k_value in cls.DEFAULT_K_ANONYMITY.items():
                if k_value < 1:
                    raise ValueError(f"K-anonymity value for {level} must be >= 1")
            
            # Validate thresholds
            thresholds = list(cls.SENSITIVITY_THRESHOLDS.values())
            if not all(thresholds[i] >= thresholds[i+1] for i in range(len(thresholds)-1)):
                raise ValueError("Sensitivity thresholds must be in descending order")
            
            return True
            
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False

# Environment-specific configurations
class DevelopmentConfig(AbenaConfig):
    """Development environment configuration"""
    LOG_LEVEL = 'DEBUG'
    DIFFERENTIAL_PRIVACY_EPSILON = 0.5  # Less strict for development

class ProductionConfig(AbenaConfig):
    """Production environment configuration"""
    LOG_LEVEL = 'WARNING'
    DIFFERENTIAL_PRIVACY_EPSILON = 0.01  # Very strict for production
    
    # Enhanced security for production
    PROCESSING_RULES = {
        **AbenaConfig.PROCESSING_RULES,
        'max_processing_time_seconds': 10,  # Stricter timeout
        'max_data_size_mb': 50,  # Smaller max size
        'rate_limiting_enabled': True
    }

class TestingConfig(AbenaConfig):
    """Testing environment configuration"""
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'test_abena_triage.log'
    
    # Relaxed settings for testing
    SENSITIVITY_THRESHOLDS = {
        'SENSITIVE': 6,
        'PERSONAL': 4,
        'CLINICAL': 2,
        'STATISTICAL': 1
    }

# Configuration factory
def get_config(environment: str = None) -> AbenaConfig:
    """Get configuration based on environment"""
    environment = environment or os.getenv('ABENA_ENVIRONMENT', 'development').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(environment, DevelopmentConfig)
    
    # Validate configuration
    if not config_class.validate_config():
        raise ValueError(f"Invalid configuration for environment: {environment}")
    
    return config_class 