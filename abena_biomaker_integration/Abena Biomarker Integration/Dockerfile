FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create mock abena_sdk if it doesn't exist
RUN echo 'class AbenaSDK:\n    def __init__(self):\n        pass\n    def get_biomarker_data(self):\n        return {"status": "mock_data"}' > abena_sdk.py

# Expose port
EXPOSE 8050

# Start the Dash app
CMD ["python", "gui.py"] 