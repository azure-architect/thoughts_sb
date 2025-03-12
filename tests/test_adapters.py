# tests/test_adapters.py
import sys
import os
import argparse

# Add the parent directory to the path so Python can find the adapters package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters import create_adapter

def test_adapter(adapter_type, model_name, config=None):
    """Generic test function for any adapter type."""
    if config is None:
        config = {}
    
    # Set model name in config
    config["model"] = model_name
    
    # Create and initialize adapter
    adapter = create_adapter(adapter_type)
    adapter.initialize(config)
    
    try:
        # Test simple prompt
        prompt = "What is the adapter design pattern? Explain with examples."
        print(f"Testing {adapter_type} adapter with model {model_name}")
        print(f"Prompt: {prompt}")
        
        response = adapter.generate(
            prompt=prompt,
            system_prompt="You are a software engineering expert. Provide clear, concise explanations.",
            temperature=0.7,
            max_tokens=500
        )
        
        print("\nResponse:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
    finally:
        adapter.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test LLM adapters")
    parser.add_argument("--adapter", choices=["ollama", "litellm"], default="ollama", 
                        help="Adapter type to test")
    parser.add_argument("--model", default="llama3.1:8b", 
                        help="Model name to use")
    parser.add_argument("--base-url", default="http://localhost:11434", 
                        help="Base URL for Ollama (for ollama adapter)")
    parser.add_argument("--api-base", default=None, 
                        help="API base URL (for litellm adapter)")
    parser.add_argument("--api-key", default=None, 
                        help="API key (for litellm adapter)")
    
    args = parser.parse_args()
    
    # Prepare config based on adapter type
    if args.adapter == "ollama":
        config = {"base_url": args.base_url}
    else:  # litellm
        config = {}
        if args.api_base:
            config["api_base"] = args.api_base
        if args.api_key:
            config["api_key"] = args.api_key
    
    test_adapter(args.adapter, args.model, config)