"""
Load testing utilities for generating concurrent load and monitoring performance.
"""
import asyncio
import time
from typing import List, Callable, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import logging

logger = logging.getLogger(__name__)


class LoadGenerator:
    """Generate load for testing purposes."""
    
    def __init__(self, max_workers: int = 10):
        """
        Initialize load generator.
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
    
    def generate_concurrent_requests(
        self,
        request_func: Callable,
        num_requests: int,
        *args,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate concurrent requests using thread pool.
        
        Args:
            request_func: Function to execute for each request
            num_requests: Number of requests to generate
            *args: Positional arguments for request_func
            **kwargs: Keyword arguments for request_func
        
        Returns:
            List of results from each request
        """
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(request_func, *args, **kwargs)
                for _ in range(num_requests)
            ]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append({
                        "success": True,
                        "result": result,
                        "error": None
                    })
                except Exception as e:
                    results.append({
                        "success": False,
                        "result": None,
                        "error": str(e)
                    })
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(
            f"Completed {num_requests} requests in {duration:.2f}s "
            f"({num_requests/duration:.2f} req/s)"
        )
        
        return results
    
    async def generate_async_requests(
        self,
        request_func: Callable,
        num_requests: int,
        *args,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate concurrent requests using asyncio.
        
        Args:
            request_func: Async function to execute for each request
            num_requests: Number of requests to generate
            *args: Positional arguments for request_func
            **kwargs: Keyword arguments for request_func
        
        Returns:
            List of results from each request
        """
        results = []
        start_time = time.time()
        
        tasks = [
            request_func(*args, **kwargs)
            for _ in range(num_requests)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for response in responses:
            if isinstance(response, Exception):
                results.append({
                    "success": False,
                    "result": None,
                    "error": str(response)
                })
            else:
                results.append({
                    "success": True,
                    "result": response,
                    "error": None
                })
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(
            f"Completed {num_requests} async requests in {duration:.2f}s "
            f"({num_requests/duration:.2f} req/s)"
        )
        
        return results
    
    def ramp_up_load(
        self,
        request_func: Callable,
        initial_load: int,
        final_load: int,
        ramp_duration: int,
        step_interval: int = 1,
        *args,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Gradually increase load over time.
        
        Args:
            request_func: Function to execute for each request
            initial_load: Initial number of concurrent requests
            final_load: Final number of concurrent requests
            ramp_duration: Duration of ramp-up in seconds
            step_interval: Interval between load increases in seconds
            *args: Positional arguments for request_func
            **kwargs: Keyword arguments for request_func
        
        Returns:
            List of results from all requests
        """
        all_results = []
        num_steps = ramp_duration // step_interval
        load_increment = (final_load - initial_load) / num_steps
        
        current_load = initial_load
        
        for step in range(num_steps):
            logger.info(f"Ramp-up step {step + 1}/{num_steps}: {int(current_load)} requests")
            
            step_results = self.generate_concurrent_requests(
                request_func,
                int(current_load),
                *args,
                **kwargs
            )
            
            all_results.extend(step_results)
            current_load += load_increment
            
            if step < num_steps - 1:
                time.sleep(step_interval)
        
        return all_results
    
    def sustained_load(
        self,
        request_func: Callable,
        requests_per_second: float,
        duration: int,
        *args,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate sustained load at a specific rate.
        
        Args:
            request_func: Function to execute for each request
            requests_per_second: Target requests per second
            duration: Duration in seconds
            *args: Positional arguments for request_func
            **kwargs: Keyword arguments for request_func
        
        Returns:
            List of results from all requests
        """
        all_results = []
        interval = 1.0 / requests_per_second
        end_time = time.time() + duration
        
        while time.time() < end_time:
            start_request = time.time()
            
            try:
                result = request_func(*args, **kwargs)
                all_results.append({
                    "success": True,
                    "result": result,
                    "error": None,
                    "timestamp": time.time()
                })
            except Exception as e:
                all_results.append({
                    "success": False,
                    "result": None,
                    "error": str(e),
                    "timestamp": time.time()
                })
            
            elapsed = time.time() - start_request
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)
        
        return all_results


def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate performance metrics from load test results.
    
    Args:
        results: List of result dictionaries
    
    Returns:
        Dictionary with calculated metrics
    """
    total_requests = len(results)
    successful_requests = sum(1 for r in results if r.get("success", False))
    failed_requests = total_requests - successful_requests
    
    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Extract response times if available
    response_times = [
        r.get("response_time", 0)
        for r in results
        if r.get("success", False) and "response_time" in r
    ]
    
    metrics = {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate": success_rate
    }
    
    if response_times:
        metrics.update({
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "avg_response_time": statistics.mean(response_times),
            "median_response_time": statistics.median(response_times),
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else response_times[0],
            "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 1 else response_times[0]
        })
    
    return metrics

