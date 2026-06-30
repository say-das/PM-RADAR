#!/usr/bin/env python3
"""
Quick verification script for PM Radar v2 Core Infrastructure
Run this to verify v2 collectors are working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.collectors.orchestrator import CollectorOrchestrator
from dotenv import load_dotenv

def main():
    print("=" * 70)
    print("PM RADAR V2 - VERIFICATION TEST")
    print("=" * 70)
    print()

    # Load environment variables
    load_dotenv()

    print("→ Initializing v2 orchestrator for 'fraud' topic...")
    orchestrator = CollectorOrchestrator("fraud")
    print("  ✓ Orchestrator initialized")
    print()

    print("→ Collecting data from all sources...")
    print()
    collected = orchestrator.collect_all()
    print()

    print("=" * 70)
    print("COLLECTION RESULTS")
    print("=" * 70)
    print()
    print(f"✓ RSS Articles:        {len(collected['rss_articles']):>4} collected")
    print(f"✓ Reddit Posts:        {len(collected['reddit_posts']):>4} collected")
    print(f"✓ Changelog Entries:   {len(collected['competitor_changelogs']):>4} collected")
    print()

    if collected['rss_articles']:
        print("Sample RSS Article:")
        article = collected['rss_articles'][0]
        print(f"  Source:   {article['source']}")
        print(f"  Category: {article['category']}")
        print(f"  Title:    {article['title'][:70]}...")
        print()

    if collected['reddit_posts']:
        print("Sample Reddit Post:")
        post = collected['reddit_posts'][0]
        print(f"  Subreddit: r/{post['subreddit']}")
        print(f"  Title:     {post['title'][:70]}...")
        print()

    print("=" * 70)
    print("✓ V2 CORE INFRASTRUCTURE WORKING")
    print("=" * 70)
    print()
    print("Ready for Sub-Project 2: Analyzers & LLM Providers")
    print()

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print()
        print("=" * 70)
        print(f"✗ ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
