import pytest
from core.collectors.base import BaseCollector


class MockCollector(BaseCollector):
    """Test implementation of BaseCollector"""

    def collect(self):
        return [{"id": "1", "content": "test"}]


def test_base_collector_requires_collect_implementation():
    """Test that BaseCollector enforces collect() method"""

    class IncompleteCollector(BaseCollector):
        pass

    with pytest.raises(TypeError):
        collector = IncompleteCollector({})


def test_base_collector_can_be_instantiated_with_config():
    """Test BaseCollector accepts config dict"""
    config = {"api_key": "test", "limit": 10}
    collector = MockCollector(config)

    assert collector.config == config
    assert collector.config["limit"] == 10


def test_collect_returns_list():
    """Test collect() returns list"""
    collector = MockCollector({})
    result = collector.collect()

    assert isinstance(result, list)
    assert len(result) == 1
