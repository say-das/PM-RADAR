#!/usr/bin/env python3
"""
Report Validation Script
Checks all sections of generated report for errors before publishing.
"""

import sys
from pathlib import Path

def validate_report(report_path):
    """Validate report has no parsing errors and all expected sections"""

    with open(report_path) as f:
        content = f.read()

    errors = []
    warnings = []

    # Check for parsing errors
    if "Analysis Error:" in content:
        error_count = content.count("Analysis Error:")
        errors.append(f"Found {error_count} 'Analysis Error' message(s)")

    if "Unable to parse" in content:
        errors.append("Found 'Unable to parse' error message")

    # Check for expected sections
    required_sections = [
        "## Executive Summary",
        "## Telecom Fraud Digest",
        "## General Fraud & Security Digest",
        "## Competition Watch",
        "## Sources"
    ]

    for section in required_sections:
        if section not in content:
            errors.append(f"Missing required section: {section}")

    # Check for optional sections (warnings only)
    optional_sections = [
        "## Twilio Community Discussions"
    ]

    for section in optional_sections:
        if section not in content:
            warnings.append(f"Optional section not present: {section}")

    # Check for empty sections
    if "**Top Threats & Trends:**\n\n---" in content:
        errors.append("Telecom Fraud section has no content")

    if "**Top Threats & Trends:**\n\n**Regulatory" in content:
        # Empty top trends
        warnings.append("Some sections may have empty content")

    # Print results
    print("=" * 70)
    print(f"REPORT VALIDATION: {report_path}")
    print("=" * 70)

    if not errors and not warnings:
        print("\n✓ ALL CHECKS PASSED - Report is valid")
        return True

    if errors:
        print(f"\n✗ ERRORS FOUND: {len(errors)}")
        for err in errors:
            print(f"  ✗ {err}")

    if warnings:
        print(f"\n⚠ WARNINGS: {len(warnings)}")
        for warn in warnings:
            print(f"  ⚠ {warn}")

    return len(errors) == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate_report.py data/reports/YYYY-MM-DD.md")
        sys.exit(1)

    report_file = sys.argv[1]

    if not Path(report_file).exists():
        print(f"✗ Report file not found: {report_file}")
        sys.exit(1)

    valid = validate_report(report_file)
    sys.exit(0 if valid else 1)
