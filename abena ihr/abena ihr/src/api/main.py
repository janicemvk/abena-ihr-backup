"""
Abena IHR - Clinical Outcomes API

Main FastAPI application for the clinical outcomes management system.
Provides RESTful API endpoints for managing clinical outcomes, measurements,
and data collection forms.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any
import os
from datetime import datetime

# Import routers
from .routers import outcomes
from src.clinical_outcomes.data_collection import outcome_router
from src.predictive_analytics.predictive_engine import prediction_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Abena IHR Clinical Outcomes API...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Initialize database connections, load configurations, etc.
    try:
        # Add any startup initialization here
        logger.info("API startup completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Abena IHR Clinical Outcomes API...")
    try:
        # Cleanup resources, close connections, etc.
        logger.info("API shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Abena IHR - Clinical Outcomes API",
    description="""
    Clinical Outcomes Management System API for Abena IHR.
    
    This API provides endpoints for:
    - Managing clinical outcome definitions
    - Collecting and validating clinical measurements
    - Managing data collection forms
    - Evaluating outcomes against criteria
    - Generating reports and analytics
    
    ## Features
    
    * **Outcome Management**: Define and manage clinical outcomes with measurement criteria
    * **Data Collection**: Collect clinical measurements through structured forms
    * **Quality Assurance**: Validate data quality and maintain audit trails
    * **Evaluation**: Evaluate measurements against outcome definitions
    * **Reporting**: Generate comprehensive reports and analytics
    """,
    version="1.0.0",
    contact={
        "name": "Abena IHR Development Team",
        "email": "dev@abena-ihr.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:8080",  # Alternative frontend port
        "https://abena-ihr.com",  # Production domain
        "https://www.abena-ihr.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Configure trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "abena-ihr.com",
        "www.abena-ihr.com",
        "*.abena-ihr.com",
    ]
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify API status.
    
    Returns:
        Dictionary containing API health status and version information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "Abena IHR Clinical Outcomes API",
        "environment": os.getenv("ENVIRONMENT", "development")
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing API information and available endpoints.
    
    Returns:
        Dictionary containing API information and links
    """
    return {
        "message": "Welcome to Abena IHR Clinical Outcomes API",
        "version": "1.0.0",
        "description": "Clinical Outcomes Management System",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "outcomes": "/api/v1/outcomes",
            "measurements": "/api/v1/measurements",
            "forms": "/api/v1/forms",
            "frameworks": "/api/v1/frameworks"
        },
        "timestamp": datetime.now().isoformat()
    }


# Include API routers
app.include_router(
    outcomes.router,
    prefix="/api/v1",
    tags=["Clinical Outcomes"]
)

# Presentation Layer - Include additional routers
app.include_router(outcome_router, prefix="/api/v1/outcomes")
app.include_router(prediction_router, prefix="/api/v1/predictions")


# API version endpoint
@app.get("/api/version", tags=["API Info"])
async def get_api_version() -> Dict[str, Any]:
    """
    Get API version information.
    
    Returns:
        Dictionary containing API version details
    """
    return {
        "version": "1.0.0",
        "api_name": "Abena IHR Clinical Outcomes API",
        "release_date": "2024-06-20",
        "status": "stable",
        "compatibility": {
            "python": "3.8+",
            "fastapi": "0.100.0+",
            "postgresql": "12+"
        }
    }


# Configuration endpoint (for development/debugging)
@app.get("/api/config", tags=["API Info"])
async def get_api_config() -> Dict[str, Any]:
    """
    Get API configuration information (development only).
    
    Returns:
        Dictionary containing API configuration details
    """
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(
            status_code=403,
            detail="Configuration endpoint not available in production"
        )
    
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "database_url": os.getenv("DATABASE_URL", "not_set"),
        "cors_origins": [
            "http://localhost:3000",
            "http://localhost:8080",
            "https://abena-ihr.com",
        ],
        "trusted_hosts": [
            "localhost",
            "127.0.0.1",
            "abena-ihr.com",
        ]
    }


if __name__ == "__main__":
    # Development server configuration
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    ) 