"""
Unit tests for Abena Security Configuration

Tests the configuration management and validation.
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch

from abena_ihr_security.sdk import AbenaSecurityConfig


class TestAbenaSecurityConfig:
    """Test cases for AbenaSecurityConfig"""

    def test_config_creation_with_defaults(self):
        """Test configuration creation with default values"""
        config = AbenaSecurityConfig()

        assert (
            config.database_url
            == "postgresql://user:pass@localhost/abena_ihr"
        )
        assert config.redis_url == "redis://localhost:6379"
        assert config.master_key_path == "/secure/master.key"
        assert config.encryption_algorithm == "AES_256_GCM"
        assert config.key_rotation_days == 365
        assert config.audit_retention_days == 2555
        assert config.compliance_framework == "HIPAA"
        assert config.masking_enabled is True
        assert config.tokenization_enabled is True
        assert config.rules_auto_reload is True
        assert config.log_level == "INFO"
        assert config.max_connections == 20
        assert config.debug_mode is False

    def test_config_creation_with_custom_values(self):
        """Test configuration creation with custom values"""
        config = AbenaSecurityConfig(
            database_url="postgresql://custom:pass@localhost/test_db",
            redis_url="redis://localhost:6380",
            master_key_path="/custom/secure/key",
            encryption_algorithm="RSA_2048",
            key_rotation_days=180,
            audit_retention_days=3650,
            compliance_framework="GDPR",
            masking_enabled=False,
            tokenization_enabled=False,
            rules_auto_reload=False,
            log_level="DEBUG",
            max_connections=50,
            debug_mode=True,
        )

        assert (
            config.database_url
            == "postgresql://custom:pass@localhost/test_db"
        )
        assert config.redis_url == "redis://localhost:6380"
        assert config.master_key_path == "/custom/secure/key"
        assert config.encryption_algorithm == "RSA_2048"
        assert config.key_rotation_days == 180
        assert config.audit_retention_days == 3650
        assert config.compliance_framework == "GDPR"
        assert config.masking_enabled is False
        assert config.tokenization_enabled is False
        assert config.rules_auto_reload is False
        assert config.log_level == "DEBUG"
        assert config.max_connections == 50
        assert config.debug_mode is True

    def test_config_validation_success(self):
        """Test successful configuration validation"""
        config = AbenaSecurityConfig(
            database_url="postgresql://user:pass@localhost/abena_ihr",
            redis_url="redis://localhost:6379",
            key_rotation_days=365,
            audit_retention_days=2555,
        )

        # Should not raise any exceptions
        assert config.database_url is not None
        assert config.redis_url is not None

    def test_config_validation_missing_database_url(self):
        """Test configuration validation with missing database URL"""
        with pytest.raises(ValueError, match="database_url is required"):
            AbenaSecurityConfig(database_url="")

    def test_config_validation_missing_redis_url(self):
        """Test configuration validation with missing Redis URL"""
        with pytest.raises(ValueError, match="redis_url is required"):
            AbenaSecurityConfig(redis_url="")

    def test_config_validation_key_rotation_too_short(self):
        """Test configuration validation with key rotation days too short"""
        with pytest.raises(
            ValueError, match="key_rotation_days must be at least 30 days"
        ):
            AbenaSecurityConfig(key_rotation_days=15)

    def test_config_validation_audit_retention_too_short(self):
        """Test configuration validation with audit retention days too short"""
        with pytest.raises(
            ValueError, match="audit_retention_days must be at least 7 years"
        ):
            AbenaSecurityConfig(audit_retention_days=1000)

    @patch.dict(
        os.environ,
        {
            "DATABASE_URL": "postgresql://env:pass@localhost/env_db",
            "REDIS_URL": "redis://localhost:6380",
            "MASTER_KEY_PATH": "/env/secure/key",
            "ENCRYPTION_ALGORITHM": "RSA_4096",
            "KEY_ROTATION_DAYS": "180",
            "AUDIT_LOG_LEVEL": "DEBUG",
            "AUDIT_RETENTION_DAYS": "3650",
            "COMPLIANCE_FRAMEWORK": "GDPR",
            "COMPLIANCE_CHECK_INTERVAL": "7200",
            "COMPLIANCE_REPORT_RETENTION_DAYS": "3650",
            "MASKING_ENABLED": "false",
            "MASKING_RULES_PATH": "/env/masking/rules.json",
            "TOKENIZATION_ENABLED": "false",
            "RULES_AUTO_RELOAD": "false",
            "RULES_CACHE_TTL": "600",
            "LOG_LEVEL": "DEBUG",
            "LOG_FORMAT": "text",
            "LOG_FILE": "/env/logs/security.log",
            "MAX_CONNECTIONS": "50",
            "CONNECTION_TIMEOUT": "60",
            "REQUEST_TIMEOUT": "120",
            "DEBUG_MODE": "true",
            "TEST_MODE": "true",
        },
    )
    def test_config_from_env(self):
        """Test configuration creation from environment variables"""
        config = AbenaSecurityConfig.from_env()

        assert config.database_url == "postgresql://env:pass@localhost/env_db"
        assert config.redis_url == "redis://localhost:6380"
        assert config.master_key_path == "/env/secure/key"
        assert config.encryption_algorithm == "RSA_4096"
        assert config.key_rotation_days == 180
        assert config.audit_log_level == "DEBUG"
        assert config.audit_retention_days == 3650
        assert config.compliance_framework == "GDPR"
        assert config.compliance_check_interval == 7200
        assert config.compliance_report_retention_days == 3650
        assert config.masking_enabled is False
        assert config.masking_rules_path == "/env/masking/rules.json"
        assert config.tokenization_enabled is False
        assert config.rules_auto_reload is False
        assert config.rules_cache_ttl == 600
        assert config.log_level == "DEBUG"
        assert config.log_format == "text"
        assert config.log_file == "/env/logs/security.log"
        assert config.max_connections == 50
        assert config.connection_timeout == 60
        assert config.request_timeout == 120
        assert config.debug_mode is True
        assert config.test_mode is True

    def test_config_from_file(self):
        """Test configuration creation from JSON file"""
        config_data = {
            "database_url": "postgresql://file:pass@localhost/file_db",
            "redis_url": "redis://localhost:6381",
            "master_key_path": "/file/secure/key",
            "encryption_algorithm": "AES_256_GCM",
            "key_rotation_days": 365,
            "audit_log_level": "INFO",
            "audit_retention_days": 2555,
            "compliance_framework": "HIPAA",
            "masking_enabled": True,
            "tokenization_enabled": True,
            "rules_auto_reload": True,
            "log_level": "INFO",
            "max_connections": 20,
            "debug_mode": False,
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            config = AbenaSecurityConfig.from_file(config_file)

            assert (
                config.database_url
                == "postgresql://file:pass@localhost/file_db"
            )
            assert config.redis_url == "redis://localhost:6381"
            assert config.master_key_path == "/file/secure/key"
            assert config.encryption_algorithm == "AES_256_GCM"
            assert config.key_rotation_days == 365
            assert config.audit_log_level == "INFO"
            assert config.audit_retention_days == 2555
            assert config.compliance_framework == "HIPAA"
            assert config.masking_enabled is True
            assert config.tokenization_enabled is True
            assert config.rules_auto_reload is True
            assert config.log_level == "INFO"
            assert config.max_connections == 20
            assert config.debug_mode is False
        finally:
            os.unlink(config_file)

    def test_config_from_file_not_found(self):
        """Test configuration creation from non-existent file"""
        with pytest.raises(
            FileNotFoundError, match="Configuration file not found"
        ):
            AbenaSecurityConfig.from_file("/nonexistent/config.json")

    def test_config_to_dict(self):
        """Test configuration conversion to dictionary"""
        config = AbenaSecurityConfig(
            database_url="postgresql://test:pass@localhost/test_db",
            redis_url="redis://localhost:6379",
            master_key_path="/test/secure/key",
            encryption_algorithm="AES_256_GCM",
            key_rotation_days=365,
            audit_log_level="INFO",
            audit_retention_days=2555,
            compliance_framework="HIPAA",
            masking_enabled=True,
            tokenization_enabled=True,
            rules_auto_reload=True,
            log_level="INFO",
            max_connections=20,
            debug_mode=False,
            custom_settings={"custom_key": "custom_value"},
        )

        result = config.to_dict()

        assert (
            result["database_url"]
            == "postgresql://test:pass@localhost/test_db"
        )
        assert result["redis_url"] == "redis://localhost:6379"
        assert result["master_key_path"] == "/test/secure/key"
        assert result["encryption_algorithm"] == "AES_256_GCM"
        assert result["key_rotation_days"] == 365
        assert result["audit_log_level"] == "INFO"
        assert result["audit_retention_days"] == 2555
        assert result["compliance_framework"] == "HIPAA"
        assert result["masking_enabled"] is True
        assert result["tokenization_enabled"] is True
        assert result["rules_auto_reload"] is True
        assert result["log_level"] == "INFO"
        assert result["max_connections"] == 20
        assert result["debug_mode"] is False
        assert result["custom_settings"]["custom_key"] == "custom_value"

    def test_config_save_to_file(self):
        """Test configuration saving to file"""
        config = AbenaSecurityConfig(
            database_url="postgresql://save:pass@localhost/save_db",
            redis_url="redis://localhost:6379",
            master_key_path="/save/secure/key",
            custom_settings={"save_key": "save_value"},
        )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            config_file = f.name

        try:
            config.save_to_file(config_file)

            # Verify the file was created and contains correct data
            assert os.path.exists(config_file)

            with open(config_file, "r") as f:
                saved_data = json.load(f)

            assert (
                saved_data["database_url"]
                == "postgresql://save:pass@localhost/save_db"
            )
            assert saved_data["redis_url"] == "redis://localhost:6379"
            assert saved_data["master_key_path"] == "/save/secure/key"
            assert saved_data["custom_settings"]["save_key"] == "save_value"
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_config_get_setting(self):
        """Test getting custom configuration setting"""
        config = AbenaSecurityConfig()
        config.custom_settings = {"test_key": "test_value", "number_key": 42}

        assert config.get_setting("test_key") == "test_value"
        assert config.get_setting("number_key") == 42
        assert config.get_setting("nonexistent_key") is None
        assert config.get_setting("nonexistent_key", "default") == "default"

    def test_config_set_setting(self):
        """Test setting custom configuration setting"""
        config = AbenaSecurityConfig()

        config.set_setting("new_key", "new_value")
        config.set_setting("number_setting", 123)

        assert config.custom_settings["new_key"] == "new_value"
        assert config.custom_settings["number_setting"] == 123

    def test_config_default_paths(self):
        """Test default path generation"""
        config = AbenaSecurityConfig()

        # Test that default paths are set
        assert config.masking_rules_path is not None
        assert config.log_file is not None

        # Test that paths contain expected directories
        assert (
            "config" in config.masking_rules_path
            or "masking_rules.json" in config.masking_rules_path
        )
        assert (
            "log" in config.log_file
            or "abena-ihr-security.log" in config.log_file
        )

    @patch.dict(os.environ, {"LOG_DIR": "/custom/log/dir"})
    def test_config_custom_log_dir(self):
        """Test configuration with custom log directory"""
        config = AbenaSecurityConfig()

        assert "/custom/log/dir" in config.log_file
        assert "abena-ihr-security.log" in config.log_file
