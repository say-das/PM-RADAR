# PM Radar v2 - Multi-Topic Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform PM Radar from single-topic (fraud) into modular multi-topic platform where teams configure independent research topics via YAML.

**Architecture:** Plugin-based with base classes for collectors/analyzers/reporters. Topic configs (YAML) define sources, prompts, sections, LLM provider. Existing fraud code refactored into first topic; v1/v2 coexist via feature flags.

**Tech Stack:** Python 3.14, YAML configs, Abstract Base Classes, OpenAI/Anthropic SDKs, feedparser, requests

---

## Scope Note

This plan builds PM Radar v2 in the `feature/v2-multi-topic-platform` branch while keeping v1 (main branch) operational. Migration strategy: feature flags per topic (`feature_flag_v2: true/false`) enable gradual rollout.

**Out of scope:**
- UI (config files only, v2.0)
- Copywriter agent (separate follow-up task)
- Additional topics beyond fraud (fraud validates architecture)

---

## File Structure

### New Files (Core Infrastructure)

**Configuration:**
- `config/global.yaml` - Shared branding, CSS, SMTP, templates
- `config/topics/fraud/topic.yaml` - Fraud topic master config
- `config/topics/fraud/prompts.yaml` - Analysis prompts (extracted from code)
- `config/topics/fraud/rss.yaml` - RSS sources (migrated from rss-sources.json)
- `config/topics/fraud/reddit.yaml` - Reddit config (migrated from reddit-config.json)
- `config/topics/fraud/changelogs.yaml` - Competitor changelogs (migrated)

**Core Pipeline:**
- `core/__init__.py` - Package init
- `core/pipeline.py` - TopicPipeline orchestrator
- `core/config_loader.py` - YAML config loading + validation

**Collectors:**
- `core/collectors/__init__.py`
- `core/collectors/base.py` - BaseCollector abstract class
- `core/collectors/orchestrator.py` - CollectorOrchestrator
- `core/collectors/rss.py` - RSSCollector (refactored from scripts/collect/rss_collector.py)
- `core/collectors/reddit.py` - RedditCollector (refactored)
- `core/collectors/changelog.py` - ChangelogCollector (refactored)

**Analyzers:**
- `core/analyzers/__init__.py`
- `core/analyzers/base.py` - BaseAnalyzer abstract class
- `core/analyzers/summarizer.py` - Content summarizer (refactored from scripts/analyze/summarizer.py)
- `core/analyzers/llm_providers.py` - LLM provider abstraction (OpenAI, Anthropic)

**Reporters:**
- `core/reporters/__init__.py`
- `core/reporters/report_generator.py` - Section assembly engine
- `core/reporters/sections/__init__.py`
- `core/reporters/sections/base.py` - BaseSection abstract class
- `core/reporters/sections/executive_summary.py`
- `core/reporters/sections/top_items.py`
- `core/reporters/sections/competitive_intel.py`

**Delivery:**
- `core/delivery/__init__.py`
- `core/delivery/email_sender.py` - Email delivery (refactored from scripts/deliver/email_sender.py)
- `core/delivery/github_release.py` - GitHub Pages publisher (refactored)

### Modified Files

- `scripts/main.py` - Updated to support v1/v2 via feature flags
- `scripts/validate_report.py` - Updated for multi-topic structure

---

## Task 1: Core Configuration System

**Goal:** Load and validate YAML topic configs

**Files:**
- Create: `core/__init__.py`
- Create: `core/config_loader.py`
- Create: `config/global.yaml`
- Test: `tests/core/test_config_loader.py`

- [x] **Step 1.1: Write failing test for config loader**

```python
# tests/core/test_config_loader.py
import pytest
from pathlib import Path
from core.config_loader import ConfigLoader

def test_load_global_config():
    """Test loading global configuration"""
    loader = ConfigLoader()
    config = loader.load_global_config()
    
    assert "branding" in config
    assert config["branding"]["primary_color"] == "#F22F46"
    assert "email" in config
    
def test_load_topic_config():
    """Test loading topic configuration"""
    loader = ConfigLoader()
    topic_config = loader.load_topic_config("fraud")
    
    assert topic_config["id"] == "fraud"
    assert "llm" in topic_config
    assert "sources" in topic_config
    
def test_load_nonexistent_topic_raises_error():
    """Test loading non-existent topic fails gracefully"""
    loader = ConfigLoader()
    
    with pytest.raises(FileNotFoundError):
        loader.load_topic_config("nonexistent")
```

- [x] **Step 1.2: Run test to verify it fails**

Run: `pytest tests/core/test_config_loader.py -v`
Expected: ModuleNotFoundError: No module named 'core'

- [x] **Step 1.3: Create core package init**

```python
# core/__init__.py
"""
PM Radar v2 - Multi-Topic Platform Core
"""

__version__ = "2.0.0"
```

- [x] **Step 1.4: Create global config file**

