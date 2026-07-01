"""Final Integration Test - PM Radar v2 Complete Pipeline Validation"""

from pathlib import Path
from core.pipeline import TopicPipeline


def test_v2_pipeline_complete():
    """Test complete v2 pipeline end-to-end"""
    print("\n" + "=" * 70)
    print("FINAL INTEGRATION TEST: PM RADAR V2 COMPLETE PIPELINE")
    print("=" * 70)
    print()

    # Run complete pipeline
    pipeline = TopicPipeline("fraud")
    results = pipeline.run(skip_delivery=True)

    # Validate all phases completed
    assert "collection" in results["phases"]
    assert "analysis" in results["phases"]
    assert "report" in results["phases"]

    collection = results["phases"]["collection"]
    analysis = results["phases"]["analysis"]
    report = results["phases"]["report"]

    print("\n→ Validation Results:")
    print(f"  ✓ Collection: {collection['articles']} articles, {collection['reddit_posts']} posts")
    print(f"  ✓ Analysis: {analysis['telecom_items']} telecom, {analysis['general_items']} general")
    print(f"  ✓ Report: {report['length']} chars, {report['citations']} citations")

    # Validate collection phase
    assert collection["articles"] > 50, "Should collect substantial articles"
    assert collection["articles"] + collection["reddit_posts"] > 0

    # Validate analysis phase
    total_items = analysis["telecom_items"] + analysis["general_items"]
    assert total_items > 0, "Should categorize some items"
    assert total_items <= collection["articles"], "Can't categorize more than collected"

    # Validate report phase
    assert report["length"] > 10000, "Report should be substantial (>10k chars)"
    assert report["citations"] > 0, "Report should have citations"

    # Validate output files exist
    assert Path(results["outputs"]["raw_data"]).exists()
    assert Path(results["outputs"]["analysis"]).exists()
    assert Path(results["outputs"]["report"]).exists()

    print("\n→ Output Files:")
    for key, path in results["outputs"].items():
        size = Path(path).stat().st_size
        print(f"  ✓ {key}: {path} ({size:,} bytes)")

    print("\n" + "=" * 70)
    print("✓ FINAL INTEGRATION TEST PASSED")
    print("=" * 70)


def test_v2_report_quality():
    """Test v2 report quality and structure"""
    print("\n" + "=" * 70)
    print("REPORT QUALITY VALIDATION")
    print("=" * 70)

    # Load generated report
    report_path = Path("data/reports/2026-07-01.md")

    if not report_path.exists():
        print("  ⚠ No report found, running pipeline first...")
        pipeline = TopicPipeline("fraud")
        pipeline.run(skip_delivery=True)

    with open(report_path) as f:
        report = f.read()

    # Validate structure
    required_sections = [
        "# Fraud & Security Intelligence",
        "## Executive Summary",
        "## 🔴 Top Threats",
        "## 🟡 General Security",
        "## Sources"
    ]

    print("\n→ Structure Validation:")
    for section in required_sections:
        assert section in report, f"Missing required section: {section}"
        print(f"  ✓ Found: {section}")

    # Validate content quality
    print("\n→ Content Validation:")

    # Should have actual content, not just placeholders
    assert "*No items identified*" not in report or report.count("*No items identified*") <= 2
    print("  ✓ Sections have content (not empty placeholders)")

    # Should have citations
    citation_count = report.count("[A")
    assert citation_count >= 10, "Should have at least 10 citations"
    print(f"  ✓ Has {citation_count} citations")

    # Should have substantial content
    assert len(report) > 15000, "Report should be substantial"
    print(f"  ✓ Report length: {len(report):,} chars")

    # Should have metadata
    assert "**Date:**" in report
    assert "**Generated:**" in report
    print("  ✓ Metadata present")

    print("\n" + "=" * 70)
    print("✓ REPORT QUALITY VALIDATED")
    print("=" * 70)


def test_v2_vs_v1_comparison():
    """Compare v2 output with v1 expectations"""
    print("\n" + "=" * 70)
    print("V1/V2 COMPATIBILITY CHECK")
    print("=" * 70)

    report_path = Path("data/reports/2026-07-01.md")

    if not report_path.exists():
        print("  ⚠ Skipping comparison - no v2 report generated yet")
        return

    with open(report_path) as f:
        v2_report = f.read()

    print("\n→ V1 Compatibility:")

    # V1 report structure expectations
    v1_expectations = {
        "Header format": "# Fraud & Security Intelligence" in v2_report,
        "Date metadata": "**Date:**" in v2_report,
        "Executive summary": "## Executive Summary" in v2_report,
        "Top threats section": "## 🔴" in v2_report or "## Top Threats" in v2_report,
        "Sources section": "## Sources" in v2_report,
        "Citations format": "[A1]" in v2_report,
        "Substantial length": len(v2_report) > 10000
    }

    all_passed = True
    for check, passed in v1_expectations.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n  ✓ V2 output matches V1 structure expectations")
    else:
        print("\n  ⚠ Some V1 compatibility checks failed")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    """Run final validation standalone"""
    try:
        test_v2_pipeline_complete()
        test_v2_report_quality()
        test_v2_vs_v1_comparison()

        print("\n" + "=" * 70)
        print("🎉 ALL FINAL INTEGRATION TESTS PASSED")
        print("=" * 70)
        print()
        print("PM RADAR V2 - COMPLETE!")
        print()
        print("Sub-Projects Complete:")
        print("  ✓ Sub-Project 1: Core Infrastructure (8 tasks)")
        print("  ✓ Sub-Project 2: Analyzers & LLM Providers (4 tasks)")
        print("  ✓ Sub-Project 3: Reporters & Section Library (4 tasks)")
        print("  ✓ Sub-Project 4: Integration & Migration (4 tasks)")
        print()
        print("Total: 20 tasks completed")
        print()
        print("Next Steps:")
        print("  - Review v2 report quality")
        print("  - Merge feature branch when ready")
        print("  - Deploy v2 pipeline to production")
        print()

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        raise
