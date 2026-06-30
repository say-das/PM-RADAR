"""Collectors - Data ingestion plugins"""

from .base import BaseCollector
from .rss import RSSCollector
from .reddit import RedditCollector

__all__ = ["BaseCollector", "RSSCollector", "RedditCollector"]
