# PM Radar: Internal Product Intelligence Platform

**Status:** Vision Document
**Owner:** Product Management
**Last Updated:** 2026-04-03
**Version:** 2.1

---

## Executive Summary

PM Radar is an internal multi-workspace AI platform that automates product research for Twilio Product Managers. Each PM configures their own workspace to monitor industry trends, competitors, social conversations, and internal customer signals. The platform eliminates 10+ hours per week of manual research, delivering automated intelligence through weekly digests and real-time alerts.

**Core Value:** Transform manual, inconsistent research into automated, always-on intelligence gathering—customized for each PM's unique product area.

---

## The Problem: Why We Need This

### Current State of PM Research at Twilio

**Manual and Time-Consuming:**
- PMs spend 8-15 hours/week on competitive research, market monitoring, and customer feedback analysis
- Research is often skipped during busy sprints
- No systematic approach across product teams

**Inconsistent and Reactive:**
- Learn about competitor launches 2-3 weeks after they happen
- Customer pain points discovered through escalations, not proactive monitoring
- Market trends identified too late to influence roadmap

**Fragmented Data Sources:**
- Customer feedback scattered across Zendesk, Slack, Gong calls, G2 reviews
- Competitive intelligence requires manual website checking, blog reading
- Industry news spread across 20+ sources, no single view
- Reddit/social discussions never systematically monitored

**Lack of Cross-Referencing:**
- No correlation between competitor moves and customer asks
- Can't connect industry trends to internal feedback patterns
- Insights remain siloed by source type

**Impact on Product Strategy:**
- Roadmap decisions based on incomplete information
- Missed competitive threats and market opportunities
- Slow response to customer sentiment shifts
- Strategic decisions driven by gut feel, not data

### What Success Looks Like

**After PM Radar:**
- Monday morning: PM receives comprehensive weekly intelligence digest
- Real-time alerts when critical signals detected (competitor launch, sentiment spike)
- 30 minutes to review insights vs 8+ hours of manual research
- Data-driven roadmap discussions with cross-source correlation
- Early detection of competitive threats and customer needs
- Historical research archive for trend analysis

---

## The Solution: Automated Intelligence Platform

### Vision

PM Radar is a multi-workspace platform where each Twilio PM configures their own automated research system. Built on proven automation principles (validated with telecom fraud use case), the platform:

1. **Collects** data from configured sources (industry, competitive, social, internal)
2. **Analyzes** using AI to detect patterns, anomalies, and themes
3. **Investigates** high-priority signals autonomously with deep dives
4. **Synthesizes** insights across all sources with correlation analysis
5. **Delivers** actionable intelligence via Slack/email digests

Each workspace operates independently with isolated configurations and private data, while sharing the underlying automation infrastructure.

---

## Platform Architecture

### Multi-Workspace Model

```
PM Radar Platform
├── Workspace: Messaging Products (PM: Sarah)
│   ├── Monitors: Sinch, Vonage, MessageBird
│   ├── Sources: Telecom news, r/telecom, Zendesk
│   └── Weekly digest: Mondays 9am
├── Workspace: Voice Products (PM: Michael)
│   ├── Monitors: Twilio Flex competitors
│   ├── Sources: CCaaS news, Gong calls, G2 reviews
│   └── Weekly digest: Mondays 10am
└── Workspace: Authentication (PM: Alex)
    ├── Monitors: Auth0, Okta, FusionAuth
    ├── Sources: Security blogs, HackerNews, support tickets
    └── Weekly digest: Tuesdays 9am
```

**Key Principles:**
- Each workspace = independent research system
- Private data, isolated configurations
- Shared infrastructure, per-workspace execution
- Self-service workspace creation for PMs

---

## Data Sources by Category

### 1. Industry & Market Intelligence

**Purpose:** Track market trends, regulations, analyst reports, industry news

**Sources:**
- RSS feeds from industry publications
- Trade journals and news sites
- Research reports (Gartner, Forrester)
- Industry blogs and thought leaders
- Conference proceedings and webinars
- Patent filings and regulatory updates

**What We Extract:**
- Emerging trends and technologies
- Regulatory changes affecting products
- Market size and growth projections
- Industry pain points and opportunities

**Collection Frequency:** Daily aggregation, weekly synthesis

---

### 2. Competitive Intelligence

**Purpose:** Monitor competitor activities, product changes, strategic moves

