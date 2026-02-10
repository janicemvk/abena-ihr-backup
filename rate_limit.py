"""
Rate Limiting Module for Quantum Healthcare Service
Uses Redis for distributed rate limiting
"""

import os
import redis
import logging
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
redis_client = None

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()  # Test connection
    logger.info("Redis connected for rate limiting")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Rate limiting will use in-memory fallback.")
    redis_client = None

# In-memory fallback (per-process, not distributed)
_memory_cache = {}

def rate_limit(max_requests=10, window=60, key_prefix="quantum"):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum number of requests allowed
        window: Time window in seconds
        key_prefix: Prefix for Redis key
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get identifier (user ID from token or IP address)
            user_id = None
            if hasattr(request, 'current_user') and request.current_user:
                user_id = request.current_user.get('user_id') or request.current_user.get('email')
            
            if not user_id:
                user_id = request.remote_addr  # Fallback to IP
            
            # Create rate limit key
            key = f"{key_prefix}:rate_limit:{user_id}"
            
            # Use Redis if available
            use_redis = redis_client is not None
            redis_available = use_redis
            if use_redis:
                # Use Redis for distributed rate limiting
                try:
                    current = redis_client.incr(key)
                    if current == 1:
                        redis_client.expire(key, window)
                    
                    if current > max_requests:
                        ttl = redis_client.ttl(key)
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'message': f'Maximum {max_requests} requests per {window} seconds',
                            'retry_after': ttl,
                            'limit': max_requests,
                            'window': window
                        }), 429
                except Exception as e:
                    logger.error(f"Redis rate limit error: {e}, falling back to memory")
                    redis_available = False
            
            # Fallback to in-memory rate limiting
            if not redis_available:
                now = datetime.now()
                if key not in _memory_cache:
                    _memory_cache[key] = {'count': 0, 'reset_time': now + timedelta(seconds=window)}
                
                cache_entry = _memory_cache[key]
                
                # Reset if window expired
                if now > cache_entry['reset_time']:
                    cache_entry['count'] = 0
                    cache_entry['reset_time'] = now + timedelta(seconds=window)
                
                cache_entry['count'] += 1
                
                if cache_entry['count'] > max_requests:
                    retry_after = int((cache_entry['reset_time'] - now).total_seconds())
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Maximum {max_requests} requests per {window} seconds',
                        'retry_after': retry_after,
                        'limit': max_requests,
                        'window': window
                    }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Predefined rate limits for different endpoints
quantum_analysis_limit = rate_limit(max_requests=5, window=300, key_prefix="quantum_analysis")  # 5 per 5 minutes
general_api_limit = rate_limit(max_requests=100, window=60, key_prefix="quantum_api")  # 100 per minute
demo_results_limit = rate_limit(max_requests=20, window=60, key_prefix="quantum_demo")  # 20 per minute



