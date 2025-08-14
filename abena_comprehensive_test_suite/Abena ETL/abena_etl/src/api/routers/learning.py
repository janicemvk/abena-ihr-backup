from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

from src.integration.system_orchestrator import AbenaIntegratedSystem
from src.feedback_loop.ml_feedback_pipeline import ContinuousLearningOrchestrator, ModelRegistry
from src.core.data_models import OutcomeData

router = APIRouter()

# Global system instance (in production, this would be dependency injected)
abena_system = AbenaIntegratedSystem()

@router.post("/daily-learning/execute")
async def execute_daily_learning(background_tasks: BackgroundTasks):
    """Manually trigger daily learning cycle"""
    try:
        # Execute learning in background
        learning_results = await abena_system.execute_daily_learning()
        
        return {
            "status": "completed",
            "execution_time": learning_results.get('execution_date'),
            "components_executed": learning_results.get('components_executed', []),
            "insights_count": len(learning_results.get('insights_discovered', [])),
            "models_updated": len(learning_results.get('models_updated', [])),
            "alerts_generated": len(learning_results.get('alerts_generated', []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning execution failed: {str(e)}")

@router.get("/daily-learning/status")
async def get_learning_status():
    """Get current status of daily learning system"""
    return {
        "system_active": abena_system.learning_task is not None,
        "last_run": abena_system.last_learning_run.isoformat() if abena_system.last_learning_run else None,
        "next_scheduled": abena_system._calculate_next_learning_time().isoformat(),
        "configuration": abena_system.daily_learning_config
    }

@router.get("/learning-reports/{period_days}")
async def get_learning_report(period_days: int = 30):
    """Generate learning report for specified period"""
    try:
        learning_report = abena_system.continuous_learning.generate_learning_report(period_days)
        return learning_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/model-performance")
async def get_model_performance():
    """Get current model performance metrics"""
    try:
        performance_data = {}
        
        # Get performance for each model type
        model_types = ['treatment_response', 'adverse_event']
        
        for model_type in model_types:
            active_model = abena_system.model_registry.get_active_model('production')
            if active_model:
                model_metadata = abena_system.model_registry.get_model_metadata(active_model)
                performance_data[model_type] = {
                    'model_id': active_model,
                    'performance_metrics': model_metadata.get('performance_metrics', {}) if model_metadata else {},
                    'last_updated': model_metadata.get('registered_date') if model_metadata else None
                }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "models": performance_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance retrieval failed: {str(e)}")

@router.get("/insights")
async def get_recent_insights(days: int = 7, significance: Optional[str] = None):
    """Get recent learning insights"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter insights by date and significance
        recent_insights = [
            insight for insight in abena_system.continuous_learning.insights_db
            if insight.discovered_date >= cutoff_date
        ]
        
        if significance:
            recent_insights = [
                insight for insight in recent_insights
                if insight.clinical_significance == significance
            ]
        
        # Convert to dict format for JSON response
        insights_response = []
        for insight in recent_insights:
            insights_response.append({
                'insight_id': insight.insight_id,
                'type': insight.insight_type,
                'description': insight.description,
                'affected_population': insight.affected_population,
                'confidence_level': insight.confidence_level,
                'clinical_significance': insight.clinical_significance,
                'recommendations': insight.actionable_recommendations,
                'validation_status': insight.validation_status,
                'discovered_date': insight.discovered_date.isoformat()
            })
        
        return {
            "period_days": days,
            "total_insights": len(insights_response),
            "insights": insights_response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights retrieval failed: {str(e)}")

@router.post("/insights/{insight_id}/validate")
async def validate_insight(insight_id: str, validation_data: Dict):
    """Manually validate a learning insight"""
    try:
        # Find the insight
        insight = None
        for i in abena_system.continuous_learning.insights_db:
            if i.insight_id == insight_id:
                insight = i
                break
        
        if not insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        # Update validation status
        insight.validation_status = validation_data.get('status', 'validated')
        
        # Add validation notes if provided
        if 'notes' in validation_data:
            insight.supporting_evidence['validation_notes'] = validation_data['notes']
        
        return {
            "insight_id": insight_id,
            "validation_status": insight.validation_status,
            "validated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight validation failed: {str(e)}")

@router.post("/outcomes")
async def add_treatment_outcome(outcome_data: Dict):
    """Add treatment outcome data for learning"""
    try:
        # Process outcome through system
        result = abena_system.process_treatment_outcome(
            outcome_data['patient_id'], 
            outcome_data
        )
        
        return {
            "status": "success",
            "outcome_processed": result.get('outcome_processed', False),
            "immediate_analysis_triggered": result.get('immediate_analysis_triggered', False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outcome processing failed: {str(e)}")

@router.get("/retraining-assessment")
async def get_retraining_assessment():
    """Get current model retraining assessment"""
    try:
        assessment = abena_system.continuous_learning._assess_retraining_needs()
        
        return {
            "assessment_date": datetime.now().isoformat(),
            "retraining_recommendations": assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining assessment failed: {str(e)}")

@router.post("/models/{model_type}/retrain")
async def trigger_model_retraining(model_type: str, background_tasks: BackgroundTasks):
    """Manually trigger model retraining"""
    try:
        if model_type not in ['treatment_response', 'adverse_event']:
            raise HTTPException(status_code=400, detail="Invalid model type")
        
        # Add retraining task to background
        background_tasks.add_task(
            _execute_model_retraining_task, 
            model_type, 
            abena_system
        )
        
        return {
            "status": "retraining_initiated",
            "model_type": model_type,
            "initiated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining initiation failed: {str(e)}")

async def _execute_model_retraining_task(model_type: str, system: AbenaIntegratedSystem):
    """Background task for model retraining"""
    try:
        # Prepare training data
        training_data = await system._prepare_training_data_for_model(model_type)
        
        # Execute retraining
        retrain_result = system.continuous_learning.retraining_pipeline.execute_retraining(
            model_type, training_data,
            optimization_config={'optimize': True, 'n_trials': 50}
        )
        
        if retrain_result.get('success', False):
            # Deploy new model
            system.model_registry.deploy_model(retrain_result['model_id'])
            system.logger.info(f"Background retraining completed for {model_type}")
        else:
            system.logger.error(f"Background retraining failed for {model_type}")
            
    except Exception as e:
        system.logger.error(f"Background retraining task failed: {str(e)}")

@router.get("/learning-dashboard")
async def get_learning_dashboard():
    """Get comprehensive learning dashboard data"""
    try:
        # Get recent learning report
        learning_report = abena_system.continuous_learning.generate_learning_report(30)
        
        # Get model performance
        model_performance = {}
        for model_type in ['treatment_response', 'adverse_event']:
            active_model = abena_system.model_registry.get_active_model('production')
            if active_model:
                model_metadata = abena_system.model_registry.get_model_metadata(active_model)
                model_performance[model_type] = model_metadata.get('performance_metrics', {}) if model_metadata else {}
        
        # Get recent insights
        recent_insights = [
            {
                'type': insight.insight_type,
                'significance': insight.clinical_significance,
                'description': insight.description,
                'discovered_date': insight.discovered_date.isoformat()
            }
            for insight in abena_system.continuous_learning.insights_db[-10:]  # Last 10 insights
        ]
        
        # Get system status
        system_status = {
            'daily_learning_active': abena_system.learning_task is not None,
            'last_learning_run': abena_system.last_learning_run.isoformat() if abena_system.last_learning_run else None,
            'next_scheduled_run': abena_system._calculate_next_learning_time().isoformat()
        }
        
        return {
            "dashboard_generated": datetime.now().isoformat(),
            "learning_report": learning_report,
            "model_performance": model_performance,
            "recent_insights": recent_insights,
            "system_status": system_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

@router.post("/learning-config")
async def update_learning_config(config_updates: Dict):
    """Update daily learning configuration"""
    try:
        # Update configuration
        for key, value in config_updates.items():
            if key in abena_system.daily_learning_config:
                abena_system.daily_learning_config[key] = value
        
        return {
            "status": "configuration_updated",
            "updated_config": abena_system.daily_learning_config,
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration update failed: {str(e)}")

@router.get("/learning-config")
async def get_learning_config():
    """Get current learning configuration"""
    return {
        "current_config": abena_system.daily_learning_config,
        "retrieved_at": datetime.now().isoformat()
    } 