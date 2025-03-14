# tests/mock_adapter.py
from typing import Dict, Any, Optional, List
from adapters.base_adapter import LLMAdapter

class MockLLMAdapter(LLMAdapter):
    """Mock adapter for testing LLM integration."""
    
    def __init__(self, responses=None):
        """Initialize with predetermined responses."""
        self.responses = responses or {}
        self.default_response = "Mock LLM response"
        self.config = {}
        self.calls = []
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the adapter with configuration."""
        self.config = config
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Update the adapter configuration."""
        self.config.update(config)
    
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None,
                temperature: float = 0.7,
                max_tokens: int = 1000,
                stop_sequences: Optional[List[str]] = None) -> str:
        """Generate a response using predefined responses."""
        # Record the call for later verification
        self.calls.append({
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop_sequences": stop_sequences
        })
        
        # Get response based on prompt or use default
        for key, response in self.responses.items():
            if key in prompt:
                return response
        return self.default_response
    
    def close(self) -> None:
        """Close the adapter."""
        pass