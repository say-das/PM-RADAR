"""Report Generator - Assembles reports from sections"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from ..config_loader import ConfigLoader
from .sections import ExecutiveSummarySection, TopItemsSection, SourcesSection, RedditCommunitySection, CompetitiveIntelSection
from .health_check import check_report_health


class ReportGenerator:
    """Generates reports from analysis data"""

    # Section type registry
    SECTION_TYPES = {
        "executive_summary": ExecutiveSummarySection,
        "top_items": TopItemsSection,
        "sources": SourcesSection,
        "reddit_community": RedditCommunitySection,
        "competitive_intel": CompetitiveIntelSection
    }

    def __init__(self, topic_id: str):
        """Initialize report generator

        Args:
            topic_id: Topic identifier (e.g., "fraud")
        """
        self.topic_id = topic_id
        self.config_loader = ConfigLoader()
        self.topic_config = self.config_loader.load_topic_config(topic_id)
        self.global_config = self.config_loader.load_global_config()

    def generate(self, analysis_data: Dict[str, Any], output_path: Path = None) -> str:
        """Generate report from analysis data

        Args:
            analysis_data: Analysis results from ContentSummarizer
            output_path: Optional path to save report (defaults to data/reports/{date}.md)

        Returns:
            Report markdown string
        """
        print("→ Generating report...")

        # Build report sections
        sections = []

        # Header
        sections.append(self._generate_header())

        # Generate each configured section (first pass - without sources)
        section_configs = self.topic_config.get("report", {}).get("sections", [])

        for section_config in section_configs:
            section_type = section_config.get("type")
            section_config_data = section_config.get("config", {})

            # Skip sources section in first pass
            if section_type == "sources":
                continue

            if section_type in self.SECTION_TYPES:
                section_class = self.SECTION_TYPES[section_type]
                section = section_class(config=section_config_data, analysis_data=analysis_data)

                try:
                    section_markdown = section.render()
                    sections.append(section_markdown)
                    print(f"  ✓ Rendered: {section_type}")
                except Exception as e:
                    print(f"  ✗ Error rendering {section_type}: {e}")
                    sections.append(f"## {section_type}\n\n*Error rendering section*\n")

            else:
                print(f"  ⚠ Unknown section type: {section_type}")

        # Assemble report content (without sources)
        report_content = "\n".join(sections)

        # Post-process: Convert citation formats (BEFORE extracting citations for sources)
        report_content = self._convert_citations(report_content)

        # Now render sources section with full report content for citation extraction
        sources_section = ""
        for section_config in section_configs:
            section_type = section_config.get("type")
            if section_type == "sources":
                section_config_data = section_config.get("config", {})
                section_config_data["_report_content"] = report_content  # Pass converted content

                section_class = self.SECTION_TYPES["sources"]
                section = section_class(config=section_config_data, analysis_data=analysis_data)

                try:
                    sources_section = section.render()
                    print(f"  ✓ Rendered: sources (filtered to cited only)")
                except Exception as e:
                    print(f"  ✗ Error rendering sources: {e}")
                    sources_section = f"## Sources\n\n*Error rendering section*\n"

        # Assemble full report (converted content + sources)
        report = report_content + "\n" + sources_section

        # Run health checks on generated report
        print("→ Running health checks...")
        health = check_report_health(report, analysis_data)

        # Log health status
        if health["status"] == "error":
            print(f"  ✗ Health check FAILED:")
            for error in health["errors"]:
                print(f"    • {error}")
        elif health["status"] == "warning":
            print(f"  ⚠️  Health check passed with warnings:")
            for warning in health["warnings"]:
                print(f"    • {warning}")
        else:
            print(f"  ✓ Health check passed")

        # Log metrics
        metrics = health["metrics"]
        print(f"  📊 Metrics: {metrics.get('length', 0)} chars, "
              f"{metrics.get('section_count', 0)} sections, "
              f"{metrics.get('article_citations', 0)} citations")

        # Save if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                f.write(report)

            print(f"  ✓ Report saved to {output_path}")

        return report

    def _generate_header(self) -> str:
        """Generate report header

        Returns:
            Markdown header string
        """
        topic_name = self.topic_config.get("name", "Intelligence Digest")
        today = datetime.now().strftime("%Y-%m-%d")

        header = f"""# {topic_name} - Weekly Report
**Date:** {today}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

---

"""
        return header

    def _convert_citations(self, report: str) -> str:
        """Convert citation formats from [ARTICLE_1] to [\[A1\]](#a1)

        Args:
            report: Report markdown string

        Returns:
            Report with converted citations
        """
        import re

        # Expand comma-separated citations: [ARTICLE_1, ARTICLE_2] -> [ARTICLE_1][ARTICLE_2]
        def expand_comma_citations(match):
            content = match.group(1)
            citations = [c.strip() for c in content.split(',')]
            return ''.join(f'[{c}]' for c in citations)

        report = re.sub(
            r'\[((?:REDDIT|ARTICLE|COMP)_\d+(?:,\s*(?:REDDIT|ARTICLE|COMP)_\d+)+)\]',
            expand_comma_citations,
            report
        )

        # Convert to anchor link format
        report = re.sub(r'\[ARTICLE_(\d+)\]', r'[\[A\1\]](#a\1)', report)
        report = re.sub(r'\[REDDIT_(\d+)\]', r'[\[R\1\]](#r\1)', report)
        report = re.sub(r'\[COMP_(\d+)\]', r'[\[C\1\]](#c\1)', report)

        # Clean up extra commas/spaces between adjacent citations
        report = re.sub(r'(\]\(\#[arc]\d+\)),\s*\[', r'\1[', report)

        return report

    def get_default_output_path(self) -> Path:
        """Get default output path for report

        Returns:
            Path to save report (data/reports/{date}.md)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return Path(f"data/reports/{today}.md")
