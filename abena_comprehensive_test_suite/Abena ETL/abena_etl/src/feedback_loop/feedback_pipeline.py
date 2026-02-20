# Abena IHR - Machine Learning Feedback Pipeline
# Advanced ML pipeline for continuous learning and model improvement

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
import joblib
import json
import hashlib
from pathlib import Path

# ML Libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, mean_absolute_error
)
from sklearn.base import BaseEstimator, ClassifierMixin
import optuna
from scipy import stats

# Custom imports
from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult
from src.predictive_analytics.predictive_engine import TreatmentResponsePredictor, AdverseEventPredictor

@dataclass
class OutcomeData:
    """Structure for treatment outcome data"""
    patient_id: str
    treatment_id: str
    prediction_id: str
    actual_outcome: float  # 0-1 scale for success
    outcome_date: datetime
    time_to_outcome: int  # days
    adverse_events: List[str]
    side_effects: List[str]
    patient_satisfaction: float  # 1-10 scale
    provider_assessment: str
    pain_reduction: float  # baseline - current
    functional_improvement: float
    medication_adherence: float  # 0-1 scale
    quality_of_life_change: float
    healthcare_utilization: Dict[str, int]  # visits, ER, hospitalizations
    cost_effectiveness: float
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelPerformanceMetrics:
    """Model performance tracking"""
    model_id: str
    model_version: str
    evaluation_date: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    mse: float
    mae: float
    false_positive_rate: float
    false_negative_rate: float
    calibration_score: float
    feature_importance: Dict[str, float]
    prediction_confidence: float
    clinical_utility_score: float
    sample_size: int
    population_coverage: Dict[str, float]  # demographic coverage

@dataclass
class LearningInsight:
    """Insights derived from outcome analysis"""
    insight_id: str
    insight_type: str  # 'pattern', 'improvement', 'concern', 'opportunity'
    description: str
    affected_population: str
    confidence_level: float
    clinical_significance: str  # 'high', 'moderate', 'low'
    actionable_recommendations: List[str]
    supporting_evidence: Dict[str, Any]
    validation_status: str  # 'pending', 'validated', 'rejected'
    discovered_date: datetime

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

