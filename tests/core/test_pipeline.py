import pytest
from pathlib import Path
from core.pipeline import TopicPipeline


def test_pipeline_initializes():
    """Test TopicPipeline initializes correctly"""
    pipeline = TopicPipeline("fraud")

    assert pipeline.topic_id == "fraud"
    assert pipeline.collector is not None
    assert pipeline.analyzer is not None
    assert pipeline.reporter is not None


def test_pipeline_run_creates_outputs(tmp_path):
    """Test pipeline creates all output files"""
    # Note: This is a full integration test that makes real API calls
    # It will take ~2 minutes to complete

    pipeline = TopicPipeline("fraud")

    # Override output paths to use tmp directory
    pipeline.raw_data_path = tmp_path / "raw_data.json"
    pipeline.analysis_path = tmp_path / "analysis.json"
    pipeline.report_path = tmp_path / "report.md"

    # Run pipeline (skip delivery)
    results = pipeline.run(skip_delivery=True)

    # Verify outputs were created
    assert pipeline.raw_data_path.exists()
    assert pipeline.analysis_path.exists()
    assert pipeline.report_path.exists()

    # Verify results structure
    assert "phases" in results
    assert "collection" in results["phases"]
    assert "analysis" in results["phases"]
    assert "report" in results["phases"]

    # Verify content
    assert results["phases"]["collection"]["articles"] > 0
    assert results["phases"]["report"]["length"] > 1000

    print(f"\n✓ Pipeline created all outputs:")
    print(f"  - Raw data: {results['phases']['collection']['articles']} articles")
    print(f"  - Analysis: {results['phases']['analysis']['telecom_items']} telecom items")
    print(f"  - Report: {results['phases']['report']['length']} chars")


def test_pipeline_skip_collection_loads_existing():
    """Test pipeline can skip collection and load existing data"""
    pipeline = TopicPipeline("fraud")

    # This test requires existing data from a previous run
    # If the file doesn't exist, skip the test

    if not pipeline.raw_data_path.exists():
        pytest.skip("No existing raw data to test skip_collection")

    # Should load existing data without error
    results = pipeline.run(skip_collection=True, skip_report=True, skip_delivery=True)

    assert "collection" in results["phases"]
    assert results["phases"]["collection"]["articles"] > 0
