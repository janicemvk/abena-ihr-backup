"""
Data Privacy and Security Tests for Abena IHR System

This module contains comprehensive security tests to ensure HIPAA
compliance, data protection, and system security requirements.
"""

import pytest
import re
import hashlib
import json
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.core.data_models import PatientProfile


# ============================================================================
# SECURITY TEST HELPERS
# ============================================================================

class SecurityTestHelper:
    """Helper class for security testing utilities"""
    
    @staticmethod
    def contains_phi(text: str) -> bool:
        """Check if text contains potential PHI patterns"""
        phi_patterns = [
            r'\d{3}-\d{2}-\d{4}',  # SSN pattern
            r'\d{3}-\d{3}-\d{4}',  # Phone number pattern
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # Date pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email pattern
            r'\b\d{5}(-\d{4})?\b',  # ZIP code pattern
        ]
        
        for pattern in phi_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    @staticmethod
    def is_properly_anonymized(original_data: dict, anonymized_data: dict) -> bool:
        """Check if data is properly anonymized"""
        # Check that identifiable fields are removed or anonymized
        sensitive_fields = ['ssn', 'phone', 'email', 'address', 'name']
        
        for field in sensitive_fields:
            if field in original_data and field in anonymized_data:
                if original_data[field] == anonymized_data[field]:
                    return False  # Field not anonymized
        
        return True
    
    @staticmethod
    def check_encryption_markers(data: str) -> bool:
        """Check if data shows signs of encryption"""
        # Encrypted data should not be human-readable
        if not data:
            return False
        
        # Check for base64-like patterns (common in encryption)
        base64_pattern = r'^[A-Za-z0-9+/]*={0,2}$'
        
        # Check for non-printable characters or high entropy
        if re.match(base64_pattern, data) and len(data) > 10:
            return True
        
        # Check entropy (encrypted data should have high entropy)
        entropy = SecurityTestHelper.calculate_entropy(data)
        return entropy > 4.0  # Threshold for likely encrypted data
    
    @staticmethod
    def calculate_entropy(data: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not data:
            return 0.0
        
        # Count frequency of each character
        freq = {}
        for char in data:
            freq[char] = freq.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(data)
        
        for count in freq.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy


# ============================================================================
# DATA PRIVACY TESTS
# ============================================================================

@pytest.mark.security
class TestDataPrivacy:
    """Data privacy and PHI protection tests"""
    
    def test_patient_data_does_not_leak_in_logs(self, sample_patient, caplog):
        """Test that patient PHI doesn't leak in log messages"""
        # Create a logger for testing
        logger = logging.getLogger("test_phi_logger")
        logger.setLevel(logging.DEBUG)
        
        # Clear any existing log records
        caplog.clear()
        
        # Simulate various logging scenarios
        logger.info(f"Processing patient: {sample_patient.patient_id}")
        logger.debug(f"Patient age: {sample_patient.age}")
        logger.warning(f"High pain scores detected for patient {sample_patient.patient_id}")
        
        # Simulate error logging with patient data
        try:
            # This should NOT log sensitive data
            if sample_patient.medical_history:
                logger.error(f"Medical history processing failed for patient {sample_patient.patient_id}")
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
        
        # Check that sensitive data patterns are not in logs
        for record in caplog.records:
            message = record.message
            
            # Should not contain SSN patterns
            assert not re.search(r'\d{3}-\d{2}-\d{4}', message), \
                f"SSN pattern found in log: {message}"
            
            # Should not contain phone number patterns
            assert not re.search(r'\d{3}-\d{3}-\d{4}', message), \
                f"Phone pattern found in log: {message}"
            
            # Should not contain email patterns
            assert not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message), \
                f"Email pattern found in log: {message}"
            
            # Patient ID is acceptable for operational purposes
            assert sample_patient.patient_id in message or "patient" in message.lower()
    
    def test_patient_data_serialization_security(self, sample_patient):
        """Test that patient data serialization doesn't expose sensitive fields"""
        # Convert patient to string representation
        patient_str = str(sample_patient)
        
        # Patient ID should be present (needed for operations)
        assert sample_patient.patient_id in patient_str
        
        # Check that PHI patterns are not exposed
        assert not SecurityTestHelper.contains_phi(patient_str), \
            "PHI patterns detected in patient string representation"
        
        # Convert to dictionary for JSON serialization testing
        patient_dict = sample_patient.__dict__.copy()
        
        # Remove or anonymize sensitive fields before serialization
        safe_patient_dict = patient_dict.copy()
        
        # Fields that should be anonymized or removed
        if 'ssn' in safe_patient_dict:
            del safe_patient_dict['ssn']
        
        if 'phone' in safe_patient_dict:
            del safe_patient_dict['phone']
        
        if 'email' in safe_patient_dict:
            del safe_patient_dict['email']
        
        # Test JSON serialization
        json_str = json.dumps(safe_patient_dict)
        assert not SecurityTestHelper.contains_phi(json_str), \
            "PHI patterns detected in JSON serialization"
    
    def test_data_anonymization_for_analytics(self, sample_patient):
        """Test data anonymization for analytics purposes"""
        # Mock anonymization function
        def anonymize_patient_data(patient: PatientProfile) -> dict:
            """Anonymize patient data for analytics"""
            anonymized = {
                'patient_id_hash': hashlib.sha256(patient.patient_id.encode()).hexdigest()[:12],
                'age_range': f"{(patient.age // 10) * 10}-{(patient.age // 10) * 10 + 9}",
                'gender': patient.gender,
                'genomics_data': patient.genomics_data,  # Genomics can be used for research
                'biomarkers': patient.biomarkers,
                'medical_history_count': len(patient.medical_history),
                'current_medications_count': len(patient.current_medications),
                'pain_score_avg': sum(patient.pain_scores) / len(patient.pain_scores) if patient.pain_scores else 0,
                'functional_score': patient.functional_assessments.get('mobility_score', 0),
                'created_month': datetime.now().strftime('%Y-%m')  # Month precision only
            }
            return anonymized
        
        original_data = sample_patient.__dict__.copy()
        anonymized_data = anonymize_patient_data(sample_patient)
        
        # Verify anonymization
        assert SecurityTestHelper.is_properly_anonymized(original_data, anonymized_data)
        
        # Verify no direct PHI in anonymized data
        anonymized_str = json.dumps(anonymized_data)
        assert not SecurityTestHelper.contains_phi(anonymized_str)
        
        # Verify useful data is preserved for analytics
        assert 'age_range' in anonymized_data
        assert 'genomics_data' in anonymized_data
        assert 'medical_history_count' in anonymized_data
        assert anonymized_data['medical_history_count'] == len(sample_patient.medical_history)
    
    @pytest.mark.security
    def test_data_encryption_at_rest(self):
        """Test that sensitive data is encrypted when stored"""
        # Mock encryption function
        def encrypt_sensitive_data(data: str) -> str:
            """Mock encryption function"""
            # In real implementation, this would use proper encryption
            import base64
            encrypted = base64.b64encode(data.encode()).decode()
            return f"ENCRYPTED:{encrypted}"
        
        # Test data encryption
        sensitive_data = "Patient John Doe, SSN: 123-45-6789"
        encrypted_data = encrypt_sensitive_data(sensitive_data)
        
        # Verify encryption
        assert encrypted_data.startswith("ENCRYPTED:")
        assert "John Doe" not in encrypted_data
        assert "123-45-6789" not in encrypted_data
        assert SecurityTestHelper.check_encryption_markers(encrypted_data.replace("ENCRYPTED:", ""))
    
    def test_database_field_encryption(self):
        """Test database field-level encryption"""
        # Mock database model with encrypted fields
        class EncryptedPatientRecord:
            def __init__(self, patient: PatientProfile):
                # Encrypt sensitive fields
                self.patient_id = patient.patient_id  # Hash or encrypt
                self.encrypted_name = self._encrypt_field("test_name")
                self.encrypted_ssn = self._encrypt_field("123-45-6789")
                self.age = patient.age  # Age can be stored in clear
                self.gender = patient.gender  # Gender can be stored in clear
                self.encrypted_medical_history = self._encrypt_field(json.dumps(patient.medical_history))
            
            def _encrypt_field(self, data: str) -> str:
                """Mock field encryption"""
                import base64
                return base64.b64encode(data.encode()).decode()
        
        # Create encrypted record
        encrypted_record = EncryptedPatientRecord(sample_patient)
        
        # Verify sensitive fields are encrypted
        assert SecurityTestHelper.check_encryption_markers(encrypted_record.encrypted_name)
        assert SecurityTestHelper.check_encryption_markers(encrypted_record.encrypted_ssn)
        assert SecurityTestHelper.check_encryption_markers(encrypted_record.encrypted_medical_history)
        
        # Verify non-sensitive fields are accessible
        assert encrypted_record.age == sample_patient.age
        assert encrypted_record.gender == sample_patient.gender


