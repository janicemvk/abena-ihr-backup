Abena SDK)?# Abena IHR Authentication & Authorization Service
# ================================================
# Multi-stage Docker build for production-ready auth service

# ======================================================
# BUILD STAGE
# ======================================================

FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    && npm config set python python3

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Set ownership
RUN chown -R nodejs:nodejs /app

# ======================================================
# PRODUCTION STAGE
# ======================================================

FROM node:18-alpine AS production

# Install runtime dependencies
RUN apk add --no-cache \
    dumb-init \
    curl \
    && rm -rf /var/cache/apk/*

# Create app directory
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy built application from builder stage
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./
COPY --from=builder --chown=nodejs:nodejs /app/server.js ./
COPY --from=builder --chown=nodejs:nodejs /app/config ./config
COPY --from=builder --chown=nodejs:nodejs /app/middleware ./middleware
COPY --from=builder --chown=nodejs:nodejs /app/routes ./routes
COPY --from=builder --chown=nodejs:nodejs /app/services ./services
COPY --from=builder --chown=nodejs:nodejs /app/utils ./utils
COPY --from=builder --chown=nodejs:nodejs /app/models ./models
COPY --from=builder --chown=nodejs:nodejs /app/validators ./validators

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/temp && \
    chown -R nodejs:nodejs /app/logs /app/uploads /app/temp

# Set environment variables
ENV NODE_ENV=production
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER nodejs

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["node", "server.js"]

# ======================================================
# DEVELOPMENT STAGE (Optional)
# ======================================================

FROM node:18-alpine AS development

# Set working directory
WORKDIR /app

# Install development dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    && npm config set python python3

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm install

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/temp

# Set environment variables
ENV NODE_ENV=development
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application in development mode
CMD ["npm", "run", "dev"]

# ======================================================
# METADATA
# ======================================================

LABEL maintainer="Abena IHR Team <support@abenahealth.org>"
LABEL version="1.0.0"
LABEL description="Authentication and Authorization Service for Abena IHR"
LABEL org.opencontainers.image.title="Abena IHR Auth Service"
LABEL org.opencontainers.image.description="Secure authentication and authorization microservice"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="Abena Health"
LABEL org.opencontainers.image.source="https://github.com/abena-ihr/auth-service" 