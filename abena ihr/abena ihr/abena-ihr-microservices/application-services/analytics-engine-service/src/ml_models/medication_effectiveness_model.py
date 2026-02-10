"""
Medication Effectiveness Prediction Model
========================================

This module provides machine learning models for predicting medication effectiveness
based on patient characteristics, medication details, and clinical factors.
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

class MedicationEffectivenessModel:
    """Medication effectiveness prediction model"""
    
    def __init__(self, medication_type: str = "general"):
        self.medication_type = medication_type
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
        
    def prepare_features(self, patient_data: Dict[str, Any], medication_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features from patient and medication data"""
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
        
        # Medication characteristics
        features.extend([
            medication_data.get('dosage_mg', 0),
            medication_data.get('frequency_per_day', 0),
            medication_data.get('duration_days', 0),
            1 if medication_data.get('taken_with_food', False) else 0,
            1 if medication_data.get('combination_therapy', False) else 0,
            medication_data.get('patient_compliance_rate', 0.8)  # Default 80%
        ])
        
        # Medication class encoding
        medication_classes = ['ace_inhibitor', 'beta_blocker', 'diuretic', 'statin', 'antidiabetic', 'anticoagulant']
        medication_class = medication_data.get('medication_class', 'ace_inhibitor')
        for m_class in medication_classes:
            features.append(1 if m_class == medication_class else 0)
            
        # Lab results
        lab_results = patient_data.get('lab_results', {})
        for lab_name in ['creatinine', 'albumin', 'hemoglobin', 'platelets', 'wbc', 'liver_enzymes']:
            value = lab_results.get(lab_name, 0)
            features.append(value / 1000)  # Simple normalization
            
        # Pad with zeros if needed
        while len(features) < 60:
            features.append(0)
            
        return np.array(features).reshape(1, -1)
        
    def train(self, training_data: pd.DataFrame, target_column: str, 
              model_type: str = "random_forest") -> Dict[str, Any]:
        """Train the medication effectiveness model"""
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
            
            logger.info(f"Medication effectiveness model trained successfully. Accuracy: {accuracy:.3f}")
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'auc_score': auc_score,
                'cv_scores': cv_scores.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error training medication effectiveness model: {e}")
            raise
            
    def predict(self, patient_data: Dict[str, Any], medication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict medication effectiveness for a patient"""
        try:
            if self.model is None:
                raise ValueError("Model not trained. Please train the model first.")
                
            # Prepare features
            features = self.prepare_features(patient_data, medication_data)
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
                        
            # Map prediction to effectiveness categories
            effectiveness_categories = ['ineffective', 'moderately_effective', 'effective', 'highly_effective']
            predicted_effectiveness = effectiveness_categories[prediction] if prediction < len(effectiveness_categories) else 'unknown'
            
            return {
                'prediction': predicted_effectiveness,
                'confidence': float(max(probabilities)),
                'probabilities': probabilities.tolist(),
                'effectiveness_score': float(max(probabilities)),
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
                'medication_type': self.medication_type
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
            self.medication_type = model_data['medication_type']
            
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'medication_type': self.medication_type,
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
            age = np.random.normal(55, 20)
            age = max(18, min(100, age))
            
            gender = np.random.choice(['male', 'female'])
            
            height = np.random.normal(170, 10)
            weight = np.random.normal(75, 15)
            bmi = weight / ((height / 100) ** 2)
            
            # Generate health metrics
            bp_systolic = np.random.normal(130, 25)
            bp_diastolic = np.random.normal(85, 15)
            heart_rate = np.random.normal(75, 15)
            temperature = np.random.normal(36.8, 0.5)
            glucose = np.random.normal(110, 25)
            
            # Generate comorbidities
            diabetes = np.random.choice([0, 1], p=[0.8, 0.2])
            smoking = np.random.choice([0, 1], p=[0.8, 0.2])
            family_history_count = np.random.poisson(1.5)
            medication_count = np.random.poisson(3)
            
            # Generate medication data
            dosage = np.random.normal(50, 20)
            frequency = np.random.choice([1, 2, 3])
            duration = np.random.exponential(30)
            taken_with_food = np.random.choice([0, 1], p=[0.3, 0.7])
            combination_therapy = np.random.choice([0, 1], p=[0.6, 0.4])
            compliance_rate = np.random.beta(8, 2)  # Beta distribution for compliance
            
            # Generate medication class
            medication_classes = ['ace_inhibitor', 'beta_blocker', 'diuretic', 'statin', 'antidiabetic', 'anticoagulant']
            medication_class = np.random.choice(medication_classes)
            
            # Generate lab results
            creatinine = np.random.normal(1.1, 0.3)
            albumin = np.random.normal(4.0, 0.5)
            hemoglobin = np.random.normal(14, 2)
            platelets = np.random.normal(250, 50)
            wbc = np.random.normal(7, 2)
            liver_enzymes = np.random.normal(25, 10)
            
            # Create feature vector
            features = [
                age, 1 if gender == 'male' else 0, height, weight, bmi,
                bp_systolic, bp_diastolic, heart_rate, temperature, glucose,
                diabetes, smoking, family_history_count, medication_count,
                dosage, frequency, duration, taken_with_food, combination_therapy, compliance_rate
            ]
            
            # Add medication class encoding
            for m_class in medication_classes:
                features.append(1 if m_class == medication_class else 0)
                
            # Add lab results
            features.extend([creatinine, albumin, hemoglobin, platelets, wbc, liver_enzymes])
            
            # Pad with zeros
            while len(features) < 60:
                features.append(0)
                
            # Generate target (medication effectiveness)
            # Simple rule-based target generation
            effectiveness_score = 0.5  # Base score
            
            # Age factor
            if age > 75:
                effectiveness_score -= 0.1
            elif age < 30:
                effectiveness_score += 0.05
                
            # Health factor
            if bmi > 30:
                effectiveness_score -= 0.1
            if diabetes:
                effectiveness_score -= 0.05
            if smoking:
                effectiveness_score -= 0.1
                
            # Medication factor
            if combination_therapy:
                effectiveness_score += 0.1
            if taken_with_food:
                effectiveness_score += 0.05
            if compliance_rate > 0.9:
                effectiveness_score += 0.2
            elif compliance_rate < 0.7:
                effectiveness_score -= 0.2
                
            # Add randomness
            effectiveness_score += np.random.normal(0, 0.15)
            effectiveness_score = max(0, min(1, effectiveness_score))
            
            # Convert to effectiveness category
            if effectiveness_score > 0.8:
                target = 3  # highly_effective
            elif effectiveness_score > 0.6:
                target = 2  # effective
            elif effectiveness_score > 0.4:
                target = 1  # moderately_effective
            else:
                target = 0  # ineffective
                
            data.append(features + [target])
            
        # Create DataFrame
        feature_names = [f'feature_{i}' for i in range(60)]
        columns = feature_names + ['medication_effectiveness']
        
        return pd.DataFrame(data, columns=columns)

# Example usage
if __name__ == "__main__":
    # Create model
    model = MedicationEffectivenessModel(medication_type="cardiovascular")
    
    # Generate sample data
    training_data = model.generate_sample_data(1000)
    
    # Train model
    results = model.train(training_data, 'medication_effectiveness', 'random_forest')
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
        'smoking_status': 'former',
        'family_history': ['heart_disease'],
        'medications': ['metformin'],
        'lab_results': {
            'creatinine': 1.2,
            'albumin': 3.8,
            'hemoglobin': 13.5,
            'platelets': 240,
            'wbc': 7.5,
            'liver_enzymes': 28
        }
    }
    
    sample_medication = {
        'medication_class': 'ace_inhibitor',
        'dosage_mg': 25,
        'frequency_per_day': 2,
        'duration_days': 30,
        'taken_with_food': True,
        'combination_therapy': True,
        'patient_compliance_rate': 0.9
    }
    
    prediction = model.predict(sample_patient, sample_medication)
    print(f"Prediction: {prediction}")
    
    # Save model
    model.save_model('medication_effectiveness_model.pkl') 