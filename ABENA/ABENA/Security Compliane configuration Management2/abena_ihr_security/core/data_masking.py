"""
Data Masking Service

Provides data masking and anonymization capabilities for sensitive information.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DataMaskingService:
    """Service for masking sensitive data"""

    def __init__(self):
        """Initialize data masking service"""
        logger.info("DataMaskingService initialized")

    def mask_data(
        self, data: Dict[str, Any], context: str = "default"
    ) -> Dict[str, Any]:
        """
        Apply data masking to sensitive information

        Args:
            data: Data to mask
            context: Masking context (e.g., "nurse", "technician", "default")

        Returns:
            Masked data
        """
        try:
            masked_data = data.copy()

            # Apply masking based on context
            if context == "nurse":
                masked_data = self._mask_for_nurse(masked_data)
            elif context == "technician":
                masked_data = self._mask_for_technician(masked_data)
            elif context == "physician":
                masked_data = self._mask_for_physician(masked_data)
            elif context == "administrator":
                masked_data = self._mask_for_administrator(masked_data)
            else:
                masked_data = self._mask_default(masked_data)

            logger.info(f"Data masked successfully for context: {context}")
            return masked_data

        except Exception as e:
            logger.error(f"Data masking failed: {str(e)}")
            raise

    def _mask_for_nurse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask data for nurse context"""
        masked = data.copy()

        # Mask SSN
        if "ssn" in masked:
            masked["ssn"] = "XXX-XX-" + masked["ssn"][-4:]

        # Mask phone
        if "phone" in masked:
            masked["phone"] = "555-***-" + masked["phone"][-4:]

        # Mask email
        if "email" in masked:
            parts = masked["email"].split("@")
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                masked["email"] = username[:3] + "***@" + domain

        # Mask name
        if "name" in masked:
            name_parts = masked["name"].split()
            if len(name_parts) >= 2:
                masked["name"] = (
                    name_parts[0][:1] + "*** " + name_parts[-1][:1] + "***"
                )
            else:
                masked["name"] = masked["name"][:1] + "***"

        return masked

    def _mask_for_technician(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask data for technician context"""
        masked = data.copy()

        # Mask SSN
        if "ssn" in masked:
            masked["ssn"] = "XXX-XX-" + masked["ssn"][-4:]

        # Keep phone but mask last 4 digits
        if "phone" in masked:
            masked["phone"] = masked["phone"][:-4] + "****"

        # Keep email but mask username
        if "email" in masked:
            parts = masked["email"].split("@")
            if len(parts) == 2:
                # username = parts[0]
                domain = parts[1]
                masked["email"] = "***@" + domain

        # Keep full name
        return masked

    def _mask_for_physician(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask data for physician context"""
        masked = data.copy()

        # Mask SSN
        if "ssn" in masked:
            masked["ssn"] = "XXX-XX-" + masked["ssn"][-4:]

        # Keep phone
        # Keep email
        # Keep name
        return masked

    def _mask_for_administrator(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask data for administrator context"""
        masked = data.copy()

        # Mask SSN
        if "ssn" in masked:
            masked["ssn"] = "***-**-" + masked["ssn"][-4:]

        # Keep phone
        # Keep email
        # Keep name
        return masked

    def _mask_default(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Default masking - most restrictive"""
        masked = data.copy()

        # Mask SSN
        if "ssn" in masked:
            masked["ssn"] = "***-**-****"

        # Mask phone
        if "phone" in masked:
            masked["phone"] = "***-***-****"

        # Mask email
        if "email" in masked:
            masked["email"] = "***@***.com"

        # Mask name
        if "name" in masked:
            masked["name"] = "*** ***"

        return masked