```yaml
# config/global.yaml
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

- [x] **Step 1.5: Implement config loader**

```python
# core/config_loader.py
"""
Configuration loader for PM Radar v2
Loads and validates YAML configs for topics and global settings.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Loads YAML configuration files for topics and global settings"""
    
    def __init__(self, base_path: Path = None):
        """
        Initialize config loader
        
        Args:
            base_path: Base directory for configs (defaults to project root)
        """
        if base_path is None:
            # Assume we're running from project root
            base_path = Path.cwd()
        
        self.base_path = base_path
        self.config_dir = base_path / "config"
        self.topics_dir = self.config_dir / "topics"
    
    def load_global_config(self) -> Dict[str, Any]:
        """
        Load global configuration
        
        Returns:
            Dict containing global config
            
        Raises:
            FileNotFoundError: If global.yaml doesn't exist
        """
        global_config_path = self.config_dir / "global.yaml"
        
        if not global_config_path.exists():
            raise FileNotFoundError(f"Global config not found: {global_config_path}")
        
        with open(global_config_path) as f:
            return yaml.safe_load(f)
    
    def load_topic_config(self, topic_id: str) -> Dict[str, Any]:
        """
        Load topic configuration
        
        Args:
            topic_id: Topic identifier (e.g., "fraud")
            
        Returns:
            Dict containing topic config
            
        Raises:
            FileNotFoundError: If topic config doesn't exist
        """
        topic_config_path = self.topics_dir / topic_id / "topic.yaml"
        
        if not topic_config_path.exists():
            raise FileNotFoundError(f"Topic config not found: {topic_config_path}")
        
        with open(topic_config_path) as f:
            config = yaml.safe_load(f)
        
        # Resolve relative paths in config
        topic_dir = self.topics_dir / topic_id
        if "prompts_path" in config:
            config["prompts_path"] = str(topic_dir / config["prompts_path"])
        
        return config
    
    def list_topics(self) -> list[str]:
        """
        List all available topics
        
        Returns:
            List of topic IDs
        """
        if not self.topics_dir.exists():
            return []
        
        topics = []
        for topic_dir in self.topics_dir.iterdir():
            if topic_dir.is_dir() and (topic_dir / "topic.yaml").exists():
                topics.append(topic_dir.name)
        
        return sorted(topics)
```

- [x] **Step 1.6: Run tests to verify they pass**

Run: `pytest tests/core/test_config_loader.py -v`
Expected: 2 tests pass (global config test will fail until we create topic config)

- [x] **Step 1.7: Create test directory structure**

```bash
mkdir -p tests/core
touch tests/__init__.py tests/core/__init__.py
```

- [x] **Step 1.8: Commit**

```bash
git add core/ config/global.yaml tests/core/
git commit -m "feat(core): add config loader with YAML support

- ConfigLoader class for loading global and topic configs
- Global config with branding, styling, email settings
- Tests for config loading with error handling"
```

---

## Task 2: Base Collector Interface

**Goal:** Define abstract base class for all collectors

**Files:**
- Create: `core/collectors/__init__.py`
- Create: `core/collectors/base.py`
- Test: `tests/core/collectors/test_base.py`

- [ ] **Step 2.1: Write failing test for base collector**

```python
# tests/core/collectors/test_base.py
import pytest
from core.collectors.base import BaseCollector


class MockCollector(BaseCollector):
    """Test implementation of BaseCollector"""
    
    def collect(self):
        return [{"id": "1", "content": "test"}]


def test_base_collector_requires_collect_implementation():
    """Test that BaseCollector enforces collect() method"""
    
    class IncompleteCollector(BaseCollector):
        pass
    
    with pytest.raises(TypeError):
        collector = IncompleteCollector({})


def test_base_collector_can_be_instantiated_with_config():
    """Test BaseCollector accepts config dict"""
    config = {"api_key": "test", "limit": 10}
    collector = MockCollector(config)
    
    assert collector.config == config
    assert collector.config["limit"] == 10


def test_collect_returns_list():
    """Test collect() returns list"""
    collector = MockCollector({})
    result = collector.collect()
    
    assert isinstance(result, list)
    assert len(result) == 1
```

- [ ] **Step 2.2: Run test to verify it fails**

Run: `pytest tests/core/collectors/test_base.py -v`
Expected: ModuleNotFoundError: No module named 'core.collectors'

- [ ] **Step 2.3: Create collectors package**

```python
# core/collectors/__init__.py
"""
Collectors - Data ingestion plugins
"""

from .base import BaseCollector

