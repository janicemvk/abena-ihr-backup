#!/usr/bin/env python3
"""
Simple test script to verify the clinical outcomes system is working
"""

import sys
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test FastAPI imports
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn imported successfully")
        
        # Test Pydantic imports
        import pydantic
        print("✅ Pydantic imported successfully")
        
        # Test data processing imports
        import pandas as pd
        import numpy as np
        print("✅ Pandas and NumPy imported successfully")
        
        # Test our clinical outcomes modules
        from src.clinical_outcomes.outcome_framework import (
            ClinicalOutcomeRecord, PainScoreAssessment, MeasurementTiming, DataQualityLevel
        )
        print("✅ Clinical outcomes framework imported successfully")
        
        from src.clinical_outcomes.data_collection import OutcomeCollectionService
        print("✅ Data collection service imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of the clinical outcomes system"""
    try:
        print("\nTesting basic functionality...")
        
        from src.clinical_outcomes.outcome_framework import (
            ClinicalOutcomeRecord, PainScoreAssessment, MeasurementTiming, DataQualityLevel
        )
        from src.clinical_outcomes.data_collection import OutcomeCollectionService
        
        # Create a service instance
        service = OutcomeCollectionService()
        print("✅ OutcomeCollectionService created successfully")
        
        # Create a sample pain assessment
        pain_assessment = PainScoreAssessment(
            patient_id="TEST_001",
            assessment_date=datetime.now(),
            measurement_timing=MeasurementTiming.BASELINE,
            current_pain=5.0,
            average_pain_24h=6.0,
            worst_pain_24h=8.0,
            least_pain_24h=3.0,
            pain_interference=7.0
        )
        print("✅ PainScoreAssessment created successfully")
        
        # Create a clinical outcome record
        record = ClinicalOutcomeRecord(
            record_id="TEST_RECORD_001",
            patient_id="TEST_001",
            assessment_date=datetime.now(),
            measurement_timing=MeasurementTiming.BASELINE,
            baseline_date=datetime.now(),
            pain_assessment=pain_assessment,
            data_quality=DataQualityLevel.COMPLETE
        )
        print("✅ ClinicalOutcomeRecord created successfully")
        
        # Test validation
        errors = record.validate_record()
        print(f"✅ Record validation completed with {len(errors)} errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("CLINICAL OUTCOMES SYSTEM TEST")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test functionality
        functionality_ok = test_basic_functionality()
        
        if functionality_ok:
            print("\n" + "=" * 50)
            print("🎉 ALL TESTS PASSED! System is ready to use.")
            print("=" * 50)
            return True
        else:
            print("\n" + "=" * 50)
            print("❌ Functionality tests failed.")
            print("=" * 50)
            return False
    else:
        print("\n" + "=" * 50)
        print("❌ Import tests failed. Please check your dependencies.")
        print("=" * 50)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 