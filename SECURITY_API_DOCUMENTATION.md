# ABENA Security API Documentation & Usage Guide

**Version:** 1.0.0  
**Last Updated:** December 5, 2025  
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Protected Endpoints](#protected-endpoints)
4. [Role-Based Access Control](#role-based-access-control)
5. [Rate Limiting](#rate-limiting)
6. [Input Validation](#input-validation)
7. [Error Handling](#error-handling)
8. [Security Best Practices](#security-best-practices)
9. [Code Examples](#code-examples)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The ABENA IHR Security API provides secure authentication and authorization for all healthcare endpoints. It implements:

- ✅ **JWT Token Authentication** - Secure, stateless authentication
- ✅ **Bcrypt Password Hashing** - Industry-standard password security
- ✅ **Role-Based Access Control (RBAC)** - Provider, Patient, Admin roles
- ✅ **Rate Limiting** - Protection against brute force attacks
- ✅ **Input Validation** - SQL injection, XSS, and command injection prevention

### Base URL

```
Production: https://api.abena.com
Development: http://localhost:4002
```

### API Version

All endpoints use `/api/v1/` prefix.

---

## Authentication

### Login Endpoint

Authenticate users and receive a JWT access token.

**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "email": "dr.johnson@abena.com",
  "password": "SecureP@ss123"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "userId": "123",
  "userName": "Dr. John Johnson",
  "userType": "provider",
  "userRole": "provider",
  "expiresAt": "2025-12-05T18:30:00.000Z",
  "message": "Login successful"
}
```

**Error Responses:**

| Status Code | Description | Example Response |
|------------|------------|------------------|
| 400 | Invalid email format | `{"detail": "Invalid email format: ..."}` |
| 401 | Invalid credentials | `{"detail": "Invalid credentials"}` |
| 429 | Rate limit exceeded | `{"detail": "Rate limit exceeded. Please try again later."}` |
| 500 | Server error | `{"detail": "Authentication failed"}` |

**Security Features:**
- Email format validation
- Bcrypt password verification
- Rate limiting (prevents brute force attacks)
- JWT token generation with 8-hour expiration

---

## Protected Endpoints

Most ABENA IHR endpoints require authentication. Include the JWT token in the `Authorization` header.

### Using JWT Tokens

**Header Format:**
```
Authorization: Bearer <your-jwt-token>
```

**Example:**
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     http://localhost:4002/api/v1/doctors
```

### Protected Endpoints List

| Endpoint | Method | Description | Required Role |
|----------|--------|-------------|---------------|
| `/api/v1/doctors` | GET | Get all doctors | Any authenticated user |
| `/api/v1/prescriptions` | GET | Get prescriptions | Provider, Patient |
| `/api/v1/prescriptions` | POST | Create prescription | Provider |
| `/api/v1/prescriptions/{id}` | PUT | Update prescription | Provider |
| `/api/v1/prescriptions/{id}` | DELETE | Delete prescription | Provider |
| `/api/v1/patients` | POST | Create patient | Provider, Admin |
| `/api/v1/providers/{id}/patients` | GET | Get provider's patients | Provider |
| `/api/v1/lab-requests` | POST | Create lab request | Provider |
| `/api/v1/lab-results` | GET | Get lab results | Provider, Patient |
| `/api/v1/documents` | GET | Get documents | Provider, Patient |
| `/api/v1/documents/upload` | POST | Upload document | Provider, Patient |

**Note:** Some endpoints may have additional role-based restrictions. See [Role-Based Access Control](#role-based-access-control) section.

---

## Role-Based Access Control

ABENA IHR supports three user roles:

### User Roles

| Role | Value | Description |
|------|-------|-------------|
| Provider | `provider` | Healthcare providers (doctors, nurses) |
| Patient | `patient` | Patients |
| Admin | `admin` | System administrators |

### Role Permissions

**Provider:**
- ✅ Create, read, update, delete prescriptions
- ✅ Create lab requests
- ✅ View all patients
- ✅ Upload documents
- ✅ View lab results

**Patient:**
- ✅ View own prescriptions
- ✅ View own lab results
- ✅ View own documents
- ✅ Upload own documents
- ❌ Cannot create prescriptions
- ❌ Cannot view other patients' data

**Admin:**
- ✅ All provider permissions
- ✅ System management
- ✅ User management

### Checking User Role

The JWT token contains the user's role. Decode the token to access role information:

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
decoded = jwt.decode(token, options={"verify_signature": False})
user_role = decoded.get("role")  # "provider", "patient", or "admin"
```

---

## Rate Limiting

Rate limiting protects against brute force attacks and API abuse.

### Rate Limits

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Login endpoint | 5 requests | 15 minutes |
| General API endpoints | 100 requests | 1 minute |
| File upload endpoints | 10 requests | 1 minute |

### Rate Limit Headers

When rate limiting is active, the API returns these headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1638720000
```

### Rate Limit Exceeded Response

**Status Code:** `429 Too Many Requests`

```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

**Handling Rate Limits:**
- Implement exponential backoff
- Cache responses when possible
- Use batch endpoints when available
- Monitor `X-RateLimit-Remaining` header

---

## Input Validation

All user inputs are validated and sanitized to prevent security vulnerabilities.

### Email Validation

Emails must conform to RFC 5322 standards:

```json
✅ Valid: "dr.johnson@abena.com"
✅ Valid: "patient+test@example.org"
❌ Invalid: "not-an-email"
❌ Invalid: "user@"
```

### Password Requirements

**For New Passwords:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

**Example:**
```
✅ Valid: "SecureP@ss123"
❌ Invalid: "password" (too weak)
❌ Invalid: "12345678" (no letters)
```

### SQL Injection Prevention

All database queries use parameterized statements. User inputs are automatically sanitized.

### XSS Prevention

All string inputs are sanitized using `bleach` library to remove potentially dangerous HTML/JavaScript.

### Command Injection Prevention

File paths and system commands are validated to prevent command injection attacks.

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Status Code | Meaning | Common Causes |
|------------|---------|---------------|
| 400 | Bad Request | Invalid input format, missing required fields |
| 401 | Unauthorized | Missing or invalid JWT token, expired token |
| 403 | Forbidden | Insufficient permissions for requested action |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error, database connection issue |

### Token Expiration

JWT tokens expire after 8 hours. When a token expires:

**Response:** `401 Unauthorized`

```json
{
  "detail": "Token has expired"
}
```

**Solution:** Re-authenticate using the login endpoint to get a new token.

### Invalid Token

**Response:** `401 Unauthorized`

```json
{
  "detail": "Invalid authentication credentials"
}
```

**Solution:** Verify the token is correctly formatted and not corrupted.

---

## Security Best Practices

### 1. Token Storage

**✅ DO:**
- Store tokens in `httpOnly` cookies (server-side)
- Use `localStorage` or `sessionStorage` for client-side apps (with HTTPS)
- Implement token refresh mechanism
- Clear tokens on logout

**❌ DON'T:**
- Store tokens in plain text
- Include tokens in URLs or query parameters
- Share tokens between users
- Store tokens in browser cookies without `httpOnly` flag

### 2. Password Security

**✅ DO:**
- Use strong, unique passwords
- Implement password reset functionality
- Hash passwords with bcrypt (already implemented)
- Never log passwords

**❌ DON'T:**
- Send passwords via email
- Store passwords in plain text
- Use default passwords
- Reuse passwords across services

### 3. HTTPS Only

**✅ DO:**
- Always use HTTPS in production
- Enforce HTTPS redirects
- Use secure cookies (`Secure` flag)

**❌ DON'T:**
- Send tokens over HTTP
- Allow mixed content (HTTP/HTTPS)

### 4. API Security

**✅ DO:**
- Validate all inputs
- Use parameterized queries
- Implement rate limiting
- Log security events
- Monitor for suspicious activity

**❌ DON'T:**
- Trust client-side validation alone
- Expose sensitive data in error messages
- Allow unlimited API requests
- Skip input sanitization

### 5. Error Messages

**✅ DO:**
- Return generic error messages to users
- Log detailed errors server-side
- Avoid exposing system internals

**❌ DON'T:**
- Reveal database structure
- Expose file paths
- Show stack traces to users

---

## Code Examples

### JavaScript/TypeScript (Frontend)

#### Login and Store Token

```javascript
async function login(email, password) {
  try {
    const response = await fetch('http://localhost:4002/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Store token securely
    localStorage.setItem('authToken', data.access_token);
    localStorage.setItem('userRole', data.userRole);
    localStorage.setItem('userId', data.userId);
    
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}
```

#### Making Authenticated Requests

```javascript
async function getDoctors() {
  const token = localStorage.getItem('authToken');
  
  try {
    const response = await fetch('http://localhost:4002/api/v1/doctors', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 401) {
      // Token expired, redirect to login
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      return;
    }

    if (!response.ok) {
      throw new Error('Failed to fetch doctors');
    }

    const doctors = await response.json();
    return doctors;
  } catch (error) {
    console.error('Error fetching doctors:', error);
    throw error;
  }
}
```

#### Axios Interceptor Example

```javascript
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:4002/api/v1',
});

// Add token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Use the instance
api.get('/doctors').then(response => {
  console.log(response.data);
});
```

### Python (Backend/Testing)

#### Login and Get Token

```python
import requests

def login(email: str, password: str) -> dict:
    """Login and return authentication data"""
    url = "http://localhost:4002/api/v1/auth/login"
    payload = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    return {
        "token": data["access_token"],
        "user_id": data["userId"],
        "role": data["userRole"]
    }

# Usage
auth_data = login("dr.johnson@abena.com", "SecureP@ss123")
token = auth_data["token"]
```

#### Making Authenticated Requests

```python
import requests

def get_doctors(token: str) -> list:
    """Get list of doctors with authentication"""
    url = "http://localhost:4002/api/v1/doctors"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

# Usage
doctors = get_doctors(token)
```

#### Using Requests Session

```python
import requests

class AbenaAPIClient:
    def __init__(self, base_url: str = "http://localhost:4002/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def login(self, email: str, password: str):
        """Login and store token"""
        url = f"{self.base_url}/auth/login"
        response = self.session.post(url, json={"email": email, "password": password})
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}"
        })
        return data
    
    def get_doctors(self):
        """Get doctors"""
        url = f"{self.base_url}/doctors"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def create_prescription(self, prescription_data: dict):
        """Create prescription (requires provider role)"""
        url = f"{self.base_url}/prescriptions"
        response = self.session.post(url, json=prescription_data)
        response.raise_for_status()
        return response.json()

# Usage
client = AbenaAPIClient()
client.login("dr.johnson@abena.com", "SecureP@ss123")
doctors = client.get_doctors()
```

### PowerShell (Testing/Admin)

#### Login Function

```powershell
function Invoke-AbenaLogin {
    param(
        [string]$Email,
        [string]$Password,
        [string]$BaseUrl = "http://localhost:4002"
    )
    
    $body = @{
        email = $Email
        password = $Password
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v1/auth/login" `
            -Method Post `
            -Body $body `
            -ContentType "application/json"
        
        return $response
    }
    catch {
        Write-Error "Login failed: $($_.Exception.Message)"
        throw
    }
}

# Usage
$auth = Invoke-AbenaLogin -Email "dr.johnson@abena.com" -Password "SecureP@ss123"
$token = $auth.access_token
```

#### Authenticated API Call

```powershell
function Invoke-AbenaAPI {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [object]$Body = $null,
        [string]$Token
    )
    
    $url = "http://localhost:4002/api/v1/$Endpoint"
    $headers["Authorization"] = "Bearer $Token"
    $headers["Content-Type"] = "application/json"
    
    $params = @{
        Uri = $url
        Method = $Method
        Headers = $Headers
    }
    
    if ($Body) {
        $params["Body"] = ($Body | ConvertTo-Json)
    }
    
    try {
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        Write-Error "API call failed: $($_.Exception.Message)"
        throw
    }
}

# Usage
$token = (Invoke-AbenaLogin -Email "dr.johnson@abena.com" -Password "SecureP@ss123").access_token
$doctors = Invoke-AbenaAPI -Endpoint "doctors" -Token $token
```

### cURL Examples

#### Login

```bash
curl -X POST http://localhost:4002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.johnson@abena.com",
    "password": "SecureP@ss123"
  }'
```

#### Get Doctors (with token)

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:4002/api/v1/doctors \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

#### Create Prescription (Provider only)

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:4002/api/v1/prescriptions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "123",
    "medication": "Aspirin 100mg",
    "dosage": "1 tablet daily",
    "instructions": "Take with food"
  }'
```

---

## Troubleshooting

### Common Issues

#### 1. "Invalid credentials" Error

**Possible Causes:**
- Incorrect email or password
- Password not migrated to bcrypt (check database)
- Account locked due to too many failed attempts

**Solutions:**
- Verify email and password are correct
- Check if password was migrated: `SELECT hashed_password FROM users WHERE email = '...'`
- Wait 15 minutes if rate limited
- Contact administrator to reset password

#### 2. "Token has expired" Error

**Cause:** JWT token expired (8-hour lifetime)

**Solution:** Re-authenticate using login endpoint

```javascript
// Auto-refresh token example
if (response.status === 401 && error.detail === "Token has expired") {
  // Re-login
  const newAuth = await login(email, password);
  // Retry original request with new token
}
```

#### 3. "Rate limit exceeded" Error

**Cause:** Too many requests in short time period

**Solutions:**
- Wait for rate limit window to reset
- Implement request caching
- Use batch endpoints when available
- Contact administrator for higher limits if needed

#### 4. "Invalid email format" Error

**Cause:** Email doesn't match RFC 5322 format

**Solution:** Validate email before sending:
```javascript
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
  alert("Please enter a valid email address");
}
```

#### 5. Redis Connection Warnings

**Symptom:** Rate limiting falls back to in-memory storage

**Solution:** Ensure Redis container is running:
```bash
docker-compose up -d redis
```

Verify Redis connection:
```bash
docker exec -it abena-redis redis-cli ping
# Should return: PONG
```

#### 6. Import Errors in Security Modules

**Symptom:** `ModuleNotFoundError: No module named 'bcrypt'`

**Solution:** Install dependencies:
```bash
cd abena_ihr
pip install -r requirements.txt
```

Rebuild Docker container:
```bash
docker-compose build abena-ihr
docker-compose up -d abena-ihr
```

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export LOG_LEVEL=DEBUG
```

Or in `docker-compose.yml`:
```yaml
environment:
  - LOG_LEVEL=DEBUG
```

### Getting Help

1. **Check Logs:**
   ```bash
   docker-compose logs abena-ihr
   ```

2. **Verify Security Integration:**
   ```bash
   curl http://localhost:4002/health
   ```

3. **Test Database Connection:**
   ```bash
   docker exec -it abena-postgres psql -U abena_user -d abena_ihr -c "SELECT COUNT(*) FROM users;"
   ```

4. **Review Documentation:**
   - `SECURITY_INTEGRATION_STATUS.md` - Current integration status
   - `security-package/README.md` - Security package documentation
   - `security-package/QUICK_START.md` - Quick start guide

---

## Appendix

### JWT Token Structure

Decoded JWT token example:

```json
{
  "user_id": "123",
  "email": "dr.johnson@abena.com",
  "role": "provider",
  "exp": 1638720000,
  "iat": 1638691200
}
```

**Fields:**
- `user_id`: Unique user identifier
- `email`: User's email address
- `role`: User role (provider, patient, admin)
- `exp`: Token expiration timestamp (Unix epoch)
- `iat`: Token issued at timestamp (Unix epoch)

### Environment Variables

Required environment variables for security:

```bash
# JWT Secret Key (32+ characters, keep secure!)
JWT_SECRET_KEY=your-secure-random-key-minimum-32-characters-long

# Redis URL (for rate limiting)
REDIS_URL=redis://redis:6379/0

# Database URL
DATABASE_URL=postgresql://abena_user:password@postgres:5432/abena_ihr
```

### Security Headers

The API sets these security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## Changelog

### Version 1.0.0 (December 5, 2025)
- Initial security API documentation
- JWT authentication implementation
- Bcrypt password hashing
- Rate limiting with Redis
- Input validation and sanitization
- Role-based access control

---

## Support

For security-related issues or questions:

1. Review this documentation
2. Check `SECURITY_INTEGRATION_STATUS.md` for current status
3. Review security package documentation in `security-package/`
4. Contact the development team

---

**Last Updated:** December 5, 2025  
**Document Version:** 1.0.0  
**Status:** ✅ Production Ready