__all__ = ["BaseCollector"]
```

- [ ] **Step 2.4: Implement base collector**

```python
# core/collectors/base.py
"""
Base collector interface - all collectors inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta


class BaseCollector(ABC):
    """
    Abstract base class for all collectors
    
    Collectors fetch raw data from external sources (RSS, Reddit, APIs).
    Each collector implements its own caching and rate limiting logic.
    """
    
    def __init__(self, config: Dict[str, Any], api_key: Optional[str] = None):
        """
        Initialize collector
        
        Args:
            config: Collector-specific configuration dict
            api_key: Optional API key for authenticated collectors
        """
        self.config = config
        self.api_key = api_key
        self.cache_dir = Path("data/raw/.cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """
        Collect data from source
        
        Returns:
            List of collected items (articles, posts, changes)
            
        Each item should be a dict with at least:
        - id: unique identifier
        - title: item title/summary
        - url: source URL
        - published: publication date (ISO format)
        """
        pass
    
    def _get_cache_key(self) -> str:
        """Generate cache key from config"""
        cache_data = json.dumps(self.config, sort_keys=True)
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_cache_path(self) -> Path:
        """Get path to cache file"""
        cache_key = self._get_cache_key()
        collector_name = self.__class__.__name__.lower()
        return self.cache_dir / f"{collector_name}_{cache_key}.json"
    
    def _should_use_cache(self, cache_ttl_hours: int = 24) -> bool:
        """
        Check if cached data is still valid
        
        Args:
            cache_ttl_hours: Cache time-to-live in hours
            
        Returns:
            True if cache exists and is still valid
        """
        cache_path = self._get_cache_path()
        
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path) as f:
                cached = json.load(f)
            
            cached_time = datetime.fromisoformat(cached["cached_at"])
            age = datetime.now() - cached_time
            
            return age < timedelta(hours=cache_ttl_hours)
        except Exception:
            return False
    
    def _load_from_cache(self) -> List[Dict[str, Any]]:
        """Load data from cache"""
        cache_path = self._get_cache_path()
        
        with open(cache_path) as f:
            cached = json.load(f)
        
        return cached["data"]
    
    def _save_to_cache(self, data: List[Dict[str, Any]]):
        """Save data to cache"""
        cache_path = self._get_cache_path()
        
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "config": self.config,
            "data": data
        }
        
        with open(cache_path, "w") as f:
            json.dump(cache_data, f, indent=2)
```

- [ ] **Step 2.5: Run tests to verify they pass**

Run: `pytest tests/core/collectors/test_base.py -v`
Expected: All 3 tests pass

- [ ] **Step 2.6: Create test directory**

```bash
mkdir -p tests/core/collectors
touch tests/core/collectors/__init__.py
```

- [ ] **Step 2.7: Commit**

```bash
git add core/collectors/ tests/core/collectors/
git commit -m "feat(collectors): add base collector interface

- BaseCollector abstract class with caching support
- Cache key generation from config
- TTL-based cache validation
- Tests for base collector behavior"
```

---

## Task 3: Migrate Fraud Topic to v2 Config Structure

**Goal:** Extract fraud configuration from hardcoded values into YAML files

**Files:**
- Create: `config/topics/fraud/topic.yaml`
- Create: `config/topics/fraud/prompts.yaml`
- Create: `config/topics/fraud/rss.yaml`
- Create: `config/topics/fraud/reddit.yaml`
- Create: `config/topics/fraud/changelogs.yaml`

- [ ] **Step 3.1: Create fraud topic master config**

```yaml
# config/topics/fraud/topic.yaml
id: fraud
name: "Fraud & Security Intelligence"
enabled: true
feature_flag_v2: false  # Start with v1, switch to v2 after validation

llm:
  provider: openai
  model: gpt-4o
  api_key_env: OPENAI_API_KEY

sources:
  - type: rss
    config_path: rss.yaml
  
  - type: reddit
    api_key_env: SOCIALCRAWL_API_KEY
    config_path: reddit.yaml
  
  - type: changelog
    config_path: changelogs.yaml

categories:
  - telecom_fraud
  - general_fraud
  - regulatory

prompts_path: prompts.yaml

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
  # Production recipients (disabled for testing):
  # - rlohan@twilio.com
  # - tkilam@twilio.com
  # - jhasan@twilio.com
  # - vsharma@twilio.com
```

- [ ] **Step 3.2: Extract prompts from summarizer.py to YAML**

```yaml
# config/topics/fraud/prompts.yaml
categorization: |
  Analyze these articles for FRAUD and SECURITY threats.
  Categories: SMS fraud, account takeover, SIM swapping, regulatory changes.
  Score each 0-10 for relevance to telecom fraud.
  Return JSON: [{"id": 1, "score": 9, "category": "telecom_fraud", "reason": "..."}]
  
  DEDUPLICATION (CRITICAL): Aggressively consolidate similar topics:
  - If 3+ articles are from the SAME vendor/product, keep ONLY the most critical one
  - If articles cover the same incident/breach/advisory, keep ONLY the most detailed

analysis:
  telecom_fraud: |
    Identify telecom-specific fraud threats from these articles.
    For each: describe attack pattern (4-5 sentences with editorial room), 
    affected systems, business impact, mitigation.
    Format: JSON array of {"title", "description", "citation"}
  
  general_fraud: |
    Identify general security threats relevant to communications platforms.
    For each: describe vulnerability (4-5 sentences with editorial room), 
    exploitation method, defensive measures.
    Format: JSON array of {"title", "description", "citation"}
  
  regulatory: |
    Identify regulatory changes affecting fraud prevention and data security.
    For each: summarize change (4-5 sentences with editorial room), 
    compliance requirements, deadline.
    Format: JSON array of {"title", "description", "citation"}

executive_summary: |
  Create an executive summary for a VP of Product covering this week's fraud landscape.
  Focus on: business impact, immediate risks, competitive threats.
  4-5 sentences, outcome-focused.
```

- [ ] **Step 3.3: Migrate RSS sources config**

```bash
# Copy existing RSS config with minor formatting
cp config/rss-sources.json config/topics/fraud/rss.yaml.tmp

# Convert JSON to YAML format (manual conversion)
cat > config/topics/fraud/rss.yaml << 'EOF'
sources:
  - name: "Commsrisk"
    url: "https://commsrisk.com/feed/"
    category: telecom_fraud
  
  - name: "CFCA"
    url: "https://cfca.org/feed/"
    category: telecom_fraud
  
  - name: "CISA Advisories"
    url: "https://www.cisa.gov/cybersecurity-advisories/all.xml"
    category: security_advisories
  
  - name: "Mandiant (Google)"
    url: "https://www.mandiant.com/resources/blog/rss.xml"
    category: threat_intelligence
  
  - name: "Unit 42 (Palo Alto)"
    url: "https://unit42.paloaltonetworks.com/feed/"
    category: threat_intelligence
  
  - name: "ZeroFox"
    url: "https://www.zerofox.com/feed/"
    category: dark_web
  
  - name: "FTC Consumer Alerts"
    url: "https://www.ftc.gov/feeds/press-release.xml"
    category: consumer_protection
  
  - name: "The Record"
    url: "https://therecord.media/feed/"
    category: cybersecurity_news
  
  - name: "BleepingComputer"
    url: "https://www.bleepingcomputer.com/feed/"
    category: security_news
  
  - name: "Krebs on Security"
    url: "https://krebsonsecurity.com/feed/"
    category: investigative
  
  - name: "FCA (UK) Warnings"
    url: "https://www.fca.org.uk/news/rss.xml"
    category: regulatory
  
  - name: "FortiGuard Labs"
    url: "https://feeds.fortinet.com/fortinet/blog/threat-research"
    category: threat_landscape
  
  - name: "Telecom Ramblings"
    url: "https://www.telecomramblings.com/feed/"
    category: telecom_fraud
  
  - name: "The Hacker News"
    url: "https://feeds.feedburner.com/TheHackersNews"
    category: security_news
  
  - name: "Help Net Security"
    url: "https://www.helpnetsecurity.com/feed/"
    category: security_news
EOF

rm config/topics/fraud/rss.yaml.tmp
```

- [ ] **Step 3.4: Migrate Reddit config**

```bash
# Convert reddit-config.json to YAML
cat > config/topics/fraud/reddit.yaml << 'EOF'
subreddits:
  - twilio

queries:
  - name: "Twilio Fraud Monitoring"
    keywords:
      - fraud
      - scam
      - hacked
      - breach
      - compromise
      - vulnerability
      - attack
      - phishing
    timeframe: week
    limit: 25

fetch_comments: true
comments_threshold:
  min_score: 5
  min_comments: 3
max_comments_per_post: 10
EOF
```

- [ ] **Step 3.5: Migrate competitor changelog config**

```bash
# Convert competitor-changelogs.json to YAML
cat > config/topics/fraud/changelogs.yaml << 'EOF'
competitors:
  - id: vonage
    name: Vonage
    urls:
      - url: "https://developer.vonage.com/en/fraud-defender/release-notes"
        product: "Fraud Defender"
        enabled: true
        scrape_mode: full
  
  - id: bandwidth
    name: Bandwidth
    urls:
      - url: "https://www.bandwidth.com/release-notes/?"
        product: "Platform"
        enabled: true
        scrape_mode: keyword_filter
  
  - id: sardine
    name: Sardine
    urls:
      - url: "https://www.sardine.ai/changelog.html"
        product: "Fraud Prevention Platform"
        enabled: true
        scrape_mode: full
  
  - id: abnormal
    name: Abnormal Security
    urls:
      - url: "https://abnormal.ai/changelog"
        product: "Email Security"
        enabled: true
        scrape_mode: full

extraction_settings:
  lookback_days: 30
  keywords:
    - fraud
    - security
    - verification
    - authentication
    - 2FA
    - OTP
    - anti-spam
    - rate limit
    - abuse prevention
  cache_hours: 168
  max_tokens_per_page: 10000
EOF
```

- [ ] **Step 3.6: Test config loading**

```bash
# Test that fraud topic loads correctly
python3 -c "
from core.config_loader import ConfigLoader

loader = ConfigLoader()
topic = loader.load_topic_config('fraud')
print(f'✓ Loaded topic: {topic[\"name\"]}')
print(f'✓ LLM: {topic[\"llm\"][\"provider\"]} / {topic[\"llm\"][\"model\"]}')
print(f'✓ Sources: {len(topic[\"sources\"])} configured')
"
```

Expected output:
```
✓ Loaded topic: Fraud & Security Intelligence
✓ LLM: openai / gpt-4o
✓ Sources: 3 configured
```

- [ ] **Step 3.7: Commit**

```bash
git add config/topics/fraud/
git commit -m "feat(fraud): migrate fraud topic to v2 config structure

- topic.yaml: master config with LLM, sources, report sections
- prompts.yaml: extracted analysis prompts from code
- rss.yaml: RSS sources (converted from JSON)
- reddit.yaml: Reddit config (converted from JSON)
- changelogs.yaml: competitor changelog config (converted from JSON)

Feature flag v2 disabled - v1 still active"
```

---

## Implementation Roadmap

This implementation is broken into 4 sub-projects, each producing working, testable software:

### Sub-Project 1: Core Infrastructure ✅ (THIS PLAN)
**Duration:** ~1 week  
**Deliverable:** Config system + base classes + working collectors that can fetch data

**Success Criteria:**
- Load fraud topic from YAML configs
- Collectors (RSS, Reddit, Changelog) work with new architecture
- Data collection produces same output as v1
- All tests passing

**Tasks:** 1-8 (detailed below)

---

### Sub-Project 2: Analyzers & LLM Providers (NEXT)
**Duration:** ~1 week  
**Deliverable:** Content analysis working with pluggable LLM providers

**Success Criteria:**
- BaseAnalyzer with LLM provider abstraction (OpenAI, Anthropic)
- ContentSummarizer refactored to use topic prompts from YAML
- Analysis produces same quality output as v1
- Can switch between OpenAI/Anthropic via config

**Key Components:**
- `core/analyzers/base.py` - BaseAnalyzer interface
- `core/analyzers/llm_providers.py` - OpenAI/Anthropic adapters
- `core/analyzers/summarizer.py` - Refactored content processor
- Prompt loading from `prompts.yaml`

---

### Sub-Project 3: Reporters & Section Library (AFTER SUB-PROJECT 2)
**Duration:** ~4 days  
**Deliverable:** Report generation with configurable sections

**Success Criteria:**
- BaseSection interface for report sections
- Section library (executive_summary, top_items, competitive_intel, etc.)
- ReportGenerator assembles reports from topic config
- Reports match v1 quality with global styling

**Key Components:**
- `core/reporters/report_generator.py`
- `core/reporters/sections/*.py` - Section implementations
- Section config parsing from `topic.yaml`

---

### Sub-Project 4: Integration & Migration (FINAL)
**Duration:** ~3 days  
**Deliverable:** Full v2 pipeline with feature flags, fraud migrated

**Success Criteria:**
- TopicPipeline orchestrates collect → analyze → report → deliver
- Feature flag system (v1/v2 coexist)
- Fraud topic fully migrated to v2
- End-to-end test: v2 produces identical report to v1
- Documentation for adding new topics

**Key Components:**
- `core/pipeline.py` - TopicPipeline orchestrator
- `scripts/main.py` - Updated with feature flag support
- End-to-end integration tests
- Migration guide documentation

---

## Sub-Project 1: Core Infrastructure (DETAILED TASKS)

The following tasks implement the foundation for PM Radar v2.

---

## Task 4: RSS Collector Implementation

**Goal:** Refactor existing RSS collector to use BaseCollector interface

**Files:**
- Create: `core/collectors/rss.py`
- Reference: `scripts/collect/rss_collector.py` (existing v1)
- Test: `tests/core/collectors/test_rss.py`

- [ ] **Step 4.1: Write failing test for RSS collector**

```python
# tests/core/collectors/test_rss.py
import pytest
from core.collectors.rss import RSSCollector


def test_rss_collector_loads_config():
    """Test RSS collector loads YAML config"""
    config = {
        "sources": [
            {
                "name": "Test Feed",
                "url": "https://example.com/feed.xml",
                "category": "test"
            }
        ]
    }
    
    collector = RSSCollector(config)
    assert len(collector.config["sources"]) == 1


def test_rss_collector_collect_returns_list():
    """Test collect returns list of articles"""
    config = {
        "sources": [
            {
                "name": "Commsrisk",
                "url": "https://commsrisk.com/feed/",
                "category": "telecom_fraud"
            }
        ]
    }
    
    collector = RSSCollector(config)
    # This will make a real API call
    articles = collector.collect()
    
    assert isinstance(articles, list)
    # Articles should have required fields
    if articles:
        assert "title" in articles[0]
        assert "url" in articles[0]
        assert "published" in articles[0]
```

- [ ] **Step 4.2: Run test to verify it fails**

Run: `pytest tests/core/collectors/test_rss.py -v`
Expected: ModuleNotFoundError: No module named 'core.collectors.rss'

- [ ] **Step 4.3: Implement RSS collector**

```python
# core/collectors/rss.py
"""
RSS Feed Collector
Fetches articles from RSS/Atom feeds using feedparser.
"""

import feedparser
from datetime import datetime
from typing import Dict, Any, List

from .base import BaseCollector


class RSSCollector(BaseCollector):
    """Collect articles from RSS feeds"""
    
    def collect(self) -> List[Dict[str, Any]]:
        """
        Collect articles from configured RSS feeds
        
        Returns:
            List of article dicts with keys: source, category, title, url, published, summary
        """
        # Check cache first
        if self._should_use_cache(cache_ttl_hours=24):
            return self._load_from_cache()
        
        articles = []
        sources = self.config.get("sources", [])
        
        for source in sources:
            try:
                feed = feedparser.parse(source["url"])
                
                for entry in feed.entries:
                    # Parse published date
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6]).isoformat()
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6]).isoformat()
                    else:
                        published = datetime.now().isoformat()
                    
                    article = {
                        "source": source["name"],
                        "category": source.get("category", "general"),
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "published": published,
                        "summary": entry.get("summary", entry.get("description", ""))
                    }
                    
                    articles.append(article)
            
            except Exception as e:
                print(f"  ✗ Error collecting from {source['name']}: {e}")
                continue
        
        # Save to cache
        self._save_to_cache(articles)
        
        return articles
```

- [ ] **Step 4.4: Run tests to verify they pass**

Run: `pytest tests/core/collectors/test_rss.py -v`
Expected: Both tests pass

- [ ] **Step 4.5: Test with fraud RSS config**

```bash
python3 -c "
import yaml
from core.collectors.rss import RSSCollector

# Load fraud RSS config
with open('config/topics/fraud/rss.yaml') as f:
    config = yaml.safe_load(f)

collector = RSSCollector(config)
articles = collector.collect()

print(f'✓ Collected {len(articles)} articles')
if articles:
    print(f'  Sample: {articles[0][\"title\"][:60]}...')
"
```

Expected: Collects 50-100+ articles from fraud RSS sources

- [ ] **Step 4.6: Commit**

```bash
git add core/collectors/rss.py tests/core/collectors/test_rss.py
git commit -m "feat(collectors): implement RSS collector

- RSSCollector using feedparser
- Inherits caching from BaseCollector
- Compatible with fraud rss.yaml config
- Tests for RSS collection"
```

---

## Task 5: Reddit Collector Implementation

**Goal:** Refactor Reddit collector to use BaseCollector interface

**Files:**
- Create: `core/collectors/reddit.py`
- Reference: `scripts/collect/reddit_collector.py` (existing v1)
- Test: `tests/core/collectors/test_reddit.py`

- [ ] **Step 5.1: Write failing test for Reddit collector**

```python
# tests/core/collectors/test_reddit.py
import pytest
import os
from core.collectors.reddit import RedditCollector


@pytest.mark.skipif(not os.getenv("SOCIALCRAWL_API_KEY"), reason="No API key")
def test_reddit_collector_with_real_api():
    """Test Reddit collector with real API (requires key)"""
    config = {
        "subreddits": ["twilio"],
        "queries": [
            {
                "name": "Test Query",
                "keywords": ["fraud"],
                "timeframe": "month",
                "limit": 5
            }
        ]
    }
    
    api_key = os.getenv("SOCIALCRAWL_API_KEY")
    collector = RedditCollector(config, api_key=api_key)
    posts = collector.collect()
    
    assert isinstance(posts, list)
    # May return 0-5 posts depending on activity
    if posts:
        assert "title" in posts[0]
        assert "subreddit" in posts[0]
        assert "url" in posts[0]


def test_reddit_collector_requires_api_key():
    """Test Reddit collector fails gracefully without API key"""
    config = {"subreddits": ["test"], "queries": []}
    
    collector = RedditCollector(config, api_key=None)
    
    with pytest.raises(ValueError, match="API key"):
        collector.collect()
```

- [ ] **Step 5.2: Run test to verify it fails**

Run: `pytest tests/core/collectors/test_reddit.py -v`
Expected: ModuleNotFoundError

- [ ] **Step 5.3: Implement Reddit collector**

```python
# core/collectors/reddit.py
"""
Reddit Collector
Fetches posts from Reddit using SocialCrawl API.
"""

import requests
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base import BaseCollector


class RedditCollector(BaseCollector):
    """Collect posts from Reddit via SocialCrawl API"""
    
    def __init__(self, config: Dict[str, Any], api_key: Optional[str] = None):
        super().__init__(config, api_key)
        self.base_url = "https://www.socialcrawl.dev/v1/reddit/subreddit/search"
    
    def collect(self) -> List[Dict[str, Any]]:
        """
        Collect posts from Reddit
        
        Returns:
            List of post dicts with keys: query, subreddit, title, author, score, 
            num_comments, url, selftext, created_utc
        """
        if not self.api_key:
            raise ValueError("Reddit collector requires SOCIALCRAWL_API_KEY")
        
        # Check cache first (24h TTL)
        if self._should_use_cache(cache_ttl_hours=24):
            return self._load_from_cache()
        
        posts = []
        subreddits = self.config.get("subreddits", [])
        queries = self.config.get("queries", [])
        
        for query_config in queries:
            query_name = query_config["name"]
            keywords = query_config["keywords"]
            timeframe = query_config.get("timeframe", "week")
            limit = query_config.get("limit", 25)
            
            # Build search query
            search_query = " OR ".join(keywords)
            
            # Search each subreddit
            for subreddit in subreddits:
                try:
                    response = self._api_call(subreddit, search_query, timeframe)
                    items = response.get("data", {}).get("items", [])
                    
                    for item in items[:limit]:
                        post = item.get("post", {})
                        post_id = post.get("id", "")
                        subreddit_name = post.get("ext", {}).get("subreddit", subreddit)
                        
                        # Construct Reddit URL
                        post_url = f"https://reddit.com/r/{subreddit_name}/comments/{post_id}"
                        
                        # Parse engagement
                        engagement = post.get("engagement", {})
                        content = post.get("content", {})
                        author = post.get("author", {}).get("username", "[deleted]")
                        
                        # Convert timestamp
                        published_at = post.get("published_at", 0)
                        created_utc = datetime.fromtimestamp(published_at).isoformat() if published_at else datetime.now().isoformat()
                        
                        post_data = {
                            "query": query_name,
                            "search_terms": search_query,
                            "subreddit": subreddit_name,
                            "title": content.get("text", "")[:200],
                            "author": author,
                            "score": engagement.get("likes", 0),
                            "num_comments": engagement.get("comments", 0),
                            "created_utc": created_utc,
                            "url": post_url,
                            "selftext": content.get("text", ""),
                            "upvote_ratio": None,
                            "is_self": True,
                            "comments": []
                        }
                        
                        posts.append(post_data)
                
                except Exception as e:
                    print(f"  ✗ Error collecting from r/{subreddit}: {e}")
                    continue
        
        # Save to cache
        self._save_to_cache(posts)
        
        return posts
    
    def _api_call(self, subreddit: str, query: str, timeframe: str) -> dict:
        """Make SocialCrawl API call"""
        headers = {
            "x-api-key": self.api_key,
            "Cache-Control": "no-cache",
            "Idempotency-Key": f"pmradar-{uuid.uuid4()}"
        }
        
        params = {
            "subreddit": subreddit,
            "query": query,
            "timeframe": timeframe,
            "sort": "relevance",
            "cursor": ""
        }
        
        response = requests.get(self.base_url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            raise ValueError(f"SocialCrawl API error: {response.status_code}")
        
        return response.json()
```

- [ ] **Step 5.4: Run tests to verify they pass**

Run: `pytest tests/core/collectors/test_reddit.py -v`
Expected: API key test passes if key present, otherwise skipped; ValueError test passes

- [ ] **Step 5.5: Test with fraud Reddit config**

```bash
python3 -c "
import yaml
import os
from core.collectors.reddit import RedditCollector

with open('config/topics/fraud/reddit.yaml') as f:
    config = yaml.safe_load(f)

api_key = os.getenv('SOCIALCRAWL_API_KEY')
collector = RedditCollector(config, api_key=api_key)
posts = collector.collect()

print(f'✓ Collected {len(posts)} Reddit posts')
if posts:
    print(f'  Sample: {posts[0][\"title\"][:60]}...')
"
```

Expected: Collects 0-5 posts from r/twilio (low activity subreddit)

- [ ] **Step 5.6: Commit**

```bash
git add core/collectors/reddit.py tests/core/collectors/test_reddit.py
git commit -m "feat(collectors): implement Reddit collector with SocialCrawl

- RedditCollector using SocialCrawl API
- Subreddit-specific search endpoint
- 24h caching
- Compatible with fraud reddit.yaml config"
```

---

## Task 6: Changelog Collector Implementation

**Goal:** Refactor changelog collector to use BaseCollector interface

**Files:**
- Create: `core/collectors/changelog.py`
- Reference: `scripts/collect/changelog_scraper_v3.py` (existing v1)
- Test: `tests/core/collectors/test_changelog.py`

- [ ] **Step 6.1: Write failing test stub**

```python
# tests/core/collectors/test_changelog.py
import pytest
from core.collectors.changelog import ChangelogCollector


def test_changelog_collector_loads_config():
    """Test changelog collector loads config"""
    config = {
        "competitors": [
            {
                "id": "test",
                "name": "Test Company",
                "urls": [{"url": "https://example.com", "product": "Test"}]
            }
        ]
    }
    
    collector = ChangelogCollector(config)
    assert len(collector.config["competitors"]) == 1
```

- [ ] **Step 6.2: Run test to verify it fails**

Run: `pytest tests/core/collectors/test_changelog.py -v`
Expected: ModuleNotFoundError

- [ ] **Step 6.3: Implement changelog collector (simplified - reuse existing scraper)**

```python
# core/collectors/changelog.py
"""
Changelog Collector
Scrapes competitor changelogs using Scrapling.
Wraps existing changelog_scraper_v3 logic.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

