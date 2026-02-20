"""
Tests for password_security.py module
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.password_security import PasswordSecurity, PasswordStrength


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "SecureP@ssw0rd123!"
        hashed = PasswordSecurity.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "SecureP@ssw0rd123!"
        hashed = PasswordSecurity.hash_password(password)
        
        assert PasswordSecurity.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "SecureP@ssw0rd123!"
        hashed = PasswordSecurity.hash_password(password)
        
        assert PasswordSecurity.verify_password("WrongPassword", hashed) is False
    
    def test_hash_different_salts(self):
        """Test that same password produces different hashes (different salts)"""
        password = "SecureP@ssw0rd123!"
        hashed1 = PasswordSecurity.hash_password(password)
        hashed2 = PasswordSecurity.hash_password(password)
        
        # Hashes should be different due to different salts
        assert hashed1 != hashed2
        
        # But both should verify correctly
        assert PasswordSecurity.verify_password(password, hashed1) is True
        assert PasswordSecurity.verify_password(password, hashed2) is True


class TestPasswordValidation:
    """Test password strength validation"""
    
    def test_validate_strong_password(self):
        """Test validation of strong password"""
        password = "SecureP@ssw0rd123!"
        is_valid, message = PasswordSecurity.validate_password_strength(password)
        
        assert is_valid is True
        assert "meets" in message.lower()
    
    def test_validate_short_password(self):
        """Test validation of short password"""
        password = "Short1!"
        is_valid, message = PasswordSecurity.validate_password_strength(password)
        
        assert is_valid is False
        assert "12" in message or "length" in message.lower()
    
    def test_validate_password_missing_uppercase(self):
        """Test validation of password missing uppercase"""
        password = "securepassword123!"
        is_valid, message = PasswordSecurity.validate_password_strength(password)
        
        assert is_valid is False
        assert "uppercase" in message.lower()
    
    def test_validate_password_missing_lowercase(self):
        """Test validation of password missing lowercase"""
        password = "SECUREPASSWORD123!"
        is_valid, message = PasswordSecurity.validate_password_strength(password)
        
        assert is_valid is False
        assert "lowercase" in message.lower()
    
    def test_validate_password_missing_digit(self):
        """Test validation of password missing digit"""
        password = "SecurePassword!"
        is_valid, message = PasswordSecurity.validate_password_strength(password)
        
        assert is_valid is False
        assert "digit" in message.lower()
    
    def test_validate_password_missing_special(self):
        """Test validation of password missing special character"""
        password = "SecurePassword123"
        is_valid, message = PasswordSecurity.validate_password_strength(password)
        
        assert is_valid is False
        assert "special" in message.lower()
    
    def test_validate_common_password(self):
        """Test validation rejects common passwords"""
        password = "password123"
        is_valid, message = PasswordSecurity.validate_password_strength(password)
        
        assert is_valid is False
        assert "common" in message.lower()
    
    def test_validate_sequential_numbers(self):
        """Test validation rejects sequential numbers"""
        password = "SecureP@ss12345!"
        is_valid, message = PasswordSecurity.validate_password_strength(password)
        
        assert is_valid is False
        assert "sequential" in message.lower()


class TestPasswordStrength:
    """Test password strength calculation"""
    
    def test_get_password_strength_weak(self):
        """Test weak password strength"""
        password = "weak"
        strength = PasswordSecurity.get_password_strength(password)
        
        assert strength == PasswordStrength.WEAK
    
    def test_get_password_strength_medium(self):
        """Test medium password strength"""
        password = "MediumPass123"
        strength = PasswordSecurity.get_password_strength(password)
        
        assert strength in [PasswordStrength.MEDIUM, PasswordStrength.STRONG]
    
    def test_get_password_strength_strong(self):
        """Test strong password strength"""
        password = "VerySecureP@ssw0rd123!"
        strength = PasswordSecurity.get_password_strength(password)
        
        assert strength in [PasswordStrength.STRONG, PasswordStrength.VERY_STRONG]


class TestPasswordExpiration:
    """Test password expiration functionality"""
    
    def test_is_password_expired_old(self):
        """Test password expiration for old password"""
        old_date = datetime.utcnow() - timedelta(days=100)
        assert PasswordSecurity.is_password_expired(old_date) is True
    
    def test_is_password_expired_recent(self):
        """Test password expiration for recent password"""
        recent_date = datetime.utcnow() - timedelta(days=30)
        assert PasswordSecurity.is_password_expired(recent_date) is False
    
    def test_days_until_expiration(self):
        """Test days until expiration calculation"""
        recent_date = datetime.utcnow() - timedelta(days=30)
        days_left = PasswordSecurity.days_until_expiration(recent_date)
        
        assert days_left is not None
        assert days_left > 0
        assert days_left <= 60  # Should be around 60 days (90 - 30)
    
    def test_days_until_expiration_expired(self):
        """Test days until expiration for expired password"""
        old_date = datetime.utcnow() - timedelta(days=100)
        days_left = PasswordSecurity.days_until_expiration(old_date)
        
        assert days_left is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

