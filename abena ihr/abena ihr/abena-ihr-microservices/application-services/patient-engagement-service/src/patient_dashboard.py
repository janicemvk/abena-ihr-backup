from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

app = FastAPI(title="Patient Dashboard Service")

class HealthStatus(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class ActivityType(str, Enum):
    APPOINTMENT = "appointment"
    MEDICATION = "medication"
    LAB_RESULT = "lab_result"
    VITAL_SIGN = "vital_sign"
    MESSAGE = "message"
    DOCUMENT = "document"
    ALERT = "alert"

class DashboardWidget(str, Enum):
    UPCOMING_APPOINTMENTS = "upcoming_appointments"
    RECENT_LAB_RESULTS = "recent_lab_results"
    MEDICATION_SCHEDULE = "medication_schedule"
    VITAL_TRENDS = "vital_trends"
    HEALTH_ALERTS = "health_alerts"
    MESSAGES = "messages"
    DOCUMENTS = "documents"
    CARE_TEAM = "care_team"

class PatientDashboard(BaseModel):
    id: str
    patient_id: str
    widgets: List[DashboardWidget]
    layout_config: Dict[str, Any]
    last_updated: datetime
    created_at: datetime
    metadata: Dict[str, Any] = {}

class HealthOverview(BaseModel):
    patient_id: str
    overall_status: HealthStatus
    last_assessment_date: datetime
    risk_factors: List[str]
    chronic_conditions: List[str]
    allergies: List[str]
    current_medications: int
    upcoming_appointments: int
    pending_tasks: int
    unread_messages: int
    recent_alerts: int
    metadata: Dict[str, Any] = {}

class PatientActivity(BaseModel):
    id: str
    patient_id: str
    activity_type: ActivityType
    title: str
    description: str
    timestamp: datetime
    status: str
    priority: str
    related_entity_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class HealthInsight(BaseModel):
    id: str
    patient_id: str
    insight_type: str
    title: str
    description: str
    severity: str
    actionable: bool
    action_url: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class PatientDashboardService:
    def __init__(self):
        self.dashboards: Dict[str, PatientDashboard] = {}
        self.health_overviews: Dict[str, HealthOverview] = {}
        self.activities: Dict[str, List[PatientActivity]] = {}
        self.insights: Dict[str, List[HealthInsight]] = {}
        self.widget_data: Dict[str, Dict] = {}

    def create_dashboard(self, patient_id: str, widgets: List[DashboardWidget] = None) -> PatientDashboard:
        dashboard_id = str(uuid.uuid4())
        
        default_widgets = [
            DashboardWidget.UPCOMING_APPOINTMENTS,
            DashboardWidget.RECENT_LAB_RESULTS,
            DashboardWidget.MEDICATION_SCHEDULE,
            DashboardWidget.VITAL_TRENDS,
            DashboardWidget.HEALTH_ALERTS,
            DashboardWidget.MESSAGES
        ]
        
        dashboard = PatientDashboard(
            id=dashboard_id,
            patient_id=patient_id,
            widgets=widgets or default_widgets,
            layout_config={
                "columns": 3,
                "widgets": {}
            },
            last_updated=datetime.now(),
            created_at=datetime.now(),
            metadata={}
        )
        
        self.dashboards[dashboard_id] = dashboard
        self.activities[patient_id] = []
        self.insights[patient_id] = []
        
        return dashboard

    def get_dashboard(self, patient_id: str) -> Optional[PatientDashboard]:
        for dashboard in self.dashboards.values():
            if dashboard.patient_id == patient_id:
                return dashboard
        return None

    def update_dashboard_layout(self, patient_id: str, layout_config: Dict[str, Any]) -> PatientDashboard:
        dashboard = self.get_dashboard(patient_id)
        if not dashboard:
            raise ValueError(f"Dashboard for patient {patient_id} not found")
        
        dashboard.layout_config = layout_config
        dashboard.last_updated = datetime.now()
        
        return dashboard

    def add_widget(self, patient_id: str, widget: DashboardWidget) -> PatientDashboard:
        dashboard = self.get_dashboard(patient_id)
        if not dashboard:
            raise ValueError(f"Dashboard for patient {patient_id} not found")
        
        if widget not in dashboard.widgets:
            dashboard.widgets.append(widget)
            dashboard.last_updated = datetime.now()
        
        return dashboard

    def remove_widget(self, patient_id: str, widget: DashboardWidget) -> PatientDashboard:
        dashboard = self.get_dashboard(patient_id)
        if not dashboard:
            raise ValueError(f"Dashboard for patient {patient_id} not found")
        
        if widget in dashboard.widgets:
            dashboard.widgets.remove(widget)
            dashboard.last_updated = datetime.now()
        
        return dashboard

    def create_health_overview(self, patient_id: str, health_data: Dict[str, Any]) -> HealthOverview:
        overview = HealthOverview(
            patient_id=patient_id,
            overall_status=HealthStatus(health_data.get("overall_status", "good")),
            last_assessment_date=datetime.fromisoformat(health_data.get("last_assessment_date", datetime.now().isoformat())),
            risk_factors=health_data.get("risk_factors", []),
            chronic_conditions=health_data.get("chronic_conditions", []),
            allergies=health_data.get("allergies", []),
            current_medications=health_data.get("current_medications", 0),
            upcoming_appointments=health_data.get("upcoming_appointments", 0),
            pending_tasks=health_data.get("pending_tasks", 0),
            unread_messages=health_data.get("unread_messages", 0),
            recent_alerts=health_data.get("recent_alerts", 0),
            metadata=health_data.get("metadata", {})
        )
        
        self.health_overviews[patient_id] = overview
        return overview

    def update_health_overview(self, patient_id: str, updates: Dict[str, Any]) -> HealthOverview:
        if patient_id not in self.health_overviews:
            raise ValueError(f"Health overview for patient {patient_id} not found")
        
        overview = self.health_overviews[patient_id]
        
        for key, value in updates.items():
            if hasattr(overview, key):
                setattr(overview, key, value)
        
        return overview

    def add_activity(self, patient_id: str, activity_type: ActivityType, title: str,
                    description: str, status: str = "active", priority: str = "normal",
                    related_entity_id: str = None) -> PatientActivity:
        activity = PatientActivity(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            activity_type=activity_type,
            title=title,
            description=description,
            timestamp=datetime.now(),
            status=status,
            priority=priority,
            related_entity_id=related_entity_id,
            metadata={}
        )
        
        if patient_id not in self.activities:
            self.activities[patient_id] = []
        
        self.activities[patient_id].append(activity)
        return activity

    def get_recent_activities(self, patient_id: str, limit: int = 10) -> List[PatientActivity]:
        activities = self.activities.get(patient_id, [])
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:limit]

    def get_activities_by_type(self, patient_id: str, activity_type: ActivityType) -> List[PatientActivity]:
        activities = self.activities.get(patient_id, [])
        return [activity for activity in activities if activity.activity_type == activity_type]

    def create_health_insight(self, patient_id: str, insight_type: str, title: str,
                            description: str, severity: str = "info", actionable: bool = False,
                            action_url: str = None, expires_at: datetime = None) -> HealthInsight:
        insight = HealthInsight(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            insight_type=insight_type,
            title=title,
            description=description,
            severity=severity,
            actionable=actionable,
            action_url=action_url,
            created_at=datetime.now(),
            expires_at=expires_at,
            metadata={}
        )
        
        if patient_id not in self.insights:
            self.insights[patient_id] = []
        
        self.insights[patient_id].append(insight)
        return insight

    def get_active_insights(self, patient_id: str) -> List[HealthInsight]:
        insights = self.insights.get(patient_id, [])
        now = datetime.now()
        
        active_insights = []
        for insight in insights:
            if insight.expires_at is None or insight.expires_at > now:
                active_insights.append(insight)
        
        return sorted(active_insights, key=lambda x: x.created_at, reverse=True)

    def get_widget_data(self, patient_id: str, widget: DashboardWidget) -> Dict[str, Any]:
        if patient_id not in self.widget_data:
            self.widget_data[patient_id] = {}
        
        if widget not in self.widget_data[patient_id]:
            # Generate default widget data based on widget type
            self.widget_data[patient_id][widget] = self._generate_widget_data(patient_id, widget)
        
        return self.widget_data[patient_id][widget]

    def _generate_widget_data(self, patient_id: str, widget: DashboardWidget) -> Dict[str, Any]:
        if widget == DashboardWidget.UPCOMING_APPOINTMENTS:
            return {
                "appointments": [],
                "next_appointment": None,
                "total_count": 0
            }
        elif widget == DashboardWidget.RECENT_LAB_RESULTS:
            return {
                "results": [],
                "abnormal_count": 0,
                "pending_count": 0
            }
        elif widget == DashboardWidget.MEDICATION_SCHEDULE:
            return {
                "medications": [],
                "due_soon": [],
                "missed_doses": 0
            }
        elif widget == DashboardWidget.VITAL_TRENDS:
            return {
                "vitals": [],
                "trends": {},
                "last_updated": None
            }
        elif widget == DashboardWidget.HEALTH_ALERTS:
            return {
                "alerts": [],
                "critical_count": 0,
                "warning_count": 0
            }
        elif widget == DashboardWidget.MESSAGES:
            return {
                "messages": [],
                "unread_count": 0,
                "urgent_count": 0
            }
        elif widget == DashboardWidget.DOCUMENTS:
            return {
                "documents": [],
                "recent_uploads": [],
                "total_count": 0
            }
        elif widget == DashboardWidget.CARE_TEAM:
            return {
                "team_members": [],
                "primary_provider": None,
                "specialists": []
            }
        else:
            return {}

    def update_widget_data(self, patient_id: str, widget: DashboardWidget, data: Dict[str, Any]):
        if patient_id not in self.widget_data:
            self.widget_data[patient_id] = {}
        
        self.widget_data[patient_id][widget] = data

    def get_dashboard_summary(self, patient_id: str) -> Dict[str, Any]:
        dashboard = self.get_dashboard(patient_id)
        health_overview = self.health_overviews.get(patient_id)
        recent_activities = self.get_recent_activities(patient_id, 5)
        active_insights = self.get_active_insights(patient_id)
        
        return {
            "dashboard": dashboard,
            "health_overview": health_overview,
            "recent_activities": recent_activities,
            "active_insights": active_insights,
            "widget_count": len(dashboard.widgets) if dashboard else 0,
            "last_updated": dashboard.last_updated if dashboard else None
        }

    def clear_expired_insights(self, patient_id: str = None):
        now = datetime.now()
        
        if patient_id:
            insights = self.insights.get(patient_id, [])
            self.insights[patient_id] = [insight for insight in insights 
                                       if insight.expires_at is None or insight.expires_at > now]
        else:
            for patient_id in self.insights:
                insights = self.insights[patient_id]
                self.insights[patient_id] = [insight for insight in insights 
                                           if insight.expires_at is None or insight.expires_at > now]

