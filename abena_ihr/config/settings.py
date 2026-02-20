"""
Settings

This module contains application settings and configuration management.
"""

import os

class Settings:
    """Application settings."""
    def __init__(self):
        self.env = os.getenv("ENV", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/abena_ihr")
        self.secret_key = os.getenv("SECRET_KEY", "changeme")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")

settings = Settings() 