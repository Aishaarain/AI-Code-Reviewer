"""Configuration loader for the agentic code reviewer.

Loads environment variables and provides settings for the application.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv()


class Config:
    """Configuration settings for the code reviewer."""
    
    def __init__(self):
        self.github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
        self.groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
        self.model: str = os.getenv("MODEL", "llama-3.3-70b-versatile")
        
    def validate(self) -> None:
        """Validate that required configuration is present.
        
        Raises:
            ValueError: If required configuration is missing.
        """
        if not self.github_token:
            raise ValueError(
                "GITHUB_TOKEN not set. Create a .env file with your GitHub token."
            )
        if not self.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY not set. Create a .env file with your Groq API key."
            )


# Global config instance
config = Config()
