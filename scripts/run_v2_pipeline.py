#!/usr/bin/env python3
"""
PM Radar v2 - Pipeline Runner

Command-line interface for running the v2 pipeline.
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pipeline import TopicPipeline


def main():
    parser = argparse.ArgumentParser(
        description="PM Radar v2 - Intelligence Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline for fraud topic
  python scripts/run_v2_pipeline.py fraud

  # Skip collection (use existing data)
  python scripts/run_v2_pipeline.py fraud --skip-collection

  # Only generate report (skip collection and analysis)
  python scripts/run_v2_pipeline.py fraud --skip-collection --skip-analysis

  # Include email delivery
  python scripts/run_v2_pipeline.py fraud --deliver
        """
    )

    parser.add_argument(
        "topic",
        help="Topic ID to process (e.g., 'fraud')"
    )

    parser.add_argument(
        "--skip-collection",
        action="store_true",
        help="Skip data collection (use existing raw data)"
    )

    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip analysis (use existing analysis)"
    )

    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="Skip report generation"
    )

    parser.add_argument(
        "--deliver",
        action="store_true",
        help="Enable email delivery (disabled by default)"
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    try:
        # Initialize pipeline
        pipeline = TopicPipeline(args.topic)

        # Run pipeline
        results = pipeline.run(
            skip_collection=args.skip_collection,
            skip_analysis=args.skip_analysis,
            skip_report=args.skip_report,
            skip_delivery=not args.deliver
        )

        # Success
        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        print("\nTip: Run without --skip flags to generate missing files.", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
