# PM Radar - Intelligence Digest Platform

**Automated intelligence gathering and reporting platform for product and security teams.**

PM Radar collects, analyzes, and delivers curated intelligence reports from multiple sources including RSS feeds, Reddit communities, and competitor changelogs.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- API Keys:
  - OpenAI API key (for analysis)
  - Brevo API key (for email delivery)
  - SocialCrawl API key (for Reddit data, optional)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd "PM Radar"

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys
```

### Run Your First Report

```bash
# Run the fraud intelligence topic
python3 scripts/run_v2_pipeline.py fraud

# Output will be saved to:
# - data/reports/YYYY-MM-DD.md (markdown)
# - data/reports/YYYY-MM-DD.html (HTML, if email sent)
```

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Topics](#topics)
  - [Adding a New Topic](#adding-a-new-topic)
  - [Deleting a Topic](#deleting-a-topic)
  - [Configuring a Topic](#configuring-a-topic)
- [Running Reports](#running-reports)
- [Report Sections](#report-sections)
- [Forking & Customization](#forking--customization)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

---

## 🏗️ Architecture

```
PM Radar Pipeline:

┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  COLLECT    │ -> │ ANALYZE  │ -> │  REPORT  │ -> │ DELIVER  │
└─────────────┘    └──────────┘    └──────────┘    └──────────┘
     │                  │                │               │
     v                  v                v               v
  RSS Feeds        OpenAI GPT       Markdown          Email
  Reddit           Categorize       HTML              (Brevo)
  Changelogs       Summarize        Sections
                   Citations        Citations
```

### Core Components

- **Collectors** (`core/collectors/`) - Gather data from sources
- **Analyzers** (`core/analyzers/`) - Process with LLMs
- **Reporters** (`core/reporters/`) - Generate formatted reports
- **Deliverers** (`scripts/deliver/`) - Send via email/other channels

### V2 Architecture Features

- ✅ Multiple topics in one platform
- ✅ Pluggable LLM providers (OpenAI, Anthropic)
- ✅ Section-based report generation
- ✅ YAML-driven configuration
- ✅ Automatic health checks
- ✅ Graceful error handling

---

## 📊 Topics

A **topic** is a focused area of intelligence gathering. Each topic has its own:
- Configuration (sources, prompts, sections)
- Data storage (`data/raw/`)
- Reports (`data/reports/`)

### Current Topics

| Topic ID | Name | Sources | Status |
|----------|------|---------|--------|
| `fraud` | Fraud & Security Intelligence | RSS, Reddit, Changelogs | ✅ Active |

### Adding a New Topic

Create a new intelligence topic in 5 steps:

#### Step 1: Create Topic Directory

```bash
mkdir -p config/topics/your-topic-id
```

#### Step 2: Create Topic Configuration

Create `config/topics/your-topic-id/topic.yaml`:

```yaml
# Topic Configuration
id: your-topic-id
name: "Your Topic Name"
enabled: true
feature_flag_v2: true  # Use v2 pipeline

# LLM Configuration
llm:
  provider: openai      # or "anthropic"
  model: gpt-4o
  api_key_env: OPENAI_API_KEY

# Data Sources
sources:
  - type: rss
    config_path: rss.yaml
  - type: reddit
    api_key_env: SOCIALCRAWL_API_KEY
    config_path: reddit.yaml
  - type: changelog
    config_path: changelogs.yaml

# Analysis Categories
categories:
  - your_category_1
  - your_category_2

# Prompts Configuration
prompts_path: prompts.yaml

# Report Configuration
report:
  sections:
    - type: executive_summary
    
    - type: top_items
      config:
        title: "🔴 Top Category 1 Items"
        category: "your_category_1"
        limit: 5
    
    - type: top_items
      config:
        title: "🟡 Category 2 Items"
        category: "your_category_2"
        limit: 3
    
    - type: reddit_community
      config:
        title: "## Community Discussions"
    
    - type: competitive_intel
      config:
        title: "## Competition Watch"
    
    - type: sources

