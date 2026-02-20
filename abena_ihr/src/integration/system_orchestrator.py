"""
System Orchestrator

This module provides system-level integration and orchestration
for the Abena IHR Clinical Outcomes Management System.
"""

import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

class SystemOrchestrator:
    """System-level integration and orchestration."""
    def __init__(self):
        self.integrations: Dict[str, Any] = {}

    def register_integration(self, name: str, integration: Any):
        self.integrations[name] = integration
        logger.info(f"Registered integration: {name}")

    def get_integration(self, name: str) -> Any:
        return self.integrations.get(name)

    def list_integrations(self) -> Dict[str, Any]:
        return self.integrations.copy()

# Global instance
system_orchestrator = SystemOrchestrator()

def get_system_orchestrator() -> SystemOrchestrator:
    """Get the global system orchestrator instance."""
    return system_orchestrator 