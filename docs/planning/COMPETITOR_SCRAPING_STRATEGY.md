# Competitor Release Notes Scraping Strategy

Most messaging competitors don't have RSS feeds, but publish structured release notes/changelogs. These are MORE valuable than blogs for tracking specific features.

---

## 🎯 Target URLs

### Fraud/Security-Specific Pages

**Vonage:**
- Fraud Defender: https://developer.vonage.com/en/fraud-defender/release-notes
- Verify API: https://developer.vonage.com/en/verify/release-notes
- Main Changelog: https://developer.vonage.com/en/changelog

**MessageBird:**
- Developer Changelog: https://developers.messagebird.com/changelog/
- No specific fraud page, but changelog includes security features

**Plivo:**
- Changelog: https://www.plivo.com/changelog/
- Documentation Updates: Embedded in product docs

**Bandwidth:**
- Release Notes: https://www.bandwidth.com/release-notes/
- Fraud API Changes: Part of main changelog

**Sinch:**
- Changelog: https://developers.sinch.com/changelog/
- Verification Updates: https://developers.sinch.com/docs/verification/release-notes/

---

## 🔧 Technical Approach

### Option 1: Web Scraping (Recommended)

**Pros:**
- Gets structured data from HTML
- Can extract dates, versions, categories
- Works for all competitors

**Cons:**
- Needs per-site scraping logic
- Breaks if they change HTML structure

**Implementation:**

```python
# scripts/collect/changelog_scraper.py

class ChangelogScraper:
    """Scrape competitor release notes and changelogs"""
    
    def __init__(self, config_path="config/competitor-changelogs.json"):
        with open(config_path) as f:
            self.config = json.load(f)
    
    def scrape_vonage_fraud_defender(self):
        """Scrape Vonage Fraud Defender release notes"""
        url = "https://developer.vonage.com/en/fraud-defender/release-notes"
        response = requests.get(url, headers={'User-Agent': '...'})
        soup = BeautifulSoup(response.content, 'html.parser')
        
        releases = []
        
        # Vonage uses <h2> for version, followed by <ul> for changes
        for heading in soup.find_all(['h2', 'h3']):
            # Extract version/date
            version_text = heading.get_text()
            
            # Find next <ul> or <p> for changes
            changes = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h2', 'h3']:
                    break
                if sibling.name == 'ul':
                    changes.extend([li.get_text() for li in sibling.find_all('li')])
                elif sibling.name == 'p':
                    changes.append(sibling.get_text())
            
            if changes:
                releases.append({
                    'competitor': 'Vonage',
                    'product': 'Fraud Defender',
                    'version': version_text,
                    'changes': changes,
                    'url': url,
                    'scraped_at': datetime.now().isoformat()
                })
        
        return releases
    
    def scrape_all(self):
        """Scrape all configured competitor changelogs"""
        all_changes = []
        
        for competitor in self.config['competitors']:
            scraper_method = getattr(self, f"scrape_{competitor['id']}", None)
            if scraper_method:
                try:
                    changes = scraper_method()
                    all_changes.extend(changes)
                except Exception as e:
                    print(f"Error scraping {competitor['name']}: {e}")
        
        return all_changes
```

---

### Option 2: LLM-Powered Extraction (Easiest)

**Pros:**
- Works for ANY changelog format
- No HTML parsing needed
- Adapts to structure changes

**Cons:**
- Uses more OpenAI API credits
- Slower than pure scraping

**Implementation:**

```python
class LLMChangelogExtractor:
    """Use GPT-4 to extract structured data from changelog HTML"""
    
    def extract_changes(self, url, html_content):
        """Extract changes using GPT-4"""
        
        # Truncate HTML to save tokens (keep first 10KB)
        truncated = html_content[:10000]
        
        prompt = f"""Extract release notes from this competitor changelog page.

URL: {url}

HTML Content:
{truncated}

Extract recent changes (last 3 months) and return JSON:
{{
  "releases": [
    {{
      "date": "2026-04-15",
      "version": "v2.3.0",
      "changes": [
        {{
          "type": "feature|bugfix|security",
          "category": "fraud_detection|verification|api|pricing",
          "description": "Added ML-based fraud scoring to Verify API",
          "impact": "high|medium|low"
        }}
      ]
    }}
  ]
}}

Focus on: fraud detection, security, verification, authentication, API changes, pricing.
Ignore: minor bug fixes, internal changes, documentation updates.
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
```

---

### Option 3: Hybrid Approach (Best)

Combine scraping + LLM for best of both worlds:

1. **Scrape** to get HTML sections
2. **LLM** to parse and categorize changes

