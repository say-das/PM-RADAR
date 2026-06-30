import pytest
from core.collectors.orchestrator import CollectorOrchestrator


def test_orchestrator_loads_topic():
    """Test orchestrator loads topic configuration"""
    orchestrator = CollectorOrchestrator("fraud")

    assert orchestrator.topic_id == "fraud"
    assert orchestrator.topic_config["id"] == "fraud"


def test_orchestrator_collect_all_returns_dict():
    """Test collect_all returns properly structured dict"""
    orchestrator = CollectorOrchestrator("fraud")

    # This makes real API calls - quick test
    collected = orchestrator.collect_all()

    assert "collected_at" in collected
    assert "rss_articles" in collected
    assert "reddit_posts" in collected
    assert "competitor_changelogs" in collected

    assert isinstance(collected["rss_articles"], list)
    assert isinstance(collected["reddit_posts"], list)
    assert isinstance(collected["competitor_changelogs"], list)
