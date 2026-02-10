"""
Readmission Risk Prediction Model
================================

This module provides machine learning models for predicting readmission risk
based on patient characteristics, admission details, and clinical factors.
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

class ReadmissionRiskModel:
    """Readmission risk prediction model"""
    
    def __init__(self, readmission_window: int = 30):
        self.readmission_window = readmission_window
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
        
    def prepare_features(self, patient_data: Dict[str, Any], admission_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features from patient and admission data"""
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
        
        # Admission characteristics
        features.extend([
            admission_data.get('length_of_stay', 0),
            len(admission_data.get('procedures', [])),
            1 if admission_data.get('icu_stay', False) else 0,
            1 if admission_data.get('emergency_admission', False) else 0,
            admission_data.get('number_of_diagnoses', 0),
            admission_data.get('number_of_medications', 0)
        ])
        
        # Lab results
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
        """Train the readmission risk model"""
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
            
            logger.info(f"Readmission risk model trained successfully. Accuracy: {accuracy:.3f}")
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'auc_score': auc_score,
                'cv_scores': cv_scores.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error training readmission risk model: {e}")
            raise
            
    def predict(self, patient_data: Dict[str, Any], admission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict readmission risk for a patient"""
        try:
            if self.model is None:
                raise ValueError("Model not trained. Please train the model first.")
                
            # Prepare features
            features = self.prepare_features(patient_data, admission_data)
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
            risk_categories = ['low', 'medium', 'high']
            predicted_risk = risk_categories[prediction] if prediction < len(risk_categories) else 'unknown'
            
            return {
                'prediction': predicted_risk,
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
                'readmission_window': self.readmission_window
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
            self.readmission_window = model_data['readmission_window']
            
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'readmission_window': self.readmission_window,
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
            age = np.random.normal(60, 20)
            age = max(18, min(100, age))
            
            gender = np.random.choice(['male', 'female'])
            
            height = np.random.normal(170, 10)
            weight = np.random.normal(75, 15)
            bmi = weight / ((height / 100) ** 2)
            
            # Generate health metrics
            bp_systolic = np.random.normal(130, 25)
            bp_diastolic = np.random.normal(85, 15)
            heart_rate = np.random.normal(80, 20)
            temperature = np.random.normal(36.8, 0.8)
            glucose = np.random.normal(110, 30)
            
            # Generate comorbidities
            diabetes = np.random.choice([0, 1], p=[0.8, 0.2])
            smoking = np.random.choice([0, 1], p=[0.7, 0.3])
            family_history_count = np.random.poisson(1.5)
            medication_count = np.random.poisson(3)
            
            # Generate admission data
            length_of_stay = np.random.exponential(5)
            procedures_count = np.random.poisson(2)
            icu_stay = np.random.choice([0, 1], p=[0.8, 0.2])
            emergency_admission = np.random.choice([0, 1], p=[0.6, 0.4])
            diagnoses_count = np.random.poisson(3)
            medications_count = np.random.poisson(4)
            
            # Generate lab results
            creatinine = np.random.normal(1.2, 0.4)
            albumin = np.random.normal(3.8, 0.6)
            hemoglobin = np.random.normal(13, 2.5)
            platelets = np.random.normal(240, 60)
            wbc = np.random.normal(8, 3)
            
            # Create feature vector
            features = [
                age, 1 if gender == 'male' else 0, height, weight, bmi,
                bp_systolic, bp_diastolic, heart_rate, temperature, glucose,
                diabetes, smoking, family_history_count, medication_count,
                length_of_stay, procedures_count, icu_stay, emergency_admission,
                diagnoses_count, medications_count,
                creatinine, albumin, hemoglobin, platelets, wbc
            ]
            
            # Pad with zeros
            while len(features) < 50:
                features.append(0)
                
            # Generate target (readmission risk)
            # Simple rule-based target generation
            risk_score = 0.3  # Base risk
            
            # Age factor
            if age > 75:
                risk_score += 0.2
            elif age > 65:
                risk_score += 0.1
                
            # Health factor
            if bmi > 30:
                risk_score += 0.1
            if diabetes:
                risk_score += 0.2
            if smoking:
                risk_score += 0.1
                
            # Admission factor
            if length_of_stay > 7:
                risk_score += 0.2
            if icu_stay:
                risk_score += 0.3
            if emergency_admission:
                risk_score += 0.2
            if diagnoses_count > 5:
                risk_score += 0.1
                
            # Add randomness
            risk_score += np.random.normal(0, 0.15)
            risk_score = max(0, min(1, risk_score))
            
            # Convert to risk category
            if risk_score > 0.6:
                target = 2  # high
            elif risk_score > 0.3:
                target = 1  # medium
            else:
                target = 0  # low
                
            data.append(features + [target])
            
        # Create DataFrame
        feature_names = [f'feature_{i}' for i in range(50)]
        columns = feature_names + ['readmission_risk']
        
        return pd.DataFrame(data, columns=columns)

# Example usage
if __name__ == "__main__":
    # Create model
    model = ReadmissionRiskModel(readmission_window=30)
    
    # Generate sample data
    training_data = model.generate_sample_data(1000)
    
    # Train model
    results = model.train(training_data, 'readmission_risk', 'random_forest')
    print(f"Training results: {results}")
    
    # Test prediction
    sample_patient = {
        'age': 75,
        'gender': 'male',
        'height_cm': 175,
        'weight_kg': 85,
        'blood_pressure_systolic': 150,
        'blood_pressure_diastolic': 95,
        'heart_rate': 85,
        'temperature': 37.2,
        'glucose_level': 120,
        'diabetes_status': 'type2',
        'smoking_status': 'current',
        'family_history': ['heart_disease', 'diabetes'],
        'medications': ['metformin', 'lisinopril', 'aspirin'],
        'lab_results': {
            'creatinine': 1.4,
            'albumin': 3.5,
            'hemoglobin': 12.5,
            'platelets': 220,
            'wbc': 8.5
        }
    }
    
    sample_admission = {
        'length_of_stay': 8,
        'procedures': ['cardiac_catheterization', 'stent_placement'],
        'icu_stay': True,
        'emergency_admission': True,
        'number_of_diagnoses': 6,
        'number_of_medications': 5
    }
    
    prediction = model.predict(sample_patient, sample_admission)
    print(f"Prediction: {prediction}")
    
    # Save model
    model.save_model('readmission_risk_model.pkl') 