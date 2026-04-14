# PM Radar MVP - Project Structure

**Version:** 1.0
**Last Updated:** 2026-04-03

---

## Directory Structure

```
pm-radar/
├── .github/
│   └── workflows/
│       └── weekly-collection.yml        # GitHub Actions workflow (runs Monday 6am)
│
├── config/
│   ├── rss-sources.json                 # List of RSS feed URLs
│   ├── reddit-config.json               # Reddit queries and subreddits
│   ├── competitors.json                 # Competitor list (for discovery agent)
│   ├── email-config.json                # Email recipients, settings
│   └── secrets.example.env              # Template for API keys (not committed)
│
├── scripts/
│   ├── collect/
│   │   ├── __init__.py
│   │   ├── rss_collector.py             # RSS feed collection
│   │   ├── reddit_collector.py          # Reddit API collection
│   │   └── competitor_discovery.py      # Claude agent for site mapping
│   │
│   ├── analyze/
│   │   ├── __init__.py
│   │   ├── summarizer.py                # OpenAI GPT-4 analysis
│   │   ├── theme_detector.py            # Group by themes
│   │   └── anomaly_detector.py          # Detect unusual patterns
│   │
│   ├── deliver/
│   │   ├── __init__.py
│   │   ├── email_sender.py              # Brevo email delivery
│   │   └── report_formatter.py          # Format markdown reports
│   │
│   └── main.py                          # Orchestration script (entry point)
│
├── data/
│   ├── raw/                             # Raw collected data (JSON)
│   │   └── 2026-04-07.json
│   │
│   ├── reports/                         # Weekly analysis reports (Markdown)
│   │   └── 2026-04-07.md
│   │
│   ├── competitor-maps/                 # Competitor site structure maps
│   │   ├── sinch.json
│   │   └── vonage.json
│   │
│   └── archive/                         # Historical data (for trending)
│       └── README.md
│
├── templates/
│   └── email-template.html              # HTML email template
│
├── tests/
│   ├── test_rss_collector.py
│   ├── test_reddit_collector.py
│   └── test_summarizer.py
│
├── docs/
│   ├── setup-guide.md                   # Setup instructions
│   ├── api-access.md                    # How to get API keys
│   └── troubleshooting.md               # Common issues
│
├── .gitignore                           # Ignore secrets, cache
├── requirements.txt                     # Python dependencies
├── README.md                            # Project overview
└── LICENSE
```

---

## Key Files Explained

### 1. GitHub Actions Workflow

**File:** `.github/workflows/weekly-collection.yml`

```yaml
name: Weekly Product Intelligence Collection

on:
  schedule:
    - cron: '0 6 * * 1'  # Monday 6am UTC
  workflow_dispatch:      # Manual trigger for testing

jobs:
  collect-analyze-deliver:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run collection pipeline
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
          BREVO_API_KEY: ${{ secrets.BREVO_API_KEY }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: python scripts/main.py

      - name: Commit data
        run: |
          git config user.name "PM Radar Bot"
          git config user.email "radar@twilio.com"
          git add data/
          git commit -m "Weekly collection: $(date +'%Y-%m-%d')" || echo "No changes"
          git push
```

---

### 2. Configuration Files

#### **config/rss-sources.json**

```json
{
  "sources": [
    {
      "name": "Telecom Reseller",
      "url": "https://telecomreseller.com/feed/",
      "category": "industry_news"
    },
    {
      "name": "Fierce Wireless",
      "url": "https://www.fiercewireless.com/rss",
      "category": "industry_news"
    },
    {
      "name": "Light Reading",
      "url": "https://www.lightreading.com/rss",
      "category": "industry_news"
    },
    {
      "name": "Sinch Blog",
      "url": "https://www.sinch.com/blog/feed/",
      "category": "competitor"
    }
  ]
}
```

#### **config/reddit-config.json**

```json
{
  "queries": [
    {
      "query": "Twilio SMS pumping",
      "timeframe": "week",
      "limit": 50,
      "subreddits": "all"
    }
  ],
  "user_agent": "TwilioProductResearch/1.0"
}
```

#### **config/competitors.json**

```json
{
  "competitors": [
    {
      "name": "Sinch",
      "domain": "sinch.com",
      "discovered": false,
      "last_discovery": null
    },
    {
      "name": "Vonage",
      "domain": "vonage.com",
      "discovered": false,
      "last_discovery": null
    }
  ]
}
```

#### **config/email-config.json**

```json
{
  "sender": {
    "email": "radar@twilio.com",
    "name": "PM Radar"
  },
  "recipients": [
    {
      "email": "pm@twilio.com",
      "name": "Product Manager"
    }
  ],
  "subject_template": "Weekly Intelligence Digest - {date}"
}
```

