# Dockerfile for ABENA Quantum Healthcare Service
# Based on Python 3.11 with quantum computing dependencies

FROM python:3.11-slim

LABEL maintainer="ABENA IHR Team"
LABEL description="Quantum Healthcare Analysis Service for ABENA IHR"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .
COPY templates/ /app/templates/

# Create data directory for quantum analysis results
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:5000/api/demo-results || exit 1

# Run Flask application
CMD ["python", "app.py"]

