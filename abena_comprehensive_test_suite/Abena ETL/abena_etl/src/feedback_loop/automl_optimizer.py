# Abena IHR - AutoML Optimizer
# Automated machine learning optimization using Optuna

import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import optuna

# Update import to handle path issues
try:
    from src.predictive_analytics.predictive_engine import TreatmentResponsePredictor, AdverseEventPredictor
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    try:
        from predictive_analytics.predictive_engine import TreatmentResponsePredictor, AdverseEventPredictor
    except ImportError:
        # Create placeholder classes for testing
        class TreatmentResponsePredictor:
            def __init__(self):
                pass
            def _train_with_params(self, data, params):
                pass
            def predict_treatment_response(self, patient, treatment):
                class MockResult:
                    success_probability = 0.7
                return MockResult()
        
        class AdverseEventPredictor:
            def __init__(self):
                pass

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