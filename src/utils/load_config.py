import os
from dotenv import load_dotenv
from typing import Dict

def load_config(env_file: str = ".env") -> Dict[str, str]:
    """
    Load configuration from the .env file or environment variables.
    
    Args:
        env_file (str): Path to the .env file
        
    Returns:
        Dict[str, str]: Dictionary containing configuration values
    """
    load_dotenv(env_file)
    
    # Required configurations
    required_vars = ["BOT_TOKEN", "CHAT_ID", "HUGGINGFACE_API_TOKEN"]
    config = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        config[var] = value
    
    return config