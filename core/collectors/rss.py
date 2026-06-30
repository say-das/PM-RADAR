"""RSS Feed Collector - Fetches articles from RSS/Atom feeds using feedparser"""

import feedparser
from datetime import datetime
from typing import Dict, Any, List

from .base import BaseCollector


class RSSCollector(BaseCollector):
    """Collect articles from RSS feeds"""

    def collect(self) -> List[Dict[str, Any]]:
        """Collect articles from configured RSS feeds

        Returns:
            List of article dicts with keys: source, category, title, url, published, summary
        """
        # Check cache first
        if self._should_use_cache(cache_ttl_hours=24):
            return self._load_from_cache()

        articles = []
        sources = self.config.get("sources", [])

        for source in sources:
            try:
                feed = feedparser.parse(source["url"])

                for entry in feed.entries:
                    # Parse published date
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6]).isoformat()
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6]).isoformat()
                    else:
                        published = datetime.now().isoformat()

                    article = {
                        "source": source["name"],
                        "category": source.get("category", "general"),
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "published": published,
                        "summary": entry.get("summary", entry.get("description", ""))
                    }

                    articles.append(article)

            except Exception as e:
                print(f"  ✗ Error collecting from {source['name']}: {e}")
                continue

        # Save to cache
        self._save_to_cache(articles)

        return articles
