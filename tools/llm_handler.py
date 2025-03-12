import os
import json
import yaml
import logging
from datetime import datetime
from adapters import create_llm_adapter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
llm_adapter = None
LLM_CONFIGS = {}

def initialize_llm_configs(config_path, adapter_type="litellm"):
    """
    Initialize the global LLM configurations and adapter.
    This should be called at system startup.
    
    Args:
        config_path (str): Path to the YAML config file
        adapter_type (str): Type of adapter to use ("litellm" or "ollama")
    """
    global LLM_CONFIGS, llm_adapter
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Extract LLM configurations
        LLM_CONFIGS = config.get('llm_configs', {})
        
        # Create and initialize the adapter
        llm_adapter = create_llm_adapter(adapter_type)
        llm_adapter.initialize(LLM_CONFIGS)
        
        logger.info(f"Loaded {len(LLM_CONFIGS)} LLM configurations: {list(LLM_CONFIGS.keys())}")
        
    except Exception as e:
        logger.error(f"Error initializing LLM configurations: {e}")
        LLM_CONFIGS = {'default': {
            'provider': 'ollama',
            'model': 'qwen2.5:14b',
            'temperature': 0.7
        }}
        # Create a fallback adapter
        llm_adapter = create_llm_adapter("litellm")
        llm_adapter.initialize(LLM_CONFIGS)

def communicate_with_llm(prompt, config_name='default'):
    """
    Communicate with the LLM and get a response using the configured adapter.
    
    Args:
        prompt (str): The prompt to send to the LLM.
        config_name (str): Name of the LLM configuration to use
        
    Returns:
        str: The response from the LLM.
    """
    global llm_adapter
    
    print("========= COMMUNICATE WITH LLM FUNCTION CALLED =========")
    
    # Check if adapter is initialized
    if llm_adapter is None:
        logger.error("LLM adapter not initialized")
        return "ERROR: LLM adapter not initialized"
    
    try:
        # Use the adapter to get a response
        response = llm_adapter.complete(prompt, config_name)
        print(f"Received response from LLM, length: {len(response)}")
        return response
    except Exception as e:
        logger.error(f"Error communicating with LLM: {e}")
        return f"ERROR: Failed to communicate with LLM: {str(e)}"