---

### 3. Main Orchestration Script

**File:** `scripts/main.py`

```python
"""
PM Radar MVP - Main Orchestration Script
Runs weekly collection, analysis, and delivery pipeline.
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Import collectors
from collect.rss_collector import RSSCollector
from collect.reddit_collector import RedditCollector
from collect.competitor_discovery import CompetitorDiscoveryAgent

# Import analyzers
from analyze.summarizer import ContentAnalyzerAgent
from analyze.theme_detector import ThemeDetector

# Import delivery
from deliver.email_sender import EmailSender
from deliver.report_formatter import ReportFormatter


def main():
    print("=" * 60)
    print("PM RADAR - WEEKLY INTELLIGENCE COLLECTION")
    print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    # 1. COLLECTION PHASE
    print("\n[1/4] COLLECTING DATA...")
    collected_data = {}

    # RSS feeds
    print("  → Collecting RSS feeds...")
    rss_collector = RSSCollector("config/rss-sources.json")
    collected_data["rss_articles"] = rss_collector.collect()
    print(f"    ✓ Collected {len(collected_data['rss_articles'])} articles")

    # Reddit
    print("  → Collecting Reddit posts...")
    reddit_collector = RedditCollector("config/reddit-config.json")
    collected_data["reddit_posts"] = reddit_collector.collect()
    print(f"    ✓ Collected {len(collected_data['reddit_posts'])} posts")

    # Source Discovery Agent (Phase 2 - runs monthly)
    print("  → Checking for new sources (Source Discovery Agent)...")
    # Note: Source Discovery Agent will be implemented in Phase 2
    # Will automatically discover competitor URLs, analyst RSS feeds, community sources
    print(f"    ⚠ Source Discovery Agent not yet implemented")

    # Save raw data
    date_str = datetime.now().strftime('%Y-%m-%d')
    raw_data_path = f"data/raw/{date_str}.json"
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    with open(raw_data_path, 'w') as f:
        json.dump(collected_data, f, indent=2)
    print(f"  → Raw data saved: {raw_data_path}")

    # 2. ANALYSIS PHASE
    print("\n[2/4] ANALYZING DATA...")

    # Content Analysis
    print("  → Running Content Analyzer Agent...")
    analyzer = ContentAnalyzerAgent()
    summaries = analyzer.analyze(collected_data)
    print(f"    ✓ Generated summaries")

    # Detect themes
    print("  → Detecting themes...")
    theme_detector = ThemeDetector()
    themes = theme_detector.detect(collected_data)
    print(f"    ✓ Found {len(themes)} themes")

    # 3. REPORT GENERATION
    print("\n[3/4] GENERATING REPORT...")
    formatter = ReportFormatter()
    report = formatter.format(
        summaries=summaries,
        themes=themes,
        date=date_str
    )

    # Save markdown report
    report_path = f"data/reports/{date_str}.md"
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"  → Report saved: {report_path}")

    # 4. DELIVERY
    print("\n[4/4] DELIVERING REPORT...")
    email_sender = EmailSender("config/email-config.json")
    result = email_sender.send(
        subject=f"Weekly Intelligence Digest - {date_str}",
        report_markdown=report
    )

    if result["success"]:
        print(f"  ✓ Email sent to {len(result['recipients'])} recipients")
    else:
        print(f"  ✗ Email delivery failed: {result['error']}")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

---

### 4. Sample Collector: RSS

**File:** `scripts/collect/rss_collector.py`

```python
"""
RSS Feed Collector
Fetches and parses RSS feeds from configured sources.
"""

import json
import feedparser
from datetime import datetime, timedelta


class RSSCollector:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = json.load(f)

    def collect(self):
        """Collect articles from all RSS sources."""
        articles = []
        cutoff_date = datetime.now() - timedelta(days=7)

        for source in self.config["sources"]:
            try:
                feed = feedparser.parse(source["url"])

                for entry in feed.entries:
                    # Parse date
                    pub_date = datetime(*entry.published_parsed[:6])

                    # Only include articles from last 7 days
                    if pub_date < cutoff_date:
                        continue

                    articles.append({
                        "source": source["name"],
                        "category": source["category"],
                        "title": entry.title,
                        "url": entry.link,
                        "published": pub_date.isoformat(),
                        "summary": entry.get("summary", "")[:500]
                    })

            except Exception as e:
                print(f"    ✗ Error collecting from {source['name']}: {e}")
                continue

        return articles
```

---

### 5. Python Dependencies

**File:** `requirements.txt`

```txt
# Core
python-dotenv==1.0.0

# Data collection
feedparser==6.0.10              # RSS feeds
praw==7.7.1                     # Reddit API
beautifulsoup4==4.12.2          # Web scraping (future)
requests==2.31.0

