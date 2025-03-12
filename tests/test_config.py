# test_llm_setup.py
import yaml
import os
from tools.llm_handler import initialize_llm_configs, communicate_with_llm

def test_basic_llm_integration():
    """Test the basic LLM integration to see if we can load config and send a prompt."""
    
    config_path = "config/test.yaml"
    print(f"Loading config from {config_path}")
    
    # Initialize LLM configurations
    initialize_llm_configs(config_path)
    
    # Load the config to show what we're working with
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # List available LLM configs
    llm_configs = config.get('llm_configs', {})
    print(f"Available LLM configs: {list(llm_configs.keys())}")
    
    # Pick a test config to use - let's use ollama_qwen or the default
    test_config_name = 'ollama_mistral' if 'ollama_mistral' in llm_configs else 'default'
    print(f"Using config: {test_config_name}")
    
    # Create a simple test prompt
    test_prompt = "Hello, this is a test message. Please respond with a short greeting."
    
    # Try to send the prompt and get a response
    print(f"Sending test prompt: '{test_prompt}'")
    try:
        response = communicate_with_llm(test_prompt, test_config_name)
        print("Success! Response received:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"Error communicating with LLM: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting basic LLM integration test...")
    result = test_basic_llm_integration()
    print(f"Test {'succeeded' if result else 'failed'}")