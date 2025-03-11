import os
import time
import yaml
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama  # Use the recommended import path
from tools.tools import watch_folder, read_file, process_with_agent, pass_to_next_agent, write_result

# Folder paths for watching and output
CAPTURE_FOLDER = "1-Capture"
OUTPUT_FOLDER = "6-Connect"
CONFIG_PATH = "config/config.yaml"

def load_config(config_path):
    """Load agent and task configurations from YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def create_agents(config, llm):
    """Create agents from config."""
    agents = {}
    for agent_id, agent_config in config['agents'].items():
        agents[agent_id] = Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            llm=llm,
            verbose=agent_config.get('verbose', True)
        )
    
    return agents

def create_agent_pipeline(agents):
    """Create a pipeline of agents in the correct order."""
    # The order of processing stages
    stages = ["capture", "contextualize", "clarify", "categorize", "crystallize", "connect"]
    
    # Create the pipeline of (agent, agent_name) tuples
    pipeline = []
    for stage in stages:
        if stage in agents:
            # Title case the stage name for display
            stage_name = stage.title()
            pipeline.append((agents[stage], stage_name))
    
    return pipeline

# Define the callback function for when a new file is detected
def process_new_thought(thought_object, agent_pipeline):
    """
    Process a new thought through the complete agent pipeline.
    
    Args:
        thought_object (dict): The thought object created from the captured file
        agent_pipeline (list): List of (agent, agent_name) tuples
    """
    print(f"Starting to process thought ID: {thought_object['id']}")
    
    # Initialize with the first agent
    current_thought = process_with_agent(thought_object, agent_pipeline[0][0], agent_pipeline[0][1])
    
    # Pass through the rest of the pipeline
    for agent, agent_name in agent_pipeline[1:]:
        current_thought = pass_to_next_agent(current_thought, agent, agent_name)
    
    # Write the final result to the output folder
    write_result(current_thought, OUTPUT_FOLDER)
    print(f"Completed processing thought ID: {thought_object['id']}")

def main():
    print("Starting Thought Processing System...")
    
    # Load configuration
    try:
        config = load_config(CONFIG_PATH)
        print("Loaded configuration from YAML")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return
    
    # Configure Ollama LLM with parameters from config
    llm_config = config.get('llm', {})
    llm = Ollama(
        model=llm_config.get('model_name', "ollama/qwen2.5:14b"),
        temperature=llm_config.get('temperature', 0.7),
        base_url="http://localhost:11434"
    )
    print(f"Configured LLM: {llm_config.get('model_name', 'ollama/qwen2.5:14b')}")
    
    # Create agents from config
    agents = create_agents(config, llm)
    print(f"Created {len(agents)} agents")
    
    # Create the agent pipeline
    agent_pipeline = create_agent_pipeline(agents)
    print(f"Created agent pipeline with {len(agent_pipeline)} stages")
    
    # Create the capture folder if it doesn't exist
    if not os.path.exists(CAPTURE_FOLDER):
        os.makedirs(CAPTURE_FOLDER)
        print(f"Created capture folder: {CAPTURE_FOLDER}")
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output folder: {OUTPUT_FOLDER}")
    
    # Create a callback function with access to the agent pipeline
    def callback(thought_object):
        process_new_thought(thought_object, agent_pipeline)
    
    # Start watching the capture folder
    observer = watch_folder(CAPTURE_FOLDER, callback)
    
    try:
        print("System running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("System stopped by user.")
    
    observer.join()
    print("System shutdown complete.")

if __name__ == "__main__":
    main()