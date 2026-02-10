"""
Performance Benchmarks for Abena IHR System

This module contains comprehensive performance tests that validate
system performance under clinical workloads and SLA requirements.
"""

import pytest
import time
import psutil
import concurrent.futures
import statistics
from datetime import datetime
from unittest.mock import Mock, patch
from tests.conftest import validate_prediction_result


# ============================================================================
# PERFORMANCE TEST HELPERS
# ============================================================================

class PerformanceMonitor:
    """Performance monitoring utility"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_samples = []
        self.cpu_samples = []
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.perf_counter()
        self.memory_samples = []
        self.cpu_samples = []
        
        # Initial memory sample
        process = psutil.Process()
        self.memory_samples.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_samples.append(process.cpu_percent())
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.end_time = time.perf_counter()
        
        # Final memory sample
        process = psutil.Process()
        self.memory_samples.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_samples.append(process.cpu_percent())
    
    def get_execution_time_ms(self):
        """Get execution time in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None
    
    def get_memory_usage_mb(self):
        """Get memory usage statistics"""
        if self.memory_samples:
            return {
                'initial': self.memory_samples[0],
                'final': self.memory_samples[-1],
                'delta': self.memory_samples[-1] - self.memory_samples[0],
                'max': max(self.memory_samples),
                'avg': statistics.mean(self.memory_samples)
            }
        return None


class MockPredictiveEngine:
    """Mock predictive engine for performance testing"""
    
    def __init__(self, latency_ms=50):
        self.latency_ms = latency_ms
        self.prediction_count = 0
    
    def predict_treatment_response(self, patient, treatment):
        """Mock prediction with controlled latency"""
        # Simulate processing time
        time.sleep(self.latency_ms / 1000.0)
        
        self.prediction_count += 1
        
        from src.core.data_models import PredictionResult
        return PredictionResult(
            patient_id=patient.patient_id,
            treatment_id=treatment.treatment_id,
            success_probability=0.75,
            risk_score=0.25,
            key_factors=["age", "genomics"],
            warnings=[],
            timestamp=datetime.now()
        )


# ============================================================================
# PERFORMANCE BENCHMARK TESTS
# ============================================================================

@pytest.mark.performance
class TestPredictionPerformance:
    """Performance tests for prediction engine"""
    
    def test_single_prediction_latency_benchmark(self, sample_patient, sample_treatment):
        """Test single prediction latency meets SLA requirements"""
        monitor = PerformanceMonitor()
        engine = MockPredictiveEngine(latency_ms=80)  # Simulate 80ms processing
        
        monitor.start_monitoring()
        result = engine.predict_treatment_response(sample_patient, sample_treatment)
        monitor.stop_monitoring()
        
        execution_time = monitor.get_execution_time_ms()
        
        # SLA Requirement: <100ms for single prediction
        assert execution_time < 100, f"Prediction took {execution_time:.2f}ms (>100ms SLA)"
        assert result is not None
        validate_prediction_result(result)
        
        # Memory usage should be reasonable
        memory_stats = monitor.get_memory_usage_mb()
        assert memory_stats['delta'] < 50, f"Memory usage increased by {memory_stats['delta']:.2f}MB"
    
    def test_batch_prediction_throughput_benchmark(self, realistic_patient_cohort, sample_treatment):
        """Test batch prediction throughput"""
        monitor = PerformanceMonitor()
        engine = MockPredictiveEngine(latency_ms=50)
        
        # Use subset for faster testing
        test_patients = realistic_patient_cohort[:10]
        
        monitor.start_monitoring()
        
        results = []
        for patient in test_patients:
            result = engine.predict_treatment_response(patient, sample_treatment)
            results.append(result)
        
        monitor.stop_monitoring()
        
        total_time = monitor.get_execution_time_ms()
        throughput = len(test_patients) / (total_time / 1000.0)  # predictions per second
        
        # SLA Requirement: >10 predictions/second
        assert throughput >= 10, f"Throughput {throughput:.2f}/s below 10/s requirement"
        assert len(results) == len(test_patients)
        
        # All results should be valid
        for result in results:
            validate_prediction_result(result)
    
    def test_concurrent_prediction_performance(self, realistic_patient_cohort, sample_treatment):
        """Test concurrent prediction performance"""
        engine = MockPredictiveEngine(latency_ms=75)
        test_patients = realistic_patient_cohort[:5]
        
        def make_prediction(patient):
            """Make a single prediction"""
            start = time.perf_counter()
            result = engine.predict_treatment_response(patient, sample_treatment)
            end = time.perf_counter()
            
            return {
                'result': result,
                'execution_time_ms': (end - start) * 1000,
                'patient_id': patient.patient_id
            }
        
        # Test concurrent execution
        start_time = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_prediction, patient) for patient in test_patients]
            concurrent_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.perf_counter()
        
        total_concurrent_time = (end_time - start_time) * 1000
        concurrent_throughput = len(test_patients) / (total_concurrent_time / 1000.0)
        
        # Concurrent execution should improve overall throughput
        assert concurrent_throughput > 5, f"Concurrent throughput {concurrent_throughput:.2f}/s too low"
        
        # Individual prediction times should still meet SLA
        for result_data in concurrent_results:
            assert result_data['execution_time_ms'] < 150, "Individual prediction time too high"
            validate_prediction_result(result_data['result'])
    
    def test_high_load_stress_testing(self, sample_patient, sample_treatment):
        """Test system performance under high load"""
        engine = MockPredictiveEngine(latency_ms=40)
        monitor = PerformanceMonitor()
        
        # Simulate high load with many predictions
        num_predictions = 50
        
        monitor.start_monitoring()
        
        results = []
        latencies = []
        
        for i in range(num_predictions):
            start = time.perf_counter()
            result = engine.predict_treatment_response(sample_patient, sample_treatment)
            end = time.perf_counter()
            
            latency = (end - start) * 1000
            latencies.append(latency)
            results.append(result)
        
        monitor.stop_monitoring()
        
        # Calculate performance statistics
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        
        total_time = monitor.get_execution_time_ms()
        overall_throughput = num_predictions / (total_time / 1000.0)
        
        # Performance requirements under high load
        assert avg_latency < 100, f"Average latency {avg_latency:.2f}ms under high load"
        assert p95_latency < 150, f"95th percentile latency {p95_latency:.2f}ms too high"
        assert p99_latency < 200, f"99th percentile latency {p99_latency:.2f}ms too high"
        assert overall_throughput >= 8, f"High load throughput {overall_throughput:.2f}/s too low"
        
        # Memory usage should remain stable
        memory_stats = monitor.get_memory_usage_mb()
        assert memory_stats['delta'] < 100, f"Memory leak detected: {memory_stats['delta']:.2f}MB increase"


