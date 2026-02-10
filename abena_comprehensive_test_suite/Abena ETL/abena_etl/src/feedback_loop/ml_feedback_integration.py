# Abena IHR - ML Feedback Pipeline Integration
# Integration module connecting ML feedback with the existing system

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio

from ml_data_models import OutcomeData, LearningInsight
from model_registry import ModelRegistry
from continuous_learning import ContinuousLearningOrchestrator

# Import existing system components with fallback
try:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    from api.main import app
    from core.database import get_session, Patient, Treatment, Prediction
    from predictive_analytics.predictive_engine import TreatmentResponsePredictor
    from workflow_integration.care_coordinator import CareCoordinator
    from clinical_context.context_manager import ClinicalContextManager
except ImportError as e:
    logging.warning(f"Could not import all system components: {e}")
    # Create mock components for standalone testing
    app = None
    get_session = None

class MLFeedbackIntegrator:
    """Main integration class for ML feedback pipeline with Abena IHR system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize ML feedback components
        self.model_registry = ModelRegistry()
        self.continuous_learning = ContinuousLearningOrchestrator(self.model_registry)
        
        # Configuration
        self.integration_config = {
            'automatic_outcome_collection': True,
            'real_time_feedback': True,
            'daily_analysis_enabled': True,
            'auto_retraining_enabled': True,
            'alert_thresholds': {
                'accuracy_decline': 0.05,
                'prediction_confidence_low': 0.3,
                'adverse_event_rate_high': 0.15
            }
        }
        
        # Initialize background tasks
        self._background_tasks = []
        self._is_running = False
    
    async def initialize_integration(self) -> Dict:
        """Initialize the ML feedback integration with existing system"""
        
        try:
            self.logger.info("Initializing ML Feedback Pipeline Integration")
            
            # Start background monitoring
            if self.integration_config['daily_analysis_enabled']:
                await self._start_daily_analysis_task()
            
            if self.integration_config['real_time_feedback']:
                await self._start_real_time_monitoring()
            
            self._is_running = True
            
            return {
                'status': 'success',
                'message': 'ML Feedback Pipeline integrated successfully',
                'features_enabled': {
                    'automatic_outcome_collection': self.integration_config['automatic_outcome_collection'],
                    'real_time_feedback': self.integration_config['real_time_feedback'],
                    'daily_analysis': self.integration_config['daily_analysis_enabled'],
                    'auto_retraining': self.integration_config['auto_retraining_enabled']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML feedback integration: {e}")
            return {
                'status': 'error',
                'message': f'Integration failed: {str(e)}'
            }
    
    async def collect_outcome_from_patient_record(self, patient_id: str, 
                                                treatment_id: str) -> Optional[OutcomeData]:
        """Collect outcome data from patient records"""
        
        try:
            # This would integrate with your existing database
            # For now, we'll create a sample outcome
            
            outcome = OutcomeData(
                patient_id=patient_id,
                treatment_id=treatment_id,
                prediction_id=f"pred_{patient_id}_{treatment_id}",
                actual_outcome=0.8,  # Would come from real patient data
                outcome_date=datetime.now(),
                time_to_outcome=30,
                adverse_events=[],
                side_effects=["mild_fatigue"],
                patient_satisfaction=8.5,
                provider_assessment="good_response",
                pain_reduction=4.2,
                functional_improvement=25.0,
                medication_adherence=0.92,
                quality_of_life_change=3.1,
                healthcare_utilization={"office_visits": 3, "er_visits": 0},
                cost_effectiveness=0.85,
                additional_metrics={
                    'treatment_type': 'comprehensive_pain_management',
                    'follow_up_compliance': True,
                    'side_effect_severity': 'mild'
                }
            )
            
            # Add to continuous learning system
            self.continuous_learning.add_outcome_data(outcome)
            
            self.logger.info(f"Collected outcome for patient {patient_id}, treatment {treatment_id}")
            return outcome
            
        except Exception as e:
            self.logger.error(f"Failed to collect outcome data: {e}")
            return None
    
    async def process_new_prediction(self, prediction_result: Any) -> Dict:
        """Process new prediction and add to feedback system"""
        
        try:
            # Convert prediction to our format and add to system
            self.continuous_learning.add_prediction_data(prediction_result)
            
            # Run real-time analysis if enabled
            if self.integration_config['real_time_feedback']:
                analysis = await self._run_real_time_analysis(prediction_result)
                return analysis
            
            return {'status': 'prediction_recorded'}
            
        except Exception as e:
            self.logger.error(f"Failed to process prediction: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _run_real_time_analysis(self, prediction_result: Any) -> Dict:
        """Run real-time analysis on new prediction"""
        
        # Check prediction confidence
        if hasattr(prediction_result, 'success_probability'):
            confidence = prediction_result.success_probability
            
            if confidence < self.integration_config['alert_thresholds']['prediction_confidence_low']:
                alert = {
                    'type': 'low_prediction_confidence',
                    'patient_id': prediction_result.patient_id,
                    'confidence': confidence,
                    'recommendation': 'Consider additional clinical review',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Send alert to clinical team
                await self._send_clinical_alert(alert)
                
                return {
                    'status': 'alert_generated',
                    'alert': alert
                }
        
        return {'status': 'no_action_needed'}
    
    async def _send_clinical_alert(self, alert: Dict):
        """Send alert to clinical team"""
        
        self.logger.warning(f"Clinical Alert: {alert['type']} for patient {alert['patient_id']}")
        
        # Integration point: Send to your notification system
        # This could integrate with your existing alert system
        pass
    
    async def _start_daily_analysis_task(self):
        """Start daily analysis background task"""
        
        async def daily_analysis():
            while self._is_running:
                try:
                    # Run daily analysis
                    results = self.continuous_learning.run_daily_analysis()
                    
                    # Process results and generate alerts if needed
                    await self._process_daily_analysis_results(results)
                    
                    # Wait 24 hours
                    await asyncio.sleep(24 * 60 * 60)  # 24 hours
                    
                except Exception as e:
                    self.logger.error(f"Daily analysis task failed: {e}")
                    await asyncio.sleep(60 * 60)  # Wait 1 hour before retry
        
        task = asyncio.create_task(daily_analysis())
        self._background_tasks.append(task)
        self.logger.info("Daily analysis task started")
    
    async def _start_real_time_monitoring(self):
        """Start real-time monitoring background task"""
        
        async def real_time_monitor():
            while self._is_running:
                try:
                    # Check for system health and performance
                    await self._monitor_system_health()
                    
                    # Wait 15 minutes
                    await asyncio.sleep(15 * 60)
                    
                except Exception as e:
                    self.logger.error(f"Real-time monitoring failed: {e}")
                    await asyncio.sleep(5 * 60)  # Wait 5 minutes before retry
        
        task = asyncio.create_task(real_time_monitor())
        self._background_tasks.append(task)
        self.logger.info("Real-time monitoring started")
    
    async def _monitor_system_health(self):
        """Monitor overall system health"""
        
        # Check data flow
        recent_outcomes = len([
            o for o in self.continuous_learning.outcomes_db 
            if o.outcome_date >= datetime.now() - timedelta(hours=24)
        ])
        
        recent_predictions = len([
            p for p in self.continuous_learning.predictions_db 
            if p.timestamp >= datetime.now() - timedelta(hours=24)
        ])
        
        # Generate health report
        health_status = {
            'recent_outcomes': recent_outcomes,
            'recent_predictions': recent_predictions,
            'data_flow_healthy': recent_outcomes > 0 and recent_predictions > 0,
            'timestamp': datetime.now().isoformat()
        }
        
        if not health_status['data_flow_healthy']:
            self.logger.warning("Low data flow detected in ML feedback pipeline")
    
    async def _process_daily_analysis_results(self, results: Dict):
        """Process daily analysis results and generate appropriate actions"""
        
        # Check for performance alerts
        if results.get('performance_alerts'):
            for alert in results['performance_alerts']:
                if alert['type'] == 'accuracy_degradation':
                    clinical_alert = {
                        'type': 'model_performance_decline',
                        'severity': alert['severity'],
                        'current_accuracy': alert['current_accuracy'],
                        'recommendation': 'Model retraining recommended',
                        'timestamp': datetime.now().isoformat()
                    }
                    await self._send_clinical_alert(clinical_alert)
        
        # Process new insights
        if results.get('new_insights'):
            await self._process_clinical_insights(results['new_insights'])
        
        # Check retraining recommendations
        if results.get('retraining_assessment'):
            await self._process_retraining_recommendations(results['retraining_assessment'])
    
    async def _process_clinical_insights(self, insights: List[Dict]):
        """Process and act on clinical insights"""
        
        high_priority_insights = [
            insight for insight in insights 
            if insight['clinical_significance'] == 'high'
        ]
        
        if high_priority_insights:
            for insight in high_priority_insights:
                clinical_alert = {
                    'type': 'clinical_insight',
                    'insight_type': insight['type'],
                    'description': insight['description'],
                    'severity': 'high',
                    'recommendations': insight.get('actionable_recommendations', []),
                    'timestamp': datetime.now().isoformat()
                }
                await self._send_clinical_alert(clinical_alert)
    
    async def _process_retraining_recommendations(self, assessment: Dict):
        """Process model retraining recommendations"""
        
        for model_type, recommendation in assessment.items():
            if recommendation.get('should_retrain'):
                score = recommendation.get('retrain_score', 0)
                
                if score >= self.integration_config.get('auto_retrain_threshold', 0.7):
                    # Automatic retraining
                    self.logger.info(f"Initiating automatic retraining for {model_type}")
                    # This would trigger the retraining pipeline
                
                elif score >= 0.5:
                    # Alert for manual review
                    alert = {
                        'type': 'retraining_recommendation',
                        'model_type': model_type,
                        'retrain_score': score,
                        'reasons': recommendation.get('reasons', []),
                        'action_required': 'manual_review',
                        'timestamp': datetime.now().isoformat()
                    }
                    await self._send_clinical_alert(alert)
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        
        return {
            'integration_status': 'active' if self._is_running else 'inactive',
            'total_outcomes': len(self.continuous_learning.outcomes_db),
            'total_predictions': len(self.continuous_learning.predictions_db),
            'total_insights': len(self.continuous_learning.insights_db),
            'background_tasks': len(self._background_tasks),
            'configuration': self.integration_config,
            'last_analysis': 'Not yet run',  # Would track actual last run
            'model_registry_status': 'active'
        }
    
    async def shutdown(self):
        """Gracefully shutdown the integration"""
        
        self._is_running = False
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        self.logger.info("ML Feedback Integration shutdown complete")

# Global integrator instance
ml_integrator = MLFeedbackIntegrator()

# FastAPI integration points (if available)
if app is not None:
    @app.on_event("startup")
    async def startup_ml_feedback():
        """Initialize ML feedback on application startup"""
        result = await ml_integrator.initialize_integration()
        logging.info(f"ML Feedback Integration: {result}")
    
    @app.on_event("shutdown")
    async def shutdown_ml_feedback():
        """Shutdown ML feedback on application shutdown"""
        await ml_integrator.shutdown()
    
    @app.get("/api/ml-feedback/status")
    async def get_ml_feedback_status():
        """Get ML feedback system status"""
        return ml_integrator.get_system_status()
    
    @app.post("/api/ml-feedback/collect-outcome/{patient_id}/{treatment_id}")
    async def collect_patient_outcome(patient_id: str, treatment_id: str):
        """Manually trigger outcome collection for a patient"""
        outcome = await ml_integrator.collect_outcome_from_patient_record(patient_id, treatment_id)
        if outcome:
            return {
                'status': 'success',
                'message': f'Outcome collected for patient {patient_id}',
                'outcome_id': outcome.prediction_id
            }
        else:
            return {
                'status': 'error',
                'message': 'Failed to collect outcome'
            }

# Example usage and testing
if __name__ == "__main__":
    async def test_integration():
        """Test the ML feedback integration"""
        
        print("Testing ML Feedback Integration...")
        print("=" * 50)
        
        # Initialize
        result = await ml_integrator.initialize_integration()
        print(f"Initialization: {result['status']}")
        
        # Test outcome collection
        outcome = await ml_integrator.collect_outcome_from_patient_record("TEST_001", "TX_001")
        if outcome:
            print(f"Outcome collected: {outcome.patient_id}")
        
        # Get status
        status = ml_integrator.get_system_status()
        print(f"System status: {status['integration_status']}")
        print(f"Total outcomes: {status['total_outcomes']}")
        
        # Shutdown
        await ml_integrator.shutdown()
        print("Integration test completed")
    
    # Run test
    asyncio.run(test_integration()) 