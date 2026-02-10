"""
System Reconciliation Module for Abena IHR System

This module provides regular reconciliation capabilities to identify and resolve
conflicts between recommendations, learning outcomes, and predictive analytics
to ensure system consistency and reliability.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class DiscrepancyType(Enum):
    """Types of system discrepancies"""
    LEARNING_PREDICTION_GAP = "learning_prediction_gap"
    RECOMMENDATION_CONFLICT = "recommendation_conflict"
    OUTCOME_EXPECTATION_MISMATCH = "outcome_expectation_mismatch"
    MODEL_PERFORMANCE_DRIFT = "model_performance_drift"
    CLINICAL_GUIDELINE_DEVIATION = "clinical_guideline_deviation"


class ConflictSeverity(Enum):
    """Severity levels for conflicts"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ReconciliationConflict:
    """Conflict identified during reconciliation"""
    conflict_id: str
    conflict_type: DiscrepancyType
    severity: ConflictSeverity
    description: str
    affected_patients: List[str]
    detection_time: datetime
    resolution_required: bool
    recommended_actions: List[str]
    data_points: Dict[str, Any]


@dataclass
class LearningPredictionGap:
    """Gap between learning outcomes and predictions"""
    treatment_type: str
    predicted_success_rate: float
    actual_success_rate: float
    gap_magnitude: float
    sample_size: int
    confidence_level: float
    trend_direction: str  # improving, declining, stable
    statistical_significance: bool


@dataclass
class ReconciliationReport:
    """Daily reconciliation report"""
    report_id: str
    report_date: datetime
    period_start: datetime
    period_end: datetime
    total_conflicts: int
    conflicts_by_severity: Dict[str, int]
    conflicts_by_type: Dict[str, int]
    learning_prediction_gaps: List[LearningPredictionGap]
    system_health_score: float
    recommendations: List[str]
    action_items: List[str]
    raw_conflicts: List[ReconciliationConflict]