```python
def hybrid_extract(url):
    # 1. Scrape the page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 2. Find changelog sections (generic)
    sections = []
    for heading in soup.find_all(['h1', 'h2', 'h3']):
        section_html = str(heading)
        for sibling in heading.find_next_siblings():
            if sibling.name in ['h1', 'h2', 'h3']:
                break
            section_html += str(sibling)
        sections.append(section_html)
    
    # 3. Use LLM to parse each section
    all_changes = []
    for section in sections[:10]:  # Limit to recent sections
        changes = llm_parse_section(section)
        all_changes.extend(changes)
    
    return all_changes
```

---

## 📝 Configuration File

**Create:** `config/competitor-changelogs.json`

```json
{
  "competitors": [
    {
      "id": "vonage",
      "name": "Vonage",
      "urls": [
        {
          "url": "https://developer.vonage.com/en/fraud-defender/release-notes",
          "product": "Fraud Defender",
          "scraper": "vonage_structured"
        },
        {
          "url": "https://developer.vonage.com/en/verify/release-notes",
          "product": "Verify API",
          "scraper": "vonage_structured"
        },
        {
          "url": "https://developer.vonage.com/en/changelog",
          "product": "Platform",
          "scraper": "vonage_changelog"
        }
      ]
    },
    {
      "id": "messagebird",
      "name": "MessageBird",
      "urls": [
        {
          "url": "https://developers.messagebird.com/changelog/",
          "product": "Platform",
          "scraper": "generic_llm"
        }
      ]
    },
    {
      "id": "plivo",
      "name": "Plivo",
      "urls": [
        {
          "url": "https://www.plivo.com/changelog/",
          "product": "Platform",
          "scraper": "generic_llm"
        }
      ]
    },
    {
      "id": "bandwidth",
      "name": "Bandwidth",
      "urls": [
        {
          "url": "https://www.bandwidth.com/release-notes/",
          "product": "Platform",
          "scraper": "generic_llm"
        }
      ]
    },
    {
      "id": "sinch",
      "name": "Sinch",
      "urls": [
        {
          "url": "https://developers.sinch.com/changelog/",
          "product": "Platform",
          "scraper": "generic_llm"
        },
        {
          "url": "https://developers.sinch.com/docs/verification/release-notes/",
          "product": "Verification",
          "scraper": "generic_llm"
        }
      ]
    }
  ],
  "extraction_settings": {
    "lookback_days": 90,
    "keywords": [
      "fraud",
      "security",
      "verification",
      "authentication",
      "2FA",
      "OTP",
      "anti-spam",
      "rate limit",
      "abuse prevention"
    ],
    "cache_hours": 168,
    "max_tokens_per_page": 10000
  }
}
```

---

## 🚀 Recommended Implementation

### Phase 1: LLM-Only Approach (Fastest to implement)

**Why:**
- Works for ALL changelog formats
- No HTML parsing logic needed
- Adapts to structure changes
- Easy to add new competitors

**Steps:**

1. **Create scraper:** `scripts/collect/changelog_scraper.py`
2. **Fetch HTML:** Use requests
3. **Extract with GPT-4o:** Send HTML to GPT-4o with extraction prompt
4. **Cache results:** Store for 1 week
5. **Integrate:** Add to main pipeline

**Cost:** ~$0.05-0.10 per week (5 competitors × 2-3 pages each)

---

### Implementation Code

**File:** `scripts/collect/changelog_scraper.py`