# Email Recipients
email:
  recipients:
    - your-email@example.com
```

#### Step 3: Configure Sources

**RSS Sources** (`config/topics/your-topic-id/rss.yaml`):
```yaml
feeds:
  - url: https://example.com/feed.xml
    category: security_news
    enabled: true
    
  - url: https://example.com/blog/feed
    category: industry_news
    enabled: true
```

**Reddit Sources** (`config/topics/your-topic-id/reddit.yaml`):
```yaml
subreddits:
  - name: YourSubreddit
    post_limit: 10
    time_filter: week  # hour, day, week, month, year, all
```

**Competitor Changelogs** (`config/topics/your-topic-id/changelogs.yaml`):
```yaml
competitors:
  - name: CompetitorA
    url: https://competitor-a.com/changelog
    selector: ".changelog-item"  # CSS selector
    enabled: true
```

#### Step 4: Create Analysis Prompts

Create `config/topics/your-topic-id/prompts.yaml`:

```yaml
# Article Categorization
categorization: |
  Categorize these articles into relevant categories.
  Score each article 1-10 for relevance to your topic.
  
  Categories: your_category_1, your_category_2
  
  Return JSON: [{"article_id": 1, "category": "...", "score": 8}]

# Analysis Prompts (one per category)
analysis:
  your_category_1: |
    Identify key items from these articles about category 1.
    For each item: describe pattern, business impact, mitigation.
    
    Format: JSON array of {"title", "description", "citation_ids"}
  
  your_category_2: |
    Identify key items from these articles about category 2.
    For each item: describe issue, impact, solutions.
    
    Format: JSON array of {"title", "description", "citation_ids"}

# Competitive Intelligence
competitive_intel: |
  Analyze competitor updates relevant to your domain.
  Focus on features, positioning, and competitive threats.

# Reddit Community Analysis
reddit_community: |
  Analyze community discussions for themes, pain points, and sentiment.
  Provide actionable insights for the product team.
```

#### Step 5: Run Your New Topic

```bash
python3 scripts/run_v2_pipeline.py your-topic-id
```

### Deleting a Topic

To remove a topic:

```bash
# Option 1: Disable in configuration
# Edit config/topics/your-topic-id/topic.yaml
# Set: enabled: false

# Option 2: Delete topic directory
rm -rf config/topics/your-topic-id

# Option 3: Clean up data (optional)
rm -rf data/raw/your-topic-id
rm -rf data/reports/your-topic-id
```

### Configuring a Topic

#### Change LLM Provider

Edit `config/topics/your-topic-id/topic.yaml`:
```yaml
llm:
  provider: anthropic  # Switch to Anthropic
  model: claude-3-5-sonnet-20241022
  api_key_env: ANTHROPIC_API_KEY
```

#### Adjust Report Sections

Add/remove sections in `topic.yaml`:
```yaml
report:
  sections:
    - type: executive_summary
    - type: top_items
      config:
        title: "Critical Issues"
        category: "security"
        limit: 10  # Show more items
    # Remove sections by commenting out or deleting
```

#### Update Email Recipients

Edit `topic.yaml`:
```yaml
email:
  recipients:
    - team@example.com
    - manager@example.com
```

---

## 🎯 Running Reports

### Basic Usage

```bash
# Run full pipeline (collect → analyze → report)
python3 scripts/run_v2_pipeline.py <topic_id>

# Examples:
python3 scripts/run_v2_pipeline.py fraud
python3 scripts/run_v2_pipeline.py compliance
```

### Advanced Options

```bash
# Skip collection (use existing data)
python3 scripts/run_v2_pipeline.py fraud --skip-collection

# Skip analysis (regenerate report only)
python3 scripts/run_v2_pipeline.py fraud --skip-collection --skip-analysis

