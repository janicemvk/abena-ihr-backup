# Performance tests for Prediction Engine
import pytest
import time
import concurrent.futures
from src.predictive_analytics.predictive_engine import TreatmentResponsePredictor

class TestPredictionPerformance:
    """Performance tests for prediction engine"""
    
    @pytest.mark.performance
    def test_single_prediction_latency(self, benchmark, sample_patient, sample_treatment, mock_training_data):
        """Test single prediction latency using benchmark fixture"""
        
        predictor = TreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        def make_prediction():
            return predictor.predict_treatment_response(sample_patient, sample_treatment)
        
        # Use benchmark fixture for accurate timing
        result = benchmark(make_prediction)
        
        # Verify the result is valid
        assert result.success_probability is not None
        assert 0 <= result.success_probability <= 1
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_prediction_throughput(self, sample_patient, sample_treatment, mock_training_data):
        """Test concurrent prediction throughput"""
        
        predictor = TreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        def make_prediction():
            return predictor.predict_treatment_response(sample_patient, sample_treatment)
        
        start_time = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_prediction) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.perf_counter()
        
        throughput = len(results) / (end_time - start_time)
        
        # Should handle at least 10 predictions per second
        assert throughput >= 10, f"Throughput {throughput:.2f}/s below 10/s target"
    
    @pytest.mark.performance
    def test_prediction_performance_under_load(self, benchmark, sample_patient, sample_treatment, mock_training_data):
        """Test prediction performance under load using benchmark fixture"""
        
        predictor = TreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        def batch_predictions():
            """Run multiple predictions in sequence"""
            results = []
            for _ in range(10):
                result = predictor.predict_treatment_response(sample_patient, sample_treatment)
                results.append(result)
            return results
        
        # Use benchmark fixture for accurate timing
        results = benchmark(batch_predictions)
        
        # Verify all results are valid
        assert len(results) == 10
        for result in results:
            assert result.success_probability is not None
            assert 0 <= result.success_probability <= 1 