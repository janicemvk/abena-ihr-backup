# Abena IHR - Model Retraining Pipeline
# Pipeline for automated model retraining based on new data

import numpy as np
import logging
import joblib
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, mean_absolute_error
)

from ml_data_models import OutcomeData
from model_registry import ModelRegistry
from outcome_analyzer import OutcomeAnalyzer
from automl_optimizer import AutoMLOptimizer

# Update imports to handle path issues
try:
    from src.core.data_models import PredictionResult, PatientProfile, TreatmentPlan
    from src.predictive_analytics.predictive_engine import TreatmentResponsePredictor, AdverseEventPredictor
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    try:
        from core.data_models import PredictionResult, PatientProfile, TreatmentPlan
        from predictive_analytics.predictive_engine import TreatmentResponsePredictor, AdverseEventPredictor
    except ImportError:
        # Create placeholder classes for testing
        from dataclasses import dataclass
        from datetime import datetime
        from typing import List, Dict, Any
        
        @dataclass
        class PredictionResult:
            patient_id: str
            treatment_id: str
            success_probability: float
            warnings: List[str]
            timestamp: datetime
        
        @dataclass 
        class PatientProfile:
            patient_id: str
            age: int
            gender: str
            genomics_data: Dict
            biomarkers: Dict
            medical_history: List
            current_medications: List
            lifestyle_metrics: Dict
            pain_scores: List
            functional_assessments: Dict
        
        @dataclass
        class TreatmentPlan:
            treatment_id: str
            treatment_type: str
            medications: List
            dosages: Dict
            duration_weeks: int
            lifestyle_interventions: List
        
        class TreatmentResponsePredictor:
            def __init__(self):
                pass
            def _train_with_params(self, data, params):
                pass
            def train_models(self, data):
                pass
            def predict_treatment_response(self, patient, treatment):
                return PredictionResult(
                    patient_id=patient.patient_id,
                    treatment_id=treatment.treatment_id,
                    success_probability=0.7,
                    warnings=[],
                    timestamp=datetime.now()
                )
        
        class AdverseEventPredictor:
            def __init__(self):
                pass
            def assess_adverse_event_risk(self, patient, treatment):
                return {"overall_risk_score": 0.3}

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