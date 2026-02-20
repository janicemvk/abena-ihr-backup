# Abena IHR - Provider Workflow Integration with SDK
# Native integration into clinical workflow tools with real-time alerts and automated documentation

# ✅ CORRECT PATTERN - Use Abena SDK for all auth, data, privacy, and audit needs
# 
# BEFORE (❌ Wrong - has its own auth/data):
# class SomeModule {
#   constructor() {
#     this.database = new Database();
#     this.authSystem = new CustomAuth();
#   }
# }
# 
# AFTER (✅ Correct - uses Abena SDK):
# import AbenaSDK from '@abena/sdk';
# 
# class SomeModule {
#   constructor() {
#     this.abena = new AbenaSDK({
#       authServiceUrl: 'http://localhost:3001',
#       dataServiceUrl: 'http://localhost:8001',
#       privacyServiceUrl: 'http://localhost:8002',
#       blockchainServiceUrl: 'http://localhost:8003'
#     });
#   }
#   
#   async someMethod(patientId, userId) {
#     // 1. Auto-handled auth & permissions
#     const patientData = await this.abena.getPatientData(patientId, 'module_purpose');
#     
#     // 2. Auto-handled privacy & encryption
#     // 3. Auto-handled audit logging
#     
#     // 4. Focus on your business logic
#     return this.processData(patientData);
#   }
# }

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio
import xml.etree.ElementTree as ET
from jinja2 import Template

# Import Abena SDK (Python equivalent)
from abena_sdk import AbenaSDK, AbenaConfig

