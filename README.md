# Playwright Python Testing Framework

A comprehensive Playwright Python testing framework designed for testing distributed systems, APIs, and web applications. This project demonstrates production-ready testing patterns suitable for testing satellite tracking, antenna reservation, and command/control services.

## 🎯 Job Alignment

This project is specifically designed to align with requirements for a **Software Test Engineer** role focusing on:

- **End-to-End Testing**: Playwright-based test automation
- **API Testing**: Comprehensive API testing patterns using Playwright's APIRequestContext
- **Load Testing**: Simulating hundreds to thousands of concurrent operations
- **Chaos Engineering**: Testing system resilience and failure scenarios
- **CI/CD Integration**: GitHub Actions workflows for automated testing
- **Distributed Systems**: Testing event-driven and multi-tier architectures

### Key Skills Demonstrated

- ✅ Proficiency in Python
- ✅ Experience with Playwright for E2E testing
- ✅ API testing and troubleshooting
- ✅ Load testing and performance testing
- ✅ Chaos engineering and resilience testing
- ✅ CI/CD pipeline building with GitHub Actions
- ✅ Testing distributed systems and event-driven architectures

## 📁 Project Structure

```
playwright-cypress/
├── requirements.txt              # Python dependencies
├── pytest.ini                   # Pytest configuration
├── conftest.py                  # Pytest fixtures and Playwright setup
├── .github/
│   └── workflows/
│       ├── test.yml             # Main CI/CD test workflow
│       ├── load_test.yml        # Load testing workflow
│       └── chaos_test.yml       # Chaos engineering workflow
├── tests/
│   ├── api/                     # API testing suite
│   │   ├── test_api_basics.py
│   │   ├── test_api_auth.py
│   │   ├── test_api_resilience.py
│   │   └── test_api_performance.py
│   ├── e2e/                     # End-to-end browser tests
│   │   ├── test_browser_basics.py
│   │   └── test_user_flows.py
│   ├── load/                    # Load testing suite
│   │   ├── test_concurrent_requests.py
│   │   └── test_simulated_load.py
│   ├── chaos/                   # Chaos engineering suite
│   │   ├── test_network_failures.py
│   │   ├── test_service_degradation.py
│   │   └── test_recovery_procedures.py
│   └── integration/             # Integration tests
│       └── test_distributed_systems.py
└── utils/                       # Utility modules
    ├── api_client.py
    ├── load_generator.py
    ├── chaos_monkey.py
    └── test_helpers.py
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9, 3.10, or 3.11 (recommended)
  - **Note**: Python 3.12+ may have compatibility issues with some packages. Python 3.11 is recommended for best compatibility.
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd playwright-cypress
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

   For headless browser support:
   ```bash
   playwright install --with-deps
   ```

### Environment Variables (Optional)

Create a `.env` file in the project root for custom configuration:

```env
API_BASE_URL=https://jsonplaceholder.typicode.com
BASE_URL=https://playwright.dev
API_TOKEN=your-api-token-here
TEST_TIMEOUT=30000
```

## 🧪 Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Suites

**API Tests:**
```bash
pytest tests/api/ -v
```

**E2E Browser Tests:**
```bash
pytest tests/e2e/ -v
```

**Load Tests:**
```bash
pytest tests/load/ -v -m load
```

**Chaos Engineering Tests:**
```bash
pytest tests/chaos/ -v -m chaos
```

**Integration Tests:**
```bash
pytest tests/integration/ -v -m integration
```

### Run Tests in Parallel

```bash
pytest -n auto
```

### Run with HTML Reports

```bash
pytest --html=reports/report.html --self-contained-html
```

### Run Specific Test Files

```bash
pytest tests/api/test_api_basics.py -v
```

### Run Tests by Marker

```bash
# Run only smoke tests
pytest -m smoke

# Run slow tests
pytest -m slow

