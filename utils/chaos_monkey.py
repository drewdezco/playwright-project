"""
Chaos engineering utilities for simulating failures and testing system resilience.
"""
import random
import time
import logging
from typing import Callable, Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures to simulate."""
    NETWORK_TIMEOUT = "network_timeout"
    CONNECTION_FAILURE = "connection_failure"
    SLOW_RESPONSE = "slow_response"
    PARTIAL_FAILURE = "partial_failure"
    SERVICE_UNAVAILABLE = "service_unavailable"
    RANDOM = "random"


class ChaosMonkey:
    """Simulate failures and chaos scenarios for testing resilience."""
    
    def __init__(self, failure_rate: float = 0.1):
        """
        Initialize chaos monkey.
        
        Args:
            failure_rate: Probability of failure (0.0 to 1.0)
        """
        self.failure_rate = failure_rate
        self.failure_count = 0
        self.total_requests = 0
    
    def should_fail(self) -> bool:
        """Determine if a failure should occur based on failure rate."""
        self.total_requests += 1
        should_fail = random.random() < self.failure_rate
        if should_fail:
            self.failure_count += 1
        return should_fail
    
    def simulate_network_timeout(self, timeout_duration: float = 5.0):
        """
        Simulate a network timeout by sleeping longer than expected.
        
        Args:
            timeout_duration: Duration to wait before timing out
        """
        logger.warning(f"Simulating network timeout for {timeout_duration}s")
        time.sleep(timeout_duration)
        raise TimeoutError(f"Network request timed out after {timeout_duration}s")
    
    def simulate_connection_failure(self):
        """Simulate a connection failure."""
        logger.warning("Simulating connection failure")
        raise ConnectionError("Failed to establish connection")
    
    def simulate_slow_response(self, delay: float = 2.0):
        """
        Simulate a slow response by adding delay.
        
        Args:
            delay: Delay in seconds
        """
        logger.warning(f"Simulating slow response with {delay}s delay")
        time.sleep(delay)
    
    def simulate_service_unavailable(self):
        """Simulate service unavailable error."""
        logger.warning("Simulating service unavailable")
        raise Exception("Service unavailable (503)")
    
    def inject_failure(
        self,
        func: Callable,
        failure_type: Optional[FailureType] = None,
        **kwargs
    ) -> Any:
        """
        Inject a failure into a function call.
        
        Args:
            func: Function to execute
            failure_type: Type of failure to inject
            **kwargs: Arguments to pass to func
        
        Returns:
            Result of function call or raises exception
        """
        if failure_type is None:
            failure_type = FailureType.RANDOM
        
        if not self.should_fail():
            return func(**kwargs)
        
        if failure_type == FailureType.NETWORK_TIMEOUT:
            self.simulate_network_timeout(kwargs.get("timeout_duration", 5.0))
        elif failure_type == FailureType.CONNECTION_FAILURE:
            self.simulate_connection_failure()
        elif failure_type == FailureType.SLOW_RESPONSE:
            self.simulate_slow_response(kwargs.get("delay", 2.0))
            return func(**kwargs)  # Execute after delay
        elif failure_type == FailureType.SERVICE_UNAVAILABLE:
            self.simulate_service_unavailable()
        elif failure_type == FailureType.RANDOM:
            failure_types = [
                FailureType.NETWORK_TIMEOUT,
                FailureType.CONNECTION_FAILURE,
                FailureType.SERVICE_UNAVAILABLE
            ]
            selected_type = random.choice(failure_types)
            return self.inject_failure(func, selected_type, **kwargs)
        else:
            return func(**kwargs)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get chaos monkey statistics."""
        return {
            "total_requests": self.total_requests,
            "failure_count": self.failure_count,
            "failure_rate": self.failure_rate,
            "actual_failure_rate": (
                self.failure_count / self.total_requests
                if self.total_requests > 0
                else 0
            )
        }


class NetworkChaos:
    """Simulate network-level chaos scenarios."""
    
    @staticmethod
    def simulate_packet_loss(probability: float = 0.1):
        """
        Simulate packet loss by randomly failing requests.
        
        Args:
            probability: Probability of packet loss (0.0 to 1.0)
        """
        if random.random() < probability:
            raise ConnectionError("Packet loss detected")
    
    @staticmethod
    def simulate_network_partition():
        """Simulate network partition."""
        raise ConnectionError("Network partition detected")
    
    @staticmethod
    def simulate_bandwidth_throttle(delay: float = 0.5):
        """
        Simulate bandwidth throttling by adding delay.
        
        Args:
            delay: Delay in seconds
        """
        time.sleep(delay)


class ServiceChaos:
    """Simulate service-level chaos scenarios."""
    
    @staticmethod
    def simulate_degraded_performance(multiplier: float = 2.0):
        """
        Simulate degraded service performance.
        
        Args:
            multiplier: Performance degradation multiplier
        """
        return multiplier
    
    @staticmethod
    def simulate_partial_failure(failure_percentage: float = 0.3):
        """
        Simulate partial service failure.
        
        Args:
            failure_percentage: Percentage of requests that should fail
        """
        if random.random() < failure_percentage:
            raise Exception("Partial service failure")
    
    @staticmethod
    def simulate_cascading_failure():
        """Simulate cascading failure."""
        raise Exception("Cascading failure detected - service chain broken")

