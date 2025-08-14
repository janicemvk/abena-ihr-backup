from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Import configuration
from config import settings, get_settings

# Import the FastAPI apps from the analytics modules
from predictive_analytics_engine import app as predictive_app
from population_analytics import app as population_app
from real_time_analytics import app as realtime_app

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Abena IHR Analytics Engine Service",
    description="Unified entry point for predictive, population, and real-time analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount or include routers from the submodules
app.mount("/predictive", predictive_app)
app.mount("/population", population_app)
app.mount("/realtime", realtime_app)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": settings.service_name,
        "version": "1.0.0"
    }

@app.get("/config")
async def get_config():
    """Get service configuration (non-sensitive)"""
    return {
        "service_name": settings.service_name,
        "port": settings.port,
        "model_update_interval": settings.model_update_interval,
        "monitoring_frequency_minutes": settings.monitoring_frequency_minutes,
        "max_concurrent_sessions": settings.max_concurrent_sessions,
        "enable_gpu": settings.enable_gpu,
        "batch_size": settings.batch_size,
        "log_level": settings.log_level,
        "enable_performance_metrics": settings.enable_performance_metrics
    }

if __name__ == "__main__":
    logger.info(f"Starting {settings.service_name} on port {settings.port}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.port,
        log_level=settings.log_level.lower()
    ) 