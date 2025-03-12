# adapters/litellm_adapter.py
from typing import Dict, Any, Optional, List
import litellm
import os
from .base_adapter import LLMAdapter

class LiteLLMAdapter(LLMAdapter):
    """Adapter for communicating with LLMs through LiteLLM."""
    
    def __init__(self):
        self.model = None
        self.temperature = 0.7
        self.max_tokens = 1000
        
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the LiteLLM adapter with configuration."""
        self.model = config.get("model", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1000)
        
        # Handle API keys from config
        api_key = config.get("api_key")
        if api_key:
            # Set the appropriate environment variable for the model type
            model_prefix = self.model.split("-")[0].lower()
            if "gemini" in model_prefix:
                os.environ["GOOGLE_API_KEY"] = api_key
            elif "gpt" in model_prefix or "openai" in model_prefix:
                os.environ["OPENAI_API_KEY"] = api_key
            elif "claude" in model_prefix:
                os.environ["ANTHROPIC_API_KEY"] = api_key
            else:
                # Generic fallback
                litellm.api_key = api_key
        
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None,
                temperature: Optional[float] = None,
                max_tokens: Optional[int] = None,
                stop_sequences: Optional[List[str]] = None) -> str:
        """Generate a response using LiteLLM."""
        # Use provided params or fall back to initialized values
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                stop=stop_sequences
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response with LiteLLM: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def close(self) -> None:
        """Close any open resources."""
        # LiteLLM typically doesn't need explicit cleanup
        pass