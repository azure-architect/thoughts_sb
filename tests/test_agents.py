# test_agents.py
import yaml
import os
from tools.llm_handler import communicate_with_llm, initialize_llm_configs
from tools.document_processor import process_with_agent
from datetime import datetime

def test_mistral_nemo_agents():
    # Load configuration
    config_path = 'config/test.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Initialize LLM manager with configs
    initialize_llm_configs(config_path)
    
    # Sample thought content
    sample_thought = """# Initial Thought
    
    I need to consolidate our AI training documentation and create a central knowledge base for the team.
    
    ## Current Issues
    
    - Documentation is scattered across Google Drive, Notion, and GitHub
    - New team members are having trouble finding the right resources
    - Some documentation is outdated and contradictory
    
    ## Possible Solutions
    
    - Create a new wiki in Confluence
    - Set up a documentation site with MkDocs
    - Reorganize existing Notion workspace
    
    Need to decide by end of quarter and implement in Q2.
    """
    
    # Agent roles to test
    agent_roles = ["capture", "contextualize", "clarify", "categorize", "crystallize", "connect"]
    
    # Get prompt templates
    prompt_templates = {}
    for role, agent_config in config["agents"].items():
        if "prompt_template" in agent_config:
            prompt_templates[role] = agent_config["prompt_template"]
    
    # Create a mock thought object
    thought_object = {
        "id": "thought_test_" + str(int(datetime.now().timestamp())),
        "timestamp": datetime.now().isoformat(),
        "original_filename": "test_thought.txt",
        "original_path": "test/thought.txt",
        "content": sample_thought,
        "processing_stage": "capture",
        "processing_history": []
    }
    
    # Test each agent
    for role in agent_roles:
        print(f"\n\nTesting {role.upper()} agent with Mistral-Nemo...\n" + "="*50)
        
        # Create a mock agent object with minimal required attributes
        mock_agent = type('Agent', (), {})()
        mock_agent.role = config["agents"][role]["role"]
        mock_agent.goal = config["agents"][role]["goal"]
        mock_agent.backstory = config["agents"][role]["backstory"]
        # Use the specified LLM config from the config file
        mock_agent.llm_config = config["agents"][role].get("llm", "default")
        
        # Process thought
        result = process_with_agent(thought_object.copy(), mock_agent, role.title(), role, prompt_templates)
        
        # Display results
        if f"{role.lower()}_results" in result:
            print(f"\nResponse:\n{result[f'{role.lower()}_results']}")
        else:
            print(f"\nNo response found for {role}")
        print("-"*50)

if __name__ == "__main__":
    test_mistral_nemo_agents()