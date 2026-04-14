# Automated Product Intelligence System
## Agentic Research & Competitive Intelligence Platform

**Status:** Proposal
**Owner:** Product Management
**Last Updated:** 2026-03-31
**Version:** 1.2

---

## Executive Summary

An automated system that continuously monitors telecom fraud market landscape through RSS feeds, competitor analysis, social listening, and internal customer signals (Gong, Slack). Uses OpenAI for weekly collection/summarization and autonomous agents for deep investigation when anomalies are detected.

**Key Innovation:** Agentic triage layer that automatically investigates high-priority signals overnight, delivering actionable analysis instead of raw alerts.

**ROI:** Transforms 8+ hours/week of manual research into 30 minutes of report review. Early detection of competitive threats and market shifts.

**Cost:** ~$20-40/month (vs. PM time cost: ~$400/week)

---

## Problem Statement

### Current State (Manual Process):
- Inconsistent monitoring - depends on PM bandwidth
- 3-8 hours/week spent on research when done
- Often skipped during busy sprints
- Reactive - learn about competitor moves 2-3 months late
- Siloed sources - Reddit insights never correlated with Gong calls
- No historical tracking - can't see long-term trends

### Impact:
- **Competitive blindness:** Missed 4 competitor fraud detection launches in Q4 2025
- **Customer churn risk:** Customers asking about competitor features we weren't tracking
- **Strategic lag:** Product roadmap decisions made on stale market intel
- **Lost opportunities:** Market trends identified too late to capitalize

---

## Solution Architecture

### Three-Layer System:

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: COLLECTION (Automated, Weekly)                │
│  ─────────────────────────────────────────              │
│  • RSS feeds (industry news)                            │
│  • Competitor blog scrapers                             │
│  • Reddit/social listening                              │
│  • Slack VOC channels                                   │
│  • Gong call transcripts                                │
│  Storage: /research/raw-data/YYYY-MM-DD.json            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: INITIAL ANALYSIS (OpenAI GPT-4)              │
│  ────────────────────────────────────────              │
│  • Summarize by source type                             │
│  • Group by themes                                      │
│  • Detect anomalies (>2σ from baseline)                 │
│  • Flag high-priority signals                           │
│  • Compare week-over-week                               │
│  Output: /research/weekly-reports/YYYY-MM-DD.md         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
          ┌─────────┴──────────┐
          │ Threshold Check    │
          │ High Priority?     │
          └─────────┬──────────┘
                    │
        ┌───────────┴────────────┐
        │ NO                YES  │
        ▼                        ▼
┌──────────────┐    ┌─────────────────────────────────────┐
│  Email Only  │    │ LAYER 3: AUTONOMOUS INVESTIGATION   │
│              │    │ (Claude Agent via Bedrock)          │
└──────────────┘    │ ────────────────────────────────    │
                    │ • Deep scrape triggered sources     │
                    │ • Cross-reference internal data     │
                    │ • Correlation analysis              │
                    │ • Strategic implications            │
                    │ • Action recommendations            │
                    │ Output: /research/investigations/   │
                    └─────────────────────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │  Monday Morning Delivery            │
                    │  • Weekly summary email             │
                    │  • + Investigation memo (if any)    │
                    └─────────────────────────────────────┘
```

---

## Layer Details

### Layer 1: Data Collection

**Schedule:** Weekly (Monday 6am UTC)
**Duration:** 20-30 minutes (including agent discovery)
**Technology:** GitHub Actions + Python + Claude Agent

**Data Sources by Phase:**

#### MVP (Phase 1) Sources:

| Source | What We Track | Update Frequency | Method | Phase |
|--------|---------------|------------------|--------|-------|
| **Industry RSS** | Telecom fraud news, regulations, market trends | Weekly | RSS (feedparser) | MVP |
| **Reddit Search** | "Twilio SMS pumping", "telecom fraud" mentions | Last 7 days | SociaVault API or praw | MVP |
| **Competitor Discovery** | Site structure mapping for 2 competitors | One-time discovery | Claude Agent | MVP |

#### Phase 2+ Sources:

| Source | What We Track | Update Frequency | Method | Phase |
|--------|---------------|------------------|--------|-------|
| **Competitor Content** | Blog posts, product updates from mapped sites | Weekly | BeautifulSoup | Phase 2 |
| **Slack VOC** | #customer-feedback, #product-requests channels | Last 7 days | Slack API | Phase 2 |
| **Gong Calls** | Customer calls mentioning fraud, competitors | Last 7 days | Gong API | Phase 2 |
| **Additional Reddit** | Expand to 3-5 queries across subreddits | Last 7 days | SociaVault/praw | Phase 2 |

---

#### Competitor Discovery Agent (MVP Feature)

**Purpose:** Automatically map competitor web presence to understand their information architecture

**Why this matters:**
- Different competitors organize content differently
- Manual discovery is time-consuming and incomplete
- Site structures change over time
- Enables targeted content collection in Phase 2

**Agent Task:** Given competitor name (e.g., "Sinch"), discover and catalog key pages

**Discovery Workflow:**
```
Input: Competitor name + domain (e.g., "Sinch", "sinch.com")
↓
Agent autonomously:
1. Start at homepage
2. Find navigation menus, footer links, sitemap
3. Identify key page categories:
   - Blog/News (for product updates)
   - Pricing (for competitive pricing intel)
   - Products/Solutions (for feature comparison)
   - API Documentation (for technical competitive analysis)
   - About/Company (for company positioning)
   - Resources/Case Studies (for customer use cases)
