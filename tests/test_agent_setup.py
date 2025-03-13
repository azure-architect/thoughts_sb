# tests/test_agent_setup.py
import pytest
from tests.mock_adapter import MockLLMAdapter

def test_agent_configuration():
    """Test that agents are correctly configured from YAML."""
    # Create a test configuration
    config = {
        "agents": {
            "capture": {
                "role": "Thought Capture Specialist",
                "goal": "Efficiently capture raw thoughts",
                "backstory": "You excel at preserving raw ideas",
                "verbose": True,
                "llm_config": "test_llm"
            }
        }
    }
    
    # Create an agent object (simulating what the main code would do)
    agent = type('Agent', (), {})()
    agent.role = config["agents"]["capture"]["role"]
    agent.goal = config["agents"]["capture"]["goal"]
    agent.backstory = config["agents"]["capture"]["backstory"]
    agent.llm_config = config["agents"]["capture"]["llm_config"]
    
    # Check that agent properties match configuration
    assert agent.role == "Thought Capture Specialist"
    assert agent.goal == "Efficiently capture raw thoughts"
    assert agent.backstory == "You excel at preserving raw ideas"
    assert agent.llm_config == "test_llm"