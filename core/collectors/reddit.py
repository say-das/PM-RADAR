"""Reddit Collector - Fetches posts from Reddit using SocialCrawl API"""

import requests
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base import BaseCollector


class RedditCollector(BaseCollector):
    """Collect posts from Reddit via SocialCrawl API"""

    def __init__(self, config: Dict[str, Any], api_key: Optional[str] = None):
        super().__init__(config, api_key)
        self.base_url = "https://www.socialcrawl.dev/v1/reddit/subreddit/search"

    def collect(self) -> List[Dict[str, Any]]:
        """Collect posts from Reddit

        Returns:
            List of post dicts with keys: query, subreddit, title, author, score,
            num_comments, url, selftext, created_utc
        """
        if not self.api_key:
            raise ValueError("Reddit collector requires SOCIALCRAWL_API_KEY")

        # Check cache first (24h TTL)
        if self._should_use_cache(cache_ttl_hours=24):
            return self._load_from_cache()

        posts = []
        subreddits = self.config.get("subreddits", [])
        queries = self.config.get("queries", [])

        for query_config in queries:
            query_name = query_config["name"]
            keywords = query_config["keywords"]
            timeframe = query_config.get("timeframe", "week")
            limit = query_config.get("limit", 25)

            # Build search query
            search_query = " OR ".join(keywords)

            # Search each subreddit
            for subreddit in subreddits:
                try:
                    response = self._api_call(subreddit, search_query, timeframe)
                    items = response.get("data", {}).get("items", [])

                    for item in items[:limit]:
                        post = item.get("post", {})
                        post_id = post.get("id", "")
                        subreddit_name = post.get("ext", {}).get("subreddit", subreddit)

                        # Construct Reddit URL
                        post_url = f"https://reddit.com/r/{subreddit_name}/comments/{post_id}"

                        # Parse engagement
                        engagement = post.get("engagement", {})
                        content = post.get("content", {})
                        author = post.get("author", {}).get("username", "[deleted]")

                        # Convert timestamp
                        published_at = post.get("published_at", 0)
                        created_utc = datetime.fromtimestamp(published_at).isoformat() if published_at else datetime.now().isoformat()

                        post_data = {
                            "query": query_name,
                            "search_terms": search_query,
                            "subreddit": subreddit_name,
                            "title": content.get("text", "")[:200],
                            "author": author,
                            "score": engagement.get("likes", 0),
                            "num_comments": engagement.get("comments", 0),
                            "created_utc": created_utc,
                            "url": post_url,
                            "selftext": content.get("text", ""),
                            "upvote_ratio": None,
                            "is_self": True,
                            "comments": []
                        }

                        posts.append(post_data)

                except Exception as e:
                    print(f"  ✗ Error collecting from r/{subreddit}: {e}")
                    continue

        # Save to cache
        self._save_to_cache(posts)

        return posts

    def _api_call(self, subreddit: str, query: str, timeframe: str) -> dict:
        """Make SocialCrawl API call"""
        headers = {
            "x-api-key": self.api_key,
            "Cache-Control": "no-cache",
            "Idempotency-Key": f"pmradar-{uuid.uuid4()}"
        }

        params = {
            "subreddit": subreddit,
            "query": query,
            "timeframe": timeframe,
            "sort": "relevance",
            "cursor": ""
        }

        response = requests.get(self.base_url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            raise ValueError(f"SocialCrawl API error: {response.status_code}")

        return response.json()