# Run API tests only
pytest -m api
```

## 📊 Test Suites Overview

### API Testing (`tests/api/`)

- **test_api_basics.py**: Basic CRUD operations, query parameters, response validation
- **test_api_auth.py**: Authentication patterns (Bearer tokens, API keys, Basic auth)
- **test_api_resilience.py**: Retry logic, timeout handling, circuit breakers, rate limiting
- **test_api_performance.py**: Response time assertions, throughput testing, latency measurements

### E2E Browser Testing (`tests/e2e/`)

- **test_browser_basics.py**: Page navigation, element interactions, forms, screenshots
- **test_user_flows.py**: Complete user journeys, multi-step workflows, error handling

### Load Testing (`tests/load/`)

- **test_concurrent_requests.py**: Concurrent API calls, thread pools, performance under load
- **test_simulated_load.py**: Simulating hundreds/thousands of operations, ramp-up patterns, sustained load

### Chaos Engineering (`tests/chaos/`)

- **test_network_failures.py**: Network timeouts, connection failures, retry mechanisms
- **test_service_degradation.py**: Slow responses, partial failures, fallback mechanisms
- **test_recovery_procedures.py**: Recovery workflows, data consistency, operational recovery

### Integration Testing (`tests/integration/`)

- **test_distributed_systems.py**: Event-driven architectures, multi-service integration, database consistency, cache invalidation, message queues

## 🔧 Utility Modules

### `utils/api_client.py`

Wrapper around Playwright's APIRequestContext with:
- Automatic retry logic
- Request/response logging
- Error handling utilities
- Status and JSON assertions

### `utils/load_generator.py`

Load testing utilities:
- Concurrent request generation
- Ramp-up patterns
- Sustained load generation
- Performance metrics calculation

### `utils/chaos_monkey.py`

Chaos engineering utilities:
- Network failure simulation
- Service degradation utilities
- Random failure injection
- Failure statistics

### `utils/test_helpers.py`

Common test utilities:
- Test data generation
- Wait utilities
- Assertion helpers
- Retry patterns

## 🔄 CI/CD Integration

### GitHub Actions Workflows

#### `test.yml` - Main Test Suite
- Runs on push/PR to main/develop branches
- Tests across Python 3.9, 3.10, 3.11
- Parallel test execution
- Uploads test reports and screenshots

#### `load_test.yml` - Load Testing
- Scheduled nightly at 2 AM UTC
- Can be manually triggered with custom parameters
- Performance benchmarking
- Metrics collection

#### `chaos_test.yml` - Chaos Engineering
- Scheduled weekly on Sundays at 3 AM UTC
- Failure injection testing
- Recovery procedure validation
- Resilience testing

### Running Workflows Locally

You can simulate GitHub Actions locally using [act](https://github.com/nektos/act):

```bash
# Run test workflow
act push

# Run load test workflow
act workflow_dispatch -W .github/workflows/load_test.yml

# Run chaos test workflow
act workflow_dispatch -W .github/workflows/chaos_test.yml
```

## 📝 Writing Tests

### Basic API Test Example

```python
import pytest
from playwright.sync_api import APIRequestContext

@pytest.mark.api
def test_get_request(api_request_context: APIRequestContext):
    response = api_request_context.get("/posts/1")
    assert response.status == 200
    data = response.json()
    assert "id" in data
```

### Using APIClient Wrapper

```python
from utils.api_client import APIClient

def test_with_client(api_request_context: APIRequestContext):
    client = APIClient(api_request_context, max_retries=3)
    response = client.get("/posts/1")
    client.assert_status(response, 200)
```

### Load Testing Example

```python
from utils.load_generator import LoadGenerator

def test_concurrent_load(api_request_context: APIRequestContext):
    generator = LoadGenerator(max_workers=10)
    
    def make_request():
        return api_request_context.get("/posts/1")
    
    results = generator.generate_concurrent_requests(make_request, 100)
    successful = sum(1 for r in results if r["success"])
    assert successful >= 95
```

### Chaos Engineering Example

```python
from utils.chaos_monkey import ChaosMonkey, FailureType

def test_chaos_injection(api_request_context: APIRequestContext):
    chaos = ChaosMonkey(failure_rate=0.1)
    
    def make_request():
        return api_request_context.get("/posts/1")
    
    # Inject random failures
    try:
        chaos.inject_failure(make_request, FailureType.RANDOM)
    except Exception:
        # Expected failures
        pass
```

## 🎓 Learning Resources

### Playwright Python Documentation
- [Playwright Python Docs](https://playwright.dev/python/)
- [API Testing Guide](https://playwright.dev/python/docs/api-testing)

### Testing Patterns Demonstrated
- API Testing Best Practices
- Load Testing Strategies
- Chaos Engineering Principles
- Distributed Systems Testing
- CI/CD Integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is for educational purposes and demonstrates testing patterns suitable for professional software testing roles.

## 🔍 Troubleshooting

### Common Issues

**Issue**: Playwright browsers not found
```bash
# Solution: Install browsers
playwright install
```

**Issue**: Import errors
```bash
# Solution: Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

**Issue**: Build errors with Python 3.12+ (greenlet, etc.)
```bash
# Solution: Use Python 3.11 or earlier for best compatibility
# Or try upgrading pip and setuptools first:
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Issue**: Tests timing out
```bash
# Solution: Increase timeout in pytest.ini or use --timeout flag
pytest --timeout=600
```

**Issue**: Parallel test failures
```bash
# Solution: Run tests sequentially to debug
pytest -n 0
```

## 📈 Next Steps

- Add more test scenarios for your specific use case
- Integrate with your CI/CD pipeline
- Customize test data generators
- Add custom assertions and utilities
- Extend chaos engineering scenarios
- Add performance benchmarking

## 💡 Tips

- Use markers to organize tests (`@pytest.mark.api`, `@pytest.mark.slow`)
- Leverage fixtures in `conftest.py` for reusable setup
- Use `pytest-xdist` for parallel execution
- Generate HTML reports for better visualization
- Monitor test execution times and optimize slow tests

---

**Built for learning Playwright Python testing patterns aligned with professional software testing requirements.**

