# Mock Real-Time Alert System - Updated to use Abena SDK
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.core.abena_sdk import AbenaSDK

class RealTimeAlertSystem:
    """Real-Time Alert System using Abena SDK for data access and alert management"""
    
    def __init__(self, abena_sdk: AbenaSDK):
        self.abena = abena_sdk
        self.active_alerts = {}
        self.alert_rules = {
            'high_pain': self._check_high_pain,
            'adverse_event': self._check_adverse_event,
            'medication_interaction': self._check_medication_interaction,
            'vital_signs_abnormal': self._check_vital_signs
        }
    
    async def create_alert(self, patient_id: str, alert_type: str, alert_data: Dict[str, Any]) -> str:
        """Create alert using Abena SDK"""
        try:
            # Get patient data through Abena SDK
            patient_data = await self.abena.get_patient_data(patient_id, 'alert_creation')
            
            alert_id = f"alert_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            alert = {
                'alert_id': alert_id,
                'patient_id': patient_id,
                'type': alert_type,
                'data': alert_data,
                'created_at': datetime.now(),
                'status': 'active',
                'acknowledged': False,
                'acknowledged_by': None,
                'acknowledged_at': None
            }
            
            # Store alert locally
            self.active_alerts[alert_id] = alert
            
            # Create alert through Abena SDK (handles blockchain and audit)
            await self.abena.create_alert({
                'alert_id': alert_id,
                'patient_id': patient_id,
                'type': alert_type,
                'severity': alert_data.get('severity', 'medium'),
                'message': alert_data.get('message', 'Alert created')
            })
            
            return alert_id
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'alert_creation_failure',
                'message': f'Alert creation failed: {str(e)}',
                'severity': 'high'
            })
            return ""
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge alert using Abena SDK"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert['acknowledged'] = True
            alert['acknowledged_by'] = user_id
            alert['acknowledged_at'] = datetime.now()
            alert['status'] = 'acknowledged'
            
            # Log acknowledgment through Abena SDK
            await self.abena.save_treatment_plan(alert['patient_id'], {
                'action': 'alert_acknowledged',
                'alert_id': alert_id,
                'user_id': user_id,
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
    
    async def get_active_alerts(self, patient_id: str = None) -> List[Dict[str, Any]]:
        """Get active alerts using Abena SDK"""
        try:
            if patient_id:
                # Get patient-specific alerts
                patient_data = await self.abena.get_patient_data(patient_id, 'alert_retrieval')
                alerts = [alert for alert in self.active_alerts.values() 
                         if alert['patient_id'] == patient_id and alert['status'] == 'active']
            else:
                # Get all active alerts
                alerts = [alert for alert in self.active_alerts.values() 
                         if alert['status'] == 'active']
            
            return alerts
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'alert_retrieval_failure',
                'message': f'Alert retrieval failed: {str(e)}',
                'severity': 'medium'
            })
            return []
    
    async def check_patient_alerts(self, patient_id: str, patient_data: Dict[str, Any]) -> List[str]:
        """Check for potential alerts based on patient data using Abena SDK"""
        try:
            # Get patient data through Abena SDK
            full_patient_data = await self.abena.get_patient_data(patient_id, 'alert_monitoring')
            
            triggered_alerts = []
            
            # Check each alert rule
            for rule_name, rule_func in self.alert_rules.items():
                if rule_func(full_patient_data):
                    alert_id = await self.create_alert(patient_id, rule_name, {
                        'severity': 'medium',
                        'message': f'{rule_name.replace("_", " ").title()} detected'
                    })
                    if alert_id:
                        triggered_alerts.append(alert_id)
            
            return triggered_alerts
            
        except Exception as e:
            await self.abena.create_alert({
                'type': 'alert_monitoring_failure',
                'message': f'Alert monitoring failed: {str(e)}',
                'severity': 'high'
            })
            return []
    
    def _check_high_pain(self, patient_data: Dict[str, Any]) -> bool:
        """Check for high pain levels"""
        pain_scores = patient_data.get('pain_scores', [])
        return any(score > 8.0 for score in pain_scores) if pain_scores else False
    
    def _check_adverse_event(self, patient_data: Dict[str, Any]) -> bool:
        """Check for adverse events"""
        # Mock adverse event detection
        return False  # No adverse events in mock data
    
    def _check_medication_interaction(self, patient_data: Dict[str, Any]) -> bool:
        """Check for medication interactions"""
        medications = patient_data.get('current_medications', [])
        return len(medications) > 5  # Polypharmacy alert
    
    def _check_vital_signs(self, patient_data: Dict[str, Any]) -> bool:
        """Check for abnormal vital signs"""
        # Mock vital signs check
        return False  # No abnormal vital signs in mock data
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total_alerts = len(self.active_alerts)
        active_alerts = len([a for a in self.active_alerts.values() if a['status'] == 'active'])
        acknowledged_alerts = len([a for a in self.active_alerts.values() if a['acknowledged']])
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'acknowledged_alerts': acknowledged_alerts,
            'acknowledgment_rate': acknowledged_alerts / total_alerts if total_alerts > 0 else 0
        } 