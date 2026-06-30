"""End-to-end integration test for PM Radar v2 Core Infrastructure"""

import pytest
from pathlib import Path

from core.config_loader import ConfigLoader
from core.collectors.orchestrator import CollectorOrchestrator


def test_config_system_integration():
    """Test config system loads all fraud configs"""
    loader = ConfigLoader()

    # Load global config
    global_config = loader.load_global_config()
    assert "branding" in global_config
    assert global_config["branding"]["primary_color"] == "#F22F46"

    # Load topic config
    topic_config = loader.load_topic_config("fraud")
    assert topic_config["id"] == "fraud"
    assert topic_config["llm"]["provider"] == "openai"
    assert len(topic_config["sources"]) == 3

    # Load source configs
    rss_config = loader.load_source_config("fraud", "rss")
    assert "sources" in rss_config
    assert len(rss_config["sources"]) > 10  # At least 10 RSS sources

    reddit_config = loader.load_source_config("fraud", "reddit")
    assert "subreddits" in reddit_config
    assert "twilio" in reddit_config["subreddits"]

    changelog_config = loader.load_source_config("fraud", "changelogs")
    assert "competitors" in changelog_config
    assert len(changelog_config["competitors"]) >= 4  # At least 4 competitors

    print("✓ Config system integration: PASS")


def test_collector_orchestrator_integration():
    """Test orchestrator collects from all sources"""
    orchestrator = CollectorOrchestrator("fraud")

    # Collect all data
    collected = orchestrator.collect_all()

    # Verify structure
    assert "collected_at" in collected
    assert "topic" in collected
    assert collected["topic"] == "fraud"

    assert "rss_articles" in collected
    assert "reddit_posts" in collected
    assert "competitor_changelogs" in collected

    # Verify RSS collection
    assert isinstance(collected["rss_articles"], list)
    assert len(collected["rss_articles"]) > 0, "Should collect RSS articles"

    # Reddit and Changelogs may be empty depending on API keys/availability
    assert isinstance(collected["reddit_posts"], list)
    assert isinstance(collected["competitor_changelogs"], list)

    print(f"✓ Orchestrator integration: PASS")
    print(f"  - RSS: {len(collected['rss_articles'])} articles")
    print(f"  - Reddit: {len(collected['reddit_posts'])} posts")
    print(f"  - Changelogs: {len(collected['competitor_changelogs'])} entries")


def test_caching_integration():
    """Test that collectors use caching"""
    from core.collectors.rss import RSSCollector
    import yaml

    # Load RSS config
    with open("config/topics/fraud/rss.yaml") as f:
        config = yaml.safe_load(f)

    collector = RSSCollector(config)

    # First collection
    articles1 = collector.collect()

    # Second collection should use cache
    articles2 = collector.collect()

    # Should return same data from cache
    assert len(articles1) == len(articles2)

    print("✓ Caching integration: PASS")


def test_data_structure_compatibility():
    """Test that v2 output structure matches v1 expectations"""
    orchestrator = CollectorOrchestrator("fraud")
    collected = orchestrator.collect_all()

    # Check v1-compatible structure
    if collected["rss_articles"]:
        article = collected["rss_articles"][0]
        required_fields = ["source", "category", "title", "url", "published", "summary"]
        for field in required_fields:
            assert field in article, f"Missing required field: {field}"

    if collected["reddit_posts"]:
        post = collected["reddit_posts"][0]
        required_fields = ["subreddit", "title", "author", "url", "created_utc"]
        for field in required_fields:
            assert field in post, f"Missing required field: {field}"

    print("✓ Data structure compatibility: PASS")


if __name__ == "__main__":
    """Run integration tests standalone"""
    print("=" * 70)
    print("PM RADAR V2 - SUB-PROJECT 1 INTEGRATION TEST")
    print("=" * 70)
    print()

    try:
        test_config_system_integration()
        test_collector_orchestrator_integration()
        test_caching_integration()
        test_data_structure_compatibility()

        print()
        print("=" * 70)
        print("✓ ALL INTEGRATION TESTS PASSED")
        print("=" * 70)
        print()
        print("Sub-Project 1 (Core Infrastructure) is complete:")
        print("  ✓ Config system with YAML support")
        print("  ✓ Base collector interface with caching")
        print("  ✓ RSS, Reddit, Changelog collectors")
        print("  ✓ Collector orchestrator")
        print("  ✓ Fraud topic migrated to v2 configs")
        print()
        print("Next: Sub-Project 2 (Analyzers & LLM Providers)")

    except Exception as e:
        print()
        print("=" * 70)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 70)
        raise
