import pytest
import os
from core.collectors.reddit import RedditCollector


@pytest.mark.skipif(not os.getenv("SOCIALCRAWL_API_KEY"), reason="No API key")
def test_reddit_collector_with_real_api():
    """Test Reddit collector with real API (requires key)"""
    config = {
        "subreddits": ["twilio"],
        "queries": [
            {
                "name": "Test Query",
                "keywords": ["fraud"],
                "timeframe": "month",
                "limit": 5
            }
        ]
    }

    api_key = os.getenv("SOCIALCRAWL_API_KEY")
    collector = RedditCollector(config, api_key=api_key)
    posts = collector.collect()

    assert isinstance(posts, list)
    # May return 0-5 posts depending on activity
    if posts:
        assert "title" in posts[0]
        assert "subreddit" in posts[0]
        assert "url" in posts[0]


def test_reddit_collector_requires_api_key():
    """Test Reddit collector fails gracefully without API key"""
    config = {"subreddits": ["test"], "queries": []}

    collector = RedditCollector(config, api_key=None)

    with pytest.raises(ValueError, match="SOCIALCRAWL_API_KEY"):
        collector.collect()