from .base import BaseCollector

# Import existing v1 scraper
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "collect"))
from changelog_scraper_v3 import ChangelogScraperV3


class ChangelogCollector(BaseCollector):
    """Collect competitor changelog updates"""
    
    def collect(self) -> List[Dict[str, Any]]:
        """
        Collect changelog updates from competitors
        
        Returns:
            List of changelog dicts with keys: competitor, product, title, url, date, relevance
        """
        # Check cache first (168h TTL - one week)
        if self._should_use_cache(cache_ttl_hours=168):
            return self._load_from_cache()
        
        # Use existing v1 scraper temporarily
        # TODO: Refactor to pure collector in sub-project 2
        scraper = ChangelogScraperV3()
        changes = scraper.collect_all()
        
        # Save to cache
        self._save_to_cache(changes)
        
        return changes
```

- [ ] **Step 6.4: Run test to verify it passes**

Run: `pytest tests/core/collectors/test_changelog.py -v`
Expected: Test passes

- [ ] **Step 6.5: Test with fraud changelog config**

```bash
python3 -c "
import yaml
from core.collectors.changelog import ChangelogCollector

with open('config/topics/fraud/changelogs.yaml') as f:
    config = yaml.safe_load(f)

collector = ChangelogCollector(config)
changes = collector.collect()

