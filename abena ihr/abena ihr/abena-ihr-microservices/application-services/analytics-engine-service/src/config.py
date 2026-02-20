"""
Configuration module for Analytics Engine Service
================================================

This module handles all configuration settings for the analytics engine service,
including environment variables, service URLs, and operational parameters.
"""

import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Service Configuration
    port: int = int(os.getenv("PORT", "8004"))
    service_name: str = os.getenv("SERVICE_NAME", "analytics-engine-service")
    
    # Foundational Services URLs
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service:3001")
    data_service_url: str = os.getenv("DATA_SERVICE_URL", "http://data-ingestion-service:8001")
    privacy_service_url: str = os.getenv("PRIVACY_SERVICE_URL", "http://privacy-security-service:8002")
    blockchain_service_url: str = os.getenv("BLOCKCHAIN_SERVICE_URL", "http://blockchain-service:8003")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@unified-database:5432/abena_ihr_data")
    redis_url: str = os.getenv("REDIS_URL", "redis://:password@redis-cache:6379")
    
    # Analytics Configuration
    model_update_interval: str = os.getenv("MODEL_UPDATE_INTERVAL", "24h")
    prediction_cache_ttl: int = int(os.getenv("PREDICTION_CACHE_TTL", "3600"))
    monitoring_frequency_minutes: int = int(os.getenv("MONITORING_FREQUENCY_MINUTES", "5"))
    max_concurrent_sessions: int = int(os.getenv("MAX_CONCURRENT_SESSIONS", "100"))
    
    # ML Model Configuration
    model_storage_path: str = os.getenv("MODEL_STORAGE_PATH", "/app/models")
    enable_gpu: bool = os.getenv("ENABLE_GPU", "false").lower() == "true"
    batch_size: int = int(os.getenv("BATCH_SIZE", "32"))
    max_prediction_requests_per_minute: int = int(os.getenv("MAX_PREDICTION_REQUESTS_PER_MINUTE", "1000"))
    
    # Logging and Monitoring
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_performance_metrics: bool = os.getenv("ENABLE_PERFORMANCE_METRICS", "true").lower() == "true"
    prometheus_metrics_port: int = int(os.getenv("PROMETHEUS_METRICS_PORT", "9004"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the application settings"""
    return settings

def get_redis_config() -> dict:
    """Get Redis configuration from URL"""
    redis_url = settings.redis_url
    if redis_url.startswith("redis://"):
        # Parse redis://:password@host:port format
        parts = redis_url.replace("redis://", "").split("@")
        if len(parts) == 2:
            auth, host_port = parts
            password = auth.replace(":", "") if auth.startswith(":") else None
            host, port = host_port.split(":")
            return {
                "host": host,
                "port": int(port),
                "password": password,
                "decode_responses": True
            }
    return {
        "host": "localhost",
        "port": 6379,
        "decode_responses": True
    }

def get_database_config() -> dict:
    """Get database configuration from URL"""
    database_url = settings.database_url
    # This would typically parse the PostgreSQL URL
    # For now, return basic config
    return {
        "url": database_url,
        "pool_size": 10,
        "max_overflow": 20
    } 