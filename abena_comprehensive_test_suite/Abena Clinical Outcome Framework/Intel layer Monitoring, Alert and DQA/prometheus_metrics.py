# =============================================================================
# 2. PROMETHEUS METRICS FOR REAL-TIME MONITORING
# =============================================================================

from prometheus_client import Counter, Histogram, Gauge

class PrometheusMetrics:
    def __init__(self):
        # Integration metrics
        self.integration_requests = Counter(
            'abena_integration_requests_total',
            'Total integration requests',
            ['source_system', 'endpoint', 'status']
        )
        
        self.integration_response_time = Histogram(
            'abena_integration_response_time_seconds',
            'Integration response time',
            ['source_system', 'endpoint']
        )
        
        self.integration_errors = Counter(
            'abena_integration_errors_total',
            'Total integration errors',
            ['source_system', 'error_type']
        )
        
        # Data quality metrics
        self.data_quality_score = Gauge(
            'abena_data_quality_score',
            'Data quality score',
            ['source_system', 'data_type', 'metric_type']
        )
        
        self.records_processed = Counter(
            'abena_records_processed_total',
            'Total records processed',
            ['source_system', 'data_type', 'status']
        )
        
        # System health metrics
        self.system_health = Gauge(
            'abena_system_health_score',
            'System health score',
            ['component']
        )
        
        self.active_alerts = Gauge(
            'abena_active_alerts',
            'Number of active alerts',
            ['severity']
        ) 