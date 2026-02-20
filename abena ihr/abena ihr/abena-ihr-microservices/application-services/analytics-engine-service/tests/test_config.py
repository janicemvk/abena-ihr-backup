"""
Test configuration module for Analytics Engine Service
=====================================================

This module tests the configuration settings and environment variable loading.
"""

import pytest
import os
from src.config import Settings, get_settings, get_redis_config, get_database_config

class TestSettings:
    """Test the Settings class"""
    
    def test_default_values(self):
        """Test that default values are set correctly"""
        settings = Settings()
        assert settings.port == 8004
        assert settings.service_name == "analytics-engine-service"
        assert settings.log_level == "INFO"
        assert settings.enable_gpu is False
        assert settings.batch_size == 32
        
    def test_environment_override(self):
        """Test that environment variables override defaults"""
        os.environ["PORT"] = "9000"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["ENABLE_GPU"] = "true"
        
        settings = Settings()
        assert settings.port == 9000
        assert settings.log_level == "DEBUG"
        assert settings.enable_gpu is True
        
        # Clean up
        del os.environ["PORT"]
        del os.environ["LOG_LEVEL"]
        del os.environ["ENABLE_GPU"]
        
    def test_get_settings(self):
        """Test the get_settings function"""
        settings = get_settings()
        assert isinstance(settings, Settings)
        assert settings.service_name == "analytics-engine-service"

class TestRedisConfig:
    """Test Redis configuration parsing"""
    
    def test_redis_config_with_password(self):
        """Test Redis config parsing with password"""
        os.environ["REDIS_URL"] = "redis://:mypassword@redis-host:6379"
        
        config = get_redis_config()
        assert config["host"] == "redis-host"
        assert config["port"] == 6379
        assert config["password"] == "mypassword"
        assert config["decode_responses"] is True
        
        del os.environ["REDIS_URL"]
        
    def test_redis_config_without_password(self):
        """Test Redis config parsing without password"""
        os.environ["REDIS_URL"] = "redis://localhost:6379"
        
        config = get_redis_config()
        assert config["host"] == "localhost"
        assert config["port"] == 6379
        assert config["password"] is None
        assert config["decode_responses"] is True
        
        del os.environ["REDIS_URL"]

class TestDatabaseConfig:
    """Test database configuration"""
    
    def test_database_config(self):
        """Test database config parsing"""
        os.environ["DATABASE_URL"] = "postgresql://user:pass@host:5432/db"
        
        config = get_database_config()
        assert config["url"] == "postgresql://user:pass@host:5432/db"
        assert config["pool_size"] == 10
        assert config["max_overflow"] == 20
        
        del os.environ["DATABASE_URL"]

if __name__ == "__main__":
    pytest.main([__file__]) 