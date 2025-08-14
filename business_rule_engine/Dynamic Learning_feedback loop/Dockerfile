# Dockerfile for Abena IHR Dynamic Learning Platform with SDK
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables for Abena SDK
ENV ABENA_API_KEY=""
ENV AUTH_SERVICE_URL="http://localhost:3001"
ENV DATA_SERVICE_URL="http://localhost:8001"
ENV PRIVACY_SERVICE_URL="http://localhost:8002"
ENV BLOCKCHAIN_SERVICE_URL="http://localhost:8003"
ENV ENVIRONMENT="production"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 