4. Follow links to verify page types
5. Extract RSS feeds if available
6. Check robots.txt for scraping permissions
↓
Output: Competitor site map JSON
```

**Example Output:**
```json
{
  "competitor": "Sinch",
  "domain": "sinch.com",
  "discovered_at": "2026-03-31T10:00:00Z",
  "pages": {
    "blog": {
      "url": "https://sinch.com/blog/",
      "rss_feed": "https://sinch.com/blog/feed/",
      "post_count": 150,
      "last_updated": "2026-03-30",
      "topics": ["SMS", "Voice", "Verification"]
    },
    "pricing": {
      "url": "https://sinch.com/pricing/",
      "has_structured_data": true,
      "products_found": ["SMS", "Voice", "Email"]
    },
    "api_docs": {
      "url": "https://developers.sinch.com/docs/",
      "sections": ["SMS API", "Voice API", "Verification API"]
    },
    "products": {
      "sms": "https://sinch.com/products/sms/",
      "voice": "https://sinch.com/products/voice/",
      "fraud_detection": "https://sinch.com/products/fraud-guard/"
    },
    "case_studies": {
      "url": "https://sinch.com/case-studies/",
      "count": 45
    }
  },
  "compliance": {
    "robots_txt": "https://sinch.com/robots.txt",
    "scraping_allowed": true,
    "rate_limit_recommended": "10 seconds"
  }
}
```

**Agent Tools Available:**
- `navigate(url)` - Fetch and parse HTML
- `extract_links(page, type)` - Find links by category
- `check_rss(url)` - Verify RSS feed existence
- `fetch_robots_txt(domain)` - Get scraping rules
- `verify_page_type(url)` - Confirm page content type

**MVP Scope:** 2 competitors (e.g., Sinch, Vonage)
- One-time discovery run during MVP setup
- Stored in `config/competitor-maps/`
- Used by Phase 2 content scrapers
- Re-run quarterly or when site structure changes

**Benefits:**
- Automated vs 2-3 hours manual per competitor
- Complete coverage (humans miss pages)
- Documents compliance rules
- Enables intelligent content collection

**Cost:** ~$2-3 per competitor (Claude API for discovery)

---

#### Reddit Collection (MVP Feature)

**Purpose:** Monitor social discussions about your products and problem space

**Implementation Options:**

**Option A: SociaVault API (Recommended if available)**
```python
# Using SociaVault
import requests

response = requests.get(
    'https://api.sociavault.com/v1/scrape/reddit/search',
    headers={'X-API-Key': 'sk_live_xxxxx'},
    params={
        'query': 'Twilio SMS pumping',
        'timeframe': 'week',
        'sort': 'relevance',
        'trim': 'true'
    }
)
```

**Option B: Direct Reddit API**
```python
# Using PRAW (Reddit API)
import praw

reddit = praw.Reddit(
    client_id='your_client_id',
    client_secret='your_secret',
    user_agent='TwilioProductResearch/1.0'
)

results = reddit.subreddit('telecom+fraud+voip').search(
    'Twilio SMS pumping',
    time_filter='week',
    limit=50
)
```

**MVP Query:** Single search term
- "Twilio SMS pumping" OR "telecom fraud" (choose most relevant)
- Timeframe: Last 7 days
- Subreddits: All (unrestricted search)

**What We Extract:**
- Post title, author, subreddit
- Score (upvotes), comment count
- Post content/body
- URL for reference
- Timestamp

**Phase 2 Expansion:**
- 3-5 different queries
- Specific subreddit targeting (r/telecom, r/fraud, r/voip)
- Sentiment analysis on comments
- Trend detection (volume changes week-over-week)

---

**Weekly Collection Output Format (MVP):**
```json
{
  "collected_at": "2026-03-31T06:00:00Z",
  "week_number": 14,
  "sources": {
    "rss_articles": [
      {
        "source": "Telecom Reseller",
        "title": "New SMS Fraud Regulations in EU",
        "url": "https://...",
        "published": "2026-03-29",
        "summary": "..."
      }
    ],
    "reddit_mentions": [
      {
        "query": "Twilio SMS pumping",
        "subreddit": "r/telecom",
        "title": "Anyone else seeing SMS fraud spike?",
        "author": "user123",
        "score": 45,
        "comments": 23,
        "url": "https://reddit.com/...",
        "snippet": "We've been hit with traffic pumping attacks..."
      }
    ],
    "competitor_maps": [
      {
        "competitor": "Sinch",
        "pages_discovered": 8,
        "has_rss": true,
        "scraping_allowed": true
      },
      {
        "competitor": "Vonage",
        "pages_discovered": 6,
        "has_rss": false,
        "scraping_allowed": true
      }
    ]
  },
  "metadata": {
    "total_items": 47,
    "rss_articles_count": 32,
    "reddit_posts_count": 15,
    "competitors_mapped": 2,
    "collection_duration_seconds": 1845
  }
}
```

---

### Layer 2: Initial Analysis (OpenAI)

**Schedule:** Immediately after collection
**Duration:** 5-10 minutes
**Technology:** OpenAI GPT-4 Turbo
**Cost:** ~$2-5/week

**Analysis Pipeline:**

1. **Summarization Pass**
   - Condense each article/post/call to key points
   - Extract: main topic, sentiment, entities (companies, products)

2. **Thematic Grouping**
   - Cluster by topic: market trends, competitor moves, customer feedback, regulatory
   - Identify emerging themes

3. **Anomaly Detection**
   - Compare to historical baseline (past 12 weeks)
   - Flag: unusual volume, sentiment shifts, new topics
   - Triggers:
     - >3 competitors mentioning same feature
     - >2σ increase in negative sentiment
     - New product category appearing >5 times

4. **Week-over-Week Analysis**
   - What changed vs. last week
   - Trending up/down topics
   - New entrants or exits

5. **Priority Classification**
   ```
   [HIGH]: Immediate competitive threat, major customer issue
   [MEDIUM]: Worth monitoring, emerging trend
   [LOW]: Business as usual, no action needed
   ```

**Output:** Structured markdown report

---

### Layer 3: Autonomous Investigation Agent

**Trigger:** HIGH priority signals from Layer 2
**Schedule:** Immediately after Layer 2 flags issue
**Duration:** 30-60 minutes
**Technology:** Claude Sonnet 4.6 via Bedrock (Agent SDK)
**Cost:** ~$5-10 per investigation

**Agent Capabilities:**

#### **Investigation Agent** (Autonomous Research Workflow)

**Trigger Examples:**
- "3 competitors launched fraud detection features this week"
- "Reddit sentiment on Twilio SMS pumping increased 300%"
- "5 Gong calls mentioned switching to competitor"

**Agent Workflow:**

```python
# Pseudo-code workflow
class InvestigationAgent:
    def investigate(self, trigger_signal):
        # 1. Deep source analysis
        detailed_data = self.scrape_sources(trigger_signal.entities)

        # 2. Cross-reference internal data
        relevant_calls = self.search_gong(trigger_signal.keywords)
        slack_history = self.search_slack_history(trigger_signal.keywords)

        # 3. Historical context
        past_patterns = self.query_research_archive(trigger_signal.topic)

        # 4. Competitive positioning
        feature_comparison = self.compare_features(trigger_signal.products)

        # 5. Strategic analysis
        implications = self.analyze_implications(
            detailed_data,
            relevant_calls,
            slack_history,
            past_patterns,
            feature_comparison
        )

        # 6. Generate recommendations
        action_plan = self.recommend_actions(implications)

        return InvestigationMemo(
            trigger=trigger_signal,
            findings=detailed_data,
            cross_references={
                'gong': relevant_calls,
                'slack': slack_history,
                'historical': past_patterns
            },
            competitive_analysis=feature_comparison,
            implications=implications,
            recommended_actions=action_plan
        )
