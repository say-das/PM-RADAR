"""
Content Analyzer Agent
Uses OpenAI GPT-4o to analyze, categorize, and summarize collected research data.
"""

import json
import os
from datetime import datetime


class ContentAnalyzerAgent:
    def __init__(self):
        """Initialize Content Analyzer Agent with OpenAI GPT-4o."""
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY in .env file"
            )

    def _load_fallback_data(self, category_name, days_back=7):
        """
        Load articles from previous raw data files as fallback when current collection fails.

        Args:
            category_name: 'telecom_fraud' or 'competitor'
            days_back: Number of days to look back for data

        Returns:
            List of articles from previous collections, or empty list if none found
        """
        from pathlib import Path
        from datetime import datetime, timedelta

        fallback_articles = []
        raw_data_dir = Path("data/raw")

        if not raw_data_dir.exists():
            return []

        try:
            # Get date range to check
            today = datetime.now()
            date_range = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, days_back + 1)]

            # Check each date's raw data file
            for date_str in date_range:
                raw_file = raw_data_dir / f"{date_str}.json"

                if not raw_file.exists():
                    continue

                # Load and extract articles with matching category
                with open(raw_file, 'r') as f:
                    data = json.load(f)

                if "rss_articles" in data:
                    for article in data["rss_articles"]:
                        if article.get('category') == category_name:
                            fallback_articles.append(article)

                # If we found articles, return up to 10 most recent
                if fallback_articles:
                    return fallback_articles[:10]

        except Exception as e:
            # Silently fail - fallback is optional
            pass

        return []

    def _categorize_content(self, collected_data):
        """
        Categorize collected data into Telecom Fraud, General Fraud, and Competitive Intelligence.

        Returns:
            Dictionary with 'telecom', 'general', and 'competitive' keys, each containing articles and posts
        """
        # Define telecom-specific keywords (checked first for prioritization)
        telecom_keywords = [
            # Core telecom fraud
            'telecom fraud', 'sms pumping', 'irsf', 'iprn', 'toll fraud',
            'premium rate fraud', 'wangiri', 'international revenue share fraud',

            # Messaging platforms & protocols
            'sms', 'mms', 'rcs', 'a2p', 'p2p messaging', 'whatsapp',
            'messaging platform', 'text message', 'mobile messaging',
            'sms blaster', 'text spam',

            # Voice/calling fraud
            'robocall', 'call spoofing', 'caller id spoofing', 'voip fraud',
            'vishing', 'phone scam', 'telemarketing fraud', 'scam call',
            'phone fraud', 'phone number disconnected', 'scam block',

            # Mobile/SIM fraud
            'sim swap', 'sim box', 'sim card fraud', 'mobile number',
            'phone number fraud', 'burner phone',

            # SMS-specific fraud
            'smishing', 'sms fraud', 'sms spam', 'sms verification fraud',
            'otp fraud', 'one-time password', 'verification code fraud',

            # Telecom infrastructure
            'carrier fraud', 'mobile network fraud', 'grey route',
            'telecom carrier', 'mobile operator fraud'
        ]

        # Define general fraud keywords (checked after telecom)
        fraud_keywords = [
            'fraud', 'security', 'authentication', 'verification', 'scam',
            'spam', 'abuse', 'prevention', 'detection',
            'risk', 'compliance', 'protection', 'threat', 'attack'
        ]

        categorized = {
            'telecom': {'articles': [], 'posts': []},
            'general': {'articles': [], 'posts': []},
            'competitive': {'articles': [], 'posts': []}
        }

        # Categorize RSS articles
        if "rss_articles" in collected_data:
            for article in collected_data["rss_articles"]:
                text = (article['title'] + ' ' + article['summary']).lower()
                article_category = article.get('category', '')

                # Priority 1: Check source category first
                # Articles from telecom_fraud sources (Commsrisk, CFCA, Globe) → always telecom
                if article_category == 'telecom_fraud':
                    categorized['telecom']['articles'].append(article)
                # Priority 2: Competitor content (only if fraud-related)
                elif article_category == 'competitor':
                    if any(keyword in text for keyword in telecom_keywords + fraud_keywords):
                        categorized['competitive']['articles'].append(article)
                # Priority 3: Keyword-based classification for other sources
                # Check telecom keywords FIRST (priority over general)
                elif any(keyword in text for keyword in telecom_keywords):
                    categorized['telecom']['articles'].append(article)
                elif any(keyword in text for keyword in fraud_keywords):
                    categorized['general']['articles'].append(article)
                # If no keywords match, skip the article (don't categorize)

        # Reddit posts are NOT categorized into Telecom/General
        # They will be analyzed separately as Twilio Community Discussions

        # Fallback: Use previous week's data if current collection failed
        if len(categorized['telecom']['articles']) == 0:
            print("    → No telecom articles found, checking fallback data...")
            fallback_articles = self._load_fallback_data('telecom_fraud', days_back=7)
            if fallback_articles:
                categorized['telecom']['articles'].extend(fallback_articles)
                print(f"    ✓ Loaded {len(fallback_articles)} telecom articles from fallback")
            else:
                print("    ⚠ No fallback data available")

        if len(categorized['competitive']['articles']) == 0:
            fallback_articles = self._load_fallback_data('competitor', days_back=7)
            if fallback_articles:
                categorized['competitive']['articles'].extend(fallback_articles)
                print(f"    ✓ Loaded {len(fallback_articles)} competitive articles from fallback")

        return categorized

    def analyze(self, collected_data):
        """
        Analyze collected data and generate summaries.

        Args:
            collected_data: Dictionary with keys like 'rss_articles', 'reddit_posts'

        Returns:
            Dictionary with analysis results
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai library not installed. Run: pip install openai"
            )

        client = OpenAI(api_key=self.api_key)

        print("Analyzing data with Content Analyzer Agent (GPT-4o)...")

        # Categorize content first
        print("  → Categorizing content by topic...")
        categorized = self._categorize_content(collected_data)

        telecom_count = len(categorized['telecom']['articles']) + len(categorized['telecom']['posts'])
        general_count = len(categorized['general']['articles']) + len(categorized['general']['posts'])
        competitive_count = len(categorized['competitive']['articles']) + len(categorized['competitive']['posts'])

        print(f"    ✓ Telecom Fraud: {telecom_count} items")
        print(f"    ✓ General Fraud: {general_count} items")
        print(f"    ✓ Competitive Intelligence: {competitive_count} items")

        analysis = {
            "analyzed_at": datetime.now().isoformat(),
            "telecom_fraud_summary": None,
            "general_fraud_summary": None,
            "competitive_intelligence_summary": None,
            "categorized_counts": {
                "telecom": telecom_count,
                "general": general_count,
                "competitive": competitive_count
            }
        }

        # Analyze Telecom Fraud content
        if telecom_count > 0:
            print("  → Analyzing Telecom Fraud content...")
            analysis["telecom_fraud_summary"] = self._analyze_category(
                client,
                categorized['telecom'],
                "Telecom Fraud"
            )
            print("    ✓ Telecom Fraud analysis complete")

        # Analyze General Fraud content
        if general_count > 0:
            print("  → Analyzing General Fraud content...")
            analysis["general_fraud_summary"] = self._analyze_category(
                client,
                categorized['general'],
                "General Fraud & Security"
            )
            print("    ✓ General Fraud analysis complete")

        # Analyze Competitive Intelligence content
        if competitive_count > 0:
            print("  → Analyzing Competitive Intelligence content...")
            analysis["competitive_intelligence_summary"] = self._analyze_competitive(
                client,
                categorized['competitive']
            )
            print("    ✓ Competitive Intelligence analysis complete")

        # Analyze Twilio Reddit Community Discussions (separate section)
        reddit_posts = collected_data.get('reddit_posts', [])
        if reddit_posts:
            print("  → Analyzing Twilio Reddit Community...")
            analysis["reddit_community_summary"] = self._analyze_reddit_community(
                client,
                reddit_posts
            )
            print("    ✓ Twilio Reddit Community analysis complete")

        return analysis

    def _analyze_competitive(self, client, category_data):
        """Analyze competitive intelligence focused on fraud-related launches and features."""
        articles = category_data['articles']
        posts = category_data['posts']

        # Prepare combined content
        content_parts = []

        if articles:
            article_text = "\n\n".join([
                f"[{a['source']}] {a['title']}\nPublished: {a['published']}\nSummary: {a['summary']}"
                for a in articles[:20]  # Limit to 20 articles
            ])
            content_parts.append(f"COMPETITOR CONTENT:\n{article_text}")

        if posts:
            post_text = "\n\n".join([
                f"[REDDIT] r/{p['subreddit']} - {p['title']}\nScore: {p['score']} | Comments: {p['num_comments']}\nText: {p['selftext'][:200]}"
                for p in posts[:10]
            ])
            content_parts.append(f"SOCIAL DISCUSSIONS:\n{post_text}")

        if not content_parts:
            return None

        combined_content = "\n\n---\n\n".join(content_parts)

        prompt = f"""Analyze competitive intelligence from messaging/communications competitors (Vonage, MessageBird, Plivo, Bandwidth, Sinch) focusing on fraud prevention and security.