# Skip report generation
python3 scripts/run_v2_pipeline.py fraud --skip-report

# Enable email delivery
python3 scripts/run_v2_pipeline.py fraud --deliver
```

### Development Workflow

```bash
# 1. Collect data once
python3 scripts/run_v2_pipeline.py fraud

# 2. Iterate on prompts/sections (fast - regenerates report only)
python3 scripts/run_v2_pipeline.py fraud --skip-collection --skip-analysis

# 3. Test with fresh analysis
python3 scripts/run_v2_pipeline.py fraud --skip-collection
```

### Output Files

Reports are saved to `data/reports/`:
```
data/reports/
├── 2026-07-06.md           # Markdown report
└── 2026-07-06.html         # HTML (if email sent)
```

Raw data is saved to `data/raw/`:
```
data/raw/
├── 2026-07-06.json              # Collected articles/posts
└── 2026-07-06-analysis.json     # LLM analysis results
```

---

## 📄 Report Sections

Reports are assembled from reusable sections:

### Available Sections

| Section Type | Purpose | Configuration |
|--------------|---------|---------------|
| `executive_summary` | Stats overview | None |
| `top_items` | Ranked list of threats/trends | `title`, `category`, `limit` |
| `reddit_community` | Community insights | `title` |
| `competitive_intel` | Competitor updates | `title` |
| `sources` | Citation list | None (auto) |

### Creating a Custom Section

1. Create `core/reporters/sections/your_section.py`:

```python
from ..base_section import BaseSection

class YourSection(BaseSection):
    def render(self) -> str:
        # Get data from analysis
        data = self.analysis_data.get("your_data_key")
        
        if not data:
            return ""  # Skip if no data
        
        # Get config
        title = self.config.get("title", "## Default Title")
        
        # Render markdown
        output = [f"{title}\n"]
        output.append(data)
        
        return "\n".join(output) + "\n"
```

2. Register in `core/reporters/sections/__init__.py`:

```python
from .your_section import YourSection

__all__ = [..., "YourSection"]
```

3. Register in `core/reporters/report_generator.py`:

```python
SECTION_TYPES = {
    ...
    "your_section": YourSection
}
```

4. Use in `topic.yaml`:

```yaml
report:
  sections:
    - type: your_section
      config:
        title: "## Your Custom Section"
```

---

## 🤝 Forking & Customization

### Fork This Repository

To create your own intelligence platform:

#### 1. Fork the Repository

```bash
git clone <your-fork-url>
cd "PM Radar"
```

#### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Add your API keys to .env
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# BREVO_API_KEY=xkeysib-...
# SOCIALCRAWL_API_KEY=...
```

#### 3. Remove Example Topics

```bash
# Remove the fraud topic (or keep as reference)
rm -rf config/topics/fraud
```

#### 4. Add Your Topics

