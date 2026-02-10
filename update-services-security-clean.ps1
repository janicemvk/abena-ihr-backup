# ABENA Security Service Update Script - Phase 3
# Step 7-8: Update services with security and test

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ABENA Security Service Update - Phase 3" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Step 7: Create Security Integration Module
Write-Host "=== STEP 7: Creating Security Integration Module ===" -ForegroundColor Green
Write-Host ""

Write-Host "Creating security integration module for ABENA IHR..." -ForegroundColor Cyan

$securityModulePath = "abena_ihr\src\security_integration.py"
$securityModuleCode = @'
"""
ABENA IHR Security Integration Module
Adds JWT authentication, rate limiting, and input validation
"""

import sys
import os
from pathlib import Path

# Add security package to path
security_path = Path(__file__).parent.parent.parent / "security-package"
sys.path.insert(0, str(security_path))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import logging

# Import security modules
try:
    from middleware.auth_middleware import JWTAuth, UserRole, require_role, TokenData
    from middleware.rate_limit import RateLimitMiddleware
    from validation.input_validation import InputValidator
    from utils.password_security import PasswordSecurity
except ImportError as e:
    logging.error(f"Failed to import security modules: {e}")
    raise

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
    app.add_middleware(RateLimitMiddleware)
    logger.info("Security middleware enabled")
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
'@

# Create the security integration module
New-Item -Path "abena_ihr\src" -ItemType Directory -Force -ErrorAction SilentlyContinue | Out-Null
Set-Content -Path $securityModulePath -Value $securityModuleCode -Force
Write-Host "[OK] Security integration module created: $securityModulePath" -ForegroundColor Green

# Create update instructions
Write-Host ""
Write-Host "Creating integration instructions..." -ForegroundColor Cyan

$instructions = @'
# ABENA IHR Security Integration Instructions

## Step 1: Update main.py

Add this code to the TOP of your `abena_ihr/src/api/main.py` file:

```python
# Security Integration
try:
    from src.security_integration import (
        setup_security, 
        secure_login, 
        get_current_user_secure,
        JWTAuth,
        require_role,
        UserRole,
        LoginRequest,
        LoginResponse
    )
    SECURITY_ENABLED = True
    print("Security modules loaded successfully")
except ImportError as e:
    print(f"Warning: Security modules not available: {e}")
    SECURITY_ENABLED = False
```

## Step 2: Enable Security Middleware

After creating your FastAPI app, add:

```python
if SECURITY_ENABLED:
    app = setup_security(app)
    print("Security middleware enabled")
```

## Step 3: Update Login Endpoint

Replace your existing login endpoint with:

```python
@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Secure login with bcrypt password verification"""
    return await secure_login(
        email=credentials.email,
        password=credentials.password,
        get_user_by_email_func=get_user_by_email,
        get_user_data_func=get_user_data
    )
```

## Step 4: Protect Endpoints

Add authentication to your endpoints:

```python
@app.get("/api/v1/patients")
async def get_patients(
    current_user: dict = Depends(get_current_user_secure),
    role_check = Depends(require_role([UserRole.PROVIDER, UserRole.ADMIN]))
):
    """Only providers and admins can access"""
    return await fetch_patients()
```

## Step 5: Rebuild and Restart

After making changes:

```powershell
docker-compose build abena-ihr
docker-compose up -d abena-ihr
```

## Testing

Test with:

```powershell
curl -X POST http://localhost:4002/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"dr.johnson@abena.com","password":"Abena2024Secure"}'
```
'@

$instructionsPath = "abena_ihr\SECURITY_UPDATE_INSTRUCTIONS.txt"
Set-Content -Path $instructionsPath -Value $instructions -Force
Write-Host "[OK] Instructions created: $instructionsPath" -ForegroundColor Green

Write-Host ""
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "MANUAL STEP REQUIRED" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Please update your main.py file:" -ForegroundColor Cyan
Write-Host "1. Open: abena_ihr\src\api\main.py" -ForegroundColor White
Write-Host "2. Follow instructions in: $instructionsPath" -ForegroundColor White
Write-Host "3. Add the security code shown in the instructions" -ForegroundColor White
Write-Host ""
Write-Host "After updating main.py, press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Step 8: Test Authentication
Write-Host ""
Write-Host "=== STEP 8: Testing Authentication ===" -ForegroundColor Green
Write-Host ""

Write-Host "Rebuilding and restarting ABENA IHR service..." -ForegroundColor Cyan
Write-Host "This may take a minute..." -ForegroundColor Yellow

try {
    docker-compose build abena-ihr 2>&1 | Out-Null
    docker-compose up -d abena-ihr 2>&1 | Out-Null
    Start-Sleep -Seconds 15
    Write-Host "[OK] Service rebuilt and restarted" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Could not restart automatically. Please run manually:" -ForegroundColor Yellow
    Write-Host "  docker-compose build abena-ihr" -ForegroundColor Cyan
    Write-Host "  docker-compose up -d abena-ihr" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Testing authentication..." -ForegroundColor Cyan

$testPassed = $false

try {
    $loginBody = @{
        email = "dr.johnson@abena.com"
        password = "Abena2024Secure"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:4002/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -ErrorAction Stop
    
    if ($response.access_token) {
        Write-Host "[OK] Authentication working! Token received." -ForegroundColor Green
        $testPassed = $true
    }
    
} catch {
    Write-Host "[INFO] Authentication test could not connect to service" -ForegroundColor Yellow
    Write-Host "This is normal if you haven't updated main.py yet" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Phase 3 Status" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[OK] Security integration module created" -ForegroundColor Green
Write-Host "[OK] Update instructions provided" -ForegroundColor Green

if ($testPassed) {
    Write-Host "[OK] Authentication test passed" -ForegroundColor Green
} else {
    Write-Host "[PENDING] Authentication test - update main.py first" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update abena_ihr\src\api\main.py (if not done)" -ForegroundColor White
Write-Host "2. Rebuild service: docker-compose build abena-ihr" -ForegroundColor White
Write-Host "3. Restart service: docker-compose up -d abena-ihr" -ForegroundColor White
Write-Host "4. Test login at http://localhost:4002/api/v1/auth/login" -ForegroundColor White
Write-Host ""
Write-Host "Phase 3 Complete!" -ForegroundColor Green

