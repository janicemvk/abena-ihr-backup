/**
 * Abena IHR Authentication & Authorization Service
 * ================================================
 * 
 * Comprehensive authentication and authorization service providing:
 * - JWT-based authentication
 * - OAuth2 integration (Google, Microsoft, SAML)
 * - Multi-factor authentication (TOTP, SMS, Email)
 * - Role-based access control (RBAC)
 * - Session management
 * - Security features and compliance
 */

require('express-async-errors');
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const passport = require('passport');
const morgan = require('morgan');
const hpp = require('hpp');
const xss = require('xss-clean');
const mongoSanitize = require('express-mongo-sanitize');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const winston = require('winston');
const expressWinston = require('express-winston');
const cron = require('node-cron');

// Import custom modules
const config = require('./config');
const logger = require('./utils/logger');
const redisClient = require('./utils/redis');
const db = require('./utils/database');
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const requestLogger = require('./middleware/requestLogger');

// Import routes
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const roleRoutes = require('./routes/roles');
const permissionRoutes = require('./routes/permissions');
const sessionRoutes = require('./routes/sessions');
const mfaRoutes = require('./routes/mfa');
const oauthRoutes = require('./routes/oauth');
const healthRoutes = require('./routes/health');

// Import services
const AuthService = require('./services/AuthService');
const UserService = require('./services/UserService');
const RoleService = require('./services/RoleService');
const PermissionService = require('./services/PermissionService');
const SessionService = require('./services/SessionService');
const MFAService = require('./services/MFAService');
const OAuthService = require('./services/OAuthService');
const AuditService = require('./services/AuditService');

// Import passport strategies
require('./config/passport');

// Initialize Express app
const app = express();

// ======================================================
// SECURITY MIDDLEWARE
// ======================================================

// Security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  crossOriginEmbedderPolicy: false,
}));

// CORS configuration
app.use(cors({
  origin: config.corsOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api/', limiter);

// Stricter rate limiting for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 requests per windowMs
  message: 'Too many authentication attempts, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/register', authLimiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Security middleware
app.use(hpp()); // Protect against HTTP Parameter Pollution
app.use(xss()); // Protect against XSS attacks
app.use(mongoSanitize()); // Protect against NoSQL injection

// Compression
app.use(compression());

// ======================================================
// SESSION CONFIGURATION
// ======================================================

// Redis session store
const redisStore = new RedisStore({
  client: redisClient,
  prefix: 'auth_session:',
  ttl: config.session.ttl,
});

// Session middleware
app.use(session({
  store: redisStore,
  secret: config.session.secret,
  name: 'abena_auth_session',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: config.environment === 'production',
    httpOnly: true,
    maxAge: config.session.ttl * 1000,
    sameSite: 'strict',
  },
}));

// ======================================================
// PASSPORT CONFIGURATION
// ======================================================

app.use(passport.initialize());
app.use(passport.session());

// ======================================================
// LOGGING MIDDLEWARE
// ======================================================

// Request logging
app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } }));

// Express Winston logging
app.use(expressWinston.logger({
  winstonInstance: logger,
  meta: true,
  msg: 'HTTP {{req.method}} {{req.url}}',
  expressFormat: true,
  colorize: false,
}));

// ======================================================
// SWAGGER DOCUMENTATION
// ======================================================

const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Abena IHR Auth Service API',
      version: '1.0.0',
      description: 'Authentication and Authorization Service for Abena IHR',
      contact: {
        name: 'Abena IHR Team',
        email: 'support@abenahealth.org',
      },
    },
    servers: [
      {
        url: `http://localhost:${config.port}`,
        description: 'Development server',
      },
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
        },
      },
    },
  },
  apis: ['./routes/*.js', './models/*.js'],
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// ======================================================
// HEALTH CHECK
// ======================================================

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'auth-service',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: config.environment,
    database: db.isConnected() ? 'connected' : 'disconnected',
    redis: redisClient.status === 'ready' ? 'connected' : 'disconnected',
  });
});

