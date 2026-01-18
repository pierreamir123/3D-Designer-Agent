"""
Configuration module for 3D Designer Agent.
Handles LiteLLM integration and model configuration.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class LiteLLMConfig:
    """Configuration for LiteLLM proxy integration."""
    
    def __init__(self):
        # LiteLLM proxy configuration
        # Default to http://localhost:4000 if not specified
        self.base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        self.api_key = os.getenv("LITELLM_API_KEY", "")
        
        # Model names (these should match your LiteLLM proxy configuration)
        self.default_model = os.getenv("LITELLM_MODEL", "gpt-4o")
        
    def get_openai_config(self) -> dict:
        """
        Returns configuration dict for LangChain's ChatOpenAI to use LiteLLM proxy.
        """
        config = {
            "model": self.default_model,
            "api_key": self.api_key,
            "temperature": 0
        }
        
        # Add base URL - LangChain uses 'base_url' in newer versions
        if self.base_url:
            config["base_url"] = self.base_url
            
        return config

# Global config instance
config = LiteLLMConfig()
