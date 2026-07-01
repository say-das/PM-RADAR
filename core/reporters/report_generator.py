"""Report Generator - Assembles reports from sections"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from ..config_loader import ConfigLoader
from .sections import ExecutiveSummarySection, TopItemsSection, SourcesSection


class ReportGenerator:
    """Generates reports from analysis data"""

    # Section type registry
    SECTION_TYPES = {
        "executive_summary": ExecutiveSummarySection,
        "top_items": TopItemsSection,
        "sources": SourcesSection
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

        # Generate each configured section
        section_configs = self.topic_config.get("report", {}).get("sections", [])

        for section_config in section_configs:
            section_type = section_config.get("type")
            section_config_data = section_config.get("config", {})

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

        # Assemble full report
        report = "\n".join(sections)

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

    def get_default_output_path(self) -> Path:
        """Get default output path for report

        Returns:
            Path to save report (data/reports/{date}.md)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return Path(f"data/reports/{today}.md")
