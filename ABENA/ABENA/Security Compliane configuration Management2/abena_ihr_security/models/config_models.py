"""
Configuration Models for Abena IHR Security

This module contains database models for configuration management,
including integration settings and business rules.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ModuleConfiguration(Base):
    """
    Module Configuration Model

    Stores configuration settings for different modules of the security SDK,
    allowing for dynamic and centralized management of behavior.
    """

    __tablename__ = "module_configurations"

    id = Column(Integer, primary_key=True)
    module_name = Column(String(100), unique=True, nullable=False)
    configuration = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return (
            f"<ModuleConfiguration(module_name='{self.module_name}',"
            f" is_active={self.is_active})>"
        )

    def get_setting(self, key: str, default=None):
        """Get a specific setting from the configuration"""
        return self.configuration.get(key, default)


class BusinessRule(Base):
    """
    Business Rule Model

    Stores business rules for data validation, transformation, and compliance.
    """

    __tablename__ = "business_rules"

    id = Column(Integer, primary_key=True)
    rule_id = Column(String(36), unique=True, nullable=False)
    rule_name = Column(String(100), nullable=False)
    description = Column(Text)
    rule_type = Column(
        String(50), nullable=False
    )  # validation, transformation, compliance
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, nullable=False)
    priority = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return (
            f"<BusinessRule(rule_name='{self.rule_name}',"
            f" type='{self.rule_type}', priority={self.priority})>"
        )
