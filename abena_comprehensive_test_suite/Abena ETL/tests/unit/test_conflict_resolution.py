"""
Unit Tests for Conflict Resolution Engine

This module contains unit tests for the conflict resolution system
that manages competing clinical recommendations and predictions.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult


# ============================================================================
# MOCK CONFLICT RESOLUTION CLASSES
# ============================================================================

class MockConflictResolution:
    """Mock conflict resolution engine for testing"""
    
    def __init__(self, threshold=0.3):
        self.threshold = threshold
        self.safety_keywords = [
            'contraindicated', 'dangerous', 'high risk', 'avoid',
            'emergency', 'urgent', 'severe interaction', 'toxicity'
        ]
        self.escalation_rules = {
            'safety_concern': 'EMERGENCY_REVIEW',
            'high_disagreement': 'CLINICAL_REVIEW',
            'moderate_disagreement': 'PHYSICIAN_CONSULTATION'
        }
    
    def detect_safety_keywords(self, text: str) -> list:
        """Detect safety-related keywords in text"""
        detected = []
        text_lower = text.lower()
        for keyword in self.safety_keywords:
            if keyword in text_lower:
                detected.append(keyword)
        return detected
    
    def resolve_recommendation_conflict(self, clinical_recommendation, prediction_result):
        """Resolve conflicts between clinical and AI recommendations"""
        # Calculate disagreement level
        clinical_confidence = getattr(clinical_recommendation, 'confidence', 0.8)
        ai_confidence = prediction_result.success_probability
        
        disagreement = abs(clinical_confidence - ai_confidence)
        
        # Determine conflict level
        if disagreement < 0.2:
            conflict_level = 'LOW'
        elif disagreement < 0.4:
            conflict_level = 'MODERATE'
        else:
            conflict_level = 'HIGH'
        
        # Check for safety concerns
        safety_issues = []
        clinical_notes = getattr(clinical_recommendation, 'notes', '')
        prediction_warnings = prediction_result.warnings
        
        # Check clinical notes for safety keywords
        clinical_safety = self.detect_safety_keywords(clinical_notes)
        if clinical_safety:
            safety_issues.extend(clinical_safety)
        
        # Check prediction warnings
        for warning in prediction_warnings:
            warning_safety = self.detect_safety_keywords(warning)
            if warning_safety:
                safety_issues.extend(warning_safety)
        
        # Determine resolution
        if safety_issues:
            resolution = 'EMERGENCY_REVIEW'
            escalation_required = True
        elif conflict_level == 'HIGH':
            resolution = 'CLINICAL_REVIEW'
            escalation_required = True
        elif conflict_level == 'MODERATE':
            resolution = 'PHYSICIAN_CONSULTATION'
            escalation_required = True
        else:
            resolution = 'PROCEED'
            escalation_required = False
        
        # Generate rationale
        rationale = self._generate_rationale(conflict_level, disagreement, safety_issues)
        
        return {
            'conflict_detected': conflict_level != 'LOW',
            'conflict_level': conflict_level,
            'disagreement_score': disagreement,
            'safety_issues': safety_issues,
            'recommendation': resolution,
            'escalation_required': escalation_required,
            'rationale': rationale,
            'timestamp': datetime.now()
        }
    
    def _generate_rationale(self, conflict_level: str, disagreement: float, safety_issues: list) -> str:
        """Generate explanation for conflict resolution decision"""
        if safety_issues:
            return f"Safety concerns detected: {', '.join(safety_issues)}. Emergency review required."
        elif conflict_level == 'HIGH':
            return f"High disagreement between clinical and AI recommendations ({disagreement:.2f}). Clinical review needed."
        elif conflict_level == 'MODERATE':
            return f"Moderate disagreement detected ({disagreement:.2f}). Physician consultation recommended."
        else:
            return "Low disagreement between recommendations. Safe to proceed."
    
    def escalate_to_provider(self, conflict_data: dict, patient_id: str) -> dict:
        """Escalate conflict to healthcare provider"""
        escalation_data = {
            'escalation_id': f"ESC_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'patient_id': patient_id,
            'conflict_level': conflict_data['conflict_level'],
            'safety_issues': conflict_data['safety_issues'],
            'required_action': conflict_data['recommendation'],
            'priority': self._determine_priority(conflict_data),
            'created_at': datetime.now(),
            'status': 'PENDING'
        }
        
        return escalation_data
    
    def _determine_priority(self, conflict_data: dict) -> str:
        """Determine escalation priority"""
        if conflict_data['safety_issues']:
            return 'URGENT'
        elif conflict_data['conflict_level'] == 'HIGH':
            return 'HIGH'
        else:
            return 'MEDIUM'


class MockClinicalRecommendation:
    """Mock clinical recommendation for testing"""
    
    def __init__(self, treatment_id: str, confidence: float = 0.8, notes: str = ""):
        self.treatment_id = treatment_id
        self.confidence = confidence
        self.notes = notes
        self.recommended_treatment = treatment_id
        self.evidence_level = "Level II"
        self.contraindications = []
        self.monitoring_requirements = []


# ============================================================================
# UNIT TESTS
# ============================================================================

@pytest.mark.unit
class TestConflictResolution:
    """Unit tests for conflict resolution functionality"""
    
    @pytest.fixture
    def conflict_resolver(self):
        """Create conflict resolver for testing"""
        return MockConflictResolution()
    
    @pytest.fixture
    def clinical_recommendation(self):
        """Create mock clinical recommendation"""
        return MockClinicalRecommendation(
            treatment_id="CLINICAL_TX_001",
            confidence=0.85,
            notes="Standard gabapentin protocol recommended"
        )
    
    @pytest.fixture
    def prediction_result(self, sample_patient):
        """Create mock prediction result"""
        return PredictionResult(
            patient_id=sample_patient.patient_id,
            treatment_id="AI_TX_001",
            success_probability=0.75,
            risk_score=0.25,
            key_factors=["age", "genomics"],
            warnings=["Monitor for dizziness"],
            timestamp=datetime.now()
        )
    
    def test_low_conflict_resolution(self, conflict_resolver, sample_patient):
        """Test resolution of low-conflict scenarios"""
        # Create similar recommendations
        clinical_rec = MockClinicalRecommendation("TX_001", confidence=0.8)
        prediction = PredictionResult(
            patient_id=sample_patient.patient_id,
            treatment_id="TX_001",
            success_probability=0.78,  # Very close to clinical confidence
            risk_score=0.22,
            key_factors=["genomics"],
            warnings=[],
            timestamp=datetime.now()
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(clinical_rec, prediction)
        
        assert result['conflict_detected'] is False
        assert result['conflict_level'] == 'LOW'
        assert result['recommendation'] == 'PROCEED'
        assert result['escalation_required'] is False
        assert result['disagreement_score'] < 0.2
    
    def test_high_conflict_resolution(self, conflict_resolver, sample_patient):
        """Test resolution of high-conflict scenarios"""
        # Create conflicting recommendations
        clinical_rec = MockClinicalRecommendation("TX_001", confidence=0.9)
        prediction = PredictionResult(
            patient_id=sample_patient.patient_id,
            treatment_id="TX_002",
            success_probability=0.3,  # Very different from clinical confidence
            risk_score=0.7,
            key_factors=["age", "comorbidities"],
            warnings=["High risk of side effects"],
            timestamp=datetime.now()
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(clinical_rec, prediction)
        
        assert result['conflict_detected'] is True
        assert result['conflict_level'] == 'HIGH'
        assert result['recommendation'] == 'CLINICAL_REVIEW'
        assert result['escalation_required'] is True
        assert result['disagreement_score'] >= 0.4
    
    def test_safety_keyword_detection(self, conflict_resolver):
        """Test detection of safety-related keywords"""
        # Test positive cases
        safety_text = "This treatment is contraindicated due to high risk of toxicity"
        detected = conflict_resolver.detect_safety_keywords(safety_text)
        assert len(detected) > 0
        assert 'contraindicated' in detected
        assert 'high risk' in detected
        assert 'toxicity' in detected
        
        # Test negative case
        safe_text = "This treatment shows good efficacy with minimal side effects"
        detected_safe = conflict_resolver.detect_safety_keywords(safe_text)
        assert len(detected_safe) == 0
        
        # Test case insensitive
        upper_safety_text = "AVOID THIS DANGEROUS COMBINATION"
        detected_upper = conflict_resolver.detect_safety_keywords(upper_safety_text)
        assert len(detected_upper) > 0
        assert 'avoid' in detected_upper
        assert 'dangerous' in detected_upper
    
    def test_safety_concern_escalation(self, conflict_resolver, sample_patient):
        """Test escalation when safety concerns are detected"""
        # Clinical recommendation with safety concerns
        clinical_rec = MockClinicalRecommendation(
            "TX_SAFETY_001", 
            confidence=0.7,
            notes="Contraindicated in patients with severe liver disease. High risk of toxicity."
        )
        
        prediction = PredictionResult(
            patient_id=sample_patient.patient_id,
            treatment_id="TX_SAFETY_001",
            success_probability=0.6,
            risk_score=0.4,
            key_factors=["liver_function"],
            warnings=["DANGEROUS: Severe interaction detected"],
            timestamp=datetime.now()
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(clinical_rec, prediction)
        
        assert result['conflict_detected'] is True
        assert len(result['safety_issues']) > 0
        assert result['recommendation'] == 'EMERGENCY_REVIEW'
        assert result['escalation_required'] is True
        assert 'safety' in result['rationale'].lower()
    
    def test_moderate_conflict_resolution(self, conflict_resolver, sample_patient):
        """Test resolution of moderate-conflict scenarios"""
        clinical_rec = MockClinicalRecommendation("TX_MOD_001", confidence=0.8)
        prediction = PredictionResult(
            patient_id=sample_patient.patient_id,
            treatment_id="TX_MOD_001",
            success_probability=0.5,  # Moderate disagreement
            risk_score=0.5,
            key_factors=["age"],
            warnings=["Monitor closely"],
            timestamp=datetime.now()
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(clinical_rec, prediction)
        
        assert result['conflict_detected'] is True
        assert result['conflict_level'] == 'MODERATE'
        assert result['recommendation'] == 'PHYSICIAN_CONSULTATION'
        assert result['escalation_required'] is True
        assert 0.2 <= result['disagreement_score'] < 0.4
    
    def test_escalation_to_provider(self, conflict_resolver, sample_patient):
        """Test escalation workflow to healthcare provider"""
        # Create conflict scenario
        conflict_data = {
            'conflict_level': 'HIGH',
            'safety_issues': ['contraindicated'],
            'recommendation': 'EMERGENCY_REVIEW',
            'disagreement_score': 0.6
        }
        
        escalation = conflict_resolver.escalate_to_provider(conflict_data, sample_patient.patient_id)
        
        assert 'escalation_id' in escalation
        assert escalation['patient_id'] == sample_patient.patient_id
        assert escalation['conflict_level'] == 'HIGH'
        assert escalation['required_action'] == 'EMERGENCY_REVIEW'
        assert escalation['priority'] == 'URGENT'  # Due to safety issues
        assert escalation['status'] == 'PENDING'
        assert 'created_at' in escalation
    
    def test_priority_determination(self, conflict_resolver):
        """Test escalation priority determination"""
        # Urgent priority for safety issues
        safety_conflict = {
            'safety_issues': ['dangerous', 'toxicity'],
            'conflict_level': 'HIGH'
        }
        priority = conflict_resolver._determine_priority(safety_conflict)
        assert priority == 'URGENT'
        
        # High priority for high conflict without safety issues
        high_conflict = {
            'safety_issues': [],
            'conflict_level': 'HIGH'
        }
        priority = conflict_resolver._determine_priority(high_conflict)
        assert priority == 'HIGH'
        
        # Medium priority for moderate conflict
        moderate_conflict = {
            'safety_issues': [],
            'conflict_level': 'MODERATE'
        }
        priority = conflict_resolver._determine_priority(moderate_conflict)
        assert priority == 'MEDIUM'
    
    def test_rationale_generation(self, conflict_resolver):
        """Test rationale generation for different scenarios"""
        # Safety rationale
        safety_rationale = conflict_resolver._generate_rationale('HIGH', 0.6, ['contraindicated', 'dangerous'])
        assert 'safety concerns' in safety_rationale.lower()
        assert 'emergency review' in safety_rationale.lower()
        
        # High conflict rationale
        high_rationale = conflict_resolver._generate_rationale('HIGH', 0.5, [])
        assert 'high disagreement' in high_rationale.lower()
        assert 'clinical review' in high_rationale.lower()
        
        # Moderate conflict rationale
        moderate_rationale = conflict_resolver._generate_rationale('MODERATE', 0.3, [])
        assert 'moderate disagreement' in moderate_rationale.lower()
        assert 'physician consultation' in moderate_rationale.lower()
        
        # Low conflict rationale
        low_rationale = conflict_resolver._generate_rationale('LOW', 0.1, [])
        assert 'low disagreement' in low_rationale.lower()
        assert 'proceed' in low_rationale.lower()
    
    def test_conflict_resolution_edge_cases(self, conflict_resolver, sample_patient):
        """Test edge cases in conflict resolution"""
        # Test with missing confidence in clinical recommendation
        clinical_rec_no_confidence = Mock()
        clinical_rec_no_confidence.confidence = None
        
        prediction = PredictionResult(
            patient_id=sample_patient.patient_id,
            treatment_id="EDGE_TX_001",
            success_probability=0.7,
            risk_score=0.3,
            key_factors=["age"],
            warnings=[],
            timestamp=datetime.now()
        )
        
        # Should handle gracefully with default confidence
        result = conflict_resolver.resolve_recommendation_conflict(clinical_rec_no_confidence, prediction)
        assert 'conflict_detected' in result
        assert 'recommendation' in result
        
        # Test with empty warnings
        prediction_no_warnings = PredictionResult(
            patient_id=sample_patient.patient_id,
            treatment_id="EDGE_TX_002",
            success_probability=0.8,
            risk_score=0.2,
            key_factors=["genomics"],
            warnings=[],
            timestamp=datetime.now()
        )
        
        clinical_rec_empty_notes = MockClinicalRecommendation("EDGE_TX_002", confidence=0.8, notes="")
        
        result = conflict_resolver.resolve_recommendation_conflict(clinical_rec_empty_notes, prediction_no_warnings)
        assert result['safety_issues'] == []
        assert result['recommendation'] == 'PROCEED'


@pytest.mark.unit
class TestConflictResolutionIntegration:
    """Integration tests for conflict resolution with other components"""
    
    def test_end_to_end_conflict_workflow(self, sample_patient, sample_treatment):
        """Test complete conflict resolution workflow"""
        resolver = MockConflictResolution()
        
        # Create conflicting recommendations
        clinical_rec = MockClinicalRecommendation(
            sample_treatment.treatment_id,
            confidence=0.9,
            notes="Highly recommended based on clinical guidelines"
        )
        
        prediction = PredictionResult(
            patient_id=sample_patient.patient_id,
            treatment_id=sample_treatment.treatment_id,
            success_probability=0.4,  # Conflicts with clinical confidence
            risk_score=0.6,
            key_factors=["genomics", "age"],
            warnings=["High risk of adverse events"],
            timestamp=datetime.now()
        )
        
        # Resolve conflict
        conflict_result = resolver.resolve_recommendation_conflict(clinical_rec, prediction)
        
        # Should detect high conflict
        assert conflict_result['conflict_detected'] is True
        assert conflict_result['escalation_required'] is True
        
        # Escalate to provider
        escalation = resolver.escalate_to_provider(conflict_result, sample_patient.patient_id)
        
        # Verify escalation created
        assert escalation['patient_id'] == sample_patient.patient_id
        assert escalation['status'] == 'PENDING'
        assert escalation['priority'] in ['HIGH', 'URGENT', 'MEDIUM']
    
    def test_multiple_conflict_scenarios(self, conflict_resolver, sample_patient):
        """Test handling multiple conflict scenarios sequentially"""
        scenarios = [
            # Low conflict
            {
                'clinical_confidence': 0.8,
                'ai_confidence': 0.82,
                'clinical_notes': 'Standard treatment',
                'ai_warnings': ['Monitor side effects'],
                'expected_level': 'LOW'
            },
            # Moderate conflict
            {
                'clinical_confidence': 0.7,
                'ai_confidence': 0.4,
                'clinical_notes': 'Good option for this patient',
                'ai_warnings': ['Consider alternatives'],
                'expected_level': 'MODERATE'
            },
            # High conflict
            {
                'clinical_confidence': 0.9,
                'ai_confidence': 0.2,
                'clinical_notes': 'Highly effective treatment',
                'ai_warnings': ['Poor predicted outcome'],
                'expected_level': 'HIGH'
            },
            # Safety concern
            {
                'clinical_confidence': 0.8,
                'ai_confidence': 0.6,
                'clinical_notes': 'Contraindicated in liver disease',
                'ai_warnings': ['Dangerous interaction detected'],
                'expected_level': 'HIGH'  # Due to safety issues
            }
        ]
        
        for i, scenario in enumerate(scenarios):
            clinical_rec = MockClinicalRecommendation(
                f"SCENARIO_TX_{i:03d}",
                confidence=scenario['clinical_confidence'],
                notes=scenario['clinical_notes']
            )
            
            prediction = PredictionResult(
                patient_id=sample_patient.patient_id,
                treatment_id=f"SCENARIO_TX_{i:03d}",
                success_probability=scenario['ai_confidence'],
                risk_score=1 - scenario['ai_confidence'],
                key_factors=["test"],
                warnings=scenario['ai_warnings'],
                timestamp=datetime.now()
            )
            
            result = conflict_resolver.resolve_recommendation_conflict(clinical_rec, prediction)
            
            # Check expected conflict level (allowing for safety escalation)
            if 'contraindicated' in scenario['clinical_notes'].lower() or 'dangerous' in ' '.join(scenario['ai_warnings']).lower():
                assert result['recommendation'] == 'EMERGENCY_REVIEW'
            else:
                assert result['conflict_level'] == scenario['expected_level']


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 