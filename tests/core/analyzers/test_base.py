import pytest
from core.analyzers.base import BaseAnalyzer
from core.analyzers.llm_providers import OpenAIProvider


class MockAnalyzer(BaseAnalyzer):
    """Test implementation of BaseAnalyzer"""

    def analyze(self, collected_data):
        return {"status": "analyzed"}


def test_base_analyzer_loads_config():
    """Test BaseAnalyzer loads topic configuration"""
    analyzer = MockAnalyzer("fraud")

    assert analyzer.topic_id == "fraud"
    assert analyzer.topic_config["id"] == "fraud"


def test_base_analyzer_loads_prompts():
    """Test BaseAnalyzer loads prompts from YAML"""
    analyzer = MockAnalyzer("fraud")

    assert "categorization" in analyzer.prompts
    assert "analysis" in analyzer.prompts
    assert "executive_summary" in analyzer.prompts


def test_base_analyzer_initializes_llm_provider():
    """Test BaseAnalyzer initializes correct LLM provider"""
    analyzer = MockAnalyzer("fraud")

    # Fraud topic uses OpenAI
    assert isinstance(analyzer.llm_provider, OpenAIProvider)
    assert analyzer.llm_provider.model == "gpt-4o"


def test_base_analyzer_requires_analyze_implementation():
    """Test BaseAnalyzer enforces analyze() method"""

    class IncompleteAnalyzer(BaseAnalyzer):
        pass

    with pytest.raises(TypeError):
        analyzer = IncompleteAnalyzer("fraud")
