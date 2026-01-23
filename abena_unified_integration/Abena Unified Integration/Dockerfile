# Multi-stage build for Unified Integration React App
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build React application
RUN npm run build

# Production stage - serve with Nginx
FROM nginx:alpine

# Copy the built React app from builder stage
COPY --from=builder /app/build/ /usr/share/nginx/html/

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 4008

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 