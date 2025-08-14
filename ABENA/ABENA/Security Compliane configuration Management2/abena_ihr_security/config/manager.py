"""
Configuration Manager

Provides configuration management capabilities for integrations and settings.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Service for managing configurations"""

    def __init__(self):
        """Initialize configuration manager"""
        logger.info("ConfigurationManager initialized")

        # Mock configuration data
        self.configurations = {
            "Epic_EMR": {
                "integration_name": "Epic_EMR",
                "base_url": "https://fhir.epic.com",
                "timeout": 30,
                "api_key": "encrypted_api_key_epic",
                "version": "R4",
                "auth_type": "oauth2",
            },
            "Cerner_EMR": {
                "integration_name": "Cerner_EMR",
                "base_url": "https://fhir.cerner.com",
                "timeout": 45,
                "api_key": "encrypted_api_key_cerner",
                "version": "R4",
                "auth_type": "api_key",
            },
            "Lab_System": {
                "integration_name": "Lab_System",
                "base_url": "https://lab.example.com",
                "timeout": 60,
                "api_key": "encrypted_api_key_lab",
                "version": "R4",
                "auth_type": "basic",
            },
        }

    def get_integration_config(
        self, integration_name: str, include_secrets: bool = False
    ) -> Dict[str, Any]:
        """
        Get integration configuration

        Args:
            integration_name: Name of the integration
            include_secrets: Whether to include encrypted secrets

        Returns:
            Configuration data
        """
        try:
            if integration_name not in self.configurations:
                raise ValueError(f"Integration not found: {integration_name}")

            config = self.configurations[integration_name].copy()

            # Mask secrets if not requested
            if not include_secrets and "api_key" in config:
                config["api_key"] = "***"

            logger.info(
                f"Configuration retrieved for integration: "
                f"{integration_name}"
            )
            return config

        except Exception as e:
            logger.error(f"Configuration retrieval failed: {str(e)}")
            raise

    def update_integration_config(
        self, integration_name: str, config_data: Dict[str, Any]
    ) -> bool:
        """
        Update integration configuration

        Args:
            integration_name: Name of the integration
            config_data: New configuration data

        Returns:
            True if update successful
        """
        try:
            if integration_name not in self.configurations:
                self.configurations[integration_name] = {}

            self.configurations[integration_name].update(config_data)

            logger.info(
                f"Configuration updated for integration: "
                f"{integration_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Configuration update failed: {str(e)}")
            raise

    def delete_integration_config(self, integration_name: str) -> bool:
        """
        Delete integration configuration

        Args:
            integration_name: Name of the integration

        Returns:
            True if deletion successful
        """
        try:
            if integration_name in self.configurations:
                del self.configurations[integration_name]
                logger.info(
                    f"Configuration deleted for integration: "
                    f"{integration_name}"
                )
                return True
            else:
                logger.warning(
                    f"Integration not found for deletion: {integration_name}"
                )
                return False

        except Exception as e:
            logger.error(f"Configuration deletion failed: {str(e)}")
            raise

    def list_integrations(self) -> list:
        """
        List all available integrations

        Returns:
            List of integration names
        """
        return list(self.configurations.keys())
