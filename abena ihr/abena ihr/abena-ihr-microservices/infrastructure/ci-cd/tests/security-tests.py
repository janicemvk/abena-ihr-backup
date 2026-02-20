#!/usr/bin/env python3
"""
Abena IHR Security Tests
Healthcare microservices security testing
"""

import pytest
import requests
import json
import time
import os
import base64
import hashlib
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "https://api.abena-ihr.com")
API_VERSION = "v1"
TIMEOUT = 30

@dataclass
class SecurityTest:
    """Security test configuration"""
    name: str
    description: str
    severity: str  # low, medium, high, critical
    category: str  # auth, authorization, data_protection, compliance, encryption

class AbenaIHRSecurityTests:
    """Security tests for Abena IHR microservices"""
    
    def __init__(self):
        self.base_url = f"{BASE_URL}/api/{API_VERSION}"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Test results
        self.test_results = []
        
        # Test users
        self.test_users = {
            "patient": {
                "email": "patient.security@abena-ihr.com",
                "password": "SecurityTest123!",
                "role": "patient",
                "token": None
            },
            "provider": {
                "email": "provider.security@abena-ihr.com", 
                "password": "SecurityTest123!",
                "role": "provider",
                "token": None
            },
            "admin": {
                "email": "admin.security@abena-ihr.com",
                "password": "SecurityTest123!",
                "role": "admin",
                "token": None
            }
        }
    
    def setup_method(self):
        """Setup method for each test"""
        # Authenticate test users
        for user_type, user in self.test_users.items():
            user["token"] = self._authenticate_user(user["email"], user["password"])
    
    def _authenticate_user(self, email: str, password: str) -> str:
        """Authenticate user and return token"""
        auth_data = {
            "email": email,
            "password": password
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json=auth_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"Authentication failed: {response.text}")
    
    def _get_auth_headers(self, user_type: str = "patient") -> Dict[str, str]:
        """Get authenticated headers for user"""
        user = self.test_users[user_type]
        return {"Authorization": f"Bearer {user['token']}"}
    
    def _record_test_result(self, test: SecurityTest, passed: bool, details: str = ""):
        """Record test result"""
        self.test_results.append({
            "name": test.name,
            "description": test.description,
            "severity": test.severity,
            "category": test.category,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    # Authentication Tests
    def test_strong_password_policy(self):
        """Test strong password policy enforcement"""
        test = SecurityTest(
            name="Strong Password Policy",
            description="Verify that weak passwords are rejected",
            severity="high",
            category="auth"
        )
        
        weak_passwords = [
            "123456",
            "password",
            "qwerty",
            "abc123",
            "password123"
        ]
        
        for weak_password in weak_passwords:
            auth_data = {
                "email": "test@example.com",
                "password": weak_password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=auth_data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 400:
                # Weak password rejected
                self._record_test_result(test, True, f"Weak password '{weak_password}' correctly rejected")
                return
        
        self._record_test_result(test, False, "Weak passwords not properly rejected")
    
    def test_jwt_token_validation(self):
        """Test JWT token validation"""
        test = SecurityTest(
            name="JWT Token Validation",
            description="Verify JWT tokens are properly validated",
            severity="critical",
            category="auth"
        )
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid.token.here"}
        
        response = self.session.get(
            f"{self.base_url}/patient-engagement/patients/profile",
            headers=invalid_headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 401:
            self._record_test_result(test, True, "Invalid JWT token properly rejected")
        else:
            self._record_test_result(test, False, f"Invalid JWT token not rejected: {response.status_code}")
    
    def test_token_expiration(self):
        """Test token expiration handling"""
        test = SecurityTest(
            name="Token Expiration",
            description="Verify expired tokens are rejected",
            severity="high",
            category="auth"
        )
        
        # Create a token that expires in 1 second
        auth_data = {
            "email": self.test_users["patient"]["email"],
            "password": self.test_users["patient"]["password"]
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json=auth_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            
            # Wait for token to expire (if configured for short expiration)
            time.sleep(2)
            
            expired_headers = {"Authorization": f"Bearer {token}"}
            
            response = self.session.get(
                f"{self.base_url}/patient-engagement/patients/profile",
                headers=expired_headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 401:
                self._record_test_result(test, True, "Expired token properly rejected")
            else:
                self._record_test_result(test, False, f"Expired token not rejected: {response.status_code}")
        else:
            self._record_test_result(test, False, "Could not obtain token for testing")
    
    # Authorization Tests
    def test_role_based_access_control(self):
        """Test role-based access control"""
        test = SecurityTest(
            name="Role-Based Access Control",
            description="Verify users can only access resources appropriate to their role",
            severity="critical",
            category="authorization"
        )
        
        # Test patient accessing provider-only endpoint
        patient_headers = self._get_auth_headers("patient")
        
        response = self.session.post(
            f"{self.base_url}/clinical-decision-support/analyze",
            json={"patient_id": "test-123"},
            headers=patient_headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 403:
            self._record_test_result(test, True, "Patient correctly denied access to provider endpoint")
        else:
            self._record_test_result(test, False, f"Patient incorrectly allowed access: {response.status_code}")
    
    def test_cross_user_data_access(self):
        """Test cross-user data access prevention"""
        test = SecurityTest(
            name="Cross-User Data Access Prevention",
            description="Verify users cannot access other users' data",
            severity="critical",
            category="authorization"
        )
        
        # Test patient trying to access another patient's profile
        patient_headers = self._get_auth_headers("patient")
        
        response = self.session.get(
            f"{self.base_url}/patient-engagement/patients/other-patient-id/profile",
            headers=patient_headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 403:
            self._record_test_result(test, True, "Cross-user data access correctly prevented")
        else:
            self._record_test_result(test, False, f"Cross-user data access not prevented: {response.status_code}")
    
    # Data Protection Tests
    def test_data_encryption_at_rest(self):
        """Test data encryption at rest"""
        test = SecurityTest(
            name="Data Encryption at Rest",
            description="Verify sensitive data is encrypted in storage",
            severity="high",
            category="data_protection"
        )
        
        # Create sensitive data
        sensitive_data = {
            "patient_id": "test-patient-123",
            "ssn": "123-45-6789",
            "medical_record": "Patient has diabetes and hypertension"
        }
        
        headers = self._get_auth_headers("provider")
        
        response = self.session.post(
            f"{self.base_url}/privacy-security/encrypt",
            json=sensitive_data,
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            encrypted_response = response.json()
            
            # Verify data is encrypted
            if "encrypted_data" in encrypted_response:
                encrypted_data = encrypted_response["encrypted_data"]
                
                # Check that sensitive fields are encrypted
                if isinstance(encrypted_data, dict) and "ssn" in encrypted_data:
                    if encrypted_data["ssn"] != sensitive_data["ssn"]:
                        self._record_test_result(test, True, "Sensitive data properly encrypted")
                    else:
                        self._record_test_result(test, False, "Sensitive data not encrypted")
                else:
                    self._record_test_result(test, False, "Encryption response format incorrect")
            else:
                self._record_test_result(test, False, "No encrypted data in response")
        else:
            self._record_test_result(test, False, f"Encryption endpoint failed: {response.status_code}")
    
    def test_data_anonymization(self):
        """Test data anonymization"""
        test = SecurityTest(
            name="Data Anonymization",
            description="Verify sensitive data is properly anonymized",
            severity="high",
            category="data_protection"
        )
        
        patient_data = {
            "patient_id": "test-patient-123",
            "first_name": "John",
            "last_name": "Doe",
            "ssn": "123-45-6789",
            "date_of_birth": "1990-01-01",
            "address": "123 Main St, Anytown, CA 12345"
        }
        
        headers = self._get_auth_headers("admin")
        
        response = self.session.post(
            f"{self.base_url}/privacy-security/anonymize",
            json=patient_data,
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            anonymized_response = response.json()
            
            if "anonymized_data" in anonymized_response:
                anonymized = anonymized_response["anonymized_data"]
                
                # Check that PII is anonymized
                checks_passed = 0
                total_checks = 3
                
                if anonymized.get("first_name") != patient_data["first_name"]:
                    checks_passed += 1
                
                if anonymized.get("last_name") != patient_data["last_name"]:
                    checks_passed += 1
                
                if "ssn" not in anonymized:
                    checks_passed += 1
                
                if checks_passed == total_checks:
                    self._record_test_result(test, True, "Data properly anonymized")
                else:
                    self._record_test_result(test, False, f"Data not fully anonymized ({checks_passed}/{total_checks} checks passed)")
            else:
                self._record_test_result(test, False, "No anonymized data in response")
        else:
            self._record_test_result(test, False, f"Anonymization endpoint failed: {response.status_code}")
    
    # Input Validation Tests
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        test = SecurityTest(
            name="SQL Injection Prevention",
            description="Verify SQL injection attacks are prevented",
            severity="critical",
            category="data_protection"
        )
        
        sql_injection_payloads = [
            "'; DROP TABLE patients; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' UNION SELECT * FROM users --"
        ]
        
        headers = self._get_auth_headers("patient")
        
        for payload in sql_injection_payloads:
            # Test in search parameter
            response = self.session.get(
                f"{self.base_url}/patient-engagement/patients/search?q={payload}",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 400:
                self._record_test_result(test, True, f"SQL injection prevented: {payload}")
                return
        
        self._record_test_result(test, False, "SQL injection not properly prevented")
    
    def test_xss_prevention(self):
        """Test XSS prevention"""
        test = SecurityTest(
            name="XSS Prevention",
            description="Verify XSS attacks are prevented",
            severity="high",
            category="data_protection"
        )
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        headers = self._get_auth_headers("patient")
        
        for payload in xss_payloads:
            # Test in profile update
            profile_data = {
                "first_name": payload,
                "last_name": "Test"
            }
            
            response = self.session.put(
                f"{self.base_url}/patient-engagement/patients/profile",
                json=profile_data,
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 400:
                self._record_test_result(test, True, f"XSS prevented: {payload}")
                return
        
        self._record_test_result(test, False, "XSS not properly prevented")
    
    # Compliance Tests
    def test_hipaa_compliance_headers(self):
        """Test HIPAA compliance headers"""
        test = SecurityTest(
            name="HIPAA Compliance Headers",
            description="Verify HIPAA compliance headers are present",
            severity="high",
            category="compliance"
        )
        
        response = self.session.get(
            f"{self.base_url}/health",
            timeout=TIMEOUT
        )
        
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        missing_headers = []
        for header in required_headers:
            if header not in response.headers:
                missing_headers.append(header)
        
        if not missing_headers:
            self._record_test_result(test, True, "All required HIPAA headers present")
        else:
            self._record_test_result(test, False, f"Missing headers: {missing_headers}")
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        test = SecurityTest(
            name="Audit Logging",
            description="Verify audit logs are generated for sensitive operations",
            severity="high",
            category="compliance"
        )
        
        headers = self._get_auth_headers("provider")
        
        # Perform a sensitive operation
        response = self.session.post(
            f"{self.base_url}/privacy-security/encrypt",
            json={"patient_id": "test-123", "ssn": "123-45-6789"},
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            # Check if audit log was created
            audit_response = self.session.get(
                f"{self.base_url}/privacy-security/audit-logs",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if audit_response.status_code == 200:
                audit_logs = audit_response.json()
                if isinstance(audit_logs, list) and len(audit_logs) > 0:
                    self._record_test_result(test, True, "Audit logs generated for sensitive operation")
                else:
                    self._record_test_result(test, False, "No audit logs found")
            else:
                self._record_test_result(test, False, f"Audit log endpoint failed: {audit_response.status_code}")
        else:
            self._record_test_result(test, False, f"Sensitive operation failed: {response.status_code}")
    
    # Rate Limiting Tests
    def test_rate_limiting(self):
        """Test rate limiting"""
        test = SecurityTest(
            name="Rate Limiting",
            description="Verify rate limiting is enforced",
            severity="medium",
            category="auth"
        )
        
        headers = self._get_auth_headers("patient")
        
        # Make rapid requests
        rate_limited = False
        for i in range(20):
            response = self.session.get(
                f"{self.base_url}/patient-engagement/patients/profile",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 429:
                rate_limited = True
                break
        
        if rate_limited:
            self._record_test_result(test, True, "Rate limiting properly enforced")
        else:
            self._record_test_result(test, False, "Rate limiting not enforced")
    
    # Blockchain Security Tests
    def test_blockchain_immutability(self):
        """Test blockchain immutability"""
        test = SecurityTest(
            name="Blockchain Immutability",
            description="Verify health records cannot be modified once created",
            severity="critical",
            category="data_protection"
        )
        
        headers = self._get_auth_headers("provider")
        
        # Create a health record
        health_record = {
            "patient_id": "test-patient-123",
            "record_type": "lab_result",
            "data": {
                "test_name": "Security Test",
                "results": {"value": "original"}
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/blockchain/health-records",
            json=health_record,
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 201:
            record_response = response.json()
            record_id = record_response.get("record_id")
            
            if record_id:
                # Try to modify the record
                modified_record = {
                    "record_id": record_id,
                    "data": {
                        "test_name": "Security Test",
                        "results": {"value": "modified"}
                    }
                }
                
                modify_response = self.session.put(
                    f"{self.base_url}/blockchain/health-records/{record_id}",
                    json=modified_record,
                    headers=headers,
                    timeout=TIMEOUT
                )
                
                if modify_response.status_code == 403 or modify_response.status_code == 400:
                    self._record_test_result(test, True, "Blockchain immutability enforced")
                else:
                    self._record_test_result(test, False, f"Blockchain record modification allowed: {modify_response.status_code}")
            else:
                self._record_test_result(test, False, "No record ID returned")
        else:
            self._record_test_result(test, False, f"Health record creation failed: {response.status_code}")
    
    # Generate security report
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["passed"]])
        failed_tests = total_tests - passed_tests
        
        # Group by severity
        critical_failures = len([r for r in self.test_results if not r["passed"] and r["severity"] == "critical"])
        high_failures = len([r for r in self.test_results if not r["passed"] and r["severity"] == "high"])
        medium_failures = len([r for r in self.test_results if not r["passed"] and r["severity"] == "medium"])
        low_failures = len([r for r in self.test_results if not r["passed"] and r["severity"] == "low"])
        
        # Group by category
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0}
            
            if result["passed"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "severity_breakdown": {
                "critical_failures": critical_failures,
                "high_failures": high_failures,
                "medium_failures": medium_failures,
                "low_failures": low_failures
            },
            "category_breakdown": categories,
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if not r["passed"]]
        
        if any(r["severity"] == "critical" for r in failed_tests):
            recommendations.append("CRITICAL: Address critical security vulnerabilities immediately")
        
        if any(r["category"] == "auth" and not r["passed"] for r in failed_tests):
            recommendations.append("HIGH: Review and strengthen authentication mechanisms")
        
        if any(r["category"] == "authorization" and not r["passed"] for r in failed_tests):
            recommendations.append("HIGH: Implement proper authorization controls")
        
        if any(r["category"] == "data_protection" and not r["passed"] for r in failed_tests):
            recommendations.append("HIGH: Enhance data protection and encryption")
        
        if any(r["category"] == "compliance" and not r["passed"] for r in failed_tests):
            recommendations.append("HIGH: Ensure HIPAA and GDPR compliance")
        
        if not recommendations:
            recommendations.append("All security tests passed. Continue monitoring and regular security assessments.")
        
        return recommendations

# Test runner
if __name__ == "__main__":
    # Run security tests
    security_tester = AbenaIHRSecurityTests()
    
    # Run all test methods
    test_methods = [method for method in dir(security_tester) if method.startswith('test_')]
    
    print(f"Running {len(test_methods)} security tests...")
    
    for method_name in test_methods:
        try:
            test_method = getattr(security_tester, method_name)
            security_tester.setup_method()
            test_method()
            print(f"✅ {method_name} - Completed")
        except Exception as e:
            print(f"❌ {method_name} - Error: {str(e)}")
    
    # Generate and display report
    report = security_tester.generate_security_report()
    
    print("\n" + "="*60)
    print("SECURITY TEST REPORT")
    print("="*60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed_tests']}")
    print(f"Failed: {report['summary']['failed_tests']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    
    print(f"\nSeverity Breakdown:")
    print(f"  Critical Failures: {report['severity_breakdown']['critical_failures']}")
    print(f"  High Failures: {report['severity_breakdown']['high_failures']}")
    print(f"  Medium Failures: {report['severity_breakdown']['medium_failures']}")
    print(f"  Low Failures: {report['severity_breakdown']['low_failures']}")
    
    print(f"\nCategory Breakdown:")
    for category, stats in report['category_breakdown'].items():
        print(f"  {category.title()}: {stats['passed']} passed, {stats['failed']} failed")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    # Save report to file
    with open('security-test-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: security-test-report.json")
    
    # Exit with error code if critical failures
    if report['severity_breakdown']['critical_failures'] > 0:
        exit(1) 