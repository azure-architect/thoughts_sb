# tests/conftest.py
import pytest
import os
import tempfile
import yaml
from tests.mock_adapter import MockLLMAdapter

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def mock_adapter():
    """Create a mock LLM adapter for testing."""
    return MockLLMAdapter({
        "capture": "I have captured your thought",
        "contextualize": "Domain: Test, Urgency: Low, Tone: Neutral",
        "clarify": "Your thought has been clarified",
        "categorize": "This belongs to the test category",
        "crystallize": "Action: Test this system",
        "connect": "This connects to your testing framework"
    })

@pytest.fixture
def test_config():
    """Create test configuration."""
    config = {
        "agents": {
            "capture": {
                "role": "Thought Capture Specialist",
                "goal": "Efficiently capture raw thoughts",
                "backstory": "You excel at preserving raw ideas",
                "verbose": True,
                "llm_config": "test_llm"
            },
            "contextualize": {
                "role": "Context Analyst",
                "goal": "Add essential metadata",
                "backstory": "You have a talent for identifying context",
                "verbose": True,
                "llm_config": "test_llm"
            },
            "clarify": {
                "role": "Thought Clarifier",
                "goal": "Expand thoughts",
                "backstory": "You make thoughts coherent",
                "verbose": True,
                "llm_config": "test_llm"
            },
            "categorize": {
                "role": "Pattern Recognition Specialist",
                "goal": "Connect thoughts",
                "backstory": "You see patterns",
                "verbose": True,
                "llm_config": "test_llm"
            },
            "crystallize": {
                "role": "Thought Crystallizer",
                "goal": "Transform thoughts",
                "backstory": "You distill ideas",
                "verbose": True,
                "llm_config": "test_llm"
            },
            "connect": {
                "role": "Knowledge Integrator",
                "goal": "Integrate thoughts",
                "backstory": "You establish connections",
                "verbose": True,
                "llm_config": "test_llm"
            }
        },
        "llm_configs": {
            "test_llm": {
                "adapter": "ollama",
                "model": "test-model",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "default": {
                "adapter": "ollama",
                "model": "test-model",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        },
        "prompts": {
            "capture_prompt_template": "You are acting as the Capture agent. Thought: {thought_content}",
            "contextualize_prompt_template": "You are acting as the Contextualize agent. Thought: {thought_content}",
            "clarify_prompt_template": "You are acting as the Clarify agent. Thought: {thought_content}",
            "categorize_prompt_template": "You are acting as the Categorize agent. Thought: {thought_content}",
            "crystallize_prompt_template": "You are acting as the Crystallize agent. Thought: {thought_content}",
            "connect_prompt_template": "You are acting as the Connect agent. Thought: {thought_content}"
        },
        "folders": {
            "base": "/tmp/test",
            "capture": "capture",
            "contextualize": "contextualize",
            "clarify": "clarify",
            "categorize": "categorize",
            "crystallize": "crystallize",
            "connect": "connect"
        }
    }
    return config

@pytest.fixture
def test_thought():
    """Create a test thought object."""
    return {
        "id": "test_thought_1",
        "timestamp": "2025-03-13T12:00:00",
        "original_filename": "test_thought.txt",
        "original_path": "/test/path/test_thought.txt",
        "content": "This is a test thought.",
        "processing_stage": "input",
        "processing_history": []
    }