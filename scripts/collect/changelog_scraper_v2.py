"""
Competitor Changelog Scraper v2
Uses Playwright for JavaScript-rendered pages + GPT-4o for extraction
Handles both static HTML and dynamic JavaScript content
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI


class ChangelogScraperV2:
    """
    Scraper that uses Playwright for JS rendering + GPT-4o for extraction.
    Falls back to requests for simple pages.
    """

    def __init__(self, config_path="config/competitor-changelogs.json"):
        """Initialize changelog scraper with configuration."""
        with open(config_path) as f:
            self.config = json.load(f)

        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=self.api_key)
        self.cache_dir = Path("data/raw/.changelog_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Check if Playwright is available
        self.use_playwright = self._check_playwright()

    def _check_playwright(self):
        """Check if Playwright is installed"""
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            print("⚠️  Playwright not installed - falling back to requests")
            print("   Install with: pip install playwright && playwright install")
            return False

    def _get_cache_key(self, url):
        """Generate cache key from URL"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()

    def _get_cached_changes(self, url):
        """Check cache for recent extraction"""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                cached = json.load(f)

            # Check age
            cached_at = datetime.fromisoformat(cached['cached_at'])
            age_hours = (datetime.now() - cached_at).total_seconds() / 3600

            cache_limit = self.config['extraction_settings']['cache_hours']

            # Auto-delete cache older than 2 weeks
            if age_hours >= 336:  # 14 days
                print(f"      → Cache too old ({age_hours/24:.0f} days), deleting")
                cache_file.unlink()
                return None

            if age_hours < cache_limit:
                print(f"      → Using cache (age: {age_hours:.1f} hours)")
                return cached['changes']

            print(f"      → Cache expired (age: {age_hours:.1f} hours)")
            return None

        except Exception as e:
            print(f"      → Cache error: {e}")
            return None

    def _save_to_cache(self, url, changes):
        """Save extracted changes to cache"""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with open(cache_file, 'w') as f:
            json.dump({
                'url': url,
                'cached_at': datetime.now().isoformat(),
                'changes': changes
            }, f, indent=2)

    def _fetch_with_playwright(self, url):
        """Fetch page content using Playwright (handles JS rendering)"""
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                # Launch browser (headless)
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Set user agent
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) PM-Radar/1.0'
                })

                # Navigate and wait for network to be idle
                page.goto(url, wait_until='networkidle', timeout=30000)

                # Wait a bit more for any lazy-loaded content
                page.wait_for_timeout(2000)

                # Get rendered HTML
                content = page.content()

                # Extract text content
                text_content = page.evaluate('document.body.innerText')

                browser.close()

                return text_content

        except Exception as e:
            raise Exception(f"Playwright error: {str(e)[:100]}")

    def _fetch_with_requests(self, url):
        """Fetch page content using requests (for simple HTML)"""
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) PM-Radar/1.0'},
            timeout=30,
            verify=False
        )
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()

        # Get text content
        return soup.get_text(separator='\n', strip=True)

    def fetch_and_extract(self, url, competitor_name, product_name, scrape_mode="keyword_filter"):
        """Fetch HTML and extract changes using Playwright + GPT-4o"""

        mode_label = "FULL" if scrape_mode == "full" else "FILTERED"
        method = "Playwright" if self.use_playwright else "Requests"
        print(f"  [{product_name}] ({mode_label} via {method})")

        # Check cache first
        cached = self._get_cached_changes(url)
        if cached is not None:
            return cached

        print(f"    → Fetching {url}")

        try:
            # Fetch content (try Playwright first, fallback to requests)
            if self.use_playwright:
                try:
                    print(f"    → Rendering with Playwright...")
                    text_content = self._fetch_with_playwright(url)
                except Exception as e:
                    print(f"    ⚠️  Playwright failed: {str(e)[:50]}, trying requests...")
                    text_content = self._fetch_with_requests(url)
            else:
                print(f"    → Parsing HTML...")
                text_content = self._fetch_with_requests(url)

            # Truncate to save tokens
            max_tokens = self.config['extraction_settings']['max_tokens_per_page']
            truncated = text_content[:max_tokens * 4]  # Rough char estimate

            print(f"    → Extracting with GPT-4o ({len(truncated)} chars)...")

            # Extract with GPT-4o
            changes = self._extract_with_llm(truncated, url, competitor_name, product_name, scrape_mode)

            print(f"    ✓ Extracted {len(changes)} changes")

            # Save to cache
            self._save_to_cache(url, changes)

            return changes

        except Exception as e:
            print(f"    ✗ Error: {type(e).__name__}: {str(e)[:100]}")
            return []

    def _extract_with_llm(self, content, url, competitor, product, scrape_mode="keyword_filter"):
        """Use GPT-4o to extract structured changelog data"""

        keywords = self.config['extraction_settings']['keywords']
        lookback_days = self.config['extraction_settings']['lookback_days']
        cutoff_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

        # Adjust prompt based on scrape mode
        if scrape_mode == "full":
            focus_instruction = """Extract ALL release notes and changes from this page.
This is a fraud/security-specific product, so all updates are relevant."""
            filter_instruction = "Include ALL changes - features, bug fixes, API updates, pricing, etc."
        else:
            focus_instruction = f"""Focus on entries from {cutoff_date} onwards (last {lookback_days} days) related to:
- Fraud detection and prevention
- Security features and updates
- Verification and authentication
- Anti-spam and abuse prevention
- API security changes
- Pricing changes for fraud services"""
            filter_instruction = "Only include changes related to fraud, security, verification, or authentication"

        prompt = f"""Extract recent release notes from this {competitor} {product} changelog page.

URL: {url}

{focus_instruction}

Content:
{content}

Return JSON with this structure:
{{
  "changes": [
    {{
      "date": "2026-04-15",
      "version": "v2.3.0" or null if no version,
      "type": "feature|bugfix|security|deprecation|pricing",
      "category": "fraud_detection|verification|api_security|anti_spam|pricing|authentication",
      "title": "Added ML-based fraud scoring",
      "description": "Real-time fraud detection using machine learning. Scores each verification attempt 0-100 based on device signals and behavior patterns.",
      "impact": "high|medium|low",
      "relevance_to_fraud": "high|medium|low"
    }}
  ]
}}

IMPORTANT:
- {filter_instruction}
- Skip: changes older than {cutoff_date}
- Estimate date if not explicit (look for "last updated", "posted", timestamps)
- Set "relevance_to_fraud" based on importance for fraud prevention
  - high: Direct fraud/security features
  - medium: Related features (verification, auth, API security)
  - low: Tangentially related (performance, UX improvements)
- If no relevant changes found, return {{"changes": []}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            result = json.loads(response.choices[0].message.content)

            # Add metadata to each change
            for change in result.get('changes', []):
                change['competitor'] = competitor
                change['product'] = product
                change['source_url'] = url
                change['extracted_at'] = datetime.now().isoformat()

            return result.get('changes', [])

        except Exception as e:
            print(f"      ✗ LLM extraction error: {type(e).__name__}: {str(e)[:100]}")
            return []

    def collect_all(self):
        """Collect from all configured competitors"""
        all_changes = []

        print("\n" + "="*70)
        print("COMPETITOR CHANGELOG COLLECTION (V2 - Playwright)")
        print("="*70 + "\n")

        for competitor in self.config['competitors']:
            print(f"[{competitor['name']}]")

            for url_config in competitor['urls']:
                if not url_config.get('enabled', True):
                    print(f"  [{url_config['product']}] (disabled)")
                    continue

                scrape_mode = url_config.get('scrape_mode', 'keyword_filter')
                changes = self.fetch_and_extract(
                    url_config['url'],
                    competitor['name'],
                    url_config['product'],
                    scrape_mode
                )

                all_changes.extend(changes)

            print()

        # Filter by relevance
        high_relevance = [c for c in all_changes if c.get('relevance_to_fraud') == 'high']

        print(f"✓ Total changes collected: {len(all_changes)}")
        print(f"  - High relevance: {len(high_relevance)}")

        # Sort by date (newest first)
        all_changes.sort(key=lambda x: x.get('date', '1900-01-01'), reverse=True)

        return all_changes


def main():
    """Test the changelog scraper v2"""
    from dotenv import load_dotenv
    load_dotenv()

    scraper = ChangelogScraperV2()
    changes = scraper.collect_all()

    print("\n" + "="*70)
    print("SAMPLE RESULTS")
    print("="*70 + "\n")

    for change in changes[:5]:
        print(f"{change['competitor']} - {change['product']}")
        print(f"  Date: {change.get('date', 'Unknown')}")
        print(f"  Type: {change.get('type', 'Unknown')}")
        print(f"  Title: {change.get('title', 'No title')}")
        print(f"  Description: {change.get('description', 'No description')[:100]}...")
        print(f"  Relevance: {change.get('relevance_to_fraud', 'Unknown')}")
        print()


if __name__ == '__main__':
    main()