print(f'✓ Collected {len(changes)} changelog updates')
if changes:
    print(f'  Sample: {changes[0].get(\"title\", \"N/A\")[:60]}...')
"
```

Expected: Collects 0-3 changelog updates (uses cache from v1)

- [ ] **Step 6.6: Commit**

```bash
git add core/collectors/changelog.py tests/core/collectors/test_changelog.py
git commit -m "feat(collectors): implement changelog collector wrapper

- ChangelogCollector wraps existing v1 scraper
- 168h caching (one week)
- TODO: Full refactor in sub-project 2"
```

---

## Task 7: Collector Orchestrator

**Goal:** Implement orchestrator that runs all collectors for a topic

**Files:**
- Create: `core/collectors/orchestrator.py`
- Update: `core/collectors/__init__.py`
- Test: `tests/core/collectors/test_orchestrator.py`

- [ ] **Step 7.1: Write failing test for orchestrator**

```python
# tests/core/collectors/test_orchestrator.py
import pytest
import os
import yaml
from core.collectors.orchestrator import CollectorOrchestrator


def test_orchestrator_loads_collectors_from_topic_config():
    """Test orchestrator initializes collectors from topic config"""
    topic_config = {
        "id": "fraud",
        "sources": [
            {"type": "rss", "config_path": "config/topics/fraud/rss.yaml"},
            {"type": "reddit", "api_key_env": "SOCIALCRAWL_API_KEY", "config_path": "config/topics/fraud/reddit.yaml"}
        ]
    }
    
    orchestrator = CollectorOrchestrator(topic_config)
    assert len(orchestrator.collectors) >= 1  # At least RSS


