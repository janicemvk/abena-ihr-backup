# Abena IHR Authentication & Authorization Service

## Overview

The Authentication & Authorization Service is a comprehensive security microservice for the Abena IHR system. It provides secure user authentication, authorization, session management, and multi-factor authentication capabilities.

## Features

### 🔐 **Authentication**
- JWT-based authentication with access and refresh tokens
- OAuth2 integration (Google, Microsoft, SAML)
- Multi-factor authentication (TOTP, SMS, Email)
- Password policies and security validation
- Account lockout protection

### 🛡️ **Authorization**
- Role-based access control (RBAC)
- Permission-based authorization
- Resource-level access control
- Dynamic permission evaluation
- Audit logging for all access attempts

### 🔄 **Session Management**
- Redis-based session storage
- Session timeout and renewal
- Concurrent session management
- Session invalidation and cleanup
- Cross-device session tracking

### 📊 **Security & Monitoring**
- Comprehensive audit logging
- Security event monitoring
- Rate limiting and brute force protection
- IP-based access controls
- Real-time security alerts

## Quick Start

### Prerequisites
- Node.js 18+ 
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### 1. Setup

```bash
# Navigate to the auth-service directory
cd foundational-services/auth-service

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### 2. Environment Configuration

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=abena_auth_db
DB_USER=abena_auth_user
DB_PASSWORD=your_secure_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=24h
JWT_REFRESH_EXPIRES_IN=7d

# Session Configuration
SESSION_SECRET=your-super-secret-session-key-change-in-production
SESSION_TTL=86400
```

### 3. Start Services

```bash
# Development mode
npm run dev

# Production mode
npm start

# Using Docker
docker-compose up -d
```

### 4. Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/api-docs
```

## API Endpoints

### Authentication

#### POST `/api/auth/register`
Register a new user account.

#### POST `/api/auth/login`
Authenticate user and receive tokens.

#### POST `/api/auth/refresh`
Refresh access token using refresh token.

#### POST `/api/auth/logout`
Logout user and invalidate tokens.

### Multi-Factor Authentication

#### POST `/api/mfa/setup`
Setup MFA for user account.

#### POST `/api/mfa/verify`
Verify MFA code.

### User Management

#### GET `/api/users/profile`
Get current user profile.

#### PUT `/api/users/profile`
Update user profile.

### Role & Permission Management

#### GET `/api/roles`
Get all roles (admin only).

#### POST `/api/roles`
Create new role (admin only).

## Security Features

### Password Policies
- Minimum length: 8 characters
- Require uppercase letters
- Require lowercase letters
- Require numbers
- Require special characters

### Account Protection
- Maximum login attempts: 5
- Account lockout duration: 15 minutes
- IP-based rate limiting
- Session timeout: 1 hour

### Token Security
- JWT with RS256 algorithm
- Short-lived access tokens (1 hour)
- Long-lived refresh tokens (7 days)
- Token blacklisting

## Docker Deployment

### Docker Compose
```yaml
version: '3.8'

services:
  auth-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    networks:
      - abena-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: abena_auth_db
      POSTGRES_USER: abena_auth_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - abena-network

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - abena-network

volumes:
  postgres_data:
  redis_data:

networks:
  abena-network:
    driver: bridge
```

## Development

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Lint code
npm run lint
```

### Testing
```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- auth.test.js
```

## Support

### Getting Help
- Check the documentation
- Review logs for errors
- Test with minimal configuration
- Create GitHub issue with details

### Contact
- Technical Support: support@abenahealth.org
- Security Issues: security@abenahealth.org
- Development Team: dev@abenahealth.org

---

The Authentication & Authorization Service provides the security foundation for the Abena IHR system, ensuring secure access control and user management across all healthcare applications. 