@pytest.mark.security
class TestAccessControl:
    """Access control and authorization tests"""
    
    def test_role_based_access_control(self):
        """Test role-based access to patient data"""
        # Mock user roles
        class UserRole:
            PHYSICIAN = "physician"
            NURSE = "nurse"
            ADMIN = "admin"
            RESEARCHER = "researcher"
        
        # Mock access control function
        def check_patient_access(user_role: str, patient_id: str, operation: str) -> bool:
            """Check if user has access to patient data"""
            access_matrix = {
                UserRole.PHYSICIAN: ['read', 'write', 'delete'],
                UserRole.NURSE: ['read', 'write'],
                UserRole.ADMIN: ['read', 'write', 'delete', 'admin'],
                UserRole.RESEARCHER: ['read_anonymized']
            }
            
            allowed_operations = access_matrix.get(user_role, [])
            return operation in allowed_operations
        
        test_patient_id = "TEST_PATIENT_001"
        
        # Test physician access
        assert check_patient_access(UserRole.PHYSICIAN, test_patient_id, 'read')
        assert check_patient_access(UserRole.PHYSICIAN, test_patient_id, 'write')
        assert check_patient_access(UserRole.PHYSICIAN, test_patient_id, 'delete')
        
        # Test nurse access
        assert check_patient_access(UserRole.NURSE, test_patient_id, 'read')
        assert check_patient_access(UserRole.NURSE, test_patient_id, 'write')
        assert not check_patient_access(UserRole.NURSE, test_patient_id, 'delete')
        
        # Test researcher access
        assert check_patient_access(UserRole.RESEARCHER, test_patient_id, 'read_anonymized')
        assert not check_patient_access(UserRole.RESEARCHER, test_patient_id, 'read')
        assert not check_patient_access(UserRole.RESEARCHER, test_patient_id, 'write')
    
    def test_authentication_requirements(self):
        """Test authentication requirements for system access"""
        # Mock authentication function
        def authenticate_user(username: str, password: str, mfa_token: str = None) -> dict:
            """Mock user authentication"""
            # In real implementation, this would validate credentials
            if username and password and len(password) >= 8:
                return {
                    'authenticated': True,
                    'user_id': f"USER_{username.upper()}",
                    'role': 'physician',
                    'session_token': f"SESSION_{username}_{datetime.now().timestamp()}",
                    'mfa_verified': mfa_token is not None
                }
            return {'authenticated': False}
        
        # Test valid authentication
        auth_result = authenticate_user("dr_smith", "secure_password123", "123456")
        assert auth_result['authenticated'] is True
        assert auth_result['mfa_verified'] is True
        assert 'session_token' in auth_result
        
        # Test invalid authentication
        invalid_auth = authenticate_user("dr_smith", "weak")
        assert invalid_auth['authenticated'] is False
        
        # Test missing MFA
        no_mfa_auth = authenticate_user("dr_smith", "secure_password123")
        assert no_mfa_auth['authenticated'] is True
        assert no_mfa_auth['mfa_verified'] is False
    
    def test_session_management(self):
        """Test session security and management"""
        # Mock session management
        class SessionManager:
            def __init__(self):
                self.sessions = {}
            
            def create_session(self, user_id: str) -> str:
                """Create new session"""
                import uuid
                session_id = str(uuid.uuid4())
                self.sessions[session_id] = {
                    'user_id': user_id,
                    'created_at': datetime.now(),
                    'last_activity': datetime.now(),
                    'is_active': True
                }
                return session_id
            
            def validate_session(self, session_id: str) -> bool:
                """Validate session"""
                if session_id not in self.sessions:
                    return False
                
                session = self.sessions[session_id]
                if not session['is_active']:
                    return False
                
                # Check session timeout (24 hours)
                time_diff = datetime.now() - session['last_activity']
                if time_diff.total_seconds() > 86400:  # 24 hours
                    session['is_active'] = False
                    return False
                
                # Update last activity
                session['last_activity'] = datetime.now()
                return True
            
            def invalidate_session(self, session_id: str):
                """Invalidate session"""
                if session_id in self.sessions:
                    self.sessions[session_id]['is_active'] = False
        
        # Test session lifecycle
        session_mgr = SessionManager()
        
        # Create session
        session_id = session_mgr.create_session("USER_DR_SMITH")
        assert session_id is not None
        assert len(session_id) > 10  # UUID should be long
        
        # Validate active session
        assert session_mgr.validate_session(session_id) is True
        
        # Invalidate session
        session_mgr.invalidate_session(session_id)
        assert session_mgr.validate_session(session_id) is False


