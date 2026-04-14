"""
RSS Feed Collector
Fetches and parses RSS feeds from configured sources.
"""

import json
import feedparser
import requests
from datetime import datetime, timedelta
from pathlib import Path


class RSSCollector:
    def __init__(self, config_path="config/rss-sources.json"):
        """Initialize RSS collector with configuration."""
        with open(config_path) as f:
            self.config = json.load(f)
        self.sources = self.config["sources"]

    def collect(self, days_back=7):
        """
        Collect articles from all RSS sources.

        Args:
            days_back: Only collect articles from last N days (default: 7)

        Returns:
            List of article dictionaries
        """
        articles = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        print(f"Collecting RSS feeds (last {days_back} days)...")

        for source in self.sources:
            try:
                print(f"  → {source['name']}...", end=" ")

                # Fetch with requests first (better SSL handling)
                response = requests.get(
                    source["url"],
                    timeout=10,
                    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'},
                    verify=False  # Disable SSL verification for now
                )
                response.raise_for_status()

                # Parse the fetched content
                feed = feedparser.parse(response.content)

                if feed.bozo and feed.bozo_exception:
                    # Still try to use the feed if it has entries
                    if not feed.entries:
                        print(f"✗ Parse error: {feed.bozo_exception}")
                        continue

                source_articles = 0

                for entry in feed.entries:
                    # Parse publication date
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        # No date available, skip
                        continue

                    # Only include articles from last N days
                    if pub_date < cutoff_date:
                        continue

                    # Extract summary/description
                    summary = ""
                    if hasattr(entry, 'summary'):
                        summary = entry.summary
                    elif hasattr(entry, 'description'):
                        summary = entry.description

                    # Clean HTML tags from summary (basic cleaning)
                    summary = self._clean_html(summary)

                    articles.append({
                        "source": source["name"],
                        "category": source["category"],
                        "title": entry.title,
                        "url": entry.link,
                        "published": pub_date.isoformat(),
                        "summary": summary[:500]  # Limit to 500 chars
                    })

                    source_articles += 1

                print(f"✓ {source_articles} articles")

            except Exception as e:
                print(f"✗ Error: {e}")
                continue

        print(f"\nTotal collected: {len(articles)} articles")
        return articles

    def _clean_html(self, text):
        """Remove HTML tags from text (basic cleaning)."""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text


def generate_markdown_report(collection_data):
    """Generate markdown report from collection data."""
    from collections import Counter

    articles = collection_data["articles"]
    collected_at = collection_data["collected_at"]

    md = f"""# RSS Feed Collection Report

**Collection Date:** {collected_at}
**Source Type:** {collection_data['source_type']}
**Total Articles:** {len(articles)}

---

## Summary by Source

"""

    # Count articles by source
    source_counts = Counter(article['source'] for article in articles)

    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        md += f"- **{source}**: {count} articles\n"

    md += "\n---\n\n## Articles\n\n"

    # Add each article
    for i, article in enumerate(articles, 1):
        md += f"### {i}. {article['title']}\n\n"
        md += f"**Source:** {article['source']}  \n"
        md += f"**Category:** {article['category']}  \n"
        md += f"**Published:** {article['published']}  \n"
        md += f"**URL:** {article['url']}  \n\n"
        md += f"**Summary:**\n\n{article['summary']}\n\n"
        md += "---\n\n"

    # Add footer
    md += f"\n*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    md += f"*Total articles: {len(articles)} from {len(source_counts)} sources*\n"

    return md


def main():
    """Test RSS collector."""
    print("=" * 60)
    print("RSS COLLECTOR TEST")
    print("=" * 60 + "\n")

    collector = RSSCollector()
    articles = collector.collect(days_back=7)

    if articles:
        print("\n" + "=" * 60)
        print("SAMPLE ARTICLES")
        print("=" * 60)

        # Show first 3 articles
        for article in articles[:3]:
            print(f"\nTitle: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Published: {article['published']}")
            print(f"URL: {article['url']}")
            print(f"Summary: {article['summary'][:150]}...")

        # Save to test file (JSON)
        output_path = "data/raw/test-rss-collection.json"
        Path("data/raw").mkdir(parents=True, exist_ok=True)

        collection_data = {
            "collected_at": datetime.now().isoformat(),
            "source_type": "rss",
            "articles": articles
        }

        with open(output_path, 'w') as f:
            json.dump(collection_data, f, indent=2)

        print(f"\n✓ Saved JSON to: {output_path}")

        # Also save markdown report
        md_path = "data/raw/test-rss-collection.md"
        md_content = generate_markdown_report(collection_data)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"✓ Saved Markdown to: {md_path}")
    else:
        print("\n✗ No articles collected")


if __name__ == "__main__":
    main()
