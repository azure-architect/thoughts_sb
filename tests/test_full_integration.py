# test_full_integration.py
import yaml
import os
from crewai import Agent
from tools.llm_handler import initialize_llm_configs, communicate_with_llm
from tools.document_processor import process_with_agent

# Global variables
PROMPT_TEMPLATES = {}
AGENT_LLM_CONFIGS = {}

def load_config(config_path):
    """Load agent and task configurations from YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def create_agents(config):
    """Create agents from config."""
    global PROMPT_TEMPLATES, AGENT_LLM_CONFIGS
    
    # Import LangChain's Ollama integration
    from langchain_community.llms import Ollama
    
    # Create a dummy Ollama instance that won't actually be used for calls
    print("Creating dummy Ollama LLM for agents...")
    dummy_llm = Ollama(
        model="qwen2.5:14b",
        base_url="http://localhost:11434"
    )
    
    agents = {}
    for agent_id, agent_config in config['agents'].items():
        # Store the LLM config in our global dictionary
        llm_config_name = agent_config.get('llm_config', 'default')
        AGENT_LLM_CONFIGS[agent_id] = llm_config_name
        
        print(f"Creating agent {agent_id} with config {llm_config_name}")
        
        # Create the agent with the dummy LLM
        agents[agent_id] = Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            verbose=agent_config.get('verbose', True),
            llm=dummy_llm  # Using the same dummy LLM for all agents
        )
        
        # Store the prompt template
        if 'prompt_template' in agent_config:
            PROMPT_TEMPLATES[agent_id] = agent_config['prompt_template']
            print(f"Loaded prompt template for {agent_id}, length: {len(agent_config['prompt_template'])}")
        else:
            PROMPT_TEMPLATES[agent_id] = f"Process this thought as {agent_config['role']}: {{thought_content}}"
            print(f"Created default prompt template for {agent_id}")
    
    return agents

def test_document_processor(agent, agent_name, agent_id):
    """Test the document processor with a single agent."""
    # Create a simple test thought object
    thought_object = {
        "id": "test_thought_123",
        "timestamp": "2025-03-12T16:30:00",
        "content": "This is a test thought to verify that all agents can communicate with the LLM.",
        "processing_stage": "capture",
        "processing_history": []
    }
    
    print(f"\nTesting document processor with {agent_name} agent...")
    processed_thought = process_with_agent(thought_object, agent, agent_name, agent_id, PROMPT_TEMPLATES)
    
    # Check if the processing was successful
    result_key = f"{agent_name.lower()}_results"
    if result_key in processed_thought:
        result = processed_thought[result_key]
        print(f"Processing successful! Result: {result[:100]}...")
        return True
    else:
        print(f"Processing failed! No {result_key} in processed thought")
        print(f"Keys in processed thought: {list(processed_thought.keys())}")
        return False

def run_full_integration_test():
    """Run a test of the full integration between config, agents, and document processor."""
    config_path = "config/test.yaml"
    print(f"Loading config from {config_path}")
    
    # Initialize LLM configurations
    initialize_llm_configs(config_path)
    
    # Load config
    config = load_config(config_path)
    
    # Create agents
    try:
        print("Creating agents...")
        agents = create_agents(config)
        print(f"Successfully created {len(agents)} agents")
        
        # Test each agent with the document processor
        success_count = 0
        for agent_id, agent in agents.items():
            agent_name = agent_id.title()  # Capitalize first letter
            success = test_document_processor(agent, agent_name, agent_id)
            if success:
                success_count += 1
        
        print(f"\nTest summary: {success_count}/{len(agents)} agents processed thoughts successfully")
        return success_count == len(agents)
        
    except Exception as e:
        print(f"Error in integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting full integration test...")
    result = run_full_integration_test()
    print(f"Integration test {'succeeded' if result else 'failed'}")