# =============================================================================
# 10. EXAMPLE USAGE AND TESTING
# =============================================================================

import asyncio
import json
import pandas as pd
from datetime import datetime
import logging

from main_orchestrator import IntelligenceLayer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_usage():
    """Example of using the Intelligence Layer"""
    
    # Initialize Intelligence Layer
    intelligence = IntelligenceLayer(
        db_url="postgresql://user:pass@localhost/abena_ihr",
        redis_url="redis://localhost:6379"
    )
    
    print("🚀 Starting Abena IHR Intelligence Layer Example")
    print("=" * 50)
    
    # 1. Record some integration events for testing
    print("\n📊 Recording Integration Events...")
    
    # Successful integration
    await intelligence.record_integration_event(
        source_system="Epic",
        endpoint="/api/patients",
        response_time=1.5,
        status_code=200,
        success=True,
        records_processed=150
    )
    
    # Failed integration
    await intelligence.record_integration_event(
        source_system="Epic",
        endpoint="/api/observations",
        response_time=45.2,
        status_code=500,
        success=False,
        error_message="Internal server error",
        records_processed=0
    )
    
    # Another successful integration
    await intelligence.record_integration_event(
        source_system="Cerner",
        endpoint="/api/medications",
        response_time=2.1,
        status_code=200,
        success=True,
        records_processed=75
    )
    
    print("✅ Integration events recorded")
    
    # 2. Simulate data quality analysis
    print("\n🔍 Performing Data Quality Analysis...")
    
    # Sample patient data with quality issues
    sample_data = pd.DataFrame({
        'mrn': ['MRN001', 'MRN002', 'MRN003', None, 'MRN005'],
        'first_name': ['John', 'Jane', '', 'Bob', 'Alice'],
        'last_name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson'],
        'email': ['john@email.com', 'invalid-email', 'jane@test.com', 'bob@mail.com', 'alice@health.org'],
        'phone': ['+1234567890', '555-1234', 'invalid-phone', '+1987654321', '555-9876'],
        'gender': ['male', 'female', 'other', 'unknown', 'MALE'],
        'age': [30, 25, 'invalid', 45, 35]
    })
    
    quality_result = await intelligence.analyze_data_quality(
        sample_data, "patient", "Epic"
    )
    
    print("📈 Data Quality Results:")
    print(f"   Overall Score: {quality_result['overall_score']:.2%}")
    print(f"   Completeness: {quality_result['dimension_scores'].get('completeness', 0):.2%}")
    print(f"   Accuracy: {quality_result['dimension_scores'].get('validity', 0):.2%}")
    print(f"   Consistency: {quality_result['dimension_scores'].get('consistency', 0):.2%}")
    print(f"   Issues Found: {len(quality_result['issues'])}")
    
    # 3. Get comprehensive dashboard data
    print("\n📊 Generating Dashboard Data...")
    dashboard = await intelligence.get_intelligence_dashboard()
    
    print("📋 Dashboard Summary:")
    print(f"   System Status: {dashboard['system_status']}")
    print(f"   Active Alerts: {sum(dashboard['active_alerts'].values())}")
    
    if dashboard['integration_monitoring']['summary']:
        summary = dashboard['integration_monitoring']['summary']
        print(f"   Total Requests: {summary['total_requests']}")
        print(f"   Success Rate: {summary['success_rate']:.2%}")
    
    # 4. Check system health
    print("\n💚 Checking System Health...")
    health = intelligence.get_system_health()
    print(f"   Health Status: {health.get('status', 'unknown')}")
    if 'health_score' in health:
        print(f"   Health Score: {health['health_score']}/100")
    
    # 5. Demonstrate anomaly detection
    print("\n🔍 Detecting Anomalies...")
    
    # Sample numeric data for anomaly detection
    numeric_data = pd.DataFrame({
        'heart_rate': [72, 75, 68, 120, 70, 180, 65, 78, 85, 90],
        'blood_pressure': [120, 118, 125, 200, 115, 180, 110, 122, 130, 140],
        'temperature': [98.6, 98.4, 98.8, 102.5, 98.2, 99.1, 97.8, 98.9, 99.5, 100.2]
    })
    
    anomalies = intelligence.data_quality_analyzer.detect_anomalies(
        numeric_data, ['heart_rate', 'blood_pressure', 'temperature']
    )
    
    print(f"   Anomaly Score: {anomalies['anomaly_score']:.2%}")
    print(f"   Anomalous Records: {anomalies['anomalous_records']}")
    
    if anomalies['anomalies']:
        print("   Sample Anomalies:")
        for i, anomaly in enumerate(anomalies['anomalies'][:3]):
            print(f"     Record {anomaly['index']}: Score {anomaly['score']:.3f}")
    
    print("\n✅ Example completed successfully!")
    print("\n📚 Next Steps:")
    print("   1. Start the API server: python api_server.py")
    print("   2. Access the dashboard at: http://localhost:8000/dashboard")
    print("   3. View Prometheus metrics at: http://localhost:8001/metrics")
    print("   4. Configure your notification channels in main_orchestrator.py")

def create_sample_data_files():
    """Create sample data files for testing"""
    
    # Sample patient data
    patient_data = pd.DataFrame({
        'mrn': ['MRN001', 'MRN002', 'MRN003', 'MRN004', 'MRN005'],
        'first_name': ['John', 'Jane', 'Mike', 'Sarah', 'David'],
        'last_name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson'],
        'email': ['john@email.com', 'jane@test.com', 'mike@mail.com', 'sarah@health.org', 'david@clinic.com'],
        'phone': ['+1234567890', '+1987654321', '+1555123456', '+1555987654', '+1555111222'],
        'gender': ['male', 'female', 'male', 'female', 'male'],
        'age': [30, 25, 45, 35, 28],
        'admission_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']
    })
    
    # Sample observation data
    observation_data = pd.DataFrame({
        'patient_id': ['MRN001', 'MRN002', 'MRN003', 'MRN004', 'MRN005'],
        'observation_type': ['heart_rate', 'blood_pressure', 'temperature', 'weight', 'height'],
        'value': [72, 120, 98.6, 70.5, 175],
        'unit': ['bpm', 'mmHg', 'F', 'kg', 'cm'],
        'timestamp': ['2024-01-15 10:00:00', '2024-01-16 11:00:00', '2024-01-17 12:00:00', 
                     '2024-01-18 13:00:00', '2024-01-19 14:00:00']
    })
    
    # Save to files
    patient_data.to_csv('sample_patients.csv', index=False)
    observation_data.to_csv('sample_observations.csv', index=False)
    
    print("📁 Sample data files created:")
    print("   - sample_patients.csv")
    print("   - sample_observations.csv")

if __name__ == "__main__":
    # Create sample data files
    create_sample_data_files()
    
    # Run the example
    asyncio.run(example_usage()) 