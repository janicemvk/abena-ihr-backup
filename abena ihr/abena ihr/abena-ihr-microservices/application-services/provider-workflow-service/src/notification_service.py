from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import asyncio
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging

app = FastAPI(title="Provider Notification Service")

class NotificationType(str, Enum):
    TASK_ASSIGNMENT = "task_assignment"
    TASK_OVERDUE = "task_overdue"
    APPOINTMENT_REMINDER = "appointment_reminder"
    EMERGENCY_ALERT = "emergency_alert"
    CLINICAL_ALERT = "clinical_alert"
    SYSTEM_UPDATE = "system_update"
    PATIENT_MESSAGE = "patient_message"
    LAB_RESULT = "lab_result"
    IMAGING_RESULT = "imaging_result"
    MEDICATION_ALERT = "medication_alert"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Notification(BaseModel):
    id: str
    recipient_id: str
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    channels: List[NotificationChannel]
    status: NotificationStatus
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}
    template_id: Optional[str] = None
    context_data: Dict[str, Any] = {}

class NotificationTemplate(BaseModel):
    id: str
    name: str
    notification_type: NotificationType
    title_template: str
    message_template: str
    channels: List[NotificationChannel]
    priority: NotificationPriority
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class NotificationDelivery(BaseModel):
    id: str
    notification_id: str
    channel: NotificationChannel
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = {}

class NotificationPreference(BaseModel):
    id: str
    user_id: str
    notification_type: NotificationType
    channels: List[NotificationChannel]
    is_enabled: bool
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format
    timezone: str = "UTC"
    created_at: datetime
    updated_at: datetime

