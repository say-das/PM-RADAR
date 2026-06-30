"""Configuration loader for PM Radar v2"""

import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """Loads and validates YAML configuration files"""

    def __init__(self, base_path: Path = None):
        """Initialize config loader

        Args:
            base_path: Base directory for configs (defaults to project root)
        """
        if base_path is None:
            # Auto-detect project root (where config/ folder lives)
            current = Path(__file__).resolve()
            # Go up from core/config_loader.py to project root
            self.base_path = current.parent.parent
        else:
            self.base_path = Path(base_path)

        self.config_dir = self.base_path / "config"
        self.topics_dir = self.config_dir / "topics"

    def load_global_config(self) -> Dict[str, Any]:
        """Load global configuration

        Returns:
            Dictionary containing global config

        Raises:
            FileNotFoundError: If global.yaml doesn't exist
        """
        global_path = self.config_dir / "global.yaml"

        if not global_path.exists():
            raise FileNotFoundError(f"Global config not found: {global_path}")

        with open(global_path, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def load_topic_config(self, topic_id: str) -> Dict[str, Any]:
        """Load topic-specific configuration

        Args:
            topic_id: Topic identifier (e.g., "fraud")

        Returns:
            Dictionary containing topic config

        Raises:
            FileNotFoundError: If topic config doesn't exist
        """
        topic_path = self.topics_dir / topic_id / "topic.yaml"

        if not topic_path.exists():
            raise FileNotFoundError(f"Topic config not found: {topic_path}")

        with open(topic_path, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def load_source_config(self, topic_id: str, source_type: str) -> Dict[str, Any]:
        """Load source-specific configuration

        Args:
            topic_id: Topic identifier
            source_type: Source type (e.g., "rss", "reddit", "changelog")

        Returns:
            Dictionary containing source config

        Raises:
            FileNotFoundError: If source config doesn't exist
        """
        source_path = self.topics_dir / topic_id / f"{source_type}.yaml"

        if not source_path.exists():
            raise FileNotFoundError(f"Source config not found: {source_path}")

        with open(source_path, 'r') as f:
            config = yaml.safe_load(f)

        return config
