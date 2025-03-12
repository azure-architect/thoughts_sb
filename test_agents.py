import yaml
import os
from your_package.utils.llm_handler import LLMConfigManager
from your_package.agents.agent_factory import create_agent

def test_mistral_nemo_agents():
    # Load configuration
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Initialize LLM manager
    llm_manager = LLMConfigManager(config)
    
    # Sample thought content (could be loaded from your overview.md)
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
    
    # Create and test each agent
    for role in agent_roles:
        print(f"\n\nTesting {role.upper()} agent with Mistral-Nemo...\n" + "="*50)
        
        # Create agent
        agent_config = config["agents"][role]
        agent = create_agent(role, agent_config, llm_manager)
        
        # Process thought
        response = agent.process(sample_thought)
        
        print(f"\nResponse:\n{response}")
        print("-"*50)

if __name__ == "__main__":
    test_mistral_nemo_agents()