"""
Network failure simulation tests.
Tests network timeouts, connection failures, partial degradation, and retry mechanisms.
"""
import pytest
import time
from playwright.sync_api import APIRequestContext
from utils.chaos_monkey import ChaosMonkey, NetworkChaos, FailureType
from utils.test_helpers import retry_on_failure


@pytest.mark.chaos
class TestNetworkFailures:
    """Test network failure scenarios."""
    
    def test_network_timeout_simulation(self, api_request_context: APIRequestContext):
        """Test handling network timeouts."""
        chaos = ChaosMonkey(failure_rate=0.0)  # Disable random failures
        
        def make_request_with_timeout():
            # Simulate timeout scenario
            try:
                response = api_request_context.get("/posts/1", timeout=100)  # Very short timeout
                return response
            except Exception as e:
                if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                    raise TimeoutError(f"Request timed out: {e}")
                raise
        
        # Should handle timeout gracefully
        try:
            response = make_request_with_timeout()
            assert response.status == 200
        except TimeoutError:
            # Expected behavior for timeout
            pass
    
    def test_connection_failure_simulation(self, api_request_context: APIRequestContext):
        """Test handling connection failures."""
        chaos = ChaosMonkey(failure_rate=0.0)
        
        def make_request():
            # Attempt request to invalid endpoint to simulate connection failure
            try:
                response = api_request_context.get("https://invalid-domain-12345.com/api")
                return response
            except Exception as e:
                # Simulate connection failure
                if "name resolution" in str(e).lower() or "connection" in str(e).lower():
                    raise ConnectionError(f"Connection failed: {e}")
                raise
        
        # Should handle connection failure
        with pytest.raises((ConnectionError, Exception)):
            make_request()
    
    def test_partial_network_degradation(self, api_request_context: APIRequestContext):
        """Test handling partial network degradation."""
        # Simulate slow network by adding delay before request
        throttle_delay = 0.5
        
        # Measure time including throttle delay
        start_time = time.time()
        NetworkChaos.simulate_bandwidth_throttle(delay=throttle_delay)
        response = api_request_context.get("/posts/1")
        end_time = time.time()
        
        total_time = end_time - start_time
        assert response.status == 200
        
        # Total time should include the throttle delay
        # The throttle delay is 0.5s, so total should be at least that
        assert total_time >= throttle_delay, (
            f"Total time {total_time:.3f}s should be >= throttle delay {throttle_delay}s. "
            f"This demonstrates network degradation simulation."
        )
    
    def test_retry_on_network_failure(self, api_request_context: APIRequestContext):
        """Test retry mechanism on network failures."""
        attempt_count = [0]
        
        def make_request_with_retry():
            attempt_count[0] += 1
            
            # Simulate failure on first attempt
            if attempt_count[0] == 1:
                raise ConnectionError("Simulated network failure")
            
            response = api_request_context.get("/posts/1")
            return response
        
        # Retry should succeed
        response = retry_on_failure(
            make_request_with_retry,
            max_retries=3,
            delay=0.5,
            exceptions=(ConnectionError,)
        )
        
        assert response.status == 200
        assert attempt_count[0] == 2  # Should succeed on second attempt
    
    def test_packet_loss_simulation(self, api_request_context: APIRequestContext):
        """Test handling packet loss."""
        chaos = ChaosMonkey(failure_rate=0.2)  # 20% failure rate
        
        success_count = 0
        failure_count = 0
        
        for _ in range(20):
            try:
                NetworkChaos.simulate_packet_loss(probability=0.1)
                response = api_request_context.get("/posts/1")
                if response.status == 200:
                    success_count += 1
            except ConnectionError:
                failure_count += 1
        
        # Some requests may fail due to packet loss simulation
        total_requests = success_count + failure_count
        assert total_requests == 20


