# =============================================================================
# 9. FASTAPI SERVER FOR INTELLIGENCE LAYER
# =============================================================================

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from main_orchestrator import IntelligenceLayer
from config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.logging.file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Abena IHR Intelligence Layer API",
    description="Monitoring, Alerting & Data Quality Analytics API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class IntegrationEventRequest(BaseModel):
    source_system: str
    endpoint: str
    response_time: float
    status_code: int
    success: bool
    error_message: Optional[str] = None
    records_processed: int = 0

class DataQualityAnalysisRequest(BaseModel):
    data_type: str
    source_system: str
    data: List[Dict[str, Any]]

class AlertRuleRequest(BaseModel):
    rule_name: str
    condition: str  # JSON string representation of condition
    severity: str
    cooldown_minutes: int = 15

# Global intelligence layer instance
intelligence_layer: Optional[IntelligenceLayer] = None

def validate_configuration():
    """Validate configuration before starting the server"""
    issues = config.validate()
    if issues:
        logger.error("Configuration validation failed:")
        for issue in issues:
            logger.error(f"  - {issue}")
        raise RuntimeError("Configuration validation failed. Please fix the issues above.")

def get_api_key_header():
    """Get API key header name from config"""
    return config.security.api_key_header

async def verify_api_key(api_key: str = Depends(get_api_key_header)):
    """Verify API key if configured"""
    if config.is_secure():
        if not api_key or api_key != config.security.api_key_value:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

@app.on_event("startup")
async def startup_event():
    """Initialize the Intelligence Layer on startup"""
    global intelligence_layer
    
    try:
        # Validate configuration
        validate_configuration()
        logger.info("Configuration validation passed")
        
        # Initialize Intelligence Layer
        intelligence_layer = IntelligenceLayer()
        logger.info("Intelligence Layer initialized successfully")
        
        # Start monitoring in background
        asyncio.create_task(intelligence_layer.start_monitoring())
        logger.info("Background monitoring tasks started")
        
    except Exception as e:
        logger.error(f"Failed to initialize Intelligence Layer: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Abena IHR Intelligence Layer API",
        "version": "1.0.0",
        "status": "running",
        "configuration_status": intelligence_layer.get_configuration_status() if intelligence_layer else None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    health_data = intelligence_layer.get_system_health()
    config_status = intelligence_layer.get_configuration_status()
    
    return {
        "status": "healthy" if health_data.get("status") != "unknown" else "unknown",
        "timestamp": datetime.utcnow().isoformat(),
        "details": health_data,
        "configuration": config_status
    }

@app.get("/config/status")
async def get_configuration_status():
    """Get configuration status"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    return intelligence_layer.get_configuration_status()

@app.post("/integration/record")
async def record_integration_event(
    request: IntegrationEventRequest,
    api_key: str = Depends(verify_api_key)
):
    """Record an integration event for monitoring"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        await intelligence_layer.record_integration_event(
            source_system=request.source_system,
            endpoint=request.endpoint,
            response_time=request.response_time,
            status_code=request.status_code,
            success=request.success,
            error_message=request.error_message,
            records_processed=request.records_processed
        )
        
        return {"message": "Integration event recorded successfully"}
        
    except Exception as e:
        logger.error(f"Error recording integration event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data-quality/analyze")
async def analyze_data_quality(
    request: DataQualityAnalysisRequest,
    api_key: str = Depends(verify_api_key)
):
    """Analyze data quality for a dataset"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        # Convert data to pandas DataFrame
        df = pd.DataFrame(request.data)
        
        # Perform quality analysis
        result = await intelligence_layer.analyze_data_quality(
            df, request.data_type, request.source_system
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing data quality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data-quality/analyze-file")
async def analyze_data_quality_file(
    file: UploadFile = File(...),
    data_type: str = "patient",
    source_system: str = "unknown",
    api_key: str = Depends(verify_api_key)
):
    """Analyze data quality from uploaded file"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(pd.io.common.BytesIO(content))
        elif file.filename.endswith('.json'):
            data = json.loads(content.decode())
            df = pd.DataFrame(data)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Perform quality analysis
        result = await intelligence_layer.analyze_data_quality(
            df, data_type, source_system
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing data quality from file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard")
async def get_dashboard(hours: int = 24):
    """Get comprehensive dashboard data"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        dashboard_data = await intelligence_layer.get_intelligence_dashboard()
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/integration/metrics")
async def get_integration_metrics(hours: int = 24):
    """Get integration monitoring metrics"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        metrics = await intelligence_layer.integration_monitor.get_integration_dashboard_data(hours)
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting integration metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data-quality/report")
async def get_data_quality_report(source_system: Optional[str] = None, days: int = 7):
    """Get data quality report"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        report = await intelligence_layer.report_generator.generate_data_quality_report(
            source_system, days
        )
        return report
        
    except Exception as e:
        logger.error(f"Error getting data quality report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
async def get_alerts(resolved: bool = False, limit: int = 100):
    """Get alerts"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        db = next(intelligence_layer.db_session())
        from intelligence_layer import AlertLog
        
        query = db.query(AlertLog)
        if resolved is not None:
            query = query.filter(AlertLog.resolved == resolved)
        
        alerts = query.order_by(AlertLog.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "source": alert.source,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            for alert in alerts
        ]
        
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int, 
    resolution_notes: str = "",
    api_key: str = Depends(verify_api_key)
):
    """Mark an alert as resolved"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        db = next(intelligence_layer.db_session())
        from intelligence_layer import AlertLog
        
        alert = db.query(AlertLog).filter(AlertLog.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = resolution_notes
        db.commit()
        
        return {"message": "Alert resolved successfully"}
        
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alerts/rules")
async def add_alert_rule(
    request: AlertRuleRequest,
    api_key: str = Depends(verify_api_key)
):
    """Add a new alert rule"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        # Parse condition function (simplified - in production, use proper validation)
        condition_str = request.condition
        
        # Add rule to integration monitor
        intelligence_layer.integration_monitor.alert_manager.add_alert_rule(
            rule_name=request.rule_name,
            condition=lambda m: eval(condition_str, {"__builtins__": {}}, {"m": m}),
            severity=request.severity,
            cooldown_minutes=request.cooldown_minutes
        )
        
        return {"message": "Alert rule added successfully"}
        
    except Exception as e:
        logger.error(f"Error adding alert rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_prometheus_metrics():
    """Get Prometheus metrics endpoint"""
    if not intelligence_layer:
        raise HTTPException(status_code=503, detail="Intelligence Layer not initialized")
    
    try:
        # This would typically return Prometheus-formatted metrics
        # For now, return a simple status
        return {
            "prometheus_endpoint": f"http://localhost:{config.api.prometheus_port}/metrics",
            "status": "available"
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=config.api.host, 
        port=config.api.port,
        log_level=config.logging.level.lower()
    ) 