```python
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI

class ChangelogScraper:
    def __init__(self, config_path="config/competitor-changelogs.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.cache_dir = Path("data/raw/.changelog_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
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
        
        with open(cache_file) as f:
            cached = json.load(f)
        
        # Check age
        cached_at = datetime.fromisoformat(cached['cached_at'])
        age_hours = (datetime.now() - cached_at).total_seconds() / 3600
        
        cache_limit = self.config['extraction_settings']['cache_hours']
        if age_hours < cache_limit:
            return cached['changes']
        
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
    
    def fetch_and_extract(self, url, competitor_name, product_name):
        """Fetch HTML and extract changes using GPT-4o"""
        
        # Check cache first
        cached = self._get_cached_changes(url)
        if cached:
            print(f"  → Using cached data for {competitor_name} {product_name}")
            return cached
        
        print(f"  → Fetching {url}")
        
        try:
            # Fetch HTML
            response = requests.get(
                url,
                headers={'User-Agent': 'Mozilla/5.0 PM-Radar/1.0'},
                timeout=30
            )
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style tags
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # Get text content
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Truncate to save tokens
            max_tokens = self.config['extraction_settings']['max_tokens_per_page']
            truncated = text_content[:max_tokens * 4]  # Rough char estimate
            
            # Extract with GPT-4o
            changes = self._extract_with_llm(truncated, url, competitor_name, product_name)
            
            # Save to cache
            self._save_to_cache(url, changes)
            
            return changes
            
        except Exception as e:
            print(f"  ✗ Error fetching {url}: {e}")
            return []
    
    def _extract_with_llm(self, content, url, competitor, product):
        """Use GPT-4o to extract structured changelog data"""
        
        keywords = self.config['extraction_settings']['keywords']
        lookback_days = self.config['extraction_settings']['lookback_days']
        
        prompt = f"""Extract recent release notes/changelog entries from this {competitor} {product} page.

URL: {url}

Focus on entries from the last {lookback_days} days related to:
{', '.join(keywords)}

Content:
{content}

Return JSON with this structure:
{{
  "changes": [
    {{
      "date": "2026-04-15",
      "version": "v2.3.0" or null,
      "type": "feature|bugfix|security|deprecation",
      "category": "fraud_detection|verification|api|security|pricing",
      "title": "Added ML-based fraud scoring",
      "description": "Real-time fraud detection using machine learning. Scores each transaction 0-100.",
      "impact": "high|medium|low",
      "relevance_to_fraud": "high|medium|low"
    }}
  ]
}}

Rules:
- Only include fraud/security/verification related changes
- Skip minor bug fixes unrelated to security
- Skip documentation-only updates
- Estimate date if not explicit (look for "last updated", "posted", etc.)
- Set relevance_to_fraud based on how important this is for fraud prevention
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            for change in result.get('changes', []):
                change['competitor'] = competitor
                change['product'] = product
                change['source_url'] = url
            
            return result.get('changes', [])
            
        except Exception as e:
            print(f"  ✗ LLM extraction error: {e}")
            return []
    
    def collect_all(self):
        """Collect from all configured competitors"""
        all_changes = []
        
        print("\n" + "="*60)
        print("COMPETITOR CHANGELOG COLLECTION")
        print("="*60 + "\n")
        
        for competitor in self.config['competitors']:
            print(f"[{competitor['name']}]")
            
            for url_config in competitor['urls']:
                changes = self.fetch_and_extract(
                    url_config['url'],
                    competitor['name'],
                    url_config['product']
                )
                
                print(f"  ✓ Found {len(changes)} relevant changes")
                all_changes.extend(changes)
        
        print(f"\n✓ Total changes collected: {len(all_changes)}")
        
        return all_changes
```

---

### Integration with Main Pipeline

**File:** `scripts/main.py`

```python
# After RSS collection
print("\n[1.2] COMPETITOR CHANGELOG COLLECTION")
print("-" * 70)

from scripts.collect.changelog_scraper import ChangelogScraper

changelog_scraper = ChangelogScraper()
competitor_changes = changelog_scraper.collect_all()

# Add to collected_data
collected_data['competitor_changes'] = competitor_changes
```

---

### Update Analysis

**File:** `scripts/analyze/summarizer.py`

Add method to analyze competitor changes:

```python
def _analyze_competitor_changes(self, client, changes):
    """Analyze competitor changelog entries"""
    
    if not changes:
        return {}
    
    # Group by competitor
    by_competitor = {}
    for change in changes:
        comp = change['competitor']
        if comp not in by_competitor:
            by_competitor[comp] = []
        by_competitor[comp].append(change)
    
    # Format for GPT
    summary_text = ""
    for comp, comp_changes in by_competitor.items():
        summary_text += f"\n{comp}:\n"
        for change in comp_changes:
            summary_text += f"  - [{change['date']}] {change['title']}: {change['description']}\n"
    
    prompt = f"""Analyze these competitor fraud/security changes and create executive summary.

{summary_text}

Return JSON:
{{
  "key_developments": [
    {{
      "competitor": "Vonage",
      "development": "ML-based fraud scoring",
      "significance": "Major competitive threat - similar to Twilio Verify",
      "twilio_action": "Consider highlighting our existing ML capabilities"
    }}
  ],
  "market_trends": [
    {{
      "trend": "Behavioral biometrics adoption",
      "competitors_adopting": ["Sinch", "MessageBird"],
      "market_direction": "Moving beyond SMS to device fingerprinting"
    }}
  ]
}}
"""
    
    # Call GPT-4o...
    # Return analysis
```

---

## 🧪 Testing

```bash
# Test scraper alone
cd ~/Documents/CPM/Experiments/PM\ Radar
python3 -c "
from scripts.collect.changelog_scraper import ChangelogScraper
scraper = ChangelogScraper()
changes = scraper.collect_all()
print(f'Collected {len(changes)} changes')
for c in changes[:3]:
    print(f'- {c[\"competitor\"]}: {c[\"title\"]}')
"
```

---

## 💰 Cost Estimate

- **5 competitors** × **2 URLs each** = 10 pages
- **~500 tokens per page** for extraction = 5K tokens
- **GPT-4o cost**: $0.0025 per 1K input tokens
- **Weekly cost**: ~$0.01-0.02

**Cache saves 99% of costs** after first run!

---

## ✅ Recommendation

**Use LLM-based extraction** because:
1. ✅ Works for ANY changelog format
2. ✅ No HTML parsing maintenance
3. ✅ Easy to add new competitors
4. ✅ Adapts to structure changes
5. ✅ Minimal code (~200 lines)
6. ✅ Very cheap ($0.02/week)

Want me to implement this now?
