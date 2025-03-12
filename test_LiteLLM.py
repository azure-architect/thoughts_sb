# test_litellm_integration.py
import os
import json
from tools.tools import communicate_with_llm

def test_integration():
    """Test the LiteLLM integration with your existing system"""
    prompt = "Hello, please summarize this small test in one sentence."
    
    print("Testing LiteLLM integration...")
    
    # Test the communicate_with_llm function
    response = communicate_with_llm(prompt)
    
    print(f"Response: {response}")
    print(f"Response length: {len(response)}")
    
    # Check if the response is reasonable
    if len(response) > 0 and not response.startswith("ERROR:"):
        print("✅ Test passed: LiteLLM integration is working")
        return True
    else:
        print("❌ Test failed: LiteLLM integration not working properly")
        return False

if __name__ == "__main__":
    test_integration()