# PM Radar - Quick Start Guide

**Get your first report in 5 minutes.**

---

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and add:
```bash
OPENAI_API_KEY=sk-...
BREVO_API_KEY=xkeysib-...
SOCIALCRAWL_API_KEY=...  # Optional, for Reddit
```

## 3. Run Your First Report

```bash
python3 scripts/run_v2_pipeline.py fraud
```

Output:
```
✓ Collected 77 articles
✓ Analyzed articles  
✓ Generated report
→ Running health checks...
  ✓ Health check passed
  📊 Metrics: 6394 chars, 6 sections, 7 citations
  ✓ Report saved to data/reports/2026-07-06.md
```

## 4. View Report

```bash
open data/reports/2026-07-06.html
```

---

## Common Commands

### Run full pipeline
```bash
python3 scripts/run_v2_pipeline.py fraud
```

### Regenerate report only (fast)
```bash
python3 scripts/run_v2_pipeline.py fraud --skip-collection --skip-analysis
```

### Send via email
```bash
python3 scripts/run_v2_pipeline.py fraud --deliver
```

---

## Adding Your Own Topic

### 1. Create directory
```bash
mkdir -p config/topics/my-topic
```

### 2. Copy fraud config as template
```bash
cp config/topics/fraud/topic.yaml config/topics/my-topic/
cp config/topics/fraud/prompts.yaml config/topics/my-topic/
cp config/topics/fraud/rss.yaml config/topics/my-topic/
```

### 3. Edit configs
- `topic.yaml` - Change name, categories, email recipients
- `prompts.yaml` - Customize analysis prompts
- `rss.yaml` - Add your RSS feeds

### 4. Run it
```bash
python3 scripts/run_v2_pipeline.py my-topic
```

---

## Need Help?

- **Full docs:** See [README.md](README.md)
- **Troubleshooting:** See [README.md#troubleshooting](README.md#troubleshooting)
- **Architecture:** See [docs/v2-robustness-architecture.md](docs/v2-robustness-architecture.md)

---

**That's it! You're ready to generate intelligence reports.** 🎉
