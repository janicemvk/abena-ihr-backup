# Mock workflow orchestrator for testing - Updated to use Abena SDK
from enum import Enum
from typing import Dict, List, Any
from datetime import datetime
from src.core.abena_sdk import AbenaSDK

class IntegrationType(Enum):
    EPIC = "epic"
    CERNER = "cerner"

class AlertPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"

class EMRIntegrationManager:
    """EMR Integration Manager using Abena SDK for auth and data access"""
    
    def __init__(self, abena_sdk: AbenaSDK, integration_type: IntegrationType, config: Dict[str, Any], simulate_failure: bool = False):
        self.abena = abena_sdk
        self.integration_type = integration_type
        self.config = config
        self.simulate_failure = simulate_failure
        self.logger = Mock()
    
    async def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Get patient data using Abena SDK"""
        try:
            if self.simulate_failure:
                return {}
            
            # Use Abena SDK to get patient data (handles auth, privacy, audit)
            patient_data = await self.abena.get_patient_data(patient_id, 'emr_integration')
            
            # Mock EMR-specific data structure
            emr_data = {
                'patient': {'resourceType': 'Patient', 'id': patient_id},
                'observations': [],
                'medications': [],
                'retrieved_at': datetime.now(),
                'emr_type': self.integration_type.value
            }
            
            return emr_data
            
        except Exception as e:
            # Log error through Abena SDK
            await self.abena.create_alert({
                'type': 'emr_data_retrieval_failure',
                'message': f'EMR data retrieval failed: {str(e)}',
                'severity': 'medium'
            })
            return {}

class ClinicalNoteGenerator:
    """Clinical Note Generator using Abena SDK for data access and audit logging"""
    
    def __init__(self, abena_sdk: AbenaSDK):
        self.abena = abena_sdk
        self.templates = {
            'pain_management': 'template',
            'adverse_event_alert': 'template',
            'treatment_optimization': 'template'
        }
    
    async def generate_pain_management_note(self, patient_id: str, abena_insights: Dict[str, Any], provider: str) -> str:
        """Generate pain management note using Abena SDK"""
        try:
            # Get patient data through Abena SDK
            patient_data = await self.abena.get_patient_data(patient_id, 'pain_management_note')
            
            note_content = f"""
ABENA IHR CLINICAL ANALYSIS
Patient: {patient_id}
Provider: {provider}
Success Probability: {abena_insights.get('success_probability', 0) * 100:.1f}%
Recommendations: {', '.join(abena_insights.get('recommendations', []))}
            """.strip()
            
            # Save note using Abena SDK
            await self.abena.save_treatment_plan(patient_id, {
                'note_type': 'pain_management',
                'content': note_content,
                'provider': provider,
                'generated_at': datetime.now().isoformat()
            })
            
            return note_content
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'note_generation_failure',
                'message': f'Pain management note generation failed: {str(e)}',
                'severity': 'medium'
            })
            return "Error generating note"
    
    async def generate_adverse_event_alert(self, patient_id: str, risk_assessment: Dict[str, Any], provider: str) -> str:
        """Generate adverse event alert using Abena SDK"""
        try:
            # Get patient data through Abena SDK
            patient_data = await self.abena.get_patient_data(patient_id, 'adverse_event_alert')
            
            risk_level = risk_assessment.get('overall_risk_level', 'UNKNOWN')
            risk_scores = risk_assessment.get('risk_scores', {})
            
            alert_text = f"""