def test_orchestrator_collect_all_returns_dict():
    """Test collect_all returns structured dict"""
    topic_config = {
        "id": "test",
        "sources": [
            {
                "type": "rss",
                "config_path": "config/topics/fraud/rss.yaml"
            }
        ]
    }
    
    orchestrator = CollectorOrchestrator(topic_config)
    result = orchestrator.collect_all()
    
    assert isinstance(result, dict)
    assert "rss_articles" in result
    assert isinstance(result["rss_articles"], list)
```

- [ ] **Step 7.2: Run test to verify it fails**

Run: `pytest tests/core/collectors/test_orchestrator.py -v`
Expected: ModuleNotFoundError

- [ ] **Step 7.3: Implement collector orchestrator**

```python
# core/collectors/orchestrator.py
"""
Collector Orchestrator
Runs all configured collectors for a topic and aggregates results.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List

from .rss import RSSCollector
from .reddit import RedditCollector
from .changelog import ChangelogCollector


class CollectorOrchestrator:
    """Orchestrates multiple collectors for a topic"""
    
    def __init__(self, topic_config: Dict[str, Any]):
        """
        Initialize orchestrator with topic config
        
        Args:
            topic_config: Topic configuration dict with sources list
        """
        self.topic_id = topic_config["id"]
        self.collectors = []
        
        # Initialize collectors based on source configs
        for source_def in topic_config.get("sources", []):
            collector_type = source_def["type"]
            config_path = source_def["config_path"]
            api_key_env = source_def.get("api_key_env")
            
            # Resolve config path relative to project root
            if not Path(config_path).is_absolute():
                config_path = Path.cwd() / config_path
            
            # Load collector config
            with open(config_path) as f:
                collector_config = yaml.safe_load(f)
            
            # Get API key if specified
            api_key = os.getenv(api_key_env) if api_key_env else None
            
            # Instantiate collector
            if collector_type == "rss":
                collector = RSSCollector(collector_config)
            elif collector_type == "reddit":
                if not api_key:
                    print(f"  ⚠ Skipping Reddit: {api_key_env} not set")
                    continue
                collector = RedditCollector(collector_config, api_key=api_key)
            elif collector_type == "changelog":
                collector = ChangelogCollector(collector_config)
            else:
                print(f"  ⚠ Unknown collector type: {collector_type}")
                continue
            
            self.collectors.append((collector_type, collector))
    
    def collect_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run all collectors and aggregate results
        
        Returns:
            Dict with keys: rss_articles, reddit_posts, competitor_changelogs
        """
        results = {
            "rss_articles": [],
            "reddit_posts": [],
            "competitor_changelogs": []
        }
        
        for collector_type, collector in self.collectors:
            try:
                data = collector.collect()
                
                # Map to result structure
                if collector_type == "rss":
                    results["rss_articles"].extend(data)
                elif collector_type == "reddit":
                    results["reddit_posts"].extend(data)
                elif collector_type == "changelog":
                    results["competitor_changelogs"].extend(data)
            
            except Exception as e:
                print(f"  ✗ {collector_type} collector failed: {e}")
                continue
        
        return results