Follow the [Adding a New Topic](#adding-a-new-topic) guide to create your own intelligence topics.

#### 5. Customize Branding

**Report Headers** - Edit `core/reporters/report_generator.py`:
```python
def _generate_header(self) -> str:
    topic_name = self.topic_config.get("name", "Intelligence Digest")
    header = f"""# {topic_name} - Weekly Report
**Your Company Name**
**Date:** {today}
...
```

**Email Templates** - Edit `scripts/deliver/email_sender.py`:
```python
html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Your brand colors and fonts */
        body {{
            font-family: 'Your Font', sans-serif;
            color: #your-color;
        }}
    </style>
</head>
...
```

**Email Subject** - Edit `config/email-config.json`:
```json
{
  "sender": {
    "name": "Your Company Intelligence",
    "email": "intelligence@yourcompany.com"
  },
  "subject_template": "Your Company Intelligence - {date}"
}
```

#### 6. Configure Deployment

**Option A: Manual Runs**
```bash
# Run weekly via cron
0 9 * * MON python3 /path/to/scripts/run_v2_pipeline.py your-topic --deliver
```

**Option B: GitHub Actions** (create `.github/workflows/weekly-report.yml`):
```yaml
name: Weekly Intelligence Report
on:
  schedule:
    - cron: '0 9 * * MON'  # Every Monday at 9am
  workflow_dispatch:  # Manual trigger

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python3 scripts/run_v2_pipeline.py your-topic --deliver
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          BREVO_API_KEY: ${{ secrets.BREVO_API_KEY }}
```

---

## 🔧 Development

### Project Structure

```
PM Radar/
├── config/                      # Configuration files
│   ├── topics/                  # Topic definitions
│   │   └── fraud/
│   │       ├── topic.yaml       # Main topic config
│   │       ├── prompts.yaml     # LLM prompts
│   │       ├── rss.yaml         # RSS feeds
│   │       ├── reddit.yaml      # Reddit config
│   │       └── changelogs.yaml  # Competitors
│   └── email-config.json
│
├── core/                        # Core platform code
│   ├── collectors/              # Data collection
│   ├── analyzers/               # LLM analysis
│   ├── reporters/               # Report generation
│   ├── delivery/                # Report delivery
│   └── pipeline.py              # Main orchestrator
│
├── scripts/                     # Entry points
│   ├── run_v2_pipeline.py      # Main script (v2)
│   └── deliver/
│       └── email_sender.py
│
├── tests/                       # Test suite
├── data/                        # Generated data
│   ├── raw/                     # Collected & analyzed
│   └── reports/                 # Generated reports
│
└── docs/                        # Documentation
```

### Code Style

- **Fail gracefully**: Always return something, never crash
- **Validate early**: Check data format before processing
- **Log everything**: Make debugging easy
- **Use type hints**: Help IDE autocomplete
- **Write docstrings**: Explain non-obvious behavior

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=core
```

---

## 🐛 Troubleshooting

### Health Check Failures

When you see:
```
✗ Health check FAILED:
  • Citation ID 99 exceeds article count (20)
```

**Solution:** Check `data/raw/*-analysis.json` - LLM may have generated invalid citation IDs.

### JSON Parsing Errors

When you see:
```
⚠️ JSON parse error in top_items: Expecting value
```

**Solution:** LLM returned invalid JSON. The report will gracefully degrade. Check the raw analysis file to see what the LLM returned.

### Missing Sections

If sections are missing:

1. Check if section type is registered in `SECTION_TYPES`
2. Verify section config in `topic.yaml`
3. Check if analysis data has required keys
4. Review health check warnings

### Rollback to V1

If v2 reports break:

```yaml
# In config/topics/<topic_id>/topic.yaml
feature_flag_v2: false  # Switches back to v1
```

---

## 📚 Documentation

### Core Documentation

- **[Setup Guide](docs/setup/setup-guide.md)** - Initial setup
- **[Architecture Guide](docs/architecture/DESIGN_GUIDE.md)** - System design
- **[V2 Robustness](docs/v2-robustness-summary.md)** - Error handling

### Advanced Topics

- **[V2 Robustness Checklist](docs/v2-robustness-checklist.md)** - Testing strategy
- **[V2 Architecture Diagrams](docs/v2-robustness-architecture.md)** - Visual flows
- **[V1 vs V2 Comparison](docs/v1-v2-comparison.md)** - Migration reference

---

## 🔐 Security

### API Key Management

- Never commit `.env` file
- Store keys in environment variables
- Use different keys for dev/prod
- Rotate keys quarterly

### Data Privacy

- Reports contain public data only
- No PII collected
- Review email recipient list quarterly

---

## 📊 Monitoring

### Health Check Metrics

Every report generates metrics:
```
📊 Metrics: 6394 chars, 6 sections, 7 citations
```

Track these over time to detect quality degradation.

---

## 📜 License

[Your License Here]

---

**Last Updated:** July 2026  
**Version:** 2.0  
**Status:** ✅ Production Ready
