/**
 * Abena IHR Auth Service Configuration
 * ====================================
 * 
 * Centralized configuration management for authentication and authorization service
 */

require('dotenv').config();

const config = {
  // ======================================================
  // ENVIRONMENT CONFIGURATION
  // ======================================================
  
  environment: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT, 10) || 8000,
  host: process.env.HOST || '0.0.0.0',
  
  // ======================================================
  // DATABASE CONFIGURATION
  // ======================================================
  
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT, 10) || 5432,
    name: process.env.DB_NAME || 'abena_auth_db',
    user: process.env.DB_USER || 'abena_auth_user',
    password: process.env.DB_PASSWORD || 'secure_password_123',
    ssl: process.env.DB_SSL === 'true',
    maxConnections: parseInt(process.env.DB_MAX_CONNECTIONS, 10) || 20,
    idleTimeoutMillis: parseInt(process.env.DB_IDLE_TIMEOUT, 10) || 30000,
    connectionTimeoutMillis: parseInt(process.env.DB_CONNECTION_TIMEOUT, 10) || 2000,
  },
  
  // ======================================================
  // REDIS CONFIGURATION
  // ======================================================
  
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT, 10) || 6379,
    password: process.env.REDIS_PASSWORD || 'redis_password_123',
    db: parseInt(process.env.REDIS_DB, 10) || 0,
    keyPrefix: process.env.REDIS_KEY_PREFIX || 'auth:',
    retryDelayOnFailover: parseInt(process.env.REDIS_RETRY_DELAY, 10) || 100,
    maxRetriesPerRequest: parseInt(process.env.REDIS_MAX_RETRIES, 10) || 3,
  },
  
  // ======================================================
  // JWT CONFIGURATION
  // ======================================================
  
  jwt: {
    secret: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
    algorithm: process.env.JWT_ALGORITHM || 'HS256',
    expiresIn: process.env.JWT_EXPIRES_IN || '24h',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
    issuer: process.env.JWT_ISSUER || 'abena-ihr-auth',
    audience: process.env.JWT_AUDIENCE || 'abena-ihr-users',
    clockTolerance: parseInt(process.env.JWT_CLOCK_TOLERANCE, 10) || 30,
  },
  
  // ======================================================
  // SESSION CONFIGURATION
  // ======================================================
  
  session: {
    secret: process.env.SESSION_SECRET || 'your-super-secret-session-key-change-in-production',
    name: process.env.SESSION_NAME || 'abena_auth_session',
    ttl: parseInt(process.env.SESSION_TTL, 10) || 86400, // 24 hours
    rolling: process.env.SESSION_ROLLING === 'true',
    secure: process.env.SESSION_SECURE === 'true',
    httpOnly: process.env.SESSION_HTTP_ONLY !== 'false',
    sameSite: process.env.SESSION_SAME_SITE || 'strict',
  },
  
  // ======================================================
  // OAUTH CONFIGURATION
  // ======================================================
  
  oauth: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: process.env.GOOGLE_CALLBACK_URL || 'http://localhost:8000/api/oauth/google/callback',
      scope: ['profile', 'email'],
      enabled: process.env.GOOGLE_OAUTH_ENABLED === 'true',
    },
    microsoft: {
      clientId: process.env.MICROSOFT_CLIENT_ID,
      clientSecret: process.env.MICROSOFT_CLIENT_SECRET,
      callbackURL: process.env.MICROSOFT_CALLBACK_URL || 'http://localhost:8000/api/oauth/microsoft/callback',
      scope: ['user.read'],
      enabled: process.env.MICROSOFT_OAUTH_ENABLED === 'true',
    },
    saml: {
      entryPoint: process.env.SAML_ENTRY_POINT,
      issuer: process.env.SAML_ISSUER || 'abena-ihr-auth',
      cert: process.env.SAML_CERT,
      callbackURL: process.env.SAML_CALLBACK_URL || 'http://localhost:8000/api/oauth/saml/callback',
      enabled: process.env.SAML_OAUTH_ENABLED === 'true',
    },
  },
  
  // ======================================================
  // MFA CONFIGURATION
  // ======================================================
  
  mfa: {
    totp: {
      enabled: process.env.MFA_TOTP_ENABLED !== 'false',
      issuer: process.env.MFA_TOTP_ISSUER || 'Abena IHR',
      algorithm: process.env.MFA_TOTP_ALGORITHM || 'sha1',
      digits: parseInt(process.env.MFA_TOTP_DIGITS, 10) || 6,
      period: parseInt(process.env.MFA_TOTP_PERIOD, 10) || 30,
      window: parseInt(process.env.MFA_TOTP_WINDOW, 10) || 1,
    },
    sms: {
      enabled: process.env.MFA_SMS_ENABLED === 'true',
      provider: process.env.MFA_SMS_PROVIDER || 'twilio',
      twilio: {
        accountSid: process.env.TWILIO_ACCOUNT_SID,
        authToken: process.env.TWILIO_AUTH_TOKEN,
        fromNumber: process.env.TWILIO_FROM_NUMBER,
      },
    },
    email: {
      enabled: process.env.MFA_EMAIL_ENABLED === 'true',
      provider: process.env.MFA_EMAIL_PROVIDER || 'nodemailer',
      nodemailer: {
        host: process.env.EMAIL_HOST,
        port: parseInt(process.env.EMAIL_PORT, 10) || 587,
        secure: process.env.EMAIL_SECURE === 'true',
        auth: {
          user: process.env.EMAIL_USER,
          pass: process.env.EMAIL_PASS,
        },
      },
    },
  },
  
  // ======================================================
  // SECURITY CONFIGURATION
  // ======================================================
  
  security: {
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS, 10) || 12,
    passwordMinLength: parseInt(process.env.PASSWORD_MIN_LENGTH, 10) || 8,
    passwordRequireUppercase: process.env.PASSWORD_REQUIRE_UPPERCASE !== 'false',
    passwordRequireLowercase: process.env.PASSWORD_REQUIRE_LOWERCASE !== 'false',
    passwordRequireNumbers: process.env.PASSWORD_REQUIRE_NUMBERS !== 'false',
    passwordRequireSymbols: process.env.PASSWORD_REQUIRE_SYMBOLS !== 'false',
    maxLoginAttempts: parseInt(process.env.MAX_LOGIN_ATTEMPTS, 10) || 5,
    lockoutDuration: parseInt(process.env.LOCKOUT_DURATION, 10) || 900, // 15 minutes
    sessionTimeout: parseInt(process.env.SESSION_TIMEOUT, 10) || 3600, // 1 hour
    csrfProtection: process.env.CSRF_PROTECTION !== 'false',
    rateLimitWindow: parseInt(process.env.RATE_LIMIT_WINDOW, 10) || 900000, // 15 minutes
    rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX, 10) || 100,
  },
  
  // ======================================================
  // CORS CONFIGURATION
  // ======================================================
  
  corsOrigins: process.env.CORS_ORIGINS 
    ? process.env.CORS_ORIGINS.split(',') 
    : ['http://localhost:3000', 'http://localhost:3001'],
  
  // ======================================================
  // LOGGING CONFIGURATION
  // ======================================================
  
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'json',
    file: process.env.LOG_FILE || './logs/auth-service.log',
    maxSize: process.env.LOG_MAX_SIZE || '10m',
    maxFiles: parseInt(process.env.LOG_MAX_FILES, 10) || 5,
  },
  
  // ======================================================
  // AUDIT CONFIGURATION
  // ======================================================
  
  audit: {
    enabled: process.env.AUDIT_ENABLED !== 'false',
    logLevel: process.env.AUDIT_LOG_LEVEL || 'info',
    retentionDays: parseInt(process.env.AUDIT_RETENTION_DAYS, 10) || 365,
    sensitiveFields: ['password', 'token', 'secret', 'key'],
  },
  
  // ======================================================
  // EMAIL CONFIGURATION
  // ======================================================
  
  email: {
    from: process.env.EMAIL_FROM || 'noreply@abenahealth.org',
    replyTo: process.env.EMAIL_REPLY_TO || 'support@abenahealth.org',
    templates: {
      welcome: process.env.EMAIL_WELCOME_TEMPLATE || './templates/email/welcome.html',
      resetPassword: process.env.EMAIL_RESET_TEMPLATE || './templates/email/reset-password.html',
      verifyEmail: process.env.EMAIL_VERIFY_TEMPLATE || './templates/email/verify-email.html',
      mfaCode: process.env.EMAIL_MFA_TEMPLATE || './templates/email/mfa-code.html',
    },
  },
  
  // ======================================================
  // INTEGRATION CONFIGURATION
  // ======================================================
  
  integrations: {
    unifiedDataService: {
      url: process.env.UNIFIED_DATA_SERVICE_URL || 'http://localhost:8001',
      timeout: parseInt(process.env.UNIFIED_DATA_SERVICE_TIMEOUT, 10) || 5000,
    },
    clinicalService: {
      url: process.env.CLINICAL_SERVICE_URL || 'http://localhost:8002',
      timeout: parseInt(process.env.CLINICAL_SERVICE_TIMEOUT, 10) || 5000,
    },
    analyticsService: {
      url: process.env.ANALYTICS_SERVICE_URL || 'http://localhost:8003',
      timeout: parseInt(process.env.ANALYTICS_SERVICE_TIMEOUT, 10) || 5000,
    },
  },
  
  // ======================================================
  // FEATURE FLAGS
  // ======================================================
  
  features: {
    registration: process.env.FEATURE_REGISTRATION !== 'false',
    emailVerification: process.env.FEATURE_EMAIL_VERIFICATION !== 'false',
    passwordReset: process.env.FEATURE_PASSWORD_RESET !== 'false',
    mfa: process.env.FEATURE_MFA !== 'false',
    oauth: process.env.FEATURE_OAUTH !== 'false',
    sessionManagement: process.env.FEATURE_SESSION_MANAGEMENT !== 'false',
    auditLogging: process.env.FEATURE_AUDIT_LOGGING !== 'false',
    rateLimiting: process.env.FEATURE_RATE_LIMITING !== 'false',
  },
};