```

- [ ] **Step 7.4: Update collectors package exports**

```python
# core/collectors/__init__.py
"""
Collectors - Data ingestion plugins
"""

from .base import BaseCollector
from .rss import RSSCollector
from .reddit import RedditCollector
from .changelog import ChangelogCollector
from .orchestrator import CollectorOrchestrator

__all__ = [
    "BaseCollector",
    "RSSCollector",
    "RedditCollector",
    "ChangelogCollector",
    "CollectorOrchestrator"
]
```

- [ ] **Step 7.5: Run tests to verify they pass**

Run: `pytest tests/core/collectors/test_orchestrator.py -v`
Expected: Both tests pass

- [ ] **Step 7.6: Commit**

```bash
git add core/collectors/orchestrator.py core/collectors/__init__.py tests/core/collectors/test_orchestrator.py
git commit -m "feat(collectors): add collector orchestrator

- CollectorOrchestrator runs all collectors for a topic
- Loads collector configs from YAML paths
- Aggregates results into structured dict
- Graceful handling of missing API keys"
```

---

## Task 8: End-to-End Integration Test

**Goal:** Validate entire collector pipeline works with fraud topic

**Files:**
- Create: `tests/integration/test_fraud_collection.py`
- Create: `tests/integration/__init__.py`

- [ ] **Step 8.1: Create integration test**

```python
# tests/integration/test_fraud_collection.py
"""
Integration test: End-to-end fraud topic data collection
"""

