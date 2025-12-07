"""Tests for configuration management."""

import pytest
import tempfile
import shutil
from pathlib import Path
from jira_reporter.config import Config


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Create a temporary config directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    monkeypatch.setattr(Config, 'CONFIG_DIR', temp_dir)
    monkeypatch.setattr(Config, 'CONFIG_FILE', temp_dir / "config.yaml")
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_config_initialization(temp_config_dir):
    """Test config initialization creates directory."""
    config = Config()
    assert config.CONFIG_DIR.exists()


def test_config_get_set(temp_config_dir):
    """Test setting and getting configuration values."""
    config = Config()
    config.set("test_key", "test_value")
    assert config.get("test_key") == "test_value"


def test_config_get_default(temp_config_dir):
    """Test getting non-existent key returns default."""
    config = Config()
    assert config.get("nonexistent", "default") == "default"


def test_config_save_load(temp_config_dir):
    """Test saving and loading configuration."""
    config1 = Config()
    config1.set("key1", "value1")
    config1.set("key2", "value2")
    config1.save()
    
    config2 = Config()
    assert config2.get("key1") == "value1"
    assert config2.get("key2") == "value2"


def test_jira_url_methods(temp_config_dir):
    """Test Jira URL getter and setter."""
    config = Config()
    config.set_jira_url("https://jira.example.com")
    assert config.get_jira_url() == "https://jira.example.com"


def test_oauth_config_methods(temp_config_dir):
    """Test OAuth configuration getter and setter."""
    config = Config()
    config.set_oauth_config(
        "consumer_key",
        "key_cert_data",
        "access_token",
        "access_token_secret"
    )
    
    oauth = config.get_oauth_config()
    assert oauth["consumer_key"] == "consumer_key"
    assert oauth["key_cert"] == "key_cert_data"
    assert oauth["access_token"] == "access_token"
    assert oauth["access_token_secret"] == "access_token_secret"
