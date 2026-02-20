"""
Tests for rate_limit.py module
"""

import pytest
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from middleware.rate_limit import RateLimitConfig, RateLimitMiddleware


class TestRateLimitConfig:
    """Test rate limit configuration"""
    
    def test_default_limits(self):
        """Test default rate limits"""
        config = RateLimitConfig()
        
        assert "default" in config.DEFAULT_LIMITS
        limit, window = config.DEFAULT_LIMITS["default"]
        assert limit > 0
        assert window > 0
    
    def test_endpoint_limits(self):
        """Test endpoint-specific limits"""
        config = RateLimitConfig()
        
        assert "/api/auth/login" in config.ENDPOINT_LIMITS
        limit, window = config.ENDPOINT_LIMITS["/api/auth/login"]
        assert limit == 5
        assert window == 300  # 5 minutes
    
    def test_role_multipliers(self):
        """Test role-based multipliers"""
        config = RateLimitConfig()
        
        assert "admin" in config.ROLE_MULTIPLIERS
        assert config.ROLE_MULTIPLIERS["admin"] > 1.0


class TestRateLimitMiddleware:
    """Test rate limiting middleware"""
    
    def test_middleware_initialization(self):
        """Test middleware can be initialized"""
        # Mock app
        class MockApp:
            pass
        
        app = MockApp()
        
        # Should not raise exception
        middleware = RateLimitMiddleware(
            app,
            redis_host="localhost",
            redis_port=6379
        )
        
        assert middleware is not None
    
    def test_get_rate_limit(self):
        """Test getting rate limit for endpoint"""
        class MockApp:
            pass
        
        middleware = RateLimitMiddleware(MockApp())
        limit, window = middleware._get_rate_limit("/api/auth/login")
        
        assert limit > 0
        assert window > 0
    
    def test_should_skip_rate_limit(self):
        """Test paths that should skip rate limiting"""
        class MockApp:
            pass
        
        middleware = RateLimitMiddleware(MockApp())
        
        assert middleware._should_skip_rate_limit("/health") is True
        assert middleware._should_skip_rate_limit("/docs") is True
        assert middleware._should_skip_rate_limit("/api/users") is False


# Note: Full integration tests would require Redis running
# These are unit tests that don't require Redis

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

