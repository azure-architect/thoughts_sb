from .base_adapter import LLMAdapter
from .litellm_adapter import LiteLLMAdapter
from .ollama_adapter import OllamaAdapter







def create_adapter_from_config(config):
    """Create an adapter from a configuration dictionary or adapter type string.
    
    Args:
        config: Either a configuration dictionary or a string with the adapter type
        
    Returns:
        An instance of the appropriate LLMAdapter
    """
    # Handle case where config is just a string (adapter type)
    if isinstance(config, str):
        adapter_type = config.lower()
        config = {"adapter": adapter_type}  # Create minimal config dict
    else:
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