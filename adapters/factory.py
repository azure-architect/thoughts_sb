# adapters/factory.py
from typing import Dict, Any
from .base_adapter import LLMAdapter
from .litellm_adapter import LiteLLMAdapter
from .ollama_adapter import OllamaAdapter

def create_adapter_from_config(config: Dict[str, Any]) -> LLMAdapter:
    """Create an adapter from a configuration dictionary.
    
    Args:
        config: Configuration dictionary with adapter type, model, and parameters
        
    Returns:
        An instance of the appropriate LLMAdapter
        
    Raises:
        ValueError: If the adapter type is not supported
    """
    adapter_type = config.get("adapter", "").lower()
    
    if adapter_type == "ollama":
        adapter = OllamaAdapter()
    elif adapter_type == "litellm":
        adapter = LiteLLMAdapter()
    else:
        raise ValueError(f"Unsupported adapter type: {adapter_type}")
    
    # Initialize the adapter with the config
    adapter.initialize(config)
    return adapter

# Create an alias for backward compatibility
create_adapter = create_adapter_from_config