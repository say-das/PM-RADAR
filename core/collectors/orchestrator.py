"""Collector Orchestrator - Manages data collection from multiple sources"""

from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

from .rss import RSSCollector
from .reddit import RedditCollector
from .changelog import ChangelogCollector
from ..config_loader import ConfigLoader


class CollectorOrchestrator:
    """Orchestrates data collection across multiple collector types"""

    def __init__(self, topic_id: str):
        """Initialize orchestrator for a topic

        Args:
            topic_id: Topic identifier (e.g., "fraud")
        """
        self.topic_id = topic_id
        self.config_loader = ConfigLoader()
        self.topic_config = self.config_loader.load_topic_config(topic_id)

    def collect_all(self) -> Dict[str, Any]:
        """Collect data from all configured sources

        Returns:
            Dictionary with keys: rss_articles, reddit_posts, competitor_changelogs
        """
        collected_data = {
            "collected_at": datetime.now().isoformat(),
            "topic": self.topic_id,
            "rss_articles": [],
            "reddit_posts": [],
            "competitor_changelogs": []
        }

        # Collect from each source type
        for source_config in self.topic_config.get("sources", []):
            source_type = source_config["type"]

            try:
                if source_type == "rss":
                    collected_data["rss_articles"] = self._collect_rss(source_config)

                elif source_type == "reddit":
                    collected_data["reddit_posts"] = self._collect_reddit(source_config)

                elif source_type == "changelog":
                    collected_data["competitor_changelogs"] = self._collect_changelogs(source_config)

            except Exception as e:
                print(f"  ✗ Error collecting from {source_type}: {e}")
                continue

        return collected_data

    def _collect_rss(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect RSS articles"""
        print(f"→ Collecting RSS articles...")

        config_path = source_config.get("config_path")
        rss_config = self.config_loader.load_source_config(self.topic_id, "rss")

        collector = RSSCollector(rss_config)
        articles = collector.collect()

        print(f"  ✓ Collected {len(articles)} RSS articles")
        return articles

    def _collect_reddit(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect Reddit posts"""
        print(f"→ Collecting Reddit posts...")

        import os
        api_key = os.getenv(source_config.get("api_key_env", "SOCIALCRAWL_API_KEY"))

        reddit_config = self.config_loader.load_source_config(self.topic_id, "reddit")

        collector = RedditCollector(reddit_config, api_key=api_key)
        posts = collector.collect()

        print(f"  ✓ Collected {len(posts)} Reddit posts")
        return posts

    def _collect_changelogs(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect competitor changelogs"""
        print(f"→ Collecting competitor changelogs...")

        changelog_config = self.config_loader.load_source_config(self.topic_id, "changelogs")

        collector = ChangelogCollector(changelog_config)
        changelogs = collector.collect()

        print(f"  ✓ Collected {len(changelogs)} changelog entries")
        return changelogs

    def save_raw_data(self, collected_data: Dict[str, Any], output_dir: Path = None):
        """Save collected data to JSON file

        Args:
            collected_data: Data dictionary from collect_all()
            output_dir: Output directory (defaults to data/raw)
        """
        if output_dir is None:
            output_dir = Path("data/raw")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save with date-based filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_file = output_dir / f"{date_str}.json"

        with open(output_file, "w") as f:
            json.dump(collected_data, f, indent=2)

        print(f"✓ Saved raw data to {output_file}")
