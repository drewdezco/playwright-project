"""
Reusable API client wrapper around Playwright's APIRequestContext.
Provides automatic retry logic, request/response logging, and error handling.
"""
import time
import logging
from typing import Dict, Any, Optional, Union
from playwright.sync_api import APIRequestContext, APIResponse

logger = logging.getLogger(__name__)


class APIClient:
    """Wrapper around Playwright APIRequestContext with additional utilities."""
    
    def __init__(
        self,
        api_context: APIRequestContext,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: int = 30000
    ):
        """
        Initialize API client.
        
        Args:
            api_context: Playwright APIRequestContext instance
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            timeout: Request timeout in milliseconds
        """
        self.api_context = api_context
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
    
    def _log_request(self, method: str, url: str, **kwargs):
        """Log request details."""
        logger.info(f"Request: {method} {url}")
        if "data" in kwargs:
            logger.debug(f"Request body: {kwargs['data']}")
        if "params" in kwargs:
            logger.debug(f"Query params: {kwargs['params']}")
    
    def _log_response(self, response: APIResponse):
        """Log response details."""
        logger.info(f"Response: {response.status} {response.status_text}")
        try:
            body = response.json()
            logger.debug(f"Response body: {body}")
        except Exception:
            logger.debug(f"Response body: {response.text()}")
    
    def _retry_request(
        self,
        method: str,
        url: str,
        retry_on_status: list = None,
        **kwargs
    ) -> APIResponse:
        """
        Execute request with retry logic.
        
        Args:
            method: HTTP method
            url: Request URL
            retry_on_status: List of status codes that should trigger retry
            **kwargs: Additional request parameters
        
        Returns:
            APIResponse object
        """
        if retry_on_status is None:
            retry_on_status = [500, 502, 503, 504]
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                self._log_request(method, url, **kwargs)
                
                response = self.api_context.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                self._log_response(response)
                
                # Retry on specific status codes
                if response.status in retry_on_status and attempt < self.max_retries - 1:
                    logger.warning(
                        f"Request failed with status {response.status}, "
                        f"retrying ({attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                
                return response
                
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"Request failed with exception: {e}, "
                        f"retrying ({attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"Request failed after {self.max_retries} attempts")
                    raise
        
        if last_exception:
            raise last_exception
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> APIResponse:
        """Execute GET request."""
        request_kwargs = {}
        if params:
            request_kwargs["params"] = params
        if headers:
            request_kwargs["headers"] = headers
        request_kwargs.update(kwargs)
        return self._retry_request("GET", url, **request_kwargs)
    
    def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> APIResponse:
        """Execute POST request."""
        request_kwargs = {}
        if data:
            request_kwargs["data"] = data
        if headers:
            request_kwargs["headers"] = headers
        request_kwargs.update(kwargs)
        return self._retry_request("POST", url, **request_kwargs)
    
    def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> APIResponse:
        """Execute PUT request."""
        request_kwargs = {}
        if data:
            request_kwargs["data"] = data
        if headers:
            request_kwargs["headers"] = headers
        request_kwargs.update(kwargs)
        return self._retry_request("PUT", url, **request_kwargs)
    
    def patch(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> APIResponse:
        """Execute PATCH request."""
        request_kwargs = {}
        if data:
            request_kwargs["data"] = data
        if headers:
            request_kwargs["headers"] = headers
        request_kwargs.update(kwargs)
        return self._retry_request("PATCH", url, **request_kwargs)
    
    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> APIResponse:
        """Execute DELETE request."""
        request_kwargs = {}
        if headers:
            request_kwargs["headers"] = headers
        request_kwargs.update(kwargs)
        return self._retry_request("DELETE", url, **request_kwargs)
    
    def assert_status(self, response: APIResponse, expected_status: int):
        """Assert response status code."""
        assert response.status == expected_status, (
            f"Expected status {expected_status}, got {response.status}. "
            f"Response: {response.text()}"
        )
    
    def assert_json(self, response: APIResponse, expected_data: Dict[str, Any]):
        """Assert response JSON matches expected data."""
        actual_data = response.json()
        for key, value in expected_data.items():
            assert key in actual_data, f"Key '{key}' not found in response"
            assert actual_data[key] == value, (
                f"Expected {key}={value}, got {key}={actual_data[key]}"
            )

