# tests/test_ollama_adapter.py
import sys
import os

# Add the parent directory to the path so Python can find the adapters package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters import create_adapter

def test_ollama_adapter():
    """Test the Ollama adapter with an installed model."""
    # Create adapter
    adapter = create_adapter("ollama")
    
    # Initialize with a specific model
    adapter.initialize({
        "model": "llama3.1:8b",
        "base_url": "http://localhost:11434"
    })
    
    try:
        # Test basic generation
        prompt = "Explain the adapter design pattern in software engineering"
        
        print(f"Sending prompt to llama3.1:8b: {prompt}")
        response = adapter.generate(
            prompt=prompt,
            system_prompt="You are a helpful assistant with expertise in software design patterns.",
            temperature=0.7,
            max_tokens=500,
            stop_sequences=None
        )
        
        print("\nResponse from llama3.1:8b:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # Test with different parameters
        prompt2 = "Write a short poem about software design patterns"
        
        print(f"\nSending creative prompt with lower temperature: {prompt2}")
        response2 = adapter.generate(
            prompt=prompt2,
            system_prompt="You are a creative poetry writer who knows about software engineering.",
            temperature=0.5,  # Lower temperature for more focused output
            max_tokens=300,
            stop_sequences=None
        )
        
        print("\nPoem response:")
        print("-" * 50)
        print(response2)
        print("-" * 50)
        
    finally:
        # Close the adapter
        adapter.close()

if __name__ == "__main__":
    test_ollama_adapter()