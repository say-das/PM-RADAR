import pytest
from core.reporters.sections import ExecutiveSummarySection, TopItemsSection, SourcesSection


def test_executive_summary_renders():
    """Test executive summary section renders"""
    analysis_data = {
        "telecom_fraud_summary": '{"executive_summary": "This is a test summary of the fraud landscape."}'
    }

    section = ExecutiveSummarySection(analysis_data=analysis_data)
    output = section.render()

    assert "## Executive Summary" in output
    assert "test summary" in output


def test_executive_summary_handles_plain_text():
    """Test executive summary handles non-JSON text"""
    analysis_data = {
        "telecom_fraud_summary": "This is a plain text summary without JSON."
    }

    section = ExecutiveSummarySection(analysis_data=analysis_data)
    output = section.render()

    assert "## Executive Summary" in output
    assert "plain text summary" in output


def test_top_items_section_renders():
    """Test top items section renders"""
    config = {
        "title": "🔴 Top Threats",
        "category": "telecom_fraud",
        "limit": 3
    }

    analysis_data = {
        "telecom_fraud_summary": '''
        {
            "top_threats": [
                {
                    "title": "SMS Phishing Campaign",
                    "description": "Widespread SMS phishing targeting banks.",
                    "citation_ids": [1, 2]
                },
                {
                    "title": "SIM Swap Attacks",
                    "description": "Increasing SIM swap fraud incidents.",
                    "citation_ids": [3]
                }
            ]
        }
        '''
    }

    section = TopItemsSection(config=config, analysis_data=analysis_data)
    output = section.render()

    assert "## 🔴 Top Threats" in output
    assert "SMS Phishing Campaign" in output
    assert "SIM Swap Attacks" in output
    assert "[A1]" in output
    assert "[A3]" in output


def test_sources_section_renders():
    """Test sources section renders citations"""
    analysis_data = {
        "filtered_articles": [
            {
                "source": "Security News",
                "title": "Major breach disclosed",
                "url": "https://example.com/article1",
                "published": "2026-07-01T00:00:00"
            },
            {
                "source": "Tech Blog",
                "title": "New phishing technique found",
                "url": "https://example.com/article2",
                "published": "2026-06-30T00:00:00"
            }
        ]
    }

    section = SourcesSection(analysis_data=analysis_data)
    output = section.render()

    assert "## Sources" in output
    assert "[A1]" in output
    assert "[A2]" in output
    assert "Security News" in output
    assert "Major breach disclosed" in output
    assert "https://example.com/article1" in output


def test_sections_handle_empty_data():
    """Test sections handle empty/missing data gracefully"""
    empty_data = {}

    exec_section = ExecutiveSummarySection(analysis_data=empty_data)
    assert "No analysis available" in exec_section.render()

    top_section = TopItemsSection(config={"title": "Test", "category": "test"}, analysis_data=empty_data)
    assert "No items identified" in top_section.render()

    sources_section = SourcesSection(analysis_data=empty_data)
    assert "No sources cited" in sources_section.render()
