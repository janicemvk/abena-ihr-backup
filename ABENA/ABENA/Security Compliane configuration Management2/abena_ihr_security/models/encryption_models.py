"""
Encryption Models for Abena IHR Security

This module contains database models for encryption key management,
following security best practices and Abena SDK patterns.
"""

from __future__ import annotations
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    LargeBinary,
)
from sqlalchemy.orm import declarative_base
from typing import Optional, Type

datetime.now(timezone.utc)

Base: Type = declarative_base()


class EncryptedData(Base):
    """
    Encrypted Data Model

    Stores encrypted data with metadata for secure storage and retrieval.
    """

    __tablename__ = "encrypted_data"

    id = Column(Integer, primary_key=True)
    key_id = Column(String(100), nullable=False)
    encrypted_data = Column(LargeBinary, nullable=False)
    iv = Column(LargeBinary, nullable=False)
    auth_tag = Column(LargeBinary, nullable=False)
    encryption_algorithm = Column(
        String(50), nullable=False, default="AES-256-GCM"
    )
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return (
            f"<EncryptedData(key_id='{self.key_id}', "
            f"lgorithm='{self.encryption_algorithm}')>"
        )


class EncryptionKey(Base):
    """
    Encryption Key Model for Secure Key Management

    Manages encryption keys, including their status,
    rotation, and usage policies, to ensure compliance
    with data protection regulations.
    """

    __tablename__ = "encryption_keys"

    id = Column(Integer, primary_key=True)
    key_id = Column(String(100), unique=True, nullable=False)
    key_material = Column(LargeBinary, nullable=False)
    key_status = Column(
        String(20), nullable=False, default="active"
    )  # active, inactive, compromised
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    rotation_policy = Column(String(50), default="90_days")

    def __repr__(self):
        return (
            f"<EncryptionKey(key_id='{self.key_id}',"
            f" status='{self.key_status}')>"
        )

    def is_active(self) -> bool:
        """Check if the key is active"""
        return bool(self.key_status == "active")

    def is_expired(self) -> bool:
        """Check if the key has expired"""
        return bool(
            self.expires_at and self.expires_at < datetime.now(timezone.utc)
        )

    def days_to_expiry(self) -> Optional[int]:
        """Get days until key expiry"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.now(timezone.utc)
        return delta.days
