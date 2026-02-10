#!/usr/bin/env python3
"""
Simple Sample Data Creation Script for Abena IHR System
Creates realistic test data without complex imports.
"""

import random
import psycopg2
from datetime import datetime

# Database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'abena_ihr',
    'user': 'abena_user',
    'password': 'EKZz4h%*6yyH$WqK',
    'port': 5432
}

def create_sample_data():
    """Create sample data for testing"""
    
    # Sample data lists
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    medical_conditions = ["chronic_pain", "fibromyalgia", "arthritis", "diabetes", "hypertension"]
    medications = ["ibuprofen", "acetaminophen", "gabapentin", "pregabalin", "tramadol"]
    treatment_types = ["pharmacological", "behavioral", "combined", "interventional"]
    
    try:
        # Connect to database
        connection = psycopg2.connect(**DATABASE_CONFIG)
        print("✅ Connected to database successfully")
        
        with connection.cursor() as cursor:
            # Create tables
            print("Creating database tables...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id VARCHAR(50) PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    age INTEGER NOT NULL CHECK (age >= 0 AND age <= 120),
                    gender VARCHAR(20) NOT NULL,
                    medical_history TEXT[] DEFAULT '{}',
                    current_medications TEXT[] DEFAULT '{}',
                    pain_scores REAL[] DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS treatment_plans (
                    treatment_id VARCHAR(50) PRIMARY KEY,
                    patient_id VARCHAR(50) REFERENCES patients(patient_id),
                    treatment_type VARCHAR(50) NOT NULL,
                    medications TEXT[] DEFAULT '{}',
                    duration_weeks INTEGER NOT NULL CHECK (duration_weeks > 0),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS predictions (
                    prediction_id SERIAL PRIMARY KEY,
                    patient_id VARCHAR(50) REFERENCES patients(patient_id),
                    treatment_id VARCHAR(50) REFERENCES treatment_plans(treatment_id),
                    success_probability REAL NOT NULL CHECK (success_probability >= 0 AND success_probability <= 1),
                    risk_score REAL NOT NULL CHECK (risk_score >= 0 AND risk_score <= 1),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert sample patients
            print("Inserting sample patients...")
            for i in range(1, 26):  # 25 patients
                patient_id = f"PATIENT_{i:03d}"
                age = random.randint(25, 80)
                gender = random.choice(['male', 'female'])
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                # Generate medical history
                history_count = random.randint(1, 3)
                medical_history = random.sample(medical_conditions, history_count)
                
                # Generate current medications
                med_count = random.randint(0, 4)
                current_meds = random.sample(medications, med_count)
                
                # Generate pain scores
                pain_scores = []
                for _ in range(random.randint(3, 8)):
                    pain_scores.append(round(random.uniform(3.0, 9.0), 1))
                
                cursor.execute("""
                    INSERT INTO patients (patient_id, first_name, last_name, age, gender, 
                                        medical_history, current_medications, pain_scores)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (patient_id) DO NOTHING
                """, (patient_id, first_name, last_name, age, gender, 
                     medical_history, current_meds, pain_scores))
                
                # Create 1-2 treatment plans per patient
                for j in range(1, random.randint(2, 4)):
                    treatment_id = f"TX_{i:03d}_{j:02d}"
                    treatment_type = random.choice(treatment_types)
                    duration = random.randint(4, 20)
                    
                    # Generate treatment medications
                    treatment_meds = random.sample(medications, random.randint(1, 3))
                    notes = f"Treatment plan for {treatment_type} approach"
                    
                    cursor.execute("""
                        INSERT INTO treatment_plans (treatment_id, patient_id, treatment_type, 
                                                   medications, duration_weeks, notes)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (treatment_id) DO NOTHING
                    """, (treatment_id, patient_id, treatment_type, treatment_meds, duration, notes))
                    
                    # Generate prediction for this treatment
                    success_prob = random.uniform(0.3, 0.9)
                    risk_score = 1.0 - success_prob
                    
                    cursor.execute("""
                        INSERT INTO predictions (patient_id, treatment_id, success_probability, risk_score)
                        VALUES (%s, %s, %s, %s)
                    """, (patient_id, treatment_id, success_prob, risk_score))
            
            connection.commit()
            print(f"✅ Successfully created sample data!")
            
            # Display statistics
            cursor.execute("SELECT COUNT(*) FROM patients")
            patient_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM treatment_plans")
            treatment_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM predictions")
            prediction_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(success_probability)::NUMERIC(4,3) FROM predictions")
            avg_success = cursor.fetchone()[0]
            
            print(f"\n📊 SAMPLE DATA CREATED:")
            print(f"👥 Patients: {patient_count}")
            print(f"💊 Treatment Plans: {treatment_count}")
            print(f"🔮 Predictions: {prediction_count}")
            print(f"📈 Average Success Probability: {float(avg_success):.1%}")
            
            # Show a few sample patients
            print(f"\n📋 Sample Patients:")
            cursor.execute("""
                SELECT patient_id, first_name, last_name, age, gender, 
                       array_length(medical_history, 1) as conditions_count
                FROM patients LIMIT 5
            """)
            
            for row in cursor.fetchall():
                pid, fname, lname, age, gender, conditions = row
                conditions_count = conditions or 0
                print(f"   {pid}: {fname} {lname}, {age}yo {gender}, {conditions_count} conditions")
            
            print(f"\n🎯 Ready for application testing!")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Abena IHR System - Simple Sample Data Generator")
    print("=" * 55)
    success = create_sample_data()
    exit(0 if success else 1) 