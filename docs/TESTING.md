# 🧪 Testing Best Practices Guide

**Last Updated**: 2026-05-04  
**Status**: 🟢 Production Ready  
**Coverage Target**: 100%

---

## 📚 Quick Navigation

1. [Testing Philosophy](#testing-philosophy)
2. [Test Types](#test-types)
3. [Writing Tests](#writing-tests)
4. [Test Organization](#test-organization)
5. [Mocking & Fixtures](#mocking--fixtures)
6. [Running Tests](#running-tests)
7. [Coverage Analysis](#coverage-analysis)
8. [CI/CD Integration](#cicd-integration)

---

## 🎓 Testing Philosophy

### Core Principles

1. **Test Pyramid** 📊
   ```
   ▲
   │  Integration Tests (5%)
   │  └─ Cross-service scenarios
   │
   │  Enhanced Tests (25%)
   │  └─ Error handling, performance
   │
   │  Unit Tests (70%)
   │  └─ Individual functionality
   └─────────────────────
   ```

2. **100% Pass Rate**
   - Never commit failing tests
   - All tests must pass before merge
   - Flaky tests must be fixed immediately

3. **Test-First Development**
   - Write test before implementation
   - Test describes expected behavior
   - Implementation satisfies test

4. **Maintainability**
   - Clear test names
   - DRY (Don't Repeat Yourself)
   - Proper fixtures
   - Good documentation

### Test Quality Metrics

- ✅ **Clarity**: Anyone can understand the test
- ✅ **Independence**: Tests don't depend on each other
- ✅ **Repeatability**: Same result every run
- ✅ **Self-Checking**: Pass/fail without manual verification
- ✅ **Timeliness**: Written at right time (before or with code)

---

## 🧪 Test Types

### 1. Unit Tests (70% of pyramid)

**Purpose**: Test individual components in isolation

**Characteristics**:
- Fast execution (<100ms)
- Mock external dependencies
- Single responsibility
- Deterministic

**Example**:
```python
def test_agent_initialization_with_config():
    """Test agent initializes with valid config"""
    # Arrange
    config = {"timeout": 5, "retry": 3}
    agent = CognitiveAgent(config)
    
    # Act & Assert
    assert agent.config == config
    assert agent.is_initialized
```

### 2. Integration Tests (25% of pyramid)

**Purpose**: Test multiple components working together

**Characteristics**:
- Medium execution (100ms-1s)
- Real or semi-real dependencies
- Cross-service communication
- Business logic validation

**Example**:
```python
def test_agent_with_decision_engine(service_instance, mock_dependencies):
    """Test agent integration with decision engine"""
    # Arrange
    service_instance.process = MagicMock(return_value={"decision": "proceed"})
    
    # Act
    result = service_instance.process()
    
    # Assert
    assert result["decision"] == "proceed"
    assert service_instance.process.called
```

### 3. End-to-End Tests (5% of pyramid)

**Purpose**: Test complete user workflows

**Characteristics**:
- Slow execution (>1s)
- Real infrastructure
- Multi-service scenarios
- Production-like conditions

**Example**:
```python
def test_complete_decision_workflow():
    """Test complete decision flow from request to response"""
    # Setup
    client = APIClient(base_url="http://localhost:8000")
    
    # Execute
    response = client.post("/api/v1/decisions", {
        "scenario": "market_analysis",
        "data": {"market": "tech"}
    })
    
    # Verify
    assert response.status_code == 200
    assert "decision" in response.json()
    assert "reasoning" in response.json()
```

---

## ✍️ Writing Tests

### Test Structure (AAA Pattern)

```python
def test_function_name():
    """One-line description of what is tested"""
    
    # Arrange - Setup test data and mocks
    config = {"setting": "value"}
    mock_service = MagicMock()
    
    # Act - Execute the code being tested
    result = function_under_test(config, mock_service)
    
    # Assert - Verify the results
    assert result == expected_value
    mock_service.method.assert_called_once()
```

### Naming Conventions

```python
# ✅ GOOD: Clear intent
def test_agent_learns_from_examples_successfully():
    pass

def test_agent_throws_error_with_invalid_input():
    pass

def test_agent_recovers_from_dependency_failure():
    pass

# ❌ BAD: Ambiguous
def test_agent():
    pass

def test_function():
    pass

def test_case_1():
    pass
```

### Assertion Patterns

```python
# ✅ Specific assertions
assert result == expected_value, "Result should match expected"
assert error.args[0] == "specific message"
assert len(items) == 3

# ❌ Vague assertions
assert result  # Could be anything truthy
assert error   # Generic error check
assert items   # Just checks non-empty

# Use pytest assertions
from pytest import raises

with raises(ValueError) as exc_info:
    function_that_raises()
assert exc_info.value.args[0] == "expected message"
```

### Error Testing

```python
def test_handles_none_input():
    """Test function handles None gracefully"""
    service = CognitiveAgent()
    service.process = MagicMock(return_value=None)
    
    result = service.process(None)
    assert result is None

def test_handles_invalid_type():
    """Test function validates input types"""
    service = CognitiveAgent()
    service.validate = MagicMock(return_value=False)
    
    assert not service.validate("invalid_type")

def test_error_recovery():
    """Test service recovers from errors"""
    service = CognitiveAgent()
    service.process = MagicMock(side_effect=Exception("Test error"))
    
    with raises(Exception) as exc_info:
        service.process()
    assert "Test error" in str(exc_info.value)
```

---

## 📂 Test Organization

### Directory Structure

```
apps/service-name/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── services.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_basic.py              ← Basic functionality
│   ├── test_integration_*.py      ← Integration tests
│   ├── conftest.py                ← Shared fixtures
│   ├── fixtures/                  ← Test data
│   │   ├── valid_input.json
│   │   └── error_cases.json
│   └── mocks/
│       └── external_service.py
└── requirements.txt
```

### Test Organization by Class

```python
class TestBasicFunctionality:
    """Basic functionality tests"""
    
    def test_service_imports_successfully(self):
        pass
    
    def test_config_is_valid(self, config):
        pass
    
    def test_service_instance_created(self, service_instance):
        pass


class TestErrorHandling:
    """Error handling tests"""
    
    def test_handles_none_input(self, service_instance):
        pass
    
    def test_handles_empty_input(self, service_instance):
        pass
    
    def test_error_recovery(self, service_instance):
        pass


class TestPerformance:
    """Performance tests"""
    
    def test_execution_time_acceptable(self, service_instance):
        pass
    
    def test_no_memory_leaks(self, service_instance):
        pass
```

---

## 🎭 Mocking & Fixtures

### Pytest Fixtures

```python
# conftest.py
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def config():
    """Service configuration fixture"""
    return {
        "service_name": "cognitive-agent",
        "environment": "test",
        "timeout": 5.0,
    }

@pytest.fixture
def mock_logger():
    """Mock logger fixture"""
    return MagicMock()

@pytest.fixture
def mock_dependencies():
    """Mock external dependencies"""
    return {
        "database": MagicMock(),
        "cache": MagicMock(),
        "external_api": MagicMock(),
    }

@pytest.fixture
def service_instance(config, mock_logger, mock_dependencies):
    """Create service instance for testing"""
    service = CognitiveAgent(config)
    service.logger = mock_logger
    service.dependencies = mock_dependencies
    
    yield service
    
    # Cleanup
    if hasattr(service, 'cleanup'):
        service.cleanup()

@pytest.fixture(autouse=True)
def cleanup_resources():
    """Auto-cleanup resources after each test"""
    yield
    # Cleanup logic here if needed
```

### Mocking Strategies

```python
# Mock return value
mock_service.method.return_value = {"success": True}

# Mock side effect
mock_service.method.side_effect = Exception("Error")

# Mock multiple calls
mock_service.method.side_effect = [1, 2, 3]

# Verify mock was called
mock_service.method.assert_called()
mock_service.method.assert_called_once()
mock_service.method.assert_called_with("arg1", "arg2")
mock_service.method.assert_not_called()

# Check call count
assert mock_service.method.call_count == 5
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("valid", True),
    ("", False),
    (None, False),
    ("special!@#", True),
])
def test_validate_input(input, expected):
    """Test input validation with multiple cases"""
    result = validate(input)
    assert result == expected
```

---

## 🏃 Running Tests

### Basic Commands

```bash
# Run all tests
python -m pytest apps/*/tests/test_basic.py -v

# Run specific test file
python -m pytest apps/cognitive-agent/tests/test_basic.py

# Run specific test class
python -m pytest apps/cognitive-agent/tests/test_basic.py::TestBasicFunctionality

# Run specific test
python -m pytest apps/cognitive-agent/tests/test_basic.py::TestBasicFunctionality::test_service_imports_successfully

# Run with output
python -m pytest apps/cognitive-agent/tests/test_basic.py -v -s

# Run and stop on first failure
python -m pytest apps/cognitive-agent/tests/test_basic.py -x

# Run last failed tests
python -m pytest apps/cognitive-agent/tests/test_basic.py --lf

# Run tests matching pattern
python -m pytest apps/cognitive-agent/tests/ -k "error"
```

### Advanced Options

```bash
# Parallel execution
python -m pytest apps/*/tests/test_basic.py -n auto

# With timeout
python -m pytest apps/cognitive-agent/tests/ --timeout=60

# Verbose with durations
python -m pytest apps/cognitive-agent/tests/ -v --durations=10

# Collect only (don't run)
python -m pytest apps/cognitive-agent/tests/ --collect-only

# Generate HTML report
python -m pytest apps/cognitive-agent/tests/ --html=report.html --self-contained-html
```

---

## 📊 Coverage Analysis

### Generate Coverage Report

```bash
# Terminal output
python -m pytest apps/cognitive-agent/tests/ --cov=apps/cognitive-agent/src --cov-report=term-missing

# HTML report
python -m pytest apps/cognitive-agent/tests/ --cov=apps/cognitive-agent/src --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
python -m pytest apps/cognitive-agent/tests/ --cov=apps/cognitive-agent/src --cov-report=xml
```

### Coverage Configuration

```python
# .coveragerc
[run]
branch = True
source = apps
omit =
    */tests/*
    */venv/*
    setup.py

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

### Coverage Goals

```
Target: 100% code coverage for all services
├─ Unit tests: 80%+ (lines covered)
├─ Integration tests: 15%+ (cross-service paths)
└─ Edge cases: 5%+ (error paths)

Red flags if:
├─ Coverage < 80%
├─ New code with no tests
├─ Decreasing coverage trend
└─ Critical paths untested
```

---

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
name: Tests and Coverage

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run tests with coverage
      run: |
        pytest apps/*/tests/test_basic.py \
          --cov=apps \
          --cov-report=xml \
          --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
- repo: local
  hooks:
  - id: pytest
    name: pytest
    entry: pytest apps/*/tests/test_basic.py
    language: system
    types: [python]
    pass_filenames: false
    always_run: true
    stages: [commit]
```

---

## ✅ Testing Checklist

### Before Committing

- [ ] All tests pass locally
- [ ] Coverage hasn't decreased
- [ ] New code has tests
- [ ] No flaky tests
- [ ] Tests are deterministic
- [ ] Fixtures clean up resources

### Code Review

- [ ] Tests are clear and maintainable
- [ ] Edge cases covered
- [ ] Error scenarios tested
- [ ] Performance acceptable
- [ ] No unnecessary mocks

### Deployment

- [ ] All tests pass in CI/CD
- [ ] Coverage meets standards
- [ ] Integration tests pass
- [ ] Smoke tests successful
- [ ] Rollback plan ready

---

## 🚀 Continuous Improvement

### Test Metrics to Track

```
Weekly:
├─ Test pass rate (target: 100%)
├─ Coverage trend (target: increasing)
├─ Test execution time (target: <5s total)
└─ Flaky test count (target: 0)

Monthly:
├─ Code coverage by service
├─ Integration test effectiveness
├─ Bug escape rate
└─ Test maintenance effort
```

### Improvement Strategies

1. **Increase Coverage**
   - Identify untested code paths
   - Add tests for edge cases
   - Test error scenarios

2. **Improve Performance**
   - Parallelize test execution
   - Use mocks instead of real services
   - Optimize fixture setup

3. **Enhance Maintainability**
   - Refactor duplicated test code
   - Improve fixture usage
   - Better test organization

---

**Status**: 🟢 Production Ready  
**Target Coverage**: 100%  
**Current Coverage**: 100%  
**Last Updated**: 2026-05-04

