"""
Real-Time Analytics Module for Abena IHR
========================================

This module provides real-time analytics capabilities including:
- Real-time health monitoring
- Anomaly detection
- Alert generation
- Performance metrics tracking
- Live dashboard data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
import numpy as np
import pandas as pd
from collections import deque, defaultdict
import json
import redis
import httpx
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import threading
import time
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MetricType(Enum):
    VITAL_SIGNS = "vital_signs"
    LAB_RESULTS = "lab_results"
    MEDICATION = "medication"
    ACTIVITY = "activity"
    ENVIRONMENTAL = "environmental"

# Pydantic models
class RealTimeMetric(BaseModel):
    """Real-time metric data model"""
    metric_id: str
    patient_id: str
    metric_type: MetricType
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    source: str
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}

class AlertRule(BaseModel):
    """Alert rule configuration"""
    rule_id: str
    name: str
    metric_name: str
    condition: str = Field(..., regex="^(above|below|equals|not_equals|trending_up|trending_down)$")
    threshold: float
    severity: AlertSeverity
    duration: int = Field(30, ge=1)  # seconds
    enabled: bool = True
    description: str = ""

class Alert(BaseModel):
    """Alert model"""
    alert_id: str
    rule_id: str
    patient_id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False

class DashboardMetric(BaseModel):
    """Dashboard metric model"""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend: str
    status: str
    timestamp: datetime

class RealTimeAnalytics:
    """Real-time analytics engine"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.metric_buffers = defaultdict(lambda: deque(maxlen=1000))  # Store last 1000 values per metric
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_callbacks = []
        self.websocket_connections = []
        self.running = False
        self.analysis_thread = None
        
    async def start(self):
        """Start the real-time analytics engine"""
        if not self.running:
            self.running = True
            self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.analysis_thread.start()
            logger.info("Real-time analytics engine started")
            
    async def stop(self):
        """Stop the real-time analytics engine"""
        self.running = False
        if self.analysis_thread:
            self.analysis_thread.join()
        logger.info("Real-time analytics engine stopped")
        
    def add_metric(self, metric: RealTimeMetric):
        """Add a new metric to the real-time analytics"""
        try:
            # Store metric in buffer
            self.metric_buffers[metric.metric_name].append(metric)
            
            # Store in Redis for persistence
            metric_key = f"metric:{metric.patient_id}:{metric.metric_name}:{metric.timestamp.timestamp()}"
            self.redis_client.setex(
                metric_key,
                3600,  # 1 hour TTL
                json.dumps(metric.dict())
            )
            
            # Check alert rules
            self._check_alert_rules(metric)
            
            # Broadcast to websocket connections
            self._broadcast_metric(metric)
            
        except Exception as e:
            logger.error(f"Error adding metric: {e}")
            
    def add_alert_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")
        
    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
            
    def get_metrics(self, metric_name: str, patient_id: Optional[str] = None, 
                   time_window: int = 3600) -> List[RealTimeMetric]:
        """Get metrics for a specific metric name and time window"""
        try:
            metrics = []
            cutoff_time = datetime.now() - timedelta(seconds=time_window)
            
            # Get from buffer first
            buffer_metrics = list(self.metric_buffers[metric_name])
            for metric in buffer_metrics:
                if metric.timestamp >= cutoff_time:
                    if patient_id is None or metric.patient_id == patient_id:
                        metrics.append(metric)
                        
            # Get from Redis if needed
            if len(metrics) < 100:  # If we need more data
                pattern = f"metric:*:{metric_name}:*"
                if patient_id:
                    pattern = f"metric:{patient_id}:{metric_name}:*"
                    
                keys = self.redis_client.keys(pattern)
                for key in keys:
                    metric_data = self.redis_client.get(key)
                    if metric_data:
                        metric_dict = json.loads(metric_data)
                        metric = RealTimeMetric(**metric_dict)
                        if metric.timestamp >= cutoff_time:
                            metrics.append(metric)
                            
            # Sort by timestamp
            metrics.sort(key=lambda x: x.timestamp)
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return []
            
    def get_active_alerts(self, patient_id: Optional[str] = None) -> List[Alert]:
        """Get active alerts"""
        alerts = []
        for alert in self.active_alerts.values():
            if not alert.resolved:
                if patient_id is None or alert.patient_id == patient_id:
                    alerts.append(alert)
        return alerts
        
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            logger.info(f"Alert acknowledged: {alert_id}")
            
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            logger.info(f"Alert resolved: {alert_id}")
            
    def get_dashboard_metrics(self) -> List[DashboardMetric]:
        """Get metrics for dashboard display"""
        dashboard_metrics = []
        
        for metric_name in self.metric_buffers.keys():
            metrics = list(self.metric_buffers[metric_name])
            if len(metrics) >= 2:
                current = metrics[-1]
                previous = metrics[-2]
                
                change_pct = ((current.value - previous.value) / previous.value * 100) if previous.value != 0 else 0
                trend = "up" if change_pct > 0 else "down" if change_pct < 0 else "stable"
                
                # Determine status based on value ranges
                status = self._determine_metric_status(metric_name, current.value)
                
                dashboard_metric = DashboardMetric(
                    metric_name=metric_name,
                    current_value=current.value,
                    previous_value=previous.value,
                    change_percentage=change_pct,
                    trend=trend,
                    status=status,
                    timestamp=current.timestamp
                )
                dashboard_metrics.append(dashboard_metric)
                
        return dashboard_metrics
        
    def detect_anomalies(self, metric_name: str, time_window: int = 3600) -> List[Dict[str, Any]]:
        """Detect anomalies in metric data"""
        try:
            metrics = self.get_metrics(metric_name, time_window=time_window)
            if len(metrics) < 10:
                return []
                
            values = [m.value for m in metrics]
            timestamps = [m.timestamp for m in metrics]
            
            # Calculate statistical measures
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            # Detect outliers (beyond 2 standard deviations)
            anomalies = []
            for i, (value, timestamp) in enumerate(zip(values, timestamps)):
                z_score = abs((value - mean_val) / std_val) if std_val > 0 else 0
                if z_score > 2:
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'timestamp': timestamp,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 3 else 'medium'
                    })
                    
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
            
    def calculate_trends(self, metric_name: str, time_window: int = 3600) -> Dict[str, Any]:
        """Calculate trends for a metric"""
        try:
            metrics = self.get_metrics(metric_name, time_window=time_window)
            if len(metrics) < 5:
                return {}
                
            values = [m.value for m in metrics]
            timestamps = [m.timestamp.timestamp() for m in metrics]
            
            # Linear regression for trend
            x = np.array(timestamps)
            y = np.array(values)
            
            # Normalize timestamps
            x_norm = (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else x
            
            # Calculate trend
            slope, intercept = np.polyfit(x_norm, y, 1)
            
            # Calculate R-squared
            y_pred = slope * x_norm + intercept
            r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
            
            # Determine trend direction and strength
            if abs(slope) < 0.01:
                trend_direction = "stable"
                trend_strength = "weak"
            else:
                trend_direction = "increasing" if slope > 0 else "decreasing"
                trend_strength = "strong" if abs(slope) > 0.1 else "moderate"
                
            return {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_squared,
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'current_value': values[-1],
                'change_rate': slope,
                'confidence': min(r_squared, 1.0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {}
            
    def _check_alert_rules(self, metric: RealTimeMetric):
        """Check if metric triggers any alert rules"""
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled or rule.metric_name != metric.metric_name:
                continue
                
            # Check if rule is already triggered
            active_alert_key = f"{rule_id}:{metric.patient_id}"
            if active_alert_key in self.active_alerts:
                continue
                
            # Check condition
            triggered = False
            if rule.condition == "above" and metric.value > rule.threshold:
                triggered = True
            elif rule.condition == "below" and metric.value < rule.threshold:
                triggered = True
            elif rule.condition == "equals" and abs(metric.value - rule.threshold) < 0.001:
                triggered = True
            elif rule.condition == "not_equals" and abs(metric.value - rule.threshold) >= 0.001:
                triggered = True
            elif rule.condition in ["trending_up", "trending_down"]:
                # Check trend over duration
                metrics = self.get_metrics(metric.metric_name, metric.patient_id, rule.duration)
                if len(metrics) >= 2:
                    trend = self.calculate_trends(metric.metric_name, rule.duration)
                    if rule.condition == "trending_up" and trend.get('trend_direction') == 'increasing':
                        triggered = True
                    elif rule.condition == "trending_down" and trend.get('trend_direction') == 'decreasing':
                        triggered = True
                        
            if triggered:
                self._create_alert(rule, metric)
                
    def _create_alert(self, rule: AlertRule, metric: RealTimeMetric):
        """Create a new alert"""
        alert_id = f"{rule.rule_id}:{metric.patient_id}:{metric.timestamp.timestamp()}"
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            patient_id=metric.patient_id,
            metric_name=metric.metric_name,
            severity=rule.severity,
            message=f"{metric.metric_name} {rule.condition} {rule.threshold} (current: {metric.value})",
            value=metric.value,
            threshold=rule.threshold,
            timestamp=metric.timestamp
        )
        
        self.active_alerts[alert_id] = alert
        
        # Store in Redis
        alert_key = f"alert:{alert_id}"
        self.redis_client.setex(
            alert_key,
            86400,  # 24 hours TTL
            json.dumps(alert.dict())
        )
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
                
        # Broadcast to websocket connections
        self._broadcast_alert(alert)
        
        logger.info(f"Alert created: {alert_id} - {alert.message}")
        
    def _determine_metric_status(self, metric_name: str, value: float) -> str:
        """Determine status of a metric based on its value"""
        # Define normal ranges for common metrics
        normal_ranges = {
            'heart_rate': (60, 100),
            'blood_pressure_systolic': (90, 140),
            'blood_pressure_diastolic': (60, 90),
            'temperature': (36.0, 37.5),
            'oxygen_saturation': (95, 100),
            'glucose': (70, 140)
        }
        
        if metric_name in normal_ranges:
            min_val, max_val = normal_ranges[metric_name]
            if value < min_val:
                return "low"
            elif value > max_val:
                return "high"
            else:
                return "normal"
        else:
            return "unknown"
            
    def _analysis_loop(self):
        """Main analysis loop running in background thread"""
        while self.running:
            try:
                # Perform periodic analysis
                self._perform_periodic_analysis()
                
                # Clean up old alerts
                self._cleanup_old_alerts()
                
                # Sleep for a short interval
                time.sleep(5)  # 5 seconds
                
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                time.sleep(10)  # Longer sleep on error
                
    def _perform_periodic_analysis(self):
        """Perform periodic analysis tasks"""
        try:
            # Analyze trends for all metrics
            for metric_name in self.metric_buffers.keys():
                trends = self.calculate_trends(metric_name)
                if trends:
                    # Store trend data
                    trend_key = f"trend:{metric_name}"
                    self.redis_client.setex(
                        trend_key,
                        300,  # 5 minutes TTL
                        json.dumps(trends)
                    )
                    
            # Detect anomalies
            for metric_name in self.metric_buffers.keys():
                anomalies = self.detect_anomalies(metric_name)
                if anomalies:
                    # Store anomaly data
                    anomaly_key = f"anomaly:{metric_name}"
                    self.redis_client.setex(
                        anomaly_key,
                        300,  # 5 minutes TTL
                        json.dumps(anomalies)
                    )
                    
        except Exception as e:
            logger.error(f"Error in periodic analysis: {e}")
            
    def _cleanup_old_alerts(self):
        """Clean up old resolved alerts"""
        current_time = datetime.now()
        alerts_to_remove = []
        
        for alert_id, alert in self.active_alerts.items():
            # Remove alerts older than 24 hours
            if (current_time - alert.timestamp).total_seconds() > 86400:
                alerts_to_remove.append(alert_id)
                
        for alert_id in alerts_to_remove:
            del self.active_alerts[alert_id]
            
    def _broadcast_metric(self, metric: RealTimeMetric):
        """Broadcast metric to websocket connections"""
        message = {
            'type': 'metric',
            'data': metric.dict()
        }
        
        # Remove disconnected connections
        self.websocket_connections = [conn for conn in self.websocket_connections if not conn.closed]
        
        # Broadcast to remaining connections
        for connection in self.websocket_connections:
            try:
                asyncio.create_task(connection.send_text(json.dumps(message)))
            except Exception as e:
                logger.error(f"Error broadcasting metric: {e}")
                
    def _broadcast_alert(self, alert: Alert):
        """Broadcast alert to websocket connections"""
        message = {
            'type': 'alert',
            'data': alert.dict()
        }
        
        # Remove disconnected connections
        self.websocket_connections = [conn for conn in self.websocket_connections if not conn.closed]
        
        # Broadcast to remaining connections
        for connection in self.websocket_connections:
            try:
                asyncio.create_task(connection.send_text(json.dumps(message)))
            except Exception as e:
                logger.error(f"Error broadcasting alert: {e}")
                
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add a callback function for alerts"""
        self.alert_callbacks.append(callback)
        
    def add_websocket_connection(self, connection: WebSocket):
        """Add a websocket connection for real-time updates"""
        self.websocket_connections.append(connection)
        
    def remove_websocket_connection(self, connection: WebSocket):
        """Remove a websocket connection"""
        if connection in self.websocket_connections:
            self.websocket_connections.remove(connection)

# Initialize real-time analytics
real_time_analytics = RealTimeAnalytics()

# FastAPI app for real-time analytics
app = FastAPI(
    title="Abena IHR Real-Time Analytics",
    description="Real-time health monitoring and analytics",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize real-time analytics on startup"""
    await real_time_analytics.start()
    
    # Add some default alert rules
    default_rules = [
        AlertRule(
            rule_id="high_heart_rate",
            name="High Heart Rate",
            metric_name="heart_rate",
            condition="above",
            threshold=100,
            severity=AlertSeverity.MEDIUM,
            description="Heart rate above 100 BPM"
        ),
        AlertRule(
            rule_id="low_oxygen",
            name="Low Oxygen Saturation",
            metric_name="oxygen_saturation",
            condition="below",
            threshold=95,
            severity=AlertSeverity.HIGH,
            description="Oxygen saturation below 95%"
        ),
        AlertRule(
            rule_id="high_blood_pressure",
            name="High Blood Pressure",
            metric_name="blood_pressure_systolic",
            condition="above",
            threshold=140,
            severity=AlertSeverity.MEDIUM,
            description="Systolic blood pressure above 140 mmHg"
        )
    ]
    
    for rule in default_rules:
        real_time_analytics.add_alert_rule(rule)

@app.on_event("shutdown")
async def shutdown_event():
    """Stop real-time analytics on shutdown"""
    await real_time_analytics.stop()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "real_time_analytics",
        "timestamp": datetime.now(),
        "active_alerts": len(real_time_analytics.get_active_alerts()),
        "metric_count": len(real_time_analytics.metric_buffers)
    }

@app.post("/metrics")
async def add_metric(metric: RealTimeMetric):
    """Add a new metric"""
    real_time_analytics.add_metric(metric)
    return {"message": "Metric added successfully"}

@app.get("/metrics/{metric_name}")
async def get_metrics(metric_name: str, patient_id: Optional[str] = None, 
                     time_window: int = 3600):
    """Get metrics for a specific metric name"""
    metrics = real_time_analytics.get_metrics(metric_name, patient_id, time_window)
    return {
        "metric_name": metric_name,
        "patient_id": patient_id,
        "time_window": time_window,
        "count": len(metrics),
        "metrics": [metric.dict() for metric in metrics]
    }

@app.get("/alerts")
async def get_alerts(patient_id: Optional[str] = None):
    """Get active alerts"""
    alerts = real_time_analytics.get_active_alerts(patient_id)
    return {
        "alerts": [alert.dict() for alert in alerts],
        "count": len(alerts)
    }

@app.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    real_time_analytics.acknowledge_alert(alert_id)
    return {"message": "Alert acknowledged"}

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert"""
    real_time_analytics.resolve_alert(alert_id)
    return {"message": "Alert resolved"}

@app.get("/dashboard")
async def get_dashboard():
    """Get dashboard metrics"""
    metrics = real_time_analytics.get_dashboard_metrics()
    alerts = real_time_analytics.get_active_alerts()
    
    return {
        "metrics": [metric.dict() for metric in metrics],
        "alerts": [alert.dict() for alert in alerts],
        "summary": {
            "total_metrics": len(metrics),
            "active_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
        }
    }

@app.get("/anomalies/{metric_name}")
async def get_anomalies(metric_name: str, time_window: int = 3600):
    """Get anomalies for a metric"""
    anomalies = real_time_analytics.detect_anomalies(metric_name, time_window)
    return {
        "metric_name": metric_name,
        "time_window": time_window,
        "anomalies": anomalies,
        "count": len(anomalies)
    }

@app.get("/trends/{metric_name}")
async def get_trends(metric_name: str, time_window: int = 3600):
    """Get trends for a metric"""
    trends = real_time_analytics.calculate_trends(metric_name, time_window)
    return {
        "metric_name": metric_name,
        "time_window": time_window,
        "trends": trends
    }

@app.post("/alert-rules")
async def add_alert_rule(rule: AlertRule):
    """Add an alert rule"""
    real_time_analytics.add_alert_rule(rule)
    return {"message": "Alert rule added successfully"}

@app.delete("/alert-rules/{rule_id}")
async def remove_alert_rule(rule_id: str):
    """Remove an alert rule"""
    real_time_analytics.remove_alert_rule(rule_id)
    return {"message": "Alert rule removed successfully"}

@app.get("/alert-rules")
async def get_alert_rules():
    """Get all alert rules"""
    rules = list(real_time_analytics.alert_rules.values())
    return {
        "rules": [rule.dict() for rule in rules],
        "count": len(rules)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    real_time_analytics.add_websocket_connection(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        real_time_analytics.remove_websocket_connection(websocket)
        logger.info("WebSocket client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012) 