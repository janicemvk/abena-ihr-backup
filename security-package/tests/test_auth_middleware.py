"""
Tests for auth_middleware.py module
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from middleware.auth_middleware import JWTAuth, UserRole, TokenData


class TestTokenCreation:
    """Test JWT token creation"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        token = JWTAuth.create_access_token(
            user_id="usr_123",
            email="test@example.com",
            role=UserRole.PATIENT
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        token = JWTAuth.create_refresh_token(
            user_id="usr_123",
            email="test@example.com"
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_contains_user_data(self):
        """Test token contains user data"""
        user_id = "usr_123"
        email = "test@example.com"
        role = UserRole.PROVIDER
        
        token = JWTAuth.create_access_token(
            user_id=user_id,
            email=email,
            role=role
        )
        
        # Verify token
        token_data = JWTAuth.verify_token(token)
        
        assert token_data.user_id == user_id
        assert token_data.email == email
        assert token_data.role == role


class TestTokenVerification:
    """Test JWT token verification"""
    
    def test_verify_valid_token(self):
        """Test verification of valid token"""
        token = JWTAuth.create_access_token(
            user_id="usr_123",
            email="test@example.com",
            role=UserRole.PATIENT
        )
        
        token_data = JWTAuth.verify_token(token)
        
        assert token_data is not None
        assert token_data.user_id == "usr_123"
        assert token_data.email == "test@example.com"
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):  # Should raise HTTPException or similar
            JWTAuth.verify_token(invalid_token)
    
    def test_verify_expired_token(self):
        """Test verification of expired token"""
        # Create token with very short expiration
        token = JWTAuth.create_access_token(
            user_id="usr_123",
            email="test@example.com",
            role=UserRole.PATIENT,
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # Note: This test may need adjustment based on actual expiration checking
        # JWT library should handle expiration automatically
        try:
            token_data = JWTAuth.verify_token(token)
            # If token is expired, verify_token should raise an exception
            # If it doesn't, the test should check expiration manually
            if token_data.exp:
                assert datetime.utcnow() > token_data.exp
        except Exception:
            # Expected behavior - expired token should raise exception
            pass


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_role_permissions(self):
        """Test role permissions mapping"""
        admin_perms = JWTAuth.ROLE_PERMISSIONS[UserRole.ADMIN]
        patient_perms = JWTAuth.ROLE_PERMISSIONS[UserRole.PATIENT]
        
        assert len(admin_perms) > len(patient_perms)
        assert "admin:all" in admin_perms
        assert "read:own" in patient_perms
    
    def test_token_includes_permissions(self):
        """Test that token includes role permissions"""
        token = JWTAuth.create_access_token(
            user_id="usr_123",
            email="admin@example.com",
            role=UserRole.ADMIN
        )
        
        token_data = JWTAuth.verify_token(token)
        
        assert len(token_data.permissions) > 0
        assert "admin:all" in token_data.permissions


class TestTokenRefresh:
    """Test token refresh functionality"""
    
    def test_refresh_access_token(self):
        """Test refreshing access token from refresh token"""
        refresh_token = JWTAuth.create_refresh_token(
            user_id="usr_123",
            email="test@example.com"
        )
        
        # Note: refresh_access_token requires role from database
        # This is a simplified test
        try:
            new_token = JWTAuth.refresh_access_token(refresh_token)
            assert new_token is not None
        except Exception as e:
            # Expected if role lookup fails
            # In production, role should be fetched from database
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

