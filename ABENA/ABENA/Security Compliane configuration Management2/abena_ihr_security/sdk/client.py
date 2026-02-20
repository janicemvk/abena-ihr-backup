"""
Abena Security Client - Universal Service Client

This module provides the main client interface for the Abena IHR Security SDK,
following the Abena Shared SDK - Universal Service Client pattern.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timezone

from .config import AbenaSecurityConfig
from .exceptions import AbenaSecurityException, ComplianceException
from .types import SecurityContext, ComplianceResult, AuditEvent
from ..core.module_layer import ModuleLayer

datetime.now(timezone.utc)

logger = logging.getLogger(__name__)


class AbenaSecurityClient:
    """
    Abena Security Client - Universal Service Client

    Provides a unified interface for all security,
    compliance, and configuration management services
    in the Abena IHR system.

    This client follows the Abena Shared SDK - Universal Service Client pattern
    and provides a consistent API for all security operations.
    """

    def __init__(self, config: AbenaSecurityConfig):
        """
        Initialize the Abena Security Client

        Args:
            config: Configuration object for the security client
        """
        self.config = config
        self.module_layer: Optional[ModuleLayer] = None
        self._initialized = False

        logger.info("AbenaSecurityClient initialized with config")

    async def initialize(self) -> None:
        """
        Initialize the security client and all underlying services

        Raises:
            AbenaSecurityException: If initialization fails
        """
        try:
            # Initialize the module layer
            self.module_layer = ModuleLayer(
                db_url=self.config.database_url,
                redis_url=self.config.redis_url
            )

            # Initialize all services
            await self._initialize_services()

            self._initialized = True
            logger.info("AbenaSecurityClient initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize AbenaSecurityClient: {str(e)}")
            raise AbenaSecurityException(f"Initialization failed: {str(e)}")

    async def _initialize_services(self) -> None:
        """Initialize all security services"""
        # Services are initialized by the ModuleLayer
        # This method can be extended for additional service initialization
        pass

    async def process_data_with_security(
        self,
        data: Dict[str, Any],
        context: SecurityContext, operation: str = "read"
    ) -> Dict[str, Any]:
        """
        Process data through the complete security and compliance pipeline

        Args:
            data: Data to process
            context: Security context for the operation
            operation: Type of operation (read, create, update, delete)

        Returns:
            Processing result with security flags and compliance status

        Raises:
            AbenaSecurityException: If processing fails
            ComplianceException: If compliance validation fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException(
                "Client not initialized. Call initialize() first."
            )

        try:
            # Convert SecurityContext to user_context
            # format expected by module layer
            user_context = {
                "user_id": context.user_id,
                "user_role": context.user_role,
                "source_ip": context.source_ip,
                "user_agent": context.user_agent,
                "permissions": context.permissions,
                "session_id": context.session_id,
            }

            result = await self.module_layer.process_data_with_security(
                data, user_context, operation
            )

            return result

        except Exception as e:
            logger.error(f"Data processing failed: {str(e)}")
            if "compliance" in str(e).lower():
                raise ComplianceException(
                    f"Compliance validation failed: {str(e)}"
                )
            else:
                raise AbenaSecurityException(
                    f"Data processing failed: {str(e)}"
                )

    async def encrypt_data(
            self,
            data: Union[str, bytes], key_id: str
    ) -> bytes:
        """
        Encrypt data using the encryption service

        Args:
            data: Data to encrypt
            key_id: ID of the encryption key to use

        Returns:
            Encrypted data

        Raises:
            AbenaSecurityException: If encryption fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException("Client not initialized")

        try:
            return (
                self.module_layer.encryption_service.encrypt_data(data, key_id)
            )
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise AbenaSecurityException(f"Encryption failed: {str(e)}")

    async def decrypt_data(self, encrypted_data: bytes, key_id: str) -> bytes:
        """
        Decrypt data using the encryption service

        Args:
            encrypted_data: Data to decrypt
            key_id: ID of the encryption key to use

        Returns:
            Decrypted data

        Raises:
            AbenaSecurityException: If decryption fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException("Client not initialized")

        try:
            return self.module_layer.encryption_service.decrypt_data(
                encrypted_data, key_id
            )
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise AbenaSecurityException(f"Decryption failed: {str(e)}")

    async def mask_data(
        self, data: Dict[str, Any], context: str = "default"
    ) -> Dict[str, Any]:
        """
        Apply data masking to sensitive information

        Args:
            data: Data to mask
            context: Masking context (e.g., "nurse", "technician", "default")

        Returns:
            Masked data

        Raises:
            AbenaSecurityException: If masking fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException("Client not initialized")

        try:
            return (
                self.module_layer.data_masking_service.mask_data(data, context)
            )
        except Exception as e:
            logger.error(f"Data masking failed: {str(e)}")
            raise AbenaSecurityException(f"Data masking failed: {str(e)}")

    async def log_audit_event(self, event: AuditEvent) -> str:
        """
        Log an audit event

        Args:
            event: Audit event to log

        Returns:
            Event ID of the logged event

        Raises:
            AbenaSecurityException: If logging fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException("Client not initialized")

        try:
            return await self.module_layer.audit_generator.log_event(
                {
                    "event_id": event.event_id,
                    "action": event.action,
                    "timestamp": event.timestamp,
                }
            )
        except Exception as e:
            logger.error(f"Audit logging failed: {str(e)}")
            raise AbenaSecurityException(f"Audit logging failed: {str(e)}")

    async def validate_compliance(
            self,
            context: SecurityContext
    ) -> ComplianceResult:
        """
        Validate compliance for a security context

        Args:
            context: Security context to validate

        Returns:
            Compliance validation result

        Raises:
            ComplianceException: If compliance validation fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException("Client not initialized")

        try:
            compliance_context = {
                "user_id": context.user_id,
                "user_role": context.user_role,
                "action": context.action,
                "resource_type": context.resource_type,
                "encrypted": True,
                "protocol": "https",
                "requested_fields": context.requested_fields or [],
            }

            results = (
                await self.module_layer
                .hipaa_validator.validate_compliance(compliance_context)
            )

            # Convert to ComplianceResult
            non_compliant_rules = [
                rule_id
                for rule_id, result in results.items()
                if result.status.value == "non_compliant"
            ]

            if non_compliant_rules:
                return ComplianceResult(
                    compliant=False,
                    violations=non_compliant_rules,
                    details=results,
                    timestamp=datetime.now(timezone.utc),
                )
            else:
                return ComplianceResult(
                    compliant=True,
                    violations=[],
                    details=results,
                    timestamp=datetime.now(timezone.utc),
                )

        except Exception as e:
            logger.error(f"Compliance validation failed: {str(e)}")
            raise ComplianceException(
                f"Compliance validation failed: {str(e)}"
            )

    async def get_configuration(
        self, integration_name: str, include_secrets: bool = False
    ) -> Dict[str, Any]:
        """
        Get integration configuration

        Args:
            integration_name: Name of the integration
            include_secrets: Whether to include encrypted secrets

        Returns:
            Configuration data

        Raises:
            AbenaSecurityException: If configuration retrieval fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException("Client not initialized")

        try:
            return self.module_layer.config_manager.get_integration_config(
                integration_name, include_secrets=include_secrets
            )
        except Exception as e:
            logger.error(f"Configuration retrieval failed: {str(e)}")
            raise AbenaSecurityException(
                f"Configuration retrieval failed: {str(e)}"
            )

    async def apply_business_rules(
        self, data: Dict[str, Any], rule_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply business rules to data

        Args:
            data: Data to process
            rule_type: Type of rules to apply (validation,
            transformation, compliance)

        Returns:
            Processing result with applied rules and actions

        Raises:
            AbenaSecurityException: If rule processing fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException("Client not initialized")

        try:
            return (
                self.module_layer
                .business_rules_engine.apply_rules(data, rule_type)
            )
        except Exception as e:
            logger.error(f"Business rules processing failed: {str(e)}")
            raise AbenaSecurityException(
                f"Business rules processing failed: {str(e)}"
            )

    async def generate_compliance_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate compliance report for a time period

        Args:
            start_date: Start of reporting period
            end_date: End of reporting period

        Returns:
            Compliance report data

        Raises:
            AbenaSecurityException: If report generation fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException("Client not initialized")

        try:
            return (
                await self.module_layer.hipaa_validator
                .generate_compliance_report(
                    start_date,
                    end_date,
                )
            )
        except Exception as e:
            logger.error(f"Compliance report generation failed: {str(e)}")
            raise AbenaSecurityException(
                f"Compliance report generation failed: {str(e)}"
            )

    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive compliance dashboard

        Returns:
            Dashboard data with compliance metrics

        Raises:
            AbenaSecurityException: If dashboard generation fails
        """
        if not self._initialized or not self.module_layer:
            raise AbenaSecurityException("Client not initialized")

        try:
            return await self.module_layer.generate_compliance_dashboard()
        except Exception as e:
            logger.error(f"Dashboard generation failed: {str(e)}")
            raise AbenaSecurityException(
                f"Dashboard generation failed: {str(e)}"
            )

    async def close(self) -> None:
        """
        Close the security client and cleanup resources
        """
        if self._initialized and self.module_layer:
            # Cleanup resources
            if (
                hasattr(self.module_layer, "redis_client")
                and self.module_layer.redis_client
            ):
                if hasattr(self.module_layer.redis_client, "aclose"):
                    await self.module_layer.redis_client.aclose()
                else:
                    self.module_layer.redis_client.close()

            self._initialized = False
            logger.info("AbenaSecurityClient closed")

    async def __aenter__(self):
        """Asynchronous context manager entry"""
        if not self._initialized:
            await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronous context manager exit"""
        await self.close()

    def __enter__(self):
        """Synchronous context manager entry"""
        # Note: This is not recommended for an async client.
        # Use 'async with' instead.
        if not self._initialized:
            # This is a synchronous context, so we can't await.
            # This will likely cause issues if initialize() is truly async.
            # For simplicity,we assume initialize can be called in blocking way
            # or the user is responsible for running the event loop.
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    loop.create_task(self.initialize())
                else:
                    loop.run_until_complete(self.initialize())
            except RuntimeError:
                asyncio.run(self.initialize())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Synchronous context manager exit"""
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
        except RuntimeError:
            asyncio.run(self.close())