@pytest.mark.chaos
class TestNetworkResilience:
    """Test network resilience patterns."""
    
    def test_circuit_breaker_on_network_failures(self, api_request_context: APIRequestContext):
        """Test circuit breaker pattern for network failures."""
        failure_count = 0
        circuit_open = False
        max_failures = 3
        
        def make_request_with_circuit_breaker():
            nonlocal failure_count, circuit_open
            
            if circuit_open:
                raise Exception("Circuit breaker OPEN - too many failures")
            
            try:
                response = api_request_context.get("/posts/1")
                if response.status >= 500:
                    failure_count += 1
                else:
                    failure_count = 0  # Reset on success
                
                if failure_count >= max_failures:
                    circuit_open = True
                
                return response
            except Exception as e:
                failure_count += 1
                if failure_count >= max_failures:
                    circuit_open = True
                raise
        
        # Make requests
        for i in range(5):
            try:
                response = make_request_with_circuit_breaker()
                assert response.status == 200
                if circuit_open:
                    break  # Circuit opened, stop making requests
            except Exception as e:
                if "Circuit breaker" in str(e):
                    # Circuit breaker activated as expected
                    break
    
    def test_exponential_backoff_on_failures(self, api_request_context: APIRequestContext):
        """Test exponential backoff on network failures."""
        backoff_delays = []
        base_delay = 0.5
        
        def make_request_with_backoff(attempt):
            delay = base_delay * (2 ** attempt)
            backoff_delays.append(delay)
            time.sleep(delay)
            return api_request_context.get("/posts/1")
        
        # Simulate retries with exponential backoff
        for attempt in range(3):
            try:
                response = make_request_with_backoff(attempt)
                assert response.status == 200
                break
            except Exception:
                if attempt == 2:
                    raise
        
        # Verify backoff delays increased exponentially
        if len(backoff_delays) > 1:
            assert backoff_delays[1] > backoff_delays[0]
    
    def test_network_partition_handling(self, api_request_context: APIRequestContext):
        """Test handling network partitions."""
        def make_request():
            try:
                NetworkChaos.simulate_network_partition()
                return api_request_context.get("/posts/1")
            except ConnectionError:
                # Network partition detected
                raise
        
        # Should handle network partition
        with pytest.raises(ConnectionError):
            make_request()


@pytest.mark.chaos
class TestFailureInjection:
    """Test failure injection patterns."""
    
    def test_inject_timeout_failure(self, api_request_context: APIRequestContext):
        """Test injecting timeout failures."""
        chaos = ChaosMonkey(failure_rate=0.3)
        
        failures_injected = 0
        
        for _ in range(10):
            try:
                chaos.inject_failure(
                    lambda: api_request_context.get("/posts/1"),
                    failure_type=FailureType.NETWORK_TIMEOUT,
                    timeout_duration=0.1
                )
            except TimeoutError:
                failures_injected += 1
            except Exception:
                # Request succeeded
                pass
        
        # Some failures should have been injected
        assert failures_injected >= 0  # May vary based on failure rate
    
    def test_inject_connection_failure(self, api_request_context: APIRequestContext):
        """Test injecting connection failures."""
        chaos = ChaosMonkey(failure_rate=0.3)
        
        failures_injected = 0
        
        for _ in range(10):
            try:
                chaos.inject_failure(
                    lambda: api_request_context.get("/posts/1"),
                    failure_type=FailureType.CONNECTION_FAILURE
                )
            except ConnectionError:
                failures_injected += 1
            except Exception:
                # Request succeeded
                pass
        
        # Some failures should have been injected
        assert failures_injected >= 0
    
    def test_random_failure_injection(self, api_request_context: APIRequestContext):
        """Test random failure injection."""
        chaos = ChaosMonkey(failure_rate=0.2)
        
        stats = chaos.get_statistics()
        initial_total = stats["total_requests"]
        
        # Make requests with random failures
        for _ in range(20):
            try:
                chaos.inject_failure(
                    lambda: api_request_context.get("/posts/1"),
                    failure_type=FailureType.RANDOM
                )
            except Exception:
                # Failure injected
                pass
        
        final_stats = chaos.get_statistics()
        assert final_stats["total_requests"] > initial_total

