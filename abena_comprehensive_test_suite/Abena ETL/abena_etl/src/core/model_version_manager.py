"""
Model Version Manager for Abena IHR System

This module handles conflicts between dynamic learning model updates 
and predictive analytics using older model versions through versioned 
deployment with gradual rollout strategies.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class DeploymentStage(Enum):
    """Deployment stages for gradual model rollout"""
    PILOT = "pilot"           # 10% of predictions
    BETA = "beta"             # 50% of predictions
    PRODUCTION = "production" # 100% of predictions
    ROLLBACK = "rollback"     # Emergency rollback


class ModelStatus(Enum):
    """Model deployment status"""
    TRAINING = "training"
    VALIDATION = "validation"
    STAGING = "staging"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    FAILED = "failed"


@dataclass
class ValidationMetrics:
    """Model validation metrics for deployment decisions"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    improvement: float
    validation_loss: float
    auc_score: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None


@dataclass
class ModelVersion:
    """Model version information"""
    version_id: str
    model_name: str
    created_at: datetime
    metrics: ValidationMetrics
    status: ModelStatus
    deployment_percentage: float
    rollout_stage: DeploymentStage
    training_data_hash: str
    feature_set: List[str]
    hyperparameters: Dict[str, Any]


@dataclass
class DeploymentPlan:
    """Staged deployment plan for model rollout"""
    model_version: str
    stages: List[float]  # [0.1, 0.5, 1.0] for 10% -> 50% -> 100%
    stage_duration: timedelta
    success_criteria: Dict[str, float]
    rollback_criteria: Dict[str, float]
    current_stage: int


