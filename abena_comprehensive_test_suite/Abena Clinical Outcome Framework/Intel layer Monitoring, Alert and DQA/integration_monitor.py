# =============================================================================
# 4. INTEGRATION MONITORING SYSTEM
# =============================================================================

import asyncio
import json
import statistics
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import redis
import numpy as np

from alert_manager import AlertManager, AlertSeverity
from prometheus_metrics import PrometheusMetrics
from intelligence_layer import IntegrationMetrics

class IntegrationMonitor:
    def __init__(self, redis_client: redis.Redis, db_session, prometheus_metrics: PrometheusMetrics):
        self.redis_client = redis_client
        self.db_session = db_session
        self.prometheus_metrics = prometheus_metrics
        self.alert_manager = AlertManager(redis_client, db_session)
        self.setup_default_alert_rules()
    
    def setup_default_alert_rules(self):
        """Set up default monitoring alert rules"""
        
        # High error rate
        self.alert_manager.add_alert_rule(
            "high_error_rate",
            lambda m: m.get('error_rate', 0) > 0.05,  # 5% error rate
            AlertSeverity.HIGH,
            cooldown_minutes=10
        )
        
        # Slow response time
        self.alert_manager.add_alert_rule(
            "slow_response_time",
            lambda m: m.get('avg_response_time', 0) > 30.0,  # 30 seconds
            AlertSeverity.MEDIUM,
            cooldown_minutes=15
        )
        
        # Integration failure
        self.alert_manager.add_alert_rule(
            "integration_failure",
            lambda m: m.get('consecutive_failures', 0) >= 3,
            AlertSeverity.CRITICAL,
            cooldown_minutes=5
        )
        
        # Low data quality
        self.alert_manager.add_alert_rule(
            "low_data_quality",
            lambda m: m.get('data_quality_score', 1.0) < 0.7,  # Below 70%
            AlertSeverity.HIGH,
            cooldown_minutes=30
        )
    
    async def record_integration_event(self, source_system: str, endpoint: str, 
                                     response_time: float, status_code: int, 
                                     success: bool, error_message: str = None,
                                     records_processed: int = 0):
        """Record an integration event for monitoring"""
        
        # Update Prometheus metrics
        status = "success" if success else "error"
        self.prometheus_metrics.integration_requests.labels(
            source_system=source_system,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.prometheus_metrics.integration_response_time.labels(
            source_system=source_system,
            endpoint=endpoint
        ).observe(response_time)
        
        if not success:
            error_type = "timeout" if response_time > 30 else "api_error"
            self.prometheus_metrics.integration_errors.labels(
                source_system=source_system,
                error_type=error_type
            ).inc()
        
        # Store in database
        db = next(self.db_session())
        metric = IntegrationMetrics(
            source_system=source_system,
            endpoint=endpoint,
            response_time=response_time,
            status_code=status_code,
            success=success,
            error_message=error_message,
            records_processed=records_processed
        )
        db.add(metric)
        db.commit()
        
        # Update Redis with latest metrics
        metrics_key = f"integration_metrics:{source_system}"
        current_metrics = self.redis_client.get(metrics_key)
        
        if current_metrics:
            metrics = json.loads(current_metrics)
        else:
            metrics = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'consecutive_failures': 0
            }
        
        metrics['total_requests'] += 1
        if success:
            metrics['successful_requests'] += 1
            metrics['consecutive_failures'] = 0
        else:
            metrics['failed_requests'] += 1
            metrics['consecutive_failures'] += 1
        
        metrics['response_times'].append(response_time)
        if len(metrics['response_times']) > 100:  # Keep last 100 response times
            metrics['response_times'] = metrics['response_times'][-100:]
        
        # Calculate derived metrics
        metrics['error_rate'] = metrics['failed_requests'] / metrics['total_requests']
        metrics['avg_response_time'] = statistics.mean(metrics['response_times'])
        
        self.redis_client.setex(metrics_key, 3600, json.dumps(metrics))
        
        # Check alert conditions
        alerts = await self.alert_manager.check_alert_conditions(metrics)
        for alert in alerts:
            await self.alert_manager.send_alert(alert)
    
    async def get_integration_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get dashboard data for integration monitoring"""
        db = next(self.db_session())
        
        # Get metrics from last N hours
        since = datetime.utcnow() - timedelta(hours=hours)
        metrics = db.query(IntegrationMetrics).filter(
            IntegrationMetrics.timestamp >= since
        ).all()
        
        # Calculate summary statistics
        total_requests = len(metrics)
        successful_requests = len([m for m in metrics if m.success])
        failed_requests = total_requests - successful_requests
        
        # Group by source system
        system_stats = {}
        for metric in metrics:
            if metric.source_system not in system_stats:
                system_stats[metric.source_system] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'response_times': [],
                    'records_processed': 0
                }
            
            stats = system_stats[metric.source_system]
            stats['total'] += 1
            if metric.success:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
            
            if metric.response_time:
                stats['response_times'].append(metric.response_time)
            
            if metric.records_processed:
                stats['records_processed'] += metric.records_processed
        
        # Calculate averages
        for system, stats in system_stats.items():
            if stats['response_times']:
                stats['avg_response_time'] = statistics.mean(stats['response_times'])
                stats['p95_response_time'] = np.percentile(stats['response_times'], 95)
            else:
                stats['avg_response_time'] = 0
                stats['p95_response_time'] = 0
            
            stats['success_rate'] = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        
        return {
            'summary': {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate': successful_requests / total_requests if total_requests > 0 else 0
            },
            'by_system': system_stats,
            'timestamp': datetime.utcnow().isoformat()
        } 