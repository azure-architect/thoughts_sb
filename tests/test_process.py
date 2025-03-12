# test_process.py
import os
import sys
import time
import yaml
import logging
import json
from datetime import datetime

# Correctly add project root to path when running from tests directory
current_dir = os.path.dirname(os.path.abspath(__file__))  # tests directory
project_root = os.path.dirname(current_dir)  # Go up one level to project root
sys.path.insert(0, project_root)  # Insert at beginning of path

# Use relative import for tools
try:
    from tools.document_processor import process_with_agent
except ImportError:
    # If that fails, try direct import (if tools is a sibling of tests)
    sys.path.insert(0, os.path.join(project_root, 'tools'))
    from tools.document_processor import process_with_agent

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_yaml_config(file_path):
    """Load a YAML configuration file"""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        logger.error(f"Current directory: {os.getcwd()}")
        logger.error(f"File exists: {os.path.exists(file_path)}")
        return {}

def test_real_processing():
    """Test the full processing pipeline with real LLM calls"""
    logger.info(f"Project root directory: {project_root}")
    
    # Try different possible locations for config files
    config_dirs = [
        os.path.join(project_root, 'config'),
        os.path.join(project_root, 'configs'),
        os.path.join(os.getcwd(), 'config'),
        os.path.join(os.getcwd(), 'configs')
    ]
    
    # Find the correct config directory
    config_dir = None
    for dir_path in config_dirs:
        if os.path.exists(dir_path):
            config_dir = dir_path
            logger.info(f"Found config directory: {config_dir}")
            break
    
    if not config_dir:
        logger.error("Could not find config directory!")
        logger.error(f"Tried: {config_dirs}")
        return
    
    # Load configurations from the correct directory
    agents_config = load_yaml_config(os.path.join(config_dir, 'agents.yaml'))
    llms_config = load_yaml_config(os.path.join(config_dir, 'llms.yaml'))
    prompts_config = load_yaml_config(os.path.join(config_dir, 'prompts.yaml'))
    
    if not agents_config or not llms_config or not prompts_config:
        logger.error("Failed to load one or more configuration files!")
        return
    
    # Extract prompt templates
    prompt_templates = {}
    for key, value in prompts_config.items():
        if key.endswith('_prompt_template'):
            agent_id = key.replace('_prompt_template', '')
            prompt_templates[agent_id] = value
    
    # Create a test thought
    test_thought = {
        "id": f"thought-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "content": """
        I need to design a system that processes information through multiple specialized components.
        Each component should be able to use different AI models based on its specific requirements.
        Some components need larger context windows, while others benefit from faster response times.
        The whole system should be configurable through YAML files.
        """,
        "processing_stage": "init",
        "processing_history": []
    }
    
    # Create agent instances from config
    agents = {}
    for agent_id, config in agents_config['agents'].items():
        agents[agent_id] = type('Agent', (), {
            'name': config.get('role', f"{agent_id.capitalize()} Agent"),
            'llm_config': config.get('llm_config'),
            'verbose': config.get('verbose', False)
        })
    
    # Define the processing pipeline stages
    pipeline_stages = [
        ("capture", "Capture Agent"),
        ("contextualize", "Contextualize Agent"),
        ("clarify", "Clarify Agent"),
        ("categorize", "Categorize Agent"),
        ("crystallize", "Crystallize Agent"),
        ("connect", "Connect Agent")
    ]
    
    # Process the thought through the pipeline
    logger.info("=== Testing Full Pipeline with Real LLM Calls ===")
    logger.info(f"Test thought: {test_thought['content']}")
    
    current_thought = test_thought
    result_thoughts = {}
    
    # Process sequentially through all agents
    for agent_id, agent_name in pipeline_stages:
        agent = agents[agent_id]
        logger.info(f"Processing with {agent_name} (LLM: {agent.llm_config})")
        
        start_time = time.time()
        updated_thought = process_with_agent(
            current_thought.copy(),
            agent,
            agent_name,
            agent_id,
            prompt_templates
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        # Save the result
        result_thoughts[agent_id] = updated_thought
        current_thought = updated_thought
        
        # Log a snippet of the result
        result_key = f"{agent_id}_results"
        if result_key in updated_thought:
            result_text = updated_thought[result_key]
            logger.info(f"Result snippet: {result_text[:100]}...")
    
    # Save final result to file
    output_dir = os.path.join(project_root, "test_output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "real_processing_result.json")
    with open(output_path, 'w') as f:
        json.dump(current_thought, f, indent=2)
    
    logger.info("=== Real Processing Test Complete ===")
    logger.info(f"Final result saved to {output_path}")
    
    return current_thought

if __name__ == "__main__":
    test_real_processing()