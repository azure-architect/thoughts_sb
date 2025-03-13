# tests/test_thought_processing.py
import pytest
from tools.document_processor import process_with_agent
from tests.mock_adapter import MockLLMAdapter

# Create mock agents for testing
def create_mock_agent(role, goal, backstory, llm_config="test_llm"):
    """Create a mock agent for testing."""
    agent = type('Agent', (), {})()
    agent.role = role
    agent.goal = goal
    agent.backstory = backstory
    agent.llm_config = llm_config
    return agent

# Create mock prompt templates
MOCK_PROMPT_TEMPLATES = {
    "capture": "You are acting as the Capture agent. Thought: {thought_content}",
    "contextualize": "You are acting as the Contextualize agent. Thought: {thought_content}",
    "clarify": "You are acting as the Clarify agent. Thought: {thought_content}",
    "categorize": "You are acting as the Categorize agent. Thought: {thought_content}",
    "crystallize": "You are acting as the Crystallize agent. Thought: {thought_content}",
    "connect": "You are acting as the Connect agent. Thought: {thought_content}"
}

# Patch the LLM handler to use our mock adapter
import tools.llm_handler
def mock_communicate_with_llm(prompt, config_name='default'):
    """Mock the communicate_with_llm function."""
    # Return different responses based on the stage mentioned in the prompt
    if "Capture agent" in prompt:
        return "I have captured your thought."
    elif "Contextualize agent" in prompt:
        return "Domain: Test, Urgency: Low, Tone: Neutral"
    elif "Clarify agent" in prompt:
        return "Your thought has been clarified."
    elif "Categorize agent" in prompt:
        return "This belongs to the test category."
    elif "Crystallize agent" in prompt:
        return "Action: Test this system."
    elif "Connect agent" in prompt:
        return "This connects to your testing framework."
    else:
        return "Generic response."

# Store the original function
original_communicate_with_llm = tools.llm_handler.communicate_with_llm

def setup_function():
    """Replace the real LLM communication with our mock for testing."""
    tools.llm_handler.communicate_with_llm = mock_communicate_with_llm

def teardown_function():
    """Restore the real LLM communication after testing."""
    tools.llm_handler.communicate_with_llm = original_communicate_with_llm

def test_capture_stage():
    """Test the capture stage of thought processing."""
    # Create a test thought
    thought = {
        "id": "test_thought_1",
        "timestamp": "2025-03-13T12:00:00",
        "original_filename": "test_thought.txt",
        "original_path": "/test/path/test_thought.txt",
        "content": "This is a test thought.",
        "processing_stage": "input",
        "processing_history": []
    }
    
    # Create a capture agent
    agent = create_mock_agent(
        "Thought Capture Specialist",
        "Efficiently capture raw thoughts",
        "You excel at preserving raw ideas"
    )
    
    # Process the thought with the capture agent
    result = process_with_agent(thought, agent, "Capture", "capture", MOCK_PROMPT_TEMPLATES)
    
    # Check that the thought was processed correctly
    assert result["processing_stage"] == "capture"
    assert len(result["processing_history"]) == 1
    assert result["processing_history"][0]["stage"] == "input"
    assert "capture_results" in result
    assert result["capture_results"] == "I have captured your thought."

def test_contextualize_stage():
    """Test the contextualize stage of thought processing."""
    # Create a test thought with capture stage complete
    thought = {
        "id": "test_thought_1",
        "timestamp": "2025-03-13T12:00:00",
        "original_filename": "test_thought.txt",
        "original_path": "/test/path/test_thought.txt",
        "content": "This is a test thought.",
        "processing_stage": "capture",
        "processing_history": [
            {"stage": "input", "timestamp": "2025-03-13T12:00:00"}
        ],
        "capture_results": "I have captured your thought."
    }
    
    # Create a contextualize agent
    agent = create_mock_agent(
        "Context Analyst",
        "Add essential metadata",
        "You have a talent for identifying context"
    )
    
    # Process the thought with the contextualize agent
    result = process_with_agent(thought, agent, "Contextualize", "contextualize", MOCK_PROMPT_TEMPLATES)
    
    # Check that the thought was processed correctly
    assert result["processing_stage"] == "contextualize"
    assert len(result["processing_history"]) == 2
    assert result["processing_history"][1]["stage"] == "capture"
    assert "contextualize_results" in result
    assert result["contextualize_results"] == "Domain: Test, Urgency: Low, Tone: Neutral"

def test_complete_pipeline():
    """Test the complete thought processing pipeline."""
    # Create a test thought
    thought = {
        "id": "test_thought_1",
        "timestamp": "2025-03-13T12:00:00",
        "original_filename": "test_thought.txt",
        "original_path": "/test/path/test_thought.txt",
        "content": "This is a test thought.",
        "processing_stage": "input",
        "processing_history": []
    }
    
    # Define the agent pipeline
    agent_pipeline = [
        ("capture", "Capture"),
        ("contextualize", "Contextualize"),
        ("clarify", "Clarify"),
        ("categorize", "Categorize"),
        ("crystallize", "Crystallize"),
        ("connect", "Connect")
    ]
    
    # Create agents
    agents = {
        "capture": create_mock_agent("Thought Capture Specialist", "Capture thoughts", "You preserve ideas"),
        "contextualize": create_mock_agent("Context Analyst", "Add metadata", "You identify context"),
        "clarify": create_mock_agent("Thought Clarifier", "Expand thoughts", "You make thoughts coherent"),
        "categorize": create_mock_agent("Pattern Recognition Specialist", "Connect thoughts", "You see patterns"),
        "crystallize": create_mock_agent("Thought Crystallizer", "Transform thoughts", "You distill ideas"),
        "connect": create_mock_agent("Knowledge Integrator", "Integrate thoughts", "You establish connections")
    }
    
    # Process the thought through each stage
    current_thought = thought
    
    for agent_id, agent_name in agent_pipeline:
        if agent_id in agents:
            current_thought = process_with_agent(
                current_thought, 
                agents[agent_id],
                agent_name,
                agent_id,
                MOCK_PROMPT_TEMPLATES
            )
    
    # Check that the thought was processed through all stages
    assert current_thought["processing_stage"] == "connect"
    assert len(current_thought["processing_history"]) == 6
    assert "capture_results" in current_thought
    assert "contextualize_results" in current_thought
    assert "clarify_results" in current_thought
    assert "categorize_results" in current_thought
    assert "crystallize_results" in current_thought
    assert "connect_results" in current_thought