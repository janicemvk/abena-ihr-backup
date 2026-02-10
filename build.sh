#!/bin/bash
# Build script for Render deployment
# This ensures all dependencies install correctly

set -e  # Exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"

