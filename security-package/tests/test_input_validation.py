"""
Tests for input_validation.py module
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from validation.input_validation import InputValidator, PatientInput


class TestStringSanitization:
    """Test string sanitization"""
    
    def test_sanitize_normal_string(self):
        """Test sanitization of normal string"""
        input_str = "Normal text here"
        sanitized = InputValidator.sanitize_string(input_str)
        
        assert sanitized == input_str
    
    def test_sanitize_xss_script(self):
        """Test sanitization removes XSS script tags"""
        input_str = "<script>alert('xss')</script>"
        sanitized = InputValidator.sanitize_string(input_str)
        
        assert "<script>" not in sanitized.lower()
        assert "alert" not in sanitized.lower()
    
    def test_sanitize_sql_injection(self):
        """Test sanitization blocks SQL injection"""
        input_str = "'; DROP TABLE users; --"
        
        with pytest.raises(ValueError, match="SQL"):
            InputValidator.sanitize_string(input_str)
    
    def test_sanitize_path_traversal(self):
        """Test sanitization blocks path traversal"""
        input_str = "../../etc/passwd"
        
        with pytest.raises(ValueError, match="path"):
            InputValidator.sanitize_string(input_str)
    
    def test_sanitize_max_length(self):
        """Test sanitization enforces max length"""
        input_str = "a" * 200
        sanitized = InputValidator.sanitize_string(input_str, max_length=100)
        
        assert len(sanitized) == 100


class TestEmailValidation:
    """Test email validation"""
    
    def test_validate_valid_email(self):
        """Test validation of valid email"""
        email = "user@example.com"
        is_valid, error = InputValidator.validate_email(email)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_email(self):
        """Test validation of invalid email"""
        email = "invalid-email"
        is_valid, error = InputValidator.validate_email(email)
        
        assert is_valid is False
        assert error is not None
    
    def test_validate_empty_email(self):
        """Test validation of empty email"""
        email = ""
        is_valid, error = InputValidator.validate_email(email)
        
        assert is_valid is False
        assert "empty" in error.lower()


class TestPhoneValidation:
    """Test phone number validation"""
    
    def test_validate_valid_phone(self):
        """Test validation of valid phone"""
        phone = "(555) 123-4567"
        is_valid, error = InputValidator.validate_phone(phone)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_phone(self):
        """Test validation of invalid phone"""
        phone = "123"
        is_valid, error = InputValidator.validate_phone(phone)
        
        assert is_valid is False
        assert error is not None


class TestSSNValidation:
    """Test SSN validation"""
    
    def test_validate_valid_ssn(self):
        """Test validation of valid SSN"""
        ssn = "123-45-6789"
        is_valid, error = InputValidator.validate_ssn(ssn)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_ssn_all_zeros(self):
        """Test validation rejects SSN with all zeros"""
        ssn = "000-12-3456"
        is_valid, error = InputValidator.validate_ssn(ssn)
        
        assert is_valid is False
        assert "zero" in error.lower()


class TestDateValidation:
    """Test date validation"""
    
    def test_validate_valid_date(self):
        """Test validation of valid date"""
        date_str = "2024-01-15"
        is_valid, dt, error = InputValidator.validate_date(date_str)
        
        assert is_valid is True
        assert dt is not None
        assert error is None
    
    def test_validate_invalid_date(self):
        """Test validation of invalid date"""
        date_str = "invalid-date"
        is_valid, dt, error = InputValidator.validate_date(date_str)
        
        assert is_valid is False
        assert dt is None
        assert error is not None


class TestPydanticModels:
    """Test Pydantic model validation"""
    
    def test_patient_input_valid(self):
        """Test valid patient input"""
        patient = PatientInput(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="(555) 123-4567",
            date_of_birth="1990-01-15"
        )
        
        assert patient.first_name == "John"
        assert patient.email == "john@example.com"
    
    def test_patient_input_invalid_email(self):
        """Test patient input with invalid email"""
        with pytest.raises(Exception):  # Should raise ValidationError
            PatientInput(
                first_name="John",
                last_name="Doe",
                email="invalid-email",
                phone="(555) 123-4567",
                date_of_birth="1990-01-15"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

