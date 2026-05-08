# PM Radar - Weekly Intelligence Digest

Automated intelligence gathering system for fraud prevention and telecom security news.

## 📊 What It Does

PM Radar automatically collects, analyzes, and delivers weekly intelligence reports covering:
- **Telecom Fraud**: SMS pumping, IRSF, robocalls, SIM swap attacks
- **General Fraud & Security**: Industry-wide security threats and trends
- **Competition Watch**: Competitor product updates from Vonage, Bandwidth, etc.
- **Community Insights**: Reddit discussions from r/twilio

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API Keys:
  - OpenAI API (for analysis)
  - SociaVault API (for Reddit data)
  - Brevo API (optional, for email delivery)

### Installation

```bash
# Clone the repository
git clone https://github.com/say-das/PM-RADAR.git
cd PM-RADAR

# Install dependencies
pip install -r requirements.txt

# Install browser for web scraping
patchright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running Locally

```bash
# Run full pipeline (collect, analyze, generate report)
python scripts/main.py

# Or collect RSS data only
python scripts/collect/rss_collector.py
```

Reports are generated in:
- `data/reports/YYYY-MM-DD.md` (Markdown)
- `data/reports/YYYY-MM-DD.html` (HTML)

## 📁 Project Structure

```
PM-RADAR/
├── scripts/
│   ├── collect/          # Data collection scripts
│   │   ├── rss_collector.py
│   │   ├── reddit_collector.py
│   │   └── changelog_scraper_v3.py
│   ├── analyze/          # AI analysis
│   │   └── summarizer.py
│   ├── deliver/          # Report delivery
│   │   ├── email_sender.py
│   │   ├── pdf_exporter.py
│   │   └── github_release.py
│   └── main.py           # Main orchestration
├── config/               # Configuration files
│   ├── rss-feeds.json
│   ├── reddit-queries.json
│   └── competitor-changelogs.json
├── data/
│   ├── raw/              # Collected data
│   └── reports/          # Generated reports
├── docs/
│   ├── reports/          # Published HTML reports
│   └── planning/         # Design documents
└── .github/workflows/    # GitHub Actions
```

## 🤖 Automation

Weekly reports run automatically via GitHub Actions:
- **Schedule**: Every Thursday at 1:30 PM UTC
- **Workflow**: `.github/workflows/weekly-report.yml`
- **Output**: Published to GitHub Pages

## 🔧 Configuration

### RSS Feeds
Edit `config/rss-feeds.json` to add/remove sources:
```json
{
  "name": "Source Name",
  "url": "https://example.com/feed",
  "category": "telecom_fraud"
}
```

### Competitor Changelogs
Edit `config/competitor-changelogs.json`:
```json
{
  "url": "https://competitor.com/changelog",
  "product": "Product Name",
  "scrape_mode": "full"
}
```

## 📄 Documentation

- [Project Map](PROJECT_MAP.md) - System architecture
- [Changelog](CHANGELOG.md) - Version history
- [Git Upload Checklist](GIT_UPLOAD_CHECKLIST.md) - Deployment guide

## 🛠️ Development

### Adding a New Data Source

1. Add configuration to appropriate JSON file in `config/`
2. Update collector script if needed
3. Test locally: `python scripts/main.py`
4. Commit and push

### Modifying Analysis Logic

Edit `scripts/analyze/summarizer.py` - uses GPT-4o for intelligent summarization.

## 📊 Report Features

- **Executive Summary**: Key stats and metrics
- **Top 5 Threats**: Prioritized threat analysis
- **Competition Watch**: Up to 6 relevant competitor updates
- **Date Filtering**: Only shows recent (30-day) Reddit discussions
- **Smart Citations**: Inline references with clickable links
- **Glossary**: Auto-generated technical term definitions

## 🔍 Troubleshooting

### No Competitor Updates in Report
- Check if Playwright browsers are installed: `patchright install chromium`
- Verify `OPENAI_API_KEY` is set

### Reddit Section Shows Old Posts
- Cache cleared automatically for posts older than 24 hours
- Manual clear: `rm -rf data/raw/.reddit_cache`

### Commsrisk Articles Missing (CI only)
- Known issue: Commsrisk blocks GitHub Actions IPs
- Works fine locally

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a personal project, but suggestions are welcome via issues.

---

*Generated with ❤️ using Claude Code*
