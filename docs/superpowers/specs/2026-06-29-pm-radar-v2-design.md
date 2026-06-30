# PM Radar v2 - Multi-Topic Research Platform

**Date:** 2026-06-29  
**Author:** Claude Sonnet 4.5 + Saydas  
**Status:** Design Approved - Ready for Implementation

---

## Executive Summary

Transform PM Radar from a single-purpose fraud research tool into a modular, multi-topic intelligence platform. Internal teams can create research topics (fraud, AI news, PM practices, etc.) with independent configs for sources, analysis prompts, report sections, and recipient lists.

**Target Users:** Internal Twilio teams (5-10 PMs)  
**Delivery:** JSON/YAML configs + documentation (no UI in v2.0)  
**Migration Strategy:** Big bang - build v2 in parallel, switch when complete (v1 paused during development)

---

## Architecture Decision

**Selected Approach:** Plugin Architecture

**Why:**
- Separates mechanics (how to collect/analyze) from domain knowledge (what to collect/analyze)
- Easy to add new collector types (Twitter, Slack, etc.)
- LLM provider swapping is trivial (OpenAI, Anthropic, local models)
- Copywriter agent fits naturally as analyzer plugin
- Right-sized for internal teams (not over-engineered like microservices)

**Trade-off:** ~20% more initial dev time vs config-driven monolith, but saves time when adding topics/sources.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Topic Configs (YAML)                    │
│  fraud.yaml  |  ai-news.yaml  |  pm-practices.yaml          │
│  (sources, prompts, sections, recipients)                   │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   Core Pipeline Engine                      │
│  TopicPipeline: collect → analyze → qa → report → deliver  │
└─────┬───────────────┬──────────────┬──────────────┬─────────┘
      ↓               ↓              ↓              ↓
┌──────────┐  ┌──────────────┐  ┌─────────┐  ┌────────────┐
│Collectors│  │   Analyzers  │  │Reporter │  │  Delivery  │
│(plugins) │  │   (plugins)  │  │(plugins)│  │  (plugins) │
└──────────┘  └──────────────┘  └─────────┘  └────────────┘
  RSS            Summarizer        Section      Email
  Reddit         Copywriter        Library      GitHub
  Changelog      LLM Providers                  Release

┌─────────────────────────────────────────────────────────────┐
│              Global Config (Shared Styling)                 │
│  global.yaml: branding, CSS, templates, SMTP                │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
pm-radar-v2/
├── config/
│   ├── global.yaml                    # Shared: branding, styling, SMTP, templates
│   └── topics/
│       ├── fraud/
│       │   ├── topic.yaml             # Master: LLM, sources, sections, email
│       │   ├── prompts.yaml           # Analysis prompts
│       │   ├── rss.yaml               # RSS feed URLs
│       │   ├── reddit.yaml            # Subreddits, search queries
│       │   └── changelogs.yaml        # Competitor URLs
│       ├── ai-news/
│       │   └── (same structure)
│       └── pm-practices/
│           └── (same structure)
│
├── core/
│   ├── pipeline.py                    # TopicPipeline orchestrator
│   │
│   ├── collectors/
│   │   ├── base.py                    # Abstract collector interface
│   │   ├── orchestrator.py            # Runs all collectors for a topic
│   │   ├── rss.py                     # RSS feed collector
│   │   ├── reddit.py                  # Reddit API wrapper (SocialCrawl)
│   │   └── changelog.py               # Web scraper (Scrapling)
│   │
│   ├── analyzers/
│   │   ├── base.py                    # Abstract analyzer interface
│   │   ├── summarizer.py              # Content processor (filter→categorize→analyze)
│   │   ├── copywriter.py              # QA agent (auto-fix formatting/duplicates)
│   │   └── llm_providers.py           # OpenAI, Anthropic, local model adapters
│   │
│   ├── reporters/
│   │   ├── report_generator.py        # Section assembly engine
│   │   └── sections/
│   │       ├── executive_summary.py   # Section renderers
│   │       ├── top_items.py
│   │       ├── trend_analysis.py
│   │       ├── competitive_intel.py
│   │       └── regulatory_changes.py
│   │
│   └── delivery/
│       ├── email_sender.py            # SMTP delivery
│       └── github_release.py          # GitHub Pages publisher
│
├── data/
│   └── topics/
│       ├── fraud/
│       │   ├── raw/                   # Collected data by date
│       │   │   └── 2026-06-29.json
│       │   ├── analysis/              # Analysis results
│       │   │   └── 2026-06-29.json
│       │   └── reports/               # Final reports
│       │       ├── 2026-06-29.md
│       │       └── 2026-06-29.html
│       ├── ai-news/
│       └── pm-practices/
│
├── templates/
│   ├── report-template.html           # Global HTML structure
│   └── email-styles.css               # Global CSS
│
├── scripts/
│   └── main.py                        # Entry point: load topics → run pipelines
│
├── docs/                              # GitHub Pages (published reports)
│   ├── index.html                     # Landing page (all topics)
│   ├── fraud/
│   │   ├── index.html                 # Topic archive
│   │   ├── latest.html → 2026-06-29.html
│   │   └── 2026-06-29.html
│   ├── ai-news/
│   └── pm-practices/
│
├── docs/v2-migration/                 # Living documentation
│   ├── MASTER_PLAN.md                 # Progress tracker + next steps
│   ├── ARCHITECTURE.md                # Design reference
│   ├── MIGRATION_LOG.md               # Session history
│   └── DECISIONS.md                   # Architecture Decision Records
│
└── requirements.txt
```

---

## Component Design

### 1. Collectors (Data Ingestion Plugins)

**Responsibility:** Fetch raw data from external sources.

**Base Interface:**
```python
class BaseCollector(ABC):
    def __init__(self, config: dict, api_key: Optional[str] = None)
    
    @abstractmethod
    def collect(self) -> List[dict]:
        """Return list of items (articles, posts, changes)"""
    
    def get_cache_key(self) -> str
    def should_use_cache(self) -> bool
