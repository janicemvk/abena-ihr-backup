# =============================================================================
# 3. INTEGRATION MONITORING SYSTEM
# =============================================================================

import asyncio
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import redis

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Alert:
    id: str
    alert_type: str
    severity: AlertSeverity
    source: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]
    resolved: bool = False

class NotificationChannel(ABC):
    """Abstract base class for notification channels"""
    
    @abstractmethod
    async def send_notification(self, alert: Alert) -> bool:
        pass

class EmailNotificationChannel(NotificationChannel):
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str,
                 from_email: str, to_emails: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
        
        # Email template
        self.email_template = Template("""
        <html>
        <body>
            <h2>🚨 Abena IHR Alert - {{ alert.severity.value.upper() }}</h2>
            
            <div style="background-color: {% if alert.severity.value == 'critical' %}#ffebee{% elif alert.severity.value == 'high' %}#fff3e0{% else %}#f3e5f5{% endif %}; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>{{ alert.alert_type }}</h3>
                <p><strong>Source:</strong> {{ alert.source }}</p>
                <p><strong>Time:</strong> {{ alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') }}</p>
                <p><strong>Message:</strong> {{ alert.message }}</p>
            </div>
            
            {% if alert.metadata %}
            <h4>Additional Details:</h4>
            <ul>
                {% for key, value in alert.metadata.items() %}
                <li><strong>{{ key }}:</strong> {{ value }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            
            <hr>
            <p style="color: #666; font-size: 12px;">
                This is an automated alert from Abena IHR Intelligence Layer.<br>
                Please investigate and resolve the issue promptly.
            </p>
        </body>
        </html>
        """)
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[ABENA IHR] {alert.severity.value.upper()} Alert: {alert.alert_type}"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            
            # Generate email content
            html_content = self.email_template.render(alert=alert)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email notification: {str(e)}")
            return False

class SlackNotificationChannel(NotificationChannel):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send Slack notification"""
        try:
            import httpx
            
            # Map severity to color
            color_map = {
                AlertSeverity.LOW: "#36a64f",      # Green
                AlertSeverity.MEDIUM: "#ff9500",   # Orange
                AlertSeverity.HIGH: "#ff6b6b",     # Red
                AlertSeverity.CRITICAL: "#8b0000"  # Dark red
            }
            
            # Create Slack payload
            payload = {
                "attachments": [{
                    "color": color_map.get(alert.severity, "#36a64f"),
                    "title": f"🚨 {alert.severity.value.upper()} Alert: {alert.alert_type}",
                    "fields": [
                        {
                            "title": "Source",
                            "value": alert.source,
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                            "short": True
                        },
                        {
                            "title": "Message",
                            "value": alert.message,
                            "short": False
                        }
                    ],
                    "footer": "Abena IHR Intelligence Layer",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }
            
            # Add metadata if available
            if alert.metadata:
                metadata_text = "\n".join([f"• {k}: {v}" for k, v in alert.metadata.items()])
                payload["attachments"][0]["fields"].append({
                    "title": "Details",
                    "value": metadata_text,
                    "short": False
                })
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                return response.status_code == 200
                
        except Exception as e:
            logging.error(f"Failed to send Slack notification: {str(e)}")
            return False

class AlertManager:
    def __init__(self, redis_client: redis.Redis, db_session):
        self.redis_client = redis_client
        self.db_session = db_session
        self.notification_channels = []
        self.alert_rules = {}
        
    def add_notification_channel(self, channel: NotificationChannel):
        """Add a notification channel (email, Slack, etc.)"""
        self.notification_channels.append(channel)
    
    def add_alert_rule(self, rule_name: str, condition: Callable, severity: AlertSeverity, 
                      cooldown_minutes: int = 15):
        """Add an alert rule with condition function"""
        self.alert_rules[rule_name] = {
            'condition': condition,
            'severity': severity,
            'cooldown_minutes': cooldown_minutes,
            'last_triggered': None
        }
    
    async def check_alert_conditions(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check all alert conditions and return triggered alerts"""
        triggered_alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            try:
                # Check cooldown period
                if rule['last_triggered']:
                    cooldown_end = rule['last_triggered'] + timedelta(minutes=rule['cooldown_minutes'])
                    if datetime.utcnow() < cooldown_end:
                        continue
                
                # Evaluate condition
                if rule['condition'](metrics):
                    alert = Alert(
                        id=str(uuid.uuid4()),
                        alert_type=rule_name,
                        severity=rule['severity'],
                        source="intelligence_layer",
                        message=f"Alert condition triggered: {rule_name}",
                        timestamp=datetime.utcnow(),
                        metadata=metrics
                    )
                    
                    triggered_alerts.append(alert)
                    rule['last_triggered'] = datetime.utcnow()
                    
            except Exception as e:
                logging.error(f"Error evaluating alert rule {rule_name}: {str(e)}")
        
        return triggered_alerts
    
    async def send_alert(self, alert: Alert):
        """Send alert through all notification channels"""
        # Store alert in database
        db = next(self.db_session())
        from intelligence_layer import AlertLog
        alert_record = AlertLog(
            alert_type=alert.alert_type,
            severity=alert.severity.value,
            source=alert.source,
            message=alert.message,
            timestamp=alert.timestamp
        )
        db.add(alert_record)
        db.commit()
        
        # Cache alert in Redis for real-time access
        alert_key = f"alert:{alert.id}"
        self.redis_client.setex(alert_key, 86400, json.dumps(asdict(alert)))
        
        # Send through notification channels
        for channel in self.notification_channels:
            try:
                await channel.send_notification(alert)
            except Exception as e:
                logging.error(f"Failed to send alert via {channel.__class__.__name__}: {str(e)}") 