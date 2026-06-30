"""Collectors - Data ingestion plugins"""

from .base import BaseCollector
from .rss import RSSCollector
from .reddit import RedditCollector
from .changelog import ChangelogCollector
from .orchestrator import CollectorOrchestrator

__all__ = ["BaseCollector", "RSSCollector", "RedditCollector", "ChangelogCollector", "CollectorOrchestrator"]