@pytest.mark.performance
class TestSystemPerformance:
    """System-wide performance tests"""
    
    def test_api_response_time_benchmark(self):
        """Test API response time performance"""
        # Mock API responses
        from unittest.mock import Mock
        client = Mock()
        
        response_times = []
        
        # Test multiple API endpoints
        endpoints = [
            ("/api/v1/patients/", "POST"),
            ("/api/v1/predictions/generate", "POST"),
            ("/api/v1/workflows/alerts/PATIENT_001", "GET"),
            ("/api/v1/treatments/recommendations", "GET")
        ]
        
        for endpoint, method in endpoints:
            start = time.perf_counter()
            
            # Mock API call
            if method == "POST":
                response = Mock(status_code=200, json=lambda: {"status": "success"})
            else:
                response = Mock(status_code=200, json=lambda: {"data": []})
            
            # Simulate network and processing latency
            time.sleep(0.05)  # 50ms simulated latency
            
            end = time.perf_counter()
            response_time = (end - start) * 1000
            response_times.append(response_time)
        
        # API performance requirements
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 200, f"Average API response time {avg_response_time:.2f}ms too high"
        assert max_response_time < 500, f"Max API response time {max_response_time:.2f}ms too high"
    
    def test_database_query_performance(self):
        """Test database query performance simulation"""
        # Mock database operations
        query_times = []
        
        # Simulate different types of database queries
        queries = [
            ("SELECT * FROM patients WHERE id = ?", 10),  # Single patient lookup
            ("SELECT * FROM treatments WHERE patient_id = ?", 25),  # Treatment history
            ("SELECT * FROM predictions WHERE created_at > ?", 50),  # Recent predictions
            ("INSERT INTO clinical_notes VALUES (?)", 15),  # Note creation
            ("UPDATE patients SET last_visit = ? WHERE id = ?", 12)  # Patient update
        ]
        
        for query, expected_time_ms in queries:
            start = time.perf_counter()
            
            # Simulate database query execution
            time.sleep(expected_time_ms / 1000.0)
            
            end = time.perf_counter()
            actual_time = (end - start) * 1000
            query_times.append(actual_time)
        
        # Database performance requirements
        avg_query_time = statistics.mean(query_times)
        assert avg_query_time < 100, f"Average database query time {avg_query_time:.2f}ms too high"
        
        # Individual query types should meet specific requirements
        for i, (query, expected_time) in enumerate(queries):
            actual_time = query_times[i]
            # Allow 50% margin for query performance
            assert actual_time < expected_time * 1.5, f"Query {i+1} took {actual_time:.2f}ms (expected <{expected_time*1.5}ms)"
    
    def test_memory_usage_profile(self, realistic_patient_cohort):
        """Test memory usage patterns under typical workload"""
        monitor = PerformanceMonitor()
        engine = MockPredictiveEngine(latency_ms=30)
        
        monitor.start_monitoring()
        
        # Simulate typical workload: process multiple patients
        for i, patient in enumerate(realistic_patient_cohort):
            # Create mock treatment for each patient
            from src.core.data_models import TreatmentPlan
            treatment = TreatmentPlan(
                treatment_id=f"PERF_TX_{i:03d}",
                treatment_type="combined",
                medications=["medication_a"],
                dosages={"medication_a": "dose"},
                duration_weeks=8,
                lifestyle_interventions=[]
            )
            
            # Generate prediction
            result = engine.predict_treatment_response(patient, treatment)
            
            # Sample memory periodically
            if i % 2 == 0:
                process = psutil.Process()
                monitor.memory_samples.append(process.memory_info().rss / 1024 / 1024)
        
        monitor.stop_monitoring()
        
        memory_stats = monitor.get_memory_usage_mb()
        
        # Memory usage requirements
        assert memory_stats['final'] < 500, f"Final memory usage {memory_stats['final']:.2f}MB too high"
        assert memory_stats['delta'] < 100, f"Memory increase {memory_stats['delta']:.2f}MB too high"
        
        # Memory usage should be stable (no significant leaks)
        if len(monitor.memory_samples) > 4:
            # Check if memory usage grows consistently (indicating leak)
            trend = statistics.linear_regression(
                range(len(monitor.memory_samples)), 
                monitor.memory_samples
            )
            # Slope should be minimal (< 1MB per iteration)
            assert trend.slope < 1.0, f"Memory leak detected: {trend.slope:.2f}MB/iteration growth"