// ======================================================
// API ROUTES
// ======================================================

// API prefix
app.use('/api', (req, res, next) => {
  req.apiVersion = 'v1';
  next();
});

// Auth routes (no authentication required)
app.use('/api/auth', authRoutes);

// OAuth routes (no authentication required)
app.use('/api/oauth', oauthRoutes);

// Protected routes (authentication required)
app.use('/api/users', authMiddleware.authenticate, userRoutes);
app.use('/api/roles', authMiddleware.authenticate, authMiddleware.requireRole('admin'), roleRoutes);
app.use('/api/permissions', authMiddleware.authenticate, authMiddleware.requireRole('admin'), permissionRoutes);
app.use('/api/sessions', authMiddleware.authenticate, sessionRoutes);
app.use('/api/mfa', authMiddleware.authenticate, mfaRoutes);

// Health routes (no authentication required)
app.use('/api/health', healthRoutes);

// ======================================================
// ERROR HANDLING
// ======================================================

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found',
    path: req.originalUrl,
  });
});

// Global error handler
app.use(errorHandler);

// ======================================================
// CRON JOBS
// ======================================================

// Clean up expired sessions daily at 2 AM
cron.schedule('0 2 * * *', async () => {
  try {
    logger.info('Running session cleanup job');
    await SessionService.cleanupExpiredSessions();
    logger.info('Session cleanup completed');
  } catch (error) {
    logger.error('Session cleanup failed:', error);
  }
});

// Clean up expired tokens daily at 3 AM
cron.schedule('0 3 * * *', async () => {
  try {
    logger.info('Running token cleanup job');
    await AuthService.cleanupExpiredTokens();
    logger.info('Token cleanup completed');
  } catch (error) {
    logger.error('Token cleanup failed:', error);
  }
});

// Audit log rotation weekly on Sunday at 1 AM
cron.schedule('0 1 * * 0', async () => {
  try {
    logger.info('Running audit log rotation job');
    await AuditService.rotateAuditLogs();
    logger.info('Audit log rotation completed');
  } catch (error) {
    logger.error('Audit log rotation failed:', error);
  }
});

// ======================================================
// GRACEFUL SHUTDOWN
// ======================================================

const gracefulShutdown = async (signal) => {
  logger.info(`Received ${signal}. Starting graceful shutdown...`);
  
  // Close database connections
  await db.close();
  
  // Close Redis connection
  await redisClient.quit();
  
  // Close server
  server.close(() => {
    logger.info('HTTP server closed');
    process.exit(0);
  });
  
  // Force exit after 30 seconds
  setTimeout(() => {
    logger.error('Forced shutdown after timeout');
    process.exit(1);
  }, 30000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// ======================================================
// START SERVER
// ======================================================

const server = app.listen(config.port, () => {
  logger.info(`🚀 Auth Service started on port ${config.port}`);
  logger.info(`📚 API Documentation available at http://localhost:${config.port}/api-docs`);
  logger.info(`🏥 Health check available at http://localhost:${config.port}/health`);
  logger.info(`🌍 Environment: ${config.environment}`);
  logger.info(`🔐 JWT Secret: ${config.jwt.secret ? 'Configured' : 'NOT CONFIGURED'}`);
  logger.info(`🔑 OAuth Providers: ${Object.keys(config.oauth).join(', ')}`);
});

// Handle server errors
server.on('error', (error) => {
  if (error.syscall !== 'listen') {
    throw error;
  }

  const bind = typeof config.port === 'string' ? `Pipe ${config.port}` : `Port ${config.port}`;

  switch (error.code) {
    case 'EACCES':
      logger.error(`${bind} requires elevated privileges`);
      process.exit(1);
      break;
    case 'EADDRINUSE':
      logger.error(`${bind} is already in use`);
      process.exit(1);
      break;
    default:
      throw error;
  }
});

module.exports = app; 