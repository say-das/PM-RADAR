# PM Radar - Repository Structure

```
PM Radar/
│
├── 📄 README.md                 # ⭐ START HERE - Complete documentation
├── 📄 QUICK_START.md            # 5-minute getting started guide
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example              # Environment template
│
├── 📁 config/                   # Configuration files
│   ├── topics/                  # Topic definitions
│   │   └── fraud/               # Example topic
│   │       ├── topic.yaml       # Main configuration
│   │       ├── prompts.yaml     # LLM prompts
│   │       ├── rss.yaml         # RSS feeds
│   │       ├── reddit.yaml      # Reddit config
│   │       └── changelogs.yaml  # Competitors
│   └── email-config.json        # Email settings
│
├── 📁 core/                     # Core platform code
│   ├── collectors/              # Data collection
│   │   ├── rss_collector.py
│   │   ├── reddit_collector.py
│   │   └── changelog_scraper.py
│   ├── analyzers/               # LLM analysis
│   │   ├── base.py              # Base analyzer
│   │   ├── llm_providers.py     # OpenAI/Anthropic
│   │   └── summarizer.py        # Content analyzer
│   ├── reporters/               # Report generation
│   │   ├── report_generator.py  # Main generator
│   │   ├── health_check.py      # ✨ Validation
│   │   ├── utils.py             # ✨ Safe JSON parsing
│   │   ├── base_section.py      # Section interface
│   │   └── sections/            # Report sections
│   │       ├── executive_summary.py
│   │       ├── top_items.py
│   │       ├── sources.py
│   │       ├── reddit_community.py
│   │       └── competitive_intel.py
│   ├── config_loader.py         # Config management
│   └── pipeline.py              # Main orchestrator
│
├── 📁 scripts/                  # Entry points
│   ├── run_v2_pipeline.py       # ⭐ Main script (v2)
│   ├── main.py                  # V1 script (legacy)
│   ├── collect/                 # Collection scripts
│   └── deliver/                 # Delivery scripts
│       └── email_sender.py
│
├── 📁 tests/                    # Test suite
│   ├── core/
│   │   ├── collectors/
│   │   ├── analyzers/
│   │   └── reporters/
│   └── integration/
│
├── 📁 data/                     # Generated data (gitignored)
│   ├── raw/                     # Collected & analyzed
│   │   ├── YYYY-MM-DD.json
│   │   └── YYYY-MM-DD-analysis.json
│   ├── reports/                 # Generated reports
│   │   ├── YYYY-MM-DD.md
│   │   └── YYYY-MM-DD.html
│   └── logs/                    # Pipeline logs
│
└── 📁 docs/                     # Documentation
    ├── README.md                # Docs overview
    ├── setup/                   # Setup guides
    │   ├── setup-guide.md
    │   ├── email-setup-guide.md
    │   └── reddit-config-guide.md
    ├── architecture/            # Design docs
    │   ├── DESIGN_GUIDE.md
    │   └── AGENTS.md
    ├── v2-robustness-checklist.md   # ✨ Testing strategy
    ├── v2-robustness-summary.md     # ✨ Error handling
    ├── v2-robustness-architecture.md # ✨ Visual flows
    ├── v1-v2-comparison.md          # Migration guide
    └── archive/                 # Historical docs
        ├── old-planning/
        ├── old-implementation-notes/
        ├── old-agent-docs/
        ├── history/
        ├── reports/
        └── v2-migration/
```

---

## 🎯 Key Files

### For Users
- **README.md** - Complete documentation (start here)
- **QUICK_START.md** - Get started in 5 minutes
- **scripts/run_v2_pipeline.py** - Main entry point

### For Developers
- **core/pipeline.py** - Main orchestrator
- **core/reporters/report_generator.py** - Report assembly
- **core/reporters/health_check.py** - Quality validation ✨

### For Configuration
- **config/topics/fraud/** - Example topic (copy this)
- **config/email-config.json** - Email settings

### For Documentation
- **docs/v2-robustness-summary.md** - Error handling guide ✨
- **docs/architecture/DESIGN_GUIDE.md** - System design
- **docs/setup/** - Setup guides (3 files)

---

## 🚀 Quick Navigation

### I want to...

**Run my first report**
→ Read `QUICK_START.md` (5 minutes)

**Add a new topic**
→ Read `README.md` → "Adding a New Topic"

**Customize for my company**
→ Read `README.md` → "Forking & Customization"

**Understand the architecture**
→ Read `docs/v2-robustness-architecture.md`

**Fix an error**
→ Read `README.md` → "Troubleshooting"

**Contribute code**
→ Read `README.md` → "Development"

**See old docs**
→ Check `docs/archive/`

---

## ✨ Recent Additions (V2)

New files for robustness:
- `core/reporters/health_check.py` - Automatic validation
- `core/reporters/utils.py` - Safe JSON parsing
- `docs/v2-robustness-*.md` - Testing & error handling guides (3 files)

---

**Legend:**
- ⭐ = Start here
- ✨ = New in v2
- 📄 = File
- 📁 = Directory