class ModelVersionManager:
    """
    Manages model version conflicts and handles staged deployments
    to ensure smooth transitions between model versions.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize model version manager with configuration.
        
        Args:
            config: Configuration dictionary with deployment settings
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.active_models: Dict[str, ModelVersion] = {}
        self.deployment_plans: Dict[str, DeploymentPlan] = {}
        
    def _get_default_config(self) -> Dict:
        """Get default configuration for model deployment"""
        return {
            'improvement_threshold': 0.05,  # 5% improvement required
            'pilot_percentage': 0.1,        # 10% pilot deployment
            'beta_percentage': 0.5,         # 50% beta deployment
            'stage_duration_hours': 24,     # 24 hours per stage
            'rollback_threshold': -0.02,    # 2% performance drop triggers rollback
            'max_concurrent_deployments': 3,
            'validation_window_hours': 72,
            'monitoring_interval_minutes': 15
        }
    
    def deploy_updated_model(
        self, 
        new_model: Any, 
        validation_metrics: ValidationMetrics,
        model_name: str = "prediction_model"
    ) -> Dict[str, Any]:
        """
        Deploy updated model with staged rollout if improvement threshold is met.
        
        Args:
            new_model: The new trained model object
            validation_metrics: Validation results for the new model
            model_name: Name/identifier for the model
            
        Returns:
            Dictionary with deployment status and plan
        """
        self.logger.info(f"Evaluating deployment for model: {model_name}")
        
        # Check if improvement meets threshold
        if validation_metrics.improvement < self.config['improvement_threshold']:
            self.logger.warning(
                f"Model improvement ({validation_metrics.improvement:.3f}) "
                f"below threshold ({self.config['improvement_threshold']})"
            )
            return {
                'status': 'rejected',
                'reason': 'Insufficient improvement',
                'improvement': validation_metrics.improvement,
                'threshold': self.config['improvement_threshold']
            }
        
        # Create new model version
        version_id = self._generate_version_id(model_name)
        model_version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            created_at=datetime.now(),
            metrics=validation_metrics,
            status=ModelStatus.STAGING,
            deployment_percentage=0.0,
            rollout_stage=DeploymentStage.PILOT,
            training_data_hash=self._calculate_data_hash(new_model),
            feature_set=self._extract_feature_set(new_model),
            hyperparameters=self._extract_hyperparameters(new_model)
        )
        
        # Create deployment plan
        stages = [
            self.config['pilot_percentage'],
            self.config['beta_percentage'],
            1.0
        ]
        
        deployment_plan = self._create_deployment_plan(model_version, stages)
        
        # Start staged deployment
        return self.staged_deployment(model_version, deployment_plan)
    
    def staged_deployment(
        self, 
        model_version: ModelVersion, 
        deployment_plan: DeploymentPlan
    ) -> Dict[str, Any]:
        """
        Execute staged deployment with gradual rollout.
        
        Args:
            model_version: The model version to deploy
            deployment_plan: Staged deployment plan
            
        Returns:
            Dictionary with deployment status and monitoring info
        """
        self.logger.info(f"Starting staged deployment for {model_version.version_id}")
        
        # Store deployment plan
        self.deployment_plans[model_version.version_id] = deployment_plan
        self.active_models[model_version.version_id] = model_version
        
        # Start with pilot stage
        self._deploy_to_stage(model_version, deployment_plan.stages[0])
        
        return {
            'status': 'deploying',
            'version_id': model_version.version_id,
            'current_stage': 'pilot',
            'deployment_percentage': deployment_plan.stages[0] * 100,
            'next_stage_in': deployment_plan.stage_duration,
            'monitoring_url': f"/api/models/{model_version.version_id}/monitoring"
        }
    
    def _deploy_to_stage(self, model_version: ModelVersion, percentage: float) -> None:
        """Deploy model to specific percentage of traffic"""
        model_version.deployment_percentage = percentage
        
        if percentage <= 0.1:
            model_version.rollout_stage = DeploymentStage.PILOT
        elif percentage <= 0.5:
            model_version.rollout_stage = DeploymentStage.BETA
        else:
            model_version.rollout_stage = DeploymentStage.PRODUCTION
        
        self.logger.info(
            f"Deployed {model_version.version_id} to {percentage*100:.1f}% "
            f"({model_version.rollout_stage.value})"
        )
    
    def check_deployment_health(self, version_id: str) -> Dict[str, Any]:
        """
        Check health of deployed model and decide on next stage or rollback.
        
        Args:
            version_id: Version ID of the deployed model
            
        Returns:
            Health status and recommended action
        """
        if version_id not in self.active_models:
            return {'status': 'error', 'message': 'Model version not found'}
        
        model_version = self.active_models[version_id]
        deployment_plan = self.deployment_plans.get(version_id)
        
        if not deployment_plan:
            return {'status': 'error', 'message': 'Deployment plan not found'}
        
        # Get current performance metrics
        current_metrics = self._get_current_performance(version_id)
        
        # Check rollback criteria
        if self._should_rollback(current_metrics, deployment_plan.rollback_criteria):
            return self._execute_rollback(version_id, "Performance degradation detected")
        
        # Check success criteria for next stage
        if self._meets_success_criteria(current_metrics, deployment_plan.success_criteria):
            return self._advance_to_next_stage(version_id)
        
        return {
            'status': 'monitoring',
            'version_id': version_id,
            'current_stage': model_version.rollout_stage.value,
            'deployment_percentage': model_version.deployment_percentage * 100,
            'metrics': current_metrics
        }
    
    def _should_rollback(self, metrics: Dict, rollback_criteria: Dict) -> bool:
        """Check if rollback is needed based on performance metrics"""
        for metric_name, threshold in rollback_criteria.items():
            if metric_name in metrics:
                if metrics[metric_name] < threshold:
                    self.logger.warning(
                        f"Rollback criteria met: {metric_name} = {metrics[metric_name]} "
                        f"< {threshold}"
                    )
                    return True
        return False
    
    def _meets_success_criteria(self, metrics: Dict, success_criteria: Dict) -> bool:
        """Check if success criteria are met for advancing to next stage"""
        for metric_name, threshold in success_criteria.items():
            if metric_name in metrics:
                if metrics[metric_name] < threshold:
                    return False
        return True
    
    def _advance_to_next_stage(self, version_id: str) -> Dict[str, Any]:
        """Advance deployment to the next stage"""
        model_version = self.active_models[version_id]
        deployment_plan = self.deployment_plans[version_id]
        
        current_stage = deployment_plan.current_stage
        
        if current_stage >= len(deployment_plan.stages) - 1:
            # Already at final stage
            model_version.status = ModelStatus.ACTIVE
            return {
                'status': 'completed',
                'version_id': version_id,
                'message': 'Deployment completed successfully'
            }
        
        # Advance to next stage
        deployment_plan.current_stage += 1
        next_percentage = deployment_plan.stages[deployment_plan.current_stage]
        
        self._deploy_to_stage(model_version, next_percentage)
        
        return {
            'status': 'advanced',
            'version_id': version_id,
            'new_stage': model_version.rollout_stage.value,
            'deployment_percentage': next_percentage * 100
        }
    
    def _execute_rollback(self, version_id: str, reason: str) -> Dict[str, Any]:
        """Execute emergency rollback to previous stable version"""
        self.logger.error(f"Executing rollback for {version_id}: {reason}")
        
        model_version = self.active_models[version_id]
        model_version.status = ModelStatus.FAILED
        model_version.rollout_stage = DeploymentStage.ROLLBACK
        model_version.deployment_percentage = 0.0
        
        # Find previous stable version
        previous_version = self._get_previous_stable_version(model_version.model_name)
        
        return {
            'status': 'rolled_back',
            'failed_version': version_id,
            'active_version': previous_version.version_id if previous_version else None,
            'reason': reason,
            'rollback_time': datetime.now().isoformat()
        }
    
    def _create_deployment_plan(
        self, 
        model_version: ModelVersion, 
        stages: List[float]
    ) -> DeploymentPlan:
        """Create deployment plan with success and rollback criteria"""
        return DeploymentPlan(
            model_version=model_version.version_id,
            stages=stages,
            stage_duration=timedelta(hours=self.config['stage_duration_hours']),
            success_criteria={
                'accuracy': model_version.metrics.accuracy - 0.01,  # Allow 1% degradation
                'f1_score': model_version.metrics.f1_score - 0.01,
                'error_rate': 0.05  # Max 5% error rate
            },
            rollback_criteria={
                'accuracy': model_version.metrics.accuracy + self.config['rollback_threshold'],
                'error_rate': 0.10,  # 10% error rate triggers rollback
                'response_time_ms': 1000  # 1 second response time limit
            },
            current_stage=0
        )
    
    def _generate_version_id(self, model_name: str) -> str:
        """Generate unique version ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{model_name}_v{timestamp}"
    
    def _calculate_data_hash(self, model: Any) -> str:
        """Calculate hash of training data used"""
        # Placeholder - would calculate actual hash of training data
        return f"hash_{datetime.now().strftime('%Y%m%d')}"
    
    def _extract_feature_set(self, model: Any) -> List[str]:
        """Extract feature set used by the model"""
        # Placeholder - would extract actual features
        return ["age", "gender", "medical_history", "medications", "vitals"]
    
    def _extract_hyperparameters(self, model: Any) -> Dict[str, Any]:
        """Extract model hyperparameters"""
        # Placeholder - would extract actual hyperparameters
        return {"learning_rate": 0.001, "epochs": 100, "batch_size": 32}
    
    def _get_current_performance(self, version_id: str) -> Dict[str, float]:
        """Get current performance metrics for deployed model"""
        # Placeholder - would get actual performance from monitoring system
        return {
            "accuracy": 0.92,
            "f1_score": 0.89,
            "precision": 0.91,
            "recall": 0.87,
            "error_rate": 0.03,
            "response_time_ms": 250
        }
    
    def _get_previous_stable_version(self, model_name: str) -> Optional[ModelVersion]:
        """Get the previous stable version for rollback"""
        stable_versions = [
            mv for mv in self.active_models.values() 
            if mv.model_name == model_name and mv.status == ModelStatus.ACTIVE
        ]
        
        if stable_versions:
            return max(stable_versions, key=lambda x: x.created_at)
        return None
    
    def get_deployment_status(self, model_name: str) -> Dict[str, Any]:
        """Get current deployment status for a model"""
        active_versions = [
            mv for mv in self.active_models.values() 
            if mv.model_name == model_name
        ]
        
        return {
            'model_name': model_name,
            'active_versions': len(active_versions),
            'versions': [
                {
                    'version_id': mv.version_id,
                    'status': mv.status.value,
                    'deployment_percentage': mv.deployment_percentage * 100,
                    'stage': mv.rollout_stage.value,
                    'created_at': mv.created_at.isoformat()
                }
                for mv in active_versions
            ]
        }


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    manager = ModelVersionManager()
    
    # Mock validation metrics showing 7% improvement
    validation_metrics = ValidationMetrics(
        accuracy=0.92,
        precision=0.90,
        recall=0.88,
        f1_score=0.89,
        improvement=0.07,  # 7% improvement
        validation_loss=0.15
    )
    
    # Deploy updated model
    result = manager.deploy_updated_model(
        new_model=None,  # Mock model
        validation_metrics=validation_metrics,
        model_name="treatment_prediction_model"
    )
    
    # Convert timedelta to string for JSON serialization
    if 'next_stage_in' in result:
        result['next_stage_in'] = str(result['next_stage_in'])
    
    print(f"Deployment result: {json.dumps(result, indent=2)}")
    
    # Test insufficient improvement
    print("\n=== Testing Model Rejection ===")
    low_improvement_metrics = ValidationMetrics(
        accuracy=0.85,
        precision=0.83,
        recall=0.82,
        f1_score=0.84,
        improvement=0.03,  # 3% improvement - below threshold
        validation_loss=0.18
    )
    
    rejection_result = manager.deploy_updated_model(
        new_model=None,
        validation_metrics=low_improvement_metrics,
        model_name="treatment_prediction_model_v2"
    )
    
    print(f"Rejection result: {json.dumps(rejection_result, indent=2)}")
    
    # Test deployment status
    print("\n=== Deployment Status ===")
    status = manager.get_deployment_status("treatment_prediction_model")
    print(f"Status: {json.dumps(status, indent=2, default=str)}")
    
    print("\n✅ ModelVersionManager tests completed successfully!") 