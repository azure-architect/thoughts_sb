# utils/env_loader.py
import os
from dotenv import load_dotenv
from pathlib import Path

def load_env_vars(env_path: str = None):
    """Load environment variables from .env file."""
    if env_path is None:
        # Try to find .env in the project root
        root_dir = Path(__file__).parent.parent
        env_path = root_dir / '.env'
    
    # Load environment variables from .env file
    load_dotenv(env_path)
    
    # Check if required environment variables are set
    required_vars = []
    
    # Only warn about missing vars that might be needed
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Some features may not work properly.")