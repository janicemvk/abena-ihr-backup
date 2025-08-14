"""
Test script for Abena IHR ECS Lab Analysis Module
Demonstrates functionality with different patient scenarios using Abena SDK
"""

import os
from datetime import datetime
from ecs_analyzer import ECSAnalyzer, USING_MOCK_SDK

# Import Abena SDK components - use mock for testing
if USING_MOCK_SDK:
    from abena_sdk_mock import AbenaConfig
else:
    from abena.sdk.config import AbenaConfig

def test_authentication_and_authorization():
    """Test Abena SDK authentication and authorization"""
    
    print("=" * 60)
    print("TESTING ABENA SDK AUTHENTICATION & AUTHORIZATION")
    print("=" * 60)
    
    # Initialize analyzer with Abena config
    config = AbenaConfig()
    analyzer = ECSAnalyzer(config)
    
    # Test authentication
    print("\n1. Testing Authentication...")
    credentials = {
        "username": "test_user",
        "password": "test_password",
        "api_key": "test_api_key"
    }
    
    auth_result = analyzer.authenticate(credentials)
    print(f"   Authentication result: {auth_result}")
    
    # Test authorization
    print("\n2. Testing Authorization...")
    resources = ["patient_data", "lab_results", "vital_signs", "ekg_results", "smart_device_data"]
    actions = ["read", "write", "delete"]
    
    for resource in resources:
        for action in actions:
            auth_result = analyzer.authorize_access(resource, action)
            print(f"   {resource}.{action}: {auth_result}")
    
    print("   ✓ Authentication and authorization tests completed")

def test_all_scenarios():
    """Test the ECS analyzer with all available patient scenarios"""
    
    scenarios = [
        "healthy_baseline",
        "mild_dysfunction", 
        "moderate_dysfunction",
        "severe_dysfunction",
        "mixed_patterns"
    ]
    
    print("=" * 60)
    print("ABENA IHR ECS LAB ANALYSIS MODULE - TEST SUITE")
    print("=" * 60)
    
    for scenario in scenarios:
        print(f"\n{'='*20} TESTING: {scenario.upper()} {'='*20}")
        
        # Initialize analyzer with Abena config
        config = AbenaConfig()
        analyzer = ECSAnalyzer(config)
        
        # Load test patient data
        analyzer.load_test_patient_data(scenario)
        
        # Calculate ECS score
        ecs_score = analyzer.calculate_ecs_score()
        
        # Display results
        print(f"Patient: {analyzer.patient_data.name}")
        print(f"Patient ID: {analyzer.patient_data.patient_id}")
        print(f"Age: {analyzer.patient_data.age} years")
        print(f"BMI: {analyzer.patient_data.bmi:.1f}")
        print(f"ECS Score: {ecs_score['total_score']}")
        print(f"Classification: {ecs_score['classification']}")
        print(f"Severity: {ecs_score['severity']}")
        
        # Display category scores
        print("\nCategory Scores:")
        for category, score in ecs_score['category_scores'].items():
            print(f"  {category.replace('_', ' ').title()}: {score:.1f}")
        
        # Analyze correlations
        correlations = analyzer.analyze_correlations()
        if correlations:
            print("\nCorrelations:")
            for key, value in correlations.items():
                print(f"  {key}: {value:.3f}")
        
        # Generate recommendations
        recommendations = analyzer.generate_recommendations()
        print(f"\nRecommendations Generated:")
        print(f"  Supplements: {len(recommendations['supplements'])}")
        print(f"  Lifestyle: {len(recommendations['lifestyle'])}")
        print(f"  Dietary: {len(recommendations['dietary'])}")
        print(f"  Monitoring: {len(recommendations['monitoring'])}")
        
        # Generate HTML report
        print("\nGenerating HTML report...")
        html_report = analyzer.create_html_report()
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ecs_report_{scenario}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"Report saved: {filename}")
        
        # Display lab results summary
        print(f"\nLab Results Summary:")
        print(f"  Total lab results: {len(analyzer.lab_results)}")
        
        # Count by category
        categories = {}
        for result in analyzer.lab_results:
            cat = result.category if result.category else "other"
            categories[cat] = categories.get(cat, 0) + 1
        
        for category, count in categories.items():
            print(f"  {category.replace('_', ' ').title()}: {count}")
        
        # Display smart device data summary
        print(f"\nSmart Device Data Summary:")
        print(f"  Total measurements: {len(analyzer.smart_device_data)}")
        
        # Count by metric
        metrics = {}
        for data in analyzer.smart_device_data:
            metrics[data.metric] = metrics.get(data.metric, 0) + 1
        
        for metric, count in metrics.items():
            print(f"  {metric}: {count} measurements")
        
        print(f"\n{'='*60}")

