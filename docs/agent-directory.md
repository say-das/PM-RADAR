# PM Radar Agent Directory

**Last Updated:** 2026-04-07  
**Document Purpose:** Comprehensive list of all AI agents in the PM Radar system

---

## Core Intelligence Agents

### 1. Internal Data Collection Agent (Phase 3)
**Status:** NOT STARTED  
**Responsibility:** Gathers information from internal Twilio tools and platforms on a regular schedule:
- **Slack VOC Channel:** Monitors customer voice-of-customer discussions, extracts pain points, feature requests, and sentiment
- **Gong Calls:** Searches and analyzes sales/CS call transcripts for fraud-related discussions, customer concerns, competitive mentions
- **Marvin Reports:** Collects insights from internal product analytics and customer success reports
- **Other Internal Sources:** Jira tickets, support tickets, internal wikis

Aggregates findings by time period and writes to timestamped markdown files (e.g., `internal-intelligence-2026-W14.md`) for later consumption by Content Analyzer Agent.  
**Trigger:** Weekly (Sunday evening) before Content Analyzer runs  
**Technology:** Claude Sonnet 4.6 via AWS Bedrock  
**Output:** Timestamped markdown file with categorized internal intelligence (customer pain points, feature requests, competitive mentions, fraud trends)

---

## Discovery & Collection Agents

### 2. Source Discovery Agent (Phase 2)
**Status:** NOT STARTED  
**Responsibility:** Autonomously discovers new data sources via Google searches across three categories:
- **Competition:** Finds competitor pricing pages, blogs, changelogs, launch pages, API documentation URLs
- **Industry Analysts:** Discovers RSS feeds and feed pages from relevant analyst firms
- **Community Sources:** Identifies relevant forums, subreddits, and discussion platforms

After discovery, validates URLs are accessible and not already in source lists, then automatically updates the respective source configuration files.  
**Trigger:** Manual or scheduled (monthly)  
**Technology:** Claude Agent SDK  
**Output:** Updated source config files (competitors.json, rss-sources.json) with newly discovered URLs

---

## Quality & Compliance Agents

### 3. Source Quality Monitor Agent (Phase 3)
**Status:** NOT STARTED  
**Responsibility:** Regularly audits all configured sources and assigns quality and relevance scores:

**Quality Score (0-10):**
- RSS feed update frequency
- Link availability and uptime
- Scraping permissions (robots.txt compliance)
- Terms of Service analysis
- Rate limit considerations

**Relevance Score (0-10):**
- Content focus on telecom/communication fraud (high)
- General fraud content (medium)
- Non-fraud content (low)

Flags low-performing sources for review and recommends removal of consistently poor sources.  
**Trigger:** Weekly for quality checks, monthly for comprehensive audits  
**Technology:** Claude Agent SDK  
**Output:** Source quality report with scores, compliance status, and recommendations (KEEP/REVIEW/REMOVE)

---

## Analysis & Summarization (Non-Autonomous)

### 4. Content Analyzer Agent
**Status:** COMPLETE  
**Responsibility:** Analyzes collected data weekly. Categorizes content (Telecom Fraud, General Fraud, Competitive Intelligence), summarizes by topic, detects trends, generates executive summaries, and flags high-priority signals for Investigation Agent.  
**Trigger:** Weekly (Monday 6am UTC) after data collection  
**Technology:** OpenAI GPT-4o  
**Output:** Structured analysis JSON with summaries, trends, regulatory changes, and community sentiment

---

## Agent Summary by Phase

### Phase 1 (MVP) - COMPLETE
- None (manual skills only)

### Phase 2 (In Progress)
- Source Discovery Agent (Automated source discovery & addition)

### Phase 3 (Planned)
- Internal Data Collection Agent (Internal intelligence gathering)
- Source Quality Monitor Agent (Quality scoring & compliance)

### Phase 4 (Planned)
- None (optimization of existing agents)

### Phase 5 (Future)
- None (merged into earlier phases)

---

## Agent Interaction Map