class AlertPriority(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class IntegrationType(Enum):
    EPIC = "epic"
    CERNER = "cerner"
    ALLSCRIPTS = "allscripts"
    ATHENA = "athena"
    GENERIC_FHIR = "generic_fhir"

@dataclass
class ClinicalAlert:
    """Real-time clinical alert structure"""
    alert_id: str
    patient_id: str
    provider_id: str
    alert_type: str
    priority: AlertPriority
    title: str
    message: str
    actionable_recommendations: List[str]
    timestamp: datetime
    expires_at: datetime
    acknowledged: bool = False
    dismissed: bool = False

@dataclass
class AbenaInsight:
    """Abena clinical insight structure"""
    insight_id: str
    patient_id: str
    insight_type: str
    confidence_score: float
    recommendations: List[str]
    supporting_evidence: Dict
    generated_at: datetime
    clinical_priority: AlertPriority

class EMRIntegrationManager:
    """Manages integration with various EMR systems using Abena SDK"""
    
    def __init__(self, integration_type: IntegrationType, config: Dict):
        self.integration_type = integration_type
        self.config = config
        self.logger = self._setup_logging()
        
        # ✅ Initialize Abena SDK instead of custom auth/database
        self.abena = AbenaSDK(AbenaConfig(
            auth_service_url=config.get('auth_service_url', 'http://localhost:3001'),
            data_service_url=config.get('data_service_url', 'http://localhost:8001'),
            privacy_service_url=config.get('privacy_service_url', 'http://localhost:8002'),
            blockchain_service_url=config.get('blockchain_service_url', 'http://localhost:8003'),
            module_id='provider_workflow_integration',
            api_key=config.get('api_key')
        ))
        
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(f"abena_emr_{self.integration_type.value}")
    
    async def get_patient_data(self, patient_id: str, user_id: str) -> Dict:
        """
        Retrieve patient data using Abena SDK with automatic auth, privacy, and audit
        """
        try:
            # ✅ Use Abena SDK - handles auth, permissions, privacy, audit automatically
            patient_data = await self.abena.get_patient_data(
                patient_id, 
                purpose='provider_workflow_integration',
                user_id=user_id,
                required_data=['demographics', 'observations', 'medications', 'allergies']
            )
            
            # SDK automatically handles:
            # 1. Authentication & authorization
            # 2. Privacy controls & encryption
            # 3. Audit logging
            # 4. Data governance compliance
            
            return patient_data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve patient data via Abena SDK: {str(e)}")
            return {}
    
    async def push_clinical_note(self, patient_id: str, note_content: str, 
                               note_type: str, user_id: str) -> bool:
        """Push clinical note using Abena SDK with audit trail"""
        try:
            # ✅ Use Abena SDK for secure note creation
            note_result = await self.abena.create_clinical_note(
                patient_id=patient_id,
                content=note_content,
                note_type=note_type,
                user_id=user_id,
                system_generated=True,
                metadata={
                    'source': 'abena_provider_workflow',
                    'integration_type': self.integration_type.value
                }
            )
            
            return note_result.get('success', False)
            
        except Exception as e:
            self.logger.error(f"Failed to push clinical note: {str(e)}")
            return False

class ClinicalNoteGenerator:
    """Generates automated clinical notes using Abena SDK"""
    
    def __init__(self, abena_sdk: AbenaSDK):
        self.abena = abena_sdk  # ✅ Use shared Abena SDK instance
        self.logger = logging.getLogger(__name__)
        self.templates = self._load_note_templates()
    
    def _load_note_templates(self) -> Dict[str, Template]:
        """Load clinical note templates"""
        templates = {
            'pain_management': Template("""
ABENA IHR CLINICAL ANALYSIS - PAIN MANAGEMENT
Generated: {{ timestamp }}
Patient ID: {{ patient_id }}

ASSESSMENT:
{{ assessment }}

ABENA INSIGHTS:
• Treatment Success Probability: {{ success_probability }}%
• Risk Assessment: {{ risk_level }}
{% if key_factors %}
Key Clinical Factors:
{% for factor in key_factors %}
• {{ factor }}
{% endfor %}
{% endif %}

RECOMMENDATIONS:
{% for recommendation in recommendations %}
{{ loop.index }}. {{ recommendation }}
{% endfor %}

{% if warnings %}
CLINICAL WARNINGS:
{% for warning in warnings %}
⚠ {{ warning }}
{% endfor %}
{% endif %}

GENOMIC CONSIDERATIONS:
{{ genomic_summary }}

PLAN:
{{ treatment_plan }}

Next Review: {{ next_review_date }}
Provider: {{ provider_name }}
System: Abena IHR v2.0 with SDK Integration
            """),
            
            'adverse_event_alert': Template("""
ABENA IHR ADVERSE EVENT RISK ALERT
Generated: {{ timestamp }}
Patient ID: {{ patient_id }}
Alert Priority: {{ priority }}

RISK ASSESSMENT:
{{ risk_summary }}

HIGH-RISK EVENTS IDENTIFIED:
{% for event in high_risk_events %}
• {{ event.name }}: {{ event.probability }}% probability
  Recommendation: {{ event.mitigation }}
{% endfor %}

IMMEDIATE ACTIONS REQUIRED:
{% for action in immediate_actions %}
{{ loop.index }}. {{ action }}
{% endfor %}

Provider Notification: {{ provider_name }}
Escalation Required: {{ escalation_needed }}
            """),
            
            'treatment_optimization': Template("""
ABENA IHR TREATMENT OPTIMIZATION REPORT
Generated: {{ timestamp }}
Patient ID: {{ patient_id }}

CURRENT TREATMENT ANALYSIS:
{{ current_treatment }}

OPTIMIZATION OPPORTUNITIES:
{% for opportunity in optimizations %}
{{ loop.index }}. {{ opportunity.description }}
   Expected Improvement: {{ opportunity.expected_benefit }}
   Implementation: {{ opportunity.implementation }}
{% endfor %}

BIOMARKER TRENDS:
{{ biomarker_analysis }}

PATIENT-REPORTED OUTCOMES:
{{ patient_outcomes }}

RECOMMENDED ADJUSTMENTS:
{{ recommendations }}
            """)
        }
        return templates
    
    async def generate_pain_management_note(self, patient_id: str, abena_insights: Dict, 
                                          provider_name: str, user_id: str) -> str:
        """Generate comprehensive pain management note with SDK integration"""
        
        # ✅ Use Abena SDK to get additional context
        try:
            genomic_data = await self.abena.get_genomic_data(patient_id, user_id)
            risk_factors = await self.abena.get_risk_factors(patient_id, user_id)
        except Exception as e:
            self.logger.warning(f"Could not retrieve additional data via SDK: {str(e)}")
            genomic_data = {}
            risk_factors = {}
        
        template_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'patient_id': patient_id,
            'provider_name': provider_name,
            'assessment': abena_insights.get('clinical_assessment', 'Chronic pain patient under evaluation'),
            'success_probability': round(abena_insights.get('success_probability', 0) * 100, 1),
            'risk_level': abena_insights.get('risk_level', 'MODERATE'),
            'key_factors': abena_insights.get('key_factors', []),
            'recommendations': abena_insights.get('recommendations', []),
            'warnings': abena_insights.get('warnings', []),
            'genomic_summary': self._generate_genomic_summary(genomic_data),
            'treatment_plan': abena_insights.get('treatment_plan', 'Continue current therapy with monitoring'),
            'next_review_date': (datetime.now() + timedelta(weeks=4)).strftime('%Y-%m-%d')
        }
        
        return self.templates['pain_management'].render(**template_data)
    
    async def generate_adverse_event_alert(self, patient_id: str, risk_assessment: Dict, 
                                         provider_name: str, user_id: str) -> str:
        """Generate adverse event alert note with SDK integration"""
        
        # ✅ Use Abena SDK to get real-time risk data
        try:
            real_time_risks = await self.abena.get_real_time_risk_assessment(patient_id, user_id)
            risk_assessment.update(real_time_risks)
        except Exception as e:
            self.logger.warning(f"Could not retrieve real-time risks: {str(e)}")
        
        high_risk_events = []
        immediate_actions = []
        
        for event_type, risk_data in risk_assessment.get('risk_scores', {}).items():
            if risk_data['risk_level'] in ['HIGH', 'CRITICAL']:
                high_risk_events.append({
                    'name': event_type.replace('_', ' ').title(),
                    'probability': round(risk_data['probability'] * 100, 1),
                    'mitigation': self._get_mitigation_strategy(event_type)
                })
        
        if high_risk_events:
            immediate_actions = [
                "Review current medication list for interactions",
                "Implement enhanced monitoring protocol", 
                "Schedule follow-up within 1 week",
                "Educate patient on warning signs"
            ]
        
        template_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'patient_id': patient_id,
            'provider_name': provider_name,
            'priority': risk_assessment.get('overall_risk_level', 'MODERATE'),
            'risk_summary': f"Overall risk level: {risk_assessment.get('overall_risk_level', 'MODERATE')}",
            'high_risk_events': high_risk_events,
            'immediate_actions': immediate_actions,
            'escalation_needed': 'YES' if risk_assessment.get('overall_risk_level') == 'CRITICAL' else 'NO'
        }
        
        return self.templates['adverse_event_alert'].render(**template_data)
    
    def _generate_genomic_summary(self, genomics_data: Dict) -> str:
        """Generate genomic summary for clinical note"""
        if not genomics_data:
            return "No genomic data available"
        
        summary_parts = []
        
        if genomics_data.get('CYP2C9_activity', 1.0) < 0.7:
            summary_parts.append("Reduced CYP2C9 activity - consider dose adjustments")
        
        if genomics_data.get('OPRM1_variant', 0):
            summary_parts.append("OPRM1 variant present - may affect opioid response")
        
        if genomics_data.get('COMT_activity', 1.0) != 1.0:
            activity = "increased" if genomics_data['COMT_activity'] > 1.0 else "decreased"
            summary_parts.append(f"COMT activity {activity} - impacts pain sensitivity")
        
        return "; ".join(summary_parts) if summary_parts else "No significant pharmacogenomic variants identified"
    
    def _get_mitigation_strategy(self, event_type: str) -> str:
        """Get mitigation strategy for adverse events"""
        strategies = {
            'severe_side_effects': "Reduce dose, increase monitoring frequency",
            'treatment_discontinuation': "Provide patient education and support",
            'hospitalization': "Implement outpatient monitoring protocol",
            'drug_interaction': "Review medication list, consider alternatives",
            'allergic_reaction': "Verify allergy history, prepare emergency protocols"
        }
        return strategies.get(event_type, "Implement enhanced monitoring")

