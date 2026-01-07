"""
Pytest configuration and fixtures for Playwright Python tests.
Provides reusable fixtures for browsers, API clients, and test utilities.
"""
import os
import pytest
from playwright.sync_api import Playwright, Browser, BrowserContext, Page, APIRequestContext
from typing import Generator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, None, None]:
    """Playwright instance for the test session."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session", params=["chromium", "firefox", "webkit"])
def browser_type(request):
    """Browser type parameter for cross-browser testing."""
    return request.param


@pytest.fixture(scope="session")
def browser(playwright: Playwright, browser_type: str) -> Generator[Browser, None, None]:
    """Browser instance for the test session."""
    browser_name = getattr(playwright, browser_type)
    browser_instance = browser_name.launch(headless=True)
    yield browser_instance
    browser_instance.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Browser context for each test."""
    context_instance = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True
    )
    yield context_instance
    context_instance.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Page instance for each test."""
    page_instance = context.new_page()
    yield page_instance
    page_instance.close()


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    """API request context for API testing."""
    api_context = playwright.request.new_context(
        base_url=os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com"),
        extra_http_headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    yield api_context
    api_context.dispose()


@pytest.fixture(scope="function")
def authenticated_api_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    """Authenticated API request context."""
    token = os.getenv("API_TOKEN", "")
    api_context = playwright.request.new_context(
        base_url=os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com"),
        extra_http_headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}" if token else ""
        }
    )
    yield api_context
    api_context.dispose()


@pytest.fixture(scope="function")
def base_url() -> str:
    """Base URL for tests."""
    return os.getenv("BASE_URL", "https://playwright.dev")


@pytest.fixture(scope="function")
def api_base_url() -> str:
    """Base URL for API tests."""
    return os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com")


@pytest.fixture(scope="function")
def test_timeout() -> int:
    """Default test timeout in milliseconds."""
    return int(os.getenv("TEST_TIMEOUT", "30000"))


@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("test-results", exist_ok=True)
    yield
    # Cleanup after test (if needed)


@pytest.fixture(scope="function")
def test_data():
    """Generate test data for tests."""
    from faker import Faker
    fake = Faker()
    return {
        "name": fake.name(),
        "email": fake.email(),
        "username": fake.user_name(),
        "password": fake.password(),
        "title": fake.sentence(),
        "body": fake.text(),
        "address": fake.address(),
        "phone": fake.phone_number()
    }