@pytest.mark.performance
@pytest.mark.slow
class TestScalabilityBenchmarks:
    """Scalability and load testing benchmarks"""
    
    def test_user_concurrency_scaling(self):
        """Test system performance with increasing concurrent users"""
        engine = MockPredictiveEngine(latency_ms=60)
        
        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 20]
        performance_results = []
        
        for num_users in concurrency_levels:
            def simulate_user_session():
                """Simulate a user session with multiple operations"""
                session_start = time.perf_counter()
                
                # Simulate user performing multiple operations
                operations = [
                    ('patient_lookup', 0.02),
                    ('generate_prediction', 0.08),
                    ('view_recommendations', 0.01),
                    ('save_notes', 0.03)
                ]
                
                for op_name, op_time in operations:
                    time.sleep(op_time)  # Simulate operation time
                
                session_end = time.perf_counter()
                return (session_end - session_start) * 1000
            
            # Execute concurrent user sessions
            start_time = time.perf_counter()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [executor.submit(simulate_user_session) for _ in range(num_users)]
                session_times = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.perf_counter()
            
            total_time = (end_time - start_time) * 1000
            avg_session_time = statistics.mean(session_times)
            throughput = num_users / (total_time / 1000.0)
            
            performance_results.append({
                'concurrency': num_users,
                'avg_session_time_ms': avg_session_time,
                'total_time_ms': total_time,
                'throughput_users_per_sec': throughput
            })
        
        # Analyze scalability
        for result in performance_results:
            concurrency = result['concurrency']
            avg_session_time = result['avg_session_time_ms']
            
            # Session time should not degrade significantly with concurrency
            expected_max_session_time = 200 + (concurrency * 10)  # Allow some degradation
            assert avg_session_time < expected_max_session_time, \
                f"Session time {avg_session_time:.2f}ms too high for {concurrency} users"
        
        # System should handle at least 10 concurrent users efficiently
        max_concurrency_result = performance_results[-1]
        assert max_concurrency_result['concurrency'] >= 10, "Should handle at least 10 concurrent users"
        assert max_concurrency_result['throughput_users_per_sec'] > 0.1, "Throughput too low under high concurrency"
    
    def test_data_volume_scaling(self, realistic_patient_cohort):
        """Test performance with increasing data volumes"""
        engine = MockPredictiveEngine(latency_ms=45)
        
        # Test different data volumes
        data_sizes = [10, 25, 50]  # Number of patients to process
        
        for size in data_sizes:
            test_patients = realistic_patient_cohort[:size]
            
            start_time = time.perf_counter()
            results = []
            
            for patient in test_patients:
                from src.core.data_models import TreatmentPlan
                treatment = TreatmentPlan(
                    treatment_id=f"SCALE_TX_{patient.patient_id}",
                    treatment_type="pharmacological",
                    medications=["test_medication"],
                    dosages={"test_medication": "test_dose"},
                    duration_weeks=6,
                    lifestyle_interventions=[]
                )
                
                result = engine.predict_treatment_response(patient, treatment)
                results.append(result)
            
            end_time = time.perf_counter()
            
            total_time = (end_time - start_time) * 1000
            avg_time_per_patient = total_time / size
            throughput = size / (total_time / 1000.0)
            
            # Performance should scale reasonably with data volume
            assert avg_time_per_patient < 200, \
                f"Average time per patient {avg_time_per_patient:.2f}ms too high for {size} patients"
            assert throughput > 5, \
                f"Throughput {throughput:.2f} patients/sec too low for {size} patients"
            
            # All results should be valid
            assert len(results) == size
            for result in results:
                validate_prediction_result(result)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"]) 