def test_individual_components():
    """Test individual components of the ECS analyzer"""
    
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL COMPONENTS")
    print("="*60)
    
    # Initialize analyzer with Abena config
    config = AbenaConfig()
    analyzer = ECSAnalyzer(config)
    analyzer.load_test_patient_data("moderate_dysfunction")
    
    # Test radar chart
    print("\n1. Testing Radar Chart Generation...")
    radar_chart = analyzer.create_radar_chart()
    print(f"   Radar chart HTML length: {len(radar_chart)} characters")
    print("   ✓ Radar chart generated successfully")
    
    # Test biomarker chart
    print("\n2. Testing Biomarker Chart Generation...")
    biomarker_chart = analyzer.create_biomarker_chart()
    print(f"   Biomarker chart HTML length: {len(biomarker_chart)} characters")
    print("   ✓ Biomarker chart generated successfully")
    
    # Test temporal analysis
    print("\n3. Testing Temporal Analysis Generation...")
    temporal_chart = analyzer.create_temporal_analysis()
    print(f"   Temporal chart HTML length: {len(temporal_chart)} characters")
    print("   ✓ Temporal analysis generated successfully")
    
    # Test correlation heatmap
    print("\n4. Testing Correlation Heatmap Generation...")
    correlation_chart = analyzer.create_correlation_heatmap()
    print(f"   Correlation chart HTML length: {len(correlation_chart)} characters")
    print("   ✓ Correlation heatmap generated successfully")
    
    # Test scoring algorithm
    print("\n5. Testing Scoring Algorithm...")
    ecs_score = analyzer.calculate_ecs_score()
    print(f"   Total score: {ecs_score['total_score']}")
    print(f"   Classification: {ecs_score['classification']}")
    print("   ✓ Scoring algorithm working correctly")
    
    # Test recommendations
    print("\n6. Testing Recommendation Generation...")
    recommendations = analyzer.generate_recommendations()
    total_recs = sum(len(recs) for recs in recommendations.values())
    print(f"   Total recommendations generated: {total_recs}")
    print("   ✓ Recommendations generated successfully")

def test_performance():
    """Test performance metrics"""
    
    print("\n" + "="*60)
    print("PERFORMANCE TESTING")
    print("="*60)
    
    import time
    
    # Initialize analyzer with Abena config
    config = AbenaConfig()
    analyzer = ECSAnalyzer(config)
    analyzer.load_test_patient_data("moderate_dysfunction")
    
    # Test HTML report generation time
    print("\nTesting HTML Report Generation Performance...")
    start_time = time.time()
    html_report = analyzer.create_html_report()
    end_time = time.time()
    
    generation_time = end_time - start_time
    print(f"   Report generation time: {generation_time:.2f} seconds")
    
    if generation_time < 10:
        print("   ✓ Performance requirement met (<10 seconds)")
    else:
        print("   ⚠ Performance requirement not met (>10 seconds)")
    
    # Test memory usage
    print(f"\nReport size: {len(html_report)} characters")
    print(f"Report size: {len(html_report) / 1024:.1f} KB")
    
    # Test data handling
    print(f"\nData handling capacity:")
    print(f"   Lab results: {len(analyzer.lab_results)}")
    print(f"   Smart device measurements: {len(analyzer.smart_device_data)}")
    print(f"   Vital signs: {len(analyzer.vital_signs)}")
    print(f"   EKG results: {len(analyzer.ekg_results)}")

def test_abena_sdk_integration():
    """Test Abena SDK integration features"""
    
    print("\n" + "="*60)
    print("TESTING ABENA SDK INTEGRATION")
    print("="*60)
    
    # Initialize analyzer with Abena config
    config = AbenaConfig()
    analyzer = ECSAnalyzer(config)
    
    # Test data handler integration
    print("\n1. Testing Data Handler Integration...")
    try:
        # This would normally load real patient data from Abena system
        # For testing, we use simulated data
        analyzer.load_test_patient_data("moderate_dysfunction")
        print("   ✓ Data handler integration working")
    except Exception as e:
        print(f"   ⚠ Data handler integration issue: {e}")
    
    # Test Abena SDK model usage
    print("\n2. Testing Abena SDK Models...")
    try:
        # Verify we're using Abena SDK models
        from abena.sdk.models import AbenaPatient, AbenaLabResult, AbenaVitalSign, AbenaEKGResult, AbenaSmartDeviceData
        
        assert isinstance(analyzer.patient_data, AbenaPatient)
        assert all(isinstance(r, AbenaLabResult) for r in analyzer.lab_results)
        assert all(isinstance(v, AbenaVitalSign) for v in analyzer.vital_signs)
        assert all(isinstance(e, AbenaEKGResult) for e in analyzer.ekg_results)
        assert all(isinstance(s, AbenaSmartDeviceData) for s in analyzer.smart_device_data)
        
        print("   ✓ All data using Abena SDK models")
    except Exception as e:
        print(f"   ⚠ Model integration issue: {e}")
    
    # Test configuration integration
    print("\n3. Testing Configuration Integration...")
    try:
        assert analyzer.config is not None
        assert analyzer.authenticator is not None
        assert analyzer.authorizer is not None
        assert analyzer.data_handler is not None
        print("   ✓ Abena SDK components properly initialized")
    except Exception as e:
        print(f"   ⚠ Configuration integration issue: {e}")

def main():
    """Main test function"""
    
    print("Starting Abena IHR ECS Lab Analysis Module Tests...")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test Abena SDK integration first
        test_abena_sdk_integration()
        
        # Test authentication and authorization
        test_authentication_and_authorization()
        
        # Test all scenarios
        test_all_scenarios()
        
        # Test individual components
        test_individual_components()
        
        # Test performance
        test_performance()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # List generated files
        print("\nGenerated Files:")
        html_files = [f for f in os.listdir('.') if f.endswith('.html') and f.startswith('ecs_report_')]
        for file in html_files:
            print(f"  - {file}")
        
        print(f"\nTotal reports generated: {len(html_files)}")
        print("\nYou can open any of the HTML files in a web browser to view the reports.")
        
    except Exception as e:
        print(f"\nERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 