"""Configuration management for Jira Reporter."""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages configuration for Jira Reporter."""
    
    CONFIG_DIR = Path.home() / ".jira-reporter"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"
    
    def __init__(self):
        """Initialize configuration."""
        self.config_data: Dict[str, Any] = {}
        self._ensure_config_dir()
        self._load_config()
    
    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
    
    def save(self) -> None:
        """Save configuration to file."""
        with open(self.CONFIG_FILE, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config_data[key] = value
    
    def get_jira_url(self) -> Optional[str]:
        """Get Jira base URL."""
        return self.get("jira_url")
    
    def set_jira_url(self, url: str) -> None:
        """Set Jira base URL."""
        self.set("jira_url", url)
    
    def get_oauth_config(self) -> Optional[Dict[str, str]]:
        """Get OAuth configuration."""
        return self.get("oauth")
    
    def set_oauth_config(self, consumer_key: str, key_cert: str, access_token: str, access_token_secret: str) -> None:
        """Set OAuth configuration."""
        self.set("oauth", {
            "consumer_key": consumer_key,
            "key_cert": key_cert,
            "access_token": access_token,
            "access_token_secret": access_token_secret
        })
