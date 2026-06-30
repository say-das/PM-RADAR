import pytest
from pathlib import Path
from core.config_loader import ConfigLoader

def test_load_global_config():
    """Test loading global configuration"""
    loader = ConfigLoader()
    config = loader.load_global_config()

    assert "branding" in config
    assert config["branding"]["primary_color"] == "#F22F46"
    assert "email" in config

def test_load_topic_config():
    """Test loading topic configuration"""
    loader = ConfigLoader()
    topic_config = loader.load_topic_config("fraud")

    assert topic_config["id"] == "fraud"
    assert "llm" in topic_config
    assert "sources" in topic_config

def test_load_nonexistent_topic_raises_error():
    """Test loading non-existent topic fails gracefully"""
    loader = ConfigLoader()

    with pytest.raises(FileNotFoundError):
        loader.load_topic_config("nonexistent")
