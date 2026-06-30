"""Base collector interface - all collectors inherit from this"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta


class BaseCollector(ABC):
    """Abstract base class for all collectors

    Collectors fetch raw data from external sources (RSS, Reddit, APIs).
    Each collector implements its own caching and rate limiting logic.
    """

    def __init__(self, config: Dict[str, Any], api_key: Optional[str] = None):
        """Initialize collector

        Args:
            config: Collector-specific configuration dict
            api_key: Optional API key for authenticated collectors
        """
        self.config = config
        self.api_key = api_key
        self.cache_dir = Path("data/raw/.cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """Collect data from source

        Returns:
            List of collected items (articles, posts, changes)

        Each item should be a dict with at least:
        - id: unique identifier
        - title: item title/summary
        - url: source URL
        - published: publication date (ISO format)
        """
        pass

    def _get_cache_key(self) -> str:
        """Generate cache key from config"""
        cache_data = json.dumps(self.config, sort_keys=True)
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _get_cache_path(self) -> Path:
        """Get path to cache file"""
        cache_key = self._get_cache_key()
        collector_name = self.__class__.__name__.lower()
        return self.cache_dir / f"{collector_name}_{cache_key}.json"

    def _should_use_cache(self, cache_ttl_hours: int = 24) -> bool:
        """Check if cached data is still valid

        Args:
            cache_ttl_hours: Cache time-to-live in hours

        Returns:
            True if cache exists and is still valid
        """
        cache_path = self._get_cache_path()

        if not cache_path.exists():
            return False

        try:
            with open(cache_path) as f:
                cached = json.load(f)

            cached_time = datetime.fromisoformat(cached["cached_at"])
            age = datetime.now() - cached_time

            return age < timedelta(hours=cache_ttl_hours)
        except Exception:
            return False

    def _load_from_cache(self) -> List[Dict[str, Any]]:
        """Load data from cache"""
        cache_path = self._get_cache_path()

        with open(cache_path) as f:
            cached = json.load(f)

        return cached["data"]

    def _save_to_cache(self, data: List[Dict[str, Any]]):
        """Save data to cache"""
        cache_path = self._get_cache_path()

        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "config": self.config,
            "data": data
        }

        with open(cache_path, "w") as f:
            json.dump(cache_data, f, indent=2)
