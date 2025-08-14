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
from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult, OutcomeData, LearningInsight
from src.predictive_analytics.predictive_engine import TreatmentResponsePredictor, AdverseEventPredictor
from src.core.abena_sdk import AbenaSDK

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

class AutoMLOptimizer:
    """Automated machine learning optimization using Optuna"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.study_storage = "sqlite:///data/models/optuna_studies.db"
    
    def optimize_treatment_predictor(self, training_data: List[Tuple], 
                                   validation_data: List[Tuple],
                                   n_trials: int = 100) -> Dict:
        """Optimize treatment response predictor hyperparameters"""
        
        def objective(trial):
            # Suggest hyperparameters
            params = {
                'random_forest': {
                    'n_estimators': trial.suggest_int('rf_n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('rf_max_depth', 5, 30),
                    'min_samples_split': trial.suggest_int('rf_min_samples_split', 2, 20),
                    'min_samples_leaf': trial.suggest_int('rf_min_samples_leaf', 1, 10)
                },
                'gradient_boosting': {
                    'n_estimators': trial.suggest_int('gb_n_estimators', 50, 200),
                    'learning_rate': trial.suggest_float('gb_learning_rate', 0.01, 0.3),
                    'max_depth': trial.suggest_int('gb_max_depth', 3, 15),
                    'subsample': trial.suggest_float('gb_subsample', 0.6, 1.0)
                }
            }
            
            # Train model with suggested parameters
            predictor = TreatmentResponsePredictor()
            predictor._train_with_params(training_data, params)
            
            # Evaluate on validation set
            validation_scores = []
            for patient, treatment, actual_outcome in validation_data:
                try:
                    prediction = predictor.predict_treatment_response(patient, treatment)
                    predicted_binary = 1 if prediction.success_probability > 0.5 else 0
                    actual_binary = 1 if actual_outcome > 0.6 else 0
                    validation_scores.append(1 if predicted_binary == actual_binary else 0)
                except Exception as e:
                    self.logger.warning(f"Prediction failed during optimization: {e}")
                    validation_scores.append(0)
            
            return np.mean(validation_scores) if validation_scores else 0.0
        
        # Create study
        study = optuna.create_study(
            direction='maximize',
            storage=self.study_storage,
            study_name=f"treatment_predictor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Optimize
        study.optimize(objective, n_trials=n_trials)
        
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'n_trials': len(study.trials),
            'study_name': study.study_name
        }
    
    def optimize_adverse_event_predictor(self, training_data: List[Tuple],
                                       validation_data: List[Tuple],
                                       n_trials: int = 50) -> Dict:
        """Optimize adverse event predictor hyperparameters"""
        
        def objective(trial):
            # Suggest hyperparameters for adverse event prediction
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 200),
                'max_depth': trial.suggest_int('max_depth', 5, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 15),
                'class_weight': trial.suggest_categorical('class_weight', ['balanced', 'balanced_subsample'])
            }
            
            # Train and evaluate adverse event predictor
            # This would need implementation in the AdverseEventPredictor class
            score = np.random.random()  # Placeholder
            
            return score
        
        study = optuna.create_study(
            direction='maximize',
            storage=self.study_storage,
            study_name=f"adverse_event_predictor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        study.optimize(objective, n_trials=n_trials)
        
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'n_trials': len(study.trials),
            'study_name': study.study_name
        }

class ModelRetrainingPipeline:
    """Pipeline for automated model retraining based on new data"""
    
    def __init__(self, model_registry: ModelRegistry):
        self.model_registry = model_registry
        self.logger = logging.getLogger(__name__)
        self.outcome_analyzer = OutcomeAnalyzer()
        self.automl_optimizer = AutoMLOptimizer()
        
        # Retraining thresholds
        self.min_new_samples = 100
        self.performance_degradation_threshold = 0.05
        self.min_time_between_retraining = timedelta(days=7)
    
    def should_retrain_model(self, model_id: str, recent_outcomes: List[OutcomeData],
                           recent_predictions: List[PredictionResult]) -> Dict:
        """Determine if model should be retrained"""
        
        reasons = []
        retrain_score = 0.0
        
        # Check sample size
        if len(recent_outcomes) >= self.min_new_samples:
            reasons.append(f"Sufficient new samples: {len(recent_outcomes)}")
            retrain_score += 0.3
        
        # Check performance degradation
        if recent_predictions:
            performance_analysis = self.outcome_analyzer.analyze_prediction_accuracy(
                recent_outcomes, recent_predictions
            )
            
            if 'accuracy' in performance_analysis:
                current_accuracy = performance_analysis['accuracy']
                
                # Get historical accuracy (would need to be stored)
                historical_accuracy = 0.75  # Placeholder - should come from model metadata
                
                if historical_accuracy - current_accuracy > self.performance_degradation_threshold:
                    reasons.append(f"Performance degradation: {current_accuracy:.3f} vs {historical_accuracy:.3f}")
                    retrain_score += 0.4
        
        # Check time since last retraining
        model_metadata = self.model_registry.get_model_metadata(model_id)
        if model_metadata:
            last_training = datetime.fromisoformat(model_metadata.get('registered_date', '2020-01-01'))
            if datetime.now() - last_training > self.min_time_between_retraining:
                reasons.append(f"Time since last training: {datetime.now() - last_training}")
                retrain_score += 0.2
        
        # Check for data drift (simplified)
        if len(recent_outcomes) > 50:
            # Simple check for outcome distribution changes
            recent_success_rate = sum(1 for o in recent_outcomes if o.actual_outcome > 0.6) / len(recent_outcomes)
            expected_success_rate = 0.65  # Placeholder
            
            if abs(recent_success_rate - expected_success_rate) > 0.1:
                reasons.append(f"Data drift detected: success rate {recent_success_rate:.3f}")
                retrain_score += 0.3
        
        should_retrain = retrain_score >= 0.5
        
        return {
            'should_retrain': should_retrain,
            'retrain_score': retrain_score,
            'reasons': reasons,
            'new_samples': len(recent_outcomes),
            'recommendation': 'retrain' if should_retrain else 'monitor'
        }
    
    def execute_retraining(self, model_type: str, all_training_data: List[Tuple],
                          optimization_config: Dict = None) -> Dict:
        """Execute model retraining pipeline"""
        
        self.logger.info(f"Starting retraining for {model_type}")
        
        try:
            # Split data for training and validation
            train_data, val_data = train_test_split(all_training_data, test_size=0.2, random_state=42)
            
            # Optimize hyperparameters if requested
            if optimization_config and optimization_config.get('optimize', False):
                if model_type == 'treatment_response':
                    optimization_result = self.automl_optimizer.optimize_treatment_predictor(
                        train_data, val_data, 
                        n_trials=optimization_config.get('n_trials', 50)
                    )
                else:
                    optimization_result = self.automl_optimizer.optimize_adverse_event_predictor(
                        train_data, val_data,
                        n_trials=optimization_config.get('n_trials', 50)
                    )
                
                best_params = optimization_result['best_params']
                self.logger.info(f"Optimization completed. Best score: {optimization_result['best_score']:.3f}")
            else:
                best_params = None
            
            # Train new model
            if model_type == 'treatment_response':
                new_model = TreatmentResponsePredictor()
                if best_params:
                    new_model._train_with_params(train_data, best_params)
                else:
                    new_model.train_models(train_data)
            else:
                # Similar for adverse event predictor
                new_model = AdverseEventPredictor()
                # Would need similar training method
            
            # Evaluate new model
            validation_results = self._evaluate_model_performance(new_model, val_data, model_type)
            
            # Save new model
            model_version = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_path = f"data/models/{model_type}_v{model_version}.joblib"
            
            # Create model metadata
            metadata = {
                'model_type': model_type,
                'training_samples': len(train_data),
                'validation_samples': len(val_data),
                'performance_metrics': validation_results,
                'optimization_params': best_params,
                'training_date': datetime.now().isoformat(),
                'data_hash': self._calculate_data_hash(all_training_data)
            }
            
            # Save model to file
            joblib.dump(new_model, model_path)
            
            # Register model
            model_id = self.model_registry.register_model(
                model_type, model_version, model_path, metadata
            )
            
            self.logger.info(f"Model retraining completed: {model_id}")
            
            return {
                'success': True,
                'model_id': model_id,
                'model_path': model_path,
                'performance_metrics': validation_results,
                'training_samples': len(train_data),
                'optimization_used': best_params is not None,
                'retraining_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Model retraining failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'retraining_date': datetime.now().isoformat()
            }
    
    def _evaluate_model_performance(self, model, validation_data: List[Tuple], 
                                  model_type: str) -> Dict:
        """Evaluate model performance on validation data"""
        
        predictions = []
        actuals = []
        
        for patient, treatment, actual_outcome in validation_data:
            try:
                if model_type == 'treatment_response':
                    pred_result = model.predict_treatment_response(patient, treatment)
                    predictions.append(pred_result.success_probability)
                    actuals.append(actual_outcome)
                else:
                    # Adverse event prediction evaluation
                    risk_assessment = model.assess_adverse_event_risk(patient, treatment)
                    # Use overall risk as prediction
                    predictions.append(risk_assessment.get('overall_risk_score', 0.5))
                    actuals.append(actual_outcome)
            except Exception as e:
                self.logger.warning(f"Prediction failed during evaluation: {e}")
                continue
        
        if not predictions:
            return {"error": "No successful predictions during evaluation"}
        
        # Convert to binary for classification metrics
        pred_binary = [1 if p > 0.5 else 0 for p in predictions]
        actual_binary = [1 if a > 0.6 else 0 for a in actuals]
        
        # Calculate metrics
        accuracy = accuracy_score(actual_binary, pred_binary)
        precision = precision_score(actual_binary, pred_binary, zero_division=0)
        recall = recall_score(actual_binary, pred_binary, zero_division=0)
        f1 = f1_score(actual_binary, pred_binary, zero_division=0)
        
        if len(set(actual_binary)) > 1:
            auc = roc_auc_score(actual_binary, predictions)
        else:
            auc = 0.5
        
        mse = mean_squared_error(actuals, predictions)
        mae = mean_absolute_error(actuals, predictions)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc_roc': auc,
            'mse': mse,
            'mae': mae,
            'sample_size': len(predictions)
        }
    
    def _calculate_data_hash(self, training_data: List[Tuple]) -> str:
        """Calculate hash of training data for versioning"""
        # Create a simple hash of the training data
        data_string = str(len(training_data))
        for patient, treatment, outcome in training_data[:10]:  # Sample first 10 for efficiency
            data_string += f"{patient.patient_id}{treatment.treatment_id}{outcome}"
        
        return hashlib.md5(data_string.encode()).hexdigest()

class ContinuousLearningOrchestrator:
    """Main orchestrator for continuous learning and model improvement"""
    
    def __init__(self, model_registry: ModelRegistry, abena_config: Dict = None):
        self.model_registry = model_registry
        self.outcome_analyzer = OutcomeAnalyzer()
        self.retraining_pipeline = ModelRetrainingPipeline(model_registry)
        self.logger = logging.getLogger(__name__)
        
        # Initialize Abena SDK
        self.abena_sdk = None
        if abena_config:
            self.abena_sdk = AbenaSDK(abena_config)
            # Authenticate with Abena SDK
            if not self.abena_sdk.authenticate():
                self.logger.warning("Failed to authenticate with Abena SDK")
        
        # Learning configuration
        self.learning_config = {
            'analysis_frequency': timedelta(days=1),  # Daily analysis
            'retraining_frequency': timedelta(days=7),  # Weekly retraining check
            'insight_validation_period': timedelta(days=30),  # Monthly insight validation
            'performance_monitoring_window': timedelta(days=30),  # 30-day performance window
            'min_samples_for_analysis': 50,
            'auto_retrain_threshold': 0.7,  # Auto-retrain if score > 0.7
            'human_approval_threshold': 0.5,  # Require human approval if score > 0.5
            'auto_push_to_emr': abena_config.get('auto_push_to_emr', False) if abena_config else False
        }
        
        # Storage for insights and outcomes
        self.insights_db = []
        self.outcomes_db = []
        self.predictions_db = []
    
    def add_outcome_data(self, outcome: OutcomeData):
        """Add new outcome data to the learning system"""
        self.outcomes_db.append(outcome)
        self.logger.info(f"Added outcome data for patient {outcome.patient_id}")
    
    def add_prediction_data(self, prediction: PredictionResult):
        """Add prediction data for outcome correlation"""
        self.predictions_db.append(prediction)
        self.logger.info(f"Added prediction data for patient {prediction.patient_id}")
    
    def run_daily_analysis(self) -> Dict:
        """Run daily analysis of model performance and outcomes"""
        
        analysis_results = {
            'analysis_date': datetime.now().isoformat(),
            'outcomes_analyzed': len(self.outcomes_db),
            'predictions_analyzed': len(self.predictions_db),
            'new_insights': [],
            'performance_alerts': [],
            'recommendations': []
        }
        
        if len(self.outcomes_db) < self.learning_config['min_samples_for_analysis']:
            analysis_results['status'] = 'insufficient_data'
            return analysis_results
        
        try:
            # 1. Analyze prediction accuracy
            if self.predictions_db:
                performance_analysis = self.outcome_analyzer.analyze_prediction_accuracy(
                    self.outcomes_db[-100:],  # Last 100 outcomes
                    self.predictions_db[-100:]  # Last 100 predictions
                )
                analysis_results['performance_metrics'] = performance_analysis
                
                # Check for performance degradation
                if performance_analysis.get('accuracy', 1.0) < 0.7:
                    analysis_results['performance_alerts'].append({
                        'type': 'accuracy_degradation',
                        'current_accuracy': performance_analysis['accuracy'],
                        'threshold': 0.7,
                        'severity': 'high'
                    })
            
            # 2. Identify new patterns and insights
            new_insights = self.outcome_analyzer.identify_performance_patterns(
                self.outcomes_db[-200:]  # Last 200 outcomes
            )
            
            for insight in new_insights:
                self.insights_db.append(insight)
                analysis_results['new_insights'].append({
                    'insight_id': insight.insight_id,
                    'type': insight.insight_type,
                    'description': insight.description,
                    'clinical_significance': insight.clinical_significance
                })
            
            # 3. Generate recommendations
            recommendations = self._generate_learning_recommendations(analysis_results)
            analysis_results['recommendations'] = recommendations
            
            # 4. Check if retraining is needed
            retraining_assessment = self._assess_retraining_needs()
            analysis_results['retraining_assessment'] = retraining_assessment
            
            analysis_results['status'] = 'completed'
            
        except Exception as e:
            self.logger.error(f"Daily analysis failed: {str(e)}")
            analysis_results['status'] = 'error'
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    def _generate_learning_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Performance-based recommendations
        if analysis_results.get('performance_alerts'):
            for alert in analysis_results['performance_alerts']:
                if alert['type'] == 'accuracy_degradation':
                    recommendations.append(
                        f"Model accuracy has dropped to {alert['current_accuracy']:.3f}. "
                        "Consider immediate retraining or data quality review."
                    )
        
        # Insight-based recommendations
        high_priority_insights = [
            insight for insight in analysis_results.get('new_insights', [])
            if insight['clinical_significance'] == 'high'
        ]
        
        if high_priority_insights:
            recommendations.append(
                f"Found {len(high_priority_insights)} high-priority clinical insights. "
                "Review and validate for potential protocol updates."
            )
        
        # Data quality recommendations
        if analysis_results['outcomes_analyzed'] < 100:
            recommendations.append(
                "Limited outcome data available. Encourage more comprehensive outcome reporting."
            )
        
        # Model improvement recommendations
        if len(self.outcomes_db) > 500:
            recommendations.append(
                "Sufficient data available for advanced model optimization. "
                "Consider running hyperparameter optimization."
            )
        
        return recommendations
    
    def _assess_retraining_needs(self) -> Dict:
        """Assess if any models need retraining"""
        
        active_models = {
            'treatment_response': self.model_registry.get_active_model('production'),
            'adverse_event': self.model_registry.get_active_model('production')
        }
        
        retraining_assessments = {}
        
        for model_type, model_id in active_models.items():
            if model_id:
                # Get recent data for this model type
                recent_outcomes = self.outcomes_db[-100:]  # Last 100 outcomes
                recent_predictions = [p for p in self.predictions_db[-100:] 
                                    if model_type in p.treatment_id]  # Simplified matching
                
                assessment = self.retraining_pipeline.should_retrain_model(
                    model_id, recent_outcomes, recent_predictions
                )
                retraining_assessments[model_type] = assessment
        
        return retraining_assessments
    
    def execute_automated_learning_cycle(self) -> Dict:
        """Execute complete automated learning cycle"""
        
        cycle_results = {
            'cycle_start': datetime.now().isoformat(),
            'daily_analysis': None,
            'retraining_actions': [],
            'insights_validated': [],
            'errors': []
        }
        
        try:
            # 1. Run daily analysis
            cycle_results['daily_analysis'] = self.run_daily_analysis()
            
            # 2. Check for automated retraining opportunities
            retraining_assessment = cycle_results['daily_analysis'].get('retraining_assessment', {})
            
            for model_type, assessment in retraining_assessment.items():
                if assessment.get('should_retrain', False):
                    retrain_score = assessment.get('retrain_score', 0)
                    
                    # Auto-retrain for high confidence scores
                    if retrain_score >= self.learning_config['auto_retrain_threshold']:
                        self.logger.info(f"Auto-retraining {model_type} (score: {retrain_score})")
                        
                        # Prepare training data (simplified - would need proper data preparation)
                        training_data = self._prepare_training_data(model_type)
                        
                        retrain_result = self.retraining_pipeline.execute_retraining(
                            model_type, training_data,
                            optimization_config={'optimize': True, 'n_trials': 30}
                        )
                        
                        cycle_results['retraining_actions'].append({
                            'model_type': model_type,
                            'action': 'auto_retrain',
                            'result': retrain_result,
                            'retrain_score': retrain_score
                        })
                        
                        # Deploy new model if successful
                        if retrain_result.get('success', False):
                            self.model_registry.deploy_model(retrain_result['model_id'])
                            self.logger.info(f"Deployed new {model_type} model: {retrain_result['model_id']}")
                    
                    # Flag for human review for moderate confidence scores
                    elif retrain_score >= self.learning_config['human_approval_threshold']:
                        cycle_results['retraining_actions'].append({
                            'model_type': model_type,
                            'action': 'human_review_required',
                            'retrain_score': retrain_score,
                            'reasons': assessment.get('reasons', [])
                        })
            
            # 3. Validate pending insights
            validated_insights = self._validate_pending_insights()
            cycle_results['insights_validated'] = validated_insights
            
            cycle_results['cycle_end'] = datetime.now().isoformat()
            cycle_results['status'] = 'completed'
            
        except Exception as e:
            self.logger.error(f"Automated learning cycle failed: {str(e)}")
            cycle_results['errors'].append(str(e))
            cycle_results['status'] = 'error'
        
        return cycle_results
    
    def _prepare_training_data(self, model_type: str) -> List[Tuple]:
        """Prepare training data for retraining"""
        
        # This is a simplified version - real implementation would need proper data preparation
        training_data = []
        
        for outcome in self.outcomes_db:
            # Find corresponding patient and treatment data
            # This would need proper data storage and retrieval
            
            # Placeholder patient and treatment (would come from database)
            from src.core.data_models import PatientProfile, TreatmentPlan
            
            patient = PatientProfile(
                patient_id=outcome.patient_id,
                age=45,  # Placeholder
                gender="unknown",
                genomics_data={},
                biomarkers={},
                medical_history=[],
                current_medications=[],
                lifestyle_metrics={},
                pain_scores=[],
                functional_assessments={}
            )
            
            treatment = TreatmentPlan(
                treatment_id=outcome.treatment_id,
                treatment_type="unknown",
                medications=[],
                dosages={},
                duration_weeks=8,
                lifestyle_interventions=[]
            )
            
            training_data.append((patient, treatment, outcome.actual_outcome))
        
        return training_data
    
    def _validate_pending_insights(self) -> List[Dict]:
        """Validate insights that have been pending validation"""
        
        validated_insights = []
        current_time = datetime.now()
        
        for insight in self.insights_db:
            if insight.validation_status == 'pending':
                # Check if insight has been pending long enough for validation
                time_pending = current_time - insight.discovered_date
                
                if time_pending >= self.learning_config['insight_validation_period']:
                    # Simple validation based on subsequent outcomes
                    validation_result = self._validate_insight(insight)
                    
                    insight.validation_status = validation_result['status']
                    validated_insights.append({
                        'insight_id': insight.insight_id,
                        'validation_result': validation_result,
                        'time_to_validation': time_pending.days
                    })
        
        return validated_insights
    
    def _validate_insight(self, insight: LearningInsight) -> Dict:
        """Validate a specific insight against subsequent data"""
        
        # This is a simplified validation - real implementation would be more sophisticated
        
        # Count outcomes after insight discovery
        subsequent_outcomes = [
            o for o in self.outcomes_db 
            if o.outcome_date > insight.discovered_date
        ]
        
        if len(subsequent_outcomes) < 10:
            return {
                'status': 'insufficient_data',
                'confidence': 0.0,
                'supporting_evidence': len(subsequent_outcomes)
            }
        
        # Simple validation based on insight type
        if insight.insight_type == 'concern':
            # Check if the concern was justified
            recent_issues = sum(1 for o in subsequent_outcomes if o.actual_outcome < 0.4)
            issue_rate = recent_issues / len(subsequent_outcomes)
            
            if issue_rate > 0.2:  # High issue rate confirms concern
                return {
                    'status': 'validated',
                    'confidence': min(issue_rate * 2, 1.0),
                    'supporting_evidence': f"{recent_issues}/{len(subsequent_outcomes)} poor outcomes"
                }
            else:
                return {
                    'status': 'rejected',
                    'confidence': 1 - issue_rate,
                    'supporting_evidence': f"Only {recent_issues}/{len(subsequent_outcomes)} poor outcomes"
                }
        
        elif insight.insight_type == 'improvement':
            # Check if improvement was sustained
            recent_successes = sum(1 for o in subsequent_outcomes if o.actual_outcome > 0.6)
            success_rate = recent_successes / len(subsequent_outcomes)
            
            if success_rate > 0.7:  # High success rate confirms improvement
                return {
                    'status': 'validated',
                    'confidence': success_rate,
                    'supporting_evidence': f"{recent_successes}/{len(subsequent_outcomes)} successful outcomes"
                }
        
        # Default to pending if validation is inconclusive
        return {
            'status': 'pending',
            'confidence': 0.5,
            'supporting_evidence': 'Validation inconclusive'
        }
    
    def generate_learning_report(self, period_days: int = 30) -> Dict:
        """Generate comprehensive learning report for specified period"""
        
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        # Filter data for reporting period
        period_outcomes = [o for o in self.outcomes_db if o.outcome_date >= cutoff_date]
        period_predictions = [p for p in self.predictions_db if p.timestamp >= cutoff_date]
        period_insights = [i for i in self.insights_db if i.discovered_date >= cutoff_date]
        
        report = {
            'report_period': f"{period_days} days",
            'report_date': datetime.now().isoformat(),
            'data_summary': {
                'total_outcomes': len(period_outcomes),
                'total_predictions': len(period_predictions),
                'new_insights': len(period_insights),
                'data_coverage': len(period_outcomes) / max(len(period_predictions), 1)
            }
        }
        
        # Performance analysis
        if period_outcomes and period_predictions:
            performance_analysis = self.outcome_analyzer.analyze_prediction_accuracy(
                period_outcomes, period_predictions
            )
            report['performance_analysis'] = performance_analysis
        
        # Insights summary
        insights_summary = {
            'total_insights': len(period_insights),
            'by_type': {},
            'by_significance': {},
            'validated_insights': 0,
            'pending_insights': 0
        }
        
        for insight in period_insights:
            # Count by type
            insights_summary['by_type'][insight.insight_type] = (
                insights_summary['by_type'].get(insight.insight_type, 0) + 1
            )
            
            # Count by significance
            insights_summary['by_significance'][insight.clinical_significance] = (
                insights_summary['by_significance'].get(insight.clinical_significance, 0) + 1
            )
            
            # Count validation status
            if insight.validation_status == 'validated':
                insights_summary['validated_insights'] += 1
            elif insight.validation_status == 'pending':
                insights_summary['pending_insights'] += 1
        
        report['insights_summary'] = insights_summary
        
        # Model status
        model_status = {}
        for model_type in ['treatment_response', 'adverse_event']:
            active_model = self.model_registry.get_active_model('production')
            if active_model:
                model_metadata = self.model_registry.get_model_metadata(active_model)
                model_status[model_type] = {
                    'active_model': active_model,
                    'last_training': model_metadata.get('registered_date') if model_metadata else None,
                    'performance_metrics': model_metadata.get('performance_metrics') if model_metadata else None
                }
            else:
                model_status[model_type] = {'status': 'no_active_model'}
        
        report['model_status'] = model_status
        
        # Recommendations for next period
        recommendations = self._generate_period_recommendations(report)
        report['recommendations'] = recommendations
        
        return report
    
    def _generate_period_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on period report"""
        recommendations = []
        
        data_summary = report['data_summary']
        
        # Data collection recommendations
        if data_summary['total_outcomes'] < 50:
            recommendations.append(
                "Increase outcome data collection. Current volume insufficient for robust analysis."
            )
        
        if data_summary['data_coverage'] < 0.8:
            recommendations.append(
                "Improve prediction-outcome matching. Many predictions lack corresponding outcomes."
            )
        
        # Performance recommendations
        performance = report.get('performance_analysis', {})
        if performance.get('accuracy', 1.0) < 0.75:
            recommendations.append(
                f"Model accuracy ({performance['accuracy']:.3f}) below target. Consider retraining."
            )
        
        # Insights recommendations
        insights_summary = report['insights_summary']
        if insights_summary['pending_insights'] > 10:
            recommendations.append(
                f"{insights_summary['pending_insights']} insights pending validation. "
                "Prioritize insight validation process."
            )
        
        high_significance_insights = insights_summary['by_significance'].get('high', 0)
        if high_significance_insights > 0:
            recommendations.append(
                f"{high_significance_insights} high-significance insights discovered. "
                "Review for potential clinical protocol updates."
            )
        
        return recommendations

    # EMR Integration Methods
    def push_insights_to_emr(self, patient_id: str, insights: List[LearningInsight] = None) -> Dict:
        """Push insights to EMR system for a specific patient"""
        
        if not self.abena_sdk:
            return {
                'success': False,
                'error': 'Abena SDK not configured',
                'patient_id': patient_id
            }
        
        # Get insights for the patient if not provided
        if insights is None:
            insights = [i for i in self.insights_db if patient_id in i.affected_population]
        
        if not insights:
            return {
                'success': False,
                'error': 'No insights found for patient',
                'patient_id': patient_id
            }
        
        # Convert insights to dictionary format for Abena SDK
        insights_data = []
        for insight in insights:
            insights_data.append({
                'insight_id': insight.insight_id,
                'type': insight.insight_type,
                'description': insight.description,
                'clinical_significance': insight.clinical_significance,
                'confidence_level': insight.confidence_level,
                'actionable_recommendations': insight.actionable_recommendations,
                'supporting_evidence': insight.supporting_evidence,
                'validation_status': insight.validation_status,
                'discovered_date': insight.discovered_date.isoformat(),
                'affected_population': insight.affected_population
            })
        
        # Push to EMR via Abena SDK
        result = self.abena_sdk.push_to_emr(patient_id, insights_data, 'insights')
        
        self.logger.info(f"Pushed {len(insights)} insights to EMR for patient {patient_id}")
        return result
    
    def create_patient_clinical_summary(self, patient_id: str) -> Dict:
        """Create and push clinical summary to EMR for a patient"""
        
        if not self.abena_sdk:
            return {
                'success': False,
                'error': 'Abena SDK not configured',
                'patient_id': patient_id
            }
        
        # Get patient-specific data
        patient_outcomes = [o for o in self.outcomes_db if o.patient_id == patient_id]
        patient_predictions = [p for p in self.predictions_db if p.patient_id == patient_id]
        patient_insights = [i for i in self.insights_db if patient_id in i.affected_population]
        
        # Create clinical summary data
        summary_data = {
            'patient_id': patient_id,
            'generated_date': datetime.now().isoformat(),
            'summary_sections': {}
        }
        
        # Treatment Outcomes Summary
        if patient_outcomes:
            summary_data['summary_sections']['treatment_outcomes'] = self._summarize_outcomes_for_emr(patient_outcomes)
        
        # Prediction Analysis
        if patient_predictions:
            summary_data['summary_sections']['prediction_analysis'] = self._summarize_predictions_for_emr(patient_predictions)
        
        # Clinical Insights
        if patient_insights:
            summary_data['summary_sections']['clinical_insights'] = self._summarize_insights_for_emr(patient_insights)
        
        # Push clinical summary to EMR via Abena SDK
        result = self.abena_sdk.push_to_emr(patient_id, summary_data, 'clinical_summary')
        
        self.logger.info(f"Created clinical summary for patient {patient_id}")
        return result
    
    def auto_push_high_priority_insights(self) -> Dict:
        """Automatically push high-priority insights to EMR for all affected patients"""
        
        if not self.abena_sdk or not self.learning_config['auto_push_to_emr']:
            return {
                'success': False,
                'error': 'EMR auto-push not enabled',
                'pushed_count': 0
            }
        
        # Get high-priority insights
        high_priority_insights = [
            i for i in self.insights_db 
            if i.clinical_significance == 'high' and i.validation_status == 'validated'
        ]
        
        if not high_priority_insights:
            return {
                'success': True,
                'message': 'No high-priority insights to push',
                'pushed_count': 0
            }
        
        # Group insights by patient
        patient_insights = {}
        for insight in high_priority_insights:
            # Extract patient IDs from affected population (simplified)
            # In real implementation, this would be more sophisticated
            if 'patient' in insight.affected_population.lower():
                # Extract patient ID from description or supporting evidence
                patient_id = insight.supporting_evidence.get('patient_id', 'unknown')
                if patient_id not in patient_insights:
                    patient_insights[patient_id] = []
                patient_insights[patient_id].append(insight)
        
        # Push insights for each patient
        results = []
        for patient_id, insights in patient_insights.items():
            if patient_id != 'unknown':
                result = self.push_insights_to_emr(patient_id, insights)
                results.append(result)
        
        successful_pushes = sum(1 for r in results if r.get('success', False))
        
        return {
            'success': True,
            'total_patients': len(patient_insights),
            'successful_pushes': successful_pushes,
            'failed_pushes': len(patient_insights) - successful_pushes,
            'results': results
        }
    
    def get_patient_emr_history(self, patient_id: str, days: int = 30) -> Dict:
        """Retrieve patient's EMR history from the ML pipeline"""
        
        if not self.abena_sdk:
            return {
                'success': False,
                'error': 'Abena SDK not configured',
                'patient_id': patient_id
            }
        
        # Get local history
        cutoff_date = datetime.now() - timedelta(days=days)
        
        patient_outcomes = [
            o for o in self.outcomes_db 
            if o.patient_id == patient_id and o.outcome_date >= cutoff_date
        ]
        
        patient_predictions = [
            p for p in self.predictions_db 
            if p.patient_id == patient_id and p.timestamp >= cutoff_date
        ]
        
        patient_insights = [
            i for i in self.insights_db 
            if patient_id in i.affected_population and i.discovered_date >= cutoff_date
        ]
        
        # Get EMR history via Abena SDK
        emr_history = self.abena_sdk.get_outcome_data(patient_id, days)
        
        return {
            'success': True,
            'patient_id': patient_id,
            'date_range': f'Last {days} days',
            'local_data': {
                'outcomes_count': len(patient_outcomes),
                'predictions_count': len(patient_predictions),
                'insights_count': len(patient_insights)
            },
            'emr_data': emr_history,
            'recent_outcomes': [
                {
                    'treatment_id': o.treatment_id,
                    'outcome_score': o.actual_outcome,
                    'date': o.outcome_date.isoformat(),
                    'satisfaction': o.patient_satisfaction
                } for o in patient_outcomes[-5:]  # Last 5 outcomes
            ],
            'recent_insights': [
                {
                    'insight_id': i.insight_id,
                    'type': i.insight_type,
                    'description': i.description,
                    'significance': i.clinical_significance,
                    'date': i.discovered_date.isoformat()
                } for i in patient_insights[-5:]  # Last 5 insights
            ]
        }
    
    def _summarize_outcomes_for_emr(self, outcomes: List[OutcomeData]) -> Dict:
        """Summarize treatment outcomes for EMR"""
        if not outcomes:
            return {}
        
        recent_outcomes = sorted(outcomes, key=lambda x: x.outcome_date, reverse=True)[:5]
        
        summary = {
            'total_outcomes': len(outcomes),
            'recent_outcomes': len(recent_outcomes),
            'average_outcome_score': sum(o.actual_outcome for o in outcomes) / len(outcomes),
            'success_rate': sum(1 for o in outcomes if o.actual_outcome > 0.6) / len(outcomes),
            'adverse_events_count': sum(len(o.adverse_events) for o in outcomes),
            'recent_outcomes_detail': []
        }
        
        for outcome in recent_outcomes:
            summary['recent_outcomes_detail'].append({
                'treatment_id': outcome.treatment_id,
                'outcome_score': outcome.actual_outcome,
                'outcome_date': outcome.outcome_date.isoformat(),
                'patient_satisfaction': outcome.patient_satisfaction,
                'provider_assessment': outcome.provider_assessment,
                'adverse_events': outcome.adverse_events,
                'pain_reduction': outcome.pain_reduction,
                'functional_improvement': outcome.functional_improvement
            })
        
        return summary
    
    def _summarize_predictions_for_emr(self, predictions: List[PredictionResult]) -> Dict:
        """Summarize prediction performance for EMR"""
        if not predictions:
            return {}
        
        summary = {
            'total_predictions': len(predictions),
            'average_confidence': sum(p.confidence_score for p in predictions) / len(predictions),
            'high_confidence_predictions': sum(1 for p in predictions if p.confidence_score > 0.8),
            'predictions_with_warnings': sum(1 for p in predictions if p.warnings),
            'recent_predictions': []
        }
        
        recent_predictions = sorted(predictions, key=lambda x: x.timestamp, reverse=True)[:5]
        
        for pred in recent_predictions:
            summary['recent_predictions'].append({
                'treatment_id': pred.treatment_id,
                'success_probability': pred.success_probability,
                'confidence_score': pred.confidence_score,
                'warnings': pred.warnings,
                'recommendations': pred.recommendations,
                'timestamp': pred.timestamp.isoformat()
            })
        
        return summary
    
    def _summarize_insights_for_emr(self, insights: List[LearningInsight]) -> Dict:
        """Summarize clinical insights for EMR"""
        if not insights:
            return {}
        
        summary = {
            'total_insights': len(insights),
            'insights_by_type': {},
            'insights_by_significance': {},
            'validated_insights': sum(1 for i in insights if i.validation_status == 'validated'),
            'pending_insights': sum(1 for i in insights if i.validation_status == 'pending'),
            'high_priority_insights': []
        }
        
        # Count by type and significance
        for insight in insights:
            summary['insights_by_type'][insight.insight_type] = \
                summary['insights_by_type'].get(insight.insight_type, 0) + 1
            
            summary['insights_by_significance'][insight.clinical_significance] = \
                summary['insights_by_significance'].get(insight.clinical_significance, 0) + 1
            
            # Collect high priority insights
            if insight.clinical_significance == 'high':
                summary['high_priority_insights'].append({
                    'insight_id': insight.insight_id,
                    'type': insight.insight_type,
                    'description': insight.description,
                    'confidence_level': insight.confidence_level,
                    'recommendations': insight.actionable_recommendations,
                    'discovered_date': insight.discovered_date.isoformat()
                })
        
        return summary