class SystemReconciliation:
    """
    System Reconciliation Service
    Performs regular reconciliation checks across all system components
    """
    
    def __init__(self, integrated_system, config: Optional[Dict] = None):
        """
        Initialize system reconciliation
        
        Args:
            integrated_system: AbenaIntegratedSystem instance
            config: Configuration dictionary
        """
        self.system = integrated_system
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.reconciliation_history = []
        
    def _get_default_config(self) -> Dict:
        """Get default configuration for reconciliation"""
        return {
            'reconciliation_window_days': 7,
            'learning_prediction_threshold': 0.15,  # 15% gap threshold
            'conflict_severity_thresholds': {
                'high': 0.20,     # 20% performance gap
                'medium': 0.10,   # 10% performance gap
                'low': 0.05       # 5% performance gap
            },
            'min_sample_size': 5,
            'statistical_significance_p': 0.05,
            'health_score_weights': {
                'conflict_severity': 0.4,
                'learning_gaps': 0.3,
                'system_consistency': 0.3
            }
        }
    
    def daily_reconciliation(self) -> ReconciliationReport:
        """
        Perform daily reconciliation check across all system components
        
        Returns:
            ReconciliationReport with findings and recommendations
        """
        self.logger.info("Starting daily system reconciliation")
        
        # Define reconciliation period (last 24 hours)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        try:
            # Step 1: Check for recommendation conflicts
            self.logger.info("Step 1: Identifying recent conflicts")
            conflicts = self.identify_recent_conflicts(start_time, end_time)
            
            # Step 2: Analyze learning vs prediction discrepancies
            self.logger.info("Step 2: Analyzing learning-prediction gaps")
            discrepancies = self.analyze_learning_prediction_gaps(start_time, end_time)
            
            # Step 3: Check for model performance drift
            self.logger.info("Step 3: Checking model performance drift")
            drift_conflicts = self._check_model_performance_drift(start_time, end_time)
            
            # Step 4: Validate clinical guideline adherence
            self.logger.info("Step 4: Validating clinical guideline adherence")
            guideline_conflicts = self._check_clinical_guideline_adherence(start_time, end_time)
            
            # Combine all conflicts
            all_conflicts = conflicts + drift_conflicts + guideline_conflicts
            
            # Step 5: Generate reconciliation report
            report = self.generate_reconciliation_report(all_conflicts, discrepancies, start_time, end_time)
            
            # Store in reconciliation history
            self.reconciliation_history.append(report)
            
            self.logger.info(f"Daily reconciliation completed. Found {len(all_conflicts)} conflicts")
            return report
            
        except Exception as e:
            self.logger.error(f"Error during daily reconciliation: {str(e)}")
            raise
    
    def identify_recent_conflicts(self, start_time: datetime, end_time: datetime) -> List[ReconciliationConflict]:
        """
        Identify conflicts in recent recommendations
        
        Args:
            start_time: Start of analysis period
            end_time: End of analysis period
            
        Returns:
            List of identified conflicts
        """
        conflicts = []
        
        try:
            # Get recent recommendations from the feedback loop
            recent_recommendations = self._get_recent_recommendations(start_time, end_time)
            
            for patient_id, rec_data in recent_recommendations.items():
                recommendation = rec_data['recommendation']
                timestamp = rec_data['timestamp']
                
                # Check for internal conflicts within recommendation
                internal_conflicts = self._check_internal_recommendation_conflicts(recommendation, patient_id)
                conflicts.extend(internal_conflicts)
                
                # Check for conflicts with clinical guidelines
                guideline_conflicts = self._check_guideline_conflicts(recommendation, patient_id)
                conflicts.extend(guideline_conflicts)
                
                # Check for conflicts with recent outcomes
                outcome_conflicts = self._check_outcome_conflicts(recommendation, patient_id)
                conflicts.extend(outcome_conflicts)
            
            self.logger.info(f"Identified {len(conflicts)} conflicts in recent recommendations")
            return conflicts
            
        except Exception as e:
            self.logger.error(f"Error identifying recent conflicts: {str(e)}")
            return []
    
    def analyze_learning_prediction_gaps(self, start_time: datetime, end_time: datetime) -> List[LearningPredictionGap]:
        """
        Analyze discrepancies between learning outcomes and predictions
        
        Args:
            start_time: Start of analysis period
            end_time: End of analysis period
            
        Returns:
            List of learning-prediction gaps
        """
        gaps = []
        
        try:
            # Get learning buffer data
            learning_buffer = self.system.feedback_loop.learning_buffer
            
            # Group by treatment type
            treatment_outcomes = defaultdict(list)
            treatment_predictions = defaultdict(list)
            
            for sample in learning_buffer:
                outcome = sample['outcome']
                recommendation = sample['recommendation']
                
                # Only include outcomes within the analysis period
                if start_time <= outcome.outcome_date <= end_time:
                    treatment_name = recommendation['recommendation'].recommended_treatment.treatment_name
                    
                    treatment_outcomes[treatment_name].append({
                        'success': outcome.outcome_success,
                        'predicted_confidence': recommendation['confidence_score'],
                        'actual_outcome': outcome.outcome_success
                    })
            
            # Analyze gaps for each treatment type
            for treatment_name, outcomes in treatment_outcomes.items():
                if len(outcomes) >= self.config['min_sample_size']:
                    gap = self._calculate_learning_prediction_gap(treatment_name, outcomes)
                    if gap:
                        gaps.append(gap)
            
            self.logger.info(f"Analyzed {len(gaps)} learning-prediction gaps")
            return gaps
            
        except Exception as e:
            self.logger.error(f"Error analyzing learning-prediction gaps: {str(e)}")
            return []
    
    def _calculate_learning_prediction_gap(self, treatment_name: str, outcomes: List[Dict]) -> Optional[LearningPredictionGap]:
        """Calculate learning-prediction gap for a specific treatment"""
        if not outcomes:
            return None
        
        # Calculate actual success rate
        successful_outcomes = sum(1 for outcome in outcomes if outcome['success'])
        actual_success_rate = successful_outcomes / len(outcomes)
        
        # Calculate average predicted success rate
        predicted_success_rate = sum(outcome['predicted_confidence'] for outcome in outcomes) / len(outcomes)
        
        # Calculate gap magnitude
        gap_magnitude = abs(actual_success_rate - predicted_success_rate)
        
        # Determine if gap is significant
        if gap_magnitude < self.config['learning_prediction_threshold']:
            return None
        
        # Determine trend direction
        recent_outcomes = sorted(outcomes, key=lambda x: x.get('timestamp', datetime.now()))[-5:]
        if len(recent_outcomes) >= 3:
            recent_success_rate = sum(1 for outcome in recent_outcomes if outcome['success']) / len(recent_outcomes)
            if recent_success_rate > actual_success_rate:
                trend_direction = "improving"
            elif recent_success_rate < actual_success_rate:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
        
        return LearningPredictionGap(
            treatment_type=treatment_name,
            predicted_success_rate=predicted_success_rate,
            actual_success_rate=actual_success_rate,
            gap_magnitude=gap_magnitude,
            sample_size=len(outcomes),
            confidence_level=0.95,  # Would calculate actual confidence level
            trend_direction=trend_direction,
            statistical_significance=gap_magnitude > self.config['statistical_significance_p']
        )
    
    def generate_reconciliation_report(self, conflicts: List[ReconciliationConflict], 
                                     gaps: List[LearningPredictionGap],
                                     start_time: datetime, end_time: datetime) -> ReconciliationReport:
        """
        Generate comprehensive reconciliation report
        
        Args:
            conflicts: List of identified conflicts
            gaps: List of learning-prediction gaps
            start_time: Analysis period start
            end_time: Analysis period end
            
        Returns:
            ReconciliationReport with findings and recommendations
        """
        report_id = f"reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Count conflicts by severity and type
        conflicts_by_severity = {severity.value: 0 for severity in ConflictSeverity}
        conflicts_by_type = {disc_type.value: 0 for disc_type in DiscrepancyType}
        
        for conflict in conflicts:
            conflicts_by_severity[conflict.severity.value] += 1
            conflicts_by_type[conflict.conflict_type.value] += 1
        
        # Calculate system health score
        health_score = self._calculate_system_health_score(conflicts, gaps)
        
        # Generate recommendations and action items
        recommendations = self._generate_recommendations(conflicts, gaps)
        action_items = self._generate_action_items(conflicts, gaps)
        
        return ReconciliationReport(
            report_id=report_id,
            report_date=datetime.now(),
            period_start=start_time,
            period_end=end_time,
            total_conflicts=len(conflicts),
            conflicts_by_severity=conflicts_by_severity,
            conflicts_by_type=conflicts_by_type,
            learning_prediction_gaps=gaps,
            system_health_score=health_score,
            recommendations=recommendations,
            action_items=action_items,
            raw_conflicts=conflicts
        )
    
    def _check_model_performance_drift(self, start_time: datetime, end_time: datetime) -> List[ReconciliationConflict]:
        """Check for model performance drift"""
        conflicts = []
        
        # Get recent performance metrics from model version manager
        model_versions = self.system.predictive_engine.model_version_manager.active_models
        
        for version_id, model_version in model_versions.items():
            # Check if model performance has degraded
            current_metrics = self.system.predictive_engine.model_version_manager._get_current_performance(version_id)
            baseline_metrics = model_version.metrics
            
            accuracy_drift = baseline_metrics.accuracy - current_metrics.get('accuracy', 0)
            
            if accuracy_drift > self.config['conflict_severity_thresholds']['medium']:
                severity = ConflictSeverity.HIGH if accuracy_drift > self.config['conflict_severity_thresholds']['high'] else ConflictSeverity.MEDIUM
                
                conflicts.append(ReconciliationConflict(
                    conflict_id=f"drift_{version_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    conflict_type=DiscrepancyType.MODEL_PERFORMANCE_DRIFT,
                    severity=severity,
                    description=f"Model {model_version.model_name} showing performance drift",
                    affected_patients=[],
                    detection_time=datetime.now(),
                    resolution_required=True,
                    recommended_actions=[
                        "Review model training data",
                        "Consider model retraining",
                        "Investigate data quality issues"
                    ],
                    data_points={
                        'baseline_accuracy': baseline_metrics.accuracy,
                        'current_accuracy': current_metrics.get('accuracy', 0),
                        'drift_magnitude': accuracy_drift
                    }
                ))
        
        return conflicts
    
    def _check_clinical_guideline_adherence(self, start_time: datetime, end_time: datetime) -> List[ReconciliationConflict]:
        """Check adherence to clinical guidelines"""
        conflicts = []
        
        # Get recent recommendations
        recent_recommendations = self._get_recent_recommendations(start_time, end_time)
        
        for patient_id, rec_data in recent_recommendations.items():
            recommendation = rec_data['recommendation']
            
            # Check if recommended treatment follows clinical guidelines
            adherence_issues = self._validate_guideline_adherence(recommendation)
            
            for issue in adherence_issues:
                conflicts.append(ReconciliationConflict(
                    conflict_id=f"guideline_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    conflict_type=DiscrepancyType.CLINICAL_GUIDELINE_DEVIATION,
                    severity=ConflictSeverity.MEDIUM,
                    description=issue['description'],
                    affected_patients=[patient_id],
                    detection_time=datetime.now(),
                    resolution_required=True,
                    recommended_actions=issue['actions'],
                    data_points=issue['data']
                ))
        
        return conflicts
    
    def _get_recent_recommendations(self, start_time: datetime, end_time: datetime) -> Dict:
        """Get recommendations within the specified time period"""
        recent_recommendations = {}
        
        for patient_id, rec_data in self.system.feedback_loop.recommendation_history.items():
            timestamp = rec_data['timestamp']
            if start_time <= timestamp <= end_time:
                recent_recommendations[patient_id] = rec_data
        
        return recent_recommendations
    
    def _check_internal_recommendation_conflicts(self, recommendation, patient_id: str) -> List[ReconciliationConflict]:
        """Check for internal conflicts within a recommendation"""
        conflicts = []
        
        # Check confidence vs risk mitigation alignment
        if recommendation.confidence_score > 0.8 and len(recommendation.risk_mitigation) > 2:
            conflicts.append(ReconciliationConflict(
                conflict_id=f"internal_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                conflict_type=DiscrepancyType.RECOMMENDATION_CONFLICT,
                severity=ConflictSeverity.LOW,
                description="High confidence recommendation with extensive risk mitigation",
                affected_patients=[patient_id],
                detection_time=datetime.now(),
                resolution_required=False,
                recommended_actions=["Review risk assessment", "Validate confidence scoring"],
                data_points={
                    'confidence_score': recommendation.confidence_score,
                    'risk_mitigation_count': len(recommendation.risk_mitigation)
                }
            ))
        
        return conflicts
    
    def _check_guideline_conflicts(self, recommendation, patient_id: str) -> List[ReconciliationConflict]:
        """Check for conflicts with clinical guidelines"""
        conflicts = []
        
        # Placeholder - would implement actual guideline checking
        # For now, check if follow-up schedule is appropriate for treatment type
        treatment_name = recommendation.recommended_treatment.treatment_name
        follow_up_count = len(recommendation.follow_up_schedule)
        
        if 'ACE inhibitors' in treatment_name and follow_up_count < 2:
            conflicts.append(ReconciliationConflict(
                conflict_id=f"guideline_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                conflict_type=DiscrepancyType.CLINICAL_GUIDELINE_DEVIATION,
                severity=ConflictSeverity.MEDIUM,
                description="Insufficient follow-up scheduled for ACE inhibitor therapy",
                affected_patients=[patient_id],
                detection_time=datetime.now(),
                resolution_required=True,
                recommended_actions=["Add additional follow-up appointments", "Review monitoring protocol"],
                data_points={
                    'treatment_name': treatment_name,
                    'follow_up_count': follow_up_count
                }
            ))
        
        return conflicts
    
    def _check_outcome_conflicts(self, recommendation, patient_id: str) -> List[ReconciliationConflict]:
        """Check for conflicts with recent outcomes"""
        conflicts = []
        
        # Get outcome for this patient if available
        if patient_id in self.system.feedback_loop.outcome_history:
            outcome = self.system.feedback_loop.outcome_history[patient_id]
            
            # Check if outcome matches expectation
            if recommendation.confidence_score > 0.7 and not outcome.outcome_success:
                conflicts.append(ReconciliationConflict(
                    conflict_id=f"outcome_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    conflict_type=DiscrepancyType.OUTCOME_EXPECTATION_MISMATCH,
                    severity=ConflictSeverity.HIGH,
                    description="High confidence recommendation resulted in treatment failure",
                    affected_patients=[patient_id],
                    detection_time=datetime.now(),
                    resolution_required=True,
                    recommended_actions=[
                        "Review prediction model accuracy",
                        "Investigate patient factors",
                        "Update confidence scoring algorithm"
                    ],
                    data_points={
                        'predicted_confidence': recommendation.confidence_score,
                        'actual_outcome': outcome.outcome_success,
                        'recovery_time': outcome.recovery_time
                    }
                ))
        
        return conflicts
    
    def _validate_guideline_adherence(self, recommendation) -> List[Dict]:
        """Validate adherence to clinical guidelines"""
        issues = []
        
        # Example validation: Check monitoring requirements
        treatment_name = recommendation.recommended_treatment.treatment_name
        monitoring = recommendation.monitoring_requirements
        
        if 'ACE inhibitors' in treatment_name:
            required_monitoring = ['blood_pressure', 'kidney_function', 'potassium']
            missing_monitoring = set(required_monitoring) - set(monitoring)
            
            if missing_monitoring:
                issues.append({
                    'description': f"Missing required monitoring for {treatment_name}: {', '.join(missing_monitoring)}",
                    'actions': ["Add missing monitoring requirements", "Review clinical protocols"],
                    'data': {'missing_monitoring': list(missing_monitoring)}
                })
        
        return issues
    
    def _calculate_system_health_score(self, conflicts: List[ReconciliationConflict], 
                                     gaps: List[LearningPredictionGap]) -> float:
        """Calculate overall system health score (0-100)"""
        base_score = 100.0
        
        # Deduct points for conflicts by severity
        severity_penalties = {
            ConflictSeverity.CRITICAL: 20,
            ConflictSeverity.HIGH: 10,
            ConflictSeverity.MEDIUM: 5,
            ConflictSeverity.LOW: 1
        }
        
        for conflict in conflicts:
            base_score -= severity_penalties.get(conflict.severity, 0)
        
        # Deduct points for significant learning gaps
        for gap in gaps:
            if gap.gap_magnitude > 0.20:  # >20% gap
                base_score -= 15
            elif gap.gap_magnitude > 0.10:  # >10% gap
                base_score -= 8
            else:
                base_score -= 3
        
        return max(0.0, min(100.0, base_score))
    
    def _generate_recommendations(self, conflicts: List[ReconciliationConflict], 
                                gaps: List[LearningPredictionGap]) -> List[str]:
        """Generate system-level recommendations"""
        recommendations = []
        
        # High-level recommendations based on conflicts
        if any(c.severity == ConflictSeverity.CRITICAL for c in conflicts):
            recommendations.append("URGENT: Critical system conflicts detected - immediate review required")
        
        # Recommendations based on learning gaps
        significant_gaps = [g for g in gaps if g.gap_magnitude > 0.15]
        if significant_gaps:
            recommendations.append(f"Model calibration needed for {len(significant_gaps)} treatment types")
        
        # Pattern-based recommendations
        conflict_types = [c.conflict_type for c in conflicts]
        if conflict_types.count(DiscrepancyType.MODEL_PERFORMANCE_DRIFT) > 1:
            recommendations.append("Multiple models showing performance drift - consider system-wide model refresh")
        
        if not recommendations:
            recommendations.append("System operating within normal parameters")
        
        return recommendations
    
    def _generate_action_items(self, conflicts: List[ReconciliationConflict], 
                             gaps: List[LearningPredictionGap]) -> List[str]:
        """Generate specific action items"""
        action_items = []
        
        # Extract unique actions from conflicts
        all_actions = []
        for conflict in conflicts:
            all_actions.extend(conflict.recommended_actions)
        
        unique_actions = list(set(all_actions))
        action_items.extend(unique_actions)
        
        # Add gap-specific actions
        for gap in gaps:
            if gap.gap_magnitude > 0.20:
                action_items.append(f"Investigate {gap.treatment_type} prediction accuracy")
        
        return action_items
    
    def get_reconciliation_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get reconciliation summary for the specified number of days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_reports = [
            report for report in self.reconciliation_history 
            if report.report_date >= cutoff_date
        ]
        
        if not recent_reports:
            return {'status': 'no_recent_reports', 'days_requested': days}
        
        # Aggregate statistics
        total_conflicts = sum(report.total_conflicts for report in recent_reports)
        avg_health_score = sum(report.system_health_score for report in recent_reports) / len(recent_reports)
        
        # Trending analysis
        health_scores = [report.system_health_score for report in sorted(recent_reports, key=lambda x: x.report_date)]
        health_trend = "stable"
        if len(health_scores) >= 2:
            if health_scores[-1] > health_scores[0] + 5:
                health_trend = "improving"
            elif health_scores[-1] < health_scores[0] - 5:
                health_trend = "declining"
        
        return {
            'period_days': days,
            'reports_analyzed': len(recent_reports),
            'total_conflicts': total_conflicts,
            'avg_health_score': round(avg_health_score, 1),
            'health_trend': health_trend,
            'latest_report_date': recent_reports[-1].report_date.isoformat() if recent_reports else None
        }


