import os
import json
import time
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import litellm  # Changed from langchain_community.llms import Ollama

def communicate_with_llm(prompt, model_name="qwen2.5:14b", provider="ollama", temperature=0.7, api_key=None):
    """
    Communicate with the LLM and get a response.
    
    Args:
        prompt (str): The prompt to send to the LLM.
        model_name (str): The name of the model to use.
        provider (str): The provider to use ("ollama", "gemini", "openai", etc.)
        temperature (float): The temperature setting for generation.
        api_key (str): API key for external providers (not needed for Ollama)
        
    Returns:
        str: The response from the LLM.
    """
    print("========= COMMUNICATE WITH LLM FUNCTION CALLED =========")
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



