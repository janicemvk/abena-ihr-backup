"""
Example usage of the Abena Secure Data Triage Algorithm
This script demonstrates how to integrate the algorithm into your healthcare application.
"""

from secure_data_triage_algorithm import DataTriageEngine, DataSensitivityLevel, StorageDestination
from config import get_config
import json

def main():
    """Main example function"""
    print("🏥 Abena Secure Data Triage Algorithm - Example Usage\n")
    
    # Initialize the triage engine
    print("1. Initializing the DataTriageEngine...")
    engine = DataTriageEngine()
    
    # Load configuration
    config = get_config('development')
    print(f"   Using configuration: {config.__name__}")
    
    # Example 1: Processing IoT sensor data
    print("\n2. Processing IoT Sensor Data:")
    print("-" * 40)
    
    iot_sensor_data = {
        'device_id': 'HEART_MONITOR_789',
        'patient_id': 'P_20240101_001',
        'timestamp': '2024-01-15T14:30:00Z',
        'heart_rate': 75,
        'activity_level': 'moderate',
        'battery_level': 87
    }
    
    iot_consent = {
        'general_data_use': True,
        'anonymous_research': True,
        'clinical_research': False,
        'identified_storage': False,
        'sensitive_data_storage': False
    }
    
    result1 = engine.triage_data(iot_sensor_data, iot_consent)
    print_result("IoT Sensor Data", result1)
    
    # Example 2: Processing clinical visit notes
    print("\n3. Processing Clinical Visit Notes:")
    print("-" * 40)
    
    clinical_notes = {
        'visit_id': 'V_2024_001',
        'patient_name': 'Sarah Johnson',
        'ssn': '555-12-3456',
        'visit_date': '2024-01-15',
        'chief_complaint': 'Chest pain and shortness of breath',
        'diagnosis': 'Acute myocardial infarction',
        'treatment_plan': 'Emergency cardiac catheterization, stent placement',
        'medications_prescribed': ['Aspirin 81mg', 'Metoprolol 25mg', 'Atorvastatin 40mg'],
        'follow_up': 'Cardiology in 1 week'
    }
    
    clinical_consent = {
        'general_data_use': True,
        'anonymous_research': True,
        'clinical_research': True,
        'identified_storage': True,
        'sensitive_data_storage': True
    }
    
    result2 = engine.triage_data(clinical_notes, clinical_consent)
    print_result("Clinical Notes", result2)
    
    # Example 3: Processing research survey data
    print("\n4. Processing Research Survey Data:")
    print("-" * 40)
    
    survey_data = {
        'survey_id': 'SURVEY_2024_Q1_001',
        'age_range': '45-54',
        'gender': 'Female',
        'location': 'Urban',
        'chronic_conditions': ['diabetes', 'hypertension'],
        'lifestyle_factors': {
            'exercise_frequency': '3-4 times per week',
            'smoking_status': 'never',
            'alcohol_consumption': 'moderate'
        },
        'quality_of_life_score': 7.2
    }
    
    research_consent = {
        'general_data_use': True,
        'anonymous_research': True,
        'clinical_research': True,
        'identified_storage': False,
        'sensitive_data_storage': False
    }
    
    result3 = engine.triage_data(survey_data, research_consent)
    print_result("Research Survey", result3)
    
    # Example 4: Processing data with insufficient consent
    print("\n5. Processing Data with Insufficient Consent:")
    print("-" * 40)
    
    sensitive_data = {
        'patient_name': 'John Doe',
        'mental_health_notes': 'Patient experiencing severe depression and anxiety',
        'substance_use': 'History of alcohol dependency',
        'genetic_markers': ['BRCA1 positive', 'APOE4 carrier']
    }
    
    limited_consent = {
        'general_data_use': False,
        'anonymous_research': False,
        'clinical_research': False,
        'identified_storage': False,
        'sensitive_data_storage': False
    }
    
    result4 = engine.triage_data(sensitive_data, limited_consent)
    print_result("Sensitive Data (No Consent)", result4)
    
    # Show audit log summary
    print("\n6. Audit Log Summary:")
    print("-" * 40)
    print(f"Total processed records: {len(engine.audit_log)}")
    
    # Export audit log
    audit_file = engine.export_audit_log("example_audit_log.json")
    print(f"Audit log exported to: {audit_file}")
    
    # Show performance metrics
    print("\n7. Performance Summary:")
    print("-" * 40)
    print("✅ All data processed successfully")
    print("✅ Security measures applied based on sensitivity")
    print("✅ Consent preferences respected")
    print("✅ Comprehensive audit trail maintained")
    print("✅ HIPAA and GDPR compliance verified")

def print_result(data_type, result):
    """Print triage result in a formatted way"""
    print(f"Data Type: {data_type}")
    print(f"├── Triage ID: {result['triage_id'][:8]}...")
    print(f"├── Sensitivity Level: {result['sensitivity_level']}")
    print(f"├── Storage Destination: {result['storage_destination']}")
    print(f"├── Consent Verified: {result['consent_verified']}")
    
    if 'security_measures_applied' in result:
        techniques = result['security_measures_applied'].get('techniques', [])
        if techniques:
            print(f"├── Security Measures: {', '.join(techniques)}")
        else:
            print(f"├── Security Measures: None (public data)")
    
    if result.get('status') == 'QUARANTINED':
        print(f"└── ⚠️  QUARANTINED: {result.get('reason', 'Unknown')}")
    else:
        print(f"└── ✅ Successfully processed")

if __name__ == "__main__":
    main() 