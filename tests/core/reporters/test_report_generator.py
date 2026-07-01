import pytest
from pathlib import Path
from core.reporters.report_generator import ReportGenerator


def test_report_generator_initializes():
    """Test ReportGenerator initializes correctly"""
    generator = ReportGenerator("fraud")

    assert generator.topic_id == "fraud"
    assert generator.topic_config is not None
    assert generator.global_config is not None


def test_report_generator_generates_report():
    """Test report generation with sample data"""
    generator = ReportGenerator("fraud")

    # Sample analysis data
    analysis_data = {
        "analyzed_at": "2026-07-01T00:00:00",
        "telecom_fraud_summary": '{"executive_summary": "Test summary of fraud landscape."}',
        "categorized_counts": {"telecom": 5, "general": 3},
        "filtered_articles": [
            {
                "source": "Test Source",
                "title": "Test Article",
                "url": "https://example.com/test",
                "published": "2026-07-01T00:00:00"
            }
        ]
    }

    report = generator.generate(analysis_data)

    # Verify report structure
    assert "# Fraud & Security Intelligence" in report
    assert "## Executive Summary" in report
    assert "## Sources" in report
    assert "Test summary" in report


def test_report_generator_saves_to_file(tmp_path):
    """Test report saves to file"""
    generator = ReportGenerator("fraud")

    analysis_data = {
        "telecom_fraud_summary": "Test content",
        "filtered_articles": []
    }

    output_path = tmp_path / "test_report.md"
    report = generator.generate(analysis_data, output_path=output_path)

    # Verify file was created
    assert output_path.exists()

    # Verify content matches
    with open(output_path) as f:
        saved_content = f.read()

    assert saved_content == report


def test_report_generator_handles_section_errors():
    """Test report generator handles section rendering errors gracefully"""
    generator = ReportGenerator("fraud")

    # Malformed data that might cause section errors
    analysis_data = {
        "telecom_fraud_summary": None,  # Might cause issues
        "filtered_articles": None
    }

    # Should not raise exception
    report = generator.generate(analysis_data)

    # Should still have basic structure
    assert "# Fraud & Security Intelligence" in report
