import os
from typing import Dict, Any
from datetime import timedelta

class Settings:
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/abena_ihr")
    
    # ML Model settings
    MODEL_UPDATE_THRESHOLD = 0.05  # 5% improvement required
    PREDICTION_CONFIDENCE_THRESHOLD = 0.6
    
    # EMR Integration settings
    EMR_TIMEOUT_SECONDS = 30
    FHIR_VERSION = "R4"
    
    # Alert settings
    CRITICAL_ALERT_ESCALATION_MINUTES = 15
    HIGH_ALERT_ESCALATION_MINUTES = 60
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Daily Learning Scheduler settings
    LEARNING_SCHEDULE_TIME = os.getenv("LEARNING_SCHEDULE_TIME", "02:00")  # 2 AM daily
    LEARNING_TIMEZONE = os.getenv("LEARNING_TIMEZONE", "UTC")
    LEARNING_MAX_EXECUTION_TIME = int(os.getenv("LEARNING_MAX_EXECUTION_TIME", "7200"))  # 2 hours
    LEARNING_RETRY_ATTEMPTS = int(os.getenv("LEARNING_RETRY_ATTEMPTS", "3"))
    LEARNING_RETRY_DELAY = int(os.getenv("LEARNING_RETRY_DELAY", "300"))  # 5 minutes
    LEARNING_NOTIFICATION_ENABLED = os.getenv("LEARNING_NOTIFICATION_ENABLED", "true").lower() == "true"
    LEARNING_HEALTH_CHECK_INTERVAL = int(os.getenv("LEARNING_HEALTH_CHECK_INTERVAL", "3600"))  # 1 hour

    # Model Registry settings
    MODEL_REGISTRY_PATH = os.getenv("MODEL_REGISTRY_PATH", "models/registry")
    MODEL_VERSIONING_ENABLED = os.getenv("MODEL_VERSIONING_ENABLED", "true").lower() == "true"
    MODEL_BACKUP_ENABLED = os.getenv("MODEL_BACKUP_ENABLED", "true").lower() == "true"
    MODEL_BACKUP_RETENTION_DAYS = int(os.getenv("MODEL_BACKUP_RETENTION_DAYS", "30"))

    # Continuous Learning settings
    LEARNING_BATCH_SIZE = int(os.getenv("LEARNING_BATCH_SIZE", "1000"))
    LEARNING_MIN_SAMPLES = int(os.getenv("LEARNING_MIN_SAMPLES", "100"))
    LEARNING_VALIDATION_SPLIT = float(os.getenv("LEARNING_VALIDATION_SPLIT", "0.2"))
    LEARNING_OPTIMIZATION_TRIALS = int(os.getenv("LEARNING_OPTIMIZATION_TRIALS", "50"))

    # Notification settings
    NOTIFICATION_EMAIL_ENABLED = os.getenv("NOTIFICATION_EMAIL_ENABLED", "true").lower() == "true"
    NOTIFICATION_SLACK_ENABLED = os.getenv("NOTIFICATION_SLACK_ENABLED", "true").lower() == "true"
    NOTIFICATION_SLACK_WEBHOOK = os.getenv("NOTIFICATION_SLACK_WEBHOOK", "")
    NOTIFICATION_EMAIL_SMTP_SERVER = os.getenv("NOTIFICATION_EMAIL_SMTP_SERVER", "smtp.gmail.com")
    NOTIFICATION_EMAIL_SMTP_PORT = int(os.getenv("NOTIFICATION_EMAIL_SMTP_PORT", "587"))
    NOTIFICATION_EMAIL_SENDER = os.getenv("NOTIFICATION_EMAIL_SENDER", "")
    NOTIFICATION_EMAIL_PASSWORD = os.getenv("NOTIFICATION_EMAIL_PASSWORD", "")

    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.getenv("LOG_FILE", "logs/abena_ihr.log")
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))
    API_CORS_ORIGINS = os.getenv("API_CORS_ORIGINS", "*").split(",")

    # Cache settings
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TYPE = os.getenv("CACHE_TYPE", "redis")
    CACHE_URL = os.getenv("CACHE_URL", "redis://localhost:6379/0")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

    # Feature flags
    ENABLE_ADVANCED_ANALYTICS = os.getenv("ENABLE_ADVANCED_ANALYTICS", "true").lower() == "true"
    ENABLE_REAL_TIME_PREDICTIONS = os.getenv("ENABLE_REAL_TIME_PREDICTIONS", "true").lower() == "true"
    ENABLE_AUTOMATED_INSIGHTS = os.getenv("ENABLE_AUTOMATED_INSIGHTS", "true").lower() == "true"

    # Application settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    TIMEZONE = os.getenv("TIMEZONE", "UTC")
    
    # CORS settings
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # ============================================================================
    # DAILY LEARNING CONFIGURATION
    # ============================================================================
    
    # Enable/disable daily learning system
    ENABLE_DAILY_LEARNING = os.getenv("ENABLE_DAILY_LEARNING", "true").lower() == "true"
    
    # Daily learning schedule (24-hour format)
    DAILY_LEARNING_TIME = os.getenv("DAILY_LEARNING_TIME", "02:00")
    
    # Maximum execution time for learning cycle (seconds)
    MAX_LEARNING_EXECUTION_TIME = int(os.getenv("MAX_LEARNING_EXECUTION_TIME", "7200"))  # 2 hours
    
    # Auto-retraining thresholds
    AUTO_RETRAIN_THRESHOLD = float(os.getenv("AUTO_RETRAIN_THRESHOLD", "0.7"))
    HUMAN_APPROVAL_THRESHOLD = float(os.getenv("HUMAN_APPROVAL_THRESHOLD", "0.5"))
    
    # Learning analysis settings
    MIN_SAMPLES_FOR_ANALYSIS = int(os.getenv("MIN_SAMPLES_FOR_ANALYSIS", "50"))
    PERFORMANCE_MONITORING_WINDOW_DAYS = int(os.getenv("PERFORMANCE_MONITORING_WINDOW_DAYS", "30"))
    
    # Model performance thresholds
    MIN_MODEL_ACCURACY = float(os.getenv("MIN_MODEL_ACCURACY", "0.70"))
    MAX_FALSE_POSITIVE_RATE = float(os.getenv("MAX_FALSE_POSITIVE_RATE", "0.20"))
    
    # Learning notifications
    LEARNING_NOTIFICATIONS_ENABLED = os.getenv("LEARNING_NOTIFICATIONS_ENABLED", "true").lower() == "true"
    LEARNING_NOTIFICATION_EMAIL = os.getenv("LEARNING_NOTIFICATION_EMAIL", "")
    LEARNING_NOTIFICATION_SLACK_WEBHOOK = os.getenv("LEARNING_NOTIFICATION_SLACK_WEBHOOK", "")
    
    # ============================================================================
    # REAL-TIME BIOMARKER CONFIGURATION
    # ============================================================================
    
    # Enable/disable real-time biomarker monitoring
    ENABLE_REALTIME_BIOMARKERS = os.getenv("ENABLE_REALTIME_BIOMARKERS", "false").lower() == "true"
    
    # Biomarker data retention (days)
    BIOMARKER_DATA_RETENTION_DAYS = int(os.getenv("BIOMARKER_DATA_RETENTION_DAYS", "90"))
    
    # Alert thresholds for biomarkers
    GLUCOSE_LOW_THRESHOLD = float(os.getenv("GLUCOSE_LOW_THRESHOLD", "70"))
    GLUCOSE_HIGH_THRESHOLD = float(os.getenv("GLUCOSE_HIGH_THRESHOLD", "180"))
    HRV_LOW_THRESHOLD = float(os.getenv("HRV_LOW_THRESHOLD", "20"))
    HRV_HIGH_THRESHOLD = float(os.getenv("HRV_HIGH_THRESHOLD", "100"))
    CORTISOL_LOW_THRESHOLD = float(os.getenv("CORTISOL_LOW_THRESHOLD", "5"))
    CORTISOL_HIGH_THRESHOLD = float(os.getenv("CORTISOL_HIGH_THRESHOLD", "25"))
    BP_SYSTOLIC_LOW_THRESHOLD = float(os.getenv("BP_SYSTOLIC_LOW_THRESHOLD", "90"))
    BP_SYSTOLIC_HIGH_THRESHOLD = float(os.getenv("BP_SYSTOLIC_HIGH_THRESHOLD", "140"))
    BP_DIASTOLIC_LOW_THRESHOLD = float(os.getenv("BP_DIASTOLIC_LOW_THRESHOLD", "60"))
    BP_DIASTOLIC_HIGH_THRESHOLD = float(os.getenv("BP_DIASTOLIC_HIGH_THRESHOLD", "90"))

    # ============================================================================
    # EMAIL/NOTIFICATION CONFIGURATION
    # ============================================================================
    
    # Email settings for notifications
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.hospital.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "abena@hospital.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # Notification recipients
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@hospital.com")
    CLINICAL_TEAM_EMAIL = os.getenv("CLINICAL_TEAM_EMAIL", "clinical@hospital.com")
    
    # Slack integration
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#abena-alerts")

    # ============================================================================
    # DATA PIPELINE CONFIGURATION
    # ============================================================================
    
    # Data processing batch sizes
    OUTCOME_PROCESSING_BATCH_SIZE = int(os.getenv("OUTCOME_PROCESSING_BATCH_SIZE", "100"))
    PREDICTION_PROCESSING_BATCH_SIZE = int(os.getenv("PREDICTION_PROCESSING_BATCH_SIZE", "50"))
    
    # Data quality thresholds
    MIN_DATA_QUALITY_SCORE = float(os.getenv("MIN_DATA_QUALITY_SCORE", "0.7"))
    MAX_MISSING_DATA_PERCENTAGE = float(os.getenv("MAX_MISSING_DATA_PERCENTAGE", "0.3"))

    # ============================================================================
    # SECURITY AND COMPLIANCE CONFIGURATION
    # ============================================================================
    
    # Data encryption
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
    ENCRYPT_PHI_DATA = os.getenv("ENCRYPT_PHI_DATA", "true").lower() == "true"
    
    # Audit logging
    ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
    AUDIT_LOG_RETENTION_DAYS = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "2555"))  # 7 years
    
    # Data retention policies
    OUTCOME_DATA_RETENTION_YEARS = int(os.getenv("OUTCOME_DATA_RETENTION_YEARS", "10"))
    PREDICTION_DATA_RETENTION_YEARS = int(os.getenv("PREDICTION_DATA_RETENTION_YEARS", "7"))

    # ============================================================================
    # PERFORMANCE MONITORING CONFIGURATION
    # ============================================================================
    
    # Performance metrics
    ENABLE_PERFORMANCE_MONITORING = os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true"
    PERFORMANCE_METRICS_RETENTION_DAYS = int(os.getenv("PERFORMANCE_METRICS_RETENTION_DAYS", "365"))
    
    # Response time thresholds (milliseconds)
    MAX_PREDICTION_RESPONSE_TIME = int(os.getenv("MAX_PREDICTION_RESPONSE_TIME", "1000"))
    MAX_API_RESPONSE_TIME = int(os.getenv("MAX_API_RESPONSE_TIME", "5000"))
    
    # Resource usage thresholds
    MAX_MEMORY_USAGE_PERCENT = int(os.getenv("MAX_MEMORY_USAGE_PERCENT", "80"))
    MAX_CPU_USAGE_PERCENT = int(os.getenv("MAX_CPU_USAGE_PERCENT", "70"))

    # ============================================================================
    # CLINICAL VALIDATION CONFIGURATION
    # ============================================================================
    
    # Clinical validation thresholds
    CLINICAL_VALIDATION_REQUIRED = os.getenv("CLINICAL_VALIDATION_REQUIRED", "true").lower() == "true"
    MIN_CLINICAL_VALIDATION_SAMPLE_SIZE = int(os.getenv("MIN_CLINICAL_VALIDATION_SAMPLE_SIZE", "100"))
    
    # Regulatory compliance
    FDA_COMPLIANCE_MODE = os.getenv("FDA_COMPLIANCE_MODE", "false").lower() == "true"
    HIPAA_COMPLIANCE_MODE = os.getenv("HIPAA_COMPLIANCE_MODE", "true").lower() == "true"
    
    # Clinical decision support levels
    DECISION_SUPPORT_LEVEL = os.getenv("DECISION_SUPPORT_LEVEL", "advisory")  # advisory, suggestive, directive

    def get_daily_learning_config(self) -> Dict[str, Any]:
        """Get daily learning scheduler configuration"""
        return {
            "learning_time": self.LEARNING_SCHEDULE_TIME,
            "timezone": self.LEARNING_TIMEZONE,
            "max_execution_time": self.LEARNING_MAX_EXECUTION_TIME,
            "retry_attempts": self.LEARNING_RETRY_ATTEMPTS,
            "retry_delay": self.LEARNING_RETRY_DELAY,
            "notification_enabled": self.LEARNING_NOTIFICATION_ENABLED,
            "health_check_interval": self.LEARNING_HEALTH_CHECK_INTERVAL
        }

    def get_model_registry_config(self) -> Dict[str, Any]:
        """Get model registry configuration"""
        return {
            "registry_path": self.MODEL_REGISTRY_PATH,
            "versioning_enabled": self.MODEL_VERSIONING_ENABLED,
            "backup_enabled": self.MODEL_BACKUP_ENABLED,
            "backup_retention_days": self.MODEL_BACKUP_RETENTION_DAYS
        }

    def get_continuous_learning_config(self) -> Dict[str, Any]:
        """Get continuous learning configuration"""
        return {
            "batch_size": self.LEARNING_BATCH_SIZE,
            "min_samples": self.LEARNING_MIN_SAMPLES,
            "validation_split": self.LEARNING_VALIDATION_SPLIT,
            "optimization_trials": self.LEARNING_OPTIMIZATION_TRIALS
        }

    def get_notification_config(self) -> Dict[str, Any]:
        """Get notification configuration"""
        return {
            "email_enabled": self.NOTIFICATION_EMAIL_ENABLED,
            "slack_enabled": self.NOTIFICATION_SLACK_ENABLED,
            "slack_webhook": self.NOTIFICATION_SLACK_WEBHOOK,
            "email_smtp_server": self.NOTIFICATION_EMAIL_SMTP_SERVER,
            "email_smtp_port": self.NOTIFICATION_EMAIL_SMTP_PORT,
            "email_sender": self.NOTIFICATION_EMAIL_SENDER,
            "email_password": self.NOTIFICATION_EMAIL_PASSWORD
        }

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.LOG_LEVEL,
            "format": self.LOG_FORMAT,
            "file": self.LOG_FILE,
            "max_size": self.LOG_MAX_SIZE,
            "backup_count": self.LOG_BACKUP_COUNT
        }

    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return {
            "host": self.API_HOST,
            "port": self.API_PORT,
            "workers": self.API_WORKERS,
            "timeout": self.API_TIMEOUT,
            "cors_origins": self.API_CORS_ORIGINS
        }

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration"""
        return {
            "enabled": self.CACHE_ENABLED,
            "type": self.CACHE_TYPE,
            "url": self.CACHE_URL,
            "ttl": self.CACHE_TTL
        }

    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags configuration"""
        return {
            "advanced_analytics": self.ENABLE_ADVANCED_ANALYTICS,
            "real_time_predictions": self.ENABLE_REAL_TIME_PREDICTIONS,
            "automated_insights": self.ENABLE_AUTOMATED_INSIGHTS
        }

    @classmethod
    def validate_configuration(cls):
        """Validate configuration settings"""
        errors = []
        warnings = []
        
        # Validate database URL
        if not cls.DATABASE_URL or cls.DATABASE_URL == "postgresql://user:pass@localhost/abena_ihr":
            errors.append("DATABASE_URL must be configured with actual database credentials")
        
        # Validate secret key
        if not cls.SECRET_KEY or cls.SECRET_KEY == "your-secret-key-here":
            errors.append("SECRET_KEY must be configured with a secure secret key")
        
        # Validate learning configuration
        if cls.ENABLE_DAILY_LEARNING:
            if not cls.DAILY_LEARNING_TIME:
                errors.append("DAILY_LEARNING_TIME must be specified when learning is enabled")
            
            if cls.MAX_LEARNING_EXECUTION_TIME < 300:  # 5 minutes minimum
                warnings.append("MAX_LEARNING_EXECUTION_TIME is very short, may cause timeouts")
        
        # Validate notification configuration
        if cls.LEARNING_NOTIFICATIONS_ENABLED:
            if not cls.LEARNING_NOTIFICATION_EMAIL and not cls.LEARNING_NOTIFICATION_SLACK_WEBHOOK:
                warnings.append("Learning notifications enabled but no notification channels configured")
        
        # Validate biomarker configuration
        if cls.ENABLE_REALTIME_BIOMARKERS:
            if cls.GLUCOSE_LOW_THRESHOLD >= cls.GLUCOSE_HIGH_THRESHOLD:
                errors.append("GLUCOSE_LOW_THRESHOLD must be less than GLUCOSE_HIGH_THRESHOLD")
        
        # Validate performance thresholds
        if cls.MIN_MODEL_ACCURACY < 0.5:
            warnings.append("MIN_MODEL_ACCURACY is very low, may indicate poor model performance")
        
        if cls.MAX_FALSE_POSITIVE_RATE > 0.3:
            warnings.append("MAX_FALSE_POSITIVE_RATE is high, may cause too many false alarms")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    @classmethod
    def get_biomarker_config(cls) -> Dict[str, Any]:
        """Get biomarker-specific configuration"""
        return {
            'enabled': cls.ENABLE_REALTIME_BIOMARKERS,
            'data_retention_days': cls.BIOMARKER_DATA_RETENTION_DAYS,
            'thresholds': {
                'glucose_low': cls.GLUCOSE_LOW_THRESHOLD,
                'glucose_high': cls.GLUCOSE_HIGH_THRESHOLD,
                'hrv_low': cls.HRV_LOW_THRESHOLD,
                'cortisol_high': cls.CORTISOL_HIGH_THRESHOLD
            },
            'connection_timeout': cls.DEVICE_CONNECTION_TIMEOUT,
            'read_timeout': cls.DEVICE_READ_TIMEOUT
        }

    @classmethod
    def get_notification_config(cls) -> Dict[str, Any]:
        """Get notification configuration"""
        return {
            'email': {
                'enabled': bool(cls.SMTP_SERVER and cls.SMTP_USERNAME),
                'server': cls.SMTP_SERVER,
                'port': cls.SMTP_PORT,
                'username': cls.SMTP_USERNAME,
                'use_tls': cls.SMTP_USE_TLS,
                'admin_email': cls.ADMIN_EMAIL,
                'clinical_team_email': cls.CLINICAL_TEAM_EMAIL
            },
            'slack': {
                'enabled': bool(cls.SLACK_WEBHOOK_URL),
                'webhook_url': cls.SLACK_WEBHOOK_URL,
                'channel': cls.SLACK_CHANNEL
            }
        }

# Create global settings instance
settings = Settings()

# Validate configuration on import
validation_result = settings.validate_configuration()
if not validation_result['valid']:
    import logging
    logger = logging.getLogger(__name__)
    logger.error("Configuration validation failed:")
    for error in validation_result['errors']:
        logger.error(f"  ERROR: {error}")
    for warning in validation_result['warnings']:
        logger.warning(f"  WARNING: {warning}")
    
    if validation_result['errors']:
        raise ValueError("Configuration validation failed. Please check your environment variables.")

# Export commonly used configurations
LEARNING_CONFIG = settings.get_learning_config()
BIOMARKER_CONFIG = settings.get_biomarker_config()
NOTIFICATION_CONFIG = settings.get_notification_config()