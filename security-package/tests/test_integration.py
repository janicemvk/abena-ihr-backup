"""
Integration tests for security package
Tests multiple modules working together
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.password_security import PasswordSecurity
from middleware.auth_middleware import JWTAuth, UserRole
from validation.input_validation import InputValidator


class TestPasswordAndAuthIntegration:
    """Test password security and auth middleware integration"""
    
    def test_register_login_flow(self):
        """Test complete registration and login flow"""
        # Simulate registration
        password = "SecureP@ssw0rd123!"
        hashed = PasswordSecurity.hash_password(password)
        
        # Simulate login
        is_valid = PasswordSecurity.verify_password(password, hashed)
        assert is_valid is True
        
        # Create token
        token = JWTAuth.create_access_token(
            user_id="usr_123",
            email="test@example.com",
            role=UserRole.PATIENT
        )
        
        # Verify token
        token_data = JWTAuth.verify_token(token)
        assert token_data.user_id == "usr_123"
        assert token_data.email == "test@example.com"


class TestInputValidationAndAuthIntegration:
    """Test input validation with authentication"""
    
    def test_sanitized_input_in_token(self):
        """Test that sanitized input can be used in token"""
        # Sanitize user input
        email = InputValidator.sanitize_string("user@example.com")
        is_valid, error = InputValidator.validate_email(email)
        
        assert is_valid is True
        
        # Use in token creation
        token = JWTAuth.create_access_token(
            user_id="usr_123",
            email=email,
            role=UserRole.PATIENT
        )
        
        # Verify token
        token_data = JWTAuth.verify_token(token)
        assert token_data.email == email


class TestSecurityWorkflow:
    """Test complete security workflow"""
    
    def test_complete_user_registration_workflow(self):
        """Test complete user registration security workflow"""
        # 1. Validate email
        email = "newuser@example.com"
        is_valid, error = InputValidator.validate_email(email)
        assert is_valid is True
        
        # 2. Sanitize name
        first_name = InputValidator.sanitize_string("John")
        last_name = InputValidator.sanitize_string("Doe")
        
        # 3. Validate and hash password
        password = "SecureP@ssw0rd123!"
        is_valid, msg = PasswordSecurity.validate_password_strength(password)
        assert is_valid is True
        
        hashed = PasswordSecurity.hash_password(password)
        
        # 4. Create user token
        token = JWTAuth.create_access_token(
            user_id="usr_new",
            email=email,
            role=UserRole.PATIENT
        )
        
        # 5. Verify everything works
        token_data = JWTAuth.verify_token(token)
        assert token_data.email == email
        
        # 6. Verify password
        assert PasswordSecurity.verify_password(password, hashed) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

