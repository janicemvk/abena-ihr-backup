/**
 * Abena IHR Auth Service Redis Utility
 * ====================================
 * 
 * Redis connection and utility functions for:
 * - Session storage
 * - Token caching
 * - Rate limiting
 * - User data caching
 * - Distributed locking
 */

const redis = require('redis');
const config = require('../config');
const { logger } = require('./logger');

// ======================================================
// REDIS CLIENT CONFIGURATION
// ======================================================

const redisConfig = {
  host: config.redis.host,
  port: config.redis.port,
  password: config.redis.password,
  db: config.redis.db,
  keyPrefix: config.redis.keyPrefix,
  retryDelayOnFailover: config.redis.retryDelayOnFailover,
  maxRetriesPerRequest: config.redis.maxRetriesPerRequest,
  enableReadyCheck: true,
  retryStrategy: (times) => {
    const delay = Math.min(times * 50, 2000);
    return delay;
  },
  reconnectOnError: (err) => {
    const targetError = 'READONLY';
    if (err.message.includes(targetError)) {
      return true;
    }
    return false;
  },
};

// ======================================================
// REDIS CLIENT INSTANCE
// ======================================================

let redisClient = null;

const createRedisClient = () => {
  try {
    const client = redis.createClient(redisConfig);
    
    // Event handlers
    client.on('connect', () => {
      logger.info('Redis client connected');
    });
    
    client.on('ready', () => {
      logger.info('Redis client ready');
    });
    
    client.on('error', (err) => {
      logger.error('Redis client error:', err);
    });
    
    client.on('end', () => {
      logger.warn('Redis client connection ended');
    });
    
    client.on('reconnecting', () => {
      logger.info('Redis client reconnecting...');
    });
    
    return client;
  } catch (error) {
    logger.error('Failed to create Redis client:', error);
    throw error;
  }
};

// Initialize Redis client
const initializeRedis = async () => {
  try {
    redisClient = createRedisClient();
    await redisClient.connect();
    logger.info('Redis client initialized successfully');
    return redisClient;
  } catch (error) {
    logger.error('Failed to initialize Redis client:', error);
    throw error;
  }
};

// ======================================================
// SESSION MANAGEMENT
// ======================================================

const sessionUtils = {
  // Store session data
  async setSession(sessionId, data, ttl = config.session.ttl) {
    try {
      const key = `session:${sessionId}`;
      await redisClient.setEx(key, ttl, JSON.stringify(data));
      logger.debug(`Session stored: ${sessionId}`);
      return true;
    } catch (error) {
      logger.error('Failed to store session:', error);
      return false;
    }
  },
  
  // Get session data
  async getSession(sessionId) {
    try {
      const key = `session:${sessionId}`;
      const data = await redisClient.get(key);
      if (data) {
        logger.debug(`Session retrieved: ${sessionId}`);
        return JSON.parse(data);
      }
      return null;
    } catch (error) {
      logger.error('Failed to get session:', error);
      return null;
    }
  },
  
  // Delete session
  async deleteSession(sessionId) {
    try {
      const key = `session:${sessionId}`;
      await redisClient.del(key);
      logger.debug(`Session deleted: ${sessionId}`);
      return true;
    } catch (error) {
      logger.error('Failed to delete session:', error);
      return false;
    }
  },
  
  // Extend session TTL
  async extendSession(sessionId, ttl = config.session.ttl) {
    try {
      const key = `session:${sessionId}`;
      await redisClient.expire(key, ttl);
      logger.debug(`Session extended: ${sessionId}`);
      return true;
    } catch (error) {
      logger.error('Failed to extend session:', error);
      return false;
    }
  },
  
  // Get all sessions for a user
  async getUserSessions(userId) {
    try {
      const pattern = `session:*`;
      const keys = await redisClient.keys(pattern);
      const sessions = [];
      
      for (const key of keys) {
        const data = await redisClient.get(key);
        if (data) {
          const session = JSON.parse(data);
          if (session.userId === userId) {
            sessions.push({
              sessionId: key.replace('session:', ''),
              ...session,
            });
          }
        }
      }
      
      return sessions;
    } catch (error) {
      logger.error('Failed to get user sessions:', error);
      return [];
    }
  },
};

// ======================================================
// TOKEN MANAGEMENT
// ======================================================

