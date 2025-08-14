# =============================================================================
# 7. REPORTING & DASHBOARD GENERATION
# =============================================================================

import asyncio
import json
import statistics
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import redis
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

from intelligence_layer import DataQualityMetrics, IntegrationMetrics, SystemHealth, AlertLog

class ReportGenerator:
    def __init__(self, redis_client: redis.Redis, db_session):
        self.redis_client = redis_client
        self.db_session = db_session
    
    async def generate_data_quality_report(self, source_system: str = None, 
                                         days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive data quality report"""
        since = datetime.utcnow() - timedelta(days=days)
        
        db = next(self.db_session())
        query = db.query(DataQualityMetrics).filter(DataQualityMetrics.timestamp >= since)
        
        if source_system:
            query = query.filter(DataQualityMetrics.source_system == source_system)
        
        metrics = query.all()
        
        if not metrics:
            return {"error": "No data quality metrics found for the specified period"}
        
        # Calculate aggregated scores
        total_records = sum(m.total_records for m in metrics)
        total_valid = sum(m.valid_records for m in metrics)
        
        avg_completeness = statistics.mean([m.completeness_score for m in metrics])
        avg_accuracy = statistics.mean([m.accuracy_score for m in metrics])
        avg_consistency = statistics.mean([m.consistency_score for m in metrics])
        avg_timeliness = statistics.mean([m.timeliness_score for m in metrics])
        
        overall_quality = (avg_completeness + avg_accuracy + avg_consistency + avg_timeliness) / 4
        
        # Group by source system
        by_system = {}
        for metric in metrics:
            system = metric.source_system
            if system not in by_system:
                by_system[system] = {
                    "records": 0,
                    "quality_scores": [],
                    "issues": []
                }
            
            by_system[system]["records"] += metric.total_records
            by_system[system]["quality_scores"].append({
                "completeness": metric.completeness_score,
                "accuracy": metric.accuracy_score,
                "consistency": metric.consistency_score,
                "timeliness": metric.timeliness_score
            })
            by_system[system]["issues"].extend(metric.quality_issues or [])
        
        # Calculate system averages
        for system, data in by_system.items():
            scores = data["quality_scores"]
            data["avg_completeness"] = statistics.mean([s["completeness"] for s in scores])
            data["avg_accuracy"] = statistics.mean([s["accuracy"] for s in scores])
            data["avg_consistency"] = statistics.mean([s["consistency"] for s in scores])
            data["avg_timeliness"] = statistics.mean([s["timeliness"] for s in scores])
            data["overall_quality"] = (
                data["avg_completeness"] + data["avg_accuracy"] + 
                data["avg_consistency"] + data["avg_timeliness"]
            ) / 4
        
        return {
            "report_period": f"{days} days",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_records_analyzed": total_records,
                "total_valid_records": total_valid,
                "overall_quality_score": overall_quality,
                "avg_completeness": avg_completeness,
                "avg_accuracy": avg_accuracy,
                "avg_consistency": avg_consistency,
                "avg_timeliness": avg_timeliness
            },
            "by_system": by_system,
            "recommendations": self._generate_quality_recommendations(by_system)
        }
    
    def _generate_quality_recommendations(self, system_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on quality analysis"""
        recommendations = []
        
        for system, data in system_data.items():
            if data["avg_completeness"] < 0.8:
                recommendations.append(
                    f"Improve data completeness for {system} - currently {data['avg_completeness']:.1%}"
                )
            
            if data["avg_accuracy"] < 0.8:
                recommendations.append(
                    f"Enhance data validation rules for {system} - accuracy at {data['avg_accuracy']:.1%}"
                )
            
            if data["avg_consistency"] < 0.8:
                recommendations.append(
                    f"Standardize data formats for {system} - consistency at {data['avg_consistency']:.1%}"
                )
            
            if data["avg_timeliness"] < 0.8:
                recommendations.append(
                    f"Increase sync frequency for {system} - timeliness at {data['avg_timeliness']:.1%}"
                )
        
        if not recommendations:
            recommendations.append("All systems meeting quality thresholds - continue monitoring")
        
        return recommendations
    
    def create_performance_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Create data for performance monitoring dashboard"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        db = next(self.db_session())
        
        # Get integration metrics
        integration_metrics = db.query(IntegrationMetrics).filter(
            IntegrationMetrics.timestamp >= since
        ).all()
        
        # Get system health metrics
        health_metrics = db.query(SystemHealth).filter(
            SystemHealth.timestamp >= since
        ).all()
        
        # Get recent alerts
        recent_alerts = db.query(AlertLog).filter(
            AlertLog.timestamp >= since
        ).all()
        
        # Process integration data for charts
        integration_data = []
        for metric in integration_metrics:
            integration_data.append({
                "timestamp": metric.timestamp.isoformat(),
                "source_system": metric.source_system,
                "response_time": metric.response_time or 0,
                "success": metric.success,
                "records_processed": metric.records_processed or 0
            })
        
        # Process health data for charts
        health_data = []
        for metric in health_metrics:
            health_data.append({
                "timestamp": metric.timestamp.isoformat(),
                "component": metric.component,
                "cpu_usage": metric.cpu_usage or 0,
                "memory_usage": metric.memory_usage or 0,
                "health_score": metric.health_score or 0
            })
        
        # Process alerts data
        alert_summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for alert in recent_alerts:
            if not alert.resolved:
                alert_summary[alert.severity] = alert_summary.get(alert.severity, 0) + 1
        
        return {
            "dashboard_data": {
                "integration_metrics": integration_data,
                "health_metrics": health_data,
                "active_alerts": alert_summary,
                "generated_at": datetime.utcnow().isoformat(),
                "period_hours": hours
            }
        }
    
    def generate_plotly_charts(self, dashboard_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate Plotly charts for the dashboard"""
        charts = {}
        
        # Integration response time chart
        if dashboard_data["integration_metrics"]:
            df = pd.DataFrame(dashboard_data["integration_metrics"])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = px.line(df, x='timestamp', y='response_time', color='source_system',
                         title='Integration Response Times')
            charts["response_times"] = json.dumps(fig, cls=PlotlyJSONEncoder)
            
            # Success rate chart
            success_rate = df.groupby(['source_system', 'timestamp'])['success'].mean().reset_index()
            fig2 = px.line(success_rate, x='timestamp', y='success', color='source_system',
                          title='Integration Success Rates')
            charts["success_rates"] = json.dumps(fig2, cls=PlotlyJSONEncoder)
        
        # System health chart
        if dashboard_data["health_metrics"]:
            health_df = pd.DataFrame(dashboard_data["health_metrics"])
            health_df['timestamp'] = pd.to_datetime(health_df['timestamp'])
            
            fig3 = px.line(health_df, x='timestamp', y='health_score', color='component',
                          title='System Health Score')
            charts["health_scores"] = json.dumps(fig3, cls=PlotlyJSONEncoder)
        
        return charts 