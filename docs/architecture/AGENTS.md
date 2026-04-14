# PM Radar - Agent Quick Reference

**4 Core Agents** | Last Updated: 2026-04-08

---

## 1. Content Analyzer Agent (Phase 1 - COMPLETE)
Analyzes collected data weekly using GPT-4o. Categorizes content (Telecom Fraud, General Fraud, Competitive Intelligence), summarizes by topic, detects trends, generates executive summaries, and produces professional reports with citations and glossary.

**Status:** ✅ OPERATIONAL  
**Technology:** OpenAI GPT-4o  
**Frequency:** Weekly (Monday 6am UTC)  
**Cost:** ~$0.05-0.10 per run

---

## 2. Source Discovery Agent (Phase 2 - NOT STARTED)
Automatically discovers new data sources via Google searches across three categories: Competition (pricing, blogs, changelogs, API docs), Industry Analysts (RSS feeds), and Community (forums, subreddits). Validates URLs and auto-updates source config files.

**Status:** ⏳ NOT STARTED  
**Technology:** Claude Sonnet 4.6 via AWS Bedrock  
**Frequency:** Monthly (first Monday)  
**Cost:** ~$3-5 per run

---

## 3. Source Quality Monitor Agent (Phase 3 - NOT STARTED)
Regularly audits all configured sources and assigns quality scores (RSS frequency, uptime, compliance) and relevance scores (fraud focus). Recommends KEEP/REVIEW/REMOVE actions to maintain source list health.

**Status:** ⏳ NOT STARTED  
**Technology:** Claude Sonnet 4.6 via AWS Bedrock  
**Frequency:** Weekly quick checks + Monthly comprehensive audits  
**Cost:** ~$2-4 per run

---

## 4. Internal Data Collection Agent (Phase 3 - NOT STARTED)
Gathers intelligence from internal Twilio tools weekly: Slack VOC channels, Gong call transcripts, Marvin reports. Aggregates findings into timestamped markdown files (e.g., `internal-intelligence-2026-W14.md`) for Content Analyzer Agent to read.

**Status:** ⏳ NOT STARTED  
**Technology:** Claude Sonnet 4.6 via AWS Bedrock  
**Frequency:** Weekly (Sunday evening before Content Analyzer)  
**Cost:** ~$3-5 per run

---

## Agent Status Summary

| Agent | Status | Phase | Cost/Run |
|-------|--------|-------|----------|
| Content Analyzer Agent | **✅ COMPLETE** | Phase 1 | $0.05-0.10 |
| Source Discovery Agent | ⏳ Not Started | Phase 2 | $3-5 |
| Source Quality Monitor Agent | ⏳ Not Started | Phase 3 | $2-4 |
| Internal Data Collection Agent | ⏳ Not Started | Phase 3 | $3-5 |

**Operational Agents:** 1 of 4 (25%)

---

## Weekly Workflow (When All Agents Operational)

```
Sunday Evening:
  Internal Data Collection Agent → writes internal-intelligence-YYYY-Wnn.md

Monday 6am UTC:
  1. Source Quality Monitor Agent (quick quality checks)
  2. External Data Collection (RSS, Reddit, competitor blogs)
  3. Content Analyzer Agent (reads external + internal data)
  4. Report Generation (Markdown + HTML/PDF)
  5. Email Delivery (Brevo)

First Monday of Month:
  Source Discovery Agent → finds new sources → updates config files
```

---

See [docs/agent-directory.md](docs/agent-directory.md) for detailed specifications.
