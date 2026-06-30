"""
Content Analyzer Agent
Uses OpenAI GPT-4o to analyze, categorize, and summarize collected research data.
"""

import json
import os
from datetime import datetime, timedelta, timezone


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

    def _gpt_categorize_articles(self, client, articles):
        """
        Use GPT-4o to score and categorize articles with deduplication.

        Returns:
            List of scored articles with category and deduplication info
        """
        if not articles:
            return []

        # Prepare articles for GPT (limit summary to 300 chars)
        article_list = []
        for i, article in enumerate(articles, 1):
            article_list.append(
                f"Article {i}:\n"
                f"Title: {article['title']}\n"
                f"Source: {article['source']}\n"
                f"Summary: {article['summary'][:300]}...\n"
            )

        combined_articles = "\n".join(article_list)

        prompt = f"""Score these articles for relevance to fraud prevention, security, and communications platforms.

{combined_articles}

Rate each article 0-10:
- 8-10: Highly relevant (fraud, security breaches, account takeover, telecom/messaging threats)
- 5-7: Moderately relevant (general security, vulnerabilities, compliance)
- 0-4: Low relevance (product updates, general tech news)

DEDUPLICATION (CRITICAL): Aggressively consolidate similar topics:
- If 3+ articles are from the SAME vendor/product (e.g., "Rockwell Automation"), keep ONLY the most critical one
- If articles cover the same incident/breach/advisory, keep ONLY the most detailed
- Mark duplicates with score=0 and "duplicate_of" field
- Examples to consolidate:
  * Multiple vulnerabilities from same vendor on same day → keep 1
  * Same data breach reported by different outlets → keep 1
  * Generic "CISA adds vulnerability" articles → mark as duplicates

CATEGORIZATION:
- telecom: SMS, messaging platforms, SIM swap, robocalls, telecom fraud
- general: Breaches, vulnerabilities, authentication, fraud, security threats

Return JSON:
{{
  "articles": [
    {{"id": 1, "score": 9, "category": "general", "reason": "OAuth breach affects enterprise auth"}},
    {{"id": 2, "score": 0, "duplicate_of": 1, "reason": "Same OAuth incident"}},
    {{"id": 3, "score": 7, "category": "telecom", "reason": "SMS verification fraud"}}
  ]
}}

Only include articles scoring >= 6 unless they're duplicates."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a fraud intelligence analyst. Score articles for relevance to fraud prevention, security threats, and communications platform security. Be strict - only high scores for truly relevant content."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2000
            )

            result = json.loads(response.choices[0].message.content)
            return result.get('articles', [])

        except Exception as e:
            print(f"      ✗ GPT categorization error: {type(e).__name__}: {str(e)[:100]}")
            return []

    def _categorize_content(self, collected_data):
        """
        Categorize collected data using GPT-4o scoring (keyword matching disabled).

        Returns:
            Dictionary with 'telecom', 'general', and 'competitive' keys, each containing articles and posts
        """
        categorized = {
            'telecom': {'articles': [], 'posts': []},
            'general': {'articles': [], 'posts': []},
            'competitive': {'articles': [], 'posts': []}
        }

        # Use GPT-4o to score and categorize articles
        if "rss_articles" in collected_data:
            articles = collected_data["rss_articles"]

            # Always include telecom_fraud source articles
            telecom_source_articles = [a for a in articles if a.get('category') == 'telecom_fraud']
            other_articles = [a for a in articles if a.get('category') != 'telecom_fraud']

            print("    → Using GPT-4o to score and categorize articles...")

            # Score non-telecom-source articles with GPT
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            scored_articles = self._gpt_categorize_articles(client, other_articles)

            # Map scored articles back to original articles
            for score_info in scored_articles:
                article_id = score_info.get('id', 0)
                score = score_info.get('score', 0)
                category = score_info.get('category', 'general')
                is_duplicate = score_info.get('duplicate_of') is not None

                # Skip duplicates and low scores
                if is_duplicate or score < 6:
                    continue

                # Get original article (id is 1-indexed)
                if 1 <= article_id <= len(other_articles):
                    article = other_articles[article_id - 1]
                    article['_gpt_score'] = score
                    article['_gpt_reason'] = score_info.get('reason', '')

                    if category == 'telecom':
                        categorized['telecom']['articles'].append(article)
                    else:
                        categorized['general']['articles'].append(article)

            # Add telecom source articles directly
            categorized['telecom']['articles'].extend(telecom_source_articles)

            print(f"    ✓ GPT scored {len(scored_articles)} articles, kept {len(categorized['telecom']['articles']) + len(categorized['general']['articles'])} (filtered {len(other_articles) - (len(categorized['telecom']['articles']) + len(categorized['general']['articles']) - len(telecom_source_articles))} as low-relevance/duplicates)")

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
            },
            "filtered_articles": categorized['telecom']['articles'] + categorized['general']['articles']
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
            # Filter to only recent posts (last 30 days)
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)

            recent_posts = []
            for post in reddit_posts:
                created = post.get('created_utc')
                if created:
                    try:
                        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        # Make timezone-aware if naive (SocialCrawl returns naive timestamps)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        if dt >= cutoff:
                            recent_posts.append(post)
                    except:
                        pass

            if recent_posts:
                print(f"  → Analyzing Twilio Reddit Community ({len(recent_posts)} recent posts)...")
                analysis["reddit_community_summary"] = self._analyze_reddit_community(
                    client,
                    recent_posts
                )
                print("    ✓ Twilio Reddit Community analysis complete")
            else:
                print("  → No recent Reddit posts (last 30 days) - skipping community analysis")

        # Analyze Competitor Changelogs
        competitor_changelogs = collected_data.get('competitor_changelogs', [])
        if competitor_changelogs:
            print(f"  → Analyzing Competitor Changelogs ({len(competitor_changelogs)} changes)...")
            analysis["competitor_analysis"] = self._analyze_competitor_changelogs(
                client,
                competitor_changelogs
            )
            print("    ✓ Competitor Changelog analysis complete")

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

    def _analyze_competitor_changelogs(self, client, changelogs):
        """
        Analyze competitor changelogs and add business context.
        Returns enriched changelog items with analysis.
        """
        if not changelogs:
            return []

        # Prepare changelog summaries
        changelog_text = "\n\n".join([
            f"[{c['competitor']} {c['product']}] ({c.get('date', 'Unknown')})\n"
            f"Feature: {c.get('title', 'No title')}\n"
            f"Description: {c.get('description', 'No description')}\n"
            f"Type: {c.get('type', 'unknown')}\n"
            f"Relevance: {c.get('relevance_to_fraud', 'unknown')}"
            for c in changelogs[:10]  # Limit to 10 most relevant
        ])

        prompt = f"""Analyze these competitor fraud/security feature releases and provide business context.

