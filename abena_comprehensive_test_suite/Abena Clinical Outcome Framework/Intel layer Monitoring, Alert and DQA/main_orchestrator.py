# =============================================================================
# Abena IHR - Intelligence Layer Main Orchestrator
# =============================================================================

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from config import Config
from intelligence_layer import (
    IntegrationMonitor, DataQualityAnalyzer, PerformanceMonitor, 
    ReportGenerator, PrometheusMetrics
)

# Import Abena SDK
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from abena_sdk import AbenaSDK, AbenaSDKConfig

# Initialize configuration
config = Config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.logging.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class IntelligenceLayer:
    def __init__(self):
        # Initialize Abena SDK for centralized services
        self.abena = AbenaSDK(AbenaSDKConfig(
            auth_service_url='http://localhost:3001',
            data_service_url='http://localhost:8001',
            privacy_service_url='http://localhost:8002',
            blockchain_service_url='http://localhost:8003'
        ))
        
        # Initialize components with Abena SDK integration
        self.prometheus_metrics = PrometheusMetrics()
        self.integration_monitor = IntegrationMonitor(
            self.abena, self.prometheus_metrics
        )
        self.data_quality_analyzer = DataQualityAnalyzer(
            self.abena, self.prometheus_metrics
        )
        self.performance_monitor = PerformanceMonitor(
            self.abena, self.prometheus_metrics
        )
        self.report_generator = ReportGenerator(self.abena)
        
        # Setup default configurations
        self.data_quality_analyzer.setup_default_quality_rules()
        
        # Setup notification channels
        self.setup_notifications()
        
        # Setup alert rules with configurable thresholds
        self.setup_alert_rules()
        
        logger.info("Intelligence Layer initialized successfully")
    
    def setup_notifications(self):
        """Setup notification channels"""
        self.notification_channels = {
            'email': config.email,
            'slack': config.slack
        }
        logger.info("Notification channels configured")
    
    def setup_alert_rules(self):
        """Setup alert rules with configurable thresholds"""
        self.alert_rules = {
            'high_error_rate': {
                'threshold': float(config.alerts.high_error_rate_threshold),
                'cooldown_minutes': int(config.alerts.default_alert_cooldown_minutes)
            },
            'slow_response_time': {
                'threshold': float(config.alerts.slow_response_time_threshold),
                'cooldown_minutes': int(config.alerts.default_alert_cooldown_minutes)
            },
            'low_data_quality': {
                'threshold': float(config.alerts.low_data_quality_threshold),
                'cooldown_minutes': int(config.alerts.default_alert_cooldown_minutes)
            },
            'system_health': {
                'threshold': float(config.alerts.system_health_threshold),
                'cooldown_minutes': int(config.alerts.default_alert_cooldown_minutes)
            }
        }
        logger.info("Alert rules configured")
    
    async def start_monitoring(self):
        """Start all monitoring services"""
        logger.info("Starting Intelligence Layer monitoring services")
        
        try:
            # Start Prometheus metrics server
            await self.prometheus_metrics.start_server(
                host=config.api.host,
                port=config.api.prometheus_port
            )
            
            # Start monitoring tasks
            monitoring_tasks = [
                asyncio.create_task(self.integration_monitor.start_monitoring()),
                asyncio.create_task(self.data_quality_analyzer.start_analysis()),
                asyncio.create_task(self.performance_monitor.start_monitoring()),
                asyncio.create_task(self.report_generator.start_reporting())
            ]
            
            logger.info("All monitoring services started")
            
            # Wait for all tasks to complete
            await asyncio.gather(*monitoring_tasks)
            
        except Exception as e:
            logger.error(f"Error starting monitoring services: {str(e)}")
            raise
    
    async def stop_monitoring(self):
        """Stop all monitoring services"""
        logger.info("Stopping Intelligence Layer monitoring services")
        
        try:
            # Stop monitoring tasks
            await self.integration_monitor.stop_monitoring()
            await self.data_quality_analyzer.stop_analysis()
            await self.performance_monitor.stop_monitoring()
            await self.report_generator.stop_reporting()
            
            # Stop Prometheus metrics server
            await self.prometheus_metrics.stop_server()
            
            logger.info("All monitoring services stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring services: {str(e)}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            # 1. Auto-handled auth & permissions
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'components': {}
            }
            
            # Check integration health
            integration_health = await self.integration_monitor.get_health_status()
            health_status['components']['integration'] = integration_health
            
            # Check data quality health
            quality_health = await self.data_quality_analyzer.get_health_status()
            health_status['components']['data_quality'] = quality_health
            
            # Check performance health
            performance_health = await self.performance_monitor.get_health_status()
            health_status['components']['performance'] = performance_health
            
            # Determine overall status
            component_statuses = [
                integration_health.get('status', 'unknown'),
                quality_health.get('status', 'unknown'),
                performance_health.get('status', 'unknown')
            ]
            
            if 'critical' in component_statuses:
                health_status['overall_status'] = 'critical'
            elif 'warning' in component_statuses:
                health_status['overall_status'] = 'warning'
            elif all(status == 'healthy' for status in component_statuses):
                health_status['overall_status'] = 'healthy'
            else:
                health_status['overall_status'] = 'unknown'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'error',
                'error': str(e)
            }
    
    async def generate_comprehensive_report(self, report_type: str = "daily") -> Dict[str, Any]:
        """Generate comprehensive system report"""
        try:
            # 1. Auto-handled auth & permissions
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            report = {
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'system_health': await self.get_system_health(),
                'integration_metrics': await self.integration_monitor.get_summary_metrics(),
                'data_quality_metrics': await self.data_quality_analyzer.get_summary_metrics(),
                'performance_metrics': await self.performance_monitor.get_summary_metrics(),
                'alerts_summary': await self.get_alerts_summary(),
                'recommendations': await self.generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {str(e)}")
            raise
    
    async def get_alerts_summary(self) -> Dict[str, Any]:
        """Get summary of recent alerts"""
        try:
            # This would typically query the data service for recent alerts
            # For now, return a placeholder structure
            return {
                'total_alerts_24h': 0,
                'critical_alerts': 0,
                'warning_alerts': 0,
                'resolved_alerts': 0,
                'recent_alerts': []
            }
        except Exception as e:
            logger.error(f"Error getting alerts summary: {str(e)}")
            return {}
    
    async def generate_recommendations(self) -> List[str]:
        """Generate system recommendations based on current state"""
        try:
            recommendations = []
            
            # Get system health
            health = await self.get_system_health()
            
            if health['overall_status'] == 'critical':
                recommendations.append("Immediate attention required - system health is critical")
                recommendations.append("Review integration logs for recent failures")
                recommendations.append("Check data quality metrics for anomalies")
            
            elif health['overall_status'] == 'warning':
                recommendations.append("Monitor system closely - some components showing warnings")
                recommendations.append("Review performance metrics for optimization opportunities")
            
            else:
                recommendations.append("System operating normally - continue monitoring")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Unable to generate recommendations due to system error"]

    async def get_intelligence_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive intelligence dashboard data"""
        # Get integration monitoring data
        integration_data = await self.integration_monitor.get_integration_dashboard_data(24)
        
        # Get performance dashboard data
        performance_data = self.report_generator.create_performance_dashboard_data(24)
        
        # Get data quality report
        quality_report = await self.report_generator.generate_data_quality_report(days=7)
        
        return {
            "integration_monitoring": integration_data,
            "performance_monitoring": performance_data["dashboard_data"],
            "data_quality": quality_report,
            "active_alerts": {},
            "system_status": "healthy",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def record_integration_event(self, source_system: str, endpoint: str, 
                                     response_time: float, status_code: int, 
                                     success: bool, error_message: str = None,
                                     records_processed: int = 0):
        """Record an integration event for monitoring"""
        await self.integration_monitor.record_integration_event(
            source_system, endpoint, response_time, status_code, 
            success, error_message, records_processed
        )
    
    async def analyze_data_quality(self, data, data_type: str, source_system: str):
        """Analyze data quality for a dataset"""
        return await self.data_quality_analyzer.analyze_data_quality(
            data, data_type, source_system
        )
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration status for monitoring"""
        return {
            "abena_sdk_configured": True,
            "email_configured": config.is_email_configured(),
            "slack_configured": config.is_slack_configured(),
            "security_configured": config.is_secure(),
            "alert_thresholds": {
                "high_error_rate": config.alerts.high_error_rate_threshold,
                "slow_response_time": config.alerts.slow_response_time_threshold,
                "low_data_quality": config.alerts.low_data_quality_threshold
            }
        } 