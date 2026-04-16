# PM Radar - Project Map

**Quick navigation guide for troubleshooting and development**

---

## 📁 Project Structure Overview

```
PM Radar/
├── scripts/              # All pipeline logic
│   ├── main.py          # Pipeline orchestrator (START HERE)
│   ├── collect/         # Data collection modules
│   ├── analyze/         # AI analysis modules
│   └── deliver/         # Output & delivery modules
├── config/              # RSS feeds & settings
├── data/                # Generated data & reports
│   ├── raw/            # Collected data (*.json)
│   └── reports/        # Final reports (*.md, *.html)
├── docs/               # GitHub Pages deployment
│   └── reports/        # Published HTML reports
├── templates/          # HTML/Email templates
└── .github/workflows/  # CI/CD automation
```

---

## 🎯 Entry Points & Main Functions

### **Pipeline Orchestrator**
**File:** `scripts/main.py`
- **Purpose:** Main entry point - runs entire pipeline
- **Key Function:** `main()`
  - Orchestrates: Collection → Analysis → Report Generation → Delivery
- **When to check:** Pipeline fails or step sequence issues

**Flow:**
```python
1. RSS Collection (rss_collector.py)
2. Reddit Collection (reddit_collector.py)
3. Content Analysis (summarizer.py)
4. Report Generation (main.py:generate_report)
5. GitHub Release (github_release.py)
6. Email Delivery (email_sender.py)
```

---

## 📊 Data Collection

### **RSS Feed Collector**
**File:** `scripts/collect/rss_collector.py`
- **Class:** `RSSCollector`
- **Key Methods:**
  - `collect(days_back=7)` - Main collection function
  - `_fetch_feed(url, category)` - Individual feed fetcher
- **Config:** `config/rss_feeds.json`
- **When to check:**
  - "403 Forbidden" errors
  - Missing articles from specific sources
  - Feed parsing failures

**Common Issues:**
- **403 errors:** RSS feeds blocking GitHub Actions IPs
  - Location: Line 43 (User-Agent header)
  - Fix: Check fallback system or use proxies
- **No articles collected:** Check feed URLs in config

### **Reddit Collector**
**File:** `scripts/collect/reddit_collector.py`
- **Class:** `RedditCollector`
- **Key Methods:**
  - `collect_posts(query, subreddit, timeframe, limit)` - Main collection
  - `_fetch_post_comments(post_id, subreddit)` - Comment fetcher
- **API:** SociaVault API
- **When to check:**
  - No Reddit posts collected
  - Comment fetching failures
  - API rate limits

**Common Issues:**
- **API key errors:** Check `SOCIAVAULT_API_KEY` in secrets
- **Empty results:** Verify subreddit name and query syntax

---

## 🤖 Content Analysis

### **Content Analyzer Agent**
**File:** `scripts/analyze/summarizer.py`
- **Class:** `ContentAnalyzerAgent`
- **Key Methods:**
  - `analyze(collected_data)` - Main analysis orchestrator
  - `_categorize_content(collected_data)` - Categorizes articles
  - `_analyze_category(client, category_data, category_name)` - GPT-4o analysis
  - `_analyze_competitive(client, category_data)` - Competitive intel analysis
  - `_analyze_reddit_community(client, reddit_posts)` - Reddit sentiment analysis
  - `_load_fallback_data(category_name, days_back=7)` - **FALLBACK SYSTEM**

**When to check:**
- Empty report sections
- "Analysis failed" errors
- OpenAI API errors
- Categorization issues

**Critical Logic:**

1. **Categorization (Line 22-150)**
   - Keywords: Lines 30-63 (telecom vs general fraud)
   - Priority system: source category → keywords → skip
   - **Fallback trigger:** Line 145-157 (activates if 0 articles)

2. **Fallback System (Line 24-68)**
   - Checks `data/raw/` for last 7 days
   - Extracts telecom_fraud & competitor articles
   - Returns up to 10 articles
   - Silently fails if no data found

3. **GPT-4o Prompts:**
   - Telecom/General: Lines 282-304 (includes citation requirements)
   - Competitive: Lines 211-224 (focus on fraud features)
   - Reddit: Lines 347-383 (sentiment & concerns)

