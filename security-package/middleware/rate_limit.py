"""
Abena IHR Rate Limiting Middleware
===================================

Redis-backed rate limiting middleware for FastAPI applications.
Implements sliding window algorithm to prevent abuse and DDoS attacks.

Features:
- Per-endpoint rate limiting
- Role-based rate limits
- Sliding window algorithm
- Redis backend for distributed systems
- Configurable limits per endpoint

Author: Abena IHR Security Team
Date: December 3, 2025
Version: 2.0.0
"""

import os
import time
from typing import Optional, Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis
from redis.exceptions import RedisError


class RateLimitConfig:
    """Rate limit configuration per endpoint and role"""
    
    # Default limits: (requests, window_seconds)
    DEFAULT_LIMITS = {
        "default": (100, 60),  # 100 requests per minute
    }
    
    # Endpoint-specific limits
    ENDPOINT_LIMITS: Dict[str, Tuple[int, int]] = {
        "/api/auth/login": (5, 300),  # 5 attempts per 5 minutes
        "/api/auth/register": (3, 3600),  # 3 attempts per hour
        "/api/auth/forgot-password": (3, 3600),  # 3 attempts per hour
        "/api/auth/reset-password": (5, 3600),  # 5 attempts per hour
        "/api/patients": (100, 60),  # 100 requests per minute
        "/api/reports": (50, 60),  # 50 requests per minute
        "/api/upload": (10, 60),  # 10 uploads per minute
    }
    
    # Role-based limits (multiplier for base limits)
    ROLE_MULTIPLIERS: Dict[str, float] = {
        "admin": 10.0,  # Admins get 10x the limit
        "provider": 5.0,  # Providers get 5x the limit
        "staff": 2.0,  # Staff get 2x the limit
        "patient": 1.0,  # Patients get base limit
        "viewer": 0.5,  # Viewers get half the limit
    }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis sliding window algorithm.
    
    Features:
    - Sliding window rate limiting
    - Per-endpoint configuration
    - Role-based limits
    - IP-based tracking
    - Automatic cleanup of expired entries
    """
    
    def __init__(
        self,
        app,
        redis_url: Optional[str] = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        key_prefix: str = "rate_limit:"
    ):
        """
        Initialize rate limiting middleware.
        
        Args:
            app: FastAPI application
            redis_url: Full Redis URL (redis://host:port/db)
            redis_host: Redis hostname
            redis_port: Redis port
            redis_db: Redis database number
            redis_password: Redis password
            key_prefix: Prefix for Redis keys
        """
        super().__init__(app)
        
        # Redis connection
        if redis_url:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
        else:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True
            )
        
        self.key_prefix = key_prefix
        self.config = RateLimitConfig()
        
        # Test Redis connection
        try:
            self.redis_client.ping()
        except RedisError as e:
            import warnings
            warnings.warn(
                f"Redis connection failed: {e}. Rate limiting may not work properly.",
                UserWarning
            )
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and apply rate limiting.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler
            
        Returns:
            Response object
        """
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limit(request.url.path):
            return await call_next(request)
        
        # Get rate limit key (IP + endpoint)
        client_ip = self._get_client_ip(request)
        endpoint = request.url.path
        user_role = self._get_user_role(request)  # From JWT token if available
        
        # Get rate limit for this endpoint
        limit, window = self._get_rate_limit(endpoint, user_role)
        
        # Check rate limit
        key = f"{self.key_prefix}{client_ip}:{endpoint}"
        is_allowed, remaining, reset_time = self._check_rate_limit(
            key, limit, window
        )
        
        if not is_allowed:
            # Rate limit exceeded
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": limit,
                    "window": window,
                    "reset_at": reset_time,
                    "message": f"Too many requests. Limit: {limit} per {window}s"
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time - int(time.time()))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _should_skip_rate_limit(self, path: str) -> bool:
        """Check if path should skip rate limiting"""
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]
        return any(path.startswith(skip) for skip in skip_paths)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in chain
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_user_role(self, request: Request) -> Optional[str]:
        """Extract user role from JWT token if available"""
        # Try to get from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        # In production, decode JWT token to get role
        # For now, return None (will use default limits)
        # This should be integrated with auth_middleware.py
        return None
    
    def _get_rate_limit(self, endpoint: str, user_role: Optional[str] = None) -> Tuple[int, int]:
        """
        Get rate limit for endpoint and role.
        
        Args:
            endpoint: Request endpoint path
            user_role: User role (if authenticated)
            
        Returns:
            Tuple of (limit, window_seconds)
        """
        # Get base limit for endpoint
        limit, window = self.config.ENDPOINT_LIMITS.get(
            endpoint,
            self.config.DEFAULT_LIMITS["default"]
        )
        
        # Apply role multiplier
        if user_role:
            multiplier = self.config.ROLE_MULTIPLIERS.get(
                user_role.lower(),
                1.0
            )
            limit = int(limit * multiplier)
        
        return limit, window
    
    def _check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, int]:
        """
        Check rate limit using sliding window algorithm.
        
        Args:
            key: Redis key for this rate limit
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining, reset_time)
        """
        try:
            current_time = time.time()
            window_start = current_time - window
            
            # Use Redis sorted set for sliding window
            # Key: rate_limit:ip:endpoint
            # Score: timestamp
            # Value: request_id (unique)
            
            # Remove old entries outside window
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            current_count = self.redis_client.zcard(key)
            
            # Check if limit exceeded
            if current_count >= limit:
                # Get oldest entry to calculate reset time
                oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    reset_time = int(oldest[0][1] + window)
                else:
                    reset_time = int(current_time + window)
                
                return False, 0, reset_time
            
            # Add current request
            request_id = f"{current_time}:{id(self)}"
            self.redis_client.zadd(key, {request_id: current_time})
            
            # Set expiration on key (cleanup)
            self.redis_client.expire(key, window)
            
            # Calculate remaining and reset time
            remaining = limit - current_count - 1
            reset_time = int(current_time + window)
            
            return True, remaining, reset_time
            
        except RedisError as e:
            # If Redis fails, allow request (fail open)
            # In production, you might want to fail closed
            import warnings
            warnings.warn(f"Redis error in rate limiting: {e}. Allowing request.", UserWarning)
            return True, limit, int(time.time() + window)
    
    def reset_rate_limit(self, key: str) -> bool:
        """
        Reset rate limit for a specific key (admin function).
        
        Args:
            key: Rate limit key to reset
            
        Returns:
            True if reset successful
        """
        try:
            full_key = f"{self.key_prefix}{key}"
            return bool(self.redis_client.delete(full_key))
        except RedisError:
            return False
    
    def get_rate_limit_status(self, key: str) -> Dict:
        """
        Get current rate limit status for a key.
        
        Args:
            key: Rate limit key
            
        Returns:
            Dictionary with rate limit status
        """
        try:
            full_key = f"{self.key_prefix}{key}"
            count = self.redis_client.zcard(full_key)
            ttl = self.redis_client.ttl(full_key)
            
            return {
                "key": key,
                "current_requests": count,
                "ttl_seconds": ttl if ttl > 0 else None
            }
        except RedisError:
            return {
                "key": key,
                "error": "Redis connection failed"
            }


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Abena IHR Rate Limiting Middleware - Test")
    print("=" * 60)
    
    # Test Redis connection
    print("\n1. Testing Redis connection...")
    try:
        redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        redis_client.ping()
        print("   ✓ Redis connection successful")
    except Exception as e:
        print(f"   ✗ Redis connection failed: {e}")
        print("   Note: Install Redis or use Docker: docker run -d -p 6379:6379 redis")
    
    # Test rate limit configuration
    print("\n2. Rate limit configuration:")
    config = RateLimitConfig()
    print(f"   Default limit: {config.DEFAULT_LIMITS['default']}")
    print(f"   Login limit: {config.ENDPOINT_LIMITS.get('/api/auth/login')}")
    print(f"   Register limit: {config.ENDPOINT_LIMITS.get('/api/auth/register')}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Ensure Redis is running for rate limiting to work!")
    print("   Start Redis: docker run -d -p 6379:6379 redis")

