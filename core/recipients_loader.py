"""Recipients Loader - Load email recipients from gitignored config"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional


class RecipientsLoader:
    """Load email recipients from gitignored config file"""

    def __init__(self, config_dir: Path = None):
        """
        Initialize recipients loader.

        Args:
            config_dir: Path to config directory (defaults to ./config)
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"

        self.config_dir = Path(config_dir)
        self.recipients_file = self.config_dir / "recipients.yaml"
        self.recipients_example = self.config_dir / "recipients.yaml.example"

        self._recipients_cache = None

    def load(self) -> Dict:
        """
        Load recipients configuration.

        Returns:
            Dict with 'sender', 'topics', and 'global' keys

        Raises:
            FileNotFoundError: If recipients.yaml doesn't exist
        """
        if self._recipients_cache is not None:
            return self._recipients_cache

        if not self.recipients_file.exists():
            raise FileNotFoundError(
                f"Recipients config not found: {self.recipients_file}\n"
                f"Copy {self.recipients_example} to {self.recipients_file} and add your email addresses."
            )

        with open(self.recipients_file) as f:
            self._recipients_cache = yaml.safe_load(f)

        return self._recipients_cache

    def get_sender(self) -> Dict[str, str]:
        """
        Get sender email configuration.

        Returns:
            Dict with 'name' and 'email' keys
        """
        config = self.load()
        return config.get("sender", {
            "name": "PM Radar Intelligence",
            "email": "noreply@example.com"
        })

    def get_recipients_for_topic(self, topic_id: str) -> List[str]:
        """
        Get recipient emails for a specific topic.

        Args:
            topic_id: Topic identifier (e.g., "fraud")

        Returns:
            List of email addresses
        """
        config = self.load()

        # Get topic-specific recipients
        topic_recipients = config.get("topics", {}).get(topic_id, [])

        # Add global recipients
        global_recipients = config.get("global", [])

        # Combine and deduplicate
        all_recipients = list(set(topic_recipients + global_recipients))

        return all_recipients

    def get_all_recipients(self) -> Dict[str, List[str]]:
        """
        Get all recipients organized by topic.

        Returns:
            Dict mapping topic_id to list of email addresses
        """
        config = self.load()
        topics = config.get("topics", {})
        global_recipients = config.get("global", [])

        # Add global recipients to each topic
        result = {}
        for topic_id, recipients in topics.items():
            result[topic_id] = list(set(recipients + global_recipients))

        return result


def get_recipients_loader() -> RecipientsLoader:
    """
    Get a recipients loader instance.

    Returns:
        RecipientsLoader instance

    Example:
        >>> loader = get_recipients_loader()
        >>> sender = loader.get_sender()
        >>> recipients = loader.get_recipients_for_topic("fraud")
    """
    return RecipientsLoader()