```

**Agent Tools Available:**
- `web_scrape(url)` - Deep scrape competitor pages, docs, pricing
- `search_gong(query, date_range)` - Semantic search across call transcripts
- `search_slack(channel, query, date_range)` - Historical Slack search
- `query_archive(topic)` - Search past weekly reports
- `extract_features(url)` - Parse product feature lists
- `compare_competitors(features_dict)` - Competitive matrix builder
- `sentiment_analysis(text_list)` - Aggregate sentiment
- `summarize_findings(data)` - Executive summary generator

**Investigation Output Structure:**
```markdown
# Investigation: [Trigger Topic]
**Date:** 2026-03-24
**Trigger:** 3 competitors launched fraud detection features
**Priority:** HIGH

## Executive Summary
[2-3 sentence TL;DR]

## What Happened
[Timeline of events, who did what when]

## Deep Dive: Competitor Features
### Sinch Fraud Guard
- Launched: March 20, 2026
- Features: Real-time detection, ML-based, $0.002/check
- Target customers: Enterprise
- Source: [link]

### Vonage Fraud Shield
[similar breakdown]

## Internal Cross-References
### Gong Calls (4 relevant calls found)
- Call #1234: Customer asked about Sinch features (Jan 2026)
- Call #2345: Objection handling - competitor pricing
[...]

### Slack VOC (12 relevant messages)
- #customer-feedback: 3 customers requested similar features
- Timeline shows requests started Q4 2025

## Historical Context
- Similar competitive wave in Q2 2025 (launched A2P 10DLC)
- Our response time then: 8 weeks
- Market share impact: -2%

## Competitive Gap Analysis
| Feature | Twilio | Sinch | Vonage | Bandwidth |
|---------|--------|-------|--------|-----------|
| Real-time detection | Yes | Yes | Yes | No |
| ML-based | No | Yes | Yes | No |
| Price/check | $0.003 | $0.002 | $0.0025 | - |

**Our Gap:** ML-based detection, pricing 20-50% higher

## Strategic Implications
1. **Immediate risk:** 3 enterprise customers in renewal cycle
2. **Market positioning:** Now trailing in feature parity
3. **Pricing pressure:** May need to adjust
4. **Timeline pressure:** Competitors moved in coordinated wave

## Recommended Actions
### Immediate (This week)
- [ ] Sales enablement: competitive battle card update
- [ ] Reach out to 3 at-risk customers
- [ ] Pricing committee review

### Short-term (2-4 weeks)
- [ ] Product: Fast-follow feature scope
- [ ] Marketing: messaging update
- [ ] Customer success: proactive outreach campaign

### Long-term (Quarter)
- [ ] ML-based detection roadmap
- [ ] Pricing strategy review
- [ ] Competitive monitoring automation improvements

