from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import learning_engine, clinical_context, ecdome
from app.core.config import settings
from app.core.database import engine, Base
import uvicorn
import logging
from datetime import datetime

# ✅ Initialize Abena SDK
abena_sdk = None
try:
    from abena_sdk import AbenaSDK
    abena_sdk = AbenaSDK(
        api_key=settings.ABENA_API_KEY,
        auth_service_url=settings.AUTH_SERVICE_URL,
        data_service_url=settings.DATA_SERVICE_URL,
        privacy_service_url=settings.PRIVACY_SERVICE_URL,
        blockchain_service_url=settings.BLOCKCHAIN_SERVICE_URL
    )
    logging.info("✅ Abena SDK initialized successfully")
except Exception as e:
    logging.warning(f"⚠️ Abena SDK not available: {str(e)}")
    abena_sdk = None

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Healthcare Research platform with adaptive analytics and outcome tracking",
    version=settings.VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ✅ Include SDK-enhanced routers
app.include_router(learning_engine.router, prefix="/api/learning", tags=["Learning Engine"])
app.include_router(clinical_context.router, prefix="/api/clinical", tags=["Clinical Context"])
app.include_router(ecdome.router, prefix="/api/ecdome", tags=["eCdome"])

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Enhanced dashboard for Abena IHR platform with SDK status"""
    # Get SDK status
    sdk_status = "active" if abena_sdk else "unavailable"
    
    # Mock metrics (replace with actual data from SDK)
    metrics = {
        "total_patients": 1250,
        "active_treatments": 847,
        "feedback_submissions_today": 156,
        "learning_accuracy": 0.94,
        "system_performance": {"uptime": 0.998},
        "insights_generated_today": 89
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "sdk_status": sdk_status,
        "metrics": metrics,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with SDK status"""
    return {
        "status": "healthy", 
        "platform": settings.APP_NAME,
        "version": settings.VERSION,
        "sdk_status": "active" if abena_sdk else "unavailable",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/sdk/status")
async def sdk_status():
    """Get Abena SDK status and configuration"""
    return {
        "sdk_available": abena_sdk is not None,
        "auth_service": settings.AUTH_SERVICE_URL,
        "data_service": settings.DATA_SERVICE_URL,
        "privacy_service": settings.PRIVACY_SERVICE_URL,
        "blockchain_service": settings.BLOCKCHAIN_SERVICE_URL,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 