```
Weekly Cycle:
1. Source Quality Monitor Agent (quality & relevance scoring)
   ↓
2. External Data Collection (automated scripts - Reddit, RSS, competitors)
   ↓
3. Internal Data Collection Agent (Slack VOC, Gong, Marvin → writes internal-intelligence-YYYY-Wnn.md)
   ↓
4. Content Analyzer Agent (reads external + internal data → categorizes & summarizes)
   ↓
5. Report Generation (Markdown + HTML with internal insights)
   ↓
6. Email Delivery (Brevo)

Monthly Maintenance:
1. Source Discovery Agent (Google search for new sources)
   ↓
2. URL validation & deduplication
   ↓
3. Auto-update source config files

As-Needed:
1. Source Quality Monitor Agent (comprehensive monthly audit)
```

---

## Agent Comparison

| Agent | Status | Autonomy Level | Frequency | Cost/Run |
|-------|--------|----------------|-----------|----------|
| Content Analyzer Agent | COMPLETE | Semi-automated | Weekly | $0.05-0.10 |
| Internal Data Collection Agent | NOT STARTED | Fully autonomous | Weekly | $3-5 |
| Source Discovery Agent | NOT STARTED | Fully autonomous | Monthly | $3-5 |
| Source Quality Monitor Agent | NOT STARTED | Fully autonomous | Weekly/Monthly | $2-4 |

---

## Key Capabilities by Agent

**Internal Data Collection Agent:**
- Slack VOC channel monitoring and extraction
- Gong call transcript search and analysis
- Marvin report aggregation
- Jira/support ticket analysis
- Internal wiki/documentation search
- Sentiment analysis of internal signals
- Timestamped markdown file generation
- Integration with internal Twilio APIs/tools

**Source Discovery Agent:**
- Google search automation (competition, analysts, community)
- Homepage navigation analysis
- Menu/footer link extraction
- Sitemap parsing
- RSS feed detection
- API documentation discovery
- Pricing page identification
- Changelog/launch page discovery
- URL validation and deduplication
- Automatic source config file updates

**Source Quality Monitor Agent:**
- RSS feed health monitoring (update frequency, uptime)
- Link availability testing
- robots.txt compliance checking
- Terms of Service analysis
- Rate limit detection
- Scraping permission verification
- Content relevance scoring (fraud focus)
- Quality scoring (0-10 scale)
- Source recommendation engine (KEEP/REVIEW/REMOVE)

---

## Future Agent Concepts (Not in Current Roadmap)

### Trend Prediction Agent
**Responsibility:** Uses ML on historical data to predict emerging fraud trends before they spike. Identifies weak signals and correlation patterns across multiple data sources.

### Competitive Pricing Agent
**Responsibility:** Monitors competitor pricing pages, tracks changes, analyzes pricing strategies, and alerts on significant pricing adjustments or new tier introductions.

### Customer Sentiment Agent
**Responsibility:** Aggregates sentiment across Gong, Slack, Reddit, and social media. Identifies sentiment shifts, correlates with product changes, and flags churn risk indicators.

### Market Opportunity Agent
**Responsibility:** Synthesizes intelligence across all sources to identify unmet market needs, competitive gaps, and whitespace opportunities for new product development.

---

## Implementation Priority

**Immediate (Next 4 weeks):**
1. Source Discovery Agent (Phase 2 - automated source expansion)

**Short-term (2-3 months):**
1. Internal Data Collection Agent (Phase 3 - internal intelligence gathering)
2. Source Quality Monitor Agent (Phase 3 - quality & compliance)

**Long-term (3-6 months):**
- Optimization and refinement of existing agents

---

## Notes

- All agents use Claude Sonnet 4.6 except Content Analyzer Agent (OpenAI GPT-4o)
- Agent costs are per-execution estimates
- Autonomous agents can operate overnight without human intervention
- All agent outputs are stored in git for audit trail
- Agents share common tool library (web scraping, API calls, Google search)
- Source Discovery Agent automatically updates config files without manual intervention
- Source Quality Monitor Agent provides both quick weekly checks and comprehensive monthly audits

---

**Document Owner:** Product Management  
**Review Frequency:** Monthly or when new agents added