**Common Issues:**
- **Empty telecom section:** Check fallback logs, verify raw data exists
- **OpenAI errors:** Check `OPENAI_API_KEY`, verify version >=2.0.0
- **JSON parsing errors:** GPT-4o response format issues (check prompts)
- **Missing citations:** Check prompt includes citation instructions

---

## 📝 Report Generation

### **Report Builder**
**File:** `scripts/main.py`
- **Function:** `generate_report(collected_data, analysis_results, date_str)`
  - Lines 85-142 (approx)
- **Key Logic:**
  - Markdown generation with citations
  - Sources section with anchor IDs
  - HTML conversion

**When to check:**
- Malformed markdown
- Missing sections
- Citation links broken
- Empty Sources section

**Citation System:**
- Format: `[A1](#a1)` links to `<a id="a1"></a>`
- Articles: [A1], [A2], etc.
- Reddit: [R1], [R2], etc.

**Critical Sections:**
1. **Telecom Fraud Digest:** Lines ~195-220
2. **General Fraud Digest:** Lines ~222-247
3. **Reddit Community:** Lines ~249-285
4. **Sources:** Lines ~287-320

**Common Issues:**
- **Empty sections:** Check if analysis returned data for that category
- **Broken citations:** Verify anchor IDs match link hrefs
- **JSON in output:** GPT-4o returned unparsed JSON (check prompts)

---

## 🚀 Delivery & Publishing

### **GitHub Release Publisher**
**File:** `scripts/deliver/github_release.py`
- **Class:** `GitHubReleasePublisher`
- **Key Methods:**
  - `publish_report(report_md_path, date_str)` - Main publisher
  - `_create_github_release(...)` - Uses `gh` CLI
  - `_generate_release_notes(...)` - Creates release body
  - `_commit_and_push_pages(...)` - Updates GitHub Pages
  - `_get_repo_from_git()` - Auto-detects repo from remote

**When to check:**
- Release not created
- Wrong GitHub Pages URL in release
- Release tag already exists errors
- Missing attachments

**Critical Configuration:**
- **Pages URL:** Line 21 (auto-generated from git remote)
- **Release notes:** Line 124 (uses `self.pages_base`)
- **gh CLI commands:** Line 200-213

**Common Issues:**
- **403 permission denied:** Check workflow permissions (Settings → Actions → Read/Write)
- **Tag already exists:** Delete old tag with `gh release delete`
- **Wrong URL in release:** Verify `self.pages_base` calculation
- **Files not attached:** Check file paths exist before `gh release create`

### **Email Sender**
**File:** `scripts/deliver/email_sender.py`
- **Class:** `EmailSender`
- **Key Methods:**
  - `send_report(report_md_path, recipients)` - Main sender
- **API:** Brevo (formerly SendInBlue)

**When to check:**
- Email not received
- Formatting issues in email

---

## ⚙️ Configuration Files

### **RSS Feeds**
**File:** `config/rss_feeds.json`
```json
{
  "feeds": [
    {
      "name": "Source Name",
      "url": "https://...",
      "category": "telecom_fraud | competitor | general"
    }
  ]
}
```

**Categories:**
- `telecom_fraud`: Always categorized as telecom (Commsrisk, CFCA, Globe)
- `competitor`: Messaging competitors (Vonage, MessageBird, etc.)
- `general`: General security/fraud sources

### **Environment Variables**
**File:** `.env` (local) / GitHub Secrets (CI)
- `OPENAI_API_KEY` - GPT-4o analysis
- `SOCIAVAULT_API_KEY` - Reddit data collection
- `BREVO_API_KEY` - Email delivery
- `GH_TOKEN` - Auto-provided by GitHub Actions

---

## 🔄 GitHub Actions Workflow

### **Weekly Report Automation**
**File:** `.github/workflows/weekly-report.yml`

**Schedule:** Every Thursday at 1:30 PM UTC (7:00 PM IST)
```yaml
cron: '30 13 * * 4'
```

**Jobs:**
1. **Setup:** Python 3.11.15, install dependencies
2. **Run Pipeline:** Execute `scripts/main.py`
3. **Commit:** Stage and commit generated files
4. **Publish:** Push to main branch (triggers Pages deployment)

**When to check:**
- Workflow not triggering on schedule
- Build failures
- Permission errors
- Missing secrets