## Attachments
- [Full competitor feature comparison spreadsheet]
- [Gong call excerpts]
- [Slack thread archives]
```

---

## Supporting Agent Systems

Beyond the weekly Investigation Agent, two additional agents provide system maintenance and evolution capabilities:

### Scout Agent (Source Discovery & Maintenance)

**Purpose:** Automatically discover, evaluate, and maintain data sources as the market evolves

**Trigger:** Monthly OR when entering new product area

**Problem it solves:**
- New competitors emerge that we're not monitoring
- New forums/communities become active
- Existing sources go inactive or change domains
- Niche but valuable sources get missed in manual research

**Agent Workflow:**

1. **Discovery Phase**
   - Given problem space (e.g., "telecom fraud", "SMS pumping")
   - Research relevant forums, blogs, communities
   - Identify new competitors in the space
   - Check industry directories and social media

2. **Evaluation Phase**
   For each discovered source:
   - **Activity level:** Posts/updates per week
   - **Relevance score:** % of content matching keywords (1-10)
   - **Accessibility:** API available? RSS feed? Requires scraping?
   - **Authority:** Established source vs new/unverified
   - **Cost:** Free vs paid access

3. **Testing Phase**
   - Test API endpoints if available
   - Check RSS feed validity
   - Verify scraping feasibility (see Compliance Agent)
   - Measure response time and reliability

4. **Recommendation Output**
   ```markdown
   # Source Discovery Report - March 2026

   ## New Sources Recommended (3)

   ### VoIP Security Alliance Forum
   - URL: voipsec.org/forum
   - Activity: 45 posts/week
   - Relevance: 8/10 (high focus on fraud)
   - Access: RSS feed available
   - Recommendation: ADD to weekly collection
   - Priority: HIGH

   ### CallGuard Blog
   - URL: callguard.io/blog
   - Activity: 2 posts/week
   - Relevance: 7/10
   - Access: Must scrape (no RSS)
   - Compliance: See Compliance Agent report
   - Recommendation: ADD with monitoring
   - Priority: MEDIUM

   ## Sources to Remove (1)

   ### VoIP Forum
   - Reason: No activity in 4 months
   - Last useful post: Nov 2025
   - Recommendation: REMOVE from monitoring

   ## Sources Requiring Updates (2)

   ### MessageBird Blog
   - Issue: Domain changed
   - Old: messagebird.com/blog
   - New: messagebird.com/resources/blog
   - Action: Update collection script URL
   ```

**Value:**
- Keeps source list current without manual research
- Discovers niche sources humans might miss
- Prevents wasted effort on dead sources
- Adapts as market landscape evolves

**Frequency:** Monthly (first Monday of each month)

**Cost:** ~$3-5 per run (Claude API for research + evaluation)

---

### Compliance Guardian Agent

**Purpose:** Ensure legal and ethical compliance for all data collection methods

**Trigger:**
- Before adding any new source
- Monthly audit of existing sources
- When scraper failures suggest blocking

**Problem it solves:**
- Web scraping can violate Terms of Service
- robots.txt rules change without notice
- Legal/ethical boundaries unclear
- Risk of IP blocking or legal notices

**Agent Capabilities:**

#### 1. robots.txt Compliance Checker
```python
For each source requiring web scraping:
- Fetch robots.txt file
- Parse rules for our user-agent
- Check rate limit specifications
- Verify allowed/disallowed paths
- Flag violations
```

**Example Output:**
```
Source: sinch.com/blog
- robots.txt: https://sinch.com/robots.txt
- Status: Allows all user-agents for /blog/*
- Rate limit: None specified
- Compliance: GREEN - scraping permitted
- Recommendation: Proceed with rate limiting (10 sec between requests)

Source: vonage.com/blog
- robots.txt: Disallows /blog/ for automated bots
- Compliance: RED - scraping not permitted
- Alternative found: RSS feed at vonage.com/feed
- Recommendation: Switch from scraping to RSS feed
```

#### 2. Terms of Service Analyzer
```python
- Fetch and read ToS/Privacy Policy
- Extract clauses about automated access
- Identify prohibitions or requirements
- Check for API terms and application process
- Monitor for ToS updates
```

**Example Analysis:**
```
Source: Bandwidth.com
- ToS last updated: 2026-01-15
- Relevant clause: "Automated scraping prohibited without written consent"
- API available: Yes (public API, free tier)
- Compliance: RED for scraping, GREEN for API
- Recommendation: Apply for API key, halt scraping
- Action: API application submitted 2026-03-01
```

#### 3. Access Method Classification

For each source, determines optimal access method:

| Access Method | Compliance | Reliability | Cost |
|---------------|------------|-------------|------|
| **Official API** | GREEN | High | Varies |
| **RSS Feed** | GREEN | High | Free |
| **Allowed Scraping** | YELLOW | Medium | Free |
| **Prohibited Scraping** | RED | N/A | Legal risk |
| **Paywalled** | RED | N/A | $ + compliance |

#### 4. Rate Limit Monitor
```python
- Track request frequency per source
- Detect throttling or blocking
- Adjust delays to respect limits
- Alert when source becomes inaccessible
```

#### 5. Ethical Assessment
```python
- Public vs private content
- Copyright considerations
- PII/sensitive data concerns
- Competitive intelligence vs espionage boundary
```

**Monthly Compliance Report:**
```markdown
# Compliance Audit - March 2026

## Executive Summary
- Sources monitored: 12
- Compliant (GREEN): 10
- Violations found (RED): 2
- Changes detected: 3
- Actions required: 2

## Critical Issues

### VIOLATION: Bandwidth.com Blog
**Problem:** robots.txt updated March 10 to disallow /blog/ path
**Current status:** We're still scraping (active violation)
**Risk level:** HIGH - could result in IP block or legal notice
**Alternative:** RSS feed available
**Action required:** Update collection script by EOW
**Owner:** Engineering

### CHANGE DETECTED: Telnyx ToS Updated
**Previous ToS:** No mention of automated access
**New ToS (March 15):** "Automated access prohibited without permission"
**Current status:** We're scraping (now violation)
**Risk level:** MEDIUM
**Action required:** Apply for API access, pause scraping until approved
**Status:** API application submitted March 20
**Owner:** Product

## Compliant Sources (10)

### API Access (3 sources)
- Reddit: Official API, rate limits respected
- Slack: Official API, authorized access
- Gong: Official API, licensed

### RSS Feeds (6 sources)
- Telecom Reseller
- Fierce Wireless
- Sinch Blog
- Light Reading
- TelecomTV
- VoIP Security Alliance

### Permitted Scraping (1 source)
- MessageBird Blog: robots.txt allows, ToS silent, rate limited

## Upcoming Actions
- [ ] Bandwidth: Switch to RSS by April 5
- [ ] Telnyx: Await API approval (est. April 15)
- [ ] Sinch: API key renewal June 2026
- [ ] All sources: Re-audit robots.txt April 30

## Recommendations
1. Prefer API > RSS > Scraping (in that order)
2. Set up automated robots.txt monitoring
3. Quarterly ToS review for all scraped sources
4. Document all API agreements in /docs/api-agreements/
```

**Integration with Collection Pipeline:**

```python
# Before collecting from any source
def collect_from_source(source):
    compliance_status = check_compliance(source)

    if compliance_status == "RED":
        log_error(f"Skipping {source} - compliance violation")
        send_alert(f"Compliance issue: {source}")
        return None

    if compliance_status == "YELLOW":
        # Proceed with extra caution
        apply_rate_limiting(delay=30)  # 30 sec between requests

    return fetch_data(source)
```

**Value:**
- Prevents legal/ToS violations
- Catches compliance changes automatically
- Reduces risk of IP blocking
- Documents decision trail for audits
- Guides toward more sustainable access methods

**Frequency:**
- New sources: Before first collection
- Existing sources: Monthly audit
- On-demand: When scraper fails

**Cost:** ~$2-3 per audit (Claude API for ToS analysis)

---

## Source Access Method Breakdown

Our system uses a hybrid approach with varying compliance profiles:

### Fully Compliant (No Scraping)
**RSS Feeds (6+ sources)**
- Designed for automated consumption
- Compliance: GREEN
- Reliability: HIGH
- Examples: Industry news sites, some competitor blogs

**Official APIs (4 sources)**
- Authorized access with proper credentials
- Compliance: GREEN
- Reliability: HIGH
- Examples: Reddit, Slack, Gong, (potential) competitor APIs

### Gray Area (Requires Monitoring)
**Web Scraping (2-3 sources)**
- Competitor blogs without RSS/API
- Using BeautifulSoup to parse HTML
- Compliance: YELLOW (requires ongoing monitoring)
- Risk: MEDIUM
- Mitigation:
  - Compliance Agent checks robots.txt before each addition
  - Respectful rate limiting (10-30 sec between requests)
  - Descriptive user-agent (not pretending to be browser)
  - Only public pages (no auth bypass)
  - Prefer alternatives when available

**Why scrape at all?**
- Some competitors don't offer RSS/API
- Need immediate detection of product launches
- Want structured data (features, pricing tables)
- RSS feeds often incomplete

**Responsible scraping practices:**
1. Check robots.txt FIRST (Compliance Agent)
2. Respect rate limits (1 request per 10-30 seconds)
3. Use honest user-agent: "TwilioProductResearch/1.0"
4. Cache results aggressively (don't re-scrape)
5. Monitor for access issues (may indicate blocking)
6. Switch to API/RSS as soon as available

---

## Agent Coordination Example

### Scenario: Entering New Product Area (Voice Fraud)

**Week 1: You trigger expansion:**
```
"We're expanding into voice fraud detection. Update research sources."
```

**Scout Agent activates (Monday):**
1. Researches voice fraud landscape
2. Discovers:
   - VoIP Security Alliance (forum with RSS)
   - ITSPedia blog (no RSS)
   - r/voip subreddit (has API)
   - 3 new competitors: VoiceLayer, CallGuard, FraudBuster
3. Evaluates each for activity and relevance
4. Generates recommendation report

**Compliance Agent reviews (Tuesday):**
```
VoIP Security Alliance
- Has RSS feed
- No ToS restrictions
- Compliance: GREEN → APPROVED

CallGuard Blog
- No RSS or API
- robots.txt: Allows scraping
- ToS: No restrictions found
- Compliance: YELLOW → APPROVED with monitoring

FraudBuster
- No RSS or API
- robots.txt: Disallows all bots
- ToS: Explicit scraping prohibition
- Compliance: RED → REJECTED
- Note: Could pursue partnership/API access
```

**You review and approve (Wednesday):**
- Add VoIP Security (RSS)
- Add CallGuard (scraping with monitoring)
- Skip FraudBuster (or reach out for partnership)

**Collection script auto-updates (Thursday):**
- New sources added to config
- Rate limiting configured for CallGuard
- Compliance checks scheduled

**Next Monday:**
- Weekly collection includes new voice fraud sources
- System now monitors both SMS and voice fraud spaces

**Month 2 audit:**
- Compliance Agent re-checks CallGuard
- Discovers they launched RSS feed
- Recommends switching from scraping to RSS
- Collection script updated automatically

---

## Benefits of Adaptive Source Management

1. **Market Coverage:** Don't miss emerging competitors or communities
2. **Compliance Assurance:** Automated legal/ethical boundary checking
3. **Efficiency:** Remove dead sources, optimize access methods
4. **Risk Mitigation:** Catch ToS changes before violations
5. **Adaptability:** System evolves with market landscape
6. **Documentation:** Clear audit trail for all decisions

---

## Data Flow Example

### Scenario: Competitive Feature Launch Wave

**Sunday Night:**
- Agent collects data: 47 articles, 12 competitor updates, 23 Reddit posts

**Monday 6-7am:**
- OpenAI analysis detects:
  - [HIGH PRIORITY]: "3 major competitors launched fraud detection features within 48 hours"
  - Anomaly score: 4.2σ above baseline (highly unusual)

**Monday 7-8am:**
- Investigation Agent triggered automatically
- Scrapes: Sinch blog, Vonage docs, MessageBird pricing
- Searches: 147 Gong calls (finds 4 relevant)
- Searches: Slack history (finds 12 customer requests)
- Analyzes: Past competitive responses, market impact
- Generates: 5-page investigation memo

**Monday 9am:**
- **Email arrives in your inbox:**
  - Subject: "[HIGH PRIORITY] Weekly Intelligence + Investigation"
  - Body:
    - Weekly summary (normal)
    - **+ Investigation memo attached**
    - **+ Key finding: 3 at-risk customers identified**

**Monday 9:30am:**
- You read investigation memo (10 minutes)
- Have all context needed for leadership discussion
- Action items already scoped
- Can immediately engage sales/product teams

**Monday 10am:**
- Leadership meeting: Present findings with full context
- Decision made: Fast-follow strategy approved
- **Total time from signal to action: 4 hours (vs. 2-3 weeks previously)**

---

## Success Metrics

### Efficiency Metrics:
- **Time saved:** 6-8 hours/week → 30 min/week (92% reduction)
- **Coverage:** 5 sources manually → 15+ sources automated
- **Consistency:** Ad-hoc → 100% weekly execution
- **Response time:** 2-3 weeks → <24 hours for high-priority signals

### Business Impact Metrics:
- **Early detection:** Competitor moves detected within 1-3 days
- **Customer retention:** Identify at-risk accounts before churn
- **Roadmap alignment:** Data-driven prioritization decisions
- **Competitive win rate:** Track impact on sales outcomes

### Quality Metrics:
- **Signal accuracy:** % of HIGH priority flags that led to action
- **Investigation quality:** PM rating of agent memo usefulness (1-5)
- **False positive rate:** HIGH priority flags that were non-issues
- **Coverage gaps:** Important signals that system missed

**Success Criteria (3 months):**
- [ ] 80% of HIGH priority investigations rated 4+ stars
- [ ] <20% false positive rate on HIGH priority flags
- [ ] 2+ strategic decisions informed by system insights
- [ ] $0 cost overruns (stay within $40/month budget)

---

## Implementation Plan

### Phase 1: MVP (Week 1-2)
**Goal:** Prove basic automation works with three source types

**Scope:**
- **RSS feeds:** 10+ industry news sources
- **Reddit search:** 1 query via SociaVault or Reddit API (e.g., "Twilio SMS pumping")
- **Competitor Discovery Agent:** Map 2 competitors' web presence
  - Agent discovers key pages: blog, pricing, API docs, features, about
  - Catalogs URLs for future content scraping
  - Does NOT scrape content yet (just discovery)
- **OpenAI summarization:** Analyze collected data
- **Email delivery:** Weekly report

**Deliverables:**
- GitHub Actions workflow running
- First weekly email delivered
- Raw data stored in repo
- Competitor site map for 2 companies (e.g., Sinch, Vonage)

**Success:** Email arrives Monday morning with useful summary from all three source types

---

### Phase 2: Full Collection (Week 3-4)
**Goal:** Add internal data sources and expand coverage

**Scope:**
- Competitor content scraping (use site maps from MVP)
  - Scrape blog posts from discovered URLs
  - Monitor pricing pages for changes
  - Track product/feature pages
- Expand Reddit to 3-5 queries across targeted subreddits
- Slack VOC integration (#customer-feedback, #product-requests)
- Gong API connection (if available)
- Historical trending (compare week-over-week)

**Deliverables:**
- Content scrapers using MVP competitor maps
- Comprehensive data collection pipeline
- Structured JSON storage with versioning
- Enhanced email report with trends

**Success:** All sources collecting data weekly, trend detection working

---

### Phase 3: Agent Layer (Week 5-6) [KEY PHASE]
**Goal:** Autonomous investigation capability

**Scope:**
- Anomaly detection thresholds
- Investigation Agent implementation
- Tool suite (scraping, search, analysis)
- Investigation memo generation

**Deliverables:**
- Agent workflow deployed
- First investigation memo generated
- Integration with weekly email

**Success:** Agent successfully investigates first HIGH priority signal

---

### Phase 4: Refinement (Week 7-8)
**Goal:** Tune and optimize

**Scope:**
- Adjust anomaly thresholds based on false positives
- Improve investigation agent prompts
- Add historical trending
- Better email formatting

**Deliverables:**
- Tuned system based on 4+ weeks of data
- Documentation for team
- Onboarding guide

**Success:** <20% false positive rate, 80%+ satisfaction rating

---

### Phase 5: Adaptive Systems (Month 3+)
**Goal:** Self-maintaining and evolving system

**Scope:**
- Scout Agent (source discovery & maintenance)
- Compliance Guardian Agent (automated compliance monitoring)
- Dashboard (optional)
- Additional data sources (Twitter, LinkedIn, patents)
- Predictive trending (ML on historical data)
- Multi-agent workflows (parallel investigations)
- Integration with product roadmap tools

**Deliverables:**
- Monthly Scout Agent runs
- Monthly Compliance audits
- Automated source list updates
- Compliance violation alerts

**Success:** System discovers 2+ new valuable sources, maintains 100% compliance

**Future State:** Fully autonomous, self-maintaining competitive intelligence system

---

## Technical Stack

### Infrastructure:
- **Orchestration:** GitHub Actions (free tier: 2000 min/month)
- **Storage:** Git repo + JSON files (simple, version-controlled)
- **Hosting:** GitHub (no additional hosting needed)

### APIs & Services:
- **OpenAI:** GPT-4 Turbo ($0.01/1K input, $0.03/1K output)
- **Claude (Bedrock):** Sonnet 4.6 (existing access)
- **Brevo:** Email delivery (formerly Sendinblue, free tier: 300/day)
- **Reddit:** praw library (free API)
- **Slack:** Official API (free)
- **Gong:** REST API (if available via Twilio license)

### Languages & Libraries:
- **Python 3.11+**
- **Key packages:**
  - `openai` - GPT-4 API
  - `anthropic` / AWS SDK - Claude Bedrock
  - `feedparser` - RSS feeds
  - `beautifulsoup4` + `requests` - Web scraping
  - `praw` - Reddit API
  - `slack-sdk` - Slack integration
  - `sib-api-v3-sdk` - Brevo email delivery
  - `aiohttp` - Async HTTP requests

### Agent Framework:
- **Option A:** Claude Agent SDK (recommended)
- **Option B:** LangChain + Claude
- **Option C:** Custom agentic loop with tool calling

---

## Cost Analysis

### Monthly Operating Costs:

| Component | Cost | Notes |
|-----------|------|-------|
| **GitHub Actions** | $0 | Within free tier (2000 min/month) |
| **OpenAI GPT-4** | $8-15 | ~20K tokens/week × 4 weeks |
| **Claude - Competitor Discovery** | $4-6 | One-time MVP: 2 competitors @ $2-3 each |
| **Claude Investigations** | $10-20 | 2-4 investigations/month @ $5 each (Phase 3+) |
| **SociaVault (Reddit)** | $0-5 | If used; or Reddit API (free) |
| **Scout Agent** | $3-5 | Monthly source discovery (Phase 5+) |
| **Compliance Agent** | $2-3 | Monthly compliance audit (Phase 5+) |
| **Brevo** | $0 | <300 emails/month (free tier) |
| **Reddit API** | $0 | Free tier (if not using SociaVault) |
| **Slack API** | $0 | Included (Phase 2+) |
| **Gong API** | $0 | Existing Twilio license (Phase 2+) |
| **Total (MVP/Phase 1)** | **$12-26/month** | RSS + Reddit + Competitor Discovery |
| **Total (Phase 2-4)** | **$18-35/month** | + Internal sources, no Investigation Agent yet |
| **Total (Phase 3+)** | **$28-55/month** | + Investigation Agent |
| **Total (Phase 5+)** | **$33-63/month** | + Adaptive agents |

### Cost vs. Value:

**PM Time Saved:**
- 8 hours/week × 4 weeks = 32 hours/month
- PM hourly rate: ~$75/hour (loaded cost)
- **Value: $2,400/month**

**ROI: 8,000% (80x return)**

### Cost Controls:
- OpenAI: Cache summaries, batch processing
- Claude: Only trigger on HIGH priority (2-4x/month, not every week)
- APIs: Stay within free tiers
- Storage: Git repo (free, unlimited for text)

**Budget ceiling:**
- MVP/Phase 1: $30/month
- Phase 2-4: $40/month
- Phase 3+ (with Investigation Agent): $60/month
- Phase 5+ (with all agents): $70/month

---

## Risks & Mitigations

### Technical Risks:

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **API rate limits** | Collection fails | Medium | Retry logic, respectful rate limiting |
| **Web scraping breaks** | Missing competitor data | High | Graceful degradation, alerts on failure |
| **False positives** | Alert fatigue | Medium | Tunable thresholds, feedback loop |
| **Agent hallucination** | Wrong conclusions | Low | Fact-checking layer, cite sources |
| **Cost overrun** | Budget exceeded | Low | Hard caps, monitoring, alerts |

### Operational Risks:

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Data sensitivity** | Leak internal data | Low | Sanitize before external API calls |
| **Dependency on GitHub** | System unavailable | Low | Can migrate to AWS Lambda |
| **Maintenance burden** | Becomes time sink | Medium | Clear documentation, simple architecture |
| **Team adoption** | Not used | Medium | Weekly review meetings, iterate on feedback |

### Ethical/Legal Risks:

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Scraping ToS violations** | Legal issues | Low | Check robots.txt, respect rate limits |
| **Customer data privacy** | Compliance violation | Medium | Anonymize Gong/Slack data, PII redaction |
| **Competitive intel ethics** | Reputation risk | Low | Public sources only, no espionage |

---

## Open Questions

### Technical:
- [ ] Gong API access level - do we have what we need?
- [ ] Slack bot permissions - need approval from IT?
- [ ] GitHub Actions runner - do we need private repo?
- [ ] Claude Bedrock access - can we call from GitHub Actions?

### Product:
- [ ] Agent decision threshold - how aggressive should triggers be?
- [ ] Email recipients - who gets weekly report?
- [ ] Investigation depth - how far should agent dig?
- [ ] Historical data - how far back to analyze?
- [ ] Scout Agent frequency - monthly or triggered by events?
- [ ] Compliance threshold - auto-reject RED sources or flag for manual review?
- [ ] Source approval workflow - who approves new sources discovered by Scout Agent?

### Process:
- [ ] Who owns system maintenance?
- [ ] How often to review/tune thresholds?
- [ ] What happens when agent finds critical issue on Friday night?
- [ ] Integration with existing product processes?

---

## Next Steps

### Immediate (This week):
1. **Review & align:** Get feedback on this proposal
2. **Access check:**
   - Verify Bedrock access (for Competitor Discovery Agent)
   - Check if SociaVault access exists, else use Reddit API
   - Confirm RSS feed availability for target sources
3. **Select competitors:** Choose 2 competitors for MVP discovery (e.g., Sinch, Vonage)
4. **Approve budget:** Get $70/month budget approval (covers through Phase 5)

### Week 1-2 (Phase 1 MVP):
1. Set up GitHub Actions workflow
2. Implement RSS collection (10+ sources)
3. Implement Reddit search (1 query via SociaVault or Reddit API)
4. Deploy Competitor Discovery Agent (map 2 competitor sites)
5. OpenAI summarization (all 3 source types)
6. Email delivery
7. **Deliver first weekly email with RSS + Reddit + Competitor maps**

### Week 3-4 (Phase 2):
1. Add remaining data sources
2. Structured data storage
3. Enhanced reporting

### Week 5-6 (Phase 3):
1. Implement Investigation Agent
2. Test on historical high-priority signals
3. Deploy to production

### Month 3:
1. Evaluate results
2. Tune based on feedback
3. Decide on Phase 5 scope

---

## Appendix

### A. Example Data Sources

**Industry RSS Feeds:**
- Telecom Reseller: https://telecomreseller.com/feed/
- Fierce Wireless: https://www.fiercewireless.com/rss
- Telecompaper: https://www.telecompaper.com/rss
- Light Reading: https://www.lightreading.com/rss
- TelecomTV: https://www.telecomtv.com/feed

**Competitor Sites:**
- Sinch: https://www.sinch.com/blog/
- Vonage: https://www.vonage.com/blog/
- Bandwidth: https://www.bandwidth.com/blog/
- MessageBird: https://messagebird.com/blog/
- Telnyx: https://telnyx.com/resources/blog

**Reddit Communities:**
- r/telecom
- r/fraud
- r/voip
- r/entrepreneur
- r/sales (for SaaS discussions)

### B. Example Agent Prompts

**Investigation Trigger Prompt:**
```
You are a competitive intelligence analyst for Twilio.

This week's automated scan detected a HIGH PRIORITY signal:
"3 competitors (Sinch, Vonage, MessageBird) launched fraud detection features within 48 hours"

Your task: Conduct a deep investigation and deliver an actionable memo.

Available tools:
- web_scrape(url): Deep scrape any URL
- search_gong(query, days_back): Search call transcripts
- search_slack(channel, query, days_back): Search Slack history
- query_archive(topic, months_back): Search past research
- compare_competitors(features_dict): Generate comparison table

Investigation checklist:
1. What exactly did each competitor launch? (features, pricing, positioning)
2. Have our customers asked for these features? (check Gong, Slack)
3. Has this happened before? (check archive)
4. What's our competitive gap? (feature comparison)
5. What should we do? (strategic recommendations)

Output format: Investigation memo (see template)

Begin investigation.
```

### C. Investigation Memo Template

```markdown
# Investigation: [Topic]
**Date:** YYYY-MM-DD
**Trigger:** [What caused this investigation]
**Priority:** [HIGH / MEDIUM / LOW]

## Executive Summary
[2-3 sentences: what happened, why it matters, what to do]

## What Happened
[Timeline, who did what when]

## Deep Dive
[Detailed analysis by entity/competitor]

## Internal Cross-References
### Gong Calls
[Relevant customer conversations]

### Slack VOC
[Related feedback/requests]

## Historical Context
[Have we seen this before? What happened then?]

## Competitive Analysis
[Feature/pricing comparison table]

## Strategic Implications
[Why this matters for our business]

## Recommended Actions
### Immediate (This week)
- [ ] Action 1
- [ ] Action 2

### Short-term (2-4 weeks)
- [ ] Action 3

### Long-term (Quarter)
- [ ] Action 4

## Supporting Data
[Links, screenshots, excerpts]
```

---

## Document Control

**Change Log:**

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-03-27 | 1.0 | PM | Initial proposal |
| 2026-03-30 | 1.1 | PM | Added Scout Agent and Compliance Guardian Agent sections; Updated cost analysis and implementation phases |
| 2026-03-31 | 1.2 | PM | Enhanced MVP to include Reddit search and Competitor Discovery Agent (2 competitors); Added detailed sections for both features; Updated Phase 2 scope and cost analysis |

**Review & Approval:**

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Manager | [Name] | Draft | - |
| Engineering Lead | [Name] | Pending | - |
| Data/Privacy | [Name] | Pending | - |
| Budget Approver | [Name] | Pending | - |

**Distribution:**
- Product Management
- Engineering
- Data & Privacy
- Finance (for budget approval)

---

**Questions or feedback?** Contact: [your-email]@twilio.com