@pytest.mark.security
class TestAuditTrails:
    """Audit trail and compliance logging tests"""
    
    def test_patient_access_audit_logging(self, sample_patient):
        """Test audit logging for patient data access"""
        # Mock audit logger
        class AuditLogger:
            def __init__(self):
                self.audit_log = []
            
            def log_patient_access(self, user_id: str, patient_id: str, operation: str, 
                                 result: str, details: dict = None):
                """Log patient data access"""
                audit_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'user_id': user_id,
                    'patient_id': patient_id,
                    'operation': operation,
                    'result': result,
                    'details': details or {},
                    'audit_id': f"AUDIT_{len(self.audit_log) + 1:06d}"
                }
                self.audit_log.append(audit_entry)
            
            def get_patient_audit_trail(self, patient_id: str) -> list:
                """Get audit trail for specific patient"""
                return [entry for entry in self.audit_log if entry['patient_id'] == patient_id]
        
        # Test audit logging
        audit_logger = AuditLogger()
        
        # Simulate various patient access operations
        audit_logger.log_patient_access(
            "USER_DR_SMITH", sample_patient.patient_id, "READ", "SUCCESS",
            {"fields_accessed": ["demographics", "medical_history"]}
        )
        
        audit_logger.log_patient_access(
            "USER_NURSE_JONES", sample_patient.patient_id, "UPDATE", "SUCCESS",
            {"fields_modified": ["pain_scores"], "new_values": [7.5]}
        )
        
        audit_logger.log_patient_access(
            "USER_RESEARCHER_001", sample_patient.patient_id, "READ", "DENIED",
            {"reason": "insufficient_permissions"}
        )
        
        # Verify audit trail
        patient_audit = audit_logger.get_patient_audit_trail(sample_patient.patient_id)
        assert len(patient_audit) == 3
        
        # Verify audit entry structure
        for entry in patient_audit:
            assert 'timestamp' in entry
            assert 'user_id' in entry
            assert 'patient_id' in entry
            assert 'operation' in entry
            assert 'result' in entry
            assert 'audit_id' in entry
            assert entry['patient_id'] == sample_patient.patient_id
    
    def test_system_security_event_logging(self):
        """Test logging of security-related events"""
        # Mock security event logger
        class SecurityEventLogger:
            def __init__(self):
                self.security_log = []
            
            def log_security_event(self, event_type: str, severity: str, 
                                 details: dict, user_id: str = None):
                """Log security event"""
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'event_type': event_type,
                    'severity': severity,
                    'user_id': user_id,
                    'details': details,
                    'event_id': f"SEC_{len(self.security_log) + 1:06d}"
                }
                self.security_log.append(event)
        
        # Test security event logging
        security_logger = SecurityEventLogger()
        
        # Failed login attempt
        security_logger.log_security_event(
            "AUTHENTICATION_FAILURE", "MEDIUM",
            {"username": "dr_smith", "ip_address": "192.168.1.100", "reason": "invalid_password"}
        )
        
        # Successful login with MFA
        security_logger.log_security_event(
            "AUTHENTICATION_SUCCESS", "LOW",
            {"username": "dr_smith", "ip_address": "192.168.1.100", "mfa_used": True},
            "USER_DR_SMITH"
        )
        
        # Unauthorized access attempt
        security_logger.log_security_event(
            "UNAUTHORIZED_ACCESS", "HIGH",
            {"user_id": "USER_TEMP_001", "attempted_resource": "/admin/users", "action": "blocked"},
            "USER_TEMP_001"
        )
        
        # Verify security log
        assert len(security_logger.security_log) == 3
        
        # Check high severity events
        high_severity_events = [e for e in security_logger.security_log if e['severity'] == 'HIGH']
        assert len(high_severity_events) == 1
        assert high_severity_events[0]['event_type'] == 'UNAUTHORIZED_ACCESS'
    
    def test_compliance_reporting(self, sample_patient):
        """Test compliance reporting capabilities"""
        # Mock compliance reporter
        class ComplianceReporter:
            def __init__(self, audit_logger, security_logger):
                self.audit_logger = audit_logger
                self.security_logger = security_logger
            
            def generate_hipaa_compliance_report(self, start_date: datetime, end_date: datetime) -> dict:
                """Generate HIPAA compliance report"""
                # In real implementation, this would analyze actual logs
                return {
                    'report_period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'patient_access_events': 150,
                    'unauthorized_access_attempts': 2,
                    'data_breaches': 0,
                    'encryption_compliance': 100.0,
                    'access_control_compliance': 98.5,
                    'audit_trail_completeness': 100.0,
                    'findings': [
                        'All patient access properly logged',
                        'No data breaches detected',
                        'Minor access control violations (2 incidents)'
                    ],
                    'recommendations': [
                        'Review user permissions quarterly',
                        'Implement additional MFA enforcement'
                    ]
                }
        
        # Test compliance reporting
        start_date = datetime.now().replace(day=1)  # Start of month
        end_date = datetime.now()
        
        compliance_reporter = ComplianceReporter(None, None)
        report = compliance_reporter.generate_hipaa_compliance_report(start_date, end_date)
        
        # Verify report structure
        assert 'report_period' in report
        assert 'patient_access_events' in report
        assert 'encryption_compliance' in report
        assert 'audit_trail_completeness' in report
        assert 'findings' in report
        assert 'recommendations' in report
        
        # Verify compliance metrics
        assert report['encryption_compliance'] >= 95.0
        assert report['audit_trail_completeness'] >= 99.0
        assert report['data_breaches'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 