{combined_content}

Provide:
1. Executive summary - What are competitors doing in fraud prevention?
2. New product launches or features (fraud/security related)
3. Notable customer wins or case studies (if mentioned)
4. API changes or technical updates (fraud detection, verification, etc.)
5. Competitive positioning - How are they messaging fraud prevention capabilities?

Focus ONLY on fraud, security, verification, and authentication topics. Ignore general product updates unrelated to fraud prevention.

Format as JSON with keys: executive_summary, product_launches, customer_wins, technical_updates, competitive_positioning"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a competitive intelligence analyst specializing in fraud prevention and security features for messaging platforms. Focus on product launches, features, and positioning related to fraud detection and prevention."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        return response.choices[0].message.content

    def _analyze_category(self, client, category_data, category_name):
        """Analyze content for a specific fraud category (Telecom or General)."""
        articles = category_data['articles']
        posts = category_data['posts']

        # Prepare combined content
        content_parts = []

        if articles:
            article_text = "\n\n".join([
                f"[ARTICLE_{i}] {a['title']}\nSource: {a['source']}\nURL: {a['url']}\nPublished: {a['published']}\nSummary: {a['summary']}"
                for i, a in enumerate(articles[:15], 1)  # Limit to 15 articles, numbered for citation
            ])
            content_parts.append(f"INDUSTRY NEWS:\n{article_text}")

        if posts:
            post_texts = []
            for i, p in enumerate(posts[:10], 1):  # Limit to 10 posts, numbered for citation
                # Optimized format: only essential fields
                post_str = (
                    f"[REDDIT_{i}]\n"
                    f"Title: {p['title']}\n"
                    f"Post: {p.get('selftext', '(no text)')}\n"
                    f"Score: {p['score']} | URL: {p.get('url', 'N/A')}"
                )

                # Add top 10 comments if present
                comments = p.get('comments', [])
                if comments:
                    post_str += f"\nComments ({len(comments)}):"
                    for comment in comments[:10]:  # Top 10 comments
                        # Only include comment text and score
                        post_str += f"\n  - [{comment['score']} pts] {comment['body']}"

                post_texts.append(post_str)

            post_text = "\n\n".join(post_texts)
            content_parts.append(f"SOCIAL DISCUSSIONS:\n{post_text}")

        if not content_parts:
            return None

        combined_content = "\n\n---\n\n".join(content_parts)

        prompt = f"""Analyze this {category_name} intelligence from the past week.

{combined_content}

IMPORTANT INSTRUCTIONS:
1. For articles: Include inline citations using [ARTICLE_N] notation (e.g., [ARTICLE_1]) after each claim
2. For Reddit: Include specific verbatim quotes from posts AND comments using [REDDIT_N] notation
   - Reddit posts include both the original post text and community comments
   - Use actual quotes from users and commenters to show real customer sentiment
3. Cite multiple sources when applicable (e.g., [ARTICLE_1][ARTICLE_3])

Provide:
1. Executive summary (2-3 sentences) - what's happening in {category_name}. Include [ARTICLE_N] citations.
2. Top 3 trends or threats specific to {category_name}. Each trend must cite sources with [ARTICLE_N].
3. Notable incidents, attacks, or regulatory changes. Include [ARTICLE_N] citations.
4. Anything requiring immediate attention. Include [ARTICLE_N] citations.
5. If Reddit discussions present: key concerns with VERBATIM QUOTES from posts AND comments using [REDDIT_N] citations.
   - Pay special attention to comments as they reveal additional customer pain points, workarounds, and validation of issues
   - Include actual user text snippets in quotes from both posts and comments

Format as JSON with keys: executive_summary, top_trends, regulatory_changes, immediate_attention, community_sentiment (if applicable).
Each text value must include inline [ARTICLE_N] or [REDDIT_N] citations."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a fraud intelligence analyst specializing in {category_name}. Provide actionable insights for product and security teams."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        return response.choices[0].message.content

    def _analyze_reddit_community(self, client, reddit_posts):
        """
        Analyze Twilio Reddit community discussions separately.
        Focus on trending concerns, pain points, and overall sentiment.
        """
        # IMPORTANT: This limit must match MAX_REDDIT_POSTS_FOR_ANALYSIS in main.py
        # to ensure all citations have corresponding entries in the Sources section
        MAX_POSTS = 15

        # Prepare Reddit posts with comments
        post_texts = []
        for i, p in enumerate(reddit_posts[:MAX_POSTS], 1):
            post_str = (
                f"[REDDIT_{i}]\n"
                f"Title: {p['title']}\n"
                f"Post: {p.get('selftext', '(no text)')}\n"
                f"Score: {p['score']} | URL: {p.get('url', 'N/A')}"
            )

            # Add comments
            comments = p.get('comments', [])
            if comments:
                post_str += f"\nComments ({len(comments)}):"
                for comment in comments[:10]:
                    post_str += f"\n  - [{comment['score']} pts] {comment['body']}"

            post_texts.append(post_str)

        combined_content = "\n\n".join(post_texts)

        prompt = f"""Analyze Twilio community discussions from r/twilio on Reddit.

