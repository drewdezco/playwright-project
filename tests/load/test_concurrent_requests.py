"""
Concurrent request testing patterns.
Tests concurrent API calls, thread pool execution, and measuring concurrent performance.
"""
import pytest
import time
from playwright.sync_api import APIRequestContext
from utils.load_generator import LoadGenerator, calculate_metrics
from utils.test_helpers import assert_response_time


@pytest.mark.load
class TestConcurrentRequests:
    """Test concurrent API requests."""
    
    def test_concurrent_get_requests(self, api_request_context: APIRequestContext):
        """Test concurrent GET requests."""
        def make_request():
            start_time = time.time()
            response = api_request_context.get("/posts/1")
            end_time = time.time()
            
            assert response.status == 200
            return {
                "status": response.status,
                "response_time": end_time - start_time,
                "data": response.json()
            }
        
        generator = LoadGenerator(max_workers=10)
        num_requests = 50
        
        results = generator.generate_concurrent_requests(
            make_request,
            num_requests
        )
        
        # Calculate metrics
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) == num_requests
        
        # Check response times
        response_times = [
            r["result"]["response_time"]
            for r in successful_results
        ]
        
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 2.0, f"Average response time {avg_response_time:.3f}s exceeds 2.0s"
    
    def test_concurrent_post_requests(self, api_request_context: APIRequestContext):
        """Test concurrent POST requests."""
        from utils.test_helpers import generate_test_post
        
        def make_post_request():
            test_data = generate_test_post()
            test_data["userId"] = 1
            
            start_time = time.time()
            response = api_request_context.post("/posts", data=test_data)
            end_time = time.time()
            
            assert response.status == 201
            return {
                "status": response.status,
                "response_time": end_time - start_time,
                "data": response.json()
            }
        
        generator = LoadGenerator(max_workers=5)
        num_requests = 20
        
        results = generator.generate_concurrent_requests(
            make_post_request,
            num_requests
        )
        
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) == num_requests
    
    def test_high_concurrency(self, api_request_context: APIRequestContext):
        """Test high concurrency scenarios."""
        def make_request():
            response = api_request_context.get("/posts/1")
            return response.status == 200
        
        generator = LoadGenerator(max_workers=20)
        num_requests = 100
        
        start_time = time.time()
        results = generator.generate_concurrent_requests(
            make_request,
            num_requests
        )
        end_time = time.time()
        
        duration = end_time - start_time
        successful = sum(1 for r in results if r["success"])
        
        assert successful == num_requests
        assert duration < 30, f"High concurrency test took {duration:.2f}s"
        
        # Calculate requests per second
        rps = num_requests / duration
        assert rps >= 5, f"Requests per second {rps:.2f} is below 5 req/s"
    
    def test_concurrent_mixed_operations(self, api_request_context: APIRequestContext):
        """Test concurrent mixed operations (GET, POST, PUT, DELETE)."""
        operations = []
        
        def get_operation():
            response = api_request_context.get("/posts/1")
            return {"operation": "GET", "status": response.status}
        
        def post_operation():
            test_data = {"title": "Test", "body": "Body", "userId": 1}
            response = api_request_context.post("/posts", data=test_data)
            return {"operation": "POST", "status": response.status}
        
        operations.extend([get_operation] * 30)
        operations.extend([post_operation] * 10)
        
        generator = LoadGenerator(max_workers=10)
        
        results = []
        for operation in operations:
            result = generator.generate_concurrent_requests(operation, 1)
            results.extend(result)
        
        successful = sum(1 for r in results if r["success"])
        assert successful == len(operations)