# Example usage and testing
if __name__ == "__main__":
    from .integrated_system import AbenaIntegratedSystem, PatientData, TreatmentOutcome
    from datetime import datetime
    
    # Create integrated system
    system = AbenaIntegratedSystem()
    
    # Create reconciliation service
    reconciliation = SystemReconciliation(system)
    
    print("🔍 SYSTEM RECONCILIATION TEST")
    print("=" * 50)
    
    # Perform daily reconciliation
    report = reconciliation.daily_reconciliation()
    
    print(f"📊 RECONCILIATION REPORT")
    print(f"Report ID: {report.report_id}")
    print(f"Period: {report.period_start.strftime('%Y-%m-%d %H:%M')} - {report.period_end.strftime('%Y-%m-%d %H:%M')}")
    print(f"Total Conflicts: {report.total_conflicts}")
    print(f"System Health Score: {report.system_health_score:.1f}/100")
    
    print(f"\n📈 CONFLICTS BY SEVERITY:")
    for severity, count in report.conflicts_by_severity.items():
        if count > 0:
            print(f"   {severity.upper()}: {count}")
    
    print(f"\n📋 LEARNING-PREDICTION GAPS:")
    for gap in report.learning_prediction_gaps:
        print(f"   {gap.treatment_type}: {gap.gap_magnitude:.1%} gap")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"   {i}. {rec}")
    
    print(f"\n✅ System reconciliation test completed!") 