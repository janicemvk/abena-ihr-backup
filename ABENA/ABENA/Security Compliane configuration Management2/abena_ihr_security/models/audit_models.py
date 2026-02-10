"""
Audit Models for Abena IHR Security

This module contains database models for audit trail functionality,
following HIPAA compliance requirements and Abena SDK patterns.
"""

from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
)
from sqlalchemy.orm import declarative_base
from typing import Type

Base: Type = declarative_base()


class AuditLog(Base):
    """
    Audit Log Model for HIPAA Compliance

    Represents a single audit log entry, capturing all relevant details
    for security and compliance monitoring.
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    event_id = Column(String(36), unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100))
    user_role = Column(String(50))
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100))
    source_ip = Column(String(45))
    user_agent = Column(JSON)
    request_data = Column(JSON)
    response_data = Column(JSON)
    status = Column(String(20), nullable=False)
    error_message = Column(JSON)
    processing_time = Column(JSON)
    compliance_flags = Column(JSON)

    def __repr__(self):
        return (
            f"<AuditLog(event_id='{self.event_id}', "
            f"action='{self.action}')>"
        )

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "user_role": self.user_role,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "request_data": self.request_data,
            "response_data": self.response_data,
            "status": self.status,
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "compliance_flags": self.compliance_flags,
        }
