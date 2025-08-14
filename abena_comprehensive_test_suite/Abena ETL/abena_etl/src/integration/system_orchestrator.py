from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
import logging
from dataclasses import asdict

# Import existing components
from src.predictive_analytics.predictive_engine import PredictiveAnalyticsEngine
from src.workflow_integration.workflow_orchestrator import WorkflowIntegrationOrchestrator
from src.clinical_context.clinical_context_module import ClinicalContextModule
from src.feedback_loop.ml_feedback_pipeline import (
    ContinuousLearningOrchestrator, 
    ModelRegistry,
    OutcomeData
)
from src.realtime_biomarkers.realtime_biomarker_integration import RealTimeBiomarkerIntegration

class AbenaIntegratedSystem:
    """Enhanced system orchestrator with daily automated learning"""
    
    def __init__(self):
        # Initialize core components
        self.model_registry = ModelRegistry()
        self.predictive_engine = PredictiveAnalyticsEngine()
        self.workflow_integration = WorkflowIntegrationOrchestrator({})
        self.clinical_context = ClinicalContextModule()
        self.continuous_learning = ContinuousLearningOrchestrator(self.model_registry)
        self.realtime_biomarkers = RealTimeBiomarkerIntegration()
        self.conflict_resolver = ConflictResolutionEngine()
        self.logger = logging.getLogger(__name__)
        
        # Daily learning configuration
        self.daily_learning_config = {
            'learning_schedule': '02:00',  # 2 AM daily
            'analysis_enabled': True,
            'auto_retrain_enabled': True,
            'notification_enabled': True
        }
        
        # Learning state tracking
        self.last_learning_run = None
        self.learning_task = None
        
    async def start_daily_learning_cycle(self):
        """Start the automated daily learning cycle"""
        self.logger.info("Starting automated daily learning cycle")
        
        # Schedule daily learning task
        self.learning_task = asyncio.create_task(self._daily_learning_scheduler())
        
        return True
    
    async def _daily_learning_scheduler(self):
        """Scheduler for daily learning tasks"""
        while True:
            try:
                # Calculate next run time
                next_run = self._calculate_next_learning_time()
                sleep_seconds = (next_run - datetime.now()).total_seconds()
                
                if sleep_seconds > 0:
                    self.logger.info(f"Next learning cycle scheduled for {next_run}")
                    await asyncio.sleep(sleep_seconds)
                
                # Execute daily learning
                await self.execute_daily_learning()
                
                # Update last run time
                self.last_learning_run = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Daily learning scheduler error: {str(e)}")
                # Sleep for an hour before retrying
                await asyncio.sleep(3600)
    
    def _calculate_next_learning_time(self) -> datetime:
        """Calculate next learning execution time"""
        now = datetime.now()
        scheduled_time = datetime.strptime(self.daily_learning_config['learning_schedule'], '%H:%M').time()
        
        # Calculate today's scheduled time
        today_scheduled = datetime.combine(now.date(), scheduled_time)
        
        # If today's time has passed, schedule for tomorrow
        if now > today_scheduled:
            return today_scheduled + timedelta(days=1)
        else:
            return today_scheduled
    
    async def execute_daily_learning(self) -> Dict:
        """Execute the complete daily learning process"""
        learning_results = {
            'execution_date': datetime.now().isoformat(),
            'status': 'running',
            'components_executed': [],
            'insights_discovered': [],
            'models_updated': [],
            'alerts_generated': [],
            'errors': []
        }
        
        try:
            self.logger.info("Executing daily automated learning cycle")
            
            # 1. Run daily outcome analysis
            if self.daily_learning_config['analysis_enabled']:
                analysis_result = await self._execute_daily_analysis()
                learning_results['components_executed'].append('daily_analysis')
                learning_results['insights_discovered'] = analysis_result.get('new_insights', [])
                learning_results['alerts_generated'] = analysis_result.get('performance_alerts', [])
            
            # 2. Execute model retraining if needed
            if self.daily_learning_config['auto_retrain_enabled']:
                retraining_result = await self._execute_model_retraining()
                learning_results['components_executed'].append('model_retraining')
                learning_results['models_updated'] = retraining_result.get('updated_models', [])
            
            # 3. Update predictive models with new insights
            await self._update_predictive_models_with_insights(learning_results)
            learning_results['components_executed'].append('model_updates')
            
            # 4. Generate learning reports
            learning_report = await self._generate_daily_learning_report(learning_results)
            learning_results['learning_report'] = learning_report
            learning_results['components_executed'].append('report_generation')
            
            # 5. Send notifications if enabled
            if self.daily_learning_config['notification_enabled']:
                await self._send_learning_notifications(learning_results)
                learning_results['components_executed'].append('notifications')
            
            learning_results['status'] = 'completed'
            self.logger.info("Daily automated learning cycle completed successfully")
            
        except Exception as e:
            learning_results['status'] = 'error'
            learning_results['errors'].append(str(e))
            self.logger.error(f"Daily learning cycle failed: {str(e)}")
        
        return learning_results
    
    async def _execute_daily_analysis(self) -> Dict:
        """Execute daily outcome analysis"""
        return self.continuous_learning.run_daily_analysis()
    
    async def _execute_model_retraining(self) -> Dict:
        """Execute automated model retraining"""
        retraining_results = {
            'updated_models': [],
            'retraining_decisions': {},
            'performance_improvements': {}
        }
        
        # Get retraining assessment
        retraining_assessment = self.continuous_learning._assess_retraining_needs()
        
        for model_type, assessment in retraining_assessment.items():
            retraining_results['retraining_decisions'][model_type] = assessment
            
            if assessment.get('should_retrain', False):
                retrain_score = assessment.get('retrain_score', 0)
                
                # Auto-retrain for high confidence scores
                if retrain_score >= 0.7:  # High confidence threshold
                    self.logger.info(f"Auto-retraining {model_type} (score: {retrain_score})")
                    
                    # Prepare training data
                    training_data = await self._prepare_training_data_for_model(model_type)
                    
                    # Execute retraining
                    retrain_result = self.continuous_learning.retraining_pipeline.execute_retraining(
                        model_type, training_data,
                        optimization_config={'optimize': True, 'n_trials': 30}
                    )
                    
                    if retrain_result.get('success', False):
                        # Deploy new model
                        self.model_registry.deploy_model(retrain_result['model_id'])
                        
                        retraining_results['updated_models'].append({
                            'model_type': model_type,
                            'model_id': retrain_result['model_id'],
                            'performance_improvement': retrain_result.get('performance_metrics', {}),
                            'retrain_score': retrain_score
                        })
                        
                        self.logger.info(f"Successfully retrained and deployed {model_type}")
        
        return retraining_results
    
    async def _prepare_training_data_for_model(self, model_type: str) -> List:
        """Prepare training data for specific model type"""
        # This would integrate with your data storage to get recent outcomes
        # For now, return sample data structure
        return []
    
    async def _update_predictive_models_with_insights(self, learning_results: Dict):
        """Update predictive models based on learning insights"""
        insights = learning_results.get('insights_discovered', [])
        
        for insight in insights:
            if insight.get('clinical_significance') == 'high':
                # Update model parameters or thresholds based on insights
                await self._apply_insight_to_models(insight)
    
    async def _apply_insight_to_models(self, insight: Dict):
        """Apply specific insight to predictive models"""
        # This would update model parameters, thresholds, or feature weights
        # based on discovered insights
        self.logger.info(f"Applying insight to models: {insight.get('description', 'Unknown insight')}")
    
    async def _generate_daily_learning_report(self, learning_results: Dict) -> Dict:
        """Generate comprehensive daily learning report"""
        return self.continuous_learning.generate_learning_report(period_days=1)
    
    async def _send_learning_notifications(self, learning_results: Dict):
        """Send notifications about learning results"""
        
        # High-priority notifications
        if learning_results.get('alerts_generated'):
            await self._send_priority_alerts(learning_results['alerts_generated'])
        
        # Model update notifications
        if learning_results.get('models_updated'):
            await self._send_model_update_notifications(learning_results['models_updated'])
        
        # Daily summary notification
        await self._send_daily_summary_notification(learning_results)
    
    async def _send_priority_alerts(self, alerts: List[Dict]):
        """Send high-priority alerts to clinical teams"""
        for alert in alerts:
            if alert.get('severity') == 'high':
                # Send immediate notification
                self.logger.critical(f"HIGH PRIORITY LEARNING ALERT: {alert}")
                # This would integrate with your alert system
    
    async def _send_model_update_notifications(self, updated_models: List[Dict]):
        """Send notifications about model updates"""
        for model_update in updated_models:
            self.logger.info(f"Model updated: {model_update['model_type']} -> {model_update['model_id']}")
            # This would notify relevant clinical teams
    
    async def _send_daily_summary_notification(self, learning_results: Dict):
        """Send daily learning summary"""
        summary = {
            'date': datetime.now().date().isoformat(),
            'components_executed': len(learning_results.get('components_executed', [])),
            'insights_discovered': len(learning_results.get('insights_discovered', [])),
            'models_updated': len(learning_results.get('models_updated', [])),
            'status': learning_results.get('status', 'unknown')
        }
        
        self.logger.info(f"Daily learning summary: {summary}")
        # This would send to clinical dashboard or email
    
    # EXISTING METHODS (from previous system orchestrator)
    
    def generate_treatment_plan(self, patient_id: str) -> Dict:
        """Enhanced treatment plan generation with learning integration"""
        
        # 1. Get clinical context recommendations
        clinical_recommendations = self.clinical_context.analyze_patient(patient_id)
        
        # 2. Get real-time biomarker data if available
        realtime_data = None
        try:
            realtime_data = self.realtime_biomarkers.get_real_time_patient_data(patient_id)
        except Exception as e:
            self.logger.warning(f"Could not get real-time data for {patient_id}: {str(e)}")
        
        # 3. Generate predictions with enhanced data
        prediction_results = []
        for treatment in clinical_recommendations.treatment_options:
            if realtime_data:
                # Use enhanced predictor with real-time data
                prediction = self.predictive_engine.predict_with_realtime_data(
                    patient_id, treatment, realtime_data
                )
            else:
                # Use standard prediction
                prediction = self.predictive_engine.predict_treatment_response(
                    patient_id, treatment
                )
            prediction_results.append(prediction)
        
        # 4. Resolve conflicts between recommendations and predictions
        final_recommendation = self.conflict_resolver.resolve_conflicts(
            clinical_recommendations, prediction_results
        )
        
        # 5. Track recommendation for learning
        self.continuous_learning.add_prediction_data(final_recommendation)
        
        return final_recommendation
    
    def process_treatment_outcome(self, patient_id: str, outcome_data: Dict) -> Dict:
        """Enhanced outcome processing with automated learning"""
        
        # Create outcome data structure
        outcome = OutcomeData(
            patient_id=patient_id,
            treatment_id=outcome_data.get('treatment_id', ''),
            prediction_id=outcome_data.get('prediction_id', ''),
            actual_outcome=outcome_data.get('actual_outcome', 0.0),
            outcome_date=datetime.now(),
            time_to_outcome=outcome_data.get('time_to_outcome', 30),
            adverse_events=outcome_data.get('adverse_events', []),
            side_effects=outcome_data.get('side_effects', []),
            patient_satisfaction=outcome_data.get('patient_satisfaction', 5.0),
            provider_assessment=outcome_data.get('provider_assessment', ''),
            pain_reduction=outcome_data.get('pain_reduction', 0.0),
            functional_improvement=outcome_data.get('functional_improvement', 0.0),
            medication_adherence=outcome_data.get('medication_adherence', 0.8),
            quality_of_life_change=outcome_data.get('quality_of_life_change', 0.0),
            healthcare_utilization=outcome_data.get('healthcare_utilization', {}),
            cost_effectiveness=outcome_data.get('cost_effectiveness', 0.5)
        )
        
        # Add to continuous learning system
        self.continuous_learning.add_outcome_data(outcome)
        
        # Check if this triggers immediate learning updates
        if outcome.actual_outcome < 0.3:  # Poor outcome
            # Trigger immediate analysis for poor outcomes
            immediate_analysis = self.continuous_learning.run_daily_analysis()
            
            return {
                'outcome_processed': True,
                'immediate_analysis_triggered': True,
                'analysis_results': immediate_analysis
            }
        
        return {
            'outcome_processed': True,
            'immediate_analysis_triggered': False
        }

class ConflictResolutionEngine:
    """Resolves conflicts between different system components"""
    
    def resolve_conflicts(self, clinical_rec, prediction_results):
        """Resolve conflicts between clinical and predictive recommendations"""
        # Implement conflict resolution logic
        return clinical_rec  # Simplified

# Usage example
async def initialize_daily_learning():
    """Initialize the daily learning system"""
    system = AbenaIntegratedSystem()
    
    # Start daily learning cycle
    await system.start_daily_learning_cycle()
    
    return system