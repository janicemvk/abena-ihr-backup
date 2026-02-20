from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime

# Import routers
from src.api.routers import patients, predictions, workflows, feedback
from src.api.routers.learning import router as learning_router  # NEW
from src.api.routers.realtime import router as realtime_router  # NEW

# Import system components
from src.integration.system_orchestrator import AbenaIntegratedSystem
from src.tasks.daily_learning_scheduler import DailyLearningScheduler, SchedulerConfig
from config.settings import settings

# Global system instances
abena_system = None
learning_scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    
    # Startup
    logging.info("Starting Abena IHR application...")
    
    global abena_system, learning_scheduler
    
    try:
        # Initialize main system
        abena_system = AbenaIntegratedSystem()
        
        # Initialize daily learning scheduler
        scheduler_config = SchedulerConfig(
            learning_time=settings.DAILY_LEARNING_TIME,
            timezone=settings.TIMEZONE,
            max_execution_time=settings.MAX_LEARNING_EXECUTION_TIME,
            retry_attempts=settings.LEARNING_RETRY_ATTEMPTS,
            notification_enabled=settings.LEARNING_NOTIFICATIONS_ENABLED
        )
        
        learning_scheduler = DailyLearningScheduler(scheduler_config)
        
        # Start daily learning cycle
        if settings.ENABLE_DAILY_LEARNING:
            await abena_system.start_daily_learning_cycle()
            learning_scheduler.start_scheduler()
            logging.info("Daily learning system started")
        else:
            logging.info("Daily learning system disabled in configuration")
        
        # Start real-time biomarker monitoring if enabled
        if settings.ENABLE_REALTIME_BIOMARKERS:
            # This would be configured per patient
            logging.info("Real-time biomarker system ready")
        
        logging.info("Abena IHR application started successfully")
        
        yield  # Application runs here
        
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
        raise
    
    # Shutdown
    logging.info("Shutting down Abena IHR application...")
    
    try:
        # Stop daily learning scheduler
        if learning_scheduler:
            learning_scheduler.stop_scheduler()
            logging.info("Daily learning scheduler stopped")
        
        # Stop system components
        if abena_system and hasattr(abena_system, 'realtime_biomarkers'):
            await abena_system.realtime_biomarkers.manager.stop_monitoring()
            logging.info("Real-time biomarker monitoring stopped")
        
        logging.info("Abena IHR application shutdown complete")
        
    except Exception as e:
        logging.error(f"Error during shutdown: {str(e)}")

# Create FastAPI application with lifespan management
app = FastAPI(
    title="Abena IHR API",
    description="Intelligent Health Records with Predictive Analytics and Continuous Learning",
    version="2.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["predictions"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])
app.include_router(learning_router, prefix="/api/v1/learning", tags=["learning"])  # NEW
app.include_router(realtime_router, prefix="/api/v1/realtime", tags=["realtime"])  # NEW

@app.get("/")
async def root():
    """Root endpoint with system status"""
    
    system_status = {
        "message": "Abena IHR System",
        "version": "2.1.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "predictive_analytics": True,
            "workflow_integration": True,
            "real_time_biomarkers": settings.ENABLE_REALTIME_BIOMARKERS,
            "daily_learning": settings.ENABLE_DAILY_LEARNING,
            "continuous_learning": True
        }
    }
    
    # Add learning system status if available
    if learning_scheduler:
        system_status["learning_system"] = {
            "scheduler_running": learning_scheduler.is_running,
            "last_execution": learning_scheduler.last_execution_result,
            "next_scheduled": learning_scheduler._get_next_run_time()
        }
    
    return system_status

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    try:
        # Check main system
        if abena_system:
            health_status["components"]["abena_system"] = "healthy"
            
            # Check predictive engine
            if hasattr(abena_system, 'predictive_engine'):
                health_status["components"]["predictive_engine"] = "healthy"
            
            # Check continuous learning
            if hasattr(abena_system, 'continuous_learning'):
                health_status["components"]["continuous_learning"] = "healthy"
            
            # Check real-time biomarkers
            if hasattr(abena_system, 'realtime_biomarkers'):
                biomarker_status = "healthy" if abena_system.realtime_biomarkers.manager.running else "inactive"
                health_status["components"]["realtime_biomarkers"] = biomarker_status
        
        # Check learning scheduler
        if learning_scheduler:
            scheduler_status = "healthy" if learning_scheduler.is_running else "inactive"
            health_status["components"]["learning_scheduler"] = scheduler_status
        
        # Check database connectivity
        # This would check your actual database
        health_status["components"]["database"] = "healthy"
        
        # Overall status
        unhealthy_components = [
            comp for comp, status in health_status["components"].items() 
            if status not in ["healthy", "inactive"]
        ]
        
        if unhealthy_components:
            health_status["status"] = "degraded"
            health_status["issues"] = unhealthy_components
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status

