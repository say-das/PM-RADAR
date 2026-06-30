"""Changelog Collector - Scrapes competitor changelog pages

NOTE: This is a stub implementation that wraps the existing v1 changelog scraper.
Full refactor to native BaseCollector implementation deferred to Sub-Project 2.
"""

import subprocess
import json
from typing import Dict, Any, List
from pathlib import Path

from .base import BaseCollector


class ChangelogCollector(BaseCollector):
    """Collect changelog entries from competitor websites"""

    def collect(self) -> List[Dict[str, Any]]:
        """Collect changelog entries

        Returns:
            List of changelog dicts with keys: competitor, product, title, date, description, url
        """
        # Check cache first (168h = 1 week TTL)
        if self._should_use_cache(cache_ttl_hours=168):
            return self._load_from_cache()

        # STUB: Delegate to existing v1 changelog scraper
        # TODO: Refactor v1 script into native BaseCollector implementation
        try:
            result = subprocess.run(
                ["python3", "scripts/collect/changelog_scraper_v3.py"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                print(f"  ✗ Changelog scraper error: {result.stderr[:200]}")
                return []

            # Parse output from v1 script (it writes to data/raw/*.json)
            # For now, return empty list and let v1 pipeline handle it
            changelogs = []

            # Save to cache
            self._save_to_cache(changelogs)

            return changelogs

        except Exception as e:
            print(f"  ✗ Error running changelog collector: {e}")
            return []