ADVERSE EVENT RISK ALERT
Patient: {patient_id}
Provider: {provider}
Risk Level: {risk_level}
            """.strip()
            
            for event_name, event_data in risk_scores.items():
                probability = event_data.get('probability', 0) * 100
                # Format event name for display (capitalize and replace underscores)
                display_name = event_name.replace('_', ' ').title()
                alert_text += f"\n{display_name}: {probability:.1f}%"
            
            # Create alert using Abena SDK
            await self.abena.create_alert({
                'type': 'adverse_event_risk',
                'patient_id': patient_id,
                'content': alert_text,
                'severity': risk_level.lower(),
                'provider': provider
            })
            
            return alert_text
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'alert_generation_failure',
                'message': f'Adverse event alert generation failed: {str(e)}',
                'severity': 'high'
            })
            return "Error generating alert"

class RealTimeAlertSystem:
    """Real-Time Alert System using Abena SDK for data access and alert management"""
    
    def __init__(self, abena_sdk: AbenaSDK):
        self.abena = abena_sdk
        self.active_alerts = {}
    
    async def create_alert(self, patient_id: str, provider_id: str, alert_type: str, 
                    priority: AlertPriority, title: str, message: str, 
                    recommendations: List[str], duration_hours: int = 24) -> str:
        """Create alert using Abena SDK"""
        try:
            alert_id = f"alert_{len(self.active_alerts) + 1}"
            
            alert_data = {
                'alert_id': alert_id,
                'patient_id': patient_id,
                'provider_id': provider_id,
                'alert_type': alert_type,
                'priority': priority.value,
                'title': title,
                'message': message,
                'recommendations': recommendations,
                'duration_hours': duration_hours,
                'created_at': datetime.now().isoformat(),
                'acknowledged': False
            }
            
            # Store alert locally
            self.active_alerts[alert_id] = MockAlert(
                alert_id=alert_id,
                patient_id=patient_id,
                provider_id=provider_id,
                alert_type=alert_type,
                priority=priority,
                title=title,
                message=message,
                recommendations=recommendations,
                acknowledged=False
            )
            
            # Create alert through Abena SDK (handles blockchain and audit)
            await self.abena.create_alert({
                'alert_id': alert_id,
                'patient_id': patient_id,
                'type': alert_type,
                'severity': priority.value,
                'message': message,
                'recommendations': recommendations
            })
            
            return alert_id
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'alert_creation_failure',
                'message': f'Alert creation failed: {str(e)}',
                'severity': 'high'
            })
            return ""
    
    async def acknowledge_alert(self, alert_id: str, provider_id: str) -> bool:
        """Acknowledge alert using Abena SDK"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            
            # Log acknowledgment through Abena SDK
            await self.abena.save_treatment_plan(alert.patient_id, {
                'action': 'alert_acknowledged',
                'alert_id': alert_id,
                'provider_id': provider_id,
                'timestamp': datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'alert_acknowledgment_failure',
                'message': f'Alert acknowledgment failed: {str(e)}',
                'severity': 'medium'
            })
            return False
    
    async def get_active_alerts_for_provider(self, provider_id: str) -> List['MockAlert']:
        """Get active alerts for provider using Abena SDK"""
        try:
            # Get patient data through Abena SDK to ensure access permissions
            # This is a mock implementation - in real system would filter by provider
            provider_alerts = [
                alert for alert in self.active_alerts.values() 
                if alert.provider_id == provider_id
            ]
            # Sort by priority (CRITICAL first)
            priority_order = [AlertPriority.CRITICAL, AlertPriority.HIGH, AlertPriority.MODERATE, AlertPriority.LOW]
            return sorted(provider_alerts, key=lambda x: priority_order.index(x.priority))
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'alert_retrieval_failure',
                'message': f'Alert retrieval failed: {str(e)}',
                'severity': 'medium'
            })
            return []

class MockAlert:
    def __init__(self, alert_id: str, patient_id: str, provider_id: str, 
                 alert_type: str, priority: AlertPriority, title: str, 
                 message: str, recommendations: List[str], acknowledged: bool):
        self.alert_id = alert_id
        self.patient_id = patient_id
        self.provider_id = provider_id
        self.alert_type = alert_type
        self.priority = priority
        self.title = title
        self.message = message
        self.recommendations = recommendations
        self.acknowledged = acknowledged

class Mock:
    """Simple mock class for testing"""
    pass 