{combined_content}

INSTRUCTIONS:
Analyze these Reddit discussions to understand what Twilio customers are experiencing and discussing.
Focus on identifying patterns, recurring themes, and overall sentiment.

Provide a comprehensive analysis with:

1. **Trending Concerns/Topics** (Top 5-7):
   - What are the most frequently discussed issues or concerns?
   - Group similar concerns together (e.g., "Account Verification Issues", "Fraudulent Charges", "Support Responsiveness")
   - For each concern, include 2-3 example quotes from posts/comments
   - For each quote, note which post number it came from (as an integer, not [REDDIT_N] format)

2. **Community Sentiment**:
   - Overall sentiment: Frustrated / Neutral / Positive
   - What are users most frustrated about?
   - What are users praising (if anything)?
   - Common pain points mentioned across multiple posts
   - Include specific quotes with post numbers (as integers)

3. **Key Insights**:
   - What product/service issues are repeatedly mentioned?
   - What competitors or alternatives are being discussed?
   - What workarounds or solutions are users sharing?
   - Any patterns in the types of users affected (solo devs, businesses, etc.)?
   - Note relevant post numbers (as integers, not [REDDIT_N] format)

Format as JSON with these keys:
- trending_concerns: list of objects with 'topic', 'description', 'examples' (where examples is a list of objects with 'quote' string and 'post_num' integer)
- overall_sentiment: string
- sentiment_details: object with 'frustrations' (list of strings) and 'praises' (list of strings)
- key_insights: list of objects with 'insight' string and 'post_nums' (list of integers)

