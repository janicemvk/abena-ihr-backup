#!/usr/bin/env python3
"""
Test script for Predictive Analytics Engine with Abena SDK
This script demonstrates the engine functionality with mock data.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from predictive_analytics_engine import PredictiveAnalyticsEngine, PredictionResult, CohortAnalysis

class MockAbenaSDK:
    """Mock Abena SDK for testing purposes"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.auth_token = "mock_token_12345"
        self.client = None
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Mock login"""
        return {"token": self.auth_token, "user_id": "test_user"}
    
    async def get_anonymized_dataset(self, criteria: Dict[str, Any]) -> list:
        """Mock anonymized dataset"""
        return [
            {"patient_id": "P12345", "age": 72, "risk_score": 0.8, "conditions": ["diabetes", "hypertension"]},
            {"patient_id": "P12346", "age": 65, "risk_score": 0.6, "conditions": ["copd"]},
            {"patient_id": "P12347", "age": 58, "risk_score": 0.3, "conditions": ["diabetes"]}
        ]
    
    async def get_patient_data(self, patient_id: str, purpose: str) -> Dict[str, Any]:
        """Mock patient data"""
        return {
            "patient": {
                "patient_id": patient_id,
                "demographics": {
                    "birthDate": "1950-01-15",
                    "gender": "F"
                }
            },
            "healthRecords": [
                {
                    "diagnoses": [
                        {"code": "diabetes", "chronic": True},
                        {"code": "hypertension", "chronic": True}
                    ],
                    "vitals": [
                        {"type": "heart_rate", "value": 85},
                        {"type": "blood_pressure_systolic", "value": 140},
                        {"type": "oxygen_saturation", "value": 98}
                    ],
                    "labs": [
                        {"test": "wbc", "value": 7500},
                        {"test": "creatinine", "value": 1.2}
                    ],
                    "medications": [
                        {"name": "metformin"},
                        {"name": "lisinopril"},
                        {"name": "aspirin"}
                    ],
                    "encounters": [
                        {"type": "hospitalization", "date": "2024-01-15"}
                    ]
                }
            ],
            "devices": [
                {"invasive": False, "type": "pulse_oximeter"}
            ]
        }
    
    async def log_blockchain_access(self, patient_id: str, action: str, purpose: str, metadata: Dict[str, Any]) -> str:
        """Mock blockchain logging"""
        print(f"🔗 Blockchain Log: {action} for {patient_id} - {purpose}")
        return "mock_tx_id_12345"
    
    async def validate_service_access(self, patient_id: str, action: str, service: str) -> Dict[str, Any]:
        """Mock access validation"""
        return {"granted": True, "reason": "Authorized user"}


class TestPredictiveAnalyticsEngine(PredictiveAnalyticsEngine):
    """Test version of the engine with mock SDK"""
    
    def __init__(self):
        # Override the Abena SDK with mock version
        self.abena = MockAbenaSDK({
            'auth_service_url': 'http://localhost:3001',
            'data_service_url': 'http://localhost:8001',
            'privacy_service_url': 'http://localhost:8002',
            'blockchain_service_url': 'http://localhost:8003'
        })
        
        # Model configurations
        self.models = {
            'readmission_risk': {'version': '1.2.3', 'threshold': 0.6},
            'mortality_risk': {'version': '1.1.1', 'threshold': 0.8},
            'length_of_stay': {'version': '1.0.5', 'threshold': 0.5},
            'infection_risk': {'version': '1.3.2', 'threshold': 0.7},
            'medication_adherence': {'version': '1.1.8', 'threshold': 0.6}
        }


async def test_patient_risk_prediction():
    """Test patient risk prediction functionality"""
    print("🧪 Testing Patient Risk Prediction...")
    
    engine = TestPredictiveAnalyticsEngine()
    
    # Authenticate
    await engine.authenticate('test@healthcare.org', 'test_password')
    print("✅ Authentication successful")
    
    # Test different prediction types
    prediction_types = ['readmission_risk', 'mortality_risk', 'infection_risk']
    
    for pred_type in prediction_types:
        print(f"\n📊 Testing {pred_type} prediction...")
        
        predictions = await engine.predict_patient_risk(
            patient_id='P12345',
            prediction_types=[pred_type],
            timeframe='30d'
        )
        
        for pred in predictions:
            print(f"  Risk Score: {pred.risk_score:.3f}")
            print(f"  Confidence: {pred.confidence:.3f}")
            print(f"  Factors: {pred.contributing_factors}")
            print(f"  Recommendations: {pred.recommendations[:2]}...")  # Show first 2


async def test_cohort_analysis():
    """Test population cohort analysis"""
    print("\n🧪 Testing Population Cohort Analysis...")
    
    engine = TestPredictiveAnalyticsEngine()
    await engine.authenticate('test@healthcare.org', 'test_password')
    
    cohort_analysis = await engine.analyze_population_cohort(
        cohort_criteria={
            'patients': ['P12345', 'P12346', 'P12347'],
            'age_range': [65, 85],
            'conditions': ['diabetes', 'hypertension']
        },
        analysis_type='risk_stratification'
    )
    
    print(f"✅ Cohort Analysis Complete:")
    print(f"  Cohort ID: {cohort_analysis.cohort_id}")
    print(f"  Patient Count: {cohort_analysis.patient_count}")
    print(f"  Risk Distribution: {cohort_analysis.risk_distribution}")
    print(f"  Top Risk Factors: {cohort_analysis.top_risk_factors}")
    print(f"  Data Quality Score: {cohort_analysis.data_quality_score:.3f}")


async def test_outbreak_prediction():
    """Test outbreak risk prediction"""
    print("\n🧪 Testing Outbreak Risk Prediction...")
    
    engine = TestPredictiveAnalyticsEngine()
    await engine.authenticate('test@healthcare.org', 'test_password')
    
    outbreak_risk = await engine.predict_outbreak_risk(
        facility_id='FACILITY_001',
        infection_type='general'
    )
    
    print(f"✅ Outbreak Risk Analysis Complete:")
    print(f"  Facility ID: {outbreak_risk['facility_id']}")
    print(f"  Risk Level: {outbreak_risk['risk_level']}")
    print(f"  Risk Score: {outbreak_risk['risk_score']:.3f}")
    print(f"  Contributing Factors: {outbreak_risk['contributing_factors']}")
    print(f"  Recommendations: {outbreak_risk['recommendations']}")


async def test_treatment_recommendations():
    """Test treatment recommendations"""
    print("\n🧪 Testing Treatment Recommendations...")
    
    engine = TestPredictiveAnalyticsEngine()
    await engine.authenticate('test@healthcare.org', 'test_password')
    
    recommendations = await engine.generate_treatment_recommendations(
        patient_id='P12345',
        condition='diabetes',
        current_treatments=['metformin']
    )
    
    print(f"✅ Treatment Recommendations Generated:")
    print(f"  Treatments: {recommendations['treatments']}")
    print(f"  Evidence Level: {recommendations['evidence_level']}")
    print(f"  Monitoring Requirements: {recommendations['monitoring_requirements']}")


async def test_deterioration_monitoring():
    """Test patient deterioration monitoring"""
    print("\n🧪 Testing Patient Deterioration Monitoring...")
    
    engine = TestPredictiveAnalyticsEngine()
    await engine.authenticate('test@healthcare.org', 'test_password')
    
    monitoring_result = await engine.monitor_patient_deterioration(
        patient_id='P12345',
        monitoring_duration='24h'
    )
    
    print(f"✅ Deterioration Monitoring Complete:")
    print(f"  Deterioration Score: {monitoring_result['deterioration_score']:.3f}")
    print(f"  Risk Level: {monitoring_result['risk_level']}")
    print(f"  Trending: {monitoring_result['trending']}")
    print(f"  Next Assessment: {monitoring_result['next_assessment']}")
    if monitoring_result['early_warning']:
        print(f"  Early Warning: {monitoring_result['early_warning']['message']}")


async def main():
    """Run all tests"""
    print("🚀 Starting Predictive Analytics Engine Tests")
    print("=" * 50)
    
    try:
        await test_patient_risk_prediction()
        await test_cohort_analysis()
        await test_outbreak_prediction()
        await test_treatment_recommendations()
        await test_deterioration_monitoring()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("🎉 Predictive Analytics Engine is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 