patient_dashboard_service = PatientDashboardService()

@app.post("/dashboards")
async def create_dashboard(dashboard_data: Dict[str, Any]):
    try:
        dashboard = patient_dashboard_service.create_dashboard(
            patient_id=dashboard_data["patient_id"],
            widgets=[DashboardWidget(w) for w in dashboard_data.get("widgets", [])]
        )
        return {"dashboard": dashboard}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/dashboard")
async def get_dashboard(patient_id: str):
    dashboard = patient_dashboard_service.get_dashboard(patient_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {"dashboard": dashboard}

@app.put("/patients/{patient_id}/dashboard/layout")
async def update_dashboard_layout(patient_id: str, layout_config: Dict[str, Any]):
    try:
        dashboard = patient_dashboard_service.update_dashboard_layout(patient_id, layout_config)
        return {"dashboard": dashboard}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/patients/{patient_id}/dashboard/widgets")
async def add_widget(patient_id: str, widget: DashboardWidget):
    try:
        dashboard = patient_dashboard_service.add_widget(patient_id, widget)
        return {"dashboard": dashboard}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/patients/{patient_id}/dashboard/widgets/{widget}")
async def remove_widget(patient_id: str, widget: DashboardWidget):
    try:
        dashboard = patient_dashboard_service.remove_widget(patient_id, widget)
        return {"dashboard": dashboard}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/patients/{patient_id}/health-overview")
async def create_health_overview(patient_id: str, health_data: Dict[str, Any]):
    try:
        overview = patient_dashboard_service.create_health_overview(patient_id, health_data)
        return {"health_overview": overview}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/patients/{patient_id}/health-overview")
async def update_health_overview(patient_id: str, updates: Dict[str, Any]):
    try:
        overview = patient_dashboard_service.update_health_overview(patient_id, updates)
        return {"health_overview": overview}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/patients/{patient_id}/health-overview")
async def get_health_overview(patient_id: str):
    overview = patient_dashboard_service.health_overviews.get(patient_id)
    if not overview:
        raise HTTPException(status_code=404, detail="Health overview not found")
    return {"health_overview": overview}

@app.post("/patients/{patient_id}/activities")
async def add_activity(patient_id: str, activity_data: Dict[str, Any]):
    try:
        activity = patient_dashboard_service.add_activity(
            patient_id=patient_id,
            activity_type=ActivityType(activity_data["activity_type"]),
            title=activity_data["title"],
            description=activity_data["description"],
            status=activity_data.get("status", "active"),
            priority=activity_data.get("priority", "normal"),
            related_entity_id=activity_data.get("related_entity_id")
        )
        return {"activity": activity}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/activities")
async def get_recent_activities(patient_id: str, limit: int = 10):
    activities = patient_dashboard_service.get_recent_activities(patient_id, limit)
    return {"activities": activities}

@app.get("/patients/{patient_id}/activities/{activity_type}")
async def get_activities_by_type(patient_id: str, activity_type: ActivityType):
    activities = patient_dashboard_service.get_activities_by_type(patient_id, activity_type)
    return {"activities": activities}

@app.post("/patients/{patient_id}/insights")
async def create_health_insight(patient_id: str, insight_data: Dict[str, Any]):
    try:
        insight = patient_dashboard_service.create_health_insight(
            patient_id=patient_id,
            insight_type=insight_data["insight_type"],
            title=insight_data["title"],
            description=insight_data["description"],
            severity=insight_data.get("severity", "info"),
            actionable=insight_data.get("actionable", False),
            action_url=insight_data.get("action_url"),
            expires_at=datetime.fromisoformat(insight_data["expires_at"]) if insight_data.get("expires_at") else None
        )
        return {"insight": insight}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/insights")
async def get_active_insights(patient_id: str):
    insights = patient_dashboard_service.get_active_insights(patient_id)
    return {"insights": insights}

@app.get("/patients/{patient_id}/widgets/{widget}/data")
async def get_widget_data(patient_id: str, widget: DashboardWidget):
    data = patient_dashboard_service.get_widget_data(patient_id, widget)
    return {"widget_data": data}

@app.put("/patients/{patient_id}/widgets/{widget}/data")
async def update_widget_data(patient_id: str, widget: DashboardWidget, data: Dict[str, Any]):
    patient_dashboard_service.update_widget_data(patient_id, widget, data)
    return {"message": "Widget data updated successfully"}

@app.get("/patients/{patient_id}/dashboard/summary")
async def get_dashboard_summary(patient_id: str):
    summary = patient_dashboard_service.get_dashboard_summary(patient_id)
    return {"summary": summary}

@app.post("/insights/cleanup")
async def clear_expired_insights(patient_id: str = None):
    patient_dashboard_service.clear_expired_insights(patient_id)
    return {"message": "Expired insights cleared successfully"} 