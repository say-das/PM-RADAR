"""
PM Radar MVP - Main Orchestration Script
Runs weekly collection, analysis, and delivery pipeline.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Configuration Constants
MAX_REDDIT_POSTS_FOR_ANALYSIS = 15  # Must match limit in summarizer.py _analyze_reddit_community()

# Import collectors
from scripts.collect.rss_collector import RSSCollector
from scripts.collect.reddit_collector import RedditCollector

# Import analyzers
from scripts.analyze.summarizer import ContentAnalyzerAgent

# Import deliverers
from scripts.deliver.email_sender import EmailSender


def main():
    """Main pipeline execution."""
    print("=" * 70)
    print(" " * 20 + "PM RADAR - WEEKLY INTELLIGENCE")
    print("=" * 70)
    print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)

    # Load environment variables
    load_dotenv()

    date_str = datetime.now().strftime('%Y-%m-%d')

    # =========================================================================
    # PHASE 1: DATA COLLECTION
    # =========================================================================
    print("\n" + "=" * 70)
    print("[1/3] DATA COLLECTION")
    print("=" * 70 + "\n")

    collected_data = {
        "collection_date": date_str,
        "rss_articles": [],
        "reddit_posts": [],
        "competitor_maps": []
    }

    # Collect RSS feeds
    print("[1.1] RSS FEEDS")
    print("-" * 70)
    try:
        rss_collector = RSSCollector()
        collected_data["rss_articles"] = rss_collector.collect(days_back=7)
    except Exception as e:
        print(f"✗ RSS collection failed: {e}")

    # Collect Reddit posts
    print("\n[1.2] REDDIT POSTS")
    print("-" * 70)
    try:
        reddit_collector = RedditCollector()
        collected_data["reddit_posts"] = reddit_collector.collect()
    except ValueError as e:
        print(f"⚠ Reddit collection skipped: {e}")
        print("  (SociaVault API key not configured)")
    except Exception as e:
        print(f"✗ Reddit collection failed: {e}")

    # Source Discovery Agent (Phase 2 - not yet implemented)
    print("\n[1.3] SOURCE DISCOVERY")
    print("-" * 70)
    print("⚠ Source Discovery Agent not yet implemented (Phase 2)")
    print("  Will automatically find new competitors, analysts, and community sources")

    # Save raw collected data
    raw_data_path = Path(f"data/raw/{date_str}.json")
    raw_data_path.parent.mkdir(parents=True, exist_ok=True)

    with open(raw_data_path, 'w') as f:
        json.dump(collected_data, f, indent=2)

    print(f"\n✓ Raw data saved: {raw_data_path}")

    # =========================================================================
    # PHASE 2: AI ANALYSIS (Content Analyzer Agent)
    # =========================================================================
    print("\n" + "=" * 70)
    print("[2/3] CONTENT ANALYSIS (Content Analyzer Agent)")
    print("=" * 70 + "\n")

    analysis_results = None

    # Check if we have data to analyze
    total_items = len(collected_data["rss_articles"]) + len(collected_data["reddit_posts"])

    if total_items == 0:
        print("⚠ No data collected - skipping analysis")
    else:
        try:
            analyzer = ContentAnalyzerAgent()
            analysis_results = analyzer.analyze(collected_data)

            # Save analysis
            analysis_path = Path(f"data/raw/{date_str}-analysis.json")
            with open(analysis_path, 'w') as f:
                json.dump(analysis_results, f, indent=2)

            print(f"\n✓ Analysis saved: {analysis_path}")

        except ValueError as e:
            print(f"⚠ Analysis skipped: {e}")
            print("  (OpenAI API key not configured)")
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
            import traceback
            traceback.print_exc()

    # =========================================================================
    # PHASE 3: REPORT GENERATION & DELIVERY
    # =========================================================================
    print("\n" + "=" * 70)
    print("[3/3] REPORT GENERATION & DELIVERY")
    print("=" * 70 + "\n")

    # Generate markdown report
    print("Generating report...")
    report = generate_report(collected_data, analysis_results, date_str)

    # Save report
    report_path = Path(f"data/reports/{date_str}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write(report)

    print(f"✓ Report saved: {report_path}")

    # Generate HTML version (print-ready for PDF export)
    print("\nGenerating HTML (print-ready)...")
    try:
        from scripts.deliver.pdf_exporter import PDFExporter
        exporter = PDFExporter()
        html_path = exporter.markdown_to_html(str(report_path))
        file_size = os.path.getsize(html_path) / 1024  # KB
        print(f"✓ HTML saved: {html_path} ({file_size:.1f} KB)")
        print(f"  Open in browser and use Print → Save as PDF for PDF version")
    except ImportError as e:
        print(f"⚠ HTML export skipped: Missing dependencies")
        print(f"  Install with: pip install markdown")
    except Exception as e:
        print(f"⚠ HTML generation failed: {e}")

    # GitHub Release & Pages delivery
    print("\nPublishing to GitHub Release & Pages...")
    try:
        from scripts.deliver.github_release import GitHubReleasePublisher
        github_publisher = GitHubReleasePublisher()

        # Check prerequisites
        issues = github_publisher.check_prerequisites()
        if issues:
            print(f"⚠ GitHub Release skipped - prerequisites not met:")
            for issue in issues:
                print(f"  • {issue}")
            github_result = {"success": False}
        else:
            github_result = github_publisher.publish_report(report_path, date_str)

            if github_result["success"]:
                print(f"✓ GitHub Release created: {github_result['release_url']}")
                print(f"✓ Report published at: {github_result['pages_url']}")
            else:
                print(f"✗ GitHub Release failed: {github_result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"✗ GitHub Release failed: {e}")
        import traceback
        traceback.print_exc()
        github_result = {"success": False}

    # Email delivery (optional fallback)
    print("\nSending email...")
    try:
        email_sender = EmailSender()
        email_result = email_sender.send_report(report_path, date_str)

        if email_result["success"]:
            print(f"✓ Email delivered to {email_result['recipients']} recipient(s)")
        else:
            print(f"✗ Email delivery failed: {email_result.get('error', 'Unknown error')}")
            print(f"  Report available at: {report_path}")

    except ValueError as e:
        print(f"⚠ Email delivery skipped: {e}")
        print(f"  (Brevo API key not configured)")
        print(f"  Report available at: {report_path}")
    except Exception as e:
        print(f"✗ Email delivery failed: {e}")
        print(f"  Report available at: {report_path}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)

    print(f"\nCollection Summary:")
    print(f"  • RSS articles: {len(collected_data['rss_articles'])}")
    print(f"  • Reddit posts: {len(collected_data['reddit_posts'])}")
    if analysis_results and "categorized_counts" in analysis_results:
        print(f"  • Telecom Fraud items: {analysis_results['categorized_counts']['telecom']}")
        print(f"  • General Fraud items: {analysis_results['categorized_counts']['general']}")
        print(f"  • Competitive Intelligence items: {analysis_results['categorized_counts']['competitive']}")
    print(f"  • Analysis: {'✓ Complete' if analysis_results else '✗ Skipped'}")
    print(f"  • Report: {report_path}")
    if 'github_result' in locals() and github_result["success"]:
        print(f"  • GitHub Release: ✓ Published")
        print(f"  • Pages URL: {github_result['pages_url']}")
    else:
        print(f"  • GitHub Release: ✗ Not published")
    if 'email_result' in locals() and email_result["success"]:
        print(f"  • Email: ✓ Delivered to {email_result['recipients']} recipient(s)")
    else:
        print(f"  • Email: ✗ Not delivered")

    print("\n" + "=" * 70 + "\n")


def parse_json_response(response_text):
    """Extract and parse JSON from GPT response that may be wrapped in code fences."""
    if not response_text:
        return None

    # Remove code fence markers if present
    text = response_text.strip()
    if text.startswith('```json'):
        text = text[7:]  # Remove ```json
    if text.startswith('```'):
        text = text[3:]  # Remove ```
    if text.endswith('```'):
        text = text[:-3]  # Remove trailing ```

    text = text.strip()

    try:
        return json.loads(text)
    except:
        return None


def generate_report(collected_data, analysis_results, date_str):
    """Generate markdown report from collected data and analysis."""

    # Build citation mapping from collected data
    citations = {}

    # Map articles (ARTICLE_1, ARTICLE_2, etc.)
    if "rss_articles" in collected_data:
        for i, article in enumerate(collected_data["rss_articles"][:15], 1):
            citations[f"ARTICLE_{i}"] = {
                "title": article["title"],
                "source": article["source"],
                "url": article["url"],
                "published": article["published"]
            }

    # Map Reddit posts (REDDIT_1, REDDIT_2, etc.) with URLs
    # Note: Must match the limit used in Reddit Community analysis
    if "reddit_posts" in collected_data:
        for i, post in enumerate(collected_data["reddit_posts"][:MAX_REDDIT_POSTS_FOR_ANALYSIS], 1):
            # Extract subreddit name (handle both string and dict formats)
            subreddit = post.get("subreddit", "unknown")
            if isinstance(subreddit, dict):
                subreddit = subreddit.get("name", "unknown")

            citations[f"REDDIT_{i}"] = {
                "title": post["title"],
                "subreddit": subreddit,
                "score": post["score"],
                "url": post.get("url", "")
            }

    report = f"""# PM Radar Weekly Intelligence Digest
