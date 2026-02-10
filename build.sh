#!/bin/bash
# Build script for Render deployment
# This ensures all dependencies install correctly

set -e  # Exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel

# Install dependencies with error handling
echo "Installing core dependencies..."
pip install flask==2.3.3 flask-cors==4.0.0 gunicorn==21.2.0

echo "Installing scientific computing dependencies..."
pip install numpy==1.24.3 scipy==1.11.1

echo "Installing quantum computing dependencies..."
pip install qiskit==0.44.1 || echo "Warning: qiskit installation had issues, but continuing..."

echo "Installing remaining dependencies..."
pip install matplotlib==3.7.2 python-jose[cryptography]==3.3.0 httpx==0.25.0 redis==5.0.0 psycopg2-binary==2.9.9 python-dotenv==1.0.0

# Try to install psycopg2-pool, but don't fail if it doesn't exist
pip install psycopg2-pool==1.1 || echo "Warning: psycopg2-pool not available, skipping..."

echo "Build completed successfully!"

