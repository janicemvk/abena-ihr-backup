"""
Abena IHR Secure Authentication Service
========================================

Complete secure authentication service integrating all security modules:
- Password hashing (bcrypt)
- JWT token generation
- Rate limiting
- Input validation
- User registration and login

Author: Abena IHR Security Team
Date: December 3, 2025
Version: 2.0.0
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
import asyncpg

# Import security modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.password_security import PasswordSecurity
from middleware.auth_middleware import JWTAuth, UserRole, TokenData
from validation.input_validation import InputValidator, ValidatedEmail
from middleware.rate_limit import RateLimitMiddleware


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/abena_ihr"
)


# Pydantic models
class UserRegister(BaseModel):
    """User registration model"""
    email: ValidatedEmail
    password: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.PATIENT
    phone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, message = PasswordSecurity.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v
    
    @validator('first_name', 'last_name')
    def sanitize_names(cls, v):
        return InputValidator.sanitize_string(v, max_length=100)
    
    @validator('phone')
    def validate_phone(cls, v):
        if v:
            is_valid, error = InputValidator.validate_phone(v)
            if not is_valid:
                raise ValueError(error)
        return v


class UserLogin(BaseModel):
    """User login model"""
    email: str
    password: str


class PasswordChange(BaseModel):
    """Password change model"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        is_valid, message = PasswordSecurity.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class AuthResponse(BaseModel):
    """Authentication response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict


class SecureAuthService:
    """
    Secure authentication service with all security features integrated.
    """
    
    def __init__(self, db_url: str = DATABASE_URL):
        """Initialize auth service"""
        self.db_url = db_url
        self.conn_pool = None
    
    async def init_db_pool(self):
        """Initialize database connection pool"""
        try:
            self.conn_pool = await asyncpg.create_pool(self.db_url)
        except Exception as e:
            raise Exception(f"Database connection failed: {e}")
    
    async def close_db_pool(self):
        """Close database connection pool"""
        if self.conn_pool:
            await self.conn_pool.close()
    
    async def register_user(self, user_data: UserRegister) -> AuthResponse:
        """
        Register a new user with secure password hashing.
        
        Args:
            user_data: User registration data
            
        Returns:
            AuthResponse with tokens
            
        Raises:
            HTTPException: If registration fails
        """
        # Validate input
        email = InputValidator.sanitize_string(user_data.email)
        is_valid, error = InputValidator.validate_email(email)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        async with self.conn_pool.acquire() as conn:
            # Check if user already exists
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1",
                email
            )
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            # Hash password
            hashed_password = PasswordSecurity.hash_password(user_data.password)
            
            # Create user
            user_id = await conn.fetchval(
                """
                INSERT INTO users (
                    email, password_hash, first_name, last_name,
                    role, phone, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                """,
                email,
                hashed_password,
                user_data.first_name,
                user_data.last_name,
                user_data.role.value,
                user_data.phone,
                datetime.utcnow(),
                datetime.utcnow()
            )
            
            # Generate tokens
            access_token = JWTAuth.create_access_token(
                user_id=str(user_id),
                email=email,
                role=user_data.role
            )
            
            refresh_token = JWTAuth.create_refresh_token(
                user_id=str(user_id),
                email=email
            )
            
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=JWTAuth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user={
                    "id": str(user_id),
                    "email": email,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "role": user_data.role.value
                }
            )
    
    async def login_user(self, login_data: UserLogin) -> AuthResponse:
        """
        Authenticate user and return tokens.
        
        Args:
            login_data: Login credentials
            
        Returns:
            AuthResponse with tokens
            
        Raises:
            HTTPException: If authentication fails
        """
        # Sanitize email
        email = InputValidator.sanitize_string(login_data.email)
        
        async with self.conn_pool.acquire() as conn:
            # Get user
            user = await conn.fetchrow(
                """
                SELECT id, email, password_hash, first_name, last_name, role
                FROM users
                WHERE email = $1
                """,
                email
            )
            
            if not user:
                # Don't reveal if user exists (security best practice)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Verify password
            if not user['password_hash']:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            is_valid = PasswordSecurity.verify_password(
                login_data.password,
                user['password_hash']
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Get role
            try:
                role = UserRole(user['role'])
            except ValueError:
                role = UserRole.PATIENT
            
            # Generate tokens
            access_token = JWTAuth.create_access_token(
                user_id=str(user['id']),
                email=user['email'],
                role=role
            )
            
            refresh_token = JWTAuth.create_refresh_token(
                user_id=str(user['id']),
                email=user['email']
            )
            
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=JWTAuth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user={
                    "id": str(user['id']),
                    "email": user['email'],
                    "first_name": user['first_name'],
                    "last_name": user['last_name'],
                    "role": role.value
                }
            )
    
    async def change_password(
        self,
        user_id: str,
        password_data: PasswordChange
    ) -> Dict:
        """
        Change user password.
        
        Args:
            user_id: User ID
            password_data: Current and new password
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If password change fails
        """
        async with self.conn_pool.acquire() as conn:
            # Get user
            user = await conn.fetchrow(
                "SELECT password_hash FROM users WHERE id = $1",
                user_id
            )
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Verify current password
            is_valid = PasswordSecurity.verify_password(
                password_data.current_password,
                user['password_hash']
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect"
                )
            
            # Hash new password
            new_hashed = PasswordSecurity.hash_password(password_data.new_password)
            
            # Update password
            await conn.execute(
                """
                UPDATE users
                SET 
                    password_hash = $1,
                    password_changed_at = $2,
                    updated_at = $2
                WHERE id = $3
                """,
                new_hashed,
                datetime.utcnow(),
                user_id
            )
            
            return {"message": "Password changed successfully"}


# FastAPI app setup
app = FastAPI(title="Abena IHR Secure Auth Service")

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Initialize auth service
auth_service = SecureAuthService()


@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    await auth_service.init_db_pool()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await auth_service.close_db_pool()


@app.post("/api/auth/register", response_model=AuthResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    return await auth_service.register_user(user_data)


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(login_data: UserLogin):
    """Login user"""
    return await auth_service.login_user(login_data)


@app.post("/api/auth/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: TokenData = Depends(JWTAuth.get_current_user)
):
    """Change user password"""
    return await auth_service.change_password(
        current_user.user_id,
        password_data
    )


@app.get("/api/auth/me")
async def get_current_user(
    current_user: TokenData = Depends(JWTAuth.get_current_user)
):
    """Get current user information"""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role.value,
        "permissions": current_user.permissions
    }


# Example usage
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Abena IHR Secure Authentication Service")
    print("=" * 60)
    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("\n⚠️  IMPORTANT:")
    print("   - Set DATABASE_URL environment variable")
    print("   - Set JWT_SECRET_KEY environment variable")
    print("   - Ensure Redis is running for rate limiting")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

