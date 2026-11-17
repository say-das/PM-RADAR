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


def test_collect_handles_iso_string_published_at(monkeypatch):
    """SocialCrawl returns published_at as an ISO string; must not crash."""
    config = {
        "subreddits": ["twilio"],
        "queries": [{"name": "q", "keywords": ["fraud"], "timeframe": "week", "limit": 5}],
    }
    collector = RedditCollector(config, api_key="x")
    monkeypatch.setattr(collector, "_should_use_cache", lambda **kw: False)
    monkeypatch.setattr(collector, "_save_to_cache", lambda posts: None)
    monkeypatch.setattr(collector, "_api_call", lambda *a, **k: {"data": {"items": [
        {"post": {"id": "abc", "published_at": "2026-07-12T17:34:01.000Z",
                  "content": {"text": "hello"}, "author": {"username": "u"},
                  "engagement": {"likes": 2, "comments": 5}, "ext": {"subreddit": "twilio"}}},
        {"post": {"id": "def", "published_at": 1752341641,
                  "content": {"text": "epoch"}, "engagement": {}}},
        {"post": {"id": "ghi", "published_at": None, "content": {"text": "none"}}},
    ]}})

    posts = collector.collect()

    assert len(posts) == 3
    assert posts[0]["created_utc"].startswith("2026-07-12T17:34:01")
    assert all("created_utc" in p for p in posts)


def test_collect_drops_off_subreddit_results(monkeypatch):
    """API returns site-wide posts when r/twilio has no matches; drop them."""
    config = {
        "subreddits": ["twilio"],
        "queries": [{"name": "q", "keywords": ["fraud"], "timeframe": "week", "limit": 25}],
    }
    collector = RedditCollector(config, api_key="x")
    monkeypatch.setattr(collector, "_should_use_cache", lambda **kw: False)
    monkeypatch.setattr(collector, "_save_to_cache", lambda posts: None)

    def post(pid, sub):
        return {"post": {"id": pid, "published_at": "2026-11-10T00:00:00.000Z",
                         "content": {"text": "t"}, "ext": {"subreddit": sub}}}

    monkeypatch.setattr(collector, "_api_call", lambda *a, **k: {"data": {"items": [
        post("1", "linkedin"), post("2", "Twilio"), post("3", "Steam")]}})

    posts = collector.collect()

    assert [p["subreddit"] for p in posts] == ["Twilio"]
