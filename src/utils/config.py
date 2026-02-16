"""Configuration management for the Agentic Assistant."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager for loading and accessing app settings."""

    def __init__(self, config_path: str = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to YAML config file. Defaults to config/config.yaml
        """
        self.base_dir = Path(__file__).parent.parent.parent
        self.config_dir = self.base_dir / "config"
        
        # Load environment variables
        env_path = self.config_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        
        # Load YAML configuration
        if config_path is None:
            config_path = self.config_dir / "config.yaml"
        else:
            config_path = Path(config_path)
        
        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., 'agent.model')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_env(self, key: str, default: str = None) -> str:
        """Get environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key."""
        return self.get_env("OPENAI_API_KEY", "")
    
    @property
    def openrouter_api_key(self) -> str:
        """Get OpenRouter API key."""
        return self.get_env("OPENROUTER_API_KEY", "")
    
    @property
    def langsmith_api_key(self) -> str:
        """Get LangSmith API key."""
        return self.get_env("LANGSMITH_API_KEY", "")
    
    @property
    def zomato_api_key(self) -> str:
        """Get Zomato API key."""
        return self.get_env("ZOMATO_API_KEY", "")
    
    @property
    def langsmith_enabled(self) -> bool:
        """Check if LangSmith monitoring is enabled."""
        return (
            self.get("monitoring.langsmith_enabled", False)
            and bool(self.langsmith_api_key)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()


# Global configuration instance
config = Config()
