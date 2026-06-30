import pytest
from core.collectors.rss import RSSCollector


def test_rss_collector_loads_config():
    """Test RSS collector loads YAML config"""
    config = {
        "sources": [
            {
                "name": "Test Feed",
                "url": "https://example.com/feed.xml",
                "category": "test"
            }
        ]
    }

    collector = RSSCollector(config)
    assert len(collector.config["sources"]) == 1


def test_rss_collector_collect_returns_list():
    """Test collect returns list of articles"""
    config = {
        "sources": [
            {
                "name": "Commsrisk",
                "url": "https://commsrisk.com/feed/",
                "category": "telecom_fraud"
            }
        ]
    }

    collector = RSSCollector(config)
    # This will make a real API call
    articles = collector.collect()

    assert isinstance(articles, list)
    # Articles should have required fields
    if articles:
        assert "title" in articles[0]
        assert "url" in articles[0]
        assert "published" in articles[0]
