"""
Abena SDK Analytics

Centralized analytics and prediction engine for the Abena SDK.
All modules should use this for analytics operations instead of implementing their own.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import requests

from .exceptions import AnalyticsError, ValidationError
from .config import AbenaConfig


@dataclass
class PredictionRequest:
    """Prediction request with context"""
    patient_id: str
    model_type: str
    input_data: Dict[str, Any]
    user_id: str
    purpose: str
    confidence_threshold: Optional[float] = None


@dataclass
class PredictionResponse:
    """Prediction response with metadata"""
    prediction: Any
    confidence: float
    model_version: str
    timestamp: datetime
    features_used: List[str]
    explanation: Optional[Dict[str, Any]] = None


@dataclass
class AnalyticsInsight:
    """Analytics insight with metadata"""
    insight_type: str
    value: Any
    confidence: float
    timestamp: datetime
    description: str
    recommendations: Optional[List[str]] = None


class AnalyticsEngine:
    """Centralized analytics engine for Abena SDK"""
    
    def __init__(self, config: AbenaConfig):
        self.config = config
        self._analytics_service_url = config.get_api_url("analytics")
        self._prediction_cache: Dict[str, Any] = {}
    
    def get_prediction(self, request: PredictionRequest) -> PredictionResponse:
        """Get prediction from analytics engine"""
        try:
            # Check cache first
            cache_key = self._get_prediction_cache_key(request)
            if cache_key in self._prediction_cache:
                cached_result = self._prediction_cache[cache_key]
                if not self._is_cache_expired(cached_result):
                    return cached_result["response"]
            
            # Make prediction request
            response = requests.post(
                f"{self._analytics_service_url}/predict",
                json={
                    "patient_id": request.patient_id,
                    "model_type": request.model_type,
                    "input_data": request.input_data,
                    "user_id": request.user_id,
                    "purpose": request.purpose,
                    "confidence_threshold": request.confidence_threshold or self.config.prediction_confidence_threshold
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result_data = response.json()
            
            # Create prediction response
            prediction_response = PredictionResponse(
                prediction=result_data["prediction"],
                confidence=result_data["confidence"],
                model_version=result_data["model_version"],
                timestamp=datetime.fromisoformat(result_data["timestamp"]),
                features_used=result_data.get("features_used", []),
                explanation=result_data.get("explanation")
            )
            
            # Cache result
            self._prediction_cache[cache_key] = {
                "response": prediction_response,
                "timestamp": datetime.now()
            }
            
            return prediction_response
            
        except requests.RequestException as e:
            raise AnalyticsError(f"Prediction failed: {str(e)}")
    
    def get_treatment_recommendations(self, patient_id: str, 
                                    condition: str, user_id: str) -> List[Dict[str, Any]]:
        """Get treatment recommendations for patient"""
        try:
            response = requests.post(
                f"{self._analytics_service_url}/recommendations/treatment",
                json={
                    "patient_id": patient_id,
                    "condition": condition,
                    "user_id": user_id
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()["recommendations"]
            
        except requests.RequestException as e:
            raise AnalyticsError(f"Failed to get treatment recommendations: {str(e)}")
    
    def get_risk_assessment(self, patient_id: str, risk_factors: List[str], 
                           user_id: str) -> Dict[str, Any]:
        """Get risk assessment for patient"""
        try:
            response = requests.post(
                f"{self._analytics_service_url}/risk-assessment",
                json={
                    "patient_id": patient_id,
                    "risk_factors": risk_factors,
                    "user_id": user_id
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            raise AnalyticsError(f"Risk assessment failed: {str(e)}")
    
    def get_patient_insights(self, patient_id: str, user_id: str, 
                           insight_types: Optional[List[str]] = None) -> List[AnalyticsInsight]:
        """Get insights for patient"""
        try:
            response = requests.post(
                f"{self._analytics_service_url}/insights",
                json={
                    "patient_id": patient_id,
                    "user_id": user_id,
                    "insight_types": insight_types or ["trends", "anomalies", "correlations"]
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            insights_data = response.json()["insights"]
            insights = []
            
            for insight_data in insights_data:
                insight = AnalyticsInsight(
                    insight_type=insight_data["type"],
                    value=insight_data["value"],
                    confidence=insight_data["confidence"],
                    timestamp=datetime.fromisoformat(insight_data["timestamp"]),
                    description=insight_data["description"],
                    recommendations=insight_data.get("recommendations")
                )
                insights.append(insight)
            
            return insights
            
        except requests.RequestException as e:
            raise AnalyticsError(f"Failed to get patient insights: {str(e)}")
    
    def train_model(self, model_type: str, training_data: Dict[str, Any], 
                   user_id: str) -> Dict[str, Any]:
        """Train or retrain a model"""
        try:
            response = requests.post(
                f"{self._analytics_service_url}/models/train",
                json={
                    "model_type": model_type,
                    "training_data": training_data,
                    "user_id": user_id
                },
                timeout=self.config.timeout * 2  # Training takes longer
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            raise AnalyticsError(f"Model training failed: {str(e)}")
    
    def evaluate_model(self, model_type: str, test_data: Dict[str, Any], 
                      user_id: str) -> Dict[str, Any]:
        """Evaluate model performance"""
        try:
            response = requests.post(
                f"{self._analytics_service_url}/models/evaluate",
                json={
                    "model_type": model_type,
                    "test_data": test_data,
                    "user_id": user_id
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            raise AnalyticsError(f"Model evaluation failed: {str(e)}")
    
    def get_model_metadata(self, model_type: str) -> Dict[str, Any]:
        """Get model metadata and performance metrics"""
        try:
            response = requests.get(
                f"{self._analytics_service_url}/models/{model_type}/metadata",
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            raise AnalyticsError(f"Failed to get model metadata: {str(e)}")
    
    def _get_prediction_cache_key(self, request: PredictionRequest) -> str:
        """Generate cache key for prediction request"""
        return f"{request.patient_id}:{request.model_type}:{hash(json.dumps(request.input_data, sort_keys=True))}"
    
    def _is_cache_expired(self, cached_result: Dict[str, Any]) -> bool:
        """Check if cached result is expired"""
        cache_age = (datetime.now() - cached_result["timestamp"]).total_seconds()
        return cache_age > self.config.cache_ttl
    
    def clear_cache(self):
        """Clear prediction cache"""
        self._prediction_cache.clear() 