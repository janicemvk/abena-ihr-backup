#!/usr/bin/env python3
"""
Sample Data Creation Script for Abena IHR System

This script creates realistic sample patient data for testing
and demonstration purposes.
"""

import os
import sys
import random
from datetime import datetime, timedelta
from typing import List, Dict
import psycopg2
from psycopg2.extras import Json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.data_models import PatientProfile, TreatmentPlan

# Database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'abena_ihr',
    'user': 'abena_user',
    'password': 'EKZz4h%*6yyH$WqK',
    'port': 5432
}

class SampleDataGenerator:
    """Generate realistic sample data for testing"""
    
    def __init__(self):
        self.connection = None
        self.first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
            "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
            "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
            "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna"
        ]
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"
        ]
        
        self.medical_conditions = [
            "chronic_pain", "fibromyalgia", "arthritis", "diabetes", "hypertension",
            "depression", "anxiety", "migraine", "back_pain", "osteoporosis",
            "chronic_fatigue", "neuropathy", "inflammatory_bowel_disease"
        ]
        
        self.medications = [
            "ibuprofen", "acetaminophen", "gabapentin", "pregabalin", "tramadol",
            "metformin", "lisinopril", "amlodipine", "sertraline", "duloxetine",
            "omeprazole", "metoprolol", "atorvastatin", "levothyroxine"
        ]
        
        self.treatment_types = ["pharmacological", "behavioral", "combined", "interventional"]
        
        self.lifestyle_interventions = [
            "physical_therapy", "cognitive_behavioral_therapy", "meditation",
            "exercise_therapy", "nutrition_counseling", "stress_management",
            "sleep_hygiene", "pain_education", "mindfulness_training"
        ]

    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**DATABASE_CONFIG)
            print("✅ Connected to database successfully")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        create_tables_sql = """
        -- Patients table
        CREATE TABLE IF NOT EXISTS patients (
            patient_id VARCHAR(50) PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL CHECK (age >= 0 AND age <= 120),
            gender VARCHAR(20) NOT NULL,
            genomics_data JSONB DEFAULT '{}',
            biomarkers JSONB DEFAULT '{}',
            medical_history TEXT[] DEFAULT '{}',
            current_medications TEXT[] DEFAULT '{}',
            lifestyle_metrics JSONB DEFAULT '{}',
            pain_scores REAL[] DEFAULT '{}',
            functional_assessments JSONB DEFAULT '{}',
            allergies TEXT[] DEFAULT '{}',
            lab_results JSONB DEFAULT '{}',
            vital_signs JSONB DEFAULT '{}',
            comorbidities TEXT[] DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Treatment plans table
        CREATE TABLE IF NOT EXISTS treatment_plans (
            treatment_id VARCHAR(50) PRIMARY KEY,
            patient_id VARCHAR(50) REFERENCES patients(patient_id),
            treatment_type VARCHAR(50) NOT NULL,
            medications TEXT[] DEFAULT '{}',
            dosages JSONB DEFAULT '{}',
            duration_weeks INTEGER NOT NULL CHECK (duration_weeks > 0),
            lifestyle_interventions TEXT[] DEFAULT '{}',
            notes TEXT,
            contraindications TEXT[] DEFAULT '{}',
            monitoring_requirements TEXT[] DEFAULT '{}',
            expected_outcomes TEXT[] DEFAULT '{}',
            side_effects TEXT[] DEFAULT '{}',
            cost_estimate DECIMAL(10,2),
            evidence_level VARCHAR(20) DEFAULT 'Level III',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Treatment outcomes table
        CREATE TABLE IF NOT EXISTS treatment_outcomes (
            outcome_id SERIAL PRIMARY KEY,
            patient_id VARCHAR(50) REFERENCES patients(patient_id),
            treatment_id VARCHAR(50) REFERENCES treatment_plans(treatment_id),
            outcome_type VARCHAR(50) NOT NULL,
            success_rating REAL CHECK (success_rating >= 0 AND success_rating <= 10),
            pain_reduction_percentage REAL,
            side_effects_experienced TEXT[] DEFAULT '{}',
            patient_satisfaction REAL CHECK (patient_satisfaction >= 0 AND patient_satisfaction <= 10),
            functional_improvement REAL,
            notes TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Predictions table
        CREATE TABLE IF NOT EXISTS predictions (
            prediction_id SERIAL PRIMARY KEY,
            patient_id VARCHAR(50) REFERENCES patients(patient_id),
            treatment_id VARCHAR(50) REFERENCES treatment_plans(treatment_id),
            success_probability REAL NOT NULL CHECK (success_probability >= 0 AND success_probability <= 1),
            risk_score REAL NOT NULL CHECK (risk_score >= 0 AND risk_score <= 1),
            key_factors TEXT[] DEFAULT '{}',
            warnings TEXT[] DEFAULT '{}',
            confidence_interval_low REAL,
            confidence_interval_high REAL,
            model_version VARCHAR(20) DEFAULT '1.0.0',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_patients_age ON patients(age);
        CREATE INDEX IF NOT EXISTS idx_patients_gender ON patients(gender);
        CREATE INDEX IF NOT EXISTS idx_treatment_plans_patient_id ON treatment_plans(patient_id);
        CREATE INDEX IF NOT EXISTS idx_treatment_plans_type ON treatment_plans(treatment_type);
        CREATE INDEX IF NOT EXISTS idx_predictions_patient_id ON predictions(patient_id);
        CREATE INDEX IF NOT EXISTS idx_predictions_success_prob ON predictions(success_probability);
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(create_tables_sql)
                self.connection.commit()
            print("✅ Database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Table creation failed: {e}")
            return False

    def generate_patient(self, patient_id: str) -> Dict:
        """Generate a realistic patient profile"""
        age = random.randint(18, 85)
        gender = random.choice(['male', 'female'])
        
        # Generate realistic medical history based on age
        medical_history = []
        if age > 40:
            medical_history.extend(random.sample(self.medical_conditions[:5], random.randint(1, 3)))
        if age > 60:
            medical_history.extend(random.sample(self.medical_conditions[5:], random.randint(1, 2)))
        
        # Generate current medications
        current_medications = random.sample(self.medications, random.randint(0, min(6, len(medical_history) + 2)))
        
        # Generate pain scores (realistic chronic pain patterns)
        pain_scores = []
        if "chronic_pain" in medical_history or "fibromyalgia" in medical_history:
            base_pain = random.uniform(4.0, 8.0)
            for _ in range(random.randint(5, 12)):
                pain_scores.append(max(0, min(10, base_pain + random.uniform(-2.0, 2.0))))
        
        # Generate genomics data
        genomics_data = {}
        if random.random() < 0.7:  # 70% have genomics data
            genomics_data = {
                'CYP2C9_activity': round(random.uniform(0.3, 1.8), 2),
                'OPRM1_variant': random.choice([0, 1]),
                'COMT_activity': round(random.uniform(0.5, 1.5), 2)
            }
        
        # Generate biomarkers
        biomarkers = {}
        if random.random() < 0.6:  # 60% have biomarker data
            biomarkers = {
                'inflammatory_markers': {
                    'CRP': round(random.uniform(0.1, 15.0), 2),
                    'ESR': random.randint(2, 100)
                },
                'metabolic_markers': {
                    'glucose': random.randint(70, 200),
                    'HbA1c': round(random.uniform(4.5, 12.0), 1)
                }
            }
        
        return {
            'patient_id': patient_id,
            'first_name': random.choice(self.first_names),
            'last_name': random.choice(self.last_names),
            'age': age,
            'gender': gender,
            'genomics_data': genomics_data,
            'biomarkers': biomarkers,
            'medical_history': medical_history,
            'current_medications': current_medications,
            'lifestyle_metrics': {},
            'pain_scores': pain_scores,
            'functional_assessments': {},
            'allergies': random.sample(['penicillin', 'sulfa', 'latex', 'iodine'], random.randint(0, 2)),
            'lab_results': {},
            'vital_signs': {},
            'comorbidities': []
        }

    def generate_treatment_plan(self, patient_id: str, treatment_id: str) -> Dict:
        """Generate a realistic treatment plan for a patient"""
        treatment_type = random.choice(self.treatment_types)
        
        medications = []
        dosages = {}
        
        if treatment_type in ['pharmacological', 'combined']:
            med_count = random.randint(1, 3)
            medications = random.sample(self.medications[:8], med_count)  # Pain medications
            for med in medications:
                dosages[med] = f"{random.randint(25, 200)}mg_{random.choice(['daily', 'bid', 'tid'])}"
        
        lifestyle_interventions = []
        if treatment_type in ['behavioral', 'combined']:
            lifestyle_interventions = random.sample(self.lifestyle_interventions, random.randint(1, 4))
        
        return {
            'treatment_id': treatment_id,
            'patient_id': patient_id,
            'treatment_type': treatment_type,
            'medications': medications,
            'dosages': dosages,
            'duration_weeks': random.randint(4, 24),
            'lifestyle_interventions': lifestyle_interventions,
            'notes': f'Treatment plan for {treatment_type} approach',
            'contraindications': [],
            'monitoring_requirements': ['pain_assessment', 'side_effect_monitoring'],
            'expected_outcomes': ['pain_reduction', 'improved_function'],
            'side_effects': [],
            'cost_estimate': round(random.uniform(100.0, 5000.0), 2),
            'evidence_level': random.choice(['Level I', 'Level II', 'Level III'])
        }

    def insert_sample_data(self, num_patients: int = 25):
        """Insert sample data into the database"""
        try:
            with self.connection.cursor() as cursor:
                # Insert patients
                print(f"Inserting {num_patients} sample patients...")
                for i in range(1, num_patients + 1):
                    patient_id = f"PATIENT_{i:03d}"
                    patient_data = self.generate_patient(patient_id)
                    
                    insert_patient_sql = """
                    INSERT INTO patients (
                        patient_id, first_name, last_name, age, gender,
                        genomics_data, biomarkers, medical_history, current_medications,
                        lifestyle_metrics, pain_scores, functional_assessments,
                        allergies, lab_results, vital_signs, comorbidities
                    ) VALUES (
                        %(patient_id)s, %(first_name)s, %(last_name)s, %(age)s, %(gender)s,
                        %(genomics_data)s, %(biomarkers)s, %(medical_history)s, %(current_medications)s,
                        %(lifestyle_metrics)s, %(pain_scores)s, %(functional_assessments)s,
                        %(allergies)s, %(lab_results)s, %(vital_signs)s, %(comorbidities)s
                    ) ON CONFLICT (patient_id) DO NOTHING
                    """
                    
                    cursor.execute(insert_patient_sql, {
                        **patient_data,
                        'genomics_data': Json(patient_data['genomics_data']),
                        'biomarkers': Json(patient_data['biomarkers']),
                        'lifestyle_metrics': Json(patient_data['lifestyle_metrics']),
                        'functional_assessments': Json(patient_data['functional_assessments']),
                        'lab_results': Json(patient_data['lab_results']),
                        'vital_signs': Json(patient_data['vital_signs'])
                    })
                    
                    # Insert 1-3 treatment plans per patient
                    treatment_count = random.randint(1, 3)
                    for j in range(1, treatment_count + 1):
                        treatment_id = f"TX_{i:03d}_{j:02d}"
                        treatment_data = self.generate_treatment_plan(patient_id, treatment_id)
                        
                        insert_treatment_sql = """
                        INSERT INTO treatment_plans (
                            treatment_id, patient_id, treatment_type, medications, dosages,
                            duration_weeks, lifestyle_interventions, notes, contraindications,
                            monitoring_requirements, expected_outcomes, side_effects,
                            cost_estimate, evidence_level
                        ) VALUES (
                            %(treatment_id)s, %(patient_id)s, %(treatment_type)s, %(medications)s, %(dosages)s,
                            %(duration_weeks)s, %(lifestyle_interventions)s, %(notes)s, %(contraindications)s,
                            %(monitoring_requirements)s, %(expected_outcomes)s, %(side_effects)s,
                            %(cost_estimate)s, %(evidence_level)s
                        ) ON CONFLICT (treatment_id) DO NOTHING
                        """
                        
                        cursor.execute(insert_treatment_sql, {
                            **treatment_data,
                            'dosages': Json(treatment_data['dosages'])
                        })
                        
                        # Generate a prediction for each treatment
                        success_prob = random.uniform(0.3, 0.9)
                        insert_prediction_sql = """
                        INSERT INTO predictions (
                            patient_id, treatment_id, success_probability, risk_score,
                            key_factors, warnings, confidence_interval_low, confidence_interval_high
                        ) VALUES (
                            %(patient_id)s, %(treatment_id)s, %(success_probability)s, %(risk_score)s,
                            %(key_factors)s, %(warnings)s, %(confidence_interval_low)s, %(confidence_interval_high)s
                        )
                        """
                        
                        cursor.execute(insert_prediction_sql, {
                            'patient_id': patient_id,
                            'treatment_id': treatment_id,
                            'success_probability': success_prob,
                            'risk_score': 1.0 - success_prob,
                            'key_factors': ['age', 'medical_history', 'genomics'],
                            'warnings': ['monitor_side_effects'] if success_prob < 0.6 else [],
                            'confidence_interval_low': max(0, success_prob - 0.15),
                            'confidence_interval_high': min(1, success_prob + 0.15)
                        })
                
                self.connection.commit()
                print(f"✅ Successfully inserted {num_patients} patients with treatments and predictions")
                
                # Generate some treatment outcomes
                print("Generating treatment outcomes...")
                cursor.execute("SELECT treatment_id, patient_id FROM treatment_plans LIMIT 15")
                treatments = cursor.fetchall()
                
                for treatment_id, patient_id in treatments:
                    if random.random() < 0.7:  # 70% have outcomes
                        success_rating = random.uniform(3.0, 9.0)
                        insert_outcome_sql = """
                        INSERT INTO treatment_outcomes (
                            patient_id, treatment_id, outcome_type, success_rating,
                            pain_reduction_percentage, side_effects_experienced,
                            patient_satisfaction, functional_improvement, notes
                        ) VALUES (
                            %(patient_id)s, %(treatment_id)s, %(outcome_type)s, %(success_rating)s,
                            %(pain_reduction_percentage)s, %(side_effects_experienced)s,
                            %(patient_satisfaction)s, %(functional_improvement)s, %(notes)s
                        )
                        """
                        
                        cursor.execute(insert_outcome_sql, {
                            'patient_id': patient_id,
                            'treatment_id': treatment_id,
                            'outcome_type': random.choice(['completed', 'ongoing', 'discontinued']),
                            'success_rating': success_rating,
                            'pain_reduction_percentage': random.uniform(10, 70),
                            'side_effects_experienced': random.sample(['nausea', 'dizziness', 'fatigue'], random.randint(0, 2)),
                            'patient_satisfaction': success_rating + random.uniform(-1, 1),
                            'functional_improvement': random.uniform(10, 60),
                            'notes': 'Patient reported improvement in daily activities'
                        })
                
                self.connection.commit()
                print("✅ Treatment outcomes generated successfully")
                
        except Exception as e:
            print(f"❌ Data insertion failed: {e}")
            self.connection.rollback()
            return False
        
        return True

    def display_sample_statistics(self):
        """Display statistics about the created sample data"""
        try:
            with self.connection.cursor() as cursor:
                # Patient statistics
                cursor.execute("SELECT COUNT(*) FROM patients")
                patient_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT AVG(age), MIN(age), MAX(age) FROM patients")
                age_stats = cursor.fetchone()
                
                cursor.execute("SELECT gender, COUNT(*) FROM patients GROUP BY gender")
                gender_stats = cursor.fetchall()
                
                # Treatment statistics
                cursor.execute("SELECT COUNT(*) FROM treatment_plans")
                treatment_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT treatment_type, COUNT(*) FROM treatment_plans GROUP BY treatment_type")
                treatment_type_stats = cursor.fetchall()
                
                # Prediction statistics
                cursor.execute("SELECT COUNT(*) FROM predictions")
                prediction_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT AVG(success_probability), MIN(success_probability), MAX(success_probability) FROM predictions")
                success_stats = cursor.fetchone()
                
                print("\n" + "="*60)
                print("📊 SAMPLE DATA STATISTICS")
                print("="*60)
                print(f"👥 Patients: {patient_count}")
                print(f"   Average Age: {age_stats[0]:.1f} (Range: {age_stats[1]}-{age_stats[2]})")
                print(f"   Gender Distribution:")
                for gender, count in gender_stats:
                    print(f"     {gender.title()}: {count}")
                
                print(f"\n💊 Treatment Plans: {treatment_count}")
                print(f"   Treatment Types:")
                for treatment_type, count in treatment_type_stats:
                    print(f"     {treatment_type.title()}: {count}")
                
                print(f"\n🔮 Predictions: {prediction_count}")
                print(f"   Success Probability: {success_stats[0]:.1%} (Range: {success_stats[1]:.1%}-{success_stats[2]:.1%})")
                
                cursor.execute("SELECT COUNT(*) FROM treatment_outcomes")
                outcome_count = cursor.fetchone()[0]
                print(f"\n📈 Treatment Outcomes: {outcome_count}")
                
                print("\n✅ Sample data creation completed successfully!")
                
        except Exception as e:
            print(f"❌ Statistics display failed: {e}")

    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("🔒 Database connection closed")


def main():
    """Main function to create sample data"""
    print("🏥 Abena IHR System - Sample Data Generator")
    print("=" * 50)
    
    generator = SampleDataGenerator()
    
    # Connect to database
    if not generator.connect_database():
        return False
    
    # Create tables
    if not generator.create_tables():
        generator.close_connection()
        return False
    
    # Insert sample data
    if not generator.insert_sample_data(num_patients=25):
        generator.close_connection()
        return False
    
    # Display statistics
    generator.display_sample_statistics()
    
    # Close connection
    generator.close_connection()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 