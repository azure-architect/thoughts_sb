import os
import time
import yaml
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from tools.tools import watch_folder, read_file, process_with_agent, pass_to_next_agent, write_result, process_existing_files

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

def create_agents(config, llm):
    """Create agents from config."""
    global PROMPT_TEMPLATES
    
    agents = {}
    for agent_id, agent_config in config['agents'].items():
        # Create the agent without the prompt template
        agents[agent_id] = Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            llm=llm,
            verbose=agent_config.get('verbose', True)
        )
        
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
    
    # Configure Ollama LLM with parameters from config
    llm_config = config.get('llm', {})
    model_name = llm_config.get('model_name', "llama3:8b-instruct-fp16")
    
    llm = Ollama(
        model=model_name,
        temperature=llm_config.get('temperature', 0.7),
        base_url="http://localhost:11434"
    )
    print(f"Configured LLM with model: {model_name}")
    
    # Test LLM directly
    print("Testing LLM connection directly...")
    try:
        test_response = llm.invoke("This is a test. Please reply with 'LLM is working'.")
        print(f"LLM test response: {test_response[:50]}...")
    except Exception as e:
        print(f"LLM test failed: {type(e).__name__}: {str(e)}")
    
    # Create agents from config
    agents = create_agents(config, llm)
    print(f"Created {len(agents)} agents")
    
    # Create the agent pipeline
    agent_pipeline = create_agent_pipeline(agents)
    print(f"Created agent pipeline with {len(agent_pipeline)} stages")
    
    # Debug - print the prompt templates to verify they're loaded
    print(f"Loaded prompt templates: {list(PROMPT_TEMPLATES.keys())}")
    
    # Create a callback function with access to the agent pipeline and prompt templates
    def callback(thought_object):
        process_new_thought(thought_object, agent_pipeline, PROMPT_TEMPLATES, OUTPUT_FOLDER)
    
    # Process existing files in the capture folder first
    processed_count = process_existing_files(CAPTURE_FOLDER, callback)
    if processed_count > 0:
        print(f"Processed {processed_count} existing files in {CAPTURE_FOLDER}")
    else:
        print(f"No existing files to process in {CAPTURE_FOLDER}")
    
    # Start watching the capture folder for new files
    observer = watch_folder(CAPTURE_FOLDER, callback)
    
    try:
        print(f"System running. Watching {CAPTURE_FOLDER} and writing to {OUTPUT_FOLDER}")
        print("Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("System stopped by user.")
    
    observer.join()
    print("System shutdown complete.")

if __name__ == "__main__":
    main()