**Date:** {date_str}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## Executive Summary

"""

    # Collection stats
    rss_count = len(collected_data["rss_articles"])
    reddit_count = len(collected_data["reddit_posts"])

    report += f"- **{rss_count}** industry articles reviewed\n"
    report += f"- **{reddit_count}** Reddit discussions analyzed\n"

    if analysis_results and "categorized_counts" in analysis_results:
        telecom_count = analysis_results["categorized_counts"]["telecom"]
        general_count = analysis_results["categorized_counts"]["general"]
        competitive_count = analysis_results["categorized_counts"]["competitive"]
        report += f"- **{telecom_count}** items categorized as Telecom Fraud\n"
        report += f"- **{general_count}** items categorized as General Fraud\n"
        report += f"- **{competitive_count}** items categorized as Competitive Intelligence\n"

    report += "\n---\n\n"

    # Telecom Fraud Digest
    if analysis_results and analysis_results.get("telecom_fraud_summary"):
        report += "## Telecom Fraud Digest\n\n"

        # Parse JSON from GPT-4o response
        telecom_analysis = parse_json_response(analysis_results['telecom_fraud_summary'])

        if telecom_analysis:
            if 'executive_summary' in telecom_analysis:
                report += f"**Executive Summary:**\n\n{telecom_analysis['executive_summary']}\n\n"

            if 'top_trends' in telecom_analysis and telecom_analysis['top_trends']:
                trends = telecom_analysis['top_trends']
                if isinstance(trends, list):
                    report += "**Top Threats & Trends:**\n\n"
                    for i, trend in enumerate(trends, 1):
                        # Handle dict with nested description/details
                        if isinstance(trend, dict):
                            trend_name = trend.get('trend', '')
                            description = trend.get('description', '') or trend.get('details', '')
                            report += f"{i}. **{trend_name}**: {description}\n"
                        else:
                            report += f"{i}. {trend}\n"
                    report += "\n"
                elif isinstance(trends, str) and trends.lower() not in ['none', 'n/a', 'no trends']:
                    report += f"**Top Threats & Trends:**\n\n{trends}\n\n"

            if 'regulatory_changes' in telecom_analysis and telecom_analysis['regulatory_changes']:
                changes = telecom_analysis['regulatory_changes']
                if isinstance(changes, list):
                    report += "**Regulatory & Market Changes:**\n\n"
                    for i, change in enumerate(changes, 1):
                        # Handle dict with nested description/details
                        if isinstance(change, dict):
                            incident = change.get('incident', change.get('change', ''))
                            description = change.get('description', '') or change.get('details', '')
                            report += f"{i}. **{incident}**: {description}\n"
                        else:
                            report += f"{i}. {change}\n"
                    report += "\n"
                elif isinstance(changes, str):
                    # Check if it's a "no changes" message
                    lower_changes = changes.lower()
                    if not any(phrase in lower_changes for phrase in ['no significant', 'no notable', 'none', 'n/a', 'not applicable', 'no regulatory']):
                        report += f"**Regulatory & Market Changes:**\n\n{changes}\n\n"

            if 'immediate_attention' in telecom_analysis and telecom_analysis['immediate_attention']:
                items = telecom_analysis['immediate_attention']
                if isinstance(items, list):
                    report += "**Immediate Attention Required:**\n\n"
                    for i, item in enumerate(items, 1):
                        # Handle dict with nested description/details
                        if isinstance(item, dict):
                            issue = item.get('issue', item.get('action', ''))
                            description = item.get('description', '') or item.get('details', '')
                            report += f"{i}. **{issue}**: {description}\n"
                        else:
                            report += f"{i}. {item}\n"
                    report += "\n"
                elif isinstance(items, str):
                    # Check if it's a "no action needed" message
                    lower_items = items.lower()
                    if not any(phrase in lower_items for phrase in ['none', 'n/a', 'not applicable', 'no immediate']):
                        report += f"**Immediate Attention Required:**\n\n{items}\n\n"

            if 'community_sentiment' in telecom_analysis and telecom_analysis['community_sentiment']:
                sentiment = telecom_analysis['community_sentiment']

                # Handle list of concern objects (new format with quotes)
                if isinstance(sentiment, list):
                    report += "**Community Sentiment (Reddit):**\n\n"
                    for item in sentiment:
                        if isinstance(item, dict):
                            concern_text = item.get('concern', '')
                            # Handle both 'quote' (singular) and 'quotes' (plural)
                            quote_text = item.get('quote', '')
                            quotes_list = item.get('quotes', [])

                            if concern_text and quote_text:
                                # Format: concern as title, quote as content
                                report += f"- **{concern_text}**: {quote_text}\n\n"
                            elif concern_text and quotes_list:
                                # Format: concern as title, multiple quotes as blockquotes
                                report += f"**{concern_text}:**\n\n"
                                for quote in quotes_list:
                                    report += f"> {quote}\n\n"
                            elif concern_text:
                                # Format: concern contains full text (no separate quote field)
                                report += f"- {concern_text}\n\n"
                # Handle dict type - extract all possible content
                elif isinstance(sentiment, dict):
                    # Special handling for key_concerns format
                    if 'key_concerns' in sentiment and isinstance(sentiment['key_concerns'], list):
                        report += "**Community Sentiment (Reddit):**\n\n"
                        for item in sentiment['key_concerns']:
                            if isinstance(item, dict):
                                concern = item.get('concern', '')
                                # Handle both 'details' and 'quote' fields
                                content = item.get('details', '') or item.get('quote', '')
                                if concern and content:
                                    report += f"- **{concern}**: {content}\n\n"
                    else:
                        # Fallback for other dict formats
                        sentiment_content = []
                        for key in ['sentiment', 'reddit_discussions', 'discussion', 'summary']:
                            if key in sentiment and sentiment[key]:
                                value = sentiment[key]
                                if isinstance(value, list):
                                    sentiment_content.append("\n".join(f"- {item}" for item in value))
                                else:
                                    sentiment_content.append(str(value))
                        if sentiment_content:
                            report += "**Community Sentiment (Reddit):**\n\n"
                            report += "\n\n".join(sentiment_content) + "\n\n"
                # Handle string type
                elif isinstance(sentiment, str):
                    # Check if it's NOT a "no data" message
                    if not any(phrase in sentiment.lower() for phrase in ['none', 'n/a', 'no reddit discussions', 'not applicable', 'no specific reddit']):
                        report += "**Community Sentiment (Reddit):**\n\n"
                        # Add bullet points for better hierarchy
                        lines = sentiment.strip().split('\n\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                # Remove trailing ":**" from bold statements for better formatting
                                if line.endswith(':**'):
                                    line = line[:-2] + ':'
                                # Add bullet point for each insight
                                report += f"- {line}\n\n"
        else:
            # Fallback to raw text if parsing fails
            report += f"{analysis_results['telecom_fraud_summary']}\n\n"

        report += "---\n\n"

    # General Fraud Digest
    if analysis_results and analysis_results.get("general_fraud_summary"):
        report += "## General Fraud & Security Digest\n\n"

        # Parse JSON from GPT-4o response
        general_analysis = parse_json_response(analysis_results['general_fraud_summary'])

        if general_analysis:
            if 'executive_summary' in general_analysis:
                report += f"**Executive Summary:**\n\n{general_analysis['executive_summary']}\n\n"

            if 'top_trends' in general_analysis and general_analysis['top_trends']:
                trends = general_analysis['top_trends']
                if isinstance(trends, list):
                    report += "**Top Threats & Trends:**\n\n"
                    for i, trend in enumerate(trends, 1):
                        # Handle dict with nested description
                        if isinstance(trend, dict):
                            trend_name = trend.get('trend', '')
                            description = trend.get('description', trend.get('details', ''))
                            report += f"{i}. **{trend_name}**: {description}\n"
                        else:
                            report += f"{i}. {trend}\n"
                    report += "\n"
                elif isinstance(trends, str) and trends.lower() not in ['none', 'n/a', 'no trends']:
                    report += f"**Top Threats & Trends:**\n\n{trends}\n\n"

            if 'regulatory_changes' in general_analysis and general_analysis['regulatory_changes']:
                changes = general_analysis['regulatory_changes']
                if isinstance(changes, list):
                    report += "**Regulatory & Market Changes:**\n\n"
                    for i, change in enumerate(changes, 1):
                        # Handle dict with nested description
                        if isinstance(change, dict):
                            incident = change.get('incident', change.get('change', ''))
                            description = change.get('description', change.get('details', ''))
                            report += f"{i}. **{incident}**: {description}\n"
                        else:
                            report += f"{i}. {change}\n"
                    report += "\n"
                elif isinstance(changes, str):
                    # Check if it's a "no changes" message
                    lower_changes = changes.lower()
                    if not any(phrase in lower_changes for phrase in ['no significant', 'no notable', 'none', 'n/a', 'not applicable', 'no regulatory']):
                        report += f"**Regulatory & Market Changes:**\n\n{changes}\n\n"

            if 'immediate_attention' in general_analysis and general_analysis['immediate_attention']:
                items = general_analysis['immediate_attention']
                if isinstance(items, list):
                    report += "**Immediate Attention Required:**\n\n"
                    for i, item in enumerate(items, 1):
                        # Handle dict with nested description
                        if isinstance(item, dict):
                            issue = item.get('issue', item.get('action', ''))
                            description = item.get('description', item.get('details', ''))
                            report += f"{i}. **{issue}**: {description}\n"
                        else:
                            report += f"{i}. {item}\n"
                    report += "\n"
                elif isinstance(items, str):
                    # Check if it's a "no action needed" message
                    lower_items = items.lower()
                    if not any(phrase in lower_items for phrase in ['none', 'n/a', 'not applicable', 'no immediate']):
                        report += f"**Immediate Attention Required:**\n\n{items}\n\n"

            if 'community_sentiment' in general_analysis and general_analysis['community_sentiment']:
                sentiment = general_analysis['community_sentiment']

                # Handle list of concern objects (new format with quotes)
                if isinstance(sentiment, list):
                    report += "**Community Sentiment (Reddit):**\n\n"
                    for item in sentiment:
                        if isinstance(item, dict):
                            concern_text = item.get('concern', '')
                            # Handle both 'quote' (singular) and 'quotes' (plural)
                            quote_text = item.get('quote', '')
                            quotes_list = item.get('quotes', [])

                            if concern_text and quote_text:
                                # Format: concern as title, quote as content
                                report += f"- **{concern_text}**: {quote_text}\n\n"
                            elif concern_text and quotes_list:
                                # Format: concern as title, multiple quotes as blockquotes
                                report += f"**{concern_text}:**\n\n"
                                for quote in quotes_list:
                                    report += f"> {quote}\n\n"
                            elif concern_text:
                                # Format: concern contains full text (no separate quote field)
                                report += f"- {concern_text}\n\n"
                # Handle dict type - extract all possible content
                elif isinstance(sentiment, dict):
                    # Special handling for key_concerns format
                    if 'key_concerns' in sentiment and isinstance(sentiment['key_concerns'], list):
                        report += "**Community Sentiment (Reddit):**\n\n"
                        for item in sentiment['key_concerns']:
                            if isinstance(item, dict):
                                concern = item.get('concern', '')
                                # Handle both 'details' and 'quote' fields
                                content = item.get('details', '') or item.get('quote', '')
                                if concern and content:
                                    report += f"- **{concern}**: {content}\n\n"
                    else:
                        # Fallback for other dict formats
                        sentiment_content = []
                        for key in ['sentiment', 'reddit_discussions', 'discussion', 'summary']:
                            if key in sentiment and sentiment[key]:
                                value = sentiment[key]
                                if isinstance(value, list):
                                    sentiment_content.append("\n".join(f"- {item}" for item in value))
                                else:
                                    sentiment_content.append(str(value))
                        if sentiment_content:
                            report += "**Community Sentiment (Reddit):**\n\n"
                            report += "\n\n".join(sentiment_content) + "\n\n"
                # Handle string type
                elif isinstance(sentiment, str):
                    # Check if it's NOT a "no data" message
                    if not any(phrase in sentiment.lower() for phrase in ['none', 'n/a', 'no reddit discussions', 'not applicable', 'no specific reddit']):
                        report += "**Community Sentiment (Reddit):**\n\n"
                        # Add bullet points for better hierarchy
                        lines = sentiment.strip().split('\n\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                # Remove trailing ":**" from bold statements for better formatting
                                if line.endswith(':**'):
                                    line = line[:-2] + ':'
                                # Add bullet point for each insight
                                report += f"- {line}\n\n"
        else:
            # Fallback to raw text if parsing fails
            report += f"{analysis_results['general_fraud_summary']}\n\n"

        report += "---\n\n"

    # Competitive Intelligence Digest
    if analysis_results and analysis_results.get("competitive_intelligence_summary"):
        report += "## Competitive Intelligence Digest\n\n"

        # Parse JSON from GPT-4o response
        competitive_analysis = parse_json_response(analysis_results['competitive_intelligence_summary'])

        if competitive_analysis:
            if 'executive_summary' in competitive_analysis:
                report += f"**Executive Summary:**\n\n{competitive_analysis['executive_summary']}\n\n"

            if 'product_launches' in competitive_analysis and competitive_analysis['product_launches']:
                launches = competitive_analysis['product_launches']
                if isinstance(launches, list) and launches:
                    report += "**New Product Launches & Features:**\n\n"
                    for i, launch in enumerate(launches, 1):
                        report += f"{i}. {launch}\n"
                    report += "\n"
                elif isinstance(launches, str):
                    lower_launches = launches.lower()
                    if not any(phrase in lower_launches for phrase in ['no new', 'no product', 'none', 'n/a', 'not mentioned']):
                        report += f"**New Product Launches & Features:**\n\n{launches}\n\n"

            if 'customer_wins' in competitive_analysis and competitive_analysis['customer_wins']:
                wins = competitive_analysis['customer_wins']
                if isinstance(wins, list) and wins:
                    report += "**Customer Wins & Case Studies:**\n\n"
                    for i, win in enumerate(wins, 1):
                        report += f"{i}. {win}\n"
                    report += "\n"
                elif isinstance(wins, str):
                    lower_wins = wins.lower()
                    if not any(phrase in lower_wins for phrase in ['no customer', 'no case', 'none', 'n/a', 'not mentioned']):
                        report += f"**Customer Wins & Case Studies:**\n\n{wins}\n\n"

            if 'technical_updates' in competitive_analysis and competitive_analysis['technical_updates']:
                updates = competitive_analysis['technical_updates']
                if isinstance(updates, list) and updates:
                    report += "**Technical Updates (APIs, SDKs, Security Features):**\n\n"
                    for i, update in enumerate(updates, 1):
                        report += f"{i}. {update}\n"
                    report += "\n"
                elif isinstance(updates, str):
                    lower_updates = updates.lower()
                    if not any(phrase in lower_updates for phrase in ['no technical', 'no api', 'none', 'n/a', 'not mentioned']):
                        report += f"**Technical Updates (APIs, SDKs, Security Features):**\n\n{updates}\n\n"

            if 'competitive_positioning' in competitive_analysis and competitive_analysis['competitive_positioning']:
                positioning = competitive_analysis['competitive_positioning']
                if isinstance(positioning, str):
                    lower_positioning = positioning.lower()
                    if not any(phrase in lower_positioning for phrase in ['no competitive', 'none', 'n/a', 'not mentioned']):
                        report += f"**Competitive Positioning:**\n\n{positioning}\n\n"
        else:
            # Fallback to raw text if parsing fails
            report += f"{analysis_results['competitive_intelligence_summary']}\n\n"

        report += "---\n\n"

    # Build glossary of technical terms
    import re

    # Twilio Reddit Community Discussions
    if analysis_results and analysis_results.get("reddit_community_summary"):
        report += "## Twilio Community Discussions (Reddit)\n\n"

        # Parse JSON from GPT-4o response
        reddit_analysis = parse_json_response(analysis_results['reddit_community_summary'])

        if reddit_analysis:
            # Trending Concerns/Topics
            if 'trending_concerns' in reddit_analysis and reddit_analysis['trending_concerns']:
                report += "**Trending Concerns & Topics:**\n\n"
                for i, concern in enumerate(reddit_analysis['trending_concerns'], 1):
                    topic = concern.get('topic', '')
                    description = concern.get('description', '')
                    examples = concern.get('examples', [])

                    if topic:
                        # Include number in topic name, use bold heading
                        report += f"**{i}. {topic}**\n\n"
                    if description:
                        report += f"{description}\n\n"
                    if examples:
                        report += f"**Examples:**\n\n"
                        for example in examples[:3]:  # Show top 3 examples
                            # Handle both formats: string or dict with quote/post_num
                            if isinstance(example, dict):
                                quote = example.get('quote', '')
                                post_num = example.get('post_num', 0)
                                if quote and post_num:
                                    report += f"- \"{quote}\" [\[R{post_num}\]](#r{post_num})\n"
                            else:
                                # String format (legacy)
                                report += f"- {example}\n"
                        report += "\n"

            # Overall Sentiment
            if 'overall_sentiment' in reddit_analysis:
                report += f"**Overall Sentiment:** {reddit_analysis['overall_sentiment']}\n\n"

            # Sentiment Details
            if 'sentiment_details' in reddit_analysis and reddit_analysis['sentiment_details']:
                details = reddit_analysis['sentiment_details']

                if details.get('frustrations'):
                    report += "**Key Frustrations:**\n"
                    frustrations = details['frustrations']
                    if isinstance(frustrations, list):
                        for f in frustrations:
                            report += f"- {f}\n"
                    else:
                        report += f"{frustrations}\n"
                    report += "\n"

                if details.get('praises'):
                    report += "**What Users Appreciate:**\n"
                    praises = details['praises']
                    if isinstance(praises, list):
                        for p in praises:
                            report += f"- {p}\n"
                    else:
                        report += f"{praises}\n"
                    report += "\n"

            # Key Insights
            if 'key_insights' in reddit_analysis and reddit_analysis['key_insights']:
                report += "**Key Insights:**\n\n"
                insights = reddit_analysis['key_insights']
                if isinstance(insights, list):
                    for insight in insights:
                        # Handle both formats: string or dict with insight/post_nums
                        if isinstance(insight, dict):
                            insight_text = insight.get('insight', '')
                            post_nums = insight.get('post_nums', [])
                            if insight_text:
                                citations = ''.join([f"[\[R{num}\]](#r{num})" for num in post_nums])
                                report += f"- {insight_text} {citations}\n"
                        else:
                            # String format (legacy)
                            report += f"- {insight}\n"
                else:
                    report += f"{insights}\n"
                report += "\n"

        else:
            # Fallback to raw text if parsing fails
            report += f"{analysis_results['reddit_community_summary']}\n\n"

        report += "---\n\n"

    # Define glossary of technical terms and abbreviations
    glossary = {
        'DPRK': 'Democratic People\'s Republic of Korea (North Korea)',
        'LNK': 'Windows shortcut file format (.lnk), often exploited for malware delivery',
        'C2': 'Command and Control - infrastructure used by attackers to remotely control compromised systems',
        'CISA': 'Cybersecurity and Infrastructure Security Agency (U.S. government)',
        'KEV': 'Known Exploited Vulnerabilities - CISA\'s catalog of actively exploited security flaws',
        'NPM': 'Node Package Manager - JavaScript package registry and dependency management tool',
        'API': 'Application Programming Interface - software intermediary allowing applications to communicate',
        'SMS': 'Short Message Service - text messaging protocol',
        'IRSF': 'International Revenue Share Fraud - telecom fraud using premium-rate numbers',
        'IPRN': 'International Premium Rate Number - high-cost phone numbers often used in fraud',
        'A2P': 'Application-to-Person messaging - automated messages from applications to users',
        'P2P': 'Person-to-Person messaging - direct messages between individuals',
        'SIM': 'Subscriber Identity Module - chip card used in mobile devices for carrier authentication',
        'EMS': 'Enterprise Management Server',
        'SDK': 'Software Development Kit - tools for building applications',
        'CVE': 'Common Vulnerabilities and Exposures - standard identifier for security vulnerabilities',
        'DoS': 'Denial of Service - attack that makes a system unavailable',
        'DDoS': 'Distributed Denial of Service - DoS attack from multiple sources',
        'IoT': 'Internet of Things - network of connected physical devices',
        'XSS': 'Cross-Site Scripting - security vulnerability in web applications',
        'SQL': 'Structured Query Language - database programming language',
        'VPN': 'Virtual Private Network - encrypted connection over the internet',
        'MFA': '2FA/Multi-Factor Authentication - security requiring multiple verification methods',
        'OAuth': 'Open Authorization - standard for access delegation',
        'GDPR': 'General Data Protection Regulation - EU privacy and data protection law',
        'PII': 'Personally Identifiable Information - data that can identify an individual',
        'SIEM': 'Security Information and Event Management - security data analysis platform',
        'SOC': 'Security Operations Center - centralized unit for security monitoring',
        'APT': 'Advanced Persistent Threat - sophisticated, long-term cyberattack',
        'RAT': 'Remote Access Trojan - malware providing remote control access',
        'Phishing': 'Fraudulent attempt to obtain sensitive information by disguising as trustworthy entity',
        'Vishing': 'Voice phishing - phone-based social engineering attack',
        'Smishing': 'SMS phishing - text message-based social engineering attack',
        'Zero-day': 'Previously unknown vulnerability with no available patch',
        'Patch': 'Software update fixing security vulnerabilities or bugs',
        'Exploit': 'Code or technique taking advantage of a security vulnerability',
        'Malware': 'Malicious software designed to damage or gain unauthorized access',
        'Ransomware': 'Malware that encrypts data and demands payment for decryption',
        'Botnet': 'Network of compromised computers controlled by an attacker',
        'Trojan': 'Malware disguised as legitimate software',
        'Spyware': 'Software that secretly monitors and collects user information',
        'Backdoor': 'Method of bypassing normal authentication to access a system',
        'Supply chain attack': 'Attack targeting a trusted third-party software or service provider',
        'Social engineering': 'Manipulation techniques to trick people into revealing sensitive information'
    }

    # Find technical terms actually used in the report (case-insensitive search)
    used_terms = {}
    report_lower = report.lower()

    for term, definition in glossary.items():
        # Create pattern that matches whole words
        pattern = r'\b' + re.escape(term.lower()) + r'\b'
        if re.search(pattern, report_lower):
            used_terms[term] = definition

    # Glossary section - add before sources
    if used_terms:
        report += "\n## Glossary\n\n"
        report += "*Technical terms and abbreviations used in this report:*\n\n"

        # Sort alphabetically
        for term in sorted(used_terms.keys(), key=str.lower):
            report += f"- **{term}**: {used_terms[term]}\n"

        report += "\n"

    # Convert long citations to short format with anchor links
    # ARTICLE_1 -> [A1](#a1) and REDDIT_1 -> [R1](#r1)

    # First, handle comma-separated citations like [REDDIT_2, REDDIT_14] -> [REDDIT_2][REDDIT_14]
    def expand_comma_citations(match):
        content = match.group(1)  # e.g., "REDDIT_2, REDDIT_14"
        citations = [c.strip() for c in content.split(',')]
        return ''.join(f'[{c}]' for c in citations)

    report = re.sub(r'\[((?:REDDIT|ARTICLE)_\d+(?:,\s*(?:REDDIT|ARTICLE)_\d+)+)\]', expand_comma_citations, report)

    # Now convert to anchor link format
    report = re.sub(r'\[ARTICLE_(\d+)\]', r'[\[A\1\]](#a\1)', report)
    report = re.sub(r'\[REDDIT_(\d+)\]', r'[\[R\1\]](#r\1)', report)

    # Clean up extra commas/spaces between adjacent citations
    # [\[R2\]](#r2), [\[R14\]](#r14) -> [\[R2\]](#r2)[\[R14\]](#r14)
    report = re.sub(r'(\]\(\#[ar]\d+\)),\s*\[', r'\1[', report)

    # Sources section - append citation references
    # Find all citations used in the report by looking for anchor links
    # Pattern: (#a1), (#r3) etc. in the markdown links
    anchor_matches = re.findall(r'#([ar]\d+)\)', report)
    # Convert to citation format: a1 -> [A1], r3 -> [R3]
    used_citations = set([f'[{m.upper()}]' for m in anchor_matches])

    if used_citations:
        report += "\n## Sources\n\n"

        # Group by type
        article_citations = sorted([c for c in used_citations if c.startswith('[A')], key=lambda x: int(x[2:-1]))
        reddit_citations = sorted([c for c in used_citations if c.startswith('[R')], key=lambda x: int(x[2:-1]))

        if article_citations:
            report += "**Articles:**\n\n"
            for citation_key in article_citations:
                # Convert short format back to long for lookup (A1 -> ARTICLE_1)
                num = citation_key[2:-1]
                key = f"ARTICLE_{num}"
                if key in citations:
                    c = citations[key]
                    # Add anchor link for inline citations to reference
                    # citation_key is [A1], we want anchor id to be just "a1"
                    anchor_id = citation_key[1:-1].lower()  # [A1] -> a1
                    report += f"- <a id=\"{anchor_id}\"></a>{citation_key}: [{c['title']}]({c['url']}) - {c['source']} ({c['published']})\n"
            report += "\n"

        if reddit_citations:
            report += "**Reddit Discussions:**\n\n"
            for citation_key in reddit_citations:
                # Convert short format back to long for lookup (R1 -> REDDIT_1)
                num = citation_key[2:-1]
                key = f"REDDIT_{num}"
                if key in citations:
                    c = citations[key]
                    # Add anchor link for inline citations to reference
                    # citation_key is [R3], we want anchor id to be just "r3"
                    anchor_id = citation_key[1:-1].lower()  # [R3] -> r3
                    report += f"- <a id=\"{anchor_id}\"></a>{citation_key}: [r/{c['subreddit']} - {c['title']}]({c['url']}) (Score: {c['score']})\n"
            report += "\n"

    # Footer
    report += "\n---\n\n"
    report += f"*Generated by PM Radar • {date_str}*\n"

    return report


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
