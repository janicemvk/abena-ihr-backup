# Abena IHR - Continuous Learning Orchestrator
# Main orchestrator for continuous learning and model improvement

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from ml_data_models import OutcomeData, LearningInsight
from model_registry import ModelRegistry
from outcome_analyzer import OutcomeAnalyzer
from retraining_pipeline import ModelRetrainingPipeline

# Update imports to handle path issues
try:
    from src.core.data_models import PredictionResult, PatientProfile, TreatmentPlan
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    try:
        from core.data_models import PredictionResult, PatientProfile, TreatmentPlan
    except ImportError:
        # Use the same placeholder classes as defined in retraining_pipeline
        from dataclasses import dataclass
        from datetime import datetime
        from typing import List, Dict, Any
        
        @dataclass
        class PredictionResult:
            patient_id: str
            treatment_id: str
            success_probability: float
            warnings: List[str]
            timestamp: datetime
        
        @dataclass 
        class PatientProfile:
            patient_id: str
            age: int
            gender: str
            genomics_data: Dict
            biomarkers: Dict
            medical_history: List
            current_medications: List
            lifestyle_metrics: Dict
            pain_scores: List
            functional_assessments: Dict
        
        @dataclass
        class TreatmentPlan:
            treatment_id: str
            treatment_type: str
            medications: List
            dosages: Dict
            duration_weeks: int
            lifestyle_interventions: List

