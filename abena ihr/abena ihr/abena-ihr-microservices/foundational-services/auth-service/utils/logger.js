/**
 * Abena IHR Auth Service Logger
 * =============================
 * 
 * Centralized logging utility using Winston with:
 * - Multiple transports (console, file, syslog)
 * - Log rotation and compression
 * - Structured logging with metadata
 * - Environment-specific configurations
 * - Security and audit logging
 */

const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');
const config = require('../config');

// ======================================================
// LOG FORMATS
// ======================================================

// JSON format for structured logging
const jsonFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    return JSON.stringify({
      timestamp,
      level,
      message,
      service: 'auth-service',
      environment: config.environment,
      ...meta,
    });
  })
);

// Console format for development
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let log = `${timestamp} [${level}]: ${message}`;
    
    if (Object.keys(meta).length > 0) {
      log += ` ${JSON.stringify(meta)}`;
    }
    
    return log;
  })
);

// ======================================================
// TRANSPORTS
// ======================================================

const transports = [];

// Console transport (always enabled)
transports.push(
  new winston.transports.Console({
    level: config.logging.level,
    format: config.environment === 'production' ? jsonFormat : consoleFormat,
    handleExceptions: true,
    handleRejections: true,
  })
);

// File transport for production
if (config.environment === 'production') {
  // Main application logs
  transports.push(
    new DailyRotateFile({
      filename: config.logging.file,
      datePattern: 'YYYY-MM-DD',
      zippedArchive: true,
      maxSize: config.logging.maxSize,
      maxFiles: config.logging.maxFiles,
      level: config.logging.level,
      format: jsonFormat,
      handleExceptions: true,
      handleRejections: true,
    })
  );
  
  // Error logs
  transports.push(
    new DailyRotateFile({
      filename: config.logging.file.replace('.log', '.error.log'),
      datePattern: 'YYYY-MM-DD',
      zippedArchive: true,
      maxSize: config.logging.maxSize,
      maxFiles: config.logging.maxFiles,
      level: 'error',
      format: jsonFormat,
      handleExceptions: true,
      handleRejections: true,
    })
  );
  
  // Audit logs
  if (config.audit.enabled) {
    transports.push(
      new DailyRotateFile({
        filename: config.logging.file.replace('.log', '.audit.log'),
        datePattern: 'YYYY-MM-DD',
        zippedArchive: true,
        maxSize: config.logging.maxSize,
        maxFiles: config.logging.maxFiles,
        level: config.audit.logLevel,
        format: jsonFormat,
      })
    );
  }
}

// ======================================================
// LOGGER INSTANCE
// ======================================================

const logger = winston.createLogger({
  level: config.logging.level,
  format: jsonFormat,
  transports,
  exitOnError: false,
});

// ======================================================
// AUDIT LOGGER
// ======================================================

const auditLogger = winston.createLogger({
  level: config.audit.logLevel,
  format: jsonFormat,
  transports: config.environment === 'production' 
    ? [
        new DailyRotateFile({
          filename: config.logging.file.replace('.log', '.audit.log'),
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: config.logging.maxSize,
          maxFiles: config.logging.maxFiles,
          level: config.audit.logLevel,
          format: jsonFormat,
        })
      ]
    : [
        new winston.transports.Console({
          level: config.audit.logLevel,
          format: consoleFormat,
        })
      ],
  exitOnError: false,
});

// ======================================================
// SECURITY LOGGER
// ======================================================

const securityLogger = winston.createLogger({
  level: 'info',
  format: jsonFormat,
  transports: config.environment === 'production'
    ? [
        new DailyRotateFile({
          filename: config.logging.file.replace('.log', '.security.log'),
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: config.logging.maxSize,
          maxFiles: config.logging.maxFiles,
          level: 'info',
          format: jsonFormat,
        })
      ]
    : [
        new winston.transports.Console({
          level: 'info',
          format: consoleFormat,
        })
      ],
  exitOnError: false,
});

// ======================================================
// HELPER FUNCTIONS
// ======================================================

// Sanitize sensitive data
const sanitizeData = (data) => {
  if (!data || typeof data !== 'object') {
    return data;
  }
  
  const sanitized = { ...data };
  
  config.audit.sensitiveFields.forEach(field => {
    if (sanitized[field]) {
      sanitized[field] = '[REDACTED]';
    }
  });
  
  return sanitized;
};

// Log authentication events
const logAuthEvent = (event, user, details = {}) => {
  const logData = {
    event,
    userId: user?.id,
    userEmail: user?.email,
    ipAddress: details.ipAddress,
    userAgent: details.userAgent,
    success: details.success,
    failureReason: details.failureReason,
    timestamp: new Date().toISOString(),
  };
  
  if (event.includes('login') || event.includes('logout') || event.includes('failed')) {
    securityLogger.info('Authentication event', logData);
  }
  
  if (config.audit.enabled) {
    auditLogger.info('Authentication audit', logData);
  }
};

// Log authorization events
const logAuthzEvent = (event, user, resource, action, details = {}) => {
  const logData = {
    event,
    userId: user?.id,
    userEmail: user?.email,
    resource,
    action,
    allowed: details.allowed,
    reason: details.reason,
    ipAddress: details.ipAddress,
    userAgent: details.userAgent,
    timestamp: new Date().toISOString(),
  };
  
  if (config.audit.enabled) {
    auditLogger.info('Authorization audit', logData);
  }
};

// Log security events
const logSecurityEvent = (event, details = {}) => {
  const logData = {
    event,
    severity: details.severity || 'medium',
    ipAddress: details.ipAddress,
    userAgent: details.userAgent,
    details: sanitizeData(details),
    timestamp: new Date().toISOString(),
  };
  
  securityLogger.warn('Security event', logData);
  
  if (config.audit.enabled) {
    auditLogger.warn('Security audit', logData);
  }
};

// Log performance metrics
const logPerformance = (operation, duration, details = {}) => {
  const logData = {
    operation,
    duration,
    timestamp: new Date().toISOString(),
    ...details,
  };
  
  logger.info('Performance metric', logData);
};

// ======================================================
// STREAM FOR MORGAN
// ======================================================

logger.stream = {
  write: (message) => {
    logger.info(message.trim());
  },
};

// ======================================================
// EXPORTS
// ======================================================

module.exports = {
  logger,
  auditLogger,
  securityLogger,
  logAuthEvent,
  logAuthzEvent,
  logSecurityEvent,
  logPerformance,
  sanitizeData,
}; 