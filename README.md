# PM Radar - Automated Product Intelligence System

> Automated weekly intelligence digest covering telecom fraud, security threats, and customer feedback for Product Managers.

## Overview

PM Radar automatically collects, analyzes, and delivers weekly intelligence reports from:
- **Industry RSS Feeds:** Telecom fraud news (Commsrisk, CFCA), security advisories (CISA, Unit 42), threat intelligence
- **Community Feedback:** Reddit discussions from r/twilio analyzing customer sentiment and pain points
- **Competitive Intelligence:** Fraud prevention features and product launches from competitors

**Powered by GPT-4o:** Analyzes 30+ articles and 25 Reddit posts weekly, categorizes by topic, generates executive summaries with citations.

**Time savings:** 8+ hours/week → 5 minutes/week (97% reduction)

## Quick Start

### 1. Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd pm-radar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your keys (see Configuration section)
```

### 2. Configure Sources

Edit configuration files in `config/`:
- **`rss-sources.json`** - RSS feed URLs (14 sources configured)
- **`reddit-config.json`** - Reddit search queries and subreddits
- **`email-config.json`** - Email recipients and sender details

See [Setup Guide](docs/setup/setup-guide.md) for detailed configuration.

### 3. Run Pipeline

```bash
# Test individual collectors
python -m scripts.collect.rss_collector
python -m scripts.collect.reddit_collector

# Run full pipeline (collect → analyze → report → email)
python -m scripts.main
```

### 4. Deploy to GitHub Actions (Optional)

1. Push code to GitHub
2. Add secrets in repo Settings → Secrets → Actions:
   - `OPENAI_API_KEY` - OpenAI API key for GPT-4o
   - `REDDIT_CLIENT_ID` - Reddit API client ID
   - `REDDIT_CLIENT_SECRET` - Reddit API secret
   - `BREVO_API_KEY` - Brevo/SendInBlue API key for email
3. Workflow runs automatically every Monday at 6am UTC

## Configuration

### Required API Keys

Add these to `.env` file:

```bash
# OpenAI (for content analysis)
OPENAI_API_KEY=sk-...

# Reddit (for community listening)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...

# Brevo/SendInBlue (for email delivery)
BREVO_API_KEY=...
BREVO_SENDER_EMAIL=your-email@example.com
BREVO_SENDER_NAME=PM Radar
```

**Getting API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Reddit: https://www.reddit.com/prefs/apps (create "script" app)
- Brevo: https://app.brevo.com/settings/keys/api

See [Setup Guide](docs/setup/setup-guide.md) for detailed instructions.

## Project Structure

```
pm-radar/
├── README.md              # This file
├── CHANGELOG.md           # Version history and changes
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore            # Git ignore rules
│
├── config/               # Configuration files
│   ├── rss-sources.json      # RSS feed sources (14 feeds)
│   ├── reddit-config.json    # Reddit search configuration
│   ├── email-config.json     # Email delivery settings
│   └── competitors.json      # Competitor list (for future use)
│
├── scripts/              # Python source code
│   ├── main.py               # Main pipeline orchestrator
│   ├── collect/              # Data collection modules
│   │   ├── rss_collector.py      # RSS feed collector
│   │   └── reddit_collector.py   # Reddit collector
│   ├── analyze/              # AI analysis modules
│   │   └── summarizer.py         # GPT-4o content analyzer
│   └── deliver/              # Delivery modules
│       ├── email_sender.py       # Email delivery (Brevo)
│       └── pdf_exporter.py       # HTML/PDF export
│
├── templates/            # Report templates
│   └── report-template.html  # HTML email template
│
├── data/                 # Runtime data (gitignored)
│   ├── raw/                  # Collected JSON data
│   ├── reports/              # Generated reports (MD/HTML)
│   └── archive/              # Old reports (optional)
│
├── docs/                 # Documentation
│   ├── setup/                # Setup guides
│   │   ├── setup-guide.md
│   │   ├── email-setup-guide.md
│   │   └── reddit-config-guide.md
│   ├── architecture/         # Design documents
│   │   ├── AGENTS.md
│   │   └── DESIGN_GUIDE.md
│   └── history/              # Development history
│
├── tests/                # Test files (future)
│
└── .github/              # GitHub Actions
    └── workflows/
        └── weekly-collection.yml  # Weekly automation
