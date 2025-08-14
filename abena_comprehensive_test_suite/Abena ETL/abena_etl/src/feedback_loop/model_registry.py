# Abena IHR - Model Registry
# Registry for tracking model versions and metadata

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class ModelRegistry:
    """Registry for tracking model versions and metadata"""
    
    def __init__(self, registry_path: str = "data/models/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._registry = self._load_registry()
        self.logger = logging.getLogger(__name__)
    
    def _load_registry(self) -> Dict:
        """Load model registry from file"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {"models": {}, "deployments": {}, "experiments": {}}
    
    def _save_registry(self):
        """Save model registry to file"""
        with open(self.registry_path, 'w') as f:
            json.dump(self._registry, f, indent=2, default=str)
    
    def register_model(self, model_name: str, model_version: str, 
                      model_path: str, metadata: Dict) -> str:
        """Register a new model version"""
        model_id = f"{model_name}_v{model_version}"
        
        self._registry["models"][model_id] = {
            "model_name": model_name,
            "version": model_version,
            "model_path": model_path,
            "registered_date": datetime.now().isoformat(),
            "metadata": metadata,
            "status": "registered"
        }
        
        self._save_registry()
        self.logger.info(f"Registered model: {model_id}")
        return model_id
    
    def deploy_model(self, model_id: str, deployment_environment: str = "production"):
        """Mark model as deployed"""
        if model_id in self._registry["models"]:
            self._registry["deployments"][deployment_environment] = {
                "model_id": model_id,
                "deployed_date": datetime.now().isoformat(),
                "status": "active"
            }
            self._registry["models"][model_id]["status"] = "deployed"
            self._save_registry()
            self.logger.info(f"Deployed model {model_id} to {deployment_environment}")
    
    def get_active_model(self, environment: str = "production") -> Optional[str]:
        """Get currently active model in environment"""
        if environment in self._registry["deployments"]:
            deployment = self._registry["deployments"][environment]
            if deployment["status"] == "active":
                return deployment["model_id"]
        return None
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict]:
        """Get model metadata"""
        return self._registry["models"].get(model_id) 