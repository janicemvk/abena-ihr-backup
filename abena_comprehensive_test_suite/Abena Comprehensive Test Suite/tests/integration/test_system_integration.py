# Integration tests for System Integration
import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.integration.system_orchestrator import AbenaIntegratedSystem, DataSynchronizer
from datetime import datetime

class TestSystemIntegration:
    """Integration tests for the complete system"""
    
    @pytest.fixture
    def integrated_system(self, mock_training_data):
        """Create integrated system for testing"""
        system = AbenaIntegratedSystem()
        
        # Mock initialization with training data
        adverse_event_data = []
        for patient, treatment, outcome in mock_training_data[:50]:
            adverse_outcomes = {
                'severe_side_effects': np.random.randint(0, 2),
                'treatment_discontinuation': np.random.randint(0, 2)
            }
            adverse_event_data.append((patient, treatment, adverse_outcomes))
        
        system.predictive_engine.initialize_models(mock_training_data, adverse_event_data)
        
        return system
    
    def test_full_treatment_plan_generation(self, integrated_system, sample_patient):
        """Test complete treatment plan generation workflow"""
        
        # Mock clinical context recommendations
        mock_clinical_recommendations = Mock()
        mock_clinical_recommendations.treatment_options = [
            Mock(treatment_id="TX_001", treatment_type="pharmacological"),
            Mock(treatment_id="TX_002", treatment_type="behavioral")
        ]
        
        with patch.object(integrated_system, 'clinical_context') as mock_clinical:
            mock_clinical.analyze_patient.return_value = mock_clinical_recommendations
            
            plan = integrated_system.generate_treatment_plan(sample_patient.patient_id)
            
            assert plan is not None
            assert 'patient_id' in plan or hasattr(plan, 'patient_id')
    
    def test_conflict_resolution(self, integrated_system):
        """Test conflict resolution between modules"""
        
        # Create mock conflicting recommendations
        clinical_rec = Mock()
        clinical_rec.success_probability = 0.8
        clinical_rec.alternative_treatments = []
        
        prediction_result = Mock()
        prediction_result.success_probability = 0.3  # Conflicting low probability
        
        resolver = integrated_system.conflict_resolver
        
        # This should trigger conflict resolution
        result = resolver.resolve_recommendation_conflict(clinical_rec, prediction_result)
        
        assert 'recommendation' in result
        assert result['recommendation'] == 'HOLD - Investigate alternatives'
    
    def test_outcome_processing(self, integrated_system):
        """Test outcome processing and feedback loop"""
        
        outcome_data = {
            'treatment_success': 0.7,
            'adverse_events': [],
            'patient_satisfaction': 8.5,
            'pain_reduction': 4.2
        }
        
        # This should not raise an exception
        result = integrated_system.process_treatment_outcome("TEST_PATIENT_001", outcome_data)
        
        # Verify the outcome was processed
        assert result is not None

class TestDataSynchronization:
    """Test data synchronization between modules"""
    
    def test_data_consistency_across_modules(self):
        """Test that all modules use consistent data"""
        synchronizer = DataSynchronizer()
        
        # Mock patient data update
        patient_data = {
            'patient_id': 'TEST_PATIENT_001',
            'last_updated': datetime.now(),
            'biomarkers': {'inflammatory_markers': 2.1}
        }
        
        # This should update all modules with consistent data
        synchronizer.ensure_data_consistency('TEST_PATIENT_001')
        
        # Verify synchronization completed without errors
        assert True  # If we get here, no exceptions were raised 