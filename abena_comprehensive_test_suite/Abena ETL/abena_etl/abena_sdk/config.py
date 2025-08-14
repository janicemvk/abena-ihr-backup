"""
Abena SDK Configuration

Configuration management for the Abena SDK with environment variable support,
validation, and secure credential handling.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from .exceptions import ConfigurationError


@dataclass
class AbenaConfig:
    """Configuration class for Abena SDK"""
    
    # API Configuration
    api_base_url: str = field(default_factory=lambda: os.getenv("ABENA_API_BASE_URL", "https://api.abena.com"))
    api_version: str = field(default_factory=lambda: os.getenv("ABENA_API_VERSION", "v1"))
    timeout: int = field(default_factory=lambda: int(os.getenv("ABENA_TIMEOUT", "30")))
    
    # Authentication
    client_id: Optional[str] = field(default_factory=lambda: os.getenv("ABENA_CLIENT_ID"))
    client_secret: Optional[str] = field(default_factory=lambda: os.getenv("ABENA_CLIENT_SECRET"))
    access_token: Optional[str] = field(default_factory=lambda: os.getenv("ABENA_ACCESS_TOKEN"))
    
    # Database Configuration
    database_url: Optional[str] = field(default_factory=lambda: os.getenv("ABENA_DATABASE_URL"))
    
    # Cache Configuration
    cache_enabled: bool = field(default_factory=lambda: os.getenv("ABENA_CACHE_ENABLED", "true").lower() == "true")
    cache_ttl: int = field(default_factory=lambda: int(os.getenv("ABENA_CACHE_TTL", "3600")))
    
    # Logging Configuration
    log_level: str = field(default_factory=lambda: os.getenv("ABENA_LOG_LEVEL", "INFO"))
    log_format: str = field(default_factory=lambda: os.getenv("ABENA_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    
    # FHIR Configuration
    fhir_version: str = field(default_factory=lambda: os.getenv("ABENA_FHIR_VERSION", "R4"))
    
    # Analytics Configuration
    analytics_enabled: bool = field(default_factory=lambda: os.getenv("ABENA_ANALYTICS_ENABLED", "true").lower() == "true")
    prediction_confidence_threshold: float = field(default_factory=lambda: float(os.getenv("ABENA_PREDICTION_CONFIDENCE_THRESHOLD", "0.6")))
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate()
    
    def _validate(self):
        """Validate configuration settings"""
        errors = []
        
        # Validate API configuration
        if not self.api_base_url:
            errors.append("ABENA_API_BASE_URL must be configured")
        
        if self.timeout <= 0:
            errors.append("ABENA_TIMEOUT must be greater than 0")
        
        # Validate authentication
        if not self.client_id and not self.access_token:
            errors.append("Either ABENA_CLIENT_ID or ABENA_ACCESS_TOKEN must be configured")
        
        if self.client_id and not self.client_secret:
            errors.append("ABENA_CLIENT_SECRET must be configured when using client_id")
        
        # Validate FHIR version
        valid_fhir_versions = ["R4", "R3", "R2"]
        if self.fhir_version not in valid_fhir_versions:
            errors.append(f"ABENA_FHIR_VERSION must be one of: {', '.join(valid_fhir_versions)}")
        
        # Validate prediction threshold
        if not 0.0 <= self.prediction_confidence_threshold <= 1.0:
            errors.append("ABENA_PREDICTION_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
        
        if errors:
            raise ConfigurationError("Configuration validation failed", details={"errors": errors})
    
    def get_api_url(self, endpoint: str = "") -> str:
        """Get full API URL for an endpoint"""
        base = self.api_base_url.rstrip("/")
        version = self.api_version.lstrip("v")
        endpoint = endpoint.lstrip("/")
        return f"{base}/v{version}/{endpoint}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "api_base_url": self.api_base_url,
            "api_version": self.api_version,
            "timeout": self.timeout,
            "client_id": self.client_id,
            "access_token": "***" if self.access_token else None,
            "database_url": self.database_url,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "log_level": self.log_level,
            "fhir_version": self.fhir_version,
            "analytics_enabled": self.analytics_enabled,
            "prediction_confidence_threshold": self.prediction_confidence_threshold
        }
    
    @classmethod
    def from_env(cls) -> "AbenaConfig":
        """Create configuration from environment variables"""
        return cls()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AbenaConfig":
        """Create configuration from dictionary"""
        return cls(**config_dict) 