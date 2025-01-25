import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict

def load_config() -> Dict[str, str]:
    """
    Load configuration from the .env file or environment variables.
            
    Returns:
        Dict[str, str]: Dictionary containing configuration values
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    env_file = project_root / ".env"
    load_dotenv(env_file)
    
    # Required configurations
    required_vars = ["BOT_TOKEN", "CHAT_ID", "HUGGINGFACE_LLM_TOKEN", "HUGGINGFACE_IMAGE_TOKEN",    
                    "SUPABASE_URL", "SUPABASE_KEY"]
    config = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        config[var] = value
    
    return config