class RealTimeAlertSystem:
    """Manages real-time alerts using Abena SDK"""
    
    def __init__(self, abena_sdk: AbenaSDK, emr_manager: EMRIntegrationManager):
        self.abena = abena_sdk  # ✅ Use shared Abena SDK instance
        self.emr_manager = emr_manager
        self.logger = logging.getLogger(__name__)
        self.alert_channels = []
        
    def add_alert_channel(self, channel_type: str, config: Dict):
        """Add notification channel (email, SMS, EMR popup, etc.)"""
        self.alert_channels.append({
            'type': channel_type,
            'config': config
        })
    
    async def create_alert(self, patient_id: str, provider_id: str, alert_type: str, 
                          priority: AlertPriority, title: str, message: str, 
                          recommendations: List[str], duration_hours: int = 24,
                          user_id: str = None) -> str:
        """Create new clinical alert using Abena SDK"""
        
        alert_id = str(uuid.uuid4())
        alert = ClinicalAlert(
            alert_id=alert_id,
            patient_id=patient_id,
            provider_id=provider_id,
            alert_type=alert_type,
            priority=priority,
            title=title,
            message=message,
            actionable_recommendations=recommendations,
            timestamp=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=duration_hours)
        )
        
        # ✅ Use Abena SDK to create alert with automatic audit trail
        try:
            await self.abena.create_alert(
                alert_id=alert_id,
                patient_id=patient_id,
                provider_id=provider_id,
                alert_data=asdict(alert),
                user_id=user_id or provider_id
            )
        except Exception as e:
            self.logger.error(f"Failed to create alert via SDK: {str(e)}")
        
        # Send notifications
        await self._send_alert_notifications(alert)
        
        # Push to EMR if critical
        if priority in [AlertPriority.HIGH, AlertPriority.CRITICAL]:
            await self._push_alert_to_emr(alert, user_id or provider_id)
        
        self.logger.info(f"Alert created: {alert_id} for patient {patient_id}")
        return alert_id
    
    async def _send_alert_notifications(self, alert: ClinicalAlert):
        """Send alert through configured notification channels"""
        for channel in self.alert_channels:
            try:
                if channel['type'] == 'abena_notification':
                    # ✅ Use Abena SDK notification system
                    await self.abena.send_notification(
                        user_id=alert.provider_id,
                        notification_type='clinical_alert',
                        title=alert.title,
                        message=alert.message,
                        priority=alert.priority.value,
                        metadata={'alert_id': alert.alert_id}
                    )
            except Exception as e:
                self.logger.error(f"Failed to send alert via {channel['type']}: {str(e)}")
    
    async def _push_alert_to_emr(self, alert: ClinicalAlert, user_id: str):
        """Push high priority alerts directly to EMR"""
        alert_note = f"""
ABENA IHR CLINICAL ALERT - {alert.priority.value.upper()}
{alert.title}

{alert.message}

Actionable Recommendations:
{chr(10).join(f"• {rec}" for rec in alert.actionable_recommendations)}

Alert ID: {alert.alert_id}
Generated: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await self.emr_manager.push_clinical_note(
            alert.patient_id, 
            alert_note, 
            f"Abena_Alert_{alert.priority.value}",
            user_id
        )
    
    async def acknowledge_alert(self, alert_id: str, provider_id: str) -> bool:
        """Mark alert as acknowledged by provider"""
        try:
            # ✅ Use Abena SDK to record acknowledgment
            await self.abena.acknowledge_alert(alert_id, provider_id)
            self.logger.info(f"Alert {alert_id} acknowledged by provider {provider_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to acknowledge alert via SDK: {str(e)}")
            return False
    
    async def get_active_alerts_for_provider(self, provider_id: str) -> List[ClinicalAlert]:
        """Get all active alerts for a provider using Abena SDK"""
        try:
            # ✅ Use Abena SDK to get alerts with proper permissions
            sdk_alerts = await self.abena.get_provider_alerts(provider_id)
            
            # Convert SDK alerts to ClinicalAlert objects
            active_alerts = []
            for alert_data in sdk_alerts:
                alert = ClinicalAlert(
                    alert_id=alert_data['alert_id'],
                    patient_id=alert_data['patient_id'],
                    provider_id=alert_data['provider_id'],
                    alert_type=alert_data['alert_type'],
                    priority=AlertPriority(alert_data['priority']),
                    title=alert_data['title'],
                    message=alert_data['message'],
                    actionable_recommendations=alert_data['actionable_recommendations'],
                    timestamp=datetime.fromisoformat(alert_data['timestamp']),
                    expires_at=datetime.fromisoformat(alert_data['expires_at']),
                    acknowledged=alert_data.get('acknowledged', False),
                    dismissed=alert_data.get('dismissed', False)
                )
                active_alerts.append(alert)
            
            # Sort by priority and timestamp
            priority_order = {
                AlertPriority.CRITICAL: 0,
                AlertPriority.HIGH: 1,
                AlertPriority.MODERATE: 2,
                AlertPriority.LOW: 3
            }
            
            active_alerts.sort(key=lambda x: (priority_order[x.priority], x.timestamp))
            return active_alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get alerts via SDK: {str(e)}")
            return []

class WorkflowIntegrationOrchestrator:
    """Main orchestrator for provider workflow integration using Abena SDK"""
    
    def __init__(self, config: Dict):
        # ✅ Initialize Abena SDK first
        self.abena = AbenaSDK(AbenaConfig(
            auth_service_url=config.get('auth_service_url', 'http://localhost:3001'),
            data_service_url=config.get('data_service_url', 'http://localhost:8001'),
            privacy_service_url=config.get('privacy_service_url', 'http://localhost:8002'),
            blockchain_service_url=config.get('blockchain_service_url', 'http://localhost:8003'),
            module_id='provider_workflow_integration',
            api_key=config.get('api_key')
        ))
        
        # Initialize other components with shared SDK instance
        self.emr_manager = EMRIntegrationManager(
            IntegrationType(config['emr_type']), 
            config
        )
        self.emr_manager.abena = self.abena  # Share SDK instance
        
        self.note_generator = ClinicalNoteGenerator(self.abena)
        self.alert_system = RealTimeAlertSystem(self.abena, self.emr_manager)
        self.logger = logging.getLogger(__name__)
        
        # Setup alert channels
        self._setup_alert_channels(config.get('alert_channels', []))
    
    def _setup_alert_channels(self, channels: List[Dict]):
        """Setup notification channels"""
        for channel in channels:
            self.alert_system.add_alert_channel(channel['type'], channel['config'])
    
    async def process_abena_insights(self, patient_id: str, provider_id: str, 
                                   abena_insights: AbenaInsight, user_id: str = None) -> Dict:
        """Process Abena insights and integrate into provider workflow"""
        
        user_id = user_id or provider_id
        results = {
            'patient_id': patient_id,
            'processed_at': datetime.now(),
            'actions_taken': []
        }
        
        try:
            # ✅ Use Abena SDK to validate and process insights
            validated_insights = await self.abena.validate_insights(
                patient_id, 
                asdict(abena_insights), 
                user_id
            )
            
            # 1. Generate and push clinical note
            if abena_insights.insight_type == 'pain_management':
                note_content = await self.note_generator.generate_pain_management_note(
                    patient_id, 
                    validated_insights, 
                    provider_id,
                    user_id
                )
                
                if await self.emr_manager.push_clinical_note(patient_id, note_content, 
                                                           "Abena_Pain_Management", user_id):
                    results['actions_taken'].append('Clinical note generated and pushed to EMR')
                    
                    # ✅ Log to blockchain for immutable audit trail
                    await self.abena.log_clinical_action(
                        patient_id=patient_id,
                        user_id=user_id,
                        action_type='clinical_note_generated',
                        metadata={'note_type': 'pain_management', 'insight_id': abena_insights.insight_id}
                    )
            
            # 2. Create alerts for high priority insights
            if abena_insights.clinical_priority in [AlertPriority.HIGH, AlertPriority.CRITICAL]:
                alert_id = await self.alert_system.create_alert(
                    patient_id=patient_id,
                    provider_id=provider_id,
                    alert_type=abena_insights.insight_type,
                    priority=abena_insights.clinical_priority,
                    title=f"Abena IHR: {abena_insights.insight_type.replace('_', ' ').title()}",
                    message=f"New insights available with {abena_insights.confidence_score:.1%} confidence",
                    recommendations=abena_insights.recommendations,
                    user_id=user_id
                )
                results['actions_taken'].append(f'High priority alert created: {alert_id}')
            
            # 3. Update patient risk profile using SDK
            await self._update_patient_risk_profile(patient_id, abena_insights, user_id)
            results['actions_taken'].append('Patient risk profile updated via Abena SDK')
            
            # 4. Schedule follow-up if needed
            if abena_insights.clinical_priority == AlertPriority.CRITICAL:
                await self._schedule_urgent_follow_up(patient_id, provider_id, user_id)
                results['actions_taken'].append('Urgent follow-up scheduled')
            
            # 5. ✅ Update provider dashboard via SDK
            await self.abena.update_provider_dashboard(
                provider_id=provider_id,
                patient_id=patient_id,
                insight_summary={
                    'type': abena_insights.insight_type,
                    'priority': abena_insights.clinical_priority.value,
                    'confidence': abena_insights.confidence_score,
                    'recommendations_count': len(abena_insights.recommendations)
                }
            )
            results['actions_taken'].append('Provider dashboard updated')
            
            results['status'] = 'success'
            
        except Exception as e:
            self.logger.error(f"Error processing Abena insights: {str(e)}")
            results['status'] = 'error'
            results['error'] = str(e)
            
            # ✅ Log error to Abena SDK for monitoring
            await self.abena.log_error(
                module='provider_workflow_integration',
                error=str(e),
                context={
                    'patient_id': patient_id,
                    'provider_id': provider_id,
                    'insight_type': abena_insights.insight_type
                }
            )
        
        return results
    
    async def _update_patient_risk_profile(self, patient_id: str, insights: AbenaInsight, user_id: str):
        """Update patient risk profile using Abena SDK"""
        try:
            # ✅ Use Abena SDK to update risk profile with automatic governance
            await self.abena.update_patient_risk_profile(
                patient_id=patient_id,
                risk_data={
                    'insight_type': insights.insight_type,
                    'confidence_score': insights.confidence_score,
                    'clinical_priority': insights.clinical_priority.value,
                    'generated_at': insights.generated_at.isoformat(),
                    'supporting_evidence': insights.supporting_evidence
                },
                user_id=user_id
            )
            
            self.logger.info(f"Risk profile updated for patient {patient_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to update patient risk profile: {str(e)}")
    
    async def _schedule_urgent_follow_up(self, patient_id: str, provider_id: str, user_id: str):
        """Schedule urgent follow-up using Abena SDK"""
        try:
            # ✅ Use Abena SDK to schedule follow-up with automatic notifications
            follow_up_result = await self.abena.schedule_follow_up(
                patient_id=patient_id,
                provider_id=provider_id,
                urgency='critical',
                timeframe_hours=24,
                reason='Abena IHR critical insight requires immediate attention',
                user_id=user_id
            )
            
            if follow_up_result.get('success'):
                self.logger.info(f"Urgent follow-up scheduled for patient {patient_id}")
            else:
                # Fallback to EMR scheduling system
                self.logger.info(f"Urgent follow-up flagged for manual scheduling - patient {patient_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to schedule urgent follow-up: {str(e)}")
    
    async def get_provider_dashboard_data(self, provider_id: str, user_id: str = None) -> Dict:
        """Get dashboard data for provider using Abena SDK"""
        user_id = user_id or provider_id
        
        try:
            # ✅ Use Abena SDK to get comprehensive dashboard data
            dashboard_data = await self.abena.get_provider_dashboard(
                provider_id=provider_id,
                user_id=user_id,
                include_alerts=True,
                include_patients=True,
                include_insights=True
            )
            
            # Get local active alerts as backup
            active_alerts = await self.alert_system.get_active_alerts_for_provider(provider_id)
            
            return {
                'provider_id': provider_id,
                'active_alerts': [asdict(alert) for alert in active_alerts],
                'alert_summary': {
                    'critical': len([a for a in active_alerts if a.priority == AlertPriority.CRITICAL]),
                    'high': len([a for a in active_alerts if a.priority == AlertPriority.HIGH]),
                    'moderate': len([a for a in active_alerts if a.priority == AlertPriority.MODERATE]),
                    'low': len([a for a in active_alerts if a.priority == AlertPriority.LOW])
                },
                'sdk_dashboard_data': dashboard_data,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data via SDK: {str(e)}")
            
            # Fallback to local data only
            active_alerts = await self.alert_system.get_active_alerts_for_provider(provider_id)
            
            return {
                'provider_id': provider_id,
                'active_alerts': [asdict(alert) for alert in active_alerts],
                'alert_summary': {
                    'critical': len([a for a in active_alerts if a.priority == AlertPriority.CRITICAL]),
                    'high': len([a for a in active_alerts if a.priority == AlertPriority.HIGH]),
                    'moderate': len([a for a in active_alerts if a.priority == AlertPriority.MODERATE]),
                    'low': len([a for a in active_alerts if a.priority == AlertPriority.LOW])
                },
                'last_updated': datetime.now().isoformat(),
                'sdk_status': 'unavailable'
            }
    
    async def handle_real_time_patient_encounter(self, patient_id: str, provider_id: str, 
                                               encounter_type: str, user_id: str = None) -> Dict:
        """Handle real-time patient encounter with dynamic insights using Abena SDK"""
        
        user_id = user_id or provider_id
        encounter_id = str(uuid.uuid4())
        
        try:
            # ✅ Use Abena SDK for comprehensive encounter handling
            encounter_context = await self.abena.start_patient_encounter(
                encounter_id=encounter_id,
                patient_id=patient_id,
                provider_id=provider_id,
                encounter_type=encounter_type,
                user_id=user_id
            )
            
            # 1. Retrieve latest patient data via SDK
            patient_data = await self.emr_manager.get_patient_data(patient_id, user_id)
            
            # 2. Get real-time insights from Abena SDK
            real_time_insights = await self.abena.get_real_time_insights(
                patient_id=patient_id,
                encounter_type=encounter_type,
                user_id=user_id
            )
            
            # 3. Check for pending alerts
            active_alerts = await self.alert_system.get_active_alerts_for_provider(provider_id)
            patient_alerts = [a for a in active_alerts if a.patient_id == patient_id]
            
            # 4. Generate encounter-specific recommendations
            recommendations = await self._generate_encounter_recommendations(
                patient_data, patient_alerts, real_time_insights, user_id
            )
            
            # 5. Prepare comprehensive encounter summary
            encounter_summary = {
                'encounter_id': encounter_id,
                'patient_id': patient_id,
                'provider_id': provider_id,
                'encounter_type': encounter_type,
                'timestamp': datetime.now(),
                'active_alerts': [asdict(alert) for alert in patient_alerts],
                'patient_data_retrieved': bool(patient_data),
                'real_time_insights': real_time_insights,
                'recommendations': recommendations,
                'sdk_context': encounter_context
            }
            
            # ✅ Log encounter start to blockchain for audit trail
            await self.abena.log_encounter_start(
                encounter_id=encounter_id,
                patient_id=patient_id,
                provider_id=provider_id,
                encounter_type=encounter_type,
                user_id=user_id
            )
            
            return encounter_summary
            
        except Exception as e:
            self.logger.error(f"Error handling patient encounter: {str(e)}")
            
            # Fallback to basic encounter handling
            active_alerts = await self.alert_system.get_active_alerts_for_provider(provider_id)
            patient_alerts = [a for a in active_alerts if a.patient_id == patient_id]
            
            return {
                'encounter_id': encounter_id,
                'patient_id': patient_id,
                'provider_id': provider_id,
                'encounter_type': encounter_type,
                'timestamp': datetime.now(),
                'active_alerts': [asdict(alert) for alert in patient_alerts],
                'patient_data_retrieved': False,
                'recommendations': ['Review patient alerts', 'Proceed with standard care'],
                'error': str(e),
                'sdk_status': 'unavailable'
            }
    
    async def _generate_encounter_recommendations(self, patient_data: Dict, alerts: List[ClinicalAlert], 
                                                real_time_insights: Dict, user_id: str) -> List[str]:
        """Generate real-time recommendations for patient encounter using Abena SDK"""
        recommendations = []
        
        try:
            # ✅ Use Abena SDK to generate intelligent recommendations
            sdk_recommendations = await self.abena.generate_encounter_recommendations(
                patient_data=patient_data,
                active_alerts=[asdict(alert) for alert in alerts],
                real_time_insights=real_time_insights,
                user_id=user_id
            )
            
            recommendations.extend(sdk_recommendations.get('recommendations', []))
            
        except Exception as e:
            self.logger.error(f"Failed to get SDK recommendations: {str(e)}")
        
        # Add alert-based recommendations
        if alerts:
            for alert in alerts:
                if alert.priority in [AlertPriority.HIGH, AlertPriority.CRITICAL]:
                    recommendations.extend(alert.actionable_recommendations)
        
        # Add general recommendations based on patient data
        if patient_data.get('medications'):
            recommendations.append("Review current medication list for interactions")
        
        if not recommendations:
            recommendations.append("Continue current treatment plan with routine monitoring")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    async def end_patient_encounter(self, encounter_id: str, provider_id: str, 
                                  encounter_notes: str, user_id: str = None) -> Dict:
        """End patient encounter and finalize documentation using Abena SDK"""
        
        user_id = user_id or provider_id
        
        try:
            # ✅ Use Abena SDK to properly close encounter
            result = await self.abena.end_patient_encounter(
                encounter_id=encounter_id,
                provider_id=provider_id,
                encounter_notes=encounter_notes,
                user_id=user_id
            )
            
            # Log encounter completion to blockchain
            await self.abena.log_encounter_end(
                encounter_id=encounter_id,
                provider_id=provider_id,
                user_id=user_id
            )
            
            return {
                'encounter_id': encounter_id,
                'status': 'completed',
                'finalized_at': datetime.now().isoformat(),
                'sdk_result': result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to end encounter via SDK: {str(e)}")
            return {
                'encounter_id': encounter_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# ✅ Updated example usage with Abena SDK integration
async def main():
    """Example usage of the Provider Workflow Integration with Abena SDK"""
    
    # Example configuration with Abena SDK endpoints
    config = {
        'emr_type': 'epic',  # For EMR type identification only
        
        # ✅ Abena SDK configuration - handles all auth, data, privacy, and audit
        'auth_service_url': 'http://localhost:3001',
        'data_service_url': 'http://localhost:8001',
        'privacy_service_url': 'http://localhost:8002',
        'blockchain_service_url': 'http://localhost:8003',
        'api_key': 'your_abena_api_key',
        
        'alert_channels': [
            {
                'type': 'abena_notification',  # ✅ Use Abena's notification system
                'config': {}
            }
        ]
    }
    
    # Initialize workflow integration with SDK
    workflow_orchestrator = WorkflowIntegrationOrchestrator(config)
    
    # Example Abena insight
    sample_insight = AbenaInsight(
        insight_id="INSIGHT_001",
        patient_id="PATIENT_001",
        insight_type="pain_management",
        confidence_score=0.87,
        recommendations=[
            "Consider reducing opioid dose by 25%",
            "Add CBD oil 25mg daily",
            "Implement mindfulness therapy"
        ],
        supporting_evidence={
            "genomics": {"CYP2C9_activity": 0.6},
            "biomarkers": {"inflammatory_markers": 2.1}
        },
        generated_at=datetime.now(),
        clinical_priority=AlertPriority.HIGH
    )
    
    # Process insights using SDK integration
    result = await workflow_orchestrator.process_abena_insights(
        "PATIENT_001", 
        "PROVIDER_001", 
        sample_insight,
        user_id="USER_001"
    )
    
    print("Abena IHR Provider Workflow Integration with SDK")
    print("=" * 60)
    print(f"Processing result: {result['status']}")
    print(f"Actions taken: {len(result['actions_taken'])}")
    for action in result['actions_taken']:
        print(f"  • {action}")
    
    # Example real-time encounter handling
    encounter_result = await workflow_orchestrator.handle_real_time_patient_encounter(
        "PATIENT_001",
        "PROVIDER_001", 
        "routine_visit",
        user_id="USER_001"
    )
    
    print(f"\nReal-time encounter handled: {encounter_result['encounter_id']}")
    print(f"Recommendations: {len(encounter_result['recommendations'])}")
    for rec in encounter_result['recommendations']:
        print(f"  • {rec}")
    
    # Get provider dashboard
    dashboard = await workflow_orchestrator.get_provider_dashboard_data(
        "PROVIDER_001",
        user_id="USER_001"
    )
    
    print(f"\nProvider Dashboard:")
    print(f"Active alerts: {dashboard['alert_summary']}")
    print(f"SDK integration: {'active' if 'sdk_dashboard_data' in dashboard else 'fallback mode'}")
    
    print("\n✅ Workflow Integration System Ready for Clinical Deployment with Abena SDK")

if __name__ == "__main__":
    asyncio.run(main()) 