```

**Implementations:**
- **RSSCollector:** Parse feeds via feedparser
- **RedditCollector:** SocialCrawl API (replacing SociaVault), 24h cache
- **ChangelogCollector:** Scrapling v3 web scraper, 168h cache

**Orchestrator:** Runs all collectors for a topic, aggregates results.

**Topic-specific configs:**
- `rss.yaml` - feed URLs, categories
- `reddit.yaml` - subreddits, search queries, timeframes
- `changelogs.yaml` - competitor URLs, scrape modes

---

### 2. Analyzers (Content Processing Plugins)

**Responsibility:** Transform raw data into structured insights.

**Summarizer:**
- Filters content (GPT-4o scoring 0-10)
- Categorizes by topic (fraud types vs AI categories vs PM frameworks)
- Analyzes each category using topic-specific prompts
- Returns structured JSON

**Copywriter Agent:**
- Auto-fixes formatting (citations, markdown, duplicates)
- Runs after summarizer, before report generation
- Logs all changes to diff file for feedback loop
- **Failure mode:** If copywriter fails, skip QA and proceed with raw analysis (log warning)

**LLM Providers:**
- Abstraction layer: OpenAI, Anthropic, local models
- Each topic configures: `provider`, `model`, `api_key_env`
- **Failure mode:** If LLM fails (timeout, rate limit), entire pipeline fails for that topic (no fallback)

**Topic-specific config:**
- `prompts.yaml` - categorization, analysis, executive summary prompts
- `topic.yaml` - LLM provider, model, API key environment variable

---

### 3. Reporters (Report Assembly Plugins)

**Responsibility:** Generate markdown/HTML from analysis results.

**Section Library (Preset only - no custom sections):**
- `executive_summary` - high-level overview
- `top_items` - configurable "top N" list (threats, innovations, tools)
- `trend_analysis` - pattern detection
- `competitive_intel` - competitor movements
- `regulatory_changes` - compliance updates

**Report Generator:**
- Assembles sections based on topic config
- Applies global styling (CSS, fonts, colors)
- Converts markdown → HTML using shared template
- Generates citations from filtered articles

**Global styling (not configurable per topic):**
- `global.yaml` - branding (Twilio colors), font sizes, citation format
- `report-template.html` - HTML structure
- `email-styles.css` - CSS rules

**Topic-specific config:**
- `topic.yaml` → `report.sections` - which sections to include, titles, limits

---

### 4. Delivery (Distribution Plugins)

**Email Sender:**
- Smart routing: each topic has recipient list
- Recipients subscribed to multiple topics get multiple emails
- Uses Brevo SMTP (configured in `global.yaml`)
- Attaches HTML report

**GitHub Release:**
- Publishes HTML to GitHub Pages (`docs/{topic_id}/`)
- Updates `latest.html` symlink
- No combined release (each topic independent)

**Topic-specific config:**
- `topic.yaml` → `email.recipients` - list of email addresses

---

## Data Flow

```
1. Main Loop (scripts/main.py)
   ├─ Load global.yaml (styling, SMTP)
   ├─ Load all topics from config/topics/*/topic.yaml
   ├─ Filter: only enabled topics with feature_flag_v2=true
   └─ For each topic (sequential execution):
       ↓
2. TopicPipeline (core/pipeline.py)
   ├─ Collect: CollectorOrchestrator
   │   ├─ RSSCollector → articles
   │   ├─ RedditCollector → posts (with cache)
   │   └─ ChangelogCollector → changes (with cache)
   │   └─ Save: data/topics/{id}/raw/{date}.json
   ├─ Analyze: ContentSummarizer
   │   ├─ Load prompts from prompts.yaml
   │   ├─ Filter articles (GPT scoring)
   │   ├─ Categorize by topic categories
   │   ├─ Analyze each category
   │   └─ Save: data/topics/{id}/analysis/{date}.json
   ├─ QA: CopywriterAgent
   │   ├─ Auto-fix formatting, duplicates, citations
   │   ├─ Log changes to data/topics/{id}/analysis/{date}.diff
   │   └─ Return cleaned analysis
   ├─ Report: ReportGenerator
   │   ├─ Load section library + global styles
   │   ├─ Assemble markdown from sections
   │   ├─ Convert to HTML with global template
   │   └─ Save: data/topics/{id}/reports/{date}.md + .html
   └─ Deliver:
       ├─ EmailSender: send to topic's recipients
       └─ GitHubRelease: publish to docs/{id}/
```

**Error Handling:**
- Collector fails → log error, continue with empty data
- Analyzer fails → **fail entire pipeline for that topic** (no report sent)
- Copywriter fails → skip QA, log warning, continue with raw analysis
- Reporter fails → fail pipeline (no partial reports)
- Email fails → log error, GitHub Pages still publishes

---

## Configuration System

### Global Config (`config/global.yaml`)

```yaml
branding:
  primary_color: "#F22F46"      # Twilio red
  secondary_color: "#0263E0"    # Twilio blue
  font_family: "Inter, sans-serif"

styling:
  h1_size: "20px"
  h2_size: "16px"
  h3_size: "14px"
  body_size: "14px"
  citation_format: "[A{id}]"

email:
  smtp_provider: brevo
  smtp_key_env: BREVO_API_KEY
  from_email: "sd5288@gmail.com"
  from_name: "PM Radar"

templates:
  html_template: "templates/report-template.html"
  email_css: "templates/email-styles.css"
```

### Topic Config (`config/topics/fraud/topic.yaml`)

```yaml
id: fraud
name: "Fraud & Security Intelligence"
enabled: true
feature_flag_v2: false  # false = use v1 code, true = use v2 code

llm:
  provider: openai
  model: gpt-4o
  api_key_env: OPENAI_API_KEY

sources:
  - type: rss
    config_path: config/topics/fraud/rss.yaml
  
  - type: reddit
    api_key_env: SOCIALCRAWL_API_KEY
    config_path: config/topics/fraud/reddit.yaml
  
  - type: changelog
    config_path: config/topics/fraud/changelogs.yaml

categories:
  - telecom_fraud
  - general_fraud
  - regulatory

prompts_path: config/topics/fraud/prompts.yaml

report:
  sections:
    - type: executive_summary
    
    - type: top_items
      config:
        title: "🔴 Top Threats"
        category: "telecom_fraud"
        limit: 5
    
    - type: top_items
      config:
        title: "🟡 General Security"
        category: "general_fraud"
        limit: 3
    
    - type: regulatory_changes
    
    - type: competitive_intel
      config:
        sources: ["competitor_changelogs"]

email:
  recipients:
    - saydas@twilio.com
    - rlohan@twilio.com
    - tkilam@twilio.com
    - jhasan@twilio.com
    - vsharma@twilio.com
```

### Prompts Config (`config/topics/fraud/prompts.yaml`)

```yaml
categorization: |
  Analyze these articles for FRAUD and SECURITY threats.
  Categories: SMS fraud, account takeover, SIM swapping, regulatory changes.
  Score each 0-10 for relevance to telecom fraud.
  Return JSON: [{"id": 1, "score": 9, "category": "telecom_fraud", "reason": "..."}]

analysis:
  telecom_fraud: |
    Identify telecom-specific fraud threats from these articles.
    For each: describe attack pattern, affected systems, business impact, mitigation.
    Format: JSON array of {"title", "description", "citation"}
  
  general_fraud: |
    Identify general security threats relevant to communications platforms.
    For each: describe vulnerability, exploitation method, defensive measures.
    Format: JSON array of {"title", "description", "citation"}
  
  regulatory: |
    Identify regulatory changes affecting fraud prevention and data security.
    For each: summarize change, compliance requirements, deadline.
    Format: JSON array of {"title", "description", "citation"}

executive_summary: |
  Create an executive summary for a VP of Product covering this week's fraud landscape.
  Focus on: business impact, immediate risks, competitive threats.
  4-5 sentences, outcome-focused.
```

### Reddit Config (`config/topics/fraud/reddit.yaml`)

```yaml
subreddits:
  - twilio
  - fraud
  - cybersecurity

queries:
  - name: "Telecom Fraud"
    keywords:
      - "SMS fraud"
      - "SIM swap"
      - "A2P fraud"
      - "robocall"
      - "smishing"
  
  - name: "Security Incidents"
    keywords:
      - "account takeover"
      - "credential stuffing"
      - "MFA bypass"

timeframe: "week"
limit: 20
fetch_comments: true
comments_threshold:
  min_score: 5
  min_comments: 3
max_comments_per_post: 10
```

---

## Migration Strategy

### Approach: Big Bang with Feature Flags

**Why:** Clean architecture, no dual maintenance, but safer than pure big bang.

**Phase 1: Build v2 (Week 1-2)**
- Build complete v2 architecture in parallel
- All topics have `feature_flag_v2: false` (use v1 code)
- v1 pipeline continues running weekly (fraud reports uninterrupted)

**Phase 2: Validate (Week 3)**
- Set `fraud` topic to `feature_flag_v2: true`
- Run v2 pipeline manually (not scheduled)
- Compare v2 output vs v1 output
- Fix discrepancies

**Phase 3: Cutover (Week 4)**
- Deploy v2 to production
- All topics switch to `feature_flag_v2: true`
- Disable v1 code paths
- Monitor first scheduled run

**Rollback Plan:**
- Set `feature_flag_v2: false` for all topics
- v1 code still present, can reactivate immediately

---

## Key Design Decisions

### Decision 1: Plugin Architecture vs Monolith
**Chosen:** Plugin Architecture  
**Rationale:** Right balance of modularity and simplicity for internal teams. Easy to extend with new collectors/analyzers.  
**Trade-off:** ~20% more dev time vs monolith.

### Decision 2: YAML vs JSON for Configs
**Chosen:** YAML  
**Rationale:** Cleaner syntax for nested configs, supports comments, easier for humans to read/edit.  
**Trade-off:** Less familiar to some devs than JSON.

### Decision 3: Global vs Per-Topic Styling
**Chosen:** Global  
**Rationale:** Brand consistency across all topics. Styling is not domain knowledge.  
**Trade-off:** Topics can't have unique visual identity.

### Decision 4: Copywriter Agent Mode
**Chosen:** Auto-fix with logged diff  
**Rationale:** Saves manual review time, feedback loop via diff files improves prompts over time.  
**Trade-off:** Agent might make unwanted changes (mitigated by diff review).

### Decision 5: LLM Failure Handling
**Chosen:** Fail pipeline (no fallback)  
**Rationale:** Stale data worse than no data. Team expects fresh analysis or explicit failure.  
**Trade-off:** No report sent if LLM fails (acceptable for weekly cadence).

### Decision 6: Report Sections
**Chosen:** Library only (no custom sections)  
**Rationale:** Keep structure consistent, avoid per-topic divergence.  
**Trade-off:** May not fit every future topic perfectly (expand library as needed).

### Decision 7: Email Delivery
**Chosen:** Smart routing (per-topic recipient lists)  
**Rationale:** Flexible - people subscribe to specific topics, some get multiple.  
**Trade-off:** More complex than single combined email.

### Decision 8: Migration Strategy
**Chosen:** Big bang with feature flags  
**Rationale:** Clean cutover, safer than pure big bang, no long dual maintenance.  
**Trade-off:** All-or-nothing switch per topic.

### Decision 9: Multi-Topic Execution
**Chosen:** Sequential  
**Rationale:** Simple error handling, one topic failure doesn't affect others.  
**Trade-off:** Slower than parallel (acceptable for weekly scheduled job).

### Decision 10: SocialCrawl Integration
**Chosen:** Replace SociaVault completely  
**Rationale:** SociaVault API expired, SocialCrawl is active alternative.  
**Trade-off:** Need to test/validate new API (key available).

---

## Success Criteria

**v2.0 Launch:**
- ✅ Fraud topic migrated to v2 (same quality as v1)
- ✅ AI News topic launched (new)
- ✅ PM Practices topic launched (new)
- ✅ SocialCrawl integration working
- ✅ Copywriter agent auto-fixing reports
- ✅ Smart email routing (per-topic recipients)
- ✅ Documentation complete (MASTER_PLAN.md, ARCHITECTURE.md, team guides)

**Quality Metrics:**
- Zero breaking changes to fraud report quality
- <5% false positive fixes from copywriter agent
- <30 min total pipeline execution (3 topics sequential)
- 100% config-driven (no code changes to add topic)

**Team Adoption:**
- New topic added in <2 hours (config only)
- Documentation sufficient for PM to configure topic independently

---

## Open Questions

### SocialCrawl API Format
**Status:** ✅ RESOLVED (2026-06-30)  
**Findings:**
- Endpoint: `https://www.socialcrawl.dev/v1/reddit/search`
- Auth: `x-api-key` header (lowercase)
- Searches ALL Reddit (not per-subreddit) - requires client-side filtering
- No post URLs provided - must construct from `id` + `subreddit`
- No comments - need separate Reddit JSON API call
- Response: nested `data.items[].post` structure
- Cost: 1 credit per search, 97 remaining

**Action:** Implement client-side subreddit filtering + query optimization ("twilio AND fraud" vs broad "fraud")  
**Risk:** Low - API works, structure documented, implementation straightforward  
**Documentation:** See `docs/v2-migration/SOCIALCRAWL_INTEGRATION.md`  

### Copywriter Agent Prompt Tuning
**Status:** Initial prompt to be written  
**Action:** Iterative tuning based on diff file feedback loop  
**Risk:** Low - can improve over time, doesn't block launch  

### Reddit Comment Quality
**Status:** Unknown if SocialCrawl supports comment fetching  
**Action:** Check API docs, fall back to Reddit's public JSON API if needed  
**Risk:** Low - comments are secondary data  

---

## Next Steps

1. **Create MASTER_PLAN.md** - Break design into phases with task checklist
2. **Start Phase 1.1** - Create directory structure, move existing files
3. **Implement base classes** - Collectors, analyzers, reporters
4. **Test SocialCrawl** - Validate API integration
5. **Migrate fraud topic** - First v2 topic (feature flag validation)
6. **Add second topic** - AI News or PM Practices
7. **Deploy & monitor** - First production run

---

## Appendix: Example Topic Configs

### AI News Topic

```yaml
# config/topics/ai-news/topic.yaml
id: ai-news
name: "AI Innovation Digest"
enabled: true
feature_flag_v2: false

llm:
  provider: anthropic
  model: claude-sonnet-4
  api_key_env: ANTHROPIC_API_KEY

sources:
  - type: rss
    config_path: config/topics/ai-news/rss.yaml
  - type: reddit
    api_key_env: SOCIALCRAWL_API_KEY
    config_path: config/topics/ai-news/reddit.yaml
  - type: changelog
    config_path: config/topics/ai-news/changelogs.yaml

categories:
  - model_releases
  - enterprise_tools
  - research

prompts_path: config/topics/ai-news/prompts.yaml

report:
  sections:
    - type: executive_summary
    - type: top_items
      config:
        title: "🚀 Major Releases"
        category: "model_releases"
        limit: 5
    - type: top_items
      config:
        title: "🛠️ Enterprise Tools"
        category: "enterprise_tools"
        limit: 3
    - type: trend_analysis
      config:
        title: "Adoption Trends"
        category: "research"

email:
  recipients:
    - saydas@twilio.com
    - ai-team@twilio.com
```

```yaml
# config/topics/ai-news/reddit.yaml
subreddits:
  - MachineLearning
  - LocalLLaMA
  - OpenAI
  - ClaudeAI

queries:
  - name: "Model Releases"
    keywords:
      - "GPT-5"
      - "Claude"
      - "Llama"
      - "model release"
  
  - name: "Enterprise Tools"
    keywords:
      - "LangChain"
      - "RAG"
      - "vector database"
      - "AI agents"

timeframe: "week"
limit: 30
fetch_comments: false
```

---

**End of Design Document**
