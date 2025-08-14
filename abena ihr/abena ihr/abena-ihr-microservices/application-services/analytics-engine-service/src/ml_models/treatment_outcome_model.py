"""
Treatment Outcome Prediction Model
=================================

This module provides machine learning models for predicting treatment outcomes
based on patient characteristics, treatment details, and clinical factors.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
import joblib
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class TreatmentOutcomeModel:
    """Treatment outcome prediction model"""
    
    def __init__(self, treatment_type: str = "general"):
        self.treatment_type = treatment_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.model_metadata = {
            'created_at': datetime.now(),
            'last_updated': datetime.now(),
            'version': '1.0.0',
            'performance_metrics': {}
        }
        
    def prepare_features(self, patient_data: Dict[str, Any], treatment_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features from patient and treatment data"""
        features = []
        
        # Patient demographics
        features.extend([
            patient_data.get('age', 0),
            1 if patient_data.get('gender') == 'male' else 0,
            patient_data.get('height_cm', 0),
            patient_data.get('weight_kg', 0)
        ])
        
        # Calculate BMI
        height = patient_data.get('height_cm', 0)
        weight = patient_data.get('weight_kg', 0)
        bmi = weight / ((height / 100) ** 2) if height > 0 else 0
        features.append(bmi)
        
        # Patient health status
        features.extend([
            patient_data.get('blood_pressure_systolic', 0),
            patient_data.get('blood_pressure_diastolic', 0),
            patient_data.get('heart_rate', 0),
            patient_data.get('temperature', 0),
            patient_data.get('glucose_level', 0)
        ])
        
        # Comorbidities
        features.extend([
            1 if patient_data.get('diabetes_status') in ['type1', 'type2', 'gestational'] else 0,
            1 if patient_data.get('smoking_status') == 'current' else 0,
            len(patient_data.get('family_history', [])),
            len(patient_data.get('medications', []))
        ])
        
        # Treatment characteristics
        features.extend([
            treatment_data.get('treatment_duration_days', 0),
            treatment_data.get('dosage_mg', 0),
            treatment_data.get('frequency_per_day', 0),
            1 if treatment_data.get('combination_therapy', False) else 0,
            1 if treatment_data.get('previous_treatment_failure', False) else 0
        ])
        
        # Treatment type encoding
        treatment_types = ['medication', 'surgery', 'therapy', 'lifestyle', 'monitoring']
        treatment_type = treatment_data.get('treatment_type', 'medication')
        for t_type in treatment_types:
            features.append(1 if t_type == treatment_type else 0)
            
        # Lab results
        lab_results = patient_data.get('lab_results', {})
        for lab_name in ['creatinine', 'albumin', 'hemoglobin', 'platelets', 'wbc']:
            value = lab_results.get(lab_name, 0)
            features.append(value / 1000)  # Simple normalization
            
        # Pad with zeros if needed
        while len(features) < 60:
            features.append(0)
            
        return np.array(features).reshape(1, -1)
        
    def train(self, training_data: pd.DataFrame, target_column: str, 
              model_type: str = "random_forest") -> Dict[str, Any]:
        """Train the treatment outcome model"""
        try:
            # Prepare features and target
            X = training_data.drop(columns=[target_column])
            y = training_data[target_column]
            
            # Store feature names
            self.feature_names = list(X.columns)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Select and train model
            if model_type == "random_forest":
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            elif model_type == "gradient_boosting":
                self.model = GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=5,
                    random_state=42
                )
            elif model_type == "logistic_regression":
                self.model = LogisticRegression(random_state=42, max_iter=1000)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
                
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
            auc_score = roc_auc_score(y_test, y_pred_proba[:, 1]) if len(np.unique(y)) == 2 else 0
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
            
            # Store performance metrics
            self.model_metadata['performance_metrics'] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'auc_score': auc_score,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            self.model_metadata['last_updated'] = datetime.now()
            
            logger.info(f"Treatment outcome model trained successfully. Accuracy: {accuracy:.3f}")
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'auc_score': auc_score,
                'cv_scores': cv_scores.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error training treatment outcome model: {e}")
            raise
            
    def predict(self, patient_data: Dict[str, Any], treatment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict treatment outcome for a patient"""
        try:
            if self.model is None:
                raise ValueError("Model not trained. Please train the model first.")
                
            # Prepare features
            features = self.prepare_features(patient_data, treatment_data)
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Get feature importance if available
            feature_importance = {}
            if hasattr(self.model, 'feature_importances_'):
                for i, importance in enumerate(self.model.feature_importances_):
                    if i < len(self.feature_names):
                        feature_importance[self.feature_names[i]] = float(importance)
                        
            # Map prediction to outcome categories
            outcome_categories = ['poor', 'fair', 'good', 'excellent']
            predicted_outcome = outcome_categories[prediction] if prediction < len(outcome_categories) else 'unknown'
            
            return {
                'prediction': predicted_outcome,
                'confidence': float(max(probabilities)),
                'probabilities': probabilities.tolist(),
                'success_probability': float(max(probabilities)),
                'feature_importance': feature_importance,
                'model_version': self.model_metadata['version']
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
            
    def save_model(self, filepath: str):
        """Save the trained model"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_names': self.feature_names,
                'model_metadata': self.model_metadata,
                'treatment_type': self.treatment_type
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
            
    def load_model(self, filepath: str):
        """Load a trained model"""
        try:
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_names = model_data['feature_names']
            self.model_metadata = model_data['model_metadata']
            self.treatment_type = model_data['treatment_type']
            
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'treatment_type': self.treatment_type,
            'model_type': type(self.model).__name__ if self.model else None,
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'metadata': self.model_metadata,
            'is_trained': self.model is not None
        }
        
    def generate_sample_data(self, num_samples: int = 1000) -> pd.DataFrame:
        """Generate sample training data"""
        np.random.seed(42)
        
        data = []
        for _ in range(num_samples):
            # Generate patient data
            age = np.random.normal(50, 20)
            age = max(18, min(100, age))
            
            gender = np.random.choice(['male', 'female'])
            
            height = np.random.normal(170, 10)
            weight = np.random.normal(70, 15)
            bmi = weight / ((height / 100) ** 2)
            
            # Generate health metrics
            bp_systolic = np.random.normal(120, 20)
            bp_diastolic = np.random.normal(80, 10)
            heart_rate = np.random.normal(75, 15)
            temperature = np.random.normal(36.8, 0.5)
            glucose = np.random.normal(100, 20)
            
            # Generate comorbidities
            diabetes = np.random.choice([0, 1], p=[0.9, 0.1])
            smoking = np.random.choice([0, 1], p=[0.8, 0.2])
            family_history_count = np.random.poisson(1)
            medication_count = np.random.poisson(2)
            
            # Generate treatment data
            treatment_duration = np.random.exponential(30)
            dosage = np.random.normal(50, 20)
            frequency = np.random.choice([1, 2, 3])
            combination_therapy = np.random.choice([0, 1], p=[0.7, 0.3])
            previous_failure = np.random.choice([0, 1], p=[0.8, 0.2])
            
            # Generate treatment type
            treatment_types = ['medication', 'surgery', 'therapy', 'lifestyle', 'monitoring']
            treatment_type = np.random.choice(treatment_types)
            
            # Generate lab results
            creatinine = np.random.normal(1.0, 0.3)
            albumin = np.random.normal(4.0, 0.5)
            hemoglobin = np.random.normal(14, 2)
            platelets = np.random.normal(250, 50)
            wbc = np.random.normal(7, 2)
            
            # Create feature vector
            features = [
                age, 1 if gender == 'male' else 0, height, weight, bmi,
                bp_systolic, bp_diastolic, heart_rate, temperature, glucose,
                diabetes, smoking, family_history_count, medication_count,
                treatment_duration, dosage, frequency, combination_therapy, previous_failure
            ]
            
            # Add treatment type encoding
            for t_type in treatment_types:
                features.append(1 if t_type == treatment_type else 0)
                
            # Add lab results
            features.extend([creatinine, albumin, hemoglobin, platelets, wbc])
            
            # Pad with zeros
            while len(features) < 60:
                features.append(0)
                
            # Generate target (treatment outcome)
            # Simple rule-based target generation
            outcome_score = 0.5  # Base score
            
            # Age factor
            if age > 75:
                outcome_score -= 0.2
            elif age < 30:
                outcome_score += 0.1
                
            # Health factor
            if bmi > 30:
                outcome_score -= 0.1
            if diabetes:
                outcome_score -= 0.2
            if smoking:
                outcome_score -= 0.1
                
            # Treatment factor
            if combination_therapy:
                outcome_score += 0.1
            if previous_failure:
                outcome_score -= 0.3
                
            # Add randomness
            outcome_score += np.random.normal(0, 0.2)
            outcome_score = max(0, min(1, outcome_score))
            
            # Convert to outcome category
            if outcome_score > 0.8:
                target = 3  # excellent
            elif outcome_score > 0.6:
                target = 2  # good
            elif outcome_score > 0.4:
                target = 1  # fair
            else:
                target = 0  # poor
                
            data.append(features + [target])
            
        # Create DataFrame
        feature_names = [f'feature_{i}' for i in range(60)]
        columns = feature_names + ['treatment_outcome']
        
        return pd.DataFrame(data, columns=columns)

