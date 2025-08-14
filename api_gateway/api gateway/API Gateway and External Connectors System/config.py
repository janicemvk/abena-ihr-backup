"""
Configuration management for Abena IHR Integration Layer
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30

@dataclass
class RedisConfig:
    """Redis configuration"""
    url: str
    max_connections: int = 10
    socket_timeout: int = 5

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

@dataclass
class APIConfig:
    """API configuration"""
    title: str = "Abena IHR API Gateway"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass
class ExternalAPIConfig:
    """External API configuration"""
    # Fitbit
    fitbit_client_id: Optional[str] = None
    fitbit_client_secret: Optional[str] = None
    
    # Epic
    epic_base_url: Optional[str] = None
    epic_client_id: Optional[str] = None
    epic_private_key: Optional[str] = None
    
    # Cerner
    cerner_base_url: Optional[str] = None
    cerner_client_id: Optional[str] = None
    cerner_client_secret: Optional[str] = None
    
    # Zoom
    zoom_api_key: Optional[str] = None
    zoom_api_secret: Optional[str] = None
    zoom_account_id: Optional[str] = None
    
    # LabCorp
    labcorp_client_id: Optional[str] = None
    labcorp_client_secret: Optional[str] = None
    labcorp_facility_id: Optional[str] = None

class Config:
    """Main configuration class"""
    
    def __init__(self):
        # Database
        self.database = DatabaseConfig(
            url=os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/abena_ihr")
        )
        
        # Redis
        self.redis = RedisConfig(
            url=os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        
        # Security
        self.security = SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", "your-secret-key-here")
        )
        
        # API
        self.api = APIConfig(
            debug=os.getenv("DEBUG", "false").lower() == "true"
        )
        
        # Logging
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        # External APIs
        self.external = ExternalAPIConfig(
            fitbit_client_id=os.getenv("FITBIT_CLIENT_ID"),
            fitbit_client_secret=os.getenv("FITBIT_CLIENT_SECRET"),
            epic_base_url=os.getenv("EPIC_BASE_URL"),
            epic_client_id=os.getenv("EPIC_CLIENT_ID"),
            epic_private_key=os.getenv("EPIC_PRIVATE_KEY"),
            cerner_base_url=os.getenv("CERNER_BASE_URL"),
            cerner_client_id=os.getenv("CERNER_CLIENT_ID"),
            cerner_client_secret=os.getenv("CERNER_CLIENT_SECRET"),
            zoom_api_key=os.getenv("ZOOM_API_KEY"),
            zoom_api_secret=os.getenv("ZOOM_API_SECRET"),
            zoom_account_id=os.getenv("ZOOM_ACCOUNT_ID"),
            labcorp_client_id=os.getenv("LABCORP_CLIENT_ID"),
            labcorp_client_secret=os.getenv("LABCORP_CLIENT_SECRET"),
            labcorp_facility_id=os.getenv("LABCORP_FACILITY_ID")
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        required_vars = [
            self.database.url,
            self.redis.url,
            self.security.secret_key
        ]
        
        return all(var is not None and var != "" for var in required_vars)
    
    def get_database_url(self) -> str:
        """Get database URL"""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get Redis URL"""
        return self.redis.url
    
    def get_secret_key(self) -> str:
        """Get secret key"""
        return self.security.secret_key
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.api.debug

# Global configuration instance
config = Config() 