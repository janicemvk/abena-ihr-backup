import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings - PostgreSQL for production
    DATABASE_URL: str = "postgresql://postgres:gracy@localhost/outcome_tracking"
    
    # Application settings
    APP_NAME: str = "Outcome Tracking Module"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str = "EuBPnxK87Nu7d32gvL6OjAly611FL2P1CjpaeEXlg10"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings() 