CRITICAL: Do NOT use [REDDIT_N] notation anywhere in the JSON. Use plain integers for post numbers (e.g., 2, 14, not [REDDIT_2])."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a community sentiment analyst specializing in developer and customer feedback. Analyze Reddit discussions to identify patterns, concerns, and sentiment about Twilio's products and services."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000  # More tokens for comprehensive community analysis
        )

        return response.choices[0].message.content


def main():
    """Test summarizer with sample data."""
    print("=" * 60)
    print("SUMMARIZER TEST")
    print("=" * 60 + "\n")

    from dotenv import load_dotenv
    load_dotenv()

    try:
        # Load test data
        test_rss_path = "data/raw/test-rss-collection.json"
        test_reddit_path = "data/raw/test-reddit-collection.json"

        collected_data = {}

        if os.path.exists(test_rss_path):
            with open(test_rss_path) as f:
                rss_data = json.load(f)
                collected_data["rss_articles"] = rss_data.get("articles", [])
                print(f"✓ Loaded {len(collected_data['rss_articles'])} RSS articles")

        if os.path.exists(test_reddit_path):
            with open(test_reddit_path) as f:
                reddit_data = json.load(f)
                collected_data["reddit_posts"] = reddit_data.get("posts", [])
                print(f"✓ Loaded {len(collected_data['reddit_posts'])} Reddit posts")

        if not collected_data:
            print("✗ No test data found. Run collectors first:")
            print("  python -m scripts.collect.rss_collector")
            print("  python -m scripts.collect.reddit_collector")
            return

        print("\nStarting analysis...\n")

        summarizer = ContentAnalyzerAgent()
        analysis = summarizer.analyze(collected_data)

        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)

        if analysis["rss_summary"]:
            print("\nRSS SUMMARY:")
            print(analysis["rss_summary"])

        if analysis["reddit_summary"]:
            print("\nREDDIT SUMMARY:")
            print(analysis["reddit_summary"])

        if analysis["themes"]:
            print(f"\nTHEMES ({len(analysis['themes'])}):")
            print(json.dumps(analysis["themes"], indent=2))

        if analysis["key_insights"]:
            print(f"\nKEY INSIGHTS ({len(analysis['key_insights'])}):")
            print(json.dumps(analysis["key_insights"], indent=2))

        # Save analysis
        output_path = "data/raw/test-analysis.json"
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"\n✓ Saved to: {output_path}")

    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nTo fix:")
        print("1. Get OpenAI API key from: https://platform.openai.com/api-keys")
        print("2. Add OPENAI_API_KEY to .env file")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
