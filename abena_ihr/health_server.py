from fastapi import FastAPI
import uvicorn
from datetime import datetime
import os

app = FastAPI()
PORT = int(os.getenv('PORT', 4002))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "module": "abena-ihr",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "database_connected": True
    }

@app.get("/info")
async def module_info():
    return {
        "id": "abena-ihr",
        "name": "Abena IHR Main System",
        "version": "1.0.0",
        "description": "Clinical outcomes management system",
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "api": "/api/v1"
        },
        "dependencies": ["sdk-service"],
        "capabilities": ["patient-management", "outcome-tracking", "analytics"]
    }

@app.get("/api/v1/patients")
async def get_patients():
    return {
        "success": True,
        "data": [
            {"id": "patient-001", "name": "John Doe", "status": "active"},
            {"id": "patient-002", "name": "Jane Smith", "status": "active"},
            {"id": "patient-003", "name": "Bob Johnson", "status": "active"}
        ]
    }

@app.get("/api/v1/outcomes")
async def get_outcomes():
    return {
        "success": True,
        "data": [
            {"id": "outcome-001", "name": "Pain Reduction", "status": "tracking"},
            {"id": "outcome-002", "name": "Quality of Life", "status": "tracking"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT) 