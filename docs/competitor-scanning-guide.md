# Competitive Intelligence Scanning Guide

## Overview
PM Radar uses a Claude skill to scan competitor websites for fraud/security-related product updates, feature launches, and pricing changes.

---

## How It Works

### 1. **Configuration** (`config/competitor-sources.json`)
Define competitors and what to scan:

```json
{
  "competitors": [
    {
      "name": "Vonage",
      "urls": {
        "blog": "https://www.vonage.com/blog/",
        "changelog": "https://www.vonage.com/changelog/",
        "pricing": "https://www.vonage.com/pricing/sms/",
        "security": "https://www.vonage.com/security/"
      },
      "focus_areas": [
        "fraud detection features",
        "SMS verification APIs",
        "security announcements"
      ]
    }
  ]
}
```

**URL Types You Can Add:**
- `blog` - Company blog posts
- `changelog` - Product release notes
- `pricing` - Pricing pages
- `documentation` - API/product docs
- `security` - Security pages
- `press` - Press releases
- `case_studies` - Customer stories

### 2. **Skill Invocation** (`competitor-scan`)
The skill:
- Uses WebFetch to retrieve each URL
- Claude reads and understands the content
- Filters for fraud/security-related content
- Extracts structured intelligence

### 3. **What Gets Captured**

✅ **Product Launches**
- New fraud detection APIs
- Verification services
- Security feature announcements

✅ **Feature Updates**
- Changelog entries about fraud prevention
- API security improvements
- Compliance updates

✅ **Pricing Changes**
- New fraud protection add-ons
- Verification service pricing
- Security tier changes

✅ **Technical Updates**
- API authentication changes
- SDK security updates
- Documentation about fraud prevention

❌ **What Gets Filtered Out**
- General company news
- Hiring announcements
- Events and conferences (unless fraud-related)
- Generic product updates unrelated to security

---

## Adding New Competitors

Edit `config/competitor-sources.json`:

```json
{
  "name": "NewCompetitor",
  "urls": {
    "blog": "https://www.newcompetitor.com/blog/",
    "changelog": "https://www.newcompetitor.com/changelog/"
  },
  "focus_areas": [
    "fraud detection",
    "SMS security",
    "verification APIs"
  ]
}
```

**Tips:**
- Start with 2-3 URLs (blog + changelog)
- Add more URL types if they have relevant content
- Be specific with focus_areas (helps Claude filter better)

---

## Output Format

Each finding includes:

```json
{
  "competitor": "Vonage",
  "title": "Real-Time Fraud Detection API Launch",
  "url": "https://www.vonage.com/blog/...",
  "source_type": "blog",
  "published_date": "2026-03-28",
  "summary": "2-3 sentence summary",
  "category": "product_launch",
  "relevance_score": 9,
  "key_points": [
    "Real-time detection with 100ms latency",
    "Integrates with verification APIs"
  ]
}
```

**Categories:**
- `product_launch` - New product or major feature
- `feature_update` - Enhancement to existing feature
- `pricing_change` - Pricing model update
- `technical_update` - API/SDK changes

---

## Running the Scanner

### Standalone Test
```bash
python -m scripts.collect.competitor_collector
```

### Full Pipeline
```bash
python -m scripts.main
```

The competitive intelligence will appear in the **"Competitive Intelligence Digest"** section of the report.

---

## Skill Architecture

**Skill Location:** `.claude/skills/competitor-scan.md`

**How the skill works:**
1. Receives competitor object (name, URLs, focus areas)
2. Fetches all URLs using WebFetch
3. Claude analyzes content across all sources
4. Extracts fraud/security-related findings
5. Returns structured JSON array

**Advantages over RSS:**
- Works with any website (no RSS required)
- Claude understands context (better than keyword matching)
- Single skill works for all competitors
- Handles JavaScript-rendered pages
- No CSS selectors to maintain

---

## Troubleshooting

### Skill not found
Make sure `.claude/skills/competitor-scan.md` exists in your Claude Code directory.

### No results returned
- Check if competitor URLs are accessible
- Verify focus_areas are relevant
- Try broadening fraud_keywords in config

### Too many irrelevant results
- Make focus_areas more specific
- Reduce days_back in extraction_settings
- Adjust relevance_score threshold

---

## Cost Considerations

**WebFetch Usage:**
- 5 competitors × 4 URLs each = 20 WebFetch calls per run
- Weekly run = 80 WebFetch calls/month
- Cost: Minimal (WebFetch is fast and lightweight)

**Claude Processing:**
- Skill analyzes content and extracts intelligence
- ~1-2 minutes per competitor
- Total: ~5-10 minutes per pipeline run

---

## Future Enhancements

1. **Changelog-specific parsing** - Detect version numbers, feature flags
2. **Screenshot capture** - For visual product changes
3. **Price tracking** - Historical pricing data
4. **Alert system** - Immediate notifications for major launches
5. **Competitive matrix** - Side-by-side feature comparison

---

## Configuration Reference

**extraction_settings:**
```json
{
  "max_items_per_source": 5,          // Max findings per URL type
  "days_back": 14,                    // Look back N days
  "fraud_keywords": [...],            // Keywords for filtering
  "fetch_all_urls": true,             // Fetch all URLs or stop early
  "timeout_per_url": 30               // Timeout in seconds
}
```

---

**Next Steps:**
1. ✅ Add competitors to `config/competitor-sources.json`
2. ✅ Customize focus_areas for each competitor
3. ✅ Run test: `python -m scripts.collect.competitor_collector`
4. ✅ Run full pipeline: `python -m scripts.main`
5. ✅ Review Competitive Intelligence Digest in report
