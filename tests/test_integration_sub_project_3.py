"""Integration test for Sub-Project 3: Reporters & Section Library"""

from pathlib import Path
from core.collectors.orchestrator import CollectorOrchestrator
from core.analyzers.summarizer import ContentSummarizer
from core.reporters.report_generator import ReportGenerator


def test_full_pipeline_collect_analyze_report(tmp_path):
    """Test complete collect → analyze → report pipeline"""
    print("\n" + "=" * 70)
    print("SUB-PROJECT 3 INTEGRATION TEST: Collect → Analyze → Report")
    print("=" * 70)

    # Step 1: Collect data
    print("\n→ Step 1: Collecting data...")
    orchestrator = CollectorOrchestrator("fraud")
    collected = orchestrator.collect_all()

    articles_count = len(collected["rss_articles"])
    assert articles_count > 0, "Should collect RSS articles"
    print(f"  ✓ Collected {articles_count} articles")

    # Step 2: Analyze data
    print("\n→ Step 2: Analyzing data...")
    summarizer = ContentSummarizer("fraud")
    analysis = summarizer.analyze(collected)

    telecom_count = analysis["categorized_counts"]["telecom"]
    general_count = analysis["categorized_counts"]["general"]
    print(f"  ✓ Analyzed: telecom={telecom_count}, general={general_count}")

    # Step 3: Generate report
    print("\n→ Step 3: Generating report...")
    generator = ReportGenerator("fraud")
    output_path = tmp_path / "test_report.md"
    report = generator.generate(analysis, output_path=output_path)

    # Verify report was generated
    assert output_path.exists()
    assert len(report) > 1000, "Report should have substantial content"
    print(f"  ✓ Report generated: {len(report)} chars")

    # Step 4: Verify report structure
    print("\n→ Step 4: Verifying report structure...")

    assert "# Fraud & Security Intelligence" in report
    assert "## Executive Summary" in report
    assert "## 🔴 Top Threats" in report
    assert "## 🟡 General Security" in report
    assert "## Sources" in report

    # Verify citations
    assert "[A1]" in report, "Should have at least one citation"

    print("  ✓ Report structure valid")
    print(f"  ✓ Report sections present")

    # Step 5: Verify content quality
    print("\n→ Step 5: Verifying content quality...")

    # Should have actual content, not just placeholders
    if telecom_count > 0:
        assert "*No items identified*" not in report or telecom_count == 0
        print("  ✓ Telecom threats section has content")

    # Sources should list actual articles
    source_section = report.split("## Sources")[1] if "## Sources" in report else ""
    article_count_in_sources = source_section.count("[A")
    assert article_count_in_sources > 0, "Sources section should have citations"
    print(f"  ✓ Sources section has {article_count_in_sources} citations")

    print("\n" + "=" * 70)
    print("✓ INTEGRATION TEST PASSED")
    print("=" * 70)
    print("\nSub-Project 3 Complete:")
    print("  ✓ BaseSection interface")
    print("  ✓ Core section implementations (ExecutiveSummary, TopItems, Sources)")
    print("  ✓ ReportGenerator orchestrator")
    print("  ✓ Full collect → analyze → report pipeline working")
    print("\nNext: Sub-Project 4 (Integration & Migration)")


def test_report_matches_v1_structure():
    """Test v2 report structure matches v1 expectations"""
    print("\n" + "=" * 70)
    print("V1/V2 STRUCTURE COMPATIBILITY TEST")
    print("=" * 70)

    # Generate a quick report
    orchestrator = CollectorOrchestrator("fraud")
    collected = orchestrator.collect_all()

    summarizer = ContentSummarizer("fraud")
    analysis = summarizer.analyze(collected)

    generator = ReportGenerator("fraud")
    report = generator.generate(analysis)

    # V1 report has these sections - v2 should too
    v1_required_sections = [
        "# Fraud & Security Intelligence",
        "## Executive Summary",
        "## Sources"
    ]

    for section in v1_required_sections:
        assert section in report, f"Missing v1-compatible section: {section}"
        print(f"  ✓ Found: {section}")

    print("\n  ✓ V2 report structure matches v1 expectations")
    print("=" * 70)


if __name__ == "__main__":
    """Run integration test standalone"""
    import tempfile

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            test_full_pipeline_collect_analyze_report(tmp_path)

        test_report_matches_v1_structure()

        print("\n" + "=" * 70)
        print("✓ ALL SUB-PROJECT 3 INTEGRATION TESTS PASSED")
        print("=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 70)
        raise
