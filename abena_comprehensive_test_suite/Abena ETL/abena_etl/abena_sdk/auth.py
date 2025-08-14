"""
Abena SDK Authentication

Centralized authentication and authorization handling for the Abena SDK.
All modules should use this for auth operations instead of implementing their own.
"""

import time
import jwt
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from .exceptions import AuthenticationError, AuthorizationError
from .config import AbenaConfig


@dataclass
class AuthToken:
    """Authentication token data"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return time.time() > (self.created_at + self.expires_in - 300)  # 5 min buffer
    
    @property
    def expires_at(self) -> float:
        """Get expiration timestamp"""
        return self.created_at + self.expires_in


@dataclass
class UserPermissions:
    """User permissions and roles"""
    user_id: str
    roles: List[str]
    permissions: List[str]
    organization_id: Optional[str] = None
    department_id: Optional[str] = None


class AbenaAuth:
    """Centralized authentication and authorization for Abena SDK"""
    
    def __init__(self, config: AbenaConfig):
        self.config = config
        self._token: Optional[AuthToken] = None
        self._user_permissions: Optional[UserPermissions] = None
        self._auth_service_url = config.get_api_url("auth")
    
    def authenticate(self, client_id: Optional[str] = None, 
                    client_secret: Optional[str] = None) -> AuthToken:
        """Authenticate using client credentials flow"""
        client_id = client_id or self.config.client_id
        client_secret = client_secret or self.config.client_secret
        
        if not client_id or not client_secret:
            raise AuthenticationError("Client ID and secret are required for authentication")
        
        try:
            response = requests.post(
                f"{self._auth_service_url}/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._token = AuthToken(
                access_token=token_data["access_token"],
                token_type=token_data.get("token_type", "Bearer"),
                expires_in=token_data.get("expires_in", 3600),
                refresh_token=token_data.get("refresh_token"),
                scope=token_data.get("scope")
            )
            
            return self._token
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def authenticate_with_token(self, access_token: str) -> AuthToken:
        """Authenticate using existing access token"""
        self._token = AuthToken(access_token=access_token)
        return self._token
    
    def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        if not self._token:
            if self.config.access_token:
                self.authenticate_with_token(self.config.access_token)
            else:
                self.authenticate()
        
        if self._token.is_expired:
            self._refresh_token()
        
        return self._token.access_token
    
    def _refresh_token(self):
        """Refresh the access token"""
        if not self._token or not self._token.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        try:
            response = requests.post(
                f"{self._auth_service_url}/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self._token.refresh_token
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._token = AuthToken(
                access_token=token_data["access_token"],
                token_type=token_data.get("token_type", "Bearer"),
                expires_in=token_data.get("expires_in", 3600),
                refresh_token=token_data.get("refresh_token", self._token.refresh_token),
                scope=token_data.get("scope")
            )
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    def get_user_permissions(self, user_id: str) -> UserPermissions:
        """Get user permissions and roles"""
        if self._user_permissions and self._user_permissions.user_id == user_id:
            return self._user_permissions
        
        try:
            response = requests.get(
                f"{self._auth_service_url}/users/{user_id}/permissions",
                headers={"Authorization": f"Bearer {self.get_valid_token()}"},
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            self._user_permissions = UserPermissions(
                user_id=data["user_id"],
                roles=data.get("roles", []),
                permissions=data.get("permissions", []),
                organization_id=data.get("organization_id"),
                department_id=data.get("department_id")
            )
            
            return self._user_permissions
            
        except requests.RequestException as e:
            raise AuthorizationError(f"Failed to get user permissions: {str(e)}")
    
    def check_permission(self, user_id: str, permission: str, 
                        resource_id: Optional[str] = None) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(user_id)
        
        # Check direct permission
        if permission in permissions.permissions:
            return True
        
        # Check role-based permissions
        role_permissions = self._get_role_permissions(permissions.roles)
        if permission in role_permissions:
            return True
        
        # Check resource-specific permissions
        if resource_id:
            return self._check_resource_permission(user_id, permission, resource_id)
        
        return False
    
    def _get_role_permissions(self, roles: List[str]) -> List[str]:
        """Get permissions for given roles"""
        try:
            response = requests.post(
                f"{self._auth_service_url}/roles/permissions",
                json={"roles": roles},
                headers={"Authorization": f"Bearer {self.get_valid_token()}"},
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json().get("permissions", [])
            
        except requests.RequestException:
            return []
    
    def _check_resource_permission(self, user_id: str, permission: str, 
                                  resource_id: str) -> bool:
        """Check resource-specific permission"""
        try:
            response = requests.post(
                f"{self._auth_service_url}/resources/check-permission",
                json={
                    "user_id": user_id,
                    "permission": permission,
                    "resource_id": resource_id
                },
                headers={"Authorization": f"Bearer {self.get_valid_token()}"},
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json().get("has_permission", False)
            
        except requests.RequestException:
            return False
    
    def logout(self):
        """Logout and clear tokens"""
        if self._token and self._token.refresh_token:
            try:
                requests.post(
                    f"{self._auth_service_url}/logout",
                    json={"refresh_token": self._token.refresh_token},
                    timeout=self.config.timeout
                )
            except requests.RequestException:
                pass  # Ignore logout errors
        
        self._token = None
        self._user_permissions = None 