const tokenUtils = {
  // Store access token
  async setAccessToken(token, userId, ttl = 3600) { // 1 hour
    try {
      const key = `access_token:${token}`;
      await redisClient.setEx(key, ttl, JSON.stringify({ userId, createdAt: Date.now() }));
      logger.debug(`Access token stored for user: ${userId}`);
      return true;
    } catch (error) {
      logger.error('Failed to store access token:', error);
      return false;
    }
  },
  
  // Store refresh token
  async setRefreshToken(token, userId, ttl = 604800) { // 7 days
    try {
      const key = `refresh_token:${token}`;
      await redisClient.setEx(key, ttl, JSON.stringify({ userId, createdAt: Date.now() }));
      logger.debug(`Refresh token stored for user: ${userId}`);
      return true;
    } catch (error) {
      logger.error('Failed to store refresh token:', error);
      return false;
    }
  },
  
  // Get token data
  async getToken(token, type = 'access') {
    try {
      const key = `${type}_token:${token}`;
      const data = await redisClient.get(key);
      if (data) {
        logger.debug(`${type} token retrieved`);
        return JSON.parse(data);
      }
      return null;
    } catch (error) {
      logger.error(`Failed to get ${type} token:`, error);
      return null;
    }
  },
  
  // Delete token
  async deleteToken(token, type = 'access') {
    try {
      const key = `${type}_token:${token}`;
      await redisClient.del(key);
      logger.debug(`${type} token deleted`);
      return true;
    } catch (error) {
      logger.error(`Failed to delete ${type} token:`, error);
      return false;
    }
  },
  
  // Blacklist token
  async blacklistToken(token, ttl = 3600) {
    try {
      const key = `blacklist:${token}`;
      await redisClient.setEx(key, ttl, JSON.stringify({ blacklistedAt: Date.now() }));
      logger.debug(`Token blacklisted: ${token}`);
      return true;
    } catch (error) {
      logger.error('Failed to blacklist token:', error);
      return false;
    }
  },
  
  // Check if token is blacklisted
  async isTokenBlacklisted(token) {
    try {
      const key = `blacklist:${token}`;
      const data = await redisClient.get(key);
      return !!data;
    } catch (error) {
      logger.error('Failed to check token blacklist:', error);
      return false;
    }
  },
};

// ======================================================
// RATE LIMITING
// ======================================================

const rateLimitUtils = {
  // Check rate limit
  async checkRateLimit(key, limit, window) {
    try {
      const current = await redisClient.incr(key);
      
      if (current === 1) {
        await redisClient.expire(key, window);
      }
      
      const ttl = await redisClient.ttl(key);
      
      return {
        current,
        limit,
        remaining: Math.max(0, limit - current),
        resetTime: Date.now() + (ttl * 1000),
        exceeded: current > limit,
      };
    } catch (error) {
      logger.error('Failed to check rate limit:', error);
      return {
        current: 0,
        limit,
        remaining: limit,
        resetTime: Date.now() + (window * 1000),
        exceeded: false,
      };
    }
  },
  
  // Reset rate limit
  async resetRateLimit(key) {
    try {
      await redisClient.del(key);
      logger.debug(`Rate limit reset: ${key}`);
      return true;
    } catch (error) {
      logger.error('Failed to reset rate limit:', error);
      return false;
    }
  },
  
  // Get rate limit info
  async getRateLimitInfo(key) {
    try {
      const current = await redisClient.get(key);
      const ttl = await redisClient.ttl(key);
      
      return {
        current: parseInt(current) || 0,
        ttl,
        resetTime: Date.now() + (ttl * 1000),
      };
    } catch (error) {
      logger.error('Failed to get rate limit info:', error);
      return null;
    }
  },
};

// ======================================================
// USER DATA CACHING
// ======================================================

