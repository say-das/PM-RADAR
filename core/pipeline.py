"""Topic Pipeline - Main orchestrator for PM Radar v2

Coordinates the full pipeline: collect → analyze → report → deliver
"""

from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any, Optional

from .config_loader import ConfigLoader
from .collectors.orchestrator import CollectorOrchestrator
from .analyzers.summarizer import ContentSummarizer
from .reporters.report_generator import ReportGenerator


class TopicPipeline:
    """Main pipeline orchestrator for a topic"""

    def __init__(self, topic_id: str):
        """Initialize pipeline for a topic

        Args:
            topic_id: Topic identifier (e.g., "fraud")
        """
        self.topic_id = topic_id
        self.config_loader = ConfigLoader()
        self.topic_config = self.config_loader.load_topic_config(topic_id)

        # Initialize components
        self.collector = CollectorOrchestrator(topic_id)
        self.analyzer = ContentSummarizer(topic_id)
        self.reporter = ReportGenerator(topic_id)

        # Output paths
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.raw_data_path = Path(f"data/raw/{self.date_str}.json")
        self.analysis_path = Path(f"data/raw/{self.date_str}-analysis.json")
        self.report_path = Path(f"data/reports/{self.date_str}.md")

    def run(
        self,
        skip_collection: bool = False,
        skip_analysis: bool = False,
        skip_report: bool = False,
        skip_delivery: bool = True
    ) -> Dict[str, Any]:
        """Run the complete pipeline

        Args:
            skip_collection: Skip collection phase (use existing raw data)
            skip_analysis: Skip analysis phase (use existing analysis)
            skip_report: Skip report generation
            skip_delivery: Skip email delivery (default True)

        Returns:
            Pipeline results dictionary with paths and stats
        """
        print("=" * 70)
        print(f"PM RADAR V2 PIPELINE: {self.topic_config.get('name', self.topic_id)}")
        print("=" * 70)
        print()

        results = {
            "topic_id": self.topic_id,
            "date": self.date_str,
            "phases": {},
            "outputs": {}
        }

        # Phase 1: Collection
        if skip_collection:
            print("→ Skipping collection (loading existing raw data)...")
            collected_data = self._load_raw_data()
        else:
            print("→ PHASE 1: DATA COLLECTION")
            print()
            collected_data = self.collector.collect_all()
            self._save_raw_data(collected_data)
            print()

        results["phases"]["collection"] = {
            "articles": len(collected_data.get("rss_articles", [])),
            "reddit_posts": len(collected_data.get("reddit_posts", [])),
            "changelogs": len(collected_data.get("competitor_changelogs", []))
        }
        results["outputs"]["raw_data"] = str(self.raw_data_path)

        # Phase 2: Analysis
        if skip_analysis:
            print("→ Skipping analysis (loading existing analysis)...")
            analysis_data = self._load_analysis()
        else:
            print("→ PHASE 2: CONTENT ANALYSIS")
            print()
            analysis_data = self.analyzer.analyze(collected_data)
            self._save_analysis(analysis_data)
            print()

        results["phases"]["analysis"] = {
            "telecom_items": analysis_data.get("categorized_counts", {}).get("telecom", 0),
            "general_items": analysis_data.get("categorized_counts", {}).get("general", 0)
        }
        results["outputs"]["analysis"] = str(self.analysis_path)

        # Phase 3: Report Generation
        if not skip_report:
            print("→ PHASE 3: REPORT GENERATION")
            print()
            report_content = self.reporter.generate(analysis_data, output_path=self.report_path)
            results["phases"]["report"] = {
                "length": len(report_content),
                "citations": report_content.count("[A")
            }
            results["outputs"]["report"] = str(self.report_path)
            print()

        # Phase 4: Delivery (Optional)
        if not skip_delivery:
            print("→ PHASE 4: DELIVERY")
            print()
            # Email delivery deferred to Task 2
            print("  ⚠ Email delivery not yet implemented")
            print()

        # Summary
        print("=" * 70)
        print("✓ PIPELINE COMPLETE")
        print("=" * 70)
        print()
        print("Outputs:")
        for key, path in results["outputs"].items():
            print(f"  • {key}: {path}")
        print()

        return results

    def _save_raw_data(self, data: Dict[str, Any]):
        """Save raw collected data to JSON"""
        self.raw_data_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.raw_data_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"  ✓ Saved raw data to {self.raw_data_path}")

    def _load_raw_data(self) -> Dict[str, Any]:
        """Load raw data from JSON"""
        if not self.raw_data_path.exists():
            raise FileNotFoundError(f"Raw data not found: {self.raw_data_path}")

        with open(self.raw_data_path) as f:
            return json.load(f)

    def _save_analysis(self, data: Dict[str, Any]):
        """Save analysis results to JSON"""
        self.analysis_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.analysis_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"  ✓ Saved analysis to {self.analysis_path}")

    def _load_analysis(self) -> Dict[str, Any]:
        """Load analysis from JSON"""
        if not self.analysis_path.exists():
            raise FileNotFoundError(f"Analysis not found: {self.analysis_path}")

        with open(self.analysis_path) as f:
            return json.load(f)
