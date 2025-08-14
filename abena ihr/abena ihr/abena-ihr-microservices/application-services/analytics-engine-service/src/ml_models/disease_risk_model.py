"""
Disease Risk Prediction Model
============================

This module provides machine learning models for predicting disease risk
based on patient demographics, vital signs, lab results, and other health indicators.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score, classification_report
import joblib
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DiseaseRiskModel:
    """Disease risk prediction model"""
    
    def __init__(self, disease_type: str = "general"):
        self.disease_type = disease_type
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
        
    def prepare_features(self, patient_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features from patient data"""
        features = []
        
        # Demographics
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
        
        # Vital signs
        features.extend([
            patient_data.get('blood_pressure_systolic', 0),
            patient_data.get('blood_pressure_diastolic', 0),
            patient_data.get('heart_rate', 0),
            patient_data.get('temperature', 0),
            patient_data.get('glucose_level', 0)
        ])
        
        # Cholesterol levels
        features.extend([
            patient_data.get('cholesterol_total', 0),
            patient_data.get('cholesterol_hdl', 0),
            patient_data.get('cholesterol_ldl', 0),
            patient_data.get('triglycerides', 0)
        ])
        
        # Risk factors
        features.extend([
            1 if patient_data.get('smoking_status') == 'current' else 0,
            1 if patient_data.get('diabetes_status') in ['type1', 'type2', 'gestational'] else 0,
            len(patient_data.get('family_history', [])),
            len(patient_data.get('medications', []))
        ])
        
        # Lab results (normalize)
        lab_results = patient_data.get('lab_results', {})
        for lab_name in ['creatinine', 'albumin', 'hemoglobin', 'platelets', 'wbc']:
            value = lab_results.get(lab_name, 0)
            features.append(value / 1000)  # Simple normalization
            
        # Pad with zeros if needed
        while len(features) < 50:
            features.append(0)
            
        return np.array(features).reshape(1, -1)
        
    def train(self, training_data: pd.DataFrame, target_column: str, 
              model_type: str = "random_forest") -> Dict[str, Any]:
        """Train the disease risk model"""
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
            
            logger.info(f"Disease risk model trained successfully. Accuracy: {accuracy:.3f}")
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'auc_score': auc_score,
                'cv_scores': cv_scores.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error training disease risk model: {e}")
            raise
            
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict disease risk for a patient"""
        try:
            if self.model is None:
                raise ValueError("Model not trained. Please train the model first.")
                
            # Prepare features
            features = self.prepare_features(patient_data)
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
                        
            # Map prediction to risk categories
            risk_categories = ['low_risk', 'moderate_risk', 'high_risk']
            predicted_category = risk_categories[prediction] if prediction < len(risk_categories) else 'unknown'
            
            return {
                'prediction': predicted_category,
                'confidence': float(max(probabilities)),
                'probabilities': probabilities.tolist(),
                'risk_score': float(max(probabilities)),
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
                'disease_type': self.disease_type
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
            self.disease_type = model_data['disease_type']
            
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'disease_type': self.disease_type,
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
            # Generate realistic patient data
            age = np.random.normal(50, 20)
            age = max(18, min(100, age))
            
            gender = np.random.choice(['male', 'female'])
            
            height = np.random.normal(170, 10)
            weight = np.random.normal(70, 15)
            bmi = weight / ((height / 100) ** 2)
            
            # Generate vital signs
            bp_systolic = np.random.normal(120, 20)
            bp_diastolic = np.random.normal(80, 10)
            heart_rate = np.random.normal(75, 15)
            temperature = np.random.normal(36.8, 0.5)
            glucose = np.random.normal(100, 20)
            
            # Generate cholesterol levels
            cholesterol_total = np.random.normal(200, 40)
            cholesterol_hdl = np.random.normal(50, 15)
            cholesterol_ldl = np.random.normal(120, 30)
            triglycerides = np.random.normal(150, 50)
            
            # Generate risk factors
            smoking = np.random.choice([0, 1], p=[0.8, 0.2])
            diabetes = np.random.choice([0, 1], p=[0.9, 0.1])
            family_history_count = np.random.poisson(1)
            medication_count = np.random.poisson(2)
            
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
                cholesterol_total, cholesterol_hdl, cholesterol_ldl, triglycerides,
                smoking, diabetes, family_history_count, medication_count,
                creatinine, albumin, hemoglobin, platelets, wbc
            ]
            
            # Pad with zeros
            while len(features) < 50:
                features.append(0)
                
            # Generate target (disease risk)
            # Simple rule-based target generation
            risk_score = 0
            if age > 65: risk_score += 0.3
            if bmi > 30: risk_score += 0.3
            if bp_systolic > 140: risk_score += 0.2
            if diabetes: risk_score += 0.4
            if smoking: risk_score += 0.3
            if glucose > 126: risk_score += 0.3
            
            # Add some randomness
            risk_score += np.random.normal(0, 0.1)
            risk_score = max(0, min(1, risk_score))
            
            # Convert to risk category
            if risk_score > 0.6:
                target = 2  # high_risk
            elif risk_score > 0.3:
                target = 1  # moderate_risk
            else:
                target = 0  # low_risk
                
            data.append(features + [target])
            
        # Create DataFrame
        feature_names = [f'feature_{i}' for i in range(50)]
        columns = feature_names + ['disease_risk']
        
        return pd.DataFrame(data, columns=columns)

# Example usage
if __name__ == "__main__":
    # Create model
    model = DiseaseRiskModel(disease_type="cardiovascular")
    
    # Generate sample data
    training_data = model.generate_sample_data(1000)
    
    # Train model
    results = model.train(training_data, 'disease_risk', 'random_forest')
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
        'cholesterol_total': 220,
        'cholesterol_hdl': 45,
        'cholesterol_ldl': 140,
        'triglycerides': 180,
        'smoking_status': 'current',
        'diabetes_status': 'type2',
        'family_history': ['heart_disease', 'diabetes'],
        'medications': ['metformin', 'lisinopril'],
        'lab_results': {
            'creatinine': 1.2,
            'albumin': 3.8,
            'hemoglobin': 13.5,
            'platelets': 240,
            'wbc': 7.5
        }
    }
    
    prediction = model.predict(sample_patient)
    print(f"Prediction: {prediction}")
    
    # Save model
    model.save_model('disease_risk_model.pkl') 