# Example usage
if __name__ == "__main__":
    # Create model
    model = TreatmentOutcomeModel(treatment_type="medication")
    
    # Generate sample data
    training_data = model.generate_sample_data(1000)
    
    # Train model
    results = model.train(training_data, 'treatment_outcome', 'random_forest')
    print(f"Training results: {results}")
    
    # Test prediction
    sample_patient = {
        'age': 65,
        'gender': 'male',
        'height_cm': 175,
        'weight_kg': 85,
        'blood_pressure_systolic': 150,
        'blood_pressure_diastolic': 95,
        'heart_rate': 80,
        'temperature': 36.8,
        'glucose_level': 110,
        'diabetes_status': 'type2',
        'smoking_status': 'current',
        'family_history': ['heart_disease'],
        'medications': ['metformin'],
        'lab_results': {
            'creatinine': 1.2,
            'albumin': 3.8,
            'hemoglobin': 13.5,
            'platelets': 240,
            'wbc': 7.5
        }
    }
    
    sample_treatment = {
        'treatment_type': 'medication',
        'treatment_duration_days': 30,
        'dosage_mg': 50,
        'frequency_per_day': 2,
        'combination_therapy': True,
        'previous_treatment_failure': False
    }
    
    prediction = model.predict(sample_patient, sample_treatment)
    print(f"Prediction: {prediction}")
    
    # Save model
    model.save_model('treatment_outcome_model.pkl') 