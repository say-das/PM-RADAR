"""Content Summarizer - Analyzes collected data using LLM providers

Refactored from v1 scripts/analyze/summarizer.py to use:
- BaseAnalyzer interface
- Prompts from YAML
- Pluggable LLM providers
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from .base import BaseAnalyzer


class ContentSummarizer(BaseAnalyzer):
    """Analyzes and summarizes collected content"""

    def analyze(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected data and generate summaries

        Args:
            collected_data: Dictionary with keys: rss_articles, reddit_posts, competitor_changelogs

        Returns:
            Analysis dictionary with summaries by category
        """
        print("→ Analyzing collected data...")

        # Categorize content
        categorized = self._categorize_content(collected_data)

        telecom_count = len(categorized['telecom']['articles']) + len(categorized['telecom']['posts'])
        general_count = len(categorized['general']['articles']) + len(categorized['general']['posts'])
        competitive_count = len(categorized['competitive']['articles']) + len(categorized['competitive']['posts'])

        print(f"  ✓ Telecom Fraud: {telecom_count} items")
        print(f"  ✓ General Fraud: {general_count} items")
        print(f"  ✓ Competitive Intelligence: {competitive_count} items")

        analysis = {
            "analyzed_at": datetime.now().isoformat(),
            "telecom_fraud_summary": None,
            "general_fraud_summary": None,
            "competitive_intelligence_summary": None,
            "reddit_community_summary": None,
            "competitor_analysis": None,
            "categorized_counts": {
                "telecom": telecom_count,
                "general": general_count,
                "competitive": competitive_count
            },
            "filtered_articles": categorized['telecom']['articles'] + categorized['general']['articles']
        }

        # Analyze each category
        if telecom_count > 0:
            print("→ Analyzing Telecom Fraud content...")
            analysis["telecom_fraud_summary"] = self._analyze_category(
                categorized['telecom'],
                "Telecom Fraud"
            )
            print("  ✓ Telecom Fraud analysis complete")

        if general_count > 0:
            print("→ Analyzing General Fraud content...")
            analysis["general_fraud_summary"] = self._analyze_category(
                categorized['general'],
                "General Fraud & Security"
            )
            print("  ✓ General Fraud analysis complete")

        if competitive_count > 0:
            print("→ Analyzing Competitive Intelligence...")
            analysis["competitive_intelligence_summary"] = self._analyze_competitive(
                categorized['competitive']
            )
            print("  ✓ Competitive analysis complete")

        # Analyze Reddit community discussions
        reddit_posts = collected_data.get('reddit_posts', [])
        if reddit_posts:
            recent_posts = self._filter_recent_posts(reddit_posts, days=30)
            if recent_posts:
                print(f"→ Analyzing Reddit Community ({len(recent_posts)} posts)...")
                analysis["reddit_community_summary"] = self._analyze_reddit_community(recent_posts)
                print("  ✓ Reddit analysis complete")

        # Analyze competitor changelogs
        competitor_changelogs = collected_data.get('competitor_changelogs', [])
        if competitor_changelogs:
            print(f"→ Analyzing Competitor Changelogs ({len(competitor_changelogs)} changes)...")
            analysis["competitor_analysis"] = self._analyze_competitor_changelogs(competitor_changelogs)
            print("  ✓ Changelog analysis complete")

        return analysis

    def _categorize_content(self, collected_data: Dict[str, Any]) -> Dict[str, Dict[str, List]]:
        """Categorize content using GPT scoring

        Returns:
            Dictionary with 'telecom', 'general', 'competitive' keys
        """
        categorized = {
            'telecom': {'articles': [], 'posts': []},
            'general': {'articles': [], 'posts': []},
            'competitive': {'articles': [], 'posts': []}
        }

        articles = collected_data.get("rss_articles", [])
        if not articles:
            return categorized

        # Separate telecom_fraud source articles (auto-include)
        telecom_source_articles = [a for a in articles if a.get('category') == 'telecom_fraud']
        other_articles = [a for a in articles if a.get('category') != 'telecom_fraud']

        print("  → Using LLM to score and categorize articles...")

        # Score other articles with LLM
        scored_articles = self._gpt_categorize_articles(other_articles)

        # Add scored articles to categories
        for score_info in scored_articles:
            article_id = score_info.get('id', 0)
            score = score_info.get('score', 0)
            category = score_info.get('category', 'general')
            is_duplicate = score_info.get('duplicate_of') is not None

            if is_duplicate or score < 6:
                continue

            if 1 <= article_id <= len(other_articles):
                article = other_articles[article_id - 1]
                article['_gpt_score'] = score
                article['_gpt_reason'] = score_info.get('reason', '')

                if category == 'telecom':
                    categorized['telecom']['articles'].append(article)
                else:
                    categorized['general']['articles'].append(article)

        # Add telecom source articles
        categorized['telecom']['articles'].extend(telecom_source_articles)

        return categorized

    def _gpt_categorize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use LLM to score and categorize articles"""
        if not articles:
            return []

        # Prepare article list for LLM
        article_list = []
        for i, article in enumerate(articles, 1):
            article_list.append(
                f"Article {i}:\n"
                f"Title: {article['title']}\n"
                f"Source: {article['source']}\n"
                f"Summary: {article['summary'][:300]}...\n"
            )

        combined_articles = "\n".join(article_list)

        # Get categorization prompt from YAML
        prompt_template = self.prompts.get('categorization', '')
        prompt = f"{prompt_template}\n\n{combined_articles}"

        system_prompt = "You are a fraud intelligence analyst. Score articles for relevance to fraud prevention, security threats, and communications platform security. Be strict - only high scores for truly relevant content."

        try:
            response = self.llm_provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format="json",
                temperature=0.2,
                max_tokens=2000
            )

            result = json.loads(response)
            return result.get('articles', [])

        except Exception as e:
            print(f"    ✗ LLM categorization error: {type(e).__name__}: {str(e)[:100]}")
            return []

    def _analyze_category(self, category_data: Dict[str, List], category_name: str) -> str:
        """Analyze a content category"""
        articles = category_data['articles']
        posts = category_data['posts']

        if not articles and not posts:
            return None

        # Prepare content for analysis
        content_parts = []

        if articles:
            article_text = "\n\n".join([
                f"[{i+1}] [{a['source']}] {a['title']}\nPublished: {a['published']}\nSummary: {a['summary']}"
                for i, a in enumerate(articles[:20])
            ])
            content_parts.append(f"ARTICLES:\n{article_text}")

        if posts:
            post_text = "\n\n".join([
                f"[REDDIT] r/{p['subreddit']} - {p['title']}\nScore: {p['score']} | Comments: {p['num_comments']}\nText: {p['selftext'][:200]}"
                for p in posts[:10]
            ])
            content_parts.append(f"SOCIAL DISCUSSIONS:\n{post_text}")

        combined_content = "\n\n---\n\n".join(content_parts)

        # Get analysis prompt based on category
        if "Telecom" in category_name:
            prompt_template = self.prompts.get('analysis', {}).get('telecom_fraud', '')
        else:
            prompt_template = self.prompts.get('analysis', {}).get('general_fraud', '')

        prompt = f"{prompt_template}\n\n{combined_content}"

        system_prompt = f"You are a security analyst specializing in {category_name}. Analyze the provided content and identify key threats, trends, and actionable insights."

        try:
            response = self.llm_provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2000
            )

            return response

        except Exception as e:
            print(f"    ✗ Analysis error: {type(e).__name__}: {str(e)[:100]}")
            return None

    def _analyze_competitive(self, category_data: Dict[str, List]) -> str:
        """Analyze competitive intelligence"""
        articles = category_data['articles']

        if not articles:
            return None

        article_text = "\n\n".join([
            f"[{a['source']}] {a['title']}\nPublished: {a['published']}\nSummary: {a['summary']}"
            for a in articles[:20]
        ])

        prompt_template = self.prompts.get('competitive_intel', '')
        prompt = f"{prompt_template}\n\n{article_text}"

        system_prompt = "You are a competitive intelligence analyst specializing in fraud prevention and security features for messaging platforms."

        try:
            response = self.llm_provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1500
            )

            return response

        except Exception as e:
            print(f"    ✗ Competitive analysis error: {type(e).__name__}: {str(e)[:100]}")
            return None

    def _analyze_reddit_community(self, posts: List[Dict[str, Any]]) -> str:
        """Analyze Reddit community discussions"""
        post_text = "\n\n".join([
            f"[{i+1}] r/{p['subreddit']} - {p['title']}\n"
            f"Score: {p['score']} | Comments: {p['num_comments']}\n"
            f"Content: {p['selftext'][:300]}"
            for i, p in enumerate(posts[:15])
        ])

        prompt_template = self.prompts.get('reddit_community', '')
        prompt = f"{prompt_template}\n\n{post_text}"

        system_prompt = "You are a community analyst tracking customer feedback and product discussions on social platforms."

        try:
            response = self.llm_provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1000
            )

            return response

        except Exception as e:
            print(f"    ✗ Reddit analysis error: {type(e).__name__}: {str(e)[:100]}")
            return None

    def _analyze_competitor_changelogs(self, changelogs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze competitor changelogs (stub - returns raw data)"""
        # NOTE: Full changelog analysis deferred - return raw data for now
        return changelogs

    def _filter_recent_posts(self, posts: List[Dict[str, Any]], days: int = 30) -> List[Dict[str, Any]]:
        """Filter posts to recent timeframe"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        recent = []

        for post in posts:
            created = post.get('created_utc')
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if dt >= cutoff:
                        recent.append(post)
                except:
                    pass

        return recent
