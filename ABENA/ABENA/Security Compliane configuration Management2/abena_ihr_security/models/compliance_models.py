"""
Compliance Models for Abena IHR Security

This module contains database models for HIPAA compliance tracking,
including compliance findings and reports.
"""

from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base
from typing import Type

Base: Type = declarative_base()


class ComplianceFinding(Base):
    """
    Compliance Finding Model

    Stores individual compliance findings or violations
    for tracking and remediation.
    """

    __tablename__ = "compliance_findings"

    id = Column(Integer, primary_key=True)
    finding_id = Column(String(36), unique=True, nullable=False)
    report_id = Column(String(36))
    check_id = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # critical,high,medium,low
    status = Column(String(20), default="open")  # open, closed, risk_accepted
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return (
            f"<ComplianceFinding(finding_id='{self.finding_id}', "
            f"severity='{self.severity}')>"
        )

    def to_dict(self):
        return {
            "finding_id": self.finding_id,
            "report_id": self.report_id,
            "check_id": self.check_id,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }


class ComplianceReport(Base):
    """
    Compliance Report Model

    Stores generated compliance reports for auditing and review.
    """

    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True)
    report_id = Column(String(36), unique=True, nullable=False)
    report_type = Column(String(50), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    compliance_score = Column(JSON)  # Changed from Float to JSON
    findings = Column(JSON)
    recommendations = Column(JSON)
    status = Column(String(20), default="draft")  # draft, final, archived
    generated_at = Column(DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return (
            f"<ComplianceReport(report_id='{self.report_id}', "
            f"type='{self.report_type}')>"
        )
