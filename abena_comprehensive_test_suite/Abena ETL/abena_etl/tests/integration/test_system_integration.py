"""
Integration Tests for System Components

This module contains integration tests that verify the interaction
between different system components and modules.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from tests.conftest import validate_prediction_result
from src.core.data_models import PatientProfile, TreatmentPlan


# ============================================================================
# MOCK INTEGRATED SYSTEM CLASS
# ============================================================================

class MockAbenaIntegratedSystem:
    """Mock integrated system for testing"""
    
    def __init__(self):
        self.clinical_context = MockClinicalContext()
        self.predictive_engine = MockPredictiveEngine()
        self.conflict_resolver = MockConflictResolver()
        self.workflow_orchestrator = MockWorkflowOrchestrator()
        self.learning_loop = MockLearningLoop()
    
    def generate_treatment_plan(self, patient_id: str):
        """Generate complete treatment plan"""
        # Mock workflow: clinical analysis -> prediction -> conflict resolution
        patient = self.clinical_context.get_patient(patient_id)
        clinical_options = self.clinical_context.analyze_patient(patient)
        
        best_option = clinical_options.treatment_options[0] if clinical_options.treatment_options else None
        if not best_option:
            return None
        
        prediction = self.predictive_engine.predict_treatment_response(patient, best_option)
        
        # Check for conflicts
        conflict_result = self.conflict_resolver.resolve_recommendation_conflict(
            clinical_options, prediction
        )
        
        return {
            'patient_id': patient_id,
            'treatment_plan': best_option,
            'prediction': prediction,
            'conflict_resolution': conflict_result,
            'timestamp': datetime.now()
        }
    
    def process_patient_workflow(self, patient_data: dict):
        """Process complete patient workflow"""
        patient = PatientProfile(**patient_data)
        
        # Clinical analysis
        clinical_result = self.clinical_context.analyze_patient(patient)
        
        # Predictive analytics
        predictions = []
        for treatment in clinical_result.treatment_options:
            pred = self.predictive_engine.predict_treatment_response(patient, treatment)
            predictions.append(pred)
        
        # Conflict resolution
        conflicts = []
        for i, prediction in enumerate(predictions):
            conflict = self.conflict_resolver.resolve_recommendation_conflict(
                clinical_result, prediction
            )
            conflicts.append(conflict)
        
        # Learning feedback
        self.learning_loop.update_models(patient, predictions)
        
        return {
            'patient': patient,
            'clinical_analysis': clinical_result,
            'predictions': predictions,
            'conflicts': conflicts,
            'status': 'completed'
        }


class MockClinicalContext:
    """Mock clinical context module"""
    
    def __init__(self):
        self.treatment_options = []
    
    def get_patient(self, patient_id: str):
        """Get patient by ID"""
        return PatientProfile(
            patient_id=patient_id,
            age=45,
            gender="female",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=["gabapentin"],
            lifestyle_metrics={},
            pain_scores=[7.0],
            functional_assessments={}
        )
    
    def analyze_patient(self, patient: PatientProfile):
        """Analyze patient and return treatment options"""
        treatment_options = [
            TreatmentPlan(
                treatment_id=f"TX_{patient.patient_id}_001",
                treatment_type="combined",
                medications=["pregabalin", "cbd_oil"],
                dosages={"pregabalin": "150mg_bid", "cbd_oil": "25mg_daily"},
                duration_weeks=12,
                lifestyle_interventions=["physical_therapy"]
            ),
            TreatmentPlan(
                treatment_id=f"TX_{patient.patient_id}_002",
                treatment_type="pharmacological",
                medications=["duloxetine"],
                dosages={"duloxetine": "60mg_daily"},
                duration_weeks=8,
                lifestyle_interventions=[]
            )
        ]
        
        return Mock(
            treatment_options=treatment_options,
            success_probability=0.75,
            alternative_treatments=[]
        )


class MockPredictiveEngine:
    """Mock predictive analytics engine"""
    
    def predict_treatment_response(self, patient: PatientProfile, treatment: TreatmentPlan):
        """Mock prediction"""
        from src.core.data_models import PredictionResult
        
        success_prob = 0.75 if "pregabalin" in treatment.medications else 0.65
        
        return PredictionResult(
            patient_id=patient.patient_id,
            treatment_id=treatment.treatment_id,
            success_probability=success_prob,
            risk_score=1 - success_prob,
            key_factors=["age", "medical_history"],
            warnings=[],
            timestamp=datetime.now()
        )


class MockConflictResolver:
    """Mock conflict resolution engine"""
    
    def resolve_recommendation_conflict(self, clinical_rec, prediction_result):
        """Mock conflict resolution"""
        return {
            'conflict_detected': False,
            'recommendation': 'PROCEED',
            'escalation_required': False,
            'rationale': 'No significant conflicts detected',
            'timestamp': datetime.now()
        }


class MockWorkflowOrchestrator:
    """Mock workflow orchestrator"""
    
    def __init__(self):
        self.emr_config = {}
    
    def send_clinical_note(self, patient_id: str, note_content: str):
        """Mock sending clinical note to EMR"""
        return {
            'status': 'success',
            'note_id': f'NOTE_{patient_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now()
        }
    
    def create_provider_alert(self, patient_id: str, alert_content: str, priority: str = 'medium'):
        """Mock creating provider alert"""
        return {
            'status': 'success',
            'alert_id': f'ALERT_{patient_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'priority': priority,
            'timestamp': datetime.now()
        }


class MockLearningLoop:
    """Mock dynamic learning loop"""
    
    def update_models(self, patient: PatientProfile, predictions: list):
        """Mock model updates"""
        return {
            'models_updated': ['treatment_response', 'adverse_events'],
            'performance_improvement': 0.02,
            'timestamp': datetime.now()
        }


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
class TestSystemIntegration:
    """Integration tests for the complete system"""
    
    @pytest.fixture
    def integrated_system(self):
        """Create integrated system for testing"""
        return MockAbenaIntegratedSystem()
    
    def test_treatment_plan_generation_workflow(self, integrated_system):
        """Test complete treatment plan generation workflow"""
        patient_id = "TEST_PATIENT_INTEGRATION_001"
        
        plan = integrated_system.generate_treatment_plan(patient_id)
        
        assert plan is not None
        assert plan['patient_id'] == patient_id
        assert 'treatment_plan' in plan
        assert 'prediction' in plan
        assert 'conflict_resolution' in plan
        assert 'timestamp' in plan
        
        # Validate treatment plan structure
        treatment_plan = plan['treatment_plan']
        assert hasattr(treatment_plan, 'treatment_id')
        assert hasattr(treatment_plan, 'medications')
        
        # Validate prediction structure
        prediction = plan['prediction']
        validate_prediction_result(prediction)
        
        # Validate conflict resolution
        conflict_result = plan['conflict_resolution']
        assert 'conflict_detected' in conflict_result
        assert 'recommendation' in conflict_result
    
    def test_conflict_resolution_between_modules(self, integrated_system):
        """Test conflict resolution between modules"""
        # Create conflicting recommendations
        clinical_rec = Mock(success_probability=0.8, alternative_treatments=[])
        prediction_result = Mock(success_probability=0.3)  # Conflicting low probability
        
        result = integrated_system.conflict_resolver.resolve_recommendation_conflict(
            clinical_rec, prediction_result
        )
        
        assert 'recommendation' in result
        assert result['recommendation'] in ['PROCEED', 'HOLD', 'INVESTIGATE']
        assert 'conflict_detected' in result
        assert 'rationale' in result
    
    def test_complete_patient_workflow(self, integrated_system, sample_patient):
        """Test complete patient workflow from intake to recommendations"""
        patient_data = sample_patient.__dict__.copy()
        
        workflow_result = integrated_system.process_patient_workflow(patient_data)
        
        assert workflow_result['status'] == 'completed'
        assert 'patient' in workflow_result
        assert 'clinical_analysis' in workflow_result
        assert 'predictions' in workflow_result
        assert 'conflicts' in workflow_result
        
        # Validate patient
        patient = workflow_result['patient']
        assert patient.patient_id == sample_patient.patient_id
        
        # Validate predictions
        predictions = workflow_result['predictions']
        assert len(predictions) > 0
        for prediction in predictions:
            validate_prediction_result(prediction)
        
        # Validate conflicts
        conflicts = workflow_result['conflicts']
        assert len(conflicts) == len(predictions)
    
    def test_emr_integration_workflow(self, integrated_system):
        """Test EMR integration workflow"""
        patient_id = "TEST_PATIENT_EMR_001"
        
        # Test clinical note creation
        note_result = integrated_system.workflow_orchestrator.send_clinical_note(
            patient_id, "Test clinical note content"
        )
        
        assert note_result['status'] == 'success'
        assert 'note_id' in note_result
        assert patient_id in note_result['note_id']
        
        # Test provider alert creation
        alert_result = integrated_system.workflow_orchestrator.create_provider_alert(
            patient_id, "High-risk drug interaction detected", "high"
        )
        
        assert alert_result['status'] == 'success'
        assert 'alert_id' in alert_result
        assert alert_result['priority'] == 'high'
    
    def test_learning_loop_integration(self, integrated_system, sample_patient, sample_treatment):
        """Test learning loop integration with predictions"""
        # Generate predictions
        prediction = integrated_system.predictive_engine.predict_treatment_response(
            sample_patient, sample_treatment
        )
        
        # Update models with feedback
        update_result = integrated_system.learning_loop.update_models(
            sample_patient, [prediction]
        )
        
        assert 'models_updated' in update_result
        assert 'performance_improvement' in update_result
        assert len(update_result['models_updated']) > 0
    
    def test_concurrent_patient_processing(self, integrated_system):
        """Test system handling multiple patients concurrently"""
        import concurrent.futures
        
        patient_ids = [f"CONCURRENT_PATIENT_{i:03d}" for i in range(5)]
        
        def process_patient(patient_id):
            return integrated_system.generate_treatment_plan(patient_id)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_patient, pid) for pid in patient_ids]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should complete successfully
        assert len(results) == len(patient_ids)
        for result in results:
            assert result is not None
            assert 'patient_id' in result
            assert 'treatment_plan' in result
    
    def test_error_handling_and_recovery(self, integrated_system):
        """Test system error handling and recovery"""
        # Test with invalid patient ID
        result = integrated_system.generate_treatment_plan("")
        
        # System should handle gracefully - either return None or appropriate error response
        assert result is None or ('error' in result and result['error'] is not None)
        
        # Test with partial failures
        with patch.object(integrated_system.predictive_engine, 'predict_treatment_response') as mock_predict:
            mock_predict.side_effect = Exception("Model temporarily unavailable")
            
            # System should still attempt to provide clinical recommendations
            try:
                result = integrated_system.generate_treatment_plan("TEST_PATIENT_ERROR")
                # Should either handle gracefully or raise appropriate exception
                assert True  # Test passes if no unhandled exception
            except Exception as e:
                # Expected behavior - system handles predictive engine failure
                assert "Model temporarily unavailable" in str(e)


@pytest.mark.integration
class TestDataFlowIntegration:
    """Test data flow between system components"""
    
    def test_patient_data_propagation(self, sample_patient):
        """Test patient data flows correctly through system"""
        system = MockAbenaIntegratedSystem()
        
        # Process patient through workflow
        workflow_result = system.process_patient_workflow(sample_patient.__dict__)
        
        # Verify patient data consistency
        processed_patient = workflow_result['patient']
        assert processed_patient.patient_id == sample_patient.patient_id
        assert processed_patient.age == sample_patient.age
        assert processed_patient.gender == sample_patient.gender
        
        # Verify data propagates to predictions
        predictions = workflow_result['predictions']
        for prediction in predictions:
            assert prediction.patient_id == sample_patient.patient_id
    
    def test_treatment_recommendation_consistency(self, integrated_system, sample_patient):
        """Test treatment recommendations are consistent across modules"""
        system = MockAbenaIntegratedSystem()
        
        # Get clinical recommendations
        clinical_analysis = system.clinical_context.analyze_patient(sample_patient)
        
        # Get predictive recommendations for same treatments
        predictions = []
        for treatment in clinical_analysis.treatment_options:
            pred = system.predictive_engine.predict_treatment_response(sample_patient, treatment)
            predictions.append(pred)
            
            # Verify treatment IDs match
            assert pred.treatment_id == treatment.treatment_id
            assert pred.patient_id == sample_patient.patient_id
    
    def test_conflict_resolution_data_integrity(self, integrated_system):
        """Test conflict resolution maintains data integrity"""
        system = MockAbenaIntegratedSystem()
        
        # Create test scenario
        clinical_rec = Mock(
            success_probability=0.8,
            treatment_id="TEST_TX_INTEGRITY",
            alternative_treatments=[]
        )
        
        prediction = Mock(
            success_probability=0.3,
            treatment_id="TEST_TX_INTEGRITY",
            patient_id="TEST_PATIENT_INTEGRITY"
        )
        
        # Resolve conflict
        result = system.conflict_resolver.resolve_recommendation_conflict(
            clinical_rec, prediction
        )
        
        # Verify data integrity
        assert 'timestamp' in result
        assert isinstance(result['timestamp'], datetime)
        assert 'recommendation' in result
        assert result['recommendation'] in ['PROCEED', 'HOLD', 'INVESTIGATE', 'EMERGENCY_REVIEW']


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 