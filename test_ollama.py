# test_ollama_available.py
import requests
from langchain_community.llms import Ollama
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_available_models():
    """Get list of available models from Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        else:
            logger.error(f"Failed to get models, status code: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return []

def test_with_available_model():
    """Test using first available model"""
    models = get_available_models()
    
    if not models:
        logger.error("No models available in Ollama")
        return False
    
    # Use the first available model
    model_name = models[0]
    logger.info(f"Testing with available model: {model_name}")
    
    try:
        llm = Ollama(
            model=model_name,
            temperature=0.7,
            base_url="http://localhost:11434"
        )
        
        prompt = "Hello, this is a test message. Please respond with a short greeting."
        logger.info(f"Sending prompt to model {model_name}")
        
        response = llm.invoke(prompt)
        
        logger.info(f"SUCCESS! Model {model_name} responded with:")
        logger.info(response)
        return True
    except Exception as e:
        logger.error(f"ERROR with model {model_name}: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Checking available Ollama models...")
    models = get_available_models()
    logger.info(f"Available models: {models}")
    
    success = test_with_available_model()
    sys.exit(0 if success else 1)