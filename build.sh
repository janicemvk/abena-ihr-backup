#!/bin/bash
# Build script for Render deployment
# This ensures all dependencies install correctly

set -e  # Exit on error

echo "Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Build completed successfully!"

