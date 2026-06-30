"""Collectors - Data ingestion plugins"""

from .base import BaseCollector
from .rss import RSSCollector
from .reddit import RedditCollector
from .changelog import ChangelogCollector

__all__ = ["BaseCollector", "RSSCollector", "RedditCollector", "ChangelogCollector"]
