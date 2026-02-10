# =============================================================================
# 6. PERFORMANCE MONITORING & FAILURE DETECTION
# =============================================================================

import asyncio
import json
import statistics
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import redis
import psutil
import uuid

from alert_manager import AlertManager, AlertSeverity, Alert
from prometheus_metrics import PrometheusMetrics
from intelligence_layer import SystemHealth, IntegrationMetrics

class PerformanceMonitor:
    def __init__(self, redis_client: redis.Redis, db_session, prometheus_metrics: PrometheusMetrics):
        self.redis_client = redis_client
        self.db_session = db_session
        self.prometheus_metrics = prometheus_metrics
        self.alert_manager = AlertManager(redis_client, db_session)
        
    async def monitor_system_health(self):
        """Monitor overall system health metrics"""
        while True:
            try:
                # Get system metrics
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Calculate health score (0-100)
                health_score = self._calculate_health_score(cpu_usage, memory.percent, disk.percent)
                
                # Update Prometheus metrics
                self.prometheus_metrics.system_health.labels(component="overall").set(health_score)
                
                # Store in database
                db = next(self.db_session())
                health_record = SystemHealth(
                    component="system",
                    cpu_usage=cpu_usage,
                    memory_usage=memory.percent,
                    disk_usage=disk.percent,
                    network_io=network.bytes_sent + network.bytes_recv,
                    is_healthy=health_score > 70,
                    health_score=health_score
                )
                db.add(health_record)
                db.commit()
                
                # Cache current metrics
                health_data = {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent,
                    "health_score": health_score,
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.redis_client.setex("system_health", 300, json.dumps(health_data))
                
                # Check for alerts
                if health_score < 50:
                    alert = Alert(
                        id=str(uuid.uuid4()),
                        alert_type="system_health_critical",
                        severity=AlertSeverity.CRITICAL,
                        source="performance_monitor",
                        message=f"System health critical: {health_score}/100",
                        timestamp=datetime.utcnow(),
                        metadata=health_data
                    )
                    await self.alert_manager.send_alert(alert)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    def _calculate_health_score(self, cpu: float, memory: float, disk: float) -> float:
        """Calculate overall health score based on system metrics"""
        # Weight the different metrics
        cpu_score = max(0, 100 - cpu * 2)      # CPU usage penalty
        memory_score = max(0, 100 - memory)    # Memory usage penalty
        disk_score = max(0, 100 - disk)        # Disk usage penalty
        
        # Weighted average
        health_score = (cpu_score * 0.4 + memory_score * 0.4 + disk_score * 0.2)
        return min(100, max(0, health_score))
    
    async def detect_integration_failures(self):
        """Detect and analyze integration failures"""
        while True:
            try:
                # Check integration metrics from last 5 minutes
                five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
                
                db = next(self.db_session())
                recent_failures = db.query(IntegrationMetrics).filter(
                    IntegrationMetrics.timestamp >= five_minutes_ago,
                    IntegrationMetrics.success == False
                ).all()
                
                # Group failures by source system
                failure_groups = {}
                for failure in recent_failures:
                    system = failure.source_system
                    if system not in failure_groups:
                        failure_groups[system] = []
                    failure_groups[system].append(failure)
                
                # Analyze patterns
                for system, failures in failure_groups.items():
                    if len(failures) >= 3:  # 3+ failures in 5 minutes
                        # Check if it's a new pattern
                        pattern_key = f"failure_pattern:{system}"
                        existing_pattern = self.redis_client.get(pattern_key)
                        
                        if not existing_pattern:
                            # New failure pattern detected
                            failure_analysis = self._analyze_failures(failures)
                            
                            alert = Alert(
                                id=str(uuid.uuid4()),
                                alert_type="integration_failure_pattern",
                                severity=AlertSeverity.HIGH,
                                source="failure_detector",
                                message=f"Failure pattern detected in {system}: {len(failures)} failures",
                                timestamp=datetime.utcnow(),
                                metadata=failure_analysis
                            )
                            await self.alert_manager.send_alert(alert)
                            
                            # Mark pattern as detected (cooldown for 30 minutes)
                            self.redis_client.setex(pattern_key, 1800, json.dumps(failure_analysis))
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logging.error(f"Failure detection error: {str(e)}")
                await asyncio.sleep(300)
    
    def _analyze_failures(self, failures: List[IntegrationMetrics]) -> Dict[str, Any]:
        """Analyze failure patterns to identify root causes"""
        analysis = {
            "failure_count": len(failures),
            "time_span": "5 minutes",
            "error_types": {},
            "endpoints_affected": set(),
            "status_codes": {},
            "avg_response_time": 0
        }
        
        response_times = []
        for failure in failures:
            # Categorize error types
            if failure.status_code:
                code_range = f"{failure.status_code // 100}xx"
                analysis["status_codes"][code_range] = analysis["status_codes"].get(code_range, 0) + 1
            
            # Track affected endpoints
            analysis["endpoints_affected"].add(failure.endpoint)
            
            # Collect response times
            if failure.response_time:
                response_times.append(failure.response_time)
            
            # Categorize error messages
            if failure.error_message:
                error_type = self._categorize_error(failure.error_message)
                analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
        
        # Convert set to list for JSON serialization
        analysis["endpoints_affected"] = list(analysis["endpoints_affected"])
        
        # Calculate average response time
        if response_times:
            analysis["avg_response_time"] = statistics.mean(response_times)
        
        return analysis
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message into common types"""
        error_lower = error_message.lower()
        
        if "timeout" in error_lower or "timed out" in error_lower:
            return "timeout"
        elif "connection" in error_lower:
            return "connection_error"
        elif "authentication" in error_lower or "unauthorized" in error_lower:
            return "auth_error"
        elif "rate limit" in error_lower or "too many requests" in error_lower:
            return "rate_limit"
        elif "server error" in error_lower or "internal error" in error_lower:
            return "server_error"
        else:
            return "unknown_error" 