// ======================================================
// VALIDATION
// ======================================================

// Validate required configuration
const validateConfig = () => {
  const errors = [];
  
  // Check JWT secret
  if (!config.jwt.secret || config.jwt.secret === 'your-super-secret-jwt-key-change-in-production') {
    errors.push('JWT_SECRET must be set to a secure value');
  }
  
  // Check session secret
  if (!config.session.secret || config.session.secret === 'your-super-secret-session-key-change-in-production') {
    errors.push('SESSION_SECRET must be set to a secure value');
  }
  
  // Check database configuration
  if (!config.database.password || config.database.password === 'secure_password_123') {
    errors.push('DB_PASSWORD must be set to a secure value');
  }
  
  // Check Redis configuration
  if (!config.redis.password || config.redis.password === 'redis_password_123') {
    errors.push('REDIS_PASSWORD must be set to a secure value');
  }
  
  // Check production environment
  if (config.environment === 'production') {
    if (config.session.secure !== true) {
      errors.push('SESSION_SECURE must be true in production');
    }
    
    if (!config.oauth.google.clientId || !config.oauth.google.clientSecret) {
      console.warn('Google OAuth not configured for production');
    }
    
    if (!config.oauth.microsoft.clientId || !config.oauth.microsoft.clientSecret) {
      console.warn('Microsoft OAuth not configured for production');
    }
  }
  
  if (errors.length > 0) {
    console.error('Configuration validation failed:');
    errors.forEach(error => console.error(`- ${error}`));
    process.exit(1);
  }
};

// Run validation in non-test environments
if (config.environment !== 'test') {
  validateConfig();
}

module.exports = config; 