**Common Issues:**
- **First scheduled run missed:** Normal GitHub behavior, wait for next week
- **Python version issues:** Pinned to 3.11.15 (don't use 3.14)
- **OpenAI httpx errors:** Requires openai>=2.0.0
- **Git push rejected:** Check workflow permissions
- **Missing dependencies:** Check `requirements.txt`

**File Staging (Line 46):**
```yaml
git add data/reports/ data/raw/ docs/reports/
```

---

## 🐛 Common Troubleshooting Scenarios

### **Problem: Empty Telecom Fraud Section**

**Diagnostic Path:**
1. Check logs: "Telecom Fraud: 0 items"?
2. → Check RSS collection: 403 errors on Commsrisk/Globe?
3. → Check fallback: "checking fallback data..." message?
4. → Verify fallback data exists: `data/raw/2026-*.json` files present?
5. → Check categorization keywords: `summarizer.py` Lines 30-56

**Files to check:**
- `scripts/collect/rss_collector.py` (collection)
- `scripts/analyze/summarizer.py` (fallback system)
- `data/raw/*.json` (previous data)

**Solution:**
- If feeds blocked: Fallback should activate automatically
- If no fallback data: Run collection locally, commit raw data
- If categorization wrong: Update keywords in `summarizer.py`

---

### **Problem: GitHub Release Creation Fails**

**Diagnostic Path:**
1. Check error: "Tag already exists"?
   - Solution: `gh release delete report-YYYY-MM-DD --yes`
2. Check error: "Permission denied"?
   - Solution: Settings → Actions → Workflow permissions → Read/Write
3. Check error: "File not found"?
   - Solution: Verify `data/reports/*.html` and `*.md` exist

**Files to check:**
- `scripts/deliver/github_release.py`
- `.github/workflows/weekly-report.yml` (permissions)

---

### **Problem: HTML Report Shows Raw JSON**

**Diagnostic Path:**
1. Check which section: Telecom/General/Reddit?
2. → Check GPT-4o response parsing in `main.py`
3. → Verify prompt includes "Format as JSON" in `summarizer.py`
4. → Check if `json.loads()` succeeded

**Root Cause:** GPT-4o prompt asked for JSON inside strings, breaking parser

**Files to check:**
- `scripts/analyze/summarizer.py` (prompts)
- `scripts/main.py` (JSON parsing)

**Solution:**
- Prompt must return clean JSON
- Use integers for post_nums, not "[REDDIT_N]" strings

---

### **Problem: Citations Don't Jump to Sources**

**Diagnostic Path:**
1. Check HTML anchor IDs: `<a id="a1"></a>` present?
2. Check link hrefs: `href="#a1"` match anchor IDs?
3. Check if HTML was regenerated after fix

**Files to check:**
- `scripts/main.py` (Sources section generation)
- `data/reports/*.html`

**Solution:**
- Sources must include: `<a id="a{i}"></a>[A{i}]: ...`
- Ensure HTML copied to `docs/reports/` after fix

---

### **Problem: OpenAI "proxies" Error**

**Diagnostic Path:**
1. Check Python version: Must be 3.11, NOT 3.14
2. Check openai version: Must be >=2.0.0
3. Check httpx compatibility

**Root Cause:** Python 3.14 + old openai versions = httpx incompatibility

**Files to check:**
- `.github/workflows/weekly-report.yml` (Python version)
- `requirements.txt` (openai version)

**Solution:**
- Pin Python to 3.11.15
- Use openai>=2.0.0

---

## 📦 Dependencies

### **Key Libraries**
```
openai>=2.0.0          # GPT-4o analysis (v2.x required for httpx compatibility)
feedparser==6.0.10     # RSS feed parsing
requests==2.31.0       # HTTP requests
markdown>=3.5.1        # Markdown to HTML conversion
python-dotenv==1.0.0   # Environment variables
sib-api-v3-sdk==7.6.0  # Brevo email API
```

**When to update:**
- openai: If API changes or compatibility issues
- markdown: If HTML rendering broken

---

## 🔍 Quick Reference

### **Find specific functionality:**

| Need to... | Go to... |
|------------|----------|
| Change RSS feeds | `config/rss_feeds.json` |
| Modify categorization keywords | `scripts/analyze/summarizer.py` Line 30-63 |
| Adjust fallback logic | `scripts/analyze/summarizer.py` Line 24-68 |
| Fix GPT-4o prompts | `scripts/analyze/summarizer.py` Lines 211-395 |
| Change report format | `scripts/main.py` `generate_report()` |
| Modify release notes | `scripts/deliver/github_release.py` Line 115-142 |
| Update workflow schedule | `.github/workflows/weekly-report.yml` Line 5 |
| Change email recipients | `config/email_config.json` |

### **Find specific errors:**

| Error message | Check... |
|--------------|----------|
| "403 Forbidden" | RSS collector + Fallback system |
| "Analysis failed: proxies" | Python version + openai version |
| "GitHub Release failed: Tag exists" | Delete old release tag |
| "Permission denied" | Workflow permissions setting |
| "HTML report not found" | Check markdown package installed |
| "No changes to commit" | Normal if no new data generated |

---

## 📈 Data Flow Diagram

```
┌─────────────────────┐
│  RSS Feeds (14)     │
│  Reddit (r/twilio)  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Data Collection    │
│  • rss_collector    │
│  • reddit_collector │
└──────────┬──────────┘
           │
           ↓
    data/raw/*.json
           │
           ↓
┌─────────────────────┐
│  Categorization     │
│  telecom/general/   │
│  competitive        │
│  ↓ (if empty)       │
│  FALLBACK: Load     │
│  from previous days │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  GPT-4o Analysis    │
│  • Telecom insights │
│  • General insights │
│  • Reddit sentiment │
│  • Competitive intel│
└──────────┬──────────┘
           │
           ↓
 data/raw/*-analysis.json
           │
           ↓
┌─────────────────────┐
│  Report Generation  │
│  • Markdown         │
│  • HTML (w/CSS)     │
└──────────┬──────────┘
           │
           ├→ data/reports/*.md
           ├→ data/reports/*.html
           └→ docs/reports/*.html
              │
              ↓
┌─────────────────────┐
│  Delivery           │
│  • GitHub Release   │
│  • GitHub Pages     │
│  • Email (Brevo)    │
└─────────────────────┘
```

---

## 🎓 Understanding the Codebase

### **Architecture Principles:**
1. **Modular Pipeline:** Each stage (collect/analyze/deliver) is independent
2. **Fail-Safe:** Fallback systems prevent empty reports
3. **Idempotent:** Re-running same day overwrites, doesn't duplicate
4. **Observable:** Logs at each step for debugging

### **Key Design Decisions:**

**Why fallback system?**
- RSS feeds frequently blocked by anti-bot measures
- GitHub Actions IPs often rate-limited
- Better to show week-old data than empty sections

**Why separate md and html?**
- Markdown for git-friendly diffs
- HTML for styled rendering on Pages
- Both attached to releases for flexibility

**Why not use GitHub Issues/Discussions?**
- Releases provide better notification system
- Pages hosting for rich HTML rendering
- Email integration via Brevo

**Why GPT-4o instead of local LLM?**
- Quality of summaries and citations
- No infrastructure costs (serverless)
- API reliability

---

## 🆘 Emergency Fixes

### **Pipeline completely broken:**
```bash
# 1. Check last successful run
gh run list --repo say-das/PM-RADAR --limit 5

# 2. View logs of failed run
gh run view <run-id> --log

# 3. Test locally first
cd "Experiments/PM Radar"
python3 scripts/main.py

# 4. If local works but CI fails:
# - Check secrets are set
# - Check Python version matches (3.11.15)
# - Check dependencies installed
```

### **Need to skip a section:**
Edit `scripts/main.py` and comment out the section generation code.

### **Need to regenerate a report:**
```bash
# Delete old files
rm -f data/reports/YYYY-MM-DD.*
rm -f docs/reports/YYYY-MM-DD.html
gh release delete report-YYYY-MM-DD --yes

# Re-run workflow
gh workflow run weekly-report.yml --repo say-das/PM-RADAR
```

---

## 📚 Related Documentation

- `README.md` - Project overview and setup
- `CHANGELOG.md` - Version history
- `GIT_UPLOAD_CHECKLIST.md` - Security checklist
- `.env.example` - Required environment variables

---

**Last Updated:** 2026-04-17
**Maintainer:** PM Radar Team
**Questions?** Check logs first, then review relevant file in this map.
