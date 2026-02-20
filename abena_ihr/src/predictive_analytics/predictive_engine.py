"""
Predictive Engine

This module provides machine learning model management and prediction
capabilities for the Abena IHR Clinical Outcomes Management System.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd

from ..core.data_models import Prediction, PredictionConfidence
from ..core.utils import calculate_prediction_confidence, ensure_directory

# Configure logging
logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry for managing ML models."""
    
    def __init__(self, models_dir: str = "data/models"):
        self.models_dir = Path(models_dir)
        ensure_directory(self.models_dir)
        self.models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        self._load_models()
    
    def _load_models(self):
        """Load all models from the models directory."""
        try:
            for model_file in self.models_dir.glob("*.pkl"):
                model_name = model_file.stem
                try:
                    with open(model_file, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    
                    # Load metadata
                    metadata_file = model_file.with_suffix('.json')
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            self.model_metadata[model_name] = json.load(f)
                    else:
                        self.model_metadata[model_name] = {
                            'version': '1.0.0',
                            'created_at': datetime.now().isoformat(),
                            'features': [],
                            'target': 'unknown'
                        }
                    
                    logger.info(f"Loaded model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to load model {model_name}: {e}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def register_model(self, name: str, model: Any, metadata: Dict[str, Any]):
        """Register a new model."""
        try:
            # Save model
            model_file = self.models_dir / f"{name}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)
            
            # Save metadata
            metadata_file = self.models_dir / f"{name}.json"
            metadata['created_at'] = datetime.now().isoformat()
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update registry
            self.models[name] = model
            self.model_metadata[name] = metadata
            
            logger.info(f"Registered model: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register model {name}: {e}")
            return False
    
    def get_model(self, name: str) -> Optional[Any]:
        """Get a model by name."""
        return self.models.get(name)
    
    def get_model_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get model metadata by name."""
        return self.model_metadata.get(name)
    
    def list_models(self) -> List[str]:
        """List all available models."""
        return list(self.models.keys())
    
    def delete_model(self, name: str) -> bool:
        """Delete a model."""
        try:
            if name in self.models:
                # Remove files
                model_file = self.models_dir / f"{name}.pkl"
                metadata_file = self.models_dir / f"{name}.json"
                
                if model_file.exists():
                    model_file.unlink()
                if metadata_file.exists():
                    metadata_file.unlink()
                
                # Remove from registry
                del self.models[name]
                if name in self.model_metadata:
                    del self.model_metadata[name]
                
                logger.info(f"Deleted model: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete model {name}: {e}")
            return False


class PredictiveEngine:
    """Main predictive engine for making predictions."""
    
    def __init__(self, models_dir: str = "data/models"):
        self.model_registry = ModelRegistry(models_dir)
        self.feature_processors: Dict[str, Any] = {}
        self.prediction_cache: Dict[str, Any] = {}
    
    def make_prediction(
        self,
        model_name: str,
        features: Dict[str, Any],
        patient_id: str,
        outcome_name: str
    ) -> Optional[Prediction]:
        """
        Make a prediction using the specified model.
        
        Args:
            model_name: Name of the model to use
            features: Input features for prediction
            patient_id: ID of the patient
            outcome_name: Name of the outcome being predicted
            
        Returns:
            Prediction object or None if failed
        """
        try:
            # Get model
            model = self.model_registry.get_model(model_name)
            if not model:
                logger.error(f"Model not found: {model_name}")
                return None
            
            # Get model metadata
            metadata = self.model_registry.get_model_metadata(model_name)
            if not metadata:
                logger.error(f"Model metadata not found: {model_name}")
                return None
            
            # Process features
            processed_features = self._process_features(features, metadata.get('features', []))
            if processed_features is None:
                logger.error(f"Failed to process features for model {model_name}")
                return None
            
            # Make prediction
            prediction_value = model.predict([processed_features])[0]
            
            # Calculate confidence (simplified - in real app, use model's confidence method)
            confidence_score = self._calculate_confidence_score(model, processed_features)
            confidence = calculate_prediction_confidence(confidence_score)
            
            # Create prediction object
            prediction = Prediction(
                patient_id=patient_id,
                outcome_name=outcome_name,
                predicted_value=prediction_value,
                confidence=confidence,
                confidence_score=confidence_score,
                model_version=metadata.get('version', '1.0.0'),
                features_used=list(features.keys())
            )
            
            # Cache prediction
            cache_key = f"{patient_id}_{outcome_name}_{model_name}"
            self.prediction_cache[cache_key] = prediction
            
            logger.info(f"Made prediction for patient {patient_id}, outcome {outcome_name}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return None
    
    def _process_features(self, features: Dict[str, Any], expected_features: List[str]) -> Optional[List[Any]]:
        """Process features for model input."""
        try:
            processed = []
            for feature_name in expected_features:
                if feature_name in features:
                    processed.append(features[feature_name])
                else:
                    # Use default value for missing features
                    processed.append(0.0)
            return processed
        except Exception as e:
            logger.error(f"Error processing features: {e}")
            return None
    
    def _calculate_confidence_score(self, model: Any, features: List[Any]) -> float:
        """Calculate confidence score for prediction."""
        try:
            # This is a simplified implementation
            # In a real app, you would use the model's built-in confidence method
            # or implement a more sophisticated confidence calculation
            
            # For now, return a random confidence score between 0.5 and 1.0
            import random
            return random.uniform(0.5, 1.0)
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5
    
    def batch_predict(
        self,
        model_name: str,
        patients_data: List[Dict[str, Any]],
        outcome_name: str
    ) -> List[Prediction]:
        """
        Make predictions for multiple patients.
        
        Args:
            model_name: Name of the model to use
            patients_data: List of patient data with features
            outcome_name: Name of the outcome being predicted
            
        Returns:
            List of predictions
        """
        predictions = []
        for patient_data in patients_data:
            patient_id = patient_data.get('patient_id')
            features = {k: v for k, v in patient_data.items() if k != 'patient_id'}
            
            prediction = self.make_prediction(model_name, features, patient_id, outcome_name)
            if prediction:
                predictions.append(prediction)
        
        return predictions
    
    def get_cached_prediction(
        self,
        patient_id: str,
        outcome_name: str,
        model_name: str
    ) -> Optional[Prediction]:
        """Get cached prediction if available."""
        cache_key = f"{patient_id}_{outcome_name}_{model_name}"
        return self.prediction_cache.get(cache_key)
    
    def clear_cache(self):
        """Clear prediction cache."""
        self.prediction_cache.clear()
        logger.info("Prediction cache cleared")
    
    def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """Get performance metrics for a model."""
        try:
            metadata = self.model_registry.get_model_metadata(model_name)
            if not metadata:
                return {"error": "Model not found"}
            
            # In a real application, this would calculate actual performance metrics
            # For now, return basic metadata
            return {
                "model_name": model_name,
                "version": metadata.get("version", "1.0.0"),
                "created_at": metadata.get("created_at"),
                "features": metadata.get("features", []),
                "target": metadata.get("target", "unknown"),
                "total_predictions": len([p for p in self.prediction_cache.values() 
                                        if p.model_version == metadata.get("version", "1.0.0")])
            }
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return {"error": str(e)}

    # Intelligence Layer - AI/ML prediction logic
    def predict_treatment_response(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict treatment response for a patient.
        
        Args:
            patient_data: Patient clinical data and history
            
        Returns:
            Prediction results with confidence scores
        """
        try:
            # Extract relevant features for treatment response prediction
            features = self._extract_treatment_features(patient_data)
            
            # Use appropriate model for treatment response prediction
            model_name = "treatment_response_model"  # Default model name
            
            # Check if model exists, otherwise use a fallback
            if model_name not in self.model_registry.list_models():
                logger.warning(f"Model {model_name} not found, using fallback prediction")
                return self._fallback_treatment_prediction(patient_data)
            
            # Make prediction using the model
            prediction = self.make_prediction(
                model_name=model_name,
                features=features,
                patient_id=patient_data.get("patient_id", "unknown"),
                outcome_name="treatment_response"
            )
            
            if prediction:
                return {
                    "status": "success",
                    "patient_id": patient_data.get("patient_id"),
                    "predicted_response": prediction.predicted_value,
                    "confidence": prediction.confidence.value,
                    "confidence_score": prediction.confidence_score,
                    "model_version": prediction.model_version,
                    "features_used": prediction.features_used,
                    "prediction_date": prediction.prediction_date.isoformat()
                }
            else:
                return {
                    "status": "error",
                    "patient_id": patient_data.get("patient_id"),
                    "error": "Failed to generate prediction"
                }
                
        except Exception as e:
            logger.error(f"Error predicting treatment response: {e}")
            return {
                "status": "error",
                "patient_id": patient_data.get("patient_id"),
                "error": str(e)
            }
    
    def _extract_treatment_features(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features relevant for treatment response prediction."""
        features = {}
        
        # Extract basic patient information
        if "age" in patient_data:
            features["age"] = patient_data["age"]
        if "gender" in patient_data:
            features["gender"] = patient_data["gender"]
        
        # Extract clinical measurements
        if "vital_signs" in patient_data:
            vitals = patient_data["vital_signs"]
            if "blood_pressure" in vitals:
                features["systolic_bp"] = vitals["blood_pressure"].get("systolic", 0)
                features["diastolic_bp"] = vitals["blood_pressure"].get("diastolic", 0)
            if "heart_rate" in vitals:
                features["heart_rate"] = vitals["heart_rate"]
        
        # Extract lab results
        if "lab_results" in patient_data:
            labs = patient_data["lab_results"]
            for test, value in labs.items():
                features[f"lab_{test}"] = value
        
        # Extract treatment history
        if "treatment_history" in patient_data:
            history = patient_data["treatment_history"]
            features["previous_treatments"] = len(history)
            features["treatment_compliance"] = history.get("compliance_rate", 0.0)
        
        return features
    
    def _fallback_treatment_prediction(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback prediction when model is not available."""
        # Simple rule-based prediction as fallback
        age = patient_data.get("age", 50)
        compliance = patient_data.get("treatment_history", {}).get("compliance_rate", 0.5)
        
        # Simple scoring system
        score = 0
        if age < 65:
            score += 0.3
        if compliance > 0.8:
            score += 0.4
        if "vital_signs" in patient_data:
            score += 0.2
        
        response_probability = min(score, 1.0)
        
        return {
            "status": "success",
            "patient_id": patient_data.get("patient_id"),
            "predicted_response": "positive" if response_probability > 0.6 else "negative",
            "confidence": "low",
            "confidence_score": response_probability,
            "model_version": "fallback_1.0",
            "features_used": ["age", "compliance", "vital_signs"],
            "prediction_date": datetime.now().isoformat(),
            "note": "Fallback prediction used - model not available"
        }


# Global predictive engine instance
predictive_engine = PredictiveEngine()


def get_predictive_engine() -> PredictiveEngine:
    """Get a singleton instance of the predictive engine."""
    if not hasattr(get_predictive_engine, '_instance'):
        get_predictive_engine._instance = PredictiveEngine()
    return get_predictive_engine._instance


# API Router for Predictive Engine
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
from pydantic import BaseModel

prediction_router = APIRouter()

class PredictionRequest(BaseModel):
    model_name: str
    features: Dict[str, Any]
    patient_id: str
    outcome_name: str

class PredictionResponse(BaseModel):
    prediction_id: str
    patient_id: str
    outcome_name: str
    predicted_value: Any
    confidence: str
    confidence_score: float
    model_version: str
    features_used: List[str]
    prediction_date: str

@prediction_router.post("/predict", response_model=PredictionResponse)
async def make_prediction(request: PredictionRequest):
    """Make a prediction using the specified model."""
    try:
        engine = get_predictive_engine()
        prediction = engine.make_prediction(
            model_name=request.model_name,
            features=request.features,
            patient_id=request.patient_id,
            outcome_name=request.outcome_name
        )
        
        if prediction is None:
            raise HTTPException(status_code=400, detail="Failed to make prediction")
        
        return PredictionResponse(
            prediction_id=prediction.id,
            patient_id=prediction.patient_id,
            outcome_name=prediction.outcome_name,
            predicted_value=prediction.predicted_value,
            confidence=prediction.confidence.value,
            confidence_score=prediction.confidence_score,
            model_version=prediction.model_version,
            features_used=prediction.features_used,
            prediction_date=prediction.prediction_date.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@prediction_router.get("/models")
async def list_models():
    """List all available models."""
    try:
        engine = get_predictive_engine()
        models = engine.model_registry.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

@prediction_router.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """Get information about a specific model."""
    try:
        engine = get_predictive_engine()
        metadata = engine.model_registry.get_model_metadata(model_name)
        if metadata is None:
            raise HTTPException(status_code=404, detail="Model not found")
        return {"model_name": model_name, "metadata": metadata}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

@prediction_router.get("/patients/{patient_id}/predictions")
async def get_patient_predictions(patient_id: str):
    """Get all predictions for a patient."""
    try:
        engine = get_predictive_engine()
        # This would typically query a database in a real application
        # For now, return cached predictions
        patient_predictions = [
            pred for pred in engine.prediction_cache.values()
            if pred.patient_id == patient_id
        ]
        return {"patient_id": patient_id, "predictions": patient_predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting patient predictions: {str(e)}") 