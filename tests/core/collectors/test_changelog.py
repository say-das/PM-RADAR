import pytest
from core.collectors.changelog import ChangelogCollector


def test_changelog_collector_loads_config():
    """Test changelog collector loads YAML config"""
    config = {
        "competitors": [
            {
                "id": "test",
                "name": "Test Competitor",
                "urls": []
            }
        ]
    }

    collector = ChangelogCollector(config)
    assert len(collector.config["competitors"]) == 1


def test_changelog_collector_collect_returns_list():
    """Test collect returns list (stub implementation)"""
    config = {"competitors": []}

    collector = ChangelogCollector(config)
    result = collector.collect()

    assert isinstance(result, list)
