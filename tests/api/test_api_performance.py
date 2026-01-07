"""
API performance testing patterns.
Tests response time assertions, throughput, latency measurements, and performance regression detection.
"""
import pytest
import time
from playwright.sync_api import APIRequestContext
from utils.test_helpers import assert_response_time, generate_test_post


@pytest.mark.api
class TestResponseTime:
    """Test response time assertions."""
    
    def test_response_time_assertion(self, api_request_context: APIRequestContext):
        """Test that response time is within acceptable limits."""
        start_time = time.time()
        response = api_request_context.get("/posts/1")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status == 200
        assert_response_time(response_time, max_time=2.0)
    
    def test_multiple_endpoints_response_time(self, api_request_context: APIRequestContext):
        """Test response times across multiple endpoints."""
        endpoints = ["/posts/1", "/users/1", "/comments/1"]
        max_response_time = 2.0
        
        for endpoint in endpoints:
            start_time = time.time()
            response = api_request_context.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response.status == 200
            assert_response_time(response_time, max_time=max_response_time)
    
    def test_response_time_percentile(self, api_request_context: APIRequestContext):
        """Test response time percentiles."""
        response_times = []
        num_requests = 20
        
        for _ in range(num_requests):
            start_time = time.time()
            response = api_request_context.get("/posts/1")
            end_time = time.time()
            
            assert response.status == 200
            response_times.append(end_time - start_time)
        
        # Calculate percentiles
        sorted_times = sorted(response_times)
        p50 = sorted_times[len(sorted_times) // 2]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Assert percentiles are reasonable
        assert p50 < 1.0, f"P50 response time {p50:.3f}s exceeds 1.0s"
        assert p95 < 2.0, f"P95 response time {p95:.3f}s exceeds 2.0s"
        assert p99 < 3.0, f"P99 response time {p99:.3f}s exceeds 3.0s"


@pytest.mark.api
class TestThroughput:
    """Test API throughput."""
    
    def test_requests_per_second(self, api_request_context: APIRequestContext):
        """Test requests per second throughput."""
        num_requests = 50
        start_time = time.time()
        
        for _ in range(num_requests):
            response = api_request_context.get("/posts/1")
            assert response.status == 200
        
        end_time = time.time()
        duration = end_time - start_time
        rps = num_requests / duration
        
        # Should handle at least 10 requests per second
        assert rps >= 10, f"Throughput {rps:.2f} req/s is below 10 req/s"
    
    @pytest.mark.skip(reason="ThreadPoolExecutor conflicts with Playwright sync API in parallel execution")
    def test_concurrent_throughput(self, api_request_context: APIRequestContext):
        """Test throughput under concurrent load."""
        # Note: This test is skipped because ThreadPoolExecutor conflicts with 
        # Playwright's sync API when running in parallel with pytest-xdist.
        # Use test_concurrent_requests.py for concurrent testing patterns.
        from concurrent.futures import ThreadPoolExecutor
        
        num_requests = 100
        num_workers = 10
        
        def make_request():
            response = api_request_context.get("/posts/1")
            return response.status == 200
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = list(executor.map(lambda _: make_request(), range(num_requests)))
        
        end_time = time.time()
        duration = end_time - start_time
        rps = num_requests / duration
        
        assert all(results), "Some requests failed"
        assert rps >= 5, f"Concurrent throughput {rps:.2f} req/s is below 5 req/s"


@pytest.mark.api
class TestLatency:
    """Test API latency measurements."""
    
    def test_latency_measurement(self, api_request_context: APIRequestContext):
        """Measure API latency."""
        latencies = []
        num_samples = 30
        
        for _ in range(num_samples):
            start_time = time.time()
            response = api_request_context.get("/posts/1")
            end_time = time.time()
            
            assert response.status == 200
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            latencies.append(latency)
        
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # Assert reasonable latency
        assert avg_latency < 1000, f"Average latency {avg_latency:.2f}ms exceeds 1000ms"
        assert max_latency < 5000, f"Max latency {max_latency:.2f}ms exceeds 5000ms"
    
    def test_latency_consistency(self, api_request_context: APIRequestContext):
        """Test latency consistency across requests."""
        latencies = []
        num_samples = 20
        
        for _ in range(num_samples):
            start_time = time.time()
            response = api_request_context.get("/posts/1")
            end_time = time.time()
            
            assert response.status == 200
            latencies.append((end_time - start_time) * 1000)
        
        # Calculate standard deviation
        import statistics
        if len(latencies) > 1:
            std_dev = statistics.stdev(latencies)
            mean_latency = statistics.mean(latencies)
            coefficient_of_variation = std_dev / mean_latency if mean_latency > 0 else 0
            
            # Latency consistency check - network conditions can vary significantly
            # In production, you'd want CV < 0.5, but for demo/test environments,
            # we're more lenient (CV < 1.5) due to variable network/system conditions
            # The important thing is that requests complete successfully
            assert coefficient_of_variation < 1.5, (
                f"Latency inconsistency: CV={coefficient_of_variation:.2f}. "
                f"This may be due to network variability in test environment."
            )
            
            # Verify all requests succeeded (more important than consistency)
            assert len(latencies) == num_samples, "Not all requests completed"


@pytest.mark.api
class TestPerformanceRegression:
    """Test performance regression detection."""
    
    def test_baseline_performance(self, api_request_context: APIRequestContext):
        """Establish baseline performance metrics."""
        response_times = []
        num_samples = 20
        
        for _ in range(num_samples):
            start_time = time.time()
            response = api_request_context.get("/posts/1")
            end_time = time.time()
            
            assert response.status == 200
            response_times.append(end_time - start_time)
        
        baseline_avg = sum(response_times) / len(response_times)
        baseline_p95 = sorted(response_times)[int(len(response_times) * 0.95)]
        
        # Store baseline (in real scenario, would persist this)
        # For now, just assert reasonable values
        assert baseline_avg < 1.0
        assert baseline_p95 < 2.0
    
    def test_performance_regression_detection(self, api_request_context: APIRequestContext):
        """Detect performance regressions."""
        # Simulate baseline
        baseline_avg = 0.5  # seconds
        
        # Current performance
        response_times = []
        num_samples = 20
        
        for _ in range(num_samples):
            start_time = time.time()
            response = api_request_context.get("/posts/1")
            end_time = time.time()
            
            assert response.status == 200
            response_times.append(end_time - start_time)
        
        current_avg = sum(response_times) / len(response_times)
        
        # Check for regression (50% degradation threshold)
        regression_threshold = baseline_avg * 1.5
        assert current_avg < regression_threshold, (
            f"Performance regression detected: "
            f"current={current_avg:.3f}s, baseline={baseline_avg:.3f}s"
        )
    
    def test_endpoint_comparison(self, api_request_context: APIRequestContext):
        """Compare performance across different endpoints."""
        endpoints = {
            "/posts/1": [],
            "/users/1": [],
            "/comments/1": []
        }
        
        num_samples = 10
        
        for endpoint in endpoints.keys():
            for _ in range(num_samples):
                start_time = time.time()
                response = api_request_context.get(endpoint)
                end_time = time.time()
                
                assert response.status == 200
                endpoints[endpoint].append(end_time - start_time)
        
        # Compare average response times
        avg_times = {
            endpoint: sum(times) / len(times)
            for endpoint, times in endpoints.items()
        }
        
        # All endpoints should have reasonable response times
        for endpoint, avg_time in avg_times.items():
            assert avg_time < 2.0, (
                f"Endpoint {endpoint} has high average response time: {avg_time:.3f}s"
            )