**Sources:**
- Competitor websites and blogs
- Product documentation and changelogs
- Pricing pages
- Press releases and announcements
- Job postings (hiring signals)
- GitHub repositories (for technical products)
- Case studies and customer stories

**What We Extract:**
- New product launches and features
- Pricing changes
- Market positioning shifts
- Technical capabilities
- Target customer segments
- Strategic partnerships

**Collection Frequency:** Weekly scraping with change detection

**Automation Capabilities:**
- Competitor Discovery: AI automatically maps competitor web presence (blog, pricing, docs, API pages)
- Change Detection: Monitors for updates and new content
- Feature Comparison: Maintains comparison matrix
- Compliance Checking: Ensures ethical scraping practices

---

### 3. Social Listening

**Purpose:** Monitor online conversations, sentiment, emerging topics

**Sources:**
- Reddit (targeted subreddits)
- HackerNews discussions
- Twitter/X mentions
- LinkedIn posts
- ProductHunt launches
- Developer forums and communities
- Discord/Slack communities (public)

**What We Extract:**
- Product mentions and sentiment
- Customer pain points discussed publicly
- Competitive comparisons
- Feature requests from community
- Crisis detection (negative sentiment spikes)

**Collection Frequency:** Daily monitoring, real-time alerts for spikes

**Reddit Focus (MVP):**
- Keyword-based search (e.g., "Twilio SMS pumping", "telecom fraud")
- Subreddit targeting (r/telecom, r/voip, r/entrepreneur)
- Last 7 days of discussions
- Sentiment analysis on comments

---

### 4. Internal Customer Signals

**Purpose:** Aggregate internal customer feedback and sentiment

**Sources:**

**Zendesk (Support Tickets):**
- Recent tickets by product area
- Common issues and themes
- Escalations and severity trends
- Time-to-resolution patterns

**Slack VOC Channels:**
- #customer-feedback
- #product-requests
- #field-questions
- Product-specific channels

**Gong Call Transcripts:**
- Sales calls mentioning competitors
- Customer objections and concerns
- Feature requests from prospects
- Win/loss analysis themes

**Customer Reviews:**
- G2, Capterra, TrustRadius
- App Store and Play Store reviews
- Trustpilot and similar platforms

**What We Extract:**
- Top customer pain points
- Feature request patterns
- Sentiment trends over time
- Correlation with competitor mentions
- At-risk customer signals

**Collection Frequency:** Daily aggregation from all sources

---

## Automation Layers

### Layer 1: Data Collection

**Weekly Orchestration:**
- GitHub Actions or similar scheduler triggers Monday 6am
- Parallel collection from all configured sources
- Structured storage in workspace-specific folders
- Version control for historical tracking

**Capabilities:**
- RSS feed parsing
- API integrations (Reddit, Slack, Zendesk, Gong)
- Web scraping (where compliant)
- Rate limiting and respectful collection

---

### Layer 2: Analysis & Pattern Detection

**AI-Powered Analysis:**
- Summarize each source individually
- Group findings by themes (trends, competitor moves, customer feedback)
- Detect anomalies (unusual volume, sentiment shifts, new topics)
- Week-over-week comparison
- Priority classification (High/Medium/Low)

**Anomaly Triggers:**
- 3+ competitors mentioning same feature
- 2σ increase in negative sentiment
- New product category appearing 5+ times
- Sudden spike in support tickets
- Multiple customers requesting same feature

**Output:** Structured weekly report with prioritized insights

---

### Layer 3: Autonomous Investigation (Conditional)

**When Triggered:** High-priority signals from analysis layer

**Investigation Workflow:**
1. Deep scrape competitor pages mentioned in alert
2. Search Gong calls for related customer conversations
3. Search Slack history for relevant internal discussions
4. Query historical research archive for context
5. Cross-reference with past competitive responses
6. Generate detailed investigation memo with recommendations

**Example Investigation:**
- Alert: "3 competitors launched fraud detection features this week"
- Investigation: Scrape full feature details, find 4 Gong calls where customers asked about this, identify 3 at-risk accounts, draft competitive response strategy
- Deliverable: 5-page memo ready for Monday morning

**Value:** Transforms raw alerts into actionable strategy documents

---

### Layer 4: Source Discovery & Maintenance

**Automated Source Management:**

**Discovery:**
- Given product area, research and find relevant sources
- Evaluate activity level, relevance, credibility
- Test for API availability, RSS feeds
- Recommend additions/removals

**Compliance:**
- Check robots.txt before scraping
- Analyze Terms of Service for restrictions
- Monitor for ToS changes
- Flag violations, suggest alternatives
- Maintain ethical boundaries

