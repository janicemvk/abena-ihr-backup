"""
ABENA IHR Security Integration Module
Adds JWT authentication, rate limiting, and input validation
"""

import sys
import os
from pathlib import Path

# Add security package to path
# Try mounted volume first, then relative path
security_paths = [
    Path("/security-package"),  # Docker volume mount
    Path(__file__).parent.parent.parent.parent / "security-package",  # Relative from host
]
for security_path in security_paths:
    if security_path.exists():
        sys.path.insert(0, str(security_path))
        break

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import logging

# Import security modules
try:
    from middleware.auth_middleware import JWTAuth, UserRole, TokenData
    from middleware.rate_limit import RateLimitMiddleware
    from validation.input_validation import InputValidator
    from utils.password_security import PasswordSecurity
except ImportError as e:
    logging.error(f"Failed to import security modules: {e}")
    raise

# Create wrapper function for require_role (it's a class method)
def require_role(*allowed_roles: UserRole):
    """Wrapper for JWTAuth.require_role class method"""
    return JWTAuth.require_role(*allowed_roles)

security = HTTPBearer()
logger = logging.getLogger(__name__)

class LoginRequest(BaseModel):
    email: str
    password: str
    
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    role: str

def setup_security(app: FastAPI):
    """Add security middleware to FastAPI application"""
    # Get Redis URL from environment
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    app.add_middleware(RateLimitMiddleware, redis_url=redis_url)
    logger.info(f"Security middleware enabled (Redis: {redis_url})")
    return app

async def secure_login(email: str, password: str, get_user_by_email_func, get_user_data_func):
    """Secure login endpoint handler with bcrypt password verification"""
    
    # Validate email format
    is_valid_email, error = InputValidator.validate_email(email)
    if not is_valid_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email format: {error}"
        )
    
    # Get user from database
    user = await get_user_by_email_func(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password with bcrypt
    is_valid_password = PasswordSecurity.verify_password(
        password, 
        user.get('hashed_password') or user.get('password')
    )
    
    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Get user role
    role = user.get('role', 'patient')
    user_data = await get_user_data_func(user.get('id'), role)
    
    # Create JWT token
    token = JWTAuth.create_access_token(
        user_id=str(user.get('id')),
        email=email,
        role=UserRole(role)
    )
    
    logger.info(f"User logged in: {email} (role: {role})")
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=str(user.get('id')),
        email=email,
        role=role
    )

async def get_current_user_secure(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """FastAPI dependency to get current user from JWT token"""
    token = credentials.credentials
    return JWTAuth.verify_token(token)

__all__ = [
    'setup_security',
    'secure_login',
    'get_current_user_secure',
    'JWTAuth',
    'UserRole',
    'require_role',
    'InputValidator',
    'PasswordSecurity',
    'LoginRequest',
    'LoginResponse'
]
