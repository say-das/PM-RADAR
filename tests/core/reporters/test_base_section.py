import pytest
from core.reporters.base_section import BaseSection


class MockSection(BaseSection):
    """Test implementation of BaseSection"""

    def render(self):
        return "## Mock Section\nTest content"


def test_base_section_initializes():
    """Test BaseSection initializes with config and data"""
    config = {"title": "Test"}
    data = {"key": "value"}

    section = MockSection(config, data)

    assert section.config == config
    assert section.analysis_data == data


def test_base_section_format_citation():
    """Test citation formatting"""
    section = MockSection()

    assert section.format_citation(1) == "[A1]"
    assert section.format_citation(42) == "[A42]"


def test_base_section_truncate():
    """Test text truncation"""
    section = MockSection()

    text = "This is a long piece of text"
    assert section.truncate(text, 10) == "This is..."
    assert section.truncate(text, 100) == text  # No truncation


def test_base_section_extract_citations():
    """Test citation extraction from text"""
    section = MockSection()

    text = "Some text with [A1] and [A5] citations [A12]"
    citations = section.extract_citations(text)

    assert citations == [1, 5, 12]


def test_base_section_requires_render():
    """Test BaseSection enforces render() method"""

    class IncompleteSection(BaseSection):
        pass

    with pytest.raises(TypeError):
        section = IncompleteSection()


def test_mock_section_renders():
    """Test mock section renders markdown"""
    section = MockSection()
    output = section.render()

    assert "## Mock Section" in output
    assert isinstance(output, str)