{changelog_text}

For each feature, provide a 2-3 sentence analysis answering:
- What does this feature do in practical terms?
- Why would customers want this?
- How does it compare to Twilio's capabilities? (if you can infer)
- What's the competitive implication?

Return JSON object with "features" array:
{{
  "features": [
    {{
      "competitor": "Vonage",
      "product": "Fraud Defender",
      "title": "Network blocks with TTL",
      "analysis": "Allows customers to temporarily block traffic to specific networks without permanent configuration changes. Useful for responding to fraud spikes or attacks with automatic rollback. Twilio currently requires manual rule changes or API calls for similar functionality."
    }}
  ]
}}

Focus on practical business value, not just technical descriptions. Skip features with insufficient information."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a competitive intelligence analyst for Twilio. Provide concise, actionable analysis of competitor features with business context. Write for product managers, not engineers."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1500
            )

            result = json.loads(response.choices[0].message.content)
            return result.get('features', result.get('analysis', []))

        except Exception as e:
            print(f"      ✗ Competitor analysis error: {type(e).__name__}: {str(e)[:100]}")
            return []

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
1. Executive summary (4-5 sentences) - what's happening in {category_name}. Write in news brief style: lead with the key development, then provide context. Include [ARTICLE_N] citations.

2. Top 5 trends or threats specific to {category_name} (if available):
   - REQUIRED FORMAT: {{"title": "Short headline", "description": "4-5 sentences explaining the threat"}}
   - The "description" field is MANDATORY and must contain 4-5 complete sentences
   - Description format: What is it? → Why does it matter? → What's the business impact? → What should teams consider?
   - Citations go in the description text, NOT in the title
   - If you cannot write a meaningful 4-5 sentence description, DO NOT include that item at all
   - NEVER return just a title without a description field
   - NEVER put citations at the end of titles (wrong: "Title [ARTICLE_1].:")

3. Notable incidents, attacks, or regulatory changes:
   - REQUIRED FORMAT: {{"description": "4-5 sentences with full context and citations"}}
   - Each must be 4-5 sentences with [ARTICLE_N] citations

4. Anything requiring immediate attention:
   - REQUIRED FORMAT: {{"description": "4-5 sentences explaining urgency, impact, and recommended action"}}
   - Each must be 4-5 sentences with [ARTICLE_N] citations

5. If Reddit discussions present: key concerns with VERBATIM QUOTES from posts AND comments using [REDDIT_N] citations.
   - Pay special attention to comments as they reveal additional customer pain points, workarounds, and validation of issues
   - Include actual user text snippets in quotes from both posts and comments

CRITICAL RULES:
- Every "description" field must contain 4-5 complete sentences
- Do NOT generate placeholder text like "Title [citation].:" with no explanation
- Skip items entirely if you cannot write proper descriptions
- Put citations INSIDE descriptions, not in titles

Format as JSON with keys: executive_summary, top_trends, regulatory_changes, immediate_attention, community_sentiment (if applicable).

EXAMPLE of correct top_trends format:
"top_trends": [
  {{
    "title": "Synthetic Mule Accounts",
    "description": "Fraudsters are creating sophisticated fake identities to move money [ARTICLE_2]. These accounts pass basic checks but are designed for laundering. This increases financial risk and compliance burden. Companies should enhance identity verification and deploy behavioral analytics to catch these accounts early."
  }}
]"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a fraud intelligence analyst specializing in {category_name}. Write in clear, direct news brief style for product managers and executives. Skip jargon, avoid passive voice, and focus on actionable insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2500
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
