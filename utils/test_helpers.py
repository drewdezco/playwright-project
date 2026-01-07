"""
Common test utilities and helper functions.
"""
import time
import json
from typing import Dict, Any, Optional, List
from faker import Faker
import logging

logger = logging.getLogger(__name__)
fake = Faker()


def generate_test_user() -> Dict[str, str]:
    """Generate a test user with fake data."""
    return {
        "name": fake.name(),
        "email": fake.email(),
        "username": fake.user_name(),
        "phone": fake.phone_number(),
        "website": fake.url()
    }


def generate_test_post() -> Dict[str, str]:
    """Generate a test post with fake data."""
    return {
        "title": fake.sentence(nb_words=6),
        "body": fake.text(max_nb_chars=200)
    }


def generate_test_comment() -> Dict[str, str]:
    """Generate a test comment with fake data."""
    return {
        "name": fake.name(),
        "email": fake.email(),
        "body": fake.text(max_nb_chars=150)
    }


def wait_for_condition(
    condition_func: callable,
    timeout: float = 10.0,
    interval: float = 0.5,
    error_message: Optional[str] = None
) -> bool:
    """
    Wait for a condition to become true.
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
        error_message: Custom error message if timeout occurs
    
    Returns:
        True if condition met, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if condition_func():
                return True
        except Exception as e:
            logger.debug(f"Condition check failed: {e}")
        
        time.sleep(interval)
    
    if error_message:
        raise TimeoutError(error_message)
    return False


def assert_response_time(
    response_time: float,
    max_time: float,
    message: Optional[str] = None
):
    """
    Assert that response time is within acceptable limits.
    
    Args:
        response_time: Actual response time in seconds
        max_time: Maximum acceptable response time in seconds
        message: Custom error message
    """
    if response_time > max_time:
        error_msg = (
            message or
            f"Response time {response_time:.2f}s exceeds maximum {max_time:.2f}s"
        )
        raise AssertionError(error_msg)


def assert_json_structure(
    data: Dict[str, Any],
    required_keys: List[str],
    message: Optional[str] = None
):
    """
    Assert that JSON data contains required keys.
    
    Args:
        data: JSON data to validate
        required_keys: List of required keys
        message: Custom error message
    """
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        error_msg = (
            message or
            f"Missing required keys: {', '.join(missing_keys)}"
        )
        raise AssertionError(error_msg)


def assert_status_code_in_range(
    status_code: int,
    min_code: int = 200,
    max_code: int = 299,
    message: Optional[str] = None
):
    """
    Assert that status code is within acceptable range.
    
    Args:
        status_code: HTTP status code
        min_code: Minimum acceptable status code
        max_code: Maximum acceptable status code
        message: Custom error message
    """
    if not (min_code <= status_code <= max_code):
        error_msg = (
            message or
            f"Status code {status_code} not in range {min_code}-{max_code}"
        )
        raise AssertionError(error_msg)


def cleanup_test_data(cleanup_func: callable, *args, **kwargs):
    """
    Execute cleanup function with error handling.
    
    Args:
        cleanup_func: Function to execute for cleanup
        *args: Positional arguments for cleanup function
        **kwargs: Keyword arguments for cleanup function
    """
    try:
        cleanup_func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")


def format_response_for_logging(response: Any) -> str:
    """
    Format response for logging purposes.
    
    Args:
        response: Response object to format
    
    Returns:
        Formatted string representation
    """
    if hasattr(response, "status"):
        return f"Status: {response.status}, Body: {response.text()[:200]}"
    elif isinstance(response, dict):
        return json.dumps(response, indent=2)[:200]
    else:
        return str(response)[:200]


def generate_batch_data(
    data_generator: callable,
    count: int,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Generate a batch of test data.
    
    Args:
        data_generator: Function to generate individual data items
        count: Number of items to generate
        **kwargs: Arguments to pass to data generator
    
    Returns:
        List of generated data items
    """
    return [data_generator(**kwargs) for _ in range(count)]


def retry_on_failure(
    func: callable,
    max_retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
    *args,
    **kwargs
) -> Any:
    """
    Retry a function on failure.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry on
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
    
    Returns:
        Result of function call
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"All {max_retries} attempts failed")
                raise
    
    if last_exception:
        raise last_exception