class NotificationService:
    def __init__(self):
        self.notifications: Dict[str, Notification] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.deliveries: Dict[str, List[NotificationDelivery]] = {}
        self.preferences: Dict[str, List[NotificationPreference]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize default templates
        self._initialize_default_templates()

    def _initialize_default_templates(self):
        default_templates = [
            {
                "name": "Task Assignment",
                "notification_type": NotificationType.TASK_ASSIGNMENT,
                "title_template": "New Task Assigned: {task_title}",
                "message_template": "You have been assigned a new task: {task_title}. Due: {due_date}. Priority: {priority}",
                "channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                "priority": NotificationPriority.NORMAL
            },
            {
                "name": "Task Overdue",
                "notification_type": NotificationType.TASK_OVERDUE,
                "title_template": "Task Overdue: {task_title}",
                "message_template": "The task '{task_title}' is overdue. Please complete it as soon as possible.",
                "channels": [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.IN_APP],
                "priority": NotificationPriority.HIGH
            },
            {
                "name": "Emergency Alert",
                "notification_type": NotificationType.EMERGENCY_ALERT,
                "title_template": "EMERGENCY: {alert_title}",
                "message_template": "Emergency alert: {alert_message}. Patient: {patient_name}. Immediate attention required.",
                "channels": [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.PUSH],
                "priority": NotificationPriority.CRITICAL
            },
            {
                "name": "Appointment Reminder",
                "notification_type": NotificationType.APPOINTMENT_REMINDER,
                "title_template": "Appointment Reminder: {appointment_type}",
                "message_template": "Reminder: You have a {appointment_type} appointment with {patient_name} at {appointment_time}.",
                "channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                "priority": NotificationPriority.NORMAL
            }
        ]
        
        for template_data in default_templates:
            self.create_notification_template(**template_data)

    def create_notification(self, recipient_id: str, notification_type: NotificationType,
                          title: str, message: str, channels: List[NotificationChannel],
                          priority: NotificationPriority = NotificationPriority.NORMAL,
                          scheduled_at: datetime = None, template_id: str = None,
                          context_data: Dict[str, Any] = None) -> Notification:
        notification_id = str(uuid.uuid4())
        
        notification = Notification(
            id=notification_id,
            recipient_id=recipient_id,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            channels=channels,
            status=NotificationStatus.PENDING,
            scheduled_at=scheduled_at,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            template_id=template_id,
            context_data=context_data or {},
            metadata={}
        )
        
        self.notifications[notification_id] = notification
        self.deliveries[notification_id] = []
        
        # Create delivery records for each channel
        for channel in channels:
            delivery = NotificationDelivery(
                id=str(uuid.uuid4()),
                notification_id=notification_id,
                channel=channel,
                status=NotificationStatus.PENDING,
                metadata={}
            )
            self.deliveries[notification_id].append(delivery)
        
        return notification

    def create_notification_from_template(self, template_id: str, recipient_id: str,
                                        context_data: Dict[str, Any]) -> Notification:
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        # Render template with context data
        title = template.title_template.format(**context_data)
        message = template.message_template.format(**context_data)
        
        return self.create_notification(
            recipient_id=recipient_id,
            notification_type=template.notification_type,
            title=title,
            message=message,
            channels=template.channels,
            priority=template.priority,
            template_id=template_id,
            context_data=context_data
        )

    def create_notification_template(self, name: str, notification_type: NotificationType,
                                   title_template: str, message_template: str,
                                   channels: List[NotificationChannel],
                                   priority: NotificationPriority) -> NotificationTemplate:
        template_id = str(uuid.uuid4())
        
        template = NotificationTemplate(
            id=template_id,
            name=name,
            notification_type=notification_type,
            title_template=title_template,
            message_template=message_template,
            channels=channels,
            priority=priority,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        self.templates[template_id] = template
        return template

    async def send_notification(self, notification_id: str) -> bool:
        if notification_id not in self.notifications:
            raise ValueError(f"Notification {notification_id} not found")
        
        notification = self.notifications[notification_id]
        
        # Check if notification should be sent based on preferences
        if not self._should_send_notification(notification):
            notification.status = NotificationStatus.CANCELLED
            notification.updated_at = datetime.now()
            return False
        
        # Send through each channel
        success = True
        for delivery in self.deliveries[notification_id]:
            try:
                await self._send_via_channel(notification, delivery)
                delivery.status = NotificationStatus.SENT
                delivery.sent_at = datetime.now()
            except Exception as e:
                delivery.status = NotificationStatus.FAILED
                delivery.error_message = str(e)
                delivery.retry_count += 1
                success = False
                self.logger.error(f"Failed to send notification {notification_id} via {delivery.channel}: {e}")
        
        notification.status = NotificationStatus.SENT if success else NotificationStatus.FAILED
        notification.sent_at = datetime.now()
        notification.updated_at = datetime.now()
        
        return success

    def _should_send_notification(self, notification: Notification) -> bool:
        # Check user preferences
        user_prefs = self.preferences.get(notification.recipient_id, [])
        
        # Find preference for this notification type
        for pref in user_prefs:
            if pref.notification_type == notification.notification_type:
                if not pref.is_enabled:
                    return False
                
                # Check quiet hours
                if pref.quiet_hours_start and pref.quiet_hours_end:
                    current_time = datetime.now()
                    # Simple quiet hours check (could be enhanced with timezone support)
                    current_hour = current_time.hour
                    start_hour = int(pref.quiet_hours_start.split(':')[0])
                    end_hour = int(pref.quiet_hours_end.split(':')[0])
                    
                    if start_hour <= current_hour <= end_hour:
                        return False
                
                break
        
        return True

    async def _send_via_channel(self, notification: Notification, delivery: NotificationDelivery):
        if delivery.channel == NotificationChannel.EMAIL:
            await self._send_email(notification)
        elif delivery.channel == NotificationChannel.SMS:
            await self._send_sms(notification)
        elif delivery.channel == NotificationChannel.PUSH:
            await self._send_push_notification(notification)
        elif delivery.channel == NotificationChannel.IN_APP:
            await self._send_in_app_notification(notification)
        elif delivery.channel == NotificationChannel.WEBHOOK:
            await self._send_webhook(notification)
        elif delivery.channel == NotificationChannel.SLACK:
            await self._send_slack(notification)
        elif delivery.channel == NotificationChannel.TEAMS:
            await self._send_teams(notification)

    async def _send_email(self, notification: Notification):
        # Placeholder for email sending logic
        # In production, integrate with email service (SendGrid, AWS SES, etc.)
        self.logger.info(f"Sending email to {notification.recipient_id}: {notification.title}")

    async def _send_sms(self, notification: Notification):
        # Placeholder for SMS sending logic
        # In production, integrate with SMS service (Twilio, AWS SNS, etc.)
        self.logger.info(f"Sending SMS to {notification.recipient_id}: {notification.title}")

    async def _send_push_notification(self, notification: Notification):
        # Placeholder for push notification logic
        # In production, integrate with push notification service (Firebase, etc.)
        self.logger.info(f"Sending push notification to {notification.recipient_id}: {notification.title}")

    async def _send_in_app_notification(self, notification: Notification):
        # Placeholder for in-app notification logic
        # In production, this would store the notification for the app to fetch
        self.logger.info(f"Storing in-app notification for {notification.recipient_id}: {notification.title}")

    async def _send_webhook(self, notification: Notification):
        # Placeholder for webhook sending logic
        # In production, make HTTP POST to configured webhook URL
        self.logger.info(f"Sending webhook for {notification.recipient_id}: {notification.title}")

    async def _send_slack(self, notification: Notification):
        # Placeholder for Slack integration
        # In production, post to Slack channel via Slack API
        self.logger.info(f"Sending Slack message for {notification.recipient_id}: {notification.title}")

    async def _send_teams(self, notification: Notification):
        # Placeholder for Microsoft Teams integration
        # In production, post to Teams channel via Teams webhook
        self.logger.info(f"Sending Teams message for {notification.recipient_id}: {notification.title}")

    def mark_notification_read(self, notification_id: str, user_id: str) -> Notification:
        if notification_id not in self.notifications:
            raise ValueError(f"Notification {notification_id} not found")
        
        notification = self.notifications[notification_id]
        if notification.recipient_id != user_id:
            raise ValueError("User can only mark their own notifications as read")
        
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.now()
        notification.updated_at = datetime.now()
        
        return notification

    def get_user_notifications(self, user_id: str, status: NotificationStatus = None,
                             limit: int = 50) -> List[Notification]:
        notifications = [n for n in self.notifications.values() if n.recipient_id == user_id]
        
        if status:
            notifications = [n for n in notifications if n.status == status]
        
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        return notifications[:limit]

    def get_unread_notifications(self, user_id: str) -> List[Notification]:
        return self.get_user_notifications(user_id, NotificationStatus.SENT)

    def set_notification_preference(self, user_id: str, notification_type: NotificationType,
                                  channels: List[NotificationChannel], is_enabled: bool,
                                  quiet_hours_start: str = None, quiet_hours_end: str = None,
                                  timezone: str = "UTC") -> NotificationPreference:
        preference_id = str(uuid.uuid4())
        
        preference = NotificationPreference(
            id=preference_id,
            user_id=user_id,
            notification_type=notification_type,
            channels=channels,
            is_enabled=is_enabled,
            quiet_hours_start=quiet_hours_start,
            quiet_hours_end=quiet_hours_end,
            timezone=timezone,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if user_id not in self.preferences:
            self.preferences[user_id] = []
        
        # Update existing preference or add new one
        existing_pref = None
        for pref in self.preferences[user_id]:
            if pref.notification_type == notification_type:
                existing_pref = pref
                break
        
        if existing_pref:
            existing_pref.channels = channels
            existing_pref.is_enabled = is_enabled
            existing_pref.quiet_hours_start = quiet_hours_start
            existing_pref.quiet_hours_end = quiet_hours_end
            existing_pref.timezone = timezone
            existing_pref.updated_at = datetime.now()
            return existing_pref
        else:
            self.preferences[user_id].append(preference)
            return preference

    def get_notification_statistics(self, user_id: str = None) -> Dict[str, Any]:
        notifications = self.notifications.values()
        if user_id:
            notifications = [n for n in notifications if n.recipient_id == user_id]
        
        total_notifications = len(notifications)
        sent_notifications = len([n for n in notifications if n.status == NotificationStatus.SENT])
        read_notifications = len([n for n in notifications if n.status == NotificationStatus.READ])
        failed_notifications = len([n for n in notifications if n.status == NotificationStatus.FAILED])
        
        return {
            "total_notifications": total_notifications,
            "sent_notifications": sent_notifications,
            "read_notifications": read_notifications,
            "failed_notifications": failed_notifications,
            "delivery_rate": (sent_notifications / total_notifications * 100) if total_notifications > 0 else 0,
            "read_rate": (read_notifications / sent_notifications * 100) if sent_notifications > 0 else 0
        }

notification_service = NotificationService()

@app.post("/notifications")
async def create_notification(notification_data: Dict[str, Any]):
    try:
        notification = notification_service.create_notification(
            recipient_id=notification_data["recipient_id"],
            notification_type=NotificationType(notification_data["notification_type"]),
            title=notification_data["title"],
            message=notification_data["message"],
            channels=[NotificationChannel(c) for c in notification_data["channels"]],
            priority=NotificationPriority(notification_data.get("priority", "normal")),
            scheduled_at=datetime.fromisoformat(notification_data["scheduled_at"]) if notification_data.get("scheduled_at") else None,
            template_id=notification_data.get("template_id"),
            context_data=notification_data.get("context_data", {})
        )
        return {"notification": notification}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/notifications/from-template/{template_id}")
async def create_notification_from_template(template_id: str, notification_data: Dict[str, Any]):
    try:
        notification = notification_service.create_notification_from_template(
            template_id=template_id,
            recipient_id=notification_data["recipient_id"],
            context_data=notification_data["context_data"]
        )
        return {"notification": notification}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/notifications/{notification_id}/send")
async def send_notification(notification_id: str):
    try:
        success = await notification_service.send_notification(notification_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, user_id: str):
    try:
        notification = notification_service.mark_notification_read(notification_id, user_id)
        return {"notification": notification}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}/notifications")
async def get_user_notifications(user_id: str, status: NotificationStatus = None, limit: int = 50):
    notifications = notification_service.get_user_notifications(user_id, status, limit)
    return {"notifications": notifications}

@app.get("/users/{user_id}/notifications/unread")
async def get_unread_notifications(user_id: str):
    notifications = notification_service.get_unread_notifications(user_id)
    return {"notifications": notifications}

@app.post("/notification-templates")
async def create_notification_template(template_data: Dict[str, Any]):
    try:
        template = notification_service.create_notification_template(
            name=template_data["name"],
            notification_type=NotificationType(template_data["notification_type"]),
            title_template=template_data["title_template"],
            message_template=template_data["message_template"],
            channels=[NotificationChannel(c) for c in template_data["channels"]],
            priority=NotificationPriority(template_data["priority"])
        )
        return {"template": template}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/users/{user_id}/notification-preferences")
async def set_notification_preference(user_id: str, preference_data: Dict[str, Any]):
    try:
        preference = notification_service.set_notification_preference(
            user_id=user_id,
            notification_type=NotificationType(preference_data["notification_type"]),
            channels=[NotificationChannel(c) for c in preference_data["channels"]],
            is_enabled=preference_data["is_enabled"],
            quiet_hours_start=preference_data.get("quiet_hours_start"),
            quiet_hours_end=preference_data.get("quiet_hours_end"),
            timezone=preference_data.get("timezone", "UTC")
        )
        return {"preference": preference}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/notifications/statistics")
async def get_notification_statistics(user_id: str = None):
    stats = notification_service.get_notification_statistics(user_id)
    return {"statistics": stats} 