from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Enhanced application settings with Abena SDK configuration"""
    
    # Application settings
    APP_NAME: str = "Abena IHR Dynamic Learning Platform"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # ✅ Abena SDK Configuration
    ABENA_API_KEY: str = os.getenv("ABENA_API_KEY", "your_api_key_here")
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:3001")
    DATA_SERVICE_URL: str = os.getenv("DATA_SERVICE_URL", "http://localhost:8001") 
    PRIVACY_SERVICE_URL: str = os.getenv("PRIVACY_SERVICE_URL", "http://localhost:8002")
    BLOCKCHAIN_SERVICE_URL: str = os.getenv("BLOCKCHAIN_SERVICE_URL", "http://localhost:8003")
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:4005",  # eCDome Intelligence
        "http://localhost:4006",  # Gamification
        "http://localhost:4007",  # Unified Integration
        "http://localhost:4008",  # Provider Dashboard
        "http://localhost:4009",  # Patient Dashboard
        "http://localhost:4011",  # Data Ingestion
        "http://localhost:4012",  # Biomarker GUI
        "http://localhost:8000",  # Telemedicine Platform
        "http://localhost:8080",  # API Gateway
        "https://abena-ihr.com"
    ]
    
    # Legacy database settings (for fallback only)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings() 