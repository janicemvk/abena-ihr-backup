"""
Abena Security SDK Configuration

This module provides configuration management for the Abena IHR Security SDK,
following Abena SDK patterns and best practices.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

TRUE_VALUES = {"true", "1", "t", "y", "yes"}


@dataclass
class AbenaSecurityConfig:
    """
    Configuration for Abena Security SDK

    This class manages all configuration settings for the security SDK,
    following Abena SDK patterns and providing sensible defaults.
    """

    # Database Configuration
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "postgresql://user:pass@localhost/abena_ihr"
        )
    )

    # Redis Configuration
    redis_url: str = field(
        default_factory=lambda: os.getenv(
            "REDIS_URL", "redis://localhost:6379"
        )
    )

    # Security Configuration
    master_key_path: str = field(
        default_factory=lambda: os.getenv(
            "MASTER_KEY_PATH", "/secure/master.key"
        )
    )
    encryption_algorithm: str = field(default="AES_256_GCM")
    key_rotation_days: int = field(default=365)

    # Audit Configuration
    audit_log_level: str = field(default="INFO")
    audit_retention_days: int = field(default=2555)  # 7 years for HIPAA
    audit_batch_size: int = field(default=100)

    # Compliance Configuration
    compliance_framework: str = field(default="HIPAA")
    compliance_check_interval: int = field(default=3600)  # 1 hour
    compliance_report_retention_days: int = field(default=2555)

    # Data Masking Configuration
    masking_enabled: bool = field(default=True)
    masking_rules_path: Optional[str] = field(default=None)
    tokenization_enabled: bool = field(default=True)

    # Business Rules Configuration
    rules_auto_reload: bool = field(default=True)
    rules_cache_ttl: int = field(default=300)  # 5 minutes

    # Logging Configuration
    log_level: str = field(default="INFO")
    log_format: str = field(default="json")
    log_file: Optional[str] = field(default=None)

    # Performance Configuration
    max_connections: int = field(default=20)
    connection_timeout: int = field(default=30)
    request_timeout: int = field(default=60)

    # Development Configuration
    debug_mode: bool = field(default=False)
    test_mode: bool = field(default=False)

    # Custom Configuration
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and set default values after initialization"""
        self._validate_config()
        self._set_defaults()

    def _validate_config(self):
        """Validate configuration values"""
        if not self.database_url:
            raise ValueError("database_url is required")

        if not self.redis_url:
            raise ValueError("redis_url is required")

        if self.key_rotation_days < 30:
            raise ValueError("key_rotation_days must be at least 30 days")

        if self.audit_retention_days < 2555:
            raise ValueError(
                "audit_retention_days must be at least 7 years "
                "(2555 days) for HIPAA compliance"
            )

    def _set_defaults(self):
        """Set default values for optional fields"""
        if not self.masking_rules_path:
            self.masking_rules_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "masking_rules.json"
            )

        if not self.log_file:
            self.log_file = os.path.join(
                os.getenv(
                    "LOG_DIR", "/var/log/abena"
                ), "abena-ihr-security.log"
            )

    @classmethod
    def from_env(cls) -> "AbenaSecurityConfig":
        """
        Create configuration from environment variables

        Returns:
            AbenaSecurityConfig instance
        """
        return cls(
            database_url=os.getenv(
                "DATABASE_URL", "postgresql://user:pass@localhost/abena_ihr"
            ),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            master_key_path=os.getenv("MASTER_KEY_PATH", "/secure/master.key"),
            encryption_algorithm=os.getenv(
                "ENCRYPTION_ALGORITHM", "AES_256_GCM"
            ),
            key_rotation_days=int(os.getenv("KEY_ROTATION_DAYS", "365")),
            audit_log_level=os.getenv("AUDIT_LOG_LEVEL", "INFO"),
            audit_retention_days=int(
                os.getenv("AUDIT_RETENTION_DAYS", "2555")
            ),
            audit_batch_size=int(os.getenv("AUDIT_BATCH_SIZE", "100")),
            compliance_framework=os.getenv("COMPLIANCE_FRAMEWORK", "HIPAA"),
            compliance_check_interval=int(
                os.getenv("COMPLIANCE_CHECK_INTERVAL", "3600")
            ),
            compliance_report_retention_days=int(
                os.getenv("COMPLIANCE_REPORT_RETENTION_DAYS", "2555")
            ),
            masking_enabled=(
                os.getenv("MASKING_ENABLED", "true").lower() == "true"
            ),
            masking_rules_path=os.getenv("MASKING_RULES_PATH"),
            tokenization_enabled=(
                os.getenv("TOKENIZATION_ENABLED", "true").lower() == "true"
            ),
            rules_auto_reload=(
                os.getenv("RULES_AUTO_RELOAD", "true").lower() == "true"
            ),
            rules_cache_ttl=int(os.getenv("RULES_CACHE_TTL", "300")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            log_file=os.getenv("LOG_FILE"),
            max_connections=int(os.getenv("MAX_CONNECTIONS", "20")),
            connection_timeout=int(os.getenv("CONNECTION_TIMEOUT", "30")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "60")),
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            test_mode=os.getenv("TEST_MODE", "false").lower() == "true",
        )

    @classmethod
    def from_file(cls, config_path: str) -> "AbenaSecurityConfig":
        """
        Create configuration from JSON file

        Args:
            config_path: Path to configuration file

        Returns:
            AbenaSecurityConfig instance
        """
        import json

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        with open(config_path, "r") as f:
            config_data = json.load(f)

        return cls(**config_data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary

        Returns:
            Dictionary representation of configuration
        """
        return {
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "master_key_path": self.master_key_path,
            "encryption_algorithm": self.encryption_algorithm,
            "key_rotation_days": self.key_rotation_days,
            "audit_log_level": self.audit_log_level,
            "audit_retention_days": self.audit_retention_days,
            "audit_batch_size": self.audit_batch_size,
            "compliance_framework": self.compliance_framework,
            "compliance_check_interval": self.compliance_check_interval,
            "compliance_report_retention_days": (
                self.compliance_report_retention_days
            ),
            "masking_enabled": self.masking_enabled,
            "masking_rules_path": self.masking_rules_path,
            "tokenization_enabled": self.tokenization_enabled,
            "rules_auto_reload": self.rules_auto_reload,
            "rules_cache_ttl": self.rules_cache_ttl,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "log_file": self.log_file,
            "max_connections": self.max_connections,
            "connection_timeout": self.connection_timeout,
            "request_timeout": self.request_timeout,
            "debug_mode": self.debug_mode,
            "test_mode": self.test_mode,
            "custom_settings": self.custom_settings,
        }

    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to JSON file

        Args:
            config_path: Path to save configuration file
        """
        import json

        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)

        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration setting

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value
        """
        return self.custom_settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a custom configuration setting

        Args:
            key: Setting key
            value: Setting value
        """
        self.custom_settings[key] = value