class OutcomeAnalyzer:
    """Analyzes treatment outcomes and identifies patterns"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.outcome_cache = {}
    
    def analyze_prediction_accuracy(self, outcomes: List[OutcomeData], 
                                  predictions: List[PredictionResult]) -> Dict:
        """Analyze how well predictions match actual outcomes"""
        
        # Create prediction-outcome pairs
        prediction_map = {pred.patient_id + "_" + pred.treatment_id: pred 
                         for pred in predictions}
        
        matched_pairs = []
        for outcome in outcomes:
            key = outcome.patient_id + "_" + outcome.treatment_id
            if key in prediction_map:
                matched_pairs.append((prediction_map[key], outcome))
        
        if not matched_pairs:
            return {"error": "No matched prediction-outcome pairs found"}
        
        # Calculate accuracy metrics
        predicted_probs = [pair[0].success_probability for pair in matched_pairs]
        actual_outcomes = [pair[1].actual_outcome for pair in matched_pairs]
        
        # Convert probabilities to binary predictions (threshold = 0.5)
        predicted_binary = [1 if prob > 0.5 else 0 for prob in predicted_probs]
        actual_binary = [1 if outcome > 0.6 else 0 for outcome in actual_outcomes]
        
        accuracy = accuracy_score(actual_binary, predicted_binary)
        precision = precision_score(actual_binary, predicted_binary, zero_division=0)
        recall = recall_score(actual_binary, predicted_binary, zero_division=0)
        f1 = f1_score(actual_binary, predicted_binary, zero_division=0)
        
        # AUC for probability predictions
        auc = roc_auc_score(actual_binary, predicted_probs) if len(set(actual_binary)) > 1 else 0.5
        
        # Calibration analysis
        calibration_error = self._calculate_calibration_error(predicted_probs, actual_binary)
        
        # Clinical utility metrics
        clinical_utility = self._calculate_clinical_utility(matched_pairs)
        
        return {
            "sample_size": len(matched_pairs),
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "auc_roc": auc,
            "calibration_error": calibration_error,
            "clinical_utility": clinical_utility,
            "prediction_distribution": self._analyze_prediction_distribution(predicted_probs),
            "outcome_distribution": self._analyze_outcome_distribution(actual_outcomes)
        }
    
    def _calculate_calibration_error(self, predicted_probs: List[float], 
                                   actual_binary: List[int]) -> float:
        """Calculate calibration error (reliability)"""
        if len(predicted_probs) < 10:
            return 0.0
        
        # Bin predictions and calculate calibration error
        bins = np.linspace(0, 1, 11)
        calibration_error = 0.0
        
        for i in range(len(bins) - 1):
            bin_mask = (np.array(predicted_probs) >= bins[i]) & (np.array(predicted_probs) < bins[i+1])
            if np.sum(bin_mask) > 0:
                bin_accuracy = np.mean(np.array(actual_binary)[bin_mask])
                bin_confidence = np.mean(np.array(predicted_probs)[bin_mask])
                bin_weight = np.sum(bin_mask) / len(predicted_probs)
                calibration_error += bin_weight * abs(bin_confidence - bin_accuracy)
        
        return calibration_error
    
    def _calculate_clinical_utility(self, matched_pairs: List[Tuple]) -> Dict:
        """Calculate clinical utility metrics"""
        correct_high_confidence = 0
        total_high_confidence = 0
        treatment_changes = 0
        
        for prediction, outcome in matched_pairs:
            # High confidence predictions
            if prediction.success_probability > 0.8 or prediction.success_probability < 0.2:
                total_high_confidence += 1
                predicted_success = prediction.success_probability > 0.5
                actual_success = outcome.actual_outcome > 0.6
                if predicted_success == actual_success:
                    correct_high_confidence += 1
            
            # Treatment modification based on warnings
            if prediction.warnings:
                treatment_changes += 1
        
        high_confidence_accuracy = (correct_high_confidence / total_high_confidence 
                                   if total_high_confidence > 0 else 0)
        
        return {
            "high_confidence_accuracy": high_confidence_accuracy,
            "high_confidence_predictions": total_high_confidence,
            "treatment_modifications": treatment_changes,
            "clinical_actionability": len([p for p, o in matched_pairs if p.warnings]) / len(matched_pairs)
        }
    
    def _analyze_prediction_distribution(self, predictions: List[float]) -> Dict:
        """Analyze distribution of predictions"""
        predictions = np.array(predictions)
        return {
            "mean": float(np.mean(predictions)),
            "std": float(np.std(predictions)),
            "median": float(np.median(predictions)),
            "q25": float(np.percentile(predictions, 25)),
            "q75": float(np.percentile(predictions, 75)),
            "high_confidence_rate": float(np.sum((predictions > 0.8) | (predictions < 0.2)) / len(predictions))
        }
    
    def _analyze_outcome_distribution(self, outcomes: List[float]) -> Dict:
        """Analyze distribution of actual outcomes"""
        outcomes = np.array(outcomes)
        return {
            "mean": float(np.mean(outcomes)),
            "std": float(np.std(outcomes)),
            "success_rate": float(np.sum(outcomes > 0.6) / len(outcomes)),
            "excellent_outcome_rate": float(np.sum(outcomes > 0.8) / len(outcomes)),
            "poor_outcome_rate": float(np.sum(outcomes < 0.4) / len(outcomes))
        }
    
    def identify_performance_patterns(self, outcomes: List[OutcomeData]) -> List[LearningInsight]:
        """Identify patterns in model performance"""
        insights = []
        
        # Analyze by patient demographics
        demographic_insights = self._analyze_demographic_performance(outcomes)
        insights.extend(demographic_insights)
        
        # Analyze by treatment type
        treatment_insights = self._analyze_treatment_performance(outcomes)
        insights.extend(treatment_insights)
        
        # Analyze temporal patterns
        temporal_insights = self._analyze_temporal_patterns(outcomes)
        insights.extend(temporal_insights)
        
        # Analyze adverse events
        safety_insights = self._analyze_safety_patterns(outcomes)
        insights.extend(safety_insights)
        
        return insights
    
    def _analyze_demographic_performance(self, outcomes: List[OutcomeData]) -> List[LearningInsight]:
        """Analyze performance across demographic groups"""
        insights = []
        
        # Group outcomes by demographics (simplified - would need patient demographics)
        # This is a placeholder for demographic analysis
        
        insight = LearningInsight(
            insight_id=f"demographic_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            insight_type="pattern",
            description="Demographic performance analysis completed",
            affected_population="All patient groups",
            confidence_level=0.8,
            clinical_significance="moderate",
            actionable_recommendations=[
                "Continue monitoring demographic performance",
                "Consider stratified model training"
            ],
            supporting_evidence={"sample_size": len(outcomes)},
            validation_status="pending",
            discovered_date=datetime.now()
        )
        insights.append(insight)
        
        return insights
    
    def _analyze_treatment_performance(self, outcomes: List[OutcomeData]) -> List[LearningInsight]:
        """Analyze performance by treatment type"""
        insights = []
        
        # Group by treatment types
        treatment_outcomes = {}
        for outcome in outcomes:
            treatment_type = outcome.additional_metrics.get('treatment_type', 'unknown')
            if treatment_type not in treatment_outcomes:
                treatment_outcomes[treatment_type] = []
            treatment_outcomes[treatment_type].append(outcome.actual_outcome)
        
        # Find treatments with consistently poor outcomes
        for treatment_type, outcomes_list in treatment_outcomes.items():
            if len(outcomes_list) >= 10:  # Minimum sample size
                success_rate = sum(1 for o in outcomes_list if o > 0.6) / len(outcomes_list)
                
                if success_rate < 0.4:  # Poor performance threshold
                    insight = LearningInsight(
                        insight_id=f"poor_treatment_{treatment_type}_{datetime.now().strftime('%Y%m%d')}",
                        insight_type="concern",
                        description=f"Treatment type '{treatment_type}' shows poor outcomes",
                        affected_population=f"Patients receiving {treatment_type}",
                        confidence_level=0.9,
                        clinical_significance="high",
                        actionable_recommendations=[
                            f"Review {treatment_type} treatment protocols",
                            "Consider alternative treatments",
                            "Implement enhanced monitoring"
                        ],
                        supporting_evidence={
                            "success_rate": success_rate,
                            "sample_size": len(outcomes_list),
                            "treatment_type": treatment_type
                        },
                        validation_status="pending",
                        discovered_date=datetime.now()
                    )
                    insights.append(insight)
        
        return insights
    
    def _analyze_temporal_patterns(self, outcomes: List[OutcomeData]) -> List[LearningInsight]:
        """Analyze temporal patterns in outcomes"""
        insights = []
        
        # Sort by outcome date
        sorted_outcomes = sorted(outcomes, key=lambda x: x.outcome_date)
        
        # Analyze recent vs historical performance
        if len(sorted_outcomes) >= 50:
            recent_cutoff = datetime.now() - timedelta(days=90)
            recent_outcomes = [o for o in sorted_outcomes if o.outcome_date >= recent_cutoff]
            historical_outcomes = [o for o in sorted_outcomes if o.outcome_date < recent_cutoff]
            
            if len(recent_outcomes) >= 10 and len(historical_outcomes) >= 10:
                recent_success_rate = sum(1 for o in recent_outcomes if o.actual_outcome > 0.6) / len(recent_outcomes)
                historical_success_rate = sum(1 for o in historical_outcomes if o.actual_outcome > 0.6) / len(historical_outcomes)
                
                improvement = recent_success_rate - historical_success_rate
                
                if abs(improvement) > 0.1:  # Significant change
                    insight_type = "improvement" if improvement > 0 else "concern"
                    significance = "high" if abs(improvement) > 0.2 else "moderate"
                    
                    insight = LearningInsight(
                        insight_id=f"temporal_trend_{datetime.now().strftime('%Y%m%d')}",
                        insight_type=insight_type,
                        description=f"Model performance has {'improved' if improvement > 0 else 'declined'} recently",
                        affected_population="All recent patients",
                        confidence_level=0.8,
                        clinical_significance=significance,
                        actionable_recommendations=[
                            "Investigate causes of performance change",
                            "Review recent data quality",
                            "Consider model retraining" if improvement < 0 else "Document successful practices"
                        ],
                        supporting_evidence={
                            "recent_success_rate": recent_success_rate,
                            "historical_success_rate": historical_success_rate,
                            "improvement": improvement,
                            "recent_sample_size": len(recent_outcomes),
                            "historical_sample_size": len(historical_outcomes)
                        },
                        validation_status="pending",
                        discovered_date=datetime.now()
                    )
                    insights.append(insight)
        
        return insights
    
    def _analyze_safety_patterns(self, outcomes: List[OutcomeData]) -> List[LearningInsight]:
        """Analyze adverse event and safety patterns"""
        insights = []
        
        # Count adverse events
        adverse_event_counts = {}
        total_patients = len(outcomes)
        
        for outcome in outcomes:
            for event in outcome.adverse_events:
                adverse_event_counts[event] = adverse_event_counts.get(event, 0) + 1
        
        # Identify frequent adverse events
        for event, count in adverse_event_counts.items():
            rate = count / total_patients
            
            if rate > 0.1:  # >10% occurrence rate
                severity = "high" if rate > 0.2 else "moderate"
                
                insight = LearningInsight(
                    insight_id=f"adverse_event_{event}_{datetime.now().strftime('%Y%m%d')}",
                    insight_type="concern",
                    description=f"High rate of adverse event: {event}",
                    affected_population=f"Patients experiencing {event}",
                    confidence_level=0.9,
                    clinical_significance=severity,
                    actionable_recommendations=[
                        f"Review protocols for {event} prevention",
                        "Enhance patient monitoring",
                        "Consider risk factor analysis",
                        "Update adverse event prediction models"
                    ],
                    supporting_evidence={
                        "event_type": event,
                        "occurrence_rate": rate,
                        "total_cases": count,
                        "total_patients": total_patients
                    },
                    validation_status="pending",
                    discovered_date=datetime.now()
                )
                insights.append(insight)
        
        return insights 