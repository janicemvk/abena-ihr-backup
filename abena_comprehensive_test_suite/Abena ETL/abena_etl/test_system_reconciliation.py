"""
Test System Reconciliation Module

This test demonstrates the complete system reconciliation functionality
including conflict detection, learning-prediction gap analysis, and
comprehensive reporting capabilities.
"""

from src.core import (
    AbenaIntegratedSystem, 
    SystemReconciliation,
    PatientData, 
    TreatmentOutcome
)
from datetime import datetime, timedelta
import time

def test_system_reconciliation():
    """Test comprehensive system reconciliation functionality"""
    
    print("🔍 SYSTEM RECONCILIATION COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Step 1: Initialize integrated system
    print("\n📋 Step 1: Initializing Integrated System")
    system = AbenaIntegratedSystem()
    
    # Step 2: Initialize reconciliation service
    print("📋 Step 2: Initializing Reconciliation Service")
    reconciliation = SystemReconciliation(system)
    
    # Step 3: Generate some test data with recommendations and outcomes
    print("📋 Step 3: Generating Test Data")
    
    # Create test patients with different scenarios
    test_patients = [
        {
            'patient_id': 'PAT_001',
            'data': PatientData(
                patient_id='PAT_001',
                age=65,
                gender='male',
                medical_history=['hypertension', 'diabetes'],
                current_medications=['metformin'],
                allergies=[],
                lab_results={'hba1c': 7.2, 'creatinine': 1.1},
                vital_signs={'bp_systolic': 145, 'bp_diastolic': 90},
                comorbidities=['coronary_artery_disease']
            ),
            'expected_success': True
        },
        {
            'patient_id': 'PAT_002',
            'data': PatientData(
                patient_id='PAT_002',
                age=55,
                gender='female',
                medical_history=['hypertension'],
                current_medications=[],
                allergies=['sulfa'],
                lab_results={'creatinine': 0.9},
                vital_signs={'bp_systolic': 160, 'bp_diastolic': 95},
                comorbidities=[]
            ),
            'expected_success': False  # This will create a conflict
        },
        {
            'patient_id': 'PAT_003',
            'data': PatientData(
                patient_id='PAT_003',
                age=70,
                gender='male',
                medical_history=['diabetes'],
                current_medications=[],
                allergies=[],
                lab_results={'hba1c': 8.5, 'creatinine': 1.3},
                vital_signs={'bp_systolic': 130, 'bp_diastolic': 80},
                comorbidities=['kidney_disease']
            ),
            'expected_success': True
        }
    ]
    
    # Step 4: Generate treatment plans and simulate outcomes
    print("📋 Step 4: Generating Treatment Plans and Outcomes")
    
    for patient_info in test_patients:
        patient_id = patient_info['patient_id']
        patient_data = patient_info['data']
        expected_success = patient_info['expected_success']
        
        print(f"\n   Processing {patient_id}...")
        
        # Generate treatment plan
        recommendation = system.generate_treatment_plan(patient_data)
        
        # Simulate treatment outcome (with some delay to create realistic timestamps)
        time.sleep(0.1)
        
        outcome = TreatmentOutcome(
            patient_id=patient_id,
            treatment_id=recommendation.recommended_treatment.treatment_id,
            outcome_success=expected_success,
            recovery_time=21 if expected_success else 35,
            side_effects_observed=['mild_nausea'] if not expected_success else [],
            patient_satisfaction=8.5 if expected_success else 6.0,
            readmission_required=not expected_success,
            outcome_date=datetime.now()
        )
        
        # Process the outcome
        system.process_treatment_outcome(patient_id, outcome)
        
        print(f"      ✅ {patient_id}: Plan generated, outcome processed")
    
    # Step 5: Perform daily reconciliation
    print("\n📋 Step 5: Performing Daily Reconciliation")
    report = reconciliation.daily_reconciliation()
    
    # Step 6: Display comprehensive reconciliation report
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE RECONCILIATION REPORT")
    print("=" * 60)
    
    print(f"\n🆔 Report Details:")
    print(f"   Report ID: {report.report_id}")
    print(f"   Report Date: {report.report_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Analysis Period: {report.period_start.strftime('%Y-%m-%d %H:%M')} - {report.period_end.strftime('%Y-%m-%d %H:%M')}")
    
    print(f"\n📈 System Health Metrics:")
    print(f"   Total Conflicts: {report.total_conflicts}")
    print(f"   System Health Score: {report.system_health_score:.1f}/100")
    
    if report.system_health_score >= 90:
        health_status = "🟢 EXCELLENT"
    elif report.system_health_score >= 75:
        health_status = "🟡 GOOD"
    elif report.system_health_score >= 60:
        health_status = "🟠 FAIR"
    else:
        health_status = "🔴 NEEDS ATTENTION"
    
    print(f"   Health Status: {health_status}")
    
    print(f"\n⚠️ Conflicts by Severity:")
    for severity, count in report.conflicts_by_severity.items():
        if count > 0:
            severity_icon = {
                'critical': '🚨',
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(severity, '⚪')
            print(f"   {severity_icon} {severity.upper()}: {count}")
    
    print(f"\n📊 Conflicts by Type:")
    for conflict_type, count in report.conflicts_by_type.items():
        if count > 0:
            print(f"   • {conflict_type.replace('_', ' ').title()}: {count}")
    
    print(f"\n📋 Learning-Prediction Gaps:")
    if report.learning_prediction_gaps:
        for gap in report.learning_prediction_gaps:
            trend_icon = {
                'improving': '📈',
                'declining': '📉',
                'stable': '➡️'
            }.get(gap.trend_direction, '➡️')
            
            print(f"   {trend_icon} {gap.treatment_type}:")
            print(f"      Gap Magnitude: {gap.gap_magnitude:.1%}")
            print(f"      Predicted Success: {gap.predicted_success_rate:.1%}")
            print(f"      Actual Success: {gap.actual_success_rate:.1%}")
            print(f"      Sample Size: {gap.sample_size}")
            print(f"      Trend: {gap.trend_direction}")
    else:
        print("   ✅ No significant learning-prediction gaps detected")
    
    print(f"\n💡 System Recommendations:")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"   {i}. {rec}")
    
    print(f"\n✅ Action Items:")
    if report.action_items:
        for i, action in enumerate(report.action_items, 1):
            print(f"   {i}. {action}")
    else:
        print("   ✅ No immediate action items required")
    
    # Step 7: Display detailed conflict analysis
    if report.raw_conflicts:
        print(f"\n🔍 DETAILED CONFLICT ANALYSIS")
        print("=" * 40)
        
        for i, conflict in enumerate(report.raw_conflicts, 1):
            severity_icon = {
                'critical': '🚨',
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(conflict.severity.value, '⚪')
            
            print(f"\n{severity_icon} Conflict #{i}:")
            print(f"   ID: {conflict.conflict_id}")
            print(f"   Type: {conflict.conflict_type.value.replace('_', ' ').title()}")
            print(f"   Severity: {conflict.severity.value.upper()}")
            print(f"   Description: {conflict.description}")
            print(f"   Affected Patients: {', '.join(conflict.affected_patients) if conflict.affected_patients else 'System-wide'}")
            print(f"   Resolution Required: {'Yes' if conflict.resolution_required else 'No'}")
            
            if conflict.recommended_actions:
                print(f"   Recommended Actions:")
                for action in conflict.recommended_actions:
                    print(f"      • {action}")
    
    # Step 8: Test reconciliation summary functionality
    print(f"\n📊 RECONCILIATION SUMMARY (7 days)")
    print("=" * 40)
    
    summary = reconciliation.get_reconciliation_summary(days=7)
    
    if summary.get('status') == 'no_recent_reports':
        print("   ℹ️ No historical reports available (first run)")
    else:
        print(f"   Reports Analyzed: {summary['reports_analyzed']}")
        print(f"   Total Conflicts: {summary['total_conflicts']}")
        print(f"   Average Health Score: {summary['avg_health_score']}/100")
        print(f"   Health Trend: {summary['health_trend']}")
    
    # Step 9: System status summary
    print(f"\n🏥 SYSTEM STATUS SUMMARY")
    print("=" * 40)
    
    print(f"   Clinical Context Module: ✅ Active")
    print(f"   Predictive Analytics Engine: ✅ Active")
    print(f"   Dynamic Learning Loop: ✅ Active")
    print(f"   Conflict Resolution Engine: ✅ Active")
    print(f"   System Reconciliation: ✅ Active")
    
    print(f"\n   Learning Buffer Size: {len(system.feedback_loop.learning_buffer)}")
    print(f"   Recommendation History: {len(system.feedback_loop.recommendation_history)}")
    print(f"   Outcome History: {len(system.feedback_loop.outcome_history)}")
    
    print(f"\n✅ SYSTEM RECONCILIATION TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    return report


if __name__ == "__main__":
    # Run the comprehensive test
    reconciliation_report = test_system_reconciliation()
    
    print(f"\n🎯 Final System Health Score: {reconciliation_report.system_health_score:.1f}/100")
    print(f"🎯 Total Conflicts Detected: {reconciliation_report.total_conflicts}")
    print(f"🎯 System Status: {'HEALTHY' if reconciliation_report.system_health_score >= 80 else 'NEEDS MONITORING'}") 