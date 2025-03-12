# main.py
import os
import time
import yaml
from crewai import Agent, Task, Crew
from tools.llm_handler import initialize_llm_configs, communicate_with_llm
from tools.file_watcher import watch_folder, read_file, process_existing_files
from tools.document_processor import process_with_agent, pass_to_next_agent
from tools.output_writer import write_result

# Define default paths that will be overridden by config
CAPTURE_FOLDER = "1-Capture"
OUTPUT_FOLDER = "6-Connect"
CONFIG_PATH = "config/test.yaml"

# Store prompt templates globally
PROMPT_TEMPLATES = {}

def load_config(config_path):
    """Load agent and task configurations from YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def create_agents(config):
    """Create agents from config."""
    global PROMPT_TEMPLATES
    
    agents = {}
    for agent_id, agent_config in config['agents'].items():
        # Create the agent without the prompt template
        agents[agent_id] = Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            verbose=agent_config.get('verbose', True)
        )
        
        # Store agent's LLM config name if specified
        if 'llm_config' in agent_config:
            agents[agent_id].llm_config = agent_config['llm_config']
        else:
            agents[agent_id].llm_config = 'default'
        
        # Store the prompt template separately
        if 'prompt_template' in agent_config:
            PROMPT_TEMPLATES[agent_id] = agent_config['prompt_template']
            print(f"Loaded prompt template for {agent_id}, length: {len(agent_config['prompt_template'])}")
        else:
            PROMPT_TEMPLATES[agent_id] = f"Process this thought as {agent_config['role']}: {{thought_content}}"
            print(f"Created default prompt template for {agent_id}")
    
    return agents

def create_agent_pipeline(agents):
    """Create a pipeline of agents in the correct order."""
    # The order of processing stages
    stages = ["capture", "contextualize", "clarify", "categorize", "crystallize", "connect"]
    
    # Print the keys available in the agents dictionary
    print(f"Agent keys: {list(agents.keys())}")
    
    # Create the pipeline of (agent, agent_name, agent_id) tuples
    pipeline = []
    for stage in stages:
        if stage in agents:
            # Title case the stage name for display
            stage_name = stage.title()
            pipeline.append((agents[stage], stage_name, stage))  # Using the same case as in config
    
    print(f"Agent pipeline stages: {[p[2] for p in pipeline]}")
    return pipeline

# Define the callback function for when a new file is detected
def process_new_thought(thought_object, agent_pipeline, prompt_templates, output_folder):
    """
    Process a new thought through the complete agent pipeline.
    
    Args:
        thought_object (dict): The thought object created from the captured file
        agent_pipeline (list): List of (agent, agent_name, agent_id) tuples
        prompt_templates (dict): Dictionary of prompt templates to use
        output_folder (str): Folder to write the final output to
    """
    print(f"Starting to process thought ID: {thought_object['id']}")
    
    # Initialize with the first agent
    current_thought = process_with_agent(thought_object, agent_pipeline[0][0], 
                                         agent_pipeline[0][1], agent_pipeline[0][2], 
                                         prompt_templates)
    
    # Pass through the rest of the pipeline
    for agent, agent_name, agent_id in agent_pipeline[1:]:
        current_thought = pass_to_next_agent(current_thought, agent, agent_name, agent_id, prompt_templates)
    
    # Write the final result to the output folder
    write_result(current_thought, output_folder)
    print(f"Completed processing thought ID: {thought_object['id']}")

def main():
    print("Starting Thought Processing System...")
    
    global CAPTURE_FOLDER, OUTPUT_FOLDER
    
    # Load configuration first
    try:
        config = load_config(CONFIG_PATH)
        print("Loaded configuration from YAML")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return
    
    # Now extract folder configuration
    folder_config = config.get('folders', {})
    base_path = folder_config.get('base', "")
    
    # Update global folder paths based on loaded configuration
    CAPTURE_FOLDER = os.path.join(base_path, folder_config.get('capture', "1-Capture"))
    OUTPUT_FOLDER = os.path.join(base_path, folder_config.get('connect', "6-Connect"))
    
    print(f"Configured capture folder: {CAPTURE_FOLDER}")
    print(f"Configured output folder: {OUTPUT_FOLDER}")
    
    # Ensure folders exist
    for folder in [CAPTURE_FOLDER, OUTPUT_FOLDER]:
        os.makedirs(folder, exist_ok=True)
    
    # Initialize LLM configurations
    initialize_llm_configs(CONFIG_PATH)
    
    # Create agents from config
    agents = create_agents(config)
    print(f"Created {len(agents)} agents")
    
    # Create the agent pipeline
    agent_pipeline = create_agent_pipeline(agents)
    print(f"Created agent pipeline with {len(agent_pipeline)} stages")
    
    # Debug - print the prompt templates to verify they're loaded
    print(f"Loaded prompt templates: {list(PROMPT_TEMPLATES.keys())}")
    
    # Create a callback function with access to the agent pipeline and prompt templates