"""Report Health Check - Validate generated reports for quality issues"""

import re
from typing import Dict, Any, List


class ReportHealthCheck:
    """Validates generated reports and detects potential issues"""

    # Minimum expected report length (chars)
    MIN_REPORT_LENGTH = 500

    # Required sections that should always be present
    REQUIRED_SECTIONS = [
        "Executive Summary",
        "Sources"
    ]

    def __init__(self, report: str, analysis_data: Dict[str, Any]):
        """
        Initialize health checker.

        Args:
            report: Generated markdown report
            analysis_data: Analysis data used to generate report
        """
        self.report = report
        self.analysis_data = analysis_data
        self.health = {
            "status": "ok",
            "warnings": [],
            "errors": [],
            "metrics": {}
        }

    def run_checks(self) -> Dict[str, Any]:
        """
        Run all health checks on the report.

        Returns:
            Health status dict with status, warnings, errors, metrics
        """
        self._check_length()
        self._check_sections()
        self._check_error_markers()
        self._check_citation_consistency()
        self._check_empty_sections()
        self._collect_metrics()

        # Set overall status
        if self.health["errors"]:
            self.health["status"] = "error"
        elif self.health["warnings"]:
            self.health["status"] = "warning"
        else:
            self.health["status"] = "ok"

        return self.health

    def _check_length(self):
        """Check if report meets minimum length threshold"""
        length = len(self.report)
        if length < self.MIN_REPORT_LENGTH:
            self.health["warnings"].append(
                f"Report is suspiciously short ({length} chars, expected >{self.MIN_REPORT_LENGTH})"
            )

    def _check_sections(self):
        """Verify required sections are present"""
        for section in self.REQUIRED_SECTIONS:
            if f"## {section}" not in self.report:
                self.health["errors"].append(f"Missing required section: {section}")

    def _check_error_markers(self):
        """Check for error messages in the report content"""
        error_markers = [
            "*Error rendering",
            "*No analysis available",
            "Error rendering section"
        ]

        for marker in error_markers:
            if marker in self.report:
                self.health["errors"].append(f"Report contains error marker: '{marker}'")

    def _check_citation_consistency(self):
        """Verify citations don't exceed available articles"""
        # Extract all article citation IDs from report
        article_citations = set()

        # Pattern: [\[A#\]](#a#)
        matches = re.findall(r'\[\\\[A(\d+)\\\]\]\(#a\d+\)', self.report)
        article_citations.update(int(m) for m in matches)

        # Also check simple [A#] format (shouldn't appear in final report, but check anyway)
        matches = re.findall(r'(?<!\[)\[A(\d+)\](?!\()', self.report)
        article_citations.update(int(m) for m in matches)

        article_count = len(self.analysis_data.get("filtered_articles", []))
        citation_count = len(article_citations)

        if citation_count > 0:
            max_citation = max(article_citations) if article_citations else 0

            if max_citation > article_count:
                self.health["errors"].append(
                    f"Citation ID {max_citation} exceeds article count ({article_count})"
                )

    def _check_empty_sections(self):
        """Warn if sections appear to be empty"""
        # Pattern: ## Section Title\n\n*No items identified*
        empty_pattern = r'## .+?\n\n\*No (items|sources|data|analysis)'

        matches = re.findall(empty_pattern, self.report)
        if matches:
            self.health["warnings"].append(
                f"Report contains {len(matches)} empty section(s)"
            )

    def _collect_metrics(self):
        """Collect report metrics for monitoring"""
        # Basic length
        self.health["metrics"]["length"] = len(self.report)

        # Section count
        section_count = self.report.count("\n## ")
        self.health["metrics"]["section_count"] = section_count

        # Citation counts
        article_citations = len(re.findall(r'\[\\\[A\d+\\\]\]', self.report))
        reddit_citations = len(re.findall(r'\[\\\[R\d+\\\]\]', self.report))
        comp_citations = len(re.findall(r'\[\\\[C\d+\\\]\]', self.report))

        self.health["metrics"]["article_citations"] = article_citations
        self.health["metrics"]["reddit_citations"] = reddit_citations
        self.health["metrics"]["competitor_citations"] = comp_citations

        # Article count
        article_count = len(self.analysis_data.get("filtered_articles", []))
        self.health["metrics"]["total_articles"] = article_count

        # Threat counts from analysis
        counts = self.analysis_data.get("categorized_counts", {})
        self.health["metrics"]["telecom_threats"] = counts.get("telecom", 0)
        self.health["metrics"]["general_threats"] = counts.get("general", 0)
        self.health["metrics"]["competitive_items"] = counts.get("competitive", 0)


def check_report_health(report: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to run health checks on a report.

    Args:
        report: Generated markdown report
        analysis_data: Analysis data used to generate report

    Returns:
        Health status dict

    Example:
        >>> health = check_report_health(report, analysis_data)
        >>> if health["status"] == "error":
        >>>     print("Report has errors:", health["errors"])
    """
    checker = ReportHealthCheck(report, analysis_data)
    return checker.run_checks()
