"""
Database Integration Example for Abena Secure Data Triage Algorithm
This shows how the algorithm works WITH databases, not against them.
"""

import sqlite3
import json
from secure_data_triage_algorithm import DataTriageEngine

class AbenaDatabase:
    """Example database integration with the triage algorithm"""
    
    def __init__(self, db_path="abena_healthcare.db"):
        self.db_path = db_path
        self.triage_engine = DataTriageEngine()
        self.setup_database()
    
    def setup_database(self):
        """Create database tables for different sensitivity levels"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for public/statistical data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS public_data (
                id INTEGER PRIMARY KEY,
                triage_id TEXT UNIQUE,
                data_json TEXT,
                timestamp TEXT,
                sensitivity_level TEXT
            )
        ''')
        
        # Table for clinical data (anonymized)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clinical_data (
                id INTEGER PRIMARY KEY,
                triage_id TEXT UNIQUE,
                encrypted_data TEXT,
                anonymization_method TEXT,
                timestamp TEXT,
                k_anonymity_level INTEGER
            )
        ''')
        
        # Table for identified patient data (high security)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS identified_vault (
                id INTEGER PRIMARY KEY,
                triage_id TEXT UNIQUE,
                encrypted_data TEXT,
                patient_consent_hash TEXT,
                timestamp TEXT,
                access_log TEXT
            )
        ''')
        
        # Audit trail table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY,
                triage_id TEXT,
                original_hash TEXT,
                processed_hash TEXT,
                actions_taken TEXT,
                compliance_flags TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_healthcare_data(self, raw_data, patient_consent):
        """
        Process data through triage algorithm and store in appropriate database table
        """
        # Step 1: Process through triage algorithm
        triage_result = self.triage_engine.triage_data(raw_data, patient_consent)
        
        # Step 2: Store in appropriate database table based on sensitivity
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if triage_result['storage_destination'] == 'statistical':
                # Store in public data table
                cursor.execute('''
                    INSERT INTO public_data 
                    (triage_id, data_json, timestamp, sensitivity_level)
                    VALUES (?, ?, ?, ?)
                ''', (
                    triage_result['triage_id'],
                    json.dumps(triage_result['secured_data']),
                    triage_result['timestamp'],
                    triage_result['sensitivity_level']
                ))
                
            elif triage_result['storage_destination'] == 'anonymous':
                # Store in clinical data table
                cursor.execute('''
                    INSERT INTO clinical_data 
                    (triage_id, encrypted_data, anonymization_method, timestamp, k_anonymity_level)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    triage_result['triage_id'],
                    json.dumps(triage_result['secured_data']),
                    triage_result['security_measures_applied']['method'],
                    triage_result['timestamp'],
                    triage_result['security_measures_applied']['k_anonymity']
                ))
                
            elif triage_result['storage_destination'] == 'identified':
                # Store in identified vault
                cursor.execute('''
                    INSERT INTO identified_vault 
                    (triage_id, encrypted_data, patient_consent_hash, timestamp, access_log)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    triage_result['triage_id'],
                    json.dumps(triage_result['secured_data']),
                    self.triage_engine._hash_data(patient_consent),
                    triage_result['timestamp'],
                    json.dumps([{"action": "initial_storage", "timestamp": triage_result['timestamp']}])
                ))
            
            # Always store audit trail
            cursor.execute('''
                INSERT INTO audit_trail 
                (triage_id, original_hash, processed_hash, actions_taken, compliance_flags, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                triage_result['triage_id'],
                triage_result['original_data_hash'],
                triage_result['audit_entry']['secured_data_hash'],
                json.dumps(triage_result['audit_entry']['processing_steps']),
                json.dumps(triage_result['audit_entry']['compliance_flags']),
                triage_result['timestamp']
            ))
            
            conn.commit()
            print(f"✅ Data stored successfully: {triage_result['triage_id']}")
            print(f"   Sensitivity: {triage_result['sensitivity_level']}")
            print(f"   Destination: {triage_result['storage_destination']}")
            
            return triage_result
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error storing data: {e}")
            return None
        finally:
            conn.close()
    
    def retrieve_data_securely(self, triage_id, user_permissions):
        """
        Retrieve data with security checks based on user permissions
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check all tables for the triage ID
        tables = ['public_data', 'clinical_data', 'identified_vault']
        
        for table in tables:
            cursor.execute(f'SELECT * FROM {table} WHERE triage_id = ?', (triage_id,))
            result = cursor.fetchone()
            
            if result:
                # Apply access control based on table and user permissions
                if table == 'public_data' and user_permissions.get('access_public', False):
                    return {'status': 'granted', 'data': result, 'table': table}
                elif table == 'clinical_data' and user_permissions.get('access_clinical', False):
                    return {'status': 'granted', 'data': result, 'table': table}
                elif table == 'identified_vault' and user_permissions.get('access_identified', False):
                    return {'status': 'granted', 'data': result, 'table': table}
                else:
                    return {'status': 'denied', 'reason': 'Insufficient permissions', 'table': table}
        
        conn.close()
        return {'status': 'not_found', 'reason': 'Triage ID not found'}

# Example usage
def demonstrate_database_integration():
    """Demonstrate how the triage algorithm works WITH databases"""
    
    print("🏥 Abena Database Integration Demonstration\n")
    
    # Initialize database with triage integration
    db = AbenaDatabase()
    
    # Example 1: Store IoT sensor data
    iot_data = {
        'device_id': 'SENSOR_001',
        'patient_id': 'P789',
        'heart_rate': 75,
        'timestamp': '2024-01-15T10:00:00Z'
    }
    
    iot_consent = {
        'general_data_use': True,
        'anonymous_research': True,
        'clinical_research': False,
        'identified_storage': False,
        'sensitive_data_storage': False
    }
    
    print("1. Storing IoT sensor data...")
    result1 = db.store_healthcare_data(iot_data, iot_consent)
    
    # Example 2: Store sensitive clinical notes
    clinical_data = {
        'patient_name': 'John Smith',
        'ssn': '123-45-6789',
        'diagnosis': 'Depression with anxiety',
        'notes': 'Patient shows significant improvement'
    }
    
    clinical_consent = {
        'general_data_use': True,
        'anonymous_research': True,
        'clinical_research': True,
        'identified_storage': True,
        'sensitive_data_storage': True
    }
    
    print("\n2. Storing sensitive clinical data...")
    result2 = db.store_healthcare_data(clinical_data, clinical_consent)
    
    # Example 3: Retrieve data with proper permissions
    print("\n3. Testing data retrieval with permissions...")
    
    # Researcher permissions (can access public and clinical data)
    researcher_permissions = {
        'access_public': True,
        'access_clinical': True,
        'access_identified': False
    }
    
    if result1:
        retrieval = db.retrieve_data_securely(result1['triage_id'], researcher_permissions)
        print(f"   Researcher access to IoT data: {retrieval['status']}")
    
    # Doctor permissions (full access)
    doctor_permissions = {
        'access_public': True,
        'access_clinical': True,
        'access_identified': True
    }
    
    if result2:
        retrieval = db.retrieve_data_securely(result2['triage_id'], doctor_permissions)
        print(f"   Doctor access to clinical data: {retrieval['status']}")

if __name__ == "__main__":
    demonstrate_database_integration() 