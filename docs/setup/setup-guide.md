# PM Radar Setup Guide

Quick guide to get PM Radar running locally.

## Prerequisites

- Python 3.11+
- Git (optional)
- API keys (see below)

---

## Step 1: Install Dependencies

```bash
cd "/Users/saydas/Documents/CPM/experiments/PM Radar"

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

---

## Step 2: Configure API Keys

### Create .env file

```bash
cp .env.example .env
```

### Add API keys to .env

#### Required for RSS only (MVP Phase 1a):
- None! RSS feeds work without API keys

#### Required for Reddit (MVP Phase 1b):
Get from: https://sociavault.com

1. Sign up for SociaVault account
2. Navigate to API settings/keys
3. Generate new API key

Add to `.env`:
```
SOCIAVAULT_API_KEY=sk_live_your_key_here
```

#### Required for AI Analysis (MVP Phase 2):
Get from: https://platform.openai.com/api-keys

Add to `.env`:
```
OPENAI_API_KEY=sk-proj-...
```

#### Required for Email (MVP Phase 3):
Get from: https://app.brevo.com/settings/keys/api

Add to `.env`:
```
BREVO_API_KEY=xkeysib-...
```

---

## Step 3: Configure Sources

### RSS Feeds
Edit `config/rss-sources.json` to add/remove feeds:

```json
{
  "sources": [
    {
      "name": "Your Feed Name",
      "url": "https://example.com/feed.xml",
      "category": "industry_news"
    }
  ]
}
```

### Reddit Queries
Edit `config/reddit-config.json`:

```json
{
  "queries": [
    {
      "query": "your search terms here",
      "timeframe": "week",
      "limit": 50,
      "subreddits": "all"
    }
  ]
}
```

---

## Step 4: Test Individual Components

### Test RSS Collector (No API needed)

```bash
python -m scripts.collect.rss_collector
```

**Expected output:**
```
Collecting RSS feeds (last 7 days)...
  → Telecom Reseller... ✓ 5 articles
  → Fierce Wireless... ✓ 8 articles
  ...
Total collected: 32 articles
✓ Saved to: data/raw/test-rss-collection.json
```

### Test Reddit Collector (Needs SociaVault API)

```bash
python -m scripts.collect.reddit_collector
```

**Expected output:**
```
Connecting to SociaVault API...

Searching Reddit via SociaVault: 'Twilio SMS pumping OR telecom fraud'
  Timeframe: week, Limit: 50
  ✓ Found 15 posts

Total collected: 15 posts
✓ Saved to: data/raw/test-reddit-collection.json
```

### Test AI Analyzer (Needs OpenAI API)

```bash
# First collect some data
python -m scripts.collect.rss_collector
python -m scripts.collect.reddit_collector

# Then run analysis
python -m scripts.analyze.summarizer
```

**Expected output:**
```
Analyzing data with OpenAI GPT-4...
  → Analyzing RSS articles...
    ✓ RSS analysis complete
  → Analyzing Reddit posts...
    ✓ Reddit analysis complete
✓ Saved to: data/raw/test-analysis.json
```

---

## Step 5: Run Full Pipeline

```bash
python scripts/main.py
```

**Expected output:**
```
======================================================================
                    PM RADAR - WEEKLY INTELLIGENCE
======================================================================

[1/3] DATA COLLECTION
----------------------------------------------------------------------

[1.1] RSS FEEDS
Collecting RSS feeds...
Total collected: 32 articles

[1.2] REDDIT POSTS
Searching Reddit...
Total collected: 15 posts

✓ Raw data saved: data/raw/2026-04-03.json

[2/3] AI ANALYSIS
----------------------------------------------------------------------
Analyzing data with OpenAI GPT-4...
✓ Analysis saved: data/raw/2026-04-03-analysis.json

[3/3] REPORT GENERATION & DELIVERY
----------------------------------------------------------------------
✓ Report saved: data/reports/2026-04-03.md

======================================================================
PIPELINE COMPLETE
======================================================================
```

---

## Step 6: View Report

```bash
cat "data/reports/$(date +%Y-%m-%d).md"
```

Or open in your editor/browser.

---

## Troubleshooting

### "Module not found" error

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "API key not found" error

```bash
# Check .env file exists
ls -la .env

# Verify it has your keys
cat .env

# Make sure python-dotenv is installed
pip install python-dotenv
```

### RSS feed parse errors

Some feeds may fail. This is normal. The collector will:
- Skip failed feeds
- Continue with others
- Show ✗ for failed sources

### SociaVault rate limiting

If you hit rate limits:
- Reduce `limit` in `config/reddit-config.json`
- Wait between runs
- Check your SociaVault plan limits

### OpenAI cost concerns

Typical costs per run:
- RSS analysis: ~$0.05-0.10
- Reddit analysis: ~$0.03-0.05
- Total per week: ~$0.10-0.20

Monthly: ~$1-2

---

## Next Steps

Once local testing works:

1. **Set up GitHub repo**
   ```bash
   git init
   git add .
   git commit -m "Initial PM Radar MVP"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Add GitHub Secrets**
   - Go to repo Settings → Secrets → Actions
   - Add: `OPENAI_API_KEY`, `SOCIAVAULT_API_KEY`, `BREVO_API_KEY`

3. **Deploy GitHub Actions workflow**
   - Copy workflow file (see `mvp-project-structure.md`)
   - Runs automatically every Monday 6am UTC

---

## Support

Issues? Check:
1. All dependencies installed (`pip list`)
2. .env file configured with keys
3. Virtual environment activated
4. Python 3.11+ (`python --version`)

Still stuck? Review error messages or check logs in `data/` directory.