@app.get("/system-info")
async def get_system_info():
    """Get detailed system information"""
    
    system_info = {
        "application": {
            "name": "Abena IHR",
            "version": "2.1.0",
            "description": "Intelligent Health Records with Predictive Analytics",
            "startup_time": datetime.now().isoformat()
        },
        "features": {
            "predictive_analytics": {
                "enabled": True,
                "models": ["treatment_response", "adverse_event"],
                "real_time_updates": True
            },
            "workflow_integration": {
                "enabled": True,
                "emr_support": ["Epic", "Cerner", "Generic FHIR"],
                "alert_system": True
            },
            "continuous_learning": {
                "enabled": settings.ENABLE_DAILY_LEARNING,
                "schedule": settings.DAILY_LEARNING_TIME,
                "auto_retraining": True
            },
            "real_time_biomarkers": {
                "enabled": settings.ENABLE_REALTIME_BIOMARKERS,
                "supported_devices": ["CGM", "HRV", "Cortisol", "Blood Pressure"],
                "stream_processing": True
            }
        }
    }
    
    # Add runtime statistics
    if abena_system:
        try:
            runtime_stats = {
                "active_patients": 0,  # This would come from your database
                "predictions_today": 0,  # This would come from your metrics
                "learning_insights": len(abena_system.continuous_learning.insights_db) if hasattr(abena_system.continuous_learning, 'insights_db') else 0,
                "active_alerts": 0  # This would come from your alert system
            }
            system_info["runtime_statistics"] = runtime_stats
        except Exception as e:
            system_info["runtime_statistics"] = {"error": str(e)}
    
    return system_info

# Dependency to get system instance
async def get_abena_system():
    """Dependency to get the main system instance"""
    if not abena_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    return abena_system

# Dependency to get learning scheduler
async def get_learning_scheduler():
    """Dependency to get the learning scheduler instance"""
    if not learning_scheduler:
        raise HTTPException(status_code=503, detail="Learning scheduler not initialized")
    return learning_scheduler

# Manual trigger endpoints for development/admin use
@app.post("/admin/trigger-learning")
async def trigger_learning_cycle(system: AbenaIntegratedSystem = Depends(get_abena_system)):
    """Manually trigger a learning cycle (admin only)"""
    try:
        result = await system.execute_daily_learning()
        return {
            "status": "completed",
            "execution_time": result.get('execution_date'),
            "components_executed": result.get('components_executed', []),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning cycle failed: {str(e)}")

@app.post("/admin/force-retrain/{model_type}")
async def force_model_retraining(model_type: str, system: AbenaIntegratedSystem = Depends(get_abena_system)):
    """Force model retraining (admin only)"""
    if model_type not in ['treatment_response', 'adverse_event']:
        raise HTTPException(status_code=400, detail="Invalid model type")
    
    try:
        # This would be implemented as a background task in production
        training_data = await system._prepare_training_data_for_model(model_type)
        
        retrain_result = system.continuous_learning.retraining_pipeline.execute_retraining(
            model_type, training_data,
            optimization_config={'optimize': True, 'n_trials': 30}
        )
        
        return {
            "status": "completed" if retrain_result.get('success') else "failed",
            "model_type": model_type,
            "result": retrain_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model retraining failed: {str(e)}")

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logging.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "timestamp": datetime.now().isoformat(),
        "status_code": 500
    }

if __name__ == "__main__":
    import uvicorn
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the application
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )