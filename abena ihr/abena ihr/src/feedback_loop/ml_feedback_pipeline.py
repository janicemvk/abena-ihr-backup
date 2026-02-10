"""
ML Feedback Pipeline

This module provides machine learning feedback mechanisms and
continuous model improvement capabilities for the Abena IHR system.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import asyncio
from dataclasses import dataclass, field
from enum import Enum

from ..core.data_models import Prediction, SystemEvent
from ..core.utils import generate_uuid, safe_json_dumps
from ..predictive_analytics.predictive_engine import get_predictive_engine

# Configure logging
logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Enumeration of feedback types."""
    PREDICTION_ACCURACY = "prediction_accuracy"
    MODEL_PERFORMANCE = "model_performance"
    FEATURE_IMPORTANCE = "feature_importance"
    DATA_QUALITY = "data_quality"
    USER_FEEDBACK = "user_feedback"
    CLINICAL_OUTCOME = "clinical_outcome"


class FeedbackStatus(Enum):
    """Enumeration of feedback statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    APPLIED = "applied"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ModelFeedback:
    """Feedback data for model improvement."""
    id: str = field(default_factory=generate_uuid)
    model_name: str = ""
    feedback_type: FeedbackType = FeedbackType.PREDICTION_ACCURACY
    prediction_id: Optional[str] = None
    patient_id: Optional[str] = None
    actual_outcome: Optional[Any] = None
    predicted_outcome: Optional[Any] = None
    feedback_data: Dict[str, Any] = field(default_factory=dict)
    confidence_score: Optional[float] = None
    user_id: Optional[str] = None
    status: FeedbackStatus = FeedbackStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now


@dataclass
class ModelPerformance:
    """Model performance metrics."""
    model_name: str = ""
    version: str = ""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    auc_score: float = 0.0
    total_predictions: int = 0
    correct_predictions: int = 0
    feedback_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now


class MLFeedbackPipeline:
    """Main ML feedback pipeline for continuous model improvement."""
    
    def __init__(self):
        self.feedback_queue: List[ModelFeedback] = []
        self.processed_feedback: Dict[str, ModelFeedback] = {}
        self.model_performance: Dict[str, ModelPerformance] = {}
        self.feedback_handlers: Dict[FeedbackType, List[callable]] = {}
        self.performance_thresholds: Dict[str, float] = {
            'accuracy': 0.8,
            'precision': 0.75,
            'recall': 0.75,
            'f1_score': 0.75
        }
        self.prediction_engine = get_predictive_engine()
        self._load_existing_performance()
    
    def _load_existing_performance(self):
        """Load existing model performance data."""
        try:
            # In a real app, this would load from database
            # For now, initialize with default values
            pass
        except Exception as e:
            logger.error(f"Error loading existing performance data: {e}")
    
    def submit_feedback(
        self,
        model_name: str,
        feedback_type: FeedbackType,
        feedback_data: Dict[str, Any],
        prediction_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Submit feedback for model improvement.
        
        Args:
            model_name: Name of the model
            feedback_type: Type of feedback
            feedback_data: Feedback data
            prediction_id: Optional prediction ID
            patient_id: Optional patient ID
            user_id: Optional user ID
            
        Returns:
            Feedback ID
        """
        try:
            feedback = ModelFeedback(
                model_name=model_name,
                feedback_type=feedback_type,
                prediction_id=prediction_id,
                patient_id=patient_id,
                user_id=user_id,
                feedback_data=feedback_data
            )
            
            # Extract actual and predicted outcomes if available
            if 'actual_outcome' in feedback_data:
                feedback.actual_outcome = feedback_data['actual_outcome']
            if 'predicted_outcome' in feedback_data:
                feedback.predicted_outcome = feedback_data['predicted_outcome']
            if 'confidence_score' in feedback_data:
                feedback.confidence_score = feedback_data['confidence_score']
            
            # Add to queue
            self.feedback_queue.append(feedback)
            
            # Trigger processing
            asyncio.create_task(self._process_feedback_queue())
            
            logger.info(f"Submitted feedback: {feedback.id} for model {model_name}")
            return feedback.id
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return ""
    
    async def _process_feedback_queue(self):
        """Process feedback queue asynchronously."""
        try:
            while self.feedback_queue:
                feedback = self.feedback_queue.pop(0)
                await self._process_feedback(feedback)
        except Exception as e:
            logger.error(f"Error processing feedback queue: {e}")
    
    async def _process_feedback(self, feedback: ModelFeedback):
        """Process individual feedback."""
        try:
            feedback.status = FeedbackStatus.PROCESSING
            feedback.processed_at = datetime.now()
            
            # Call registered handlers for this feedback type
            if feedback.feedback_type in self.feedback_handlers:
                for handler in self.feedback_handlers[feedback.feedback_type]:
                    try:
                        await handler(feedback)
                    except Exception as e:
                        logger.error(f"Error in feedback handler: {e}")
            
            # Update model performance
            await self._update_model_performance(feedback)
            
            # Check if model needs retraining
            await self._check_model_retraining(feedback.model_name)
            
            feedback.status = FeedbackStatus.APPLIED
            feedback.applied_at = datetime.now()
            
            # Store processed feedback
            self.processed_feedback[feedback.id] = feedback
            
            logger.info(f"Processed feedback: {feedback.id}")
            
        except Exception as e:
            logger.error(f"Error processing feedback {feedback.id}: {e}")
            feedback.status = FeedbackStatus.REJECTED
    
    async def _update_model_performance(self, feedback: ModelFeedback):
        """Update model performance metrics based on feedback."""
        try:
            model_name = feedback.model_name
            
            if model_name not in self.model_performance:
                self.model_performance[model_name] = ModelPerformance(
                    model_name=model_name,
                    version="1.0.0"
                )
            
            performance = self.model_performance[model_name]
            performance.feedback_count += 1
            performance.last_updated = datetime.now()
            
            # Update accuracy if actual and predicted outcomes are available
            if (feedback.actual_outcome is not None and 
                feedback.predicted_outcome is not None):
                
                performance.total_predictions += 1
                
                # Simple accuracy calculation
                if feedback.actual_outcome == feedback.predicted_outcome:
                    performance.correct_predictions += 1
                
                performance.accuracy = (
                    performance.correct_predictions / performance.total_predictions
                )
            
            # Update other metrics based on feedback type
            if feedback.feedback_type == FeedbackType.MODEL_PERFORMANCE:
                if 'precision' in feedback.feedback_data:
                    performance.precision = feedback.feedback_data['precision']
                if 'recall' in feedback.feedback_data:
                    performance.recall = feedback.feedback_data['recall']
                if 'f1_score' in feedback.feedback_data:
                    performance.f1_score = feedback.feedback_data['f1_score']
                if 'auc_score' in feedback.feedback_data:
                    performance.auc_score = feedback.feedback_data['auc_score']
            
            logger.info(f"Updated performance for model {model_name}")
            
        except Exception as e:
            logger.error(f"Error updating model performance: {e}")
    
    async def _check_model_retraining(self, model_name: str):
        """Check if model needs retraining based on performance."""
        try:
            if model_name not in self.model_performance:
                return
            
            performance = self.model_performance[model_name]
            
            # Check if performance is below thresholds
            needs_retraining = False
            reasons = []
            
            if performance.accuracy < self.performance_thresholds['accuracy']:
                needs_retraining = True
                reasons.append(f"Accuracy {performance.accuracy:.3f} below threshold {self.performance_thresholds['accuracy']}")
            
            if performance.f1_score < self.performance_thresholds['f1_score']:
                needs_retraining = True
                reasons.append(f"F1-score {performance.f1_score:.3f} below threshold {self.performance_thresholds['f1_score']}")
            
            if needs_retraining:
                logger.warning(f"Model {model_name} needs retraining: {', '.join(reasons)}")
                
                # Trigger retraining event
                await self._trigger_retraining_event(model_name, reasons)
            
        except Exception as e:
            logger.error(f"Error checking model retraining: {e}")
    
    async def _trigger_retraining_event(self, model_name: str, reasons: List[str]):
        """Trigger model retraining event."""
        try:
            # In a real app, this would trigger a retraining pipeline
            # For now, just log the event
            event_data = {
                'model_name': model_name,
                'reasons': reasons,
                'timestamp': datetime.now().isoformat(),
                'performance': self.model_performance[model_name].__dict__
            }
            
            logger.info(f"Retraining event triggered for {model_name}: {event_data}")
            
            # Create system event
            event = SystemEvent(
                event_type="model_retraining_required",
                event_data=event_data,
                severity="warning"
            )
            
            # In a real app, this would be stored in the database
            
        except Exception as e:
            logger.error(f"Error triggering retraining event: {e}")
    
    def register_feedback_handler(self, feedback_type: FeedbackType, handler: callable):
        """Register a feedback handler function."""
        if feedback_type not in self.feedback_handlers:
            self.feedback_handlers[feedback_type] = []
        self.feedback_handlers[feedback_type].append(handler)
        logger.info(f"Registered feedback handler for {feedback_type.value}")
    
    def get_model_performance(self, model_name: str) -> Optional[ModelPerformance]:
        """Get performance metrics for a model."""
        return self.model_performance.get(model_name)
    
    def get_all_model_performance(self) -> Dict[str, ModelPerformance]:
        """Get performance metrics for all models."""
        return self.model_performance.copy()
    
    def get_feedback_history(
        self,
        model_name: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None,
        status: Optional[FeedbackStatus] = None,
        limit: int = 100
    ) -> List[ModelFeedback]:
        """Get feedback history with optional filtering."""
        feedback_list = list(self.processed_feedback.values())
        
        # Apply filters
        if model_name:
            feedback_list = [f for f in feedback_list if f.model_name == model_name]
        if feedback_type:
            feedback_list = [f for f in feedback_list if f.feedback_type == feedback_type]
        if status:
            feedback_list = [f for f in feedback_list if f.status == status]
        
        # Sort by creation date (newest first)
        feedback_list.sort(key=lambda x: x.created_at, reverse=True)
        
        return feedback_list[:limit]
    
    def submit_prediction_feedback(
        self,
        prediction_id: str,
        actual_outcome: Any,
        confidence_rating: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Submit feedback for a specific prediction.
        
        Args:
            prediction_id: ID of the prediction
            actual_outcome: Actual outcome that occurred
            confidence_rating: User's confidence rating (1-5)
            user_id: Optional user ID
            
        Returns:
            Feedback ID
        """
        try:
            # In a real app, you would fetch the prediction from database
            # For now, create a mock prediction
            feedback_data = {
                'actual_outcome': actual_outcome,
                'confidence_rating': confidence_rating,
                'prediction_id': prediction_id
            }
            
            return self.submit_feedback(
                model_name="default_model",  # In real app, get from prediction
                feedback_type=FeedbackType.PREDICTION_ACCURACY,
                feedback_data=feedback_data,
                prediction_id=prediction_id,
                user_id=user_id
            )
            
        except Exception as e:
            logger.error(f"Error submitting prediction feedback: {e}")
            return ""
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        try:
            total_feedback = len(self.processed_feedback)
            pending_feedback = len([f for f in self.feedback_queue if f.status == FeedbackStatus.PENDING])
            
            feedback_by_type = {}
            for feedback in self.processed_feedback.values():
                feedback_type = feedback.feedback_type.value
                feedback_by_type[feedback_type] = feedback_by_type.get(feedback_type, 0) + 1
            
            feedback_by_status = {}
            for feedback in self.processed_feedback.values():
                status = feedback.status.value
                feedback_by_status[status] = feedback_by_status.get(status, 0) + 1
            
            return {
                'total_feedback': total_feedback,
                'pending_feedback': pending_feedback,
                'feedback_by_type': feedback_by_type,
                'feedback_by_status': feedback_by_status,
                'models_with_feedback': len(self.model_performance),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback statistics: {e}")
            return {}


# Global ML feedback pipeline instance
ml_feedback_pipeline = MLFeedbackPipeline()


def get_ml_feedback_pipeline() -> MLFeedbackPipeline:
    """Get the global ML feedback pipeline instance."""
    return ml_feedback_pipeline 