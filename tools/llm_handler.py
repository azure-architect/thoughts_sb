import os
import json
import yaml
import time
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import litellm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global cache for LLM configurations
LLM_CONFIGS = {}

def load_llm_configs(config_path):
    """
    Load LLM configurations from the YAML config file.
    
    Args:
        config_path (str): Path to the YAML config file
        
    Returns:
        dict: Dictionary of LLM configurations
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Extract LLM configurations
        llm_configs = config.get('llm', {})
        
        # Add a reference to each config's name
        for name, cfg in llm_configs.items():
            if isinstance(cfg, dict):  # Make sure it's a valid config dict
                cfg['name'] = name  # Add name for reference
                
        return llm_configs
    except Exception as e:
        logger.error(f"Error loading LLM configurations: {e}")
        return {'default': {
            'provider': 'ollama',
            'model_name': 'qwen2.5:14b',
            'temperature': 0.7,
            'name': 'default'
        }}

def initialize_llm_configs(config_path):
    """
    Initialize the global LLM configurations.
    This should be called at system startup.
    
    Args:
        config_path (str): Path to the YAML config file
    """
    global LLM_CONFIGS
    LLM_CONFIGS = load_llm_configs(config_path)
    logger.info(f"Loaded {len(LLM_CONFIGS)} LLM configurations: {list(LLM_CONFIGS.keys())}")

def get_llm_config(config_name='default'):
    """
    Get an LLM configuration by name.
    
    Args:
        config_name (str): Name of the configuration to use
        
    Returns:
        dict: The requested LLM configuration or the default
    """
    if not LLM_CONFIGS:
        logger.warning("LLM configurations not initialized, using hardcoded default")
        return {
            'provider': 'ollama',
            'model_name': 'qwen2.5:14b',
            'temperature': 0.7,
            'name': 'default'
        }
    
    config = LLM_CONFIGS.get(config_name)
    if not config:
        logger.warning(f"LLM configuration '{config_name}' not found, using default")
        return LLM_CONFIGS.get('default', {
            'provider': 'ollama',
            'model_name': 'qwen2.5:14b',
            'temperature': 0.7,
            'name': 'default'
        })
    
    return config

def communicate_with_llm(prompt, llm_config_name='default'):
    """
    Communicate with the LLM and get a response.
    
    Args:
        prompt (str): The prompt to send to the LLM.
        llm_config_name (str): Name of the LLM configuration to use
        
    Returns:
        str: The response from the LLM.
    """
    print("========= COMMUNICATE WITH LLM FUNCTION CALLED =========")
    
    # Get the specified LLM configuration
    if LLM_CONFIGS and llm_config_name in LLM_CONFIGS:
        config = LLM_CONFIGS[llm_config_name]
        provider = config.get('provider', 'ollama')
        model_name = config.get('model_name', 'qwen2.5:14b')
        temperature = config.get('temperature', 0.7)
        api_key = config.get('api_key')
    else:
        # Fall back to defaults if config not found
        provider = "ollama"
        model_name = "qwen2.5:14b"
        temperature = 0.7
        api_key = None
    
    print(f"Using provider: {provider}, model: {model_name}")
    print(f"Prompt first 100 chars: {prompt[:100]}...")
    
    try:
        # Configure model based on provider
        if provider.lower() == "ollama":
            # Ollama is local, use the direct model name format
            full_model_name = f"ollama/{model_name}"
            litellm.ollama_api_base = "http://localhost:11434"
        elif provider.lower() == "gemini":
            # For Gemini, use the gemini model format
            full_model_name = f"gemini/{model_name}"
            # Set API key if provided
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key
        elif provider.lower() == "openai":
            # For OpenAI, use the openai model format
            full_model_name = f"openai/{model_name}"
            # Set API key if provided
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
        elif provider.lower() == "anthropic":
            # For Anthropic/Claude, use the claude model format
            full_model_name = f"anthropic/{model_name}"
            if api_key:
                os.environ["ANTHROPIC_API_KEY"] = api_key
        else:
            # Default fallback to Ollama
            print(f"Unknown provider '{provider}', falling back to Ollama")
            full_model_name = f"ollama/{model_name}"
            litellm.ollama_api_base = "http://localhost:11434"
        
        print(f"Using model: {full_model_name}")
        
        # Get response from LLM
        response = litellm.completion(
            model=full_model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        
        # Extract the actual response text
        response_text = response.choices[0].message.content
        
        print(f"Received response from LLM, length: {len(response_text)}")
        return response_text
    except Exception as e:
        print(f"LLM ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return f"ERROR: Failed to communicate with LLM: {str(e)}"