const cacheUtils = {
  // Cache user data
  async cacheUser(userId, userData, ttl = 3600) { // 1 hour
    try {
      const key = `user:${userId}`;
      await redisClient.setEx(key, ttl, JSON.stringify(userData));
      logger.debug(`User cached: ${userId}`);
      return true;
    } catch (error) {
      logger.error('Failed to cache user:', error);
      return false;
    }
  },
  
  // Get cached user
  async getCachedUser(userId) {
    try {
      const key = `user:${userId}`;
      const data = await redisClient.get(key);
      if (data) {
        logger.debug(`User retrieved from cache: ${userId}`);
        return JSON.parse(data);
      }
      return null;
    } catch (error) {
      logger.error('Failed to get cached user:', error);
      return null;
    }
  },
  
  // Invalidate user cache
  async invalidateUser(userId) {
    try {
      const key = `user:${userId}`;
      await redisClient.del(key);
      logger.debug(`User cache invalidated: ${userId}`);
      return true;
    } catch (error) {
      logger.error('Failed to invalidate user cache:', error);
      return false;
    }
  },
  
  // Cache permissions
  async cachePermissions(userId, permissions, ttl = 1800) { // 30 minutes
    try {
      const key = `permissions:${userId}`;
      await redisClient.setEx(key, ttl, JSON.stringify(permissions));
      logger.debug(`Permissions cached: ${userId}`);
      return true;
    } catch (error) {
      logger.error('Failed to cache permissions:', error);
      return false;
    }
  },
  
  // Get cached permissions
  async getCachedPermissions(userId) {
    try {
      const key = `permissions:${userId}`;
      const data = await redisClient.get(key);
      if (data) {
        logger.debug(`Permissions retrieved from cache: ${userId}`);
        return JSON.parse(data);
      }
      return null;
    } catch (error) {
      logger.error('Failed to get cached permissions:', error);
      return null;
    }
  },
};

// ======================================================
// DISTRIBUTED LOCKING
// ======================================================

const lockUtils = {
  // Acquire distributed lock
  async acquireLock(lockKey, ttl = 30) { // 30 seconds
    try {
      const lockValue = Date.now().toString();
      const result = await redisClient.set(lockKey, lockValue, 'PX', ttl * 1000, 'NX');
      
      if (result === 'OK') {
        logger.debug(`Lock acquired: ${lockKey}`);
        return { acquired: true, value: lockValue };
      }
      
      return { acquired: false, value: null };
    } catch (error) {
      logger.error('Failed to acquire lock:', error);
      return { acquired: false, value: null };
    }
  },
  
  // Release distributed lock
  async releaseLock(lockKey, lockValue) {
    try {
      const script = `
        if redis.call("get", KEYS[1]) == ARGV[1] then
          return redis.call("del", KEYS[1])
        else
          return 0
        end
      `;
      
      const result = await redisClient.eval(script, 1, lockKey, lockValue);
      
      if (result === 1) {
        logger.debug(`Lock released: ${lockKey}`);
        return true;
      }
      
      return false;
    } catch (error) {
      logger.error('Failed to release lock:', error);
      return false;
    }
  },
  
  // Extend lock
  async extendLock(lockKey, lockValue, ttl = 30) {
    try {
      const script = `
        if redis.call("get", KEYS[1]) == ARGV[1] then
          return redis.call("pexpire", KEYS[1], ARGV[2])
        else
          return 0
        end
      `;
      
      const result = await redisClient.eval(script, 1, lockKey, lockValue, ttl * 1000);
      
      if (result === 1) {
        logger.debug(`Lock extended: ${lockKey}`);
        return true;
      }
      
      return false;
    } catch (error) {
      logger.error('Failed to extend lock:', error);
      return false;
    }
  },
};

// ======================================================
// UTILITY FUNCTIONS
// ======================================================

const utils = {
  // Get Redis info
  async getInfo() {
    try {
      const info = await redisClient.info();
      return info;
    } catch (error) {
      logger.error('Failed to get Redis info:', error);
      return null;
    }
  },
  
  // Flush database
  async flushDb() {
    try {
      await redisClient.flushDb();
      logger.info('Redis database flushed');
      return true;
    } catch (error) {
      logger.error('Failed to flush Redis database:', error);
      return false;
    }
  },
  
  // Get database size
  async getDbSize() {
    try {
      const size = await redisClient.dbSize();
      return size;
    } catch (error) {
      logger.error('Failed to get Redis database size:', error);
      return 0;
    }
  },
  
  // Health check
  async healthCheck() {
    try {
      await redisClient.ping();
      return { status: 'healthy', timestamp: Date.now() };
    } catch (error) {
      logger.error('Redis health check failed:', error);
      return { status: 'unhealthy', error: error.message, timestamp: Date.now() };
    }
  },
};

// ======================================================
// EXPORTS
// ======================================================

module.exports = {
  redisClient,
  initializeRedis,
  sessionUtils,
  tokenUtils,
  rateLimitUtils,
  cacheUtils,
  lockUtils,
  utils,
}; 