**Frequency:** Monthly audits, on-demand for new product areas

---

## Workspace Configuration

### Setup (10 Minutes Per Workspace)

**Step 1: Product Profile**
- Product name: "Twilio Messaging"
- Problem space: "SMS fraud prevention, traffic pumping"
- Keywords: "SMS pumping, telecom fraud, A2P messaging"

**Step 2: Competitors (2-5)**
- Sinch, Vonage, Bandwidth, MessageBird, Telnyx
- AI automatically discovers their blog, pricing, docs pages

**Step 3: Industry Sources**
- Select from curated list or add custom RSS feeds
- Telecom Reseller, Fierce Wireless, etc.

**Step 4: Social Listening**
- Reddit queries: "Twilio SMS pumping", "telecom fraud"
- Subreddits: r/telecom, r/fraud, r/voip

**Step 5: Internal Integrations**
- Zendesk: Select product tags to monitor
- Slack: Choose channels (#messaging-feedback)
- Gong: Filter by product area

**Step 6: Schedule & Delivery**
- Digest frequency: Weekly (Monday 9am)
- Alert preferences: High-priority only via Slack
- Email recipients: PM + team leads

---

## User Experience

### Monday Morning Workflow

**9:00am - Email Arrives:**
Subject: "PM Radar Weekly Intelligence - Messaging Products"

**Email Contents:**

```
EXECUTIVE SUMMARY
- 3 high-priority signals this week
- 47 industry articles reviewed
- 15 Reddit discussions analyzed
- 2 competitor updates detected
- 23 Zendesk tickets reviewed

HIGH PRIORITY SIGNALS

[1] Competitor Product Launch
3 competitors (Sinch, Vonage, MessageBird) launched ML-based fraud
detection features within 48 hours. Investigation memo attached.
→ Action: Review competitive response strategy by EOW

[2] Customer Sentiment Shift
Reddit mentions of "Twilio SMS pumping" increased 300% this week.
Sentiment: 60% negative. Requires immediate attention.
→ Action: Review social response strategy

INDUSTRY TRENDS
- EU regulatory changes on SMS fraud (5 articles)
- A2P 10DLC adoption reaching 80% in US market
- New fraud patterns emerging in Asia-Pacific

COMPETITIVE INTELLIGENCE
- Sinch: New pricing page detected, launched tiered fraud protection
- Bandwidth: Hiring 3 fraud engineers (LinkedIn job postings)

CUSTOMER FEEDBACK (Internal)
Top 3 pain points from Zendesk this week:
1. False positive rate concerns (12 tickets)
2. Pricing transparency requests (8 tickets)
3. API documentation gaps (6 tickets)

RECOMMENDED ACTIONS
1. [High] Review attached competitive analysis memo
2. [High] Address Reddit sentiment with social/PR team
3. [Medium] Product discussion: ML-based fraud detection roadmap
4. [Medium] Update fraud detection documentation
```

**Attachments:**
- Full weekly report (markdown)
- Investigation memo: Competitor fraud features (PDF)
- Raw data archive (JSON)

**9:10am - PM Reviews:**
- Reads executive summary (2 minutes)
- Opens high-priority investigation memo (8 minutes)
- Has full context for 10am leadership meeting

**9:30am - Takes Action:**
- Slack message to engineering: "Need to discuss ML fraud detection"
- Calendar invite: Competitive response planning session
- Note to marketing: Reddit sentiment issue

**Total Time:** 30 minutes vs 8+ hours of manual research

---

## Platform Features

### Workspace Dashboard (Web UI)

**Overview Tab:**
- Latest digest summary
- Pending high-priority alerts
- Week-over-week trend charts
- Quick links to investigations

**Sources Tab:**
- Health status of each data source
- Collection statistics
- Add/remove/configure sources

**Competitors Tab:**
- Competitor comparison matrix
- Change history timeline
- Recent updates from each

**History Tab:**
- Search past reports
- Filter by topic/theme
- Export historical data

**Settings Tab:**
- Workspace configuration
- Schedule management
- Notification preferences
- Team member access

---

## Implementation Roadmap

### Phase 0: Single-Workspace Prototype (Weeks 1-2)

**Goal:** Validate automation engine with one workspace

**Scope:**
- 10+ RSS feeds (industry news)
- 1 Reddit search query
- Competitor discovery for 2 companies
- Basic AI analysis and weekly email
- Manual Slack/Zendesk integration

**Success Criteria:**
- First weekly digest delivered
- All three source types working
- Insights deemed useful by test PM

**Cost:** $12-26/month (AI APIs only)

---

### Phase 1: Enhanced Single-Workspace (Weeks 3-4)

**Goal:** Add internal data sources and investigation capability

**Scope:**
- Slack VOC integration
- Zendesk ticket analysis
- Gong call transcript search
- Autonomous investigation for high-priority signals
- Historical trending (week-over-week)

**Success Criteria:**
- Internal sources integrated
- First investigation memo generated
- Cross-source correlation working

**Cost:** $28-55/month

---

### Phase 2: Multi-Workspace Platform (Weeks 5-12)

**Goal:** Scale to support 5-10 Twilio PM workspaces

**Scope:**
- Multi-tenant architecture
- Self-service workspace creation
- Web dashboard (React frontend)
- Workspace isolation and access control
- Admin panel for platform monitoring
- Source discovery and compliance agents

**Success Criteria:**
- 5+ PMs actively using their workspaces
- Each workspace operating independently
- 80%+ of insights rated actionable

**Cost:** $150-300/month (for 5 workspaces)

---

### Phase 3: Scale & Polish (Weeks 13-24)

**Goal:** Production-ready for all Twilio PMs

**Scope:**
- Support 20+ workspaces
- Advanced dashboard with visualizations
- Collaborative features (shared investigations)
- Integration marketplace (connect new sources easily)
- Mobile-friendly digest view
- Advanced alerting and filtering

**Success Criteria:**
- 20+ active workspaces
- 90%+ uptime
- Demonstrable impact on roadmap decisions

---

## Technical Foundation

### Infrastructure

**Orchestration:**
- Scheduled automation (GitHub Actions, AWS Lambda, or similar)
- Parallel execution per workspace
- Fault tolerance and retry logic

**Storage:**
- PostgreSQL: Workspace configs, user data, metrics
- Vector DB: Historical research for semantic search
- S3/Storage: Raw data archives, reports

**Frontend:**
- React-based dashboard
- REST API for workspace management
- Real-time updates via WebSockets

**AI Integration:**
- Analysis and summarization APIs
- Investigation capabilities
- Source discovery and compliance checking

**Email Delivery:**
- Brevo (formerly Sendinblue): Transactional email service
- Free tier: 300 emails/day (sufficient for 20+ workspaces)
- REST API integration via sib-api-v3-sdk
- Supports HTML formatting and attachments (investigation memos)

---

### Data Pipeline

```
Collection → Storage → Analysis → Investigation → Synthesis → Delivery
    ↓          ↓          ↓            ↓              ↓           ↓
  RSS       Raw JSON   AI API    Deep Dive      Report Gen    Brevo Email
  Reddit    Database   Calls     Research       Markdown      Slack
  APIs      Versioned  Pattern   Cross-ref      Dashboard     Webhook
  Scraping             Detection
```

---

### Compliance & Ethics

**Principles:**
- Only public data sources
- Respect robots.txt and ToS
- Rate limiting on all scraping
- No authentication bypass
- Customer data privacy (internal sources)
- GDPR/SOC2 considerations

**Automated Compliance:**
- Check robots.txt before adding sources
- Monitor ToS changes
- Alert on violations
- Prefer API > RSS > Scraping
- Document all access methods

---

## Success Metrics

### Efficiency Metrics
- Time saved: 8+ hours/week → 30 minutes/week per PM
- Coverage: 15+ sources automated vs 5 manual
- Consistency: 100% weekly execution vs ad-hoc
- Response time: <24 hours for high-priority vs 2-3 weeks

### Quality Metrics
- Insight accuracy: 80%+ actionable insights
- False positive rate: <20% for high-priority alerts
- PM satisfaction: 4+ stars on usefulness
- Coverage gaps: Track missed important signals

### Business Impact Metrics
- Roadmap decisions informed by PM Radar: Track over time
- Competitive threats caught early: Count and impact
- Customer issues proactively addressed: Measure prevention
- Time-to-decision improvement: Before/after comparison

---

## Risk Assessment & Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data source APIs change/break | Missing insights | Multi-source redundancy, graceful degradation |
| AI hallucination | Wrong conclusions | Source citations, confidence scoring |
| Cost overruns | Budget exceeded | Per-workspace caps, usage monitoring |
| Performance at scale | Slow digests | Parallel processing, caching |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low PM adoption | Wasted effort | Beta with engaged PMs, iterate on feedback |
| Compliance violations | Legal issues | Automated compliance checking |
| Data privacy breach | Security incident | Workspace isolation, access controls |
| System unavailable | No digests | SLA monitoring, fallback systems |

### Business Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Insights not actionable | Low value perception | PM feedback loop, quality tuning |
| Alert fatigue | PMs ignore digests | Threshold tuning, priority filtering |
| Maintenance burden | Becomes time sink | Simple architecture, clear documentation |

---

## Open Questions

### Technical Decisions
- [ ] Infrastructure: GitHub Actions vs AWS Lambda vs dedicated servers?
- [ ] Vector DB: Pinecone vs pgvector vs Weaviate?
- [ ] Frontend: Build custom or use existing internal tools?
- [ ] API access: Direct integration with Slack/Zendesk or via existing internal APIs?

### Product Decisions
- [ ] Workspace approval: Self-service or admin-approved?
- [ ] Sharing: Can PMs share insights across workspaces?
- [ ] Historical data: How far back to maintain?
- [ ] Alert thresholds: Platform-wide defaults or per-workspace tuning?

### Organizational
- [ ] Ownership: Which team owns PM Radar platform?
- [ ] Support: Who handles PM questions and issues?
- [ ] Expansion: Priority order for which PMs get workspaces?
- [ ] Success criteria: How do we measure ROI?

---

## Next Steps

### Week 1: Foundation
1. Finalize technical architecture decisions
2. Get access: Slack API, Zendesk API, Gong API
3. Select RSS feeds for prototype
4. Choose first PM beta tester (ideally Messaging/Fraud team)

### Week 2: Prototype Build
1. Build collection pipeline (RSS + Reddit)
2. Implement competitor discovery
3. Set up AI analysis pipeline
4. Create first weekly digest template

### Week 3: Beta Test
1. Deliver first digest to beta PM
2. Gather detailed feedback
3. Measure time savings
4. Iterate on insights quality

### Week 4-8: Expand & Refine
1. Add internal data sources (Slack, Zendesk, Gong)
2. Build investigation capability
3. Onboard 2-3 more PM workspaces
4. Build basic dashboard

### Week 9-12: Multi-Workspace Platform
1. Implement workspace isolation
2. Self-service workspace creation
3. Admin monitoring tools
4. Scale to 5-10 workspaces

---

## Appendix

### Example Workspace Configurations

**Workspace: Twilio Messaging - Fraud Prevention**
- PM: Sarah Chen
- Competitors: Sinch, Vonage, MessageBird, Bandwidth, Telnyx
- Industry Sources: Telecom Reseller, Fierce Wireless, Telecompaper (10 total)
- Social: Reddit ("SMS pumping", "traffic pumping"), r/telecom
- Internal: Zendesk tag "fraud", Slack #messaging-feedback, Gong calls mentioning "fraud"
- Schedule: Weekly digest Monday 9am, real-time alerts for high-priority

**Workspace: Twilio Voice - Contact Center**
- PM: Michael Rodriguez
- Competitors: Five9, Genesys, Amazon Connect, Talkdesk
- Industry Sources: CCaaS industry blogs, contact center news (12 total)
- Social: Reddit r/callcenter, LinkedIn CCaaS groups
- Internal: Zendesk tag "voice", Slack #flex-customers, G2 reviews
- Schedule: Weekly digest Tuesday 10am

**Workspace: Twilio Auth - Identity Verification**
- PM: Alex Kim
- Competitors: Auth0, Okta, FusionAuth, Ping Identity
- Industry Sources: Security blogs, identity management news (8 total)
- Social: HackerNews, r/netsec, InfoSec Twitter
- Internal: Zendesk tag "verification", Slack #auth-product
- Schedule: Weekly digest Monday 2pm

---

## Document Control

**Change Log:**

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-03-20 | 1.0 | PM | Initial multi-tenant SaaS vision |
| 2026-03-31 | 2.0 | PM | Refocused as internal tool, combined with validated automation engine, removed pricing/GTM, added implementation phases |
| 2026-04-03 | 2.1 | PM | Updated email delivery service to Brevo (replacing SendGrid); added technical implementation details |

**Review & Approval:**

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Leadership | [Name] | Pending | - |
| Engineering Lead | [Name] | Pending | - |
| Data/Privacy | [Name] | Pending | - |

**Distribution:**
- Product Management Team
- Engineering Leadership
- Platform/Tools Team