```

## Features

### Current Features (v1.0)

✅ **Automated Data Collection**
- 14 RSS feeds: Telecom fraud (Commsrisk, CFCA), security (CISA, Unit 42, Mandiant), general cybersecurity
- Reddit social listening: 25+ posts from r/twilio with comments
- 7-day collection window for recent articles

✅ **AI-Powered Analysis (GPT-4o)**
- Content categorization: Telecom Fraud, General Fraud & Security, Competitive Intelligence
- Keyword-based classification with 40+ telecom fraud keywords
- Source category prioritization (telecom sources → always telecom)
- Executive summaries with inline citations
- Reddit sentiment analysis: trending concerns, pain points, competitor mentions

✅ **Professional Reports**
- Markdown reports with clickable citations
- HTML export for email delivery
- Print-ready PDF generation (via browser print)
- Glossary of technical terms
- Complete source bibliography

✅ **Weekly Delivery**
- Email delivery via Brevo/SendInBlue
- HTML-formatted emails with proper styling
- Automated via GitHub Actions (Monday 6am UTC)
- Manual run via `python -m scripts.main`

### Report Sections

1. **Executive Summary** - Article counts by category
2. **Telecom Fraud Digest** - SMS fraud, robocalls, SIM swapping, etc.
3. **General Fraud & Security Digest** - Infrastructure vulnerabilities, data breaches
4. **Twilio Community Discussions** - Reddit sentiment, trending concerns, key insights
5. **Glossary** - Technical term definitions
6. **Sources** - Complete bibliography with clickable links

### Example Output

```
## Telecom Fraud Digest

**Executive Summary:**
Recent developments highlight SMS blasters in São Paulo and 
effective scam blocking in South Korea [[A2]](#a2)[[A3]](#a3).

**Top Threats & Trends:**
1. SMS Blasters: Brazilian authorities found the eighth SMS 
   blaster in São Paulo since July 2024 [[A2]](#a2).
2. Scam Blocks: South Korea disconnected 41,387 phone numbers 
   using 10-minute scam blocking [[A3]](#a3).
```

## Cost Estimate

**Monthly API costs (7-day weekly runs):**
- OpenAI GPT-4o: $0.15-0.40 (~20K input tokens, 2K output per run)
- Reddit API: Free
- Brevo Email: Free tier (300 emails/day)

**Total: ~$0.20-0.45/month**

## Documentation

- **Setup Guides:**
  - [Complete Setup Guide](docs/setup/setup-guide.md) - Step-by-step installation
  - [Email Configuration](docs/setup/email-setup-guide.md) - Brevo email setup
  - [Reddit Configuration](docs/setup/reddit-config-guide.md) - Reddit API setup

- **Architecture:**
  - [Agent Directory](docs/architecture/AGENTS.md) - AI agents overview
  - [Design Guide](docs/architecture/DESIGN_GUIDE.md) - System design

- **Development History:**
  - [CHANGELOG.md](CHANGELOG.md) - Version history
  - [Citation Fix](docs/citation-sources-sync.md) - Citation synchronization
  - [Reddit Community Section](docs/reddit-community-section.md) - Separate Reddit analysis

## Troubleshooting

**No telecom articles collected?**
- Check if Commsrisk/CFCA published articles in last 7 days
- Verify RSS feeds in `config/rss-sources.json` are accessible
- Run `python -m scripts.collect.rss_collector` to test

**Citations broken in report?**
- Ensure `MAX_REDDIT_POSTS_FOR_ANALYSIS` in `main.py` matches `MAX_POSTS` in `summarizer.py`
- See [Citation Fix Doc](docs/citation-sources-sync.md)

**Email not sending?**
- Verify `BREVO_API_KEY` in `.env`
- Check sender email is verified in Brevo dashboard
- See [Email Setup Guide](docs/setup/email-setup-guide.md)

**Reddit API errors?**
- Verify `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` in `.env`
- Check app type is "script" at https://www.reddit.com/prefs/apps
- See [Reddit Config Guide](docs/setup/reddit-config-guide.md)

## Contributing

This is an internal project. For improvements:
1. Create a branch: `git checkout -b feature/your-feature`
2. Make changes and test: `python -m scripts.main`
3. Update CHANGELOG.md
4. Submit pull request

## Future Roadmap

**Phase 2 - Enhanced Collection**
- ⏳ Competitor website scraping (Vonage, MessageBird blogs)
- ⏳ Longer collection windows (14-30 days for slower sources)
- ⏳ Deduplication across runs (SQLite cache)
- ⏳ Feed health monitoring

**Phase 3 - Internal Sources**
- ⏳ Slack VOC channel integration
- ⏳ Gong call transcript analysis
- ⏳ Source quality scoring

## License

Internal tool - Not for external distribution.

## Support

For questions or issues, contact the product team or create an issue in the repository.
