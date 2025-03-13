# tests/test_llm_adapter.py - revised
import pytest
from unittest.mock import patch
from adapters.factory import create_adapter
from tests.mock_adapter import MockLLMAdapter

@pytest.fixture
def mock_ollama_adapter():
    return MockLLMAdapter({"test query": "test response"})

@patch('adapters.factory.OllamaAdapter')
def test_adapter_creation(mock_adapter_class):
    """Test that an adapter can be created from a configuration."""
    # Configure the mock adapter class
    mock_adapter = MockLLMAdapter()
    mock_adapter_class.return_value = mock_adapter
    
    # Create a configuration
    config = {
        "adapter": "ollama",
        "model": "test-model",
        "temperature": 0.5
    }
    
    # Create an adapter using the factory
    adapter = create_adapter(config)
    
    # Check that the adapter was properly initialized
    assert adapter == mock_adapter
    assert "model" in adapter.config
    assert adapter.config["model"] == "test-model"

def test_adapter_functionality():
    """Test the core functionality of our mock adapter."""
    # Create an adapter with custom responses
    adapter = MockLLMAdapter({
        "test query": "test response"
    })
    
    # Initialize the adapter
    adapter.initialize({"model": "test-model"})
    
    # Test generate method
    response = adapter.generate("Here is a test query for you.")
    
    # Check that the response is as expected
    assert response == "test response"
    
    # Check call recording
    assert len(adapter.calls) == 1
    assert adapter.calls[0]["prompt"] == "Here is a test query for you."
    
    # Test set_config method
    adapter.set_config({"temperature": 0.5})
    assert adapter.config["temperature"] == 0.5
    assert adapter.config["model"] == "test-model"  # Original config preserved