@pytest.mark.load
class TestAsyncConcurrentRequests:
    """Test async concurrent requests."""
    
    @pytest.mark.asyncio
    async def test_async_concurrent_requests(self, api_request_context: APIRequestContext):
        """Test concurrent requests using asyncio."""
        import asyncio
        from playwright.async_api import async_playwright
        
        async def make_async_request():
            async with async_playwright() as p:
                api_context = await p.request.new_context(
                    base_url="https://jsonplaceholder.typicode.com"
                )
                
                response = await api_context.get("/posts/1")
                await api_context.dispose()
                return response.status == 200
        
        generator = LoadGenerator()
        num_requests = 30
        
        results = await generator.generate_async_requests(
            make_async_request,
            num_requests
        )
        
        successful = sum(1 for r in results if r["success"])
        assert successful == num_requests


@pytest.mark.load
class TestConcurrentPerformance:
    """Test performance under concurrent load."""
    
    def test_response_time_under_load(self, api_request_context: APIRequestContext):
        """Test response times under concurrent load."""
        def make_timed_request():
            start_time = time.time()
            response = api_request_context.get("/posts/1")
            end_time = time.time()
            
            return {
                "success": response.status == 200,
                "response_time": end_time - start_time,
                "status": response.status
            }
        
        generator = LoadGenerator(max_workers=15)
        num_requests = 75
        
        results = generator.generate_concurrent_requests(
            make_timed_request,
            num_requests
        )
        
        # Calculate performance metrics
        successful_results = [r for r in results if r["success"]]
        response_times = [
            r["result"]["response_time"]
            for r in successful_results
        ]
        
        metrics = calculate_metrics([
            {"success": True, "response_time": rt}
            for rt in response_times
        ])
        
        # Assert performance thresholds
        assert metrics["avg_response_time"] < 1.0, (
            f"Average response time {metrics['avg_response_time']:.3f}s exceeds 1.0s"
        )
        assert metrics.get("p95_response_time", 0) < 2.0, (
            f"P95 response time {metrics.get('p95_response_time', 0):.3f}s exceeds 2.0s"
        )
    
    def test_throughput_measurement(self, api_request_context: APIRequestContext):
        """Measure throughput under concurrent load."""
        def make_request():
            response = api_request_context.get("/posts/1")
            return response.status == 200
        
        generator = LoadGenerator(max_workers=10)
        num_requests = 100
        
        start_time = time.time()
        results = generator.generate_concurrent_requests(
            make_request,
            num_requests
        )
        end_time = time.time()
        
        duration = end_time - start_time
        throughput = num_requests / duration
        
        successful = sum(1 for r in results if r["success"])
        success_rate = (successful / num_requests) * 100
        
        assert throughput >= 10, f"Throughput {throughput:.2f} req/s is below 10 req/s"
        assert success_rate >= 95, f"Success rate {success_rate:.1f}% is below 95%"
    
    def test_bottleneck_identification(self, api_request_context: APIRequestContext):
        """Identify bottlenecks under concurrent load."""
        endpoint_times = {}
        
        endpoints = ["/posts/1", "/users/1", "/comments/1"]
        
        for endpoint in endpoints:
            def make_request():
                start_time = time.time()
                response = api_request_context.get(endpoint)
                end_time = time.time()
                return {
                    "status": response.status,
                    "response_time": end_time - start_time
                }
            
            generator = LoadGenerator(max_workers=10)
            results = generator.generate_concurrent_requests(make_request, 20)
            
            successful_results = [r for r in results if r["success"]]
            response_times = [
                r["result"]["response_time"]
                for r in successful_results
            ]
            
            endpoint_times[endpoint] = {
                "avg": sum(response_times) / len(response_times),
                "max": max(response_times),
                "min": min(response_times)
            }
        
        # Identify slowest endpoint
        slowest_endpoint = max(
            endpoint_times.items(),
            key=lambda x: x[1]["avg"]
        )
        
        # Assert no endpoint is excessively slow
        assert slowest_endpoint[1]["avg"] < 2.0, (
            f"Slowest endpoint {slowest_endpoint[0]} has avg response time "
            f"{slowest_endpoint[1]['avg']:.3f}s"
        )

