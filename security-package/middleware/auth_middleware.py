"""
Abena IHR JWT Authentication Middleware
========================================

Provides JWT-based authentication and role-based access control (RBAC)
for FastAPI applications.

Features:
- JWT token creation and verification
- Role-based access control (RBAC)
- Token expiration handling
- Secure secret key management
- FastAPI dependency injection

Author: Abena IHR Security Team
Date: December 3, 2025
Version: 2.0.0
"""

import os
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    PROVIDER = "provider"
    PATIENT = "patient"
    STAFF = "staff"
    VIEWER = "viewer"


class TokenData(BaseModel):
    """Token data model"""
    user_id: str
    email: str
    role: UserRole
    permissions: List[str] = []
    exp: Optional[datetime] = None


class JWTAuth:
    """
    JWT Authentication handler with role-based access control.
    
    Features:
    - HS256 algorithm (HMAC with SHA-256)
    - Configurable token expiration
    - Role-based permissions
    - Token refresh support
    """
    
    # JWT Configuration
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours
    REFRESH_TOKEN_EXPIRE_DAYS = 30
    
    # Get secret key from environment
    SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "CHANGE-THIS-TO-A-SECURE-RANDOM-STRING-AT-LEAST-32-CHARACTERS-LONG"
    )
    
    # Security: Require secret key to be changed
    if SECRET_KEY == "CHANGE-THIS-TO-A-SECURE-RANDOM-STRING-AT-LEAST-32-CHARACTERS-LONG":
        import warnings
        warnings.warn(
            "WARNING: Using default JWT_SECRET_KEY! Change this in production!",
            UserWarning
        )
    
    if len(SECRET_KEY) < 32:
        raise ValueError(
            "JWT_SECRET_KEY must be at least 32 characters long for security"
        )
    
    # HTTP Bearer token scheme
    security = HTTPBearer()
    
    # Role permissions mapping
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [
            "read:all", "write:all", "delete:all", "admin:all",
            "read:patients", "write:patients", "read:providers",
            "write:providers", "read:reports", "write:reports"
        ],
        UserRole.PROVIDER: [
            "read:patients", "write:patients", "read:reports",
            "write:reports", "read:own", "write:own"
        ],
        UserRole.STAFF: [
            "read:patients", "read:reports", "read:own", "write:own"
        ],
        UserRole.PATIENT: [
            "read:own", "write:own"
        ],
        UserRole.VIEWER: [
            "read:own"
        ]
    }
    
    @classmethod
    def create_access_token(
        cls,
        user_id: str,
        email: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            user_id: Unique user identifier
            email: User email address
            role: User role (from UserRole enum)
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
            
        Example:
            >>> token = JWTAuth.create_access_token(
            ...     user_id="usr_123",
            ...     email="doctor@clinic.com",
            ...     role=UserRole.PROVIDER
            ... )
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        # Get permissions for role
        permissions = cls.ROLE_PERMISSIONS.get(role, [])
        
        # Create token payload
        payload = {
            "sub": user_id,  # Subject (user ID)
            "email": email,
            "role": role.value,
            "permissions": permissions,
            "exp": expire,
            "iat": datetime.utcnow(),  # Issued at
            "type": "access"
        }
        
        # Encode token
        encoded_jwt = jwt.encode(
            payload,
            cls.SECRET_KEY,
            algorithm=cls.ALGORITHM
        )
        
        return encoded_jwt
    
    @classmethod
    def create_refresh_token(
        cls,
        user_id: str,
        email: str
    ) -> str:
        """
        Create a JWT refresh token (longer expiration).
        
        Args:
            user_id: Unique user identifier
            email: User email address
            
        Returns:
            Encoded JWT refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            payload,
            cls.SECRET_KEY,
            algorithm=cls.ALGORITHM
        )
        
        return encoded_jwt
    
    @classmethod
    def verify_token(cls, token: str) -> TokenData:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string to verify
            
        Returns:
            TokenData object with user information
            
        Raises:
            HTTPException: If token is invalid, expired, or malformed
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )
            
            # Extract user data
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role_str: str = payload.get("role")
            permissions: List[str] = payload.get("permissions", [])
            exp: int = payload.get("exp")
            
            if user_id is None or email is None:
                raise credentials_exception
            
            # Convert role string to enum
            try:
                role = UserRole(role_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user role in token"
                )
            
            # Convert expiration timestamp to datetime
            exp_datetime = datetime.utcfromtimestamp(exp) if exp else None
            
            return TokenData(
                user_id=user_id,
                email=email,
                role=role,
                permissions=permissions,
                exp=exp_datetime
            )
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
    
    @classmethod
    def get_current_user(
        cls,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> TokenData:
        """
        FastAPI dependency to get current authenticated user.
        
        Usage:
            @app.get("/protected")
            async def protected_route(current_user: TokenData = Depends(JWTAuth.get_current_user)):
                return {"user_id": current_user.user_id}
        
        Args:
            credentials: HTTP Bearer token credentials from request
            
        Returns:
            TokenData object with user information
        """
        token = credentials.credentials
        return cls.verify_token(token)
    
    @classmethod
    def require_role(cls, *allowed_roles: UserRole):
        """
        Create a dependency that requires specific role(s).
        
        Usage:
            @app.get("/admin-only")
            async def admin_route(
                user: TokenData = Depends(JWTAuth.require_role(UserRole.ADMIN))
            ):
                return {"message": "Admin access granted"}
        
        Args:
            *allowed_roles: One or more allowed roles
            
        Returns:
            Dependency function
        """
        def role_checker(
            current_user: TokenData = Depends(cls.get_current_user)
        ) -> TokenData:
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {[r.value for r in allowed_roles]}"
                )
            return current_user
        
        return role_checker
    
    @classmethod
    def require_permission(cls, permission: str):
        """
        Create a dependency that requires a specific permission.
        
        Usage:
            @app.get("/patients")
            async def get_patients(
                user: TokenData = Depends(JWTAuth.require_permission("read:patients"))
            ):
                return patients
        
        Args:
            permission: Required permission string
            
        Returns:
            Dependency function
        """
        def permission_checker(
            current_user: TokenData = Depends(cls.get_current_user)
        ) -> TokenData:
            if permission not in current_user.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required permission: {permission}"
                )
            return current_user
        
        return permission_checker
    
    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> str:
        """
        Create a new access token from a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token string
        """
        # Verify refresh token
        payload = jwt.decode(
            refresh_token,
            cls.SECRET_KEY,
            algorithms=[cls.ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user info from refresh token
        user_id = payload.get("sub")
        email = payload.get("email")
        
        # Note: Role should be retrieved from database, not refresh token
        # For now, we'll use a default or require it to be passed
        # In production, fetch user role from database
        
        # This is a simplified version - in production, fetch role from DB
        role = UserRole.PATIENT  # Default, should be fetched from DB
        
        # Create new access token
        return cls.create_access_token(
            user_id=user_id,
            email=email,
            role=role
        )


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Abena IHR JWT Authentication Middleware - Test")
    print("=" * 60)
    
    # Test token creation
    print("\n1. Creating access token...")
    token = JWTAuth.create_access_token(
        user_id="usr_12345",
        email="doctor@abena-clinic.com",
        role=UserRole.PROVIDER
    )
    print(f"   Token: {token[:50]}...")
    
    # Test token verification
    print("\n2. Verifying token...")
    try:
        token_data = JWTAuth.verify_token(token)
        print(f"   User ID: {token_data.user_id}")
        print(f"   Email: {token_data.email}")
        print(f"   Role: {token_data.role.value}")
        print(f"   Permissions: {token_data.permissions}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test refresh token
    print("\n3. Creating refresh token...")
    refresh_token = JWTAuth.create_refresh_token(
        user_id="usr_12345",
        email="doctor@abena-clinic.com"
    )
    print(f"   Refresh Token: {refresh_token[:50]}...")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Change JWT_SECRET_KEY in production!")
    print("   Set environment variable: export JWT_SECRET_KEY='your-secure-key-here'")

