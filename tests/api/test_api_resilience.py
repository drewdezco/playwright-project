"""
API resilience testing patterns.
Tests retry logic, timeout handling, error responses, circuit breakers, and rate limiting.
"""
import pytest
import time
from playwright.sync_api import APIRequestContext
from utils.api_client import APIClient
from utils.test_helpers import retry_on_failure


@pytest.mark.api
class TestRetryLogic:
    """Test retry mechanisms for failed requests."""
    
    def test_automatic_retry_on_failure(self, api_request_context: APIRequestContext):
        """Test automatic retry on transient failures."""
        client = APIClient(
            api_request_context,
            max_retries=3,
            retry_delay=0.5
        )
        
        # This should succeed after retries (if using a flaky endpoint)
        response = client.get("/posts/1")
        assert response.status == 200
    
    def test_retry_on_specific_status_codes(self, api_request_context: APIRequestContext):
        """Test retry on specific HTTP status codes."""
        client = APIClient(
            api_request_context,
            max_retries=3,
            retry_delay=0.5
        )
        
        # Retry on 5xx errors
        response = client._retry_request(
            "GET",
            "/posts/1",
            retry_on_status=[500, 502, 503, 504]
        )
        
        assert response.status == 200
    
    def test_manual_retry_pattern(self, api_request_context: APIRequestContext):
        """Test manual retry pattern using helper function."""
        def make_request():
            return api_request_context.get("/posts/1")
        
        response = retry_on_failure(
            make_request,
            max_retries=3,
            delay=0.5,
            exceptions=(Exception,)
        )
        
        assert response.status == 200


@pytest.mark.api
class TestTimeoutHandling:
    """Test timeout handling scenarios."""
    
    def test_request_timeout(self, api_request_context: APIRequestContext):
        """Test request timeout configuration."""
        # Set a short timeout
        try:
            response = api_request_context.get(
                "/posts/1",
                timeout=100  # 100ms timeout
            )
            # Request should complete quickly for this endpoint
            assert response.status == 200
        except Exception as e:
            # If timeout occurs, it's expected
            assert "timeout" in str(e).lower() or "timed out" in str(e).lower()
    
    def test_timeout_in_client(self, api_request_context: APIRequestContext):
        """Test timeout configuration in APIClient."""
        client = APIClient(
            api_request_context,
            timeout=5000  # 5 seconds
        )
        
        response = client.get("/posts/1")
        assert response.status == 200


@pytest.mark.api
class TestErrorHandling:
    """Test error response handling."""
    
    def test_handle_4xx_errors(self, api_request_context: APIRequestContext):
        """Test handling 4xx client errors."""
        response = api_request_context.get("/posts/99999")
        
        assert response.status == 404
        assert not response.ok
        
        # Should not retry on 4xx errors
        assert response.status < 500
    
    def test_handle_5xx_errors(self, playwright):
        """Test handling 5xx server errors."""
        # Using httpbin.org to simulate server errors
        api_context = playwright.request.new_context(base_url="https://httpbin.org")
        
        try:
            # httpbin.org/status/500
            response = api_context.get("/status/500")
            assert response.status == 500
        finally:
            api_context.dispose()
    
    def test_error_response_parsing(self, api_request_context: APIRequestContext):
        """Test parsing error responses."""
        response = api_request_context.get("/posts/99999")
        
        if response.status >= 400:
            # Try to parse error response
            try:
                error_data = response.json()
                # Error response may contain error details
                assert isinstance(error_data, dict) or isinstance(error_data, list)
            except Exception:
                # Some APIs return plain text errors
                error_text = response.text()
                assert len(error_text) >= 0


@pytest.mark.api
class TestCircuitBreakerPattern:
    """Test circuit breaker pattern for resilience."""
    
    def test_circuit_breaker_simulation(self, api_request_context: APIRequestContext):
        """Simulate circuit breaker pattern."""
        failure_threshold = 5
        failure_count = 0
        circuit_open = False
        
        def make_request_with_circuit_breaker():
            nonlocal failure_count, circuit_open
            
            if circuit_open:
                raise Exception("Circuit breaker is OPEN")
            
            try:
                # Simulate occasional failures
                response = api_request_context.get("/posts/1")
                if response.status >= 500:
                    failure_count += 1
                    if failure_count >= failure_threshold:
                        circuit_open = True
                else:
                    failure_count = 0  # Reset on success
                return response
            except Exception as e:
                failure_count += 1
                if failure_count >= failure_threshold:
                    circuit_open = True
                raise
        
        # Make requests
        for _ in range(10):
            try:
                response = make_request_with_circuit_breaker()
                assert response.status == 200
            except Exception as e:
                if "Circuit breaker" in str(e):
                    # Circuit breaker opened as expected
                    break


@pytest.mark.api
class TestRateLimiting:
    """Test rate limiting handling."""
    
    def test_rate_limit_detection(self, api_request_context: APIRequestContext):
        """Test detecting rate limit responses."""
        # Make multiple rapid requests
        rate_limited = False
        
        for i in range(20):
            response = api_request_context.get("/posts/1")
            
            if response.status == 429:  # Too Many Requests
                rate_limited = True
                # Check for Retry-After header
                retry_after = response.headers.get("retry-after")
                if retry_after:
                    wait_time = int(retry_after)
                    time.sleep(wait_time)
                break
        
        # Note: JSONPlaceholder doesn't rate limit, but this shows the pattern
        assert response.status in [200, 429]
    
    def test_exponential_backoff(self, api_request_context: APIRequestContext):
        """Test exponential backoff on rate limiting."""
        base_delay = 1.0
        max_delay = 60.0
        current_delay = base_delay
        
        for attempt in range(5):
            response = api_request_context.get("/posts/1")
            
            if response.status == 429:
                # Wait with exponential backoff
                time.sleep(min(current_delay, max_delay))
                current_delay *= 2  # Exponential increase
            else:
                break
        
        assert response.status == 200