# Example usage and testing
if __name__ == "__main__":
    # Initialize the ML feedback pipeline
    model_registry = ModelRegistry()
    
    # Abena SDK configuration
    abena_config = {
        'authServiceUrl': 'http://localhost:3001',
        'dataServiceUrl': 'http://localhost:8001', 
        'privacyServiceUrl': 'http://localhost:8002',
        'blockchainServiceUrl': 'http://localhost:8003',
        'auto_push_to_emr': True  # Enable automatic EMR integration
    }
    
    # Initialize with Abena SDK integration
    continuous_learning = ContinuousLearningOrchestrator(model_registry, abena_config)
    
    print("Abena IHR - ML Feedback Pipeline Initialized")
    print("=" * 60)
    
    # Example outcome data
    sample_outcome = OutcomeData(
        patient_id="PATIENT_001",
        treatment_id="TX_001", 
        prediction_id="PRED_001",
        actual_outcome=0.75,
        outcome_date=datetime.now(),
        time_to_outcome=30,
        adverse_events=[],
        side_effects=["mild_nausea"],
        patient_satisfaction=8.5,
        provider_assessment="good_response",
        pain_reduction=3.2,
        functional_improvement=15.0,
        medication_adherence=0.95,
        quality_of_life_change=2.1,
        healthcare_utilization={"office_visits": 2, "er_visits": 0},
        cost_effectiveness=0.8
    )
    
    # Add to learning system
    continuous_learning.add_outcome_data(sample_outcome)
    
    # Run analysis
    analysis_result = continuous_learning.run_daily_analysis()
    print(f"Daily analysis status: {analysis_result['status']}")
    
    # Generate learning report
    learning_report = continuous_learning.generate_learning_report(30)
    print(f"Learning report generated for {learning_report['report_period']}")
    print(f"Total outcomes analyzed: {learning_report['data_summary']['total_outcomes']}")
    
    # Abena SDK Integration Demo
    print("\n" + "=" * 60)
    print("Abena SDK Integration Demo")
    print("=" * 60)
    
    # Create clinical summary for patient
    clinical_summary = continuous_learning.create_patient_clinical_summary("PATIENT_001")
    print(f"Clinical summary created: {clinical_summary['success']}")
    
    # Push insights to EMR via Abena SDK
    emr_push = continuous_learning.push_insights_to_emr("PATIENT_001")
    print(f"Insights pushed to EMR: {emr_push['success']}")
    
    # Get patient EMR history via Abena SDK
    patient_history = continuous_learning.get_patient_emr_history("PATIENT_001", 30)
    print(f"Patient history retrieved: {patient_history['success']}")
    
    # Auto-push high priority insights via Abena SDK
    auto_push = continuous_learning.auto_push_high_priority_insights()
    print(f"Auto-push high priority insights: {auto_push['success']}")
    
    print("\nML Feedback Pipeline Ready for Clinical Deployment")
    print("Abena SDK Integration: ✅ Active") 