# AI/Analysis
openai==1.12.0                  # OpenAI GPT-4o (Content Analyzer Agent)
anthropic==0.18.1               # Claude SDK (for AI agents)
boto3==1.34.0                   # AWS SDK (if using Bedrock for agents)

# Email delivery
sib-api-v3-sdk==7.6.0           # Brevo email

# Utilities
python-dateutil==2.8.2
```

---

### 6. Environment Variables

**File:** `.env.example` (copy to `.env` locally, never commit `.env`)

```bash
# OpenAI (for analysis)
OPENAI_API_KEY=sk-...

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Brevo Email
BREVO_API_KEY=xkeysib-...

# AWS (if using Claude via Bedrock)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Optional: SociaVault (alternative to Reddit API)
# SOCIAVAULT_API_KEY=sk_live_...
```

---

### 7. .gitignore

**File:** `.gitignore`

```
# Secrets
.env
*.key
config/secrets/

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
venv/
env/

# Data (optional - you may want to commit data/)
# data/raw/*.json
# data/reports/*.md

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

---

## Setup Steps

### Step 1: Repository Setup

```bash
# Create new repo
git clone <your-repo-url>
cd pm-radar

# Create directory structure
mkdir -p .github/workflows config scripts/{collect,analyze,deliver} data/{raw,reports,competitor-maps,archive} templates tests docs

# Create initial files
touch scripts/__init__.py
touch scripts/collect/__init__.py
touch scripts/analyze/__init__.py
touch scripts/deliver/__init__.py
```

### Step 2: Configuration

```bash
# Copy example configs
cp .env.example .env

# Edit .env with your API keys
nano .env

# Edit config files
nano config/rss-sources.json
nano config/reddit-config.json
nano config/competitors.json
nano config/email-config.json
```

### Step 3: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 4: Local Testing

```bash
# Test individual collectors
python -m scripts.collect.rss_collector
python -m scripts.collect.reddit_collector

# Test full pipeline
python scripts/main.py
```

### Step 5: GitHub Actions Setup

```bash
# Add secrets to GitHub repo (Settings → Secrets → Actions)
# - OPENAI_API_KEY
# - REDDIT_CLIENT_ID
# - REDDIT_CLIENT_SECRET
# - BREVO_API_KEY
# - AWS_ACCESS_KEY_ID (if using Bedrock)
# - AWS_SECRET_ACCESS_KEY (if using Bedrock)

# Push to GitHub
git add .
git commit -m "Initial PM Radar MVP setup"
git push
```

### Step 6: First Run

```bash
# Trigger manual run via GitHub Actions
# Go to: Actions → Weekly Product Intelligence Collection → Run workflow

# Or test locally first
python scripts/main.py
```

---

## Data Flow Summary

```
Monday 6am UTC
     ↓
GitHub Actions triggers
     ↓
main.py runs
     ↓
┌──────────────────────────────────┐
│ 1. COLLECT                       │
│ ├─ RSS feeds → 32 articles       │
│ ├─ Reddit → 15 posts             │
│ └─ Competitors → 2 site maps     │
│    (one-time)                    │
└──────────────────────────────────┘
     ↓
Save: data/raw/2026-04-07.json
     ↓
┌──────────────────────────────────┐
│ 2. ANALYZE (OpenAI)              │
│ ├─ Summarize each article        │
│ ├─ Group by themes               │
│ └─ Detect patterns               │
└──────────────────────────────────┘
     ↓
┌──────────────────────────────────┐
│ 3. GENERATE REPORT               │
│ └─ Format as markdown            │
└──────────────────────────────────┘
     ↓
Save: data/reports/2026-04-07.md
     ↓
┌──────────────────────────────────┐
│ 4. DELIVER (Brevo)               │
│ └─ Send email with report        │
└──────────────────────────────────┘
     ↓
Email arrives: pm@twilio.com
```

---

## MVP Feature Checklist

- [ ] RSS collection from 10+ sources
- [ ] Reddit search (1 query)
- [ ] Source Discovery Agent (Phase 2 - finds competitor URLs)
- [ ] Content Analyzer Agent (GPT-4o for analysis)
- [ ] Theme grouping
- [ ] Weekly email delivery (Brevo)
- [ ] GitHub Actions automation
- [ ] Data storage (JSON + Markdown)
- [ ] Basic error handling

---

## Next: What to Build First?

1. **Core scripts** (`rss_collector.py`, `reddit_collector.py`)
2. **Main orchestration** (`main.py`)
3. **GitHub Actions workflow** (`.github/workflows/weekly-collection.yml`)
4. **Email delivery** (`email_sender.py`)
5. **Source Discovery Agent** (`source_discovery_agent.py` - Phase 2)

Which would you like to start with?
