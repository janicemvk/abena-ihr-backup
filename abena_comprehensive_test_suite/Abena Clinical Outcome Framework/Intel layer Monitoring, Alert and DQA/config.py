# =============================================================================
# Configuration Management for Abena IHR Intelligence Layer
# =============================================================================

import os
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30

@dataclass
class RedisConfig:
    url: str
    max_connections: int = 20
    socket_timeout: int = 5
    socket_connect_timeout: int = 5

@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    prometheus_port: int = 8001
    max_concurrent_requests: int = 100
    request_timeout_seconds: int = 30

@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    to_emails: List[str]

@dataclass
class SlackConfig:
    webhook_url: str

@dataclass
class AlertConfig:
    default_cooldown_minutes: int = 15
    high_error_rate_threshold: float = 0.05
    slow_response_time_threshold: float = 30.0
    low_data_quality_threshold: float = 0.7

@dataclass
class DataQualityConfig:
    anomaly_detection_contamination: float = 0.1
    quality_analysis_batch_size: int = 1000

@dataclass
class MonitoringConfig:
    health_check_interval_seconds: int = 60
    failure_detection_interval_seconds: int = 300
    system_health_threshold: int = 50

@dataclass
class SecurityConfig:
    api_key_header: str = "X-API-Key"
    api_key_value: Optional[str] = None
    cors_origins: List[str] = None

@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "logs/intelligence_layer.log"

class Config:
    def __init__(self):
        # Load from environment variables
        self.database = DatabaseConfig(
            url=os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/abena_ihr"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30"))
        )
        
        self.redis = RedisConfig(
            url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "20")),
            socket_timeout=int(os.getenv("REDIS_SOCKET_TIMEOUT", "5")),
            socket_connect_timeout=int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
        )
        
        self.api = APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            prometheus_port=int(os.getenv("PROMETHEUS_PORT", "8001")),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "100")),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
        )
        
        # Email configuration
        to_emails_str = os.getenv("TO_EMAILS", "admin@abena-ihr.com,ops@abena-ihr.com")
        self.email = EmailConfig(
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME", "alerts@abena-ihr.com"),
            password=os.getenv("SMTP_PASSWORD", "your_app_password"),
            from_email=os.getenv("FROM_EMAIL", "alerts@abena-ihr.com"),
            to_emails=[email.strip() for email in to_emails_str.split(",")]
        )
        
        # Slack configuration
        self.slack = SlackConfig(
            webhook_url=os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK")
        )
        
        # Alert configuration
        self.alerts = AlertConfig(
            default_cooldown_minutes=int(os.getenv("DEFAULT_ALERT_COOLDOWN_MINUTES", "15")),
            high_error_rate_threshold=float(os.getenv("HIGH_ERROR_RATE_THRESHOLD", "0.05")),
            slow_response_time_threshold=float(os.getenv("SLOW_RESPONSE_TIME_THRESHOLD", "30.0")),
            low_data_quality_threshold=float(os.getenv("LOW_DATA_QUALITY_THRESHOLD", "0.7"))
        )
        
        # Data quality configuration
        self.data_quality = DataQualityConfig(
            anomaly_detection_contamination=float(os.getenv("ANOMALY_DETECTION_CONTAMINATION", "0.1")),
            quality_analysis_batch_size=int(os.getenv("QUALITY_ANALYSIS_BATCH_SIZE", "1000"))
        )
        
        # Monitoring configuration
        self.monitoring = MonitoringConfig(
            health_check_interval_seconds=int(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "60")),
            failure_detection_interval_seconds=int(os.getenv("FAILURE_DETECTION_INTERVAL_SECONDS", "300")),
            system_health_threshold=int(os.getenv("SYSTEM_HEALTH_THRESHOLD", "50"))
        )
        
        # Security configuration
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
        self.security = SecurityConfig(
            api_key_header=os.getenv("API_KEY_HEADER", "X-API-Key"),
            api_key_value=os.getenv("API_KEY_VALUE"),
            cors_origins=[origin.strip() for origin in cors_origins_str.split(",")]
        )
        
        # Logging configuration
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file=os.getenv("LOG_FILE", "logs/intelligence_layer.log")
        )
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check required database configuration
        if not self.database.url:
            issues.append("DATABASE_URL is required")
        
        # Check required Redis configuration
        if not self.redis.url:
            issues.append("REDIS_URL is required")
        
        # Check email configuration
        if not self.email.smtp_server or not self.email.username or not self.email.password:
            issues.append("SMTP configuration is incomplete")
        
        # Check if email password is still default
        if self.email.password == "your_app_password":
            issues.append("SMTP_PASSWORD should be set to a real password")
        
        # Check if Slack webhook is still default
        if "YOUR/SLACK/WEBHOOK" in self.slack.webhook_url:
            issues.append("SLACK_WEBHOOK_URL should be set to a real webhook URL")
        
        # Check if API key is still default
        if self.security.api_key_value == "your_secure_api_key_here":
            issues.append("API_KEY_VALUE should be set to a secure API key")
        
        return issues
    
    def get_database_url(self) -> str:
        """Get database URL with connection pool parameters"""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get Redis URL"""
        return self.redis.url
    
    def is_email_configured(self) -> bool:
        """Check if email notifications are properly configured"""
        return (self.email.smtp_server and 
                self.email.username and 
                self.email.password and 
                self.email.password != "your_app_password")
    
    def is_slack_configured(self) -> bool:
        """Check if Slack notifications are properly configured"""
        return (self.slack.webhook_url and 
                "YOUR/SLACK/WEBHOOK" not in self.slack.webhook_url)
    
    def is_secure(self) -> bool:
        """Check if security is properly configured"""
        return (self.security.api_key_value and 
                self.security.api_key_value != "your_secure_api_key_here")

# Global configuration instance
config = Config() 