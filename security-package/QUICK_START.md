# Abena IHR Security Package - Quick Start Guide

**Time:** 5-10 minutes  
**Difficulty:** Easy  
**Goal:** Test security modules locally

---

## 🚀 Installation

### Step 1: Install Dependencies

```bash
cd "Abena Security Package"
pip install -r requirements.txt
```

### Step 2: Set Environment Variables

```bash
# Windows PowerShell
$env:JWT_SECRET_KEY="your-secure-secret-key-at-least-32-characters-long"
$env:DATABASE_URL="postgresql://user:password@localhost:5432/abena_ihr"

# Linux/Mac
export JWT_SECRET_KEY="your-secure-secret-key-at-least-32-characters-long"
export DATABASE_URL="postgresql://user:password@localhost:5432/abena_ihr"
```

**⚠️ IMPORTANT:** Change `JWT_SECRET_KEY` to a secure random string!

---

## 🧪 Quick Tests

### Test 1: Password Security

```bash
python utils/password_security.py
```

**Expected Output:**
```
✓ Password hashing works
✓ Password verification works
✓ Password strength validation works
```

### Test 2: JWT Authentication

```bash
python middleware/auth_middleware.py
```

**Expected Output:**
```
✓ Token creation works
✓ Token verification works
```

### Test 3: Input Validation

```bash
python validation/input_validation.py
```

**Expected Output:**
```
✓ String sanitization works
✓ Email validation works
✓ Phone validation works
```

---

## 💻 Code Examples

### Example 1: Hash and Verify Password

```python
from utils.password_security import PasswordSecurity

# Hash a password
password = "SecureP@ssw0rd123!"
hashed = PasswordSecurity.hash_password(password)
print(f"Hashed: {hashed}")

# Verify password
is_valid = PasswordSecurity.verify_password(password, hashed)
print(f"Valid: {is_valid}")  # True
```

### Example 2: Create JWT Token

```python
from middleware.auth_middleware import JWTAuth, UserRole

# Create access token
token = JWTAuth.create_access_token(
    user_id="usr_123",
    email="doctor@clinic.com",
    role=UserRole.PROVIDER
)

print(f"Token: {token}")

# Verify token
token_data = JWTAuth.verify_token(token)
print(f"User ID: {token_data.user_id}")
print(f"Email: {token_data.email}")
print(f"Role: {token_data.role.value}")
```

### Example 3: Validate Input

```python
from validation.input_validation import InputValidator

# Sanitize user input
user_input = "<script>alert('xss')</script>Hello"
safe = InputValidator.sanitize_string(user_input)
print(f"Safe: {safe}")  # "Hello" (script removed)

# Validate email
email = "user@example.com"
is_valid, error = InputValidator.validate_email(email)
print(f"Valid: {is_valid}")  # True
```

### Example 4: FastAPI Integration

```python
from fastapi import FastAPI, Depends
from middleware.auth_middleware import JWTAuth, TokenData, UserRole
from middleware.rate_limit import RateLimitMiddleware

app = FastAPI()

# Add rate limiting
app.add_middleware(RateLimitMiddleware)

@app.get("/api/patients")
async def get_patients(
    current_user: TokenData = Depends(JWTAuth.get_current_user)
):
    """Protected endpoint - requires authentication"""
    return {"message": f"Hello {current_user.email}"}

@app.get("/api/admin")
async def admin_only(
    current_user: TokenData = Depends(JWTAuth.require_role(UserRole.ADMIN))
):
    """Admin-only endpoint"""
    return {"message": "Admin access granted"}
```

---

## 🔧 Common Use Cases

### Use Case 1: User Registration

```python
from utils.password_security import PasswordSecurity
from validation.input_validation import InputValidator

def register_user(email, password, first_name, last_name):
    # 1. Validate email
    is_valid, error = InputValidator.validate_email(email)
    if not is_valid:
        return {"error": error}
    
    # 2. Validate password strength
    is_valid, msg = PasswordSecurity.validate_password_strength(password)
    if not is_valid:
        return {"error": msg}
    
    # 3. Hash password
    hashed = PasswordSecurity.hash_password(password)
    
    # 4. Sanitize names
    first_name = InputValidator.sanitize_string(first_name)
    last_name = InputValidator.sanitize_string(last_name)
    
    # 5. Save to database (your code here)
    # user = create_user(email, hashed, first_name, last_name)
    
    return {"success": True, "user_id": "usr_123"}
```

### Use Case 2: User Login

```python
from utils.password_security import PasswordSecurity
from middleware.auth_middleware import JWTAuth, UserRole

async def login_user(email, password):
    # 1. Get user from database
    # user = await get_user_by_email(email)
    
    # 2. Verify password
    is_valid = PasswordSecurity.verify_password(password, user['password_hash'])
    if not is_valid:
        return {"error": "Invalid credentials"}
    
    # 3. Create JWT token
    token = JWTAuth.create_access_token(
        user_id=user['id'],
        email=user['email'],
        role=UserRole(user['role'])
    )
    
    return {"access_token": token, "token_type": "bearer"}
```

### Use Case 3: Secure File Upload

```python
from fastapi import UploadFile
from security.file_upload import FileUploadSecurity
from middleware.auth_middleware import JWTAuth, TokenData, Depends

file_security = FileUploadSecurity()

@app.post("/api/upload")
async def upload_file(
    file: UploadFile,
    current_user: TokenData = Depends(JWTAuth.get_current_user)
):
    try:
        metadata = await file_security.upload_file(
            file,
            current_user.user_id,
            scan_virus=True
        )
        return {"success": True, "file": metadata}
    except Exception as e:
        return {"error": str(e)}
```

---

## 🧪 Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_password_security.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: "JWT_SECRET_KEY too short"

**Error:**
```
ValueError: JWT_SECRET_KEY must be at least 32 characters long
```

**Solution:**
```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set it
export JWT_SECRET_KEY="your-generated-key-here"
```

### Issue 2: "Redis connection failed"

**Error:**
```
Redis connection failed: Connection refused
```

**Solution:**
```bash
# Install Redis (Docker)
docker run -d -p 6379:6379 redis

# Or install locally (Linux)
sudo apt-get install redis-server
sudo systemctl start redis
```

### Issue 3: "Module not found"

**Error:**
```
ModuleNotFoundError: No module named 'bcrypt'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 4: "Database connection failed"

**Error:**
```
Database connection failed: connection refused
```

**Solution:**
1. Check PostgreSQL is running
2. Verify DATABASE_URL is correct
3. Check database credentials

---

## 📚 Next Steps

1. ✅ Test all modules locally
2. ✅ Review code examples
3. ✅ Read [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
4. ✅ Plan production deployment
5. ✅ Backup database
6. ✅ Run migration script

---

## 🎯 Quick Reference

### Password Security
- `PasswordSecurity.hash_password(password)` - Hash password
- `PasswordSecurity.verify_password(password, hash)` - Verify password
- `PasswordSecurity.validate_password_strength(password)` - Validate strength

### JWT Authentication
- `JWTAuth.create_access_token(user_id, email, role)` - Create token
- `JWTAuth.verify_token(token)` - Verify token
- `JWTAuth.get_current_user` - FastAPI dependency

### Input Validation
- `InputValidator.sanitize_string(input)` - Sanitize string
- `InputValidator.validate_email(email)` - Validate email
- `InputValidator.validate_phone(phone)` - Validate phone

### Rate Limiting
- `RateLimitMiddleware` - Add to FastAPI app
- Automatically rate limits all endpoints

---

## ✅ Checklist

- [ ] Dependencies installed
- [ ] Environment variables set
- [ ] Password security tested
- [ ] JWT authentication tested
- [ ] Input validation tested
- [ ] Tests passing
- [ ] Ready for production deployment

---

**Ready for production?** See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for complete deployment steps.

