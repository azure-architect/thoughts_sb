# Test Framework Documentation

## Overview

This document outlines our automated testing framework for the thought processing system. The framework provides comprehensive coverage of all system components including configuration loading, LLM adapter functionality, agent setup, file watching, thought processing pipeline, and output generation.

## Test Structure

The test suite is organized into modules that target specific system components:

- `test_config_loading.py` - Tests for environment variable and configuration loading
- `test_llm_adapter.py` - Tests for LLM adapter creation and functionality
- `test_agent.py` - Tests for agent setup and initialization
- `test_file_watcher.py` - Tests for file watching capabilities
- `test_thought_processing.py` - Tests for the complete thought processing pipeline
- `test_output_generation.py` - Tests for output formatting and generation

## Key Components

### MockLLMAdapter

The `MockLLMAdapter` class located in `tests/mock_adapter.py` implements the `LLMAdapter` interface and allows testing without external dependencies. It can be configured with predefined responses and records all calls for verification.

```python
# Example usage
from tests.mock_adapter import MockLLMAdapter

# Create with specific responses for different prompts
mock_adapter = MockLLMAdapter({
    "summarize this": "This is a summary",
    "analyze this": "This is an analysis"
})

# Later verify what was called
assert "summarize this" in mock_adapter.calls[0]["prompt"]
```

### Test Fixtures

Common test fixtures handle setup and teardown operations:

```python
@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write('{"adapter": "ollama", "model": "test-model"}')
        temp_file_path = temp_file.name
    
    yield temp_file_path
    
    # Clean up after test
    os.unlink(temp_file_path)
```

## Running Tests

### Running All Tests

```bash
# Run the entire test suite
pytest

# Run with detailed output
pytest -v

# Run with test coverage report
pytest --cov=src
```

### Running Specific Tests

```bash
# Run tests for a specific module
pytest tests/test_llm_adapter.py

# Run a specific test function
pytest tests/test_config_loading.py::test_env_variable_loading

# Run tests matching a pattern
pytest -k "adapter"
```

## Development Workflow

### Continuous Testing During Development

1. **Run relevant tests first**: When modifying a component, run its specific tests to catch issues early.

```bash
# While working on the LLM adapter
pytest tests/test_llm_adapter.py -v
```

2. **Run the full suite before committing**: Ensure all components still work together.

```bash
pytest
```

3. **Test-driven development**: For new features, write tests first to define expected behavior.

```bash
# 1. Write a failing test
# 2. Implement the feature
# 3. Ensure the test passes
pytest tests/test_new_feature.py -v
```

### Handling External Dependencies

For tests requiring external services:

1. **Use mocking**: The `MockLLMAdapter` eliminates the need for actual LLM services.

2. **Environment isolation**: Tests use temporary files and directories to avoid contaminating your development environment.

3. **Monkeypatching**: Use pytest's `monkeypatch` fixture to temporarily modify environment variables.

```python
def test_env_config(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    # Test with isolated environment variable
```

## Extending the Test Framework

### Adding New Tests

1. Create a new test file or add to an existing one based on the component being tested.
2. Follow the existing patterns for setup, execution, and assertions.
3. Use appropriate fixtures for clean test isolation.

### Testing New Components

1. Consider if a new mock is needed (similar to `MockLLMAdapter`).
2. Create fixtures that provide test instances of the component.
3. Write tests that cover both happy paths and error handling.

### Improving Test Coverage

Run coverage analysis to identify untested code paths:

```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html to view the report
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on the state from other tests.
2. **Fast execution**: Tests should run quickly to support the development workflow.
3. **Clear failure messages**: Write assertions that provide helpful information when they fail.
4. **Test both success and failure paths**: Ensure error handling is also tested.
5. **Use descriptive test names**: The function name should describe what is being tested.

## Common Testing Patterns

### Patching External Components

```python
@patch('adapters.factory.OllamaAdapter')
def test_adapter_creation(mock_adapter_class):
    mock_adapter = MockLLMAdapter()
    mock_adapter_class.return_value = mock_adapter
    
    # Test with the mock instead of real adapter
```

### Testing Asynchronous Code

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function_under_test()
    assert result == expected_value
```

### Testing Error Handling

```python
def test_error_handling():
    with pytest.raises(ValueError) as excinfo:
        function_that_should_raise()
    assert "Expected error message" in str(excinfo.value)
```

By following this documentation, you can effectively use and extend the test framework to maintain code quality and prevent regressions as you develop the thought processing system.