import pytest
from core.config_loader import ConfigLoader
from core.collectors.orchestrator import CollectorOrchestrator


def test_fraud_topic_collection_end_to_end():
    """Test complete data collection for fraud topic"""
    
    # Load fraud topic config
    loader = ConfigLoader()
    topic_config = loader.load_topic_config("fraud")
    
    # Run orchestrator
    orchestrator = CollectorOrchestrator(topic_config)
    results = orchestrator.collect_all()
    
    # Validate structure
    assert "rss_articles" in results
    assert "reddit_posts" in results
    assert "competitor_changelogs" in results
    
    # Validate RSS collection
    assert isinstance(results["rss_articles"], list)
    assert len(results["rss_articles"]) > 0, "Should collect at least some RSS articles"
    
    # Validate first article has required fields
    if results["rss_articles"]:
        article = results["rss_articles"][0]
        assert "title" in article
        assert "url" in article
        assert "published" in article
        assert "source" in article
    
    # Reddit may be empty (low activity), changelogs use cache
    assert isinstance(results["reddit_posts"], list)
    assert isinstance(results["competitor_changelogs"], list)
    
    # Print summary
    print(f"\n✓ Collection Summary:")
    print(f"  RSS: {len(results['rss_articles'])} articles")
    print(f"  Reddit: {len(results['reddit_posts'])} posts")
    print(f"  Changelogs: {len(results['competitor_changelogs'])} updates")


def test_fraud_collection_matches_v1_structure():
    """Test v2 collector output matches v1 structure for compatibility"""
    
    loader = ConfigLoader()
    topic_config = loader.load_topic_config("fraud")
    
    orchestrator = CollectorOrchestrator(topic_config)
    results = orchestrator.collect_all()
    
    # v1 expects these exact keys
    expected_keys = {"rss_articles", "reddit_posts", "competitor_changelogs"}
    assert set(results.keys()) == expected_keys
    
    # All values should be lists
    for key in expected_keys:
        assert isinstance(results[key], list), f"{key} should be a list"
```

- [ ] **Step 8.2: Create integration test directory**

```bash
mkdir -p tests/integration
touch tests/integration/__init__.py
```

- [ ] **Step 8.3: Run integration test**

Run: `pytest tests/integration/test_fraud_collection.py -v -s`
Expected: Both tests pass, shows collection summary

- [ ] **Step 8.4: Verify output matches v1 format**

```bash
python3 -c "
import json
from core.config_loader import ConfigLoader
from core.collectors.orchestrator import CollectorOrchestrator

# Collect with v2
loader = ConfigLoader()
topic_config = loader.load_topic_config('fraud')
orchestrator = CollectorOrchestrator(topic_config)
results = orchestrator.collect_all()

# Save for comparison
with open('data/raw/v2-test-collection.json', 'w') as f:
    json.dump(results, f, indent=2)

print('✓ v2 collection saved to data/raw/v2-test-collection.json')
print(f'  RSS: {len(results[\"rss_articles\"])} articles')
print(f'  Reddit: {len(results[\"reddit_posts\"])} posts')
print(f'  Changelogs: {len(results[\"competitor_changelogs\"])} updates')
"
```

Expected: Creates v2-test-collection.json with same structure as v1

- [ ] **Step 8.5: Commit**

```bash
git add tests/integration/ data/raw/v2-test-collection.json
git commit -m "test(integration): add end-to-end fraud collection test

- Full pipeline test: config → orchestrator → collectors
- Validates output structure matches v1
- Confirms fraud topic collection works end-to-end

Sub-Project 1 Complete: Core infrastructure ready"
```

---

## Sub-Project 1 Completion Checklist

- [ ] All 8 tasks completed
- [ ] All tests passing (`pytest tests/core/ tests/integration/ -v`)
- [ ] Fraud topic loads from YAML configs
- [ ] RSS collector works
- [ ] Reddit collector works (if API key present)
- [ ] Changelog collector works
- [ ] Orchestrator runs all collectors
- [ ] v2 output structure matches v1

**Next:** Sub-Project 2 - Analyzers & LLM Providers

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-30-multi-topic-platform.md`. 

**Sub-Project 1 scope:** Core infrastructure (config system, base classes, collectors, orchestrator)

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