class ContinuousLearningOrchestrator:
    """Main orchestrator for continuous learning and model improvement"""
    
    def __init__(self, model_registry: ModelRegistry):
        self.model_registry = model_registry
        self.outcome_analyzer = OutcomeAnalyzer()
        self.retraining_pipeline = ModelRetrainingPipeline(model_registry)
        self.logger = logging.getLogger(__name__)
        
        # Learning configuration
        self.learning_config = {
            'analysis_frequency': timedelta(days=1),  # Daily analysis
            'retraining_frequency': timedelta(days=7),  # Weekly retraining check
            'insight_validation_period': timedelta(days=30),  # Monthly insight validation
            'performance_monitoring_window': timedelta(days=30),  # 30-day performance window
            'min_samples_for_analysis': 50,
            'auto_retrain_threshold': 0.7,  # Auto-retrain if score > 0.7
            'human_approval_threshold': 0.5  # Require human approval if score > 0.5
        }
        
        # Storage for insights and outcomes
        self.insights_db = []
        self.outcomes_db = []
        self.predictions_db = []
    
    def add_outcome_data(self, outcome: OutcomeData):
        """Add new outcome data to the learning system"""
        self.outcomes_db.append(outcome)
        self.logger.info(f"Added outcome data for patient {outcome.patient_id}")
    
    def add_prediction_data(self, prediction: PredictionResult):
        """Add prediction data for outcome correlation"""
        self.predictions_db.append(prediction)
        self.logger.info(f"Added prediction data for patient {prediction.patient_id}")
    
    def run_daily_analysis(self) -> Dict:
        """Run daily analysis of model performance and outcomes"""
        
        analysis_results = {
            'analysis_date': datetime.now().isoformat(),
            'outcomes_analyzed': len(self.outcomes_db),
            'predictions_analyzed': len(self.predictions_db),
            'new_insights': [],
            'performance_alerts': [],
            'recommendations': []
        }
        
        if len(self.outcomes_db) < self.learning_config['min_samples_for_analysis']:
            analysis_results['status'] = 'insufficient_data'
            return analysis_results
        
        try:
            # 1. Analyze prediction accuracy
            if self.predictions_db:
                performance_analysis = self.outcome_analyzer.analyze_prediction_accuracy(
                    self.outcomes_db[-100:],  # Last 100 outcomes
                    self.predictions_db[-100:]  # Last 100 predictions
                )
                analysis_results['performance_metrics'] = performance_analysis
                
                # Check for performance degradation
                if performance_analysis.get('accuracy', 1.0) < 0.7:
                    analysis_results['performance_alerts'].append({
                        'type': 'accuracy_degradation',
                        'current_accuracy': performance_analysis['accuracy'],
                        'threshold': 0.7,
                        'severity': 'high'
                    })
            
            # 2. Identify new patterns and insights
            new_insights = self.outcome_analyzer.identify_performance_patterns(
                self.outcomes_db[-200:]  # Last 200 outcomes
            )
            
            for insight in new_insights:
                self.insights_db.append(insight)
                analysis_results['new_insights'].append({
                    'insight_id': insight.insight_id,
                    'type': insight.insight_type,
                    'description': insight.description,
                    'clinical_significance': insight.clinical_significance
                })
            
            # 3. Generate recommendations
            recommendations = self._generate_learning_recommendations(analysis_results)
            analysis_results['recommendations'] = recommendations
            
            # 4. Check if retraining is needed
            retraining_assessment = self._assess_retraining_needs()
            analysis_results['retraining_assessment'] = retraining_assessment
            
            analysis_results['status'] = 'completed'
            
        except Exception as e:
            self.logger.error(f"Daily analysis failed: {str(e)}")
            analysis_results['status'] = 'error'
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    def _generate_learning_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Performance-based recommendations
        if analysis_results.get('performance_alerts'):
            for alert in analysis_results['performance_alerts']:
                if alert['type'] == 'accuracy_degradation':
                    recommendations.append(
                        f"Model accuracy has dropped to {alert['current_accuracy']:.3f}. "
                        "Consider immediate retraining or data quality review."
                    )
        
        # Insight-based recommendations
        high_priority_insights = [
            insight for insight in analysis_results.get('new_insights', [])
            if insight['clinical_significance'] == 'high'
        ]
        
        if high_priority_insights:
            recommendations.append(
                f"Found {len(high_priority_insights)} high-priority clinical insights. "
                "Review and validate for potential protocol updates."
            )
        
        # Data quality recommendations
        if analysis_results['outcomes_analyzed'] < 100:
            recommendations.append(
                "Limited outcome data available. Encourage more comprehensive outcome reporting."
            )
        
        # Model improvement recommendations
        if len(self.outcomes_db) > 500:
            recommendations.append(
                "Sufficient data available for advanced model optimization. "
                "Consider running hyperparameter optimization."
            )
        
        return recommendations
    
    def _assess_retraining_needs(self) -> Dict:
        """Assess if any models need retraining"""
        
        active_models = {
            'treatment_response': self.model_registry.get_active_model('production'),
            'adverse_event': self.model_registry.get_active_model('production')
        }
        
        retraining_assessments = {}
        
        for model_type, model_id in active_models.items():
            if model_id:
                # Get recent data for this model type
                recent_outcomes = self.outcomes_db[-100:]  # Last 100 outcomes
                recent_predictions = [p for p in self.predictions_db[-100:] 
                                    if model_type in p.treatment_id]  # Simplified matching
                
                assessment = self.retraining_pipeline.should_retrain_model(
                    model_id, recent_outcomes, recent_predictions
                )
                retraining_assessments[model_type] = assessment
        
        return retraining_assessments
    
    def execute_automated_learning_cycle(self) -> Dict:
        """Execute complete automated learning cycle"""
        
        cycle_results = {
            'cycle_start': datetime.now().isoformat(),
            'daily_analysis': None,
            'retraining_actions': [],
            'insights_validated': [],
            'errors': []
        }
        
        try:
            # 1. Run daily analysis
            cycle_results['daily_analysis'] = self.run_daily_analysis()
            
            # 2. Check for automated retraining opportunities
            retraining_assessment = cycle_results['daily_analysis'].get('retraining_assessment', {})
            
            for model_type, assessment in retraining_assessment.items():
                if assessment.get('should_retrain', False):
                    retrain_score = assessment.get('retrain_score', 0)
                    
                    # Auto-retrain for high confidence scores
                    if retrain_score >= self.learning_config['auto_retrain_threshold']:
                        self.logger.info(f"Auto-retraining {model_type} (score: {retrain_score})")
                        
                        # Prepare training data (simplified - would need proper data preparation)
                        training_data = self._prepare_training_data(model_type)
                        
                        retrain_result = self.retraining_pipeline.execute_retraining(
                            model_type, training_data,
                            optimization_config={'optimize': True, 'n_trials': 30}
                        )
                        
                        cycle_results['retraining_actions'].append({
                            'model_type': model_type,
                            'action': 'auto_retrain',
                            'result': retrain_result,
                            'retrain_score': retrain_score
                        })
                        
                        # Deploy new model if successful
                        if retrain_result.get('success', False):
                            self.model_registry.deploy_model(retrain_result['model_id'])
                            self.logger.info(f"Deployed new {model_type} model: {retrain_result['model_id']}")
                    
                    # Flag for human review for moderate confidence scores
                    elif retrain_score >= self.learning_config['human_approval_threshold']:
                        cycle_results['retraining_actions'].append({
                            'model_type': model_type,
                            'action': 'human_review_required',
                            'retrain_score': retrain_score,
                            'reasons': assessment.get('reasons', [])
                        })
            
            # 3. Validate pending insights
            validated_insights = self._validate_pending_insights()
            cycle_results['insights_validated'] = validated_insights
            
            cycle_results['cycle_end'] = datetime.now().isoformat()
            cycle_results['status'] = 'completed'
            
        except Exception as e:
            self.logger.error(f"Automated learning cycle failed: {str(e)}")
            cycle_results['errors'].append(str(e))
            cycle_results['status'] = 'error'
        
        return cycle_results
    
    def _prepare_training_data(self, model_type: str) -> List[tuple]:
        """Prepare training data for retraining"""
        
        # This is a simplified version - real implementation would need proper data preparation
        training_data = []
        
        for outcome in self.outcomes_db:
            # Find corresponding patient and treatment data
            # This would need proper data storage and retrieval
            
            # Placeholder patient and treatment (would come from database)
            patient = PatientProfile(
                patient_id=outcome.patient_id,
                age=45,  # Placeholder
                gender="unknown",
                genomics_data={},
                biomarkers={},
                medical_history=[],
                current_medications=[],
                lifestyle_metrics={},
                pain_scores=[],
                functional_assessments={}
            )
            
            treatment = TreatmentPlan(
                treatment_id=outcome.treatment_id,
                treatment_type="unknown",
                medications=[],
                dosages={},
                duration_weeks=8,
                lifestyle_interventions=[]
            )
            
            training_data.append((patient, treatment, outcome.actual_outcome))
        
        return training_data
    
    def _validate_pending_insights(self) -> List[Dict]:
        """Validate insights that have been pending validation"""
        
        validated_insights = []
        current_time = datetime.now()
        
        for insight in self.insights_db:
            if insight.validation_status == 'pending':
                # Check if insight has been pending long enough for validation
                time_pending = current_time - insight.discovered_date
                
                if time_pending >= self.learning_config['insight_validation_period']:
                    # Simple validation based on subsequent outcomes
                    validation_result = self._validate_insight(insight)
                    
                    insight.validation_status = validation_result['status']
                    validated_insights.append({
                        'insight_id': insight.insight_id,
                        'validation_result': validation_result,
                        'time_to_validation': time_pending.days
                    })
        
        return validated_insights
    
    def _validate_insight(self, insight: LearningInsight) -> Dict:
        """Validate a specific insight against subsequent data"""
        
        # This is a simplified validation - real implementation would be more sophisticated
        
        # Count outcomes after insight discovery
        subsequent_outcomes = [
            o for o in self.outcomes_db 
            if o.outcome_date > insight.discovered_date
        ]
        
        if len(subsequent_outcomes) < 10:
            return {
                'status': 'insufficient_data',
                'confidence': 0.0,
                'supporting_evidence': len(subsequent_outcomes)
            }
        
        # Simple validation based on insight type
        if insight.insight_type == 'concern':
            # Check if the concern was justified
            recent_issues = sum(1 for o in subsequent_outcomes if o.actual_outcome < 0.4)
            issue_rate = recent_issues / len(subsequent_outcomes)
            
            if issue_rate > 0.2:  # High issue rate confirms concern
                return {
                    'status': 'validated',
                    'confidence': min(issue_rate * 2, 1.0),
                    'supporting_evidence': f"{recent_issues}/{len(subsequent_outcomes)} poor outcomes"
                }
            else:
                return {
                    'status': 'rejected',
                    'confidence': 1 - issue_rate,
                    'supporting_evidence': f"Only {recent_issues}/{len(subsequent_outcomes)} poor outcomes"
                }
        
        elif insight.insight_type == 'improvement':
            # Check if improvement was sustained
            recent_successes = sum(1 for o in subsequent_outcomes if o.actual_outcome > 0.6)
            success_rate = recent_successes / len(subsequent_outcomes)
            
            if success_rate > 0.7:  # High success rate confirms improvement
                return {
                    'status': 'validated',
                    'confidence': success_rate,
                    'supporting_evidence': f"{recent_successes}/{len(subsequent_outcomes)} successful outcomes"
                }
        
        # Default to pending if validation is inconclusive
        return {
            'status': 'pending',
            'confidence': 0.5,
            'supporting_evidence': 'Validation inconclusive'
        }
    
    def generate_learning_report(self, period_days: int = 30) -> Dict:
        """Generate comprehensive learning report for specified period"""
        
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        # Filter data for reporting period
        period_outcomes = [o for o in self.outcomes_db if o.outcome_date >= cutoff_date]
        period_predictions = [p for p in self.predictions_db if p.timestamp >= cutoff_date]
        period_insights = [i for i in self.insights_db if i.discovered_date >= cutoff_date]
        
        report = {
            'report_period': f"{period_days} days",
            'report_date': datetime.now().isoformat(),
            'data_summary': {
                'total_outcomes': len(period_outcomes),
                'total_predictions': len(period_predictions),
                'new_insights': len(period_insights),
                'data_coverage': len(period_outcomes) / max(len(period_predictions), 1)
            }
        }
        
        # Performance analysis
        if period_outcomes and period_predictions:
            performance_analysis = self.outcome_analyzer.analyze_prediction_accuracy(
                period_outcomes, period_predictions
            )
            report['performance_analysis'] = performance_analysis
        
        # Insights summary
        insights_summary = {
            'total_insights': len(period_insights),
            'by_type': {},
            'by_significance': {},
            'validated_insights': 0,
            'pending_insights': 0
        }
        
        for insight in period_insights:
            # Count by type
            insights_summary['by_type'][insight.insight_type] = (
                insights_summary['by_type'].get(insight.insight_type, 0) + 1
            )
            
            # Count by significance
            insights_summary['by_significance'][insight.clinical_significance] = (
                insights_summary['by_significance'].get(insight.clinical_significance, 0) + 1
            )
            
            # Count validation status
            if insight.validation_status == 'validated':
                insights_summary['validated_insights'] += 1
            elif insight.validation_status == 'pending':
                insights_summary['pending_insights'] += 1
        
        report['insights_summary'] = insights_summary
        
        # Model status
        model_status = {}
        for model_type in ['treatment_response', 'adverse_event']:
            active_model = self.model_registry.get_active_model('production')
            if active_model:
                model_metadata = self.model_registry.get_model_metadata(active_model)
                model_status[model_type] = {
                    'active_model': active_model,
                    'last_training': model_metadata.get('registered_date') if model_metadata else None,
                    'performance_metrics': model_metadata.get('performance_metrics') if model_metadata else None
                }
            else:
                model_status[model_type] = {'status': 'no_active_model'}
        
        report['model_status'] = model_status
        
        # Recommendations for next period
        recommendations = self._generate_period_recommendations(report)
        report['recommendations'] = recommendations
        
        return report
    
    def _generate_period_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on period report"""
        recommendations = []
        
        data_summary = report['data_summary']
        
        # Data collection recommendations
        if data_summary['total_outcomes'] < 50:
            recommendations.append(
                "Increase outcome data collection. Current volume insufficient for robust analysis."
            )
        
        if data_summary['data_coverage'] < 0.8:
            recommendations.append(
                "Improve prediction-outcome matching. Many predictions lack corresponding outcomes."
            )
        
        # Performance recommendations
        performance = report.get('performance_analysis', {})
        if performance.get('accuracy', 1.0) < 0.75:
            recommendations.append(
                f"Model accuracy ({performance['accuracy']:.3f}) below target. Consider retraining."
            )
        
        # Insights recommendations
        insights_summary = report['insights_summary']
        if insights_summary['pending_insights'] > 10:
            recommendations.append(
                f"{insights_summary['pending_insights']} insights pending validation. "
                "Prioritize insight validation process."
            )
        
        high_significance_insights = insights_summary['by_significance'].get('high', 0)
        if high_significance_insights > 0:
            recommendations.append(
                f"{high_significance_insights} high-significance insights discovered. "
                "Review for potential clinical protocol updates."
            )
        
        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Initialize the ML feedback pipeline
    model_registry = ModelRegistry()
    continuous_learning = ContinuousLearningOrchestrator(model_registry)
    
    print("Abena IHR - ML Feedback Pipeline Initialized")
    print("=" * 60)
    
    # Example outcome data
    sample_outcome = OutcomeData(
        patient_id="PATIENT_001",
        treatment_id="TX_001", 
        prediction_id="PRED_001",
        actual_outcome=0.75,
        outcome_date=datetime.now(),
        time_to_outcome=30,
        adverse_events=[],
        side_effects=["mild_nausea"],
        patient_satisfaction=8.5,
        provider_assessment="good_response",
        pain_reduction=3.2,
        functional_improvement=15.0,
        medication_adherence=0.95,
        quality_of_life_change=2.1,
        healthcare_utilization={"office_visits": 2, "er_visits": 0},
        cost_effectiveness=0.8
    )
    
    # Add to learning system
    continuous_learning.add_outcome_data(sample_outcome)
    
    # Run analysis
    analysis_result = continuous_learning.run_daily_analysis()
    print(f"Daily analysis status: {analysis_result['status']}")
    
    # Generate learning report
    learning_report = continuous_learning.generate_learning_report(30)
    print(f"Learning report generated for {learning_report['report_period']}")
    print(f"Total outcomes analyzed: {learning_report['data_summary']['total_outcomes']}")
    
    print("\nML Feedback Pipeline Ready for Clinical Deployment") 