# Abena IHR - Dynamic Learning System
# Implements adaptive learning capabilities for continuous model improvement

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from pathlib import Path
import json

from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult
from src.predictive_analytics.predictive_engine import TreatmentResponsePredictor
from .feedback_pipeline import OutcomeData, LearningInsight, ModelRegistry

@dataclass
class LearningState:
    """Tracks the current state of model learning"""
    model_id: str
    last_update: datetime
    performance_metrics: Dict[str, float]
    active_features: List[str]
    learning_rate: float
    adaptation_threshold: float
    confidence_threshold: float
    sample_weights: Dict[str, float]
    feature_importance: Dict[str, float]
    population_coverage: Dict[str, float]

class DynamicLearningSystem:
    """Implements dynamic learning capabilities for continuous model improvement"""
    
    def __init__(self, model_registry: ModelRegistry):
        self.model_registry = model_registry
        self.logger = logging.getLogger(__name__)
        self.learning_states: Dict[str, LearningState] = {}
        self.adaptation_history: List[Dict] = []
        
        # Learning configuration
        self.config = {
            'min_samples_for_adaptation': 50,
            'adaptation_frequency': timedelta(days=1),
            'performance_threshold': 0.75,
            'confidence_threshold': 0.8,
            'max_adaptation_rate': 0.1,
            'feature_importance_threshold': 0.05
        }
    
    def initialize_learning_state(self, model_id: str) -> LearningState:
        """Initialize learning state for a model"""
        model_metadata = self.model_registry.get_model_metadata(model_id)
        if not model_metadata:
            raise ValueError(f"Model {model_id} not found in registry")
        
        state = LearningState(
            model_id=model_id,
            last_update=datetime.now(),
            performance_metrics=model_metadata.get('performance_metrics', {}),
            active_features=model_metadata.get('active_features', []),
            learning_rate=0.01,
            adaptation_threshold=0.05,
            confidence_threshold=0.8,
            sample_weights={},
            feature_importance=model_metadata.get('feature_importance', {}),
            population_coverage=model_metadata.get('population_coverage', {})
        )
        
        self.learning_states[model_id] = state
        return state
    
    def process_new_outcome(self, outcome: OutcomeData, 
                          prediction: PredictionResult) -> Dict:
        """Process new outcome data and update learning state"""
        
        model_id = prediction.model_id
        if model_id not in self.learning_states:
            self.initialize_learning_state(model_id)
        
        state = self.learning_states[model_id]
        
        # Calculate prediction error
        error = abs(prediction.success_probability - outcome.actual_outcome)
        
        # Update sample weights based on error
        sample_key = f"{outcome.patient_id}_{outcome.treatment_id}"
        state.sample_weights[sample_key] = min(1.0, error * 2)
        
        # Check if adaptation is needed
        adaptation_needed = self._check_adaptation_needed(state, outcome, prediction)
        
        if adaptation_needed:
            adaptation_result = self._perform_adaptation(state, outcome, prediction)
            self.adaptation_history.append(adaptation_result)
            
            return {
                'adapted': True,
                'adaptation_result': adaptation_result,
                'new_learning_rate': state.learning_rate,
                'performance_impact': adaptation_result['performance_impact']
            }
        
        return {
            'adapted': False,
            'current_learning_rate': state.learning_rate,
            'error': error
        }
    
    def _check_adaptation_needed(self, state: LearningState, 
                               outcome: OutcomeData,
                               prediction: PredictionResult) -> bool:
        """Determine if model adaptation is needed"""
        
        # Check time since last update
        time_since_update = datetime.now() - state.last_update
        if time_since_update < self.config['adaptation_frequency']:
            return False
        
        # Check prediction error
        error = abs(prediction.success_probability - outcome.actual_outcome)
        if error > state.adaptation_threshold:
            return True
        
        # Check confidence
        if prediction.confidence < state.confidence_threshold:
            return True
        
        # Check performance metrics
        if state.performance_metrics.get('accuracy', 1.0) < self.config['performance_threshold']:
            return True
        
        return False
    
    def _perform_adaptation(self, state: LearningState,
                          outcome: OutcomeData,
                          prediction: PredictionResult) -> Dict:
        """Perform model adaptation based on new data"""
        
        # Calculate adaptation metrics
        error = abs(prediction.success_probability - outcome.actual_outcome)
        adaptation_rate = min(self.config['max_adaptation_rate'], 
                            error * state.learning_rate)
        
        # Update learning rate
        state.learning_rate = max(0.001, state.learning_rate * (1 - adaptation_rate))
        
        # Update feature importance
        self._update_feature_importance(state, outcome, prediction)
        
        # Update population coverage
        self._update_population_coverage(state, outcome)
        
        # Record adaptation
        adaptation_result = {
            'timestamp': datetime.now().isoformat(),
            'model_id': state.model_id,
            'adaptation_rate': adaptation_rate,
            'new_learning_rate': state.learning_rate,
            'error': error,
            'performance_impact': self._estimate_performance_impact(state)
        }
        
        state.last_update = datetime.now()
        return adaptation_result
    
    def _update_feature_importance(self, state: LearningState,
                                 outcome: OutcomeData,
                                 prediction: PredictionResult):
        """Update feature importance based on new outcome"""
        
        # This is a simplified version - real implementation would use more sophisticated methods
        error = abs(prediction.success_probability - outcome.actual_outcome)
        
        for feature in state.active_features:
            if feature in outcome.additional_metrics:
                current_importance = state.feature_importance.get(feature, 0.0)
                feature_value = outcome.additional_metrics[feature]
                
                # Update importance based on error and feature value
                importance_change = error * abs(feature_value) * 0.1
                state.feature_importance[feature] = max(0.0, current_importance + importance_change)
    
    def _update_population_coverage(self, state: LearningState, outcome: OutcomeData):
        """Update population coverage metrics"""
        
        # Update demographic coverage
        demographics = outcome.additional_metrics.get('demographics', {})
        for key, value in demographics.items():
            if key not in state.population_coverage:
                state.population_coverage[key] = {}
            
            if value not in state.population_coverage[key]:
                state.population_coverage[key][value] = 0
            
            state.population_coverage[key][value] += 1
    
    def _estimate_performance_impact(self, state: LearningState) -> Dict:
        """Estimate the impact of adaptation on model performance"""
        
        # This is a simplified version - real implementation would use more sophisticated methods
        return {
            'estimated_accuracy_change': state.learning_rate * 0.1,
            'confidence_impact': min(1.0, state.learning_rate * 2),
            'adaptation_stability': 1.0 - state.learning_rate
        }
    
    def get_learning_insights(self) -> List[LearningInsight]:
        """Generate insights from learning process"""
        
        insights = []
        
        # Analyze adaptation history
        if len(self.adaptation_history) >= 10:
            recent_adaptations = self.adaptation_history[-10:]
            adaptation_frequency = self._calculate_adaptation_frequency(recent_adaptations)
            
            if adaptation_frequency > 0.5:  # High adaptation frequency
                insight = LearningInsight(
                    insight_id=f"high_adaptation_{datetime.now().strftime('%Y%m%d')}",
                    insight_type="concern",
                    description="High model adaptation frequency detected",
                    affected_population="All predictions",
                    confidence_level=0.8,
                    clinical_significance="moderate",
                    actionable_recommendations=[
                        "Review model stability",
                        "Consider retraining with larger dataset",
                        "Investigate data quality issues"
                    ],
                    supporting_evidence={
                        'adaptation_frequency': adaptation_frequency,
                        'adaptation_history': recent_adaptations
                    },
                    validation_status="pending",
                    discovered_date=datetime.now()
                )
                insights.append(insight)
        
        # Analyze learning rates
        for model_id, state in self.learning_states.items():
            if state.learning_rate < 0.001:
                insight = LearningInsight(
                    insight_id=f"low_learning_{model_id}_{datetime.now().strftime('%Y%m%d')}",
                    insight_type="pattern",
                    description=f"Model {model_id} showing minimal learning",
                    affected_population="All predictions",
                    confidence_level=0.7,
                    clinical_significance="moderate",
                    actionable_recommendations=[
                        "Consider increasing learning rate",
                        "Review adaptation thresholds",
                        "Check for data drift"
                    ],
                    supporting_evidence={
                        'current_learning_rate': state.learning_rate,
                        'last_update': state.last_update.isoformat()
                    },
                    validation_status="pending",
                    discovered_date=datetime.now()
                )
                insights.append(insight)
        
        return insights
    
    def _calculate_adaptation_frequency(self, adaptations: List[Dict]) -> float:
        """Calculate frequency of adaptations"""
        if not adaptations:
            return 0.0
        
        time_span = (datetime.fromisoformat(adaptations[-1]['timestamp']) - 
                    datetime.fromisoformat(adaptations[0]['timestamp']))
        
        if time_span.total_seconds() == 0:
            return 1.0
        
        return len(adaptations) / (time_span.total_seconds() / 86400)  # Adaptations per day
    
    def save_learning_state(self, model_id: str):
        """Save current learning state to file"""
        if model_id not in self.learning_states:
            return
        
        state = self.learning_states[model_id]
        state_path = Path(f"data/learning_states/{model_id}.json")
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        state_dict = {
            'model_id': state.model_id,
            'last_update': state.last_update.isoformat(),
            'performance_metrics': state.performance_metrics,
            'active_features': state.active_features,
            'learning_rate': state.learning_rate,
            'adaptation_threshold': state.adaptation_threshold,
            'confidence_threshold': state.confidence_threshold,
            'sample_weights': state.sample_weights,
            'feature_importance': state.feature_importance,
            'population_coverage': state.population_coverage
        }
        
        with open(state_path, 'w') as f:
            json.dump(state_dict, f, indent=2)
    
    def load_learning_state(self, model_id: str) -> Optional[LearningState]:
        """Load learning state from file"""
        state_path = Path(f"data/learning_states/{model_id}.json")
        
        if not state_path.exists():
            return None
        
        with open(state_path, 'r') as f:
            state_dict = json.load(f)
        
        state = LearningState(
            model_id=state_dict['model_id'],
            last_update=datetime.fromisoformat(state_dict['last_update']),
            performance_metrics=state_dict['performance_metrics'],
            active_features=state_dict['active_features'],
            learning_rate=state_dict['learning_rate'],
            adaptation_threshold=state_dict['adaptation_threshold'],
            confidence_threshold=state_dict['confidence_threshold'],
            sample_weights=state_dict['sample_weights'],
            feature_importance=state_dict['feature_importance'],
            population_coverage=state_dict['population_coverage']
        )
        
        self.learning_states[model_id] = state
        return state

# Example usage
if __name__ == "__main__":
    # Initialize model registry
    model_registry = ModelRegistry()
    
    # Initialize dynamic learning system
    dynamic_learning = DynamicLearningSystem(model_registry)
    
    print("Abena IHR - Dynamic Learning System Initialized")
    print("=" * 60)
    
    # Example outcome and prediction
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
        cost_effectiveness=0.8,
        additional_metrics={
            'demographics': {'age': 45, 'gender': 'F'},
            'treatment_type': 'standard',
            'comorbidities': ['hypertension']
        }
    )
    
    sample_prediction = PredictionResult(
        patient_id="PATIENT_001",
        treatment_id="TX_001",
        model_id="treatment_response_v1",
        success_probability=0.65,
        confidence=0.85,
        warnings=[]
    )
    
    # Process outcome
    result = dynamic_learning.process_new_outcome(sample_outcome, sample_prediction)
    print(f"Outcome processed. Adaptation needed: {result['adapted']}")
    
    # Get learning insights
    insights = dynamic_learning.get_learning_insights()
    print(f"Generated {len(insights)} learning insights")
    
    print("\nDynamic Learning System Ready for Clinical Deployment")
