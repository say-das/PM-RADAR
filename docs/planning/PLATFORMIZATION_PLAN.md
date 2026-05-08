# PM Radar - Platformization Plan
**Multi-Topic Intelligence Platform**

Transform PM Radar from single-purpose fraud research to a flexible platform supporting multiple research topics (PM best practices, AI innovations, etc.) with independent weekly digests.

---

## 🎯 Vision

**Current:** Single topic (fraud research) → One weekly report  
**Target:** Multiple topics → Combined weekly digest with topic-specific sections

**Example Topics:**
- Fraud & Security Intelligence (existing)
- Product Management Best Practices
- AI Innovation Digest
- Developer Experience & Tools
- SaaS Metrics & Growth Strategies

---

## 📐 Architecture Overview

### Data Flow
```
Topic Configs
    ↓
Parallel Collection (RSS + Reddit per topic)
    ↓
Topic-Specific Analysis (custom prompts)
    ↓
Individual Reports (MD + HTML)
    ↓
Combined Release + Topic Pages
```

### Directory Structure
```
PM-RADAR/
├── config/
│   ├── topics.json                    # Master topic registry
│   └── topics/
│       ├── fraud/
│       │   ├── rss-feeds.json
│       │   └── prompts.json
│       ├── pm-practices/
│       │   ├── rss-feeds.json
│       │   └── prompts.json
│       └── ai-innovations/
│           ├── rss-feeds.json
│           └── prompts.json
├── data/
│   ├── raw/
│   │   ├── fraud/
│   │   │   └── 2026-04-30.json
│   │   ├── pm-practices/
│   │   │   └── 2026-04-30.json
│   │   └── ai-innovations/
│   │       └── 2026-04-30.json
│   └── reports/
│       ├── fraud/
│       ├── pm-practices/
│       └── ai-innovations/
├── docs/                              # GitHub Pages
│   ├── index.html                     # Landing page with all topics
│   ├── fraud/
│   │   ├── index.html                 # Topic archive
│   │   ├── latest.html → 2026-04-30.html
│   │   └── 2026-04-30.html
│   ├── pm-practices/
│   └── ai-innovations/
└── scripts/
    ├── main.py                        # Multi-topic orchestrator
    ├── core/
    │   └── topic_pipeline.py          # Single topic pipeline
    ├── collect/
    ├── analyze/
    └── deliver/
        └── multi_topic_release.py     # Combined release publisher
```

---

## 🔧 Implementation Plan

### Phase 1: Foundation (Week 1)

**Goal:** Refactor for multi-topic without breaking existing functionality

#### 1.1 Topic Configuration System

**Create:** `config/topics.json`
```json
{
  "version": "1.0",
  "topics": [
    {
      "id": "fraud",
      "name": "Fraud & Security Intelligence",
      "enabled": true,
      "rss_config": "config/topics/fraud/rss-feeds.json",
      "prompts_config": "config/topics/fraud/prompts.json",
      "categories": ["telecom_fraud", "general_fraud", "competitive"],
      "reddit": {
        "subreddits": ["twilio"],
        "queries": ["fraud", "security", "scam"]
      },
      "fallback_days": 7,
      "color": "#F22F46"
    }
  ]
}
```

**Migrate existing:**
- Move `config/rss_feeds.json` → `config/topics/fraud/rss-feeds.json`
- Extract prompts from `summarizer.py` → `config/topics/fraud/prompts.json`

#### 1.2 Topic Pipeline Class

**Create:** `scripts/core/topic_pipeline.py`
```python
class TopicPipeline:
    """Complete pipeline for a single topic"""
    
    def __init__(self, topic_config, date_str):
        self.id = topic_config['id']
        self.name = topic_config['name']
        self.config = topic_config
        self.date = date_str
        self.base_path = Path(f"data/{self.id}")
        
    def run(self):
        """Execute: collect → analyze → report → publish"""
        print(f"\n{'='*60}")
        print(f"TOPIC: {self.name}")
        print(f"{'='*60}\n")
        
        # 1. Collection
        collected = self._collect()
        
        # 2. Analysis with topic-specific prompts
        analysis = self._analyze(collected)
        
        # 3. Report generation
        report_md, report_html = self._generate_report(analysis)
        
        return {
            'id': self.id,
            'name': self.name,
            'report_md': report_md,
            'report_html': report_html,
            'stats': self._get_stats(collected, analysis)
        }
    
    def _collect(self):
        """Topic-specific RSS + Reddit collection"""
        collector = RSSCollector(self.config['rss_config'])
        articles = collector.collect()
        
        if self.config.get('reddit'):
            reddit = RedditCollector()
            posts = reddit.collect_posts(
                query=" OR ".join(self.config['reddit']['queries']),
                subreddit=",".join(self.config['reddit']['subreddits'])
            )
        else:
            posts = []
            
        # Save raw data
        raw_file = self.base_path / f"raw/{self.date}.json"
        raw_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {'rss_articles': articles, 'reddit_posts': posts}
        with open(raw_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return data
    
    def _analyze(self, collected):
        """Use topic-specific prompts for analysis"""
        analyzer = ContentAnalyzerAgent(
            prompts_config=self.config['prompts_config'],
            topic_id=self.id
        )
        return analyzer.analyze(collected)
    
    def _generate_report(self, analysis):
        """Generate MD and HTML reports"""
        # Generate markdown
        md_path = self.base_path / f"reports/{self.date}.md"
        md_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = generate_topic_report(
            topic_name=self.name,
            analysis=analysis,
            date_str=self.date
        )
        
        with open(md_path, 'w') as f:
            f.write(report)
        
        # Convert to HTML
        html_path = md_path.with_suffix('.html')
        convert_to_html(md_path, html_path, topic_name=self.name)
        
        return md_path, html_path
```

#### 1.3 Refactor Main Orchestrator

**Update:** `scripts/main.py`
```python
def main():
    """Multi-topic pipeline orchestrator"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Load topics
    with open('config/topics.json') as f:
        config = json.load(f)
    
    # Run enabled topics
    results = []
    for topic in config['topics']:
        if not topic['enabled']:
            print(f"⊘ Skipping disabled topic: {topic['name']}")
            continue
        
        try:
            pipeline = TopicPipeline(topic, date_str)
            result = pipeline.run()
            results.append(result)
        except Exception as e:
            print(f"✗ Topic {topic['id']} failed: {e}")
            # Continue with other topics
    
    # Deliver combined release
    if results:
        publisher = MultiTopicReleasePublisher()
        publisher.publish(results, date_str)
```

#### 1.4 Backward Compatibility

**Symlink strategy:**
```python
# Create symlinks for old paths
Path("data/raw/2026-04-30.json").symlink_to("data/fraud/raw/2026-04-30.json")
Path("data/reports/2026-04-30.html").symlink_to("data/fraud/reports/2026-04-30.html")
```

**Test:** Run with single topic (fraud) - should work identically

---

### Phase 2: Multi-Topic Support (Week 2)

#### 2.1 Add Second Topic

**Create:** `config/topics/pm-practices/rss-feeds.json`
```json
{
  "feeds": [
    {
      "name": "Mind the Product",
      "url": "https://www.mindtheproduct.com/feed/",
      "category": "frameworks"
    },
    {
      "name": "Product Coalition",
      "url": "https://productcoalition.com/feed",
      "category": "case_studies"
    },
    {
      "name": "Lenny's Newsletter",
      "url": "https://www.lennysnewsletter.com/feed",
      "category": "frameworks"
    },
    {
      "name": "Silicon Valley Product Group",
      "url": "https://www.svpg.com/feed/",
      "category": "frameworks"
    }
  ]
}
```

**Create:** `config/topics/pm-practices/prompts.json`
```json
{
  "categorization": {
    "frameworks": [
      "OKR", "PRD", "roadmap", "sprint planning", "agile", "scrum",
      "product discovery", "user story", "backlog", "prioritization"
    ],
    "case_studies": [
      "case study", "post-mortem", "lessons learned", "retrospective",
      "how we built", "behind the scenes"
    ],
    "tools": [
      "Jira", "Figma", "Miro", "ProductBoard", "Linear", "Notion",
      "product analytics", "user research tools"
    ]
  },
  "analysis": {
    "frameworks": "Analyze PM frameworks and methodologies discussed this week. Extract actionable insights for senior PMs. Focus on: decision-making frameworks, prioritization methods, and strategy planning approaches.",
    "case_studies": "Summarize key learnings from PM case studies. Extract: what worked, what failed, key decisions, and applicable lessons for other PMs.",
    "tools": "Identify new PM tools and workflows. Focus on: productivity gains, team collaboration features, and integration capabilities."
  },
  "executive_summary": "Create a digest for a VP of Product covering: emerging frameworks, noteworthy case studies, and tool innovations. Keep it actionable and strategic."
}
```

**Update:** `config/topics.json`
```json
{
  "topics": [
    { "id": "fraud", ... },
    {
      "id": "pm-practices",
      "name": "Product Management Best Practices",
      "enabled": true,
      "rss_config": "config/topics/pm-practices/rss-feeds.json",
      "prompts_config": "config/topics/pm-practices/prompts.json",
      "categories": ["frameworks", "case_studies", "tools"],
      "reddit": {
        "subreddits": ["ProductManagement", "product_design"],
        "queries": ["PM best practices", "product strategy", "roadmap"]
      },
      "fallback_days": 7,
      "color": "#0263E0"
    }
  ]
}
```

#### 2.2 Update Analyzer for Topic-Specific Prompts

**Refactor:** `scripts/analyze/summarizer.py`
```python
class ContentAnalyzerAgent:
    def __init__(self, prompts_config=None, topic_id=None):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.topic_id = topic_id
        
        # Load topic-specific prompts
        if prompts_config:
            with open(prompts_config) as f:
                self.prompts = json.load(f)
        else:
            # Fallback to default fraud prompts
            self.prompts = self._default_prompts()
    
    def _categorize_content(self, collected_data):
        """Use topic-specific keywords from prompts.json"""
        keywords = self.prompts.get('categorization', {})
        # ... use keywords for categorization
```

#### 2.3 Fallback System Per Topic

**Update:** `_load_fallback_data()` in `summarizer.py`
```python
def _load_fallback_data(self, category_name, days_back=7):
    """Load from topic-specific directory"""
    raw_data_dir = Path(f"data/{self.topic_id}/raw")
    
    if not raw_data_dir.exists():
        return []
    
    # ... rest of fallback logic
```

---

### Phase 3: Combined Release & UI (Week 3)

#### 3.1 Multi-Topic Release Publisher

**Create:** `scripts/deliver/multi_topic_release.py`
```python
class MultiTopicReleasePublisher:
    def publish(self, topic_results, date_str):
        """Create single release with all topic reports"""
        
        # Copy all HTMLs to GitHub Pages
        for result in topic_results:
            topic_id = result['id']
            html_path = result['report_html']
            
            pages_dir = Path(f"docs/{topic_id}")
            pages_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy HTML
            shutil.copy(html_path, pages_dir / f"{date_str}.html")
            
            # Update "latest" symlink
            latest = pages_dir / "latest.html"
            if latest.exists():
                latest.unlink()
            latest.symlink_to(f"{date_str}.html")
        
        # Generate combined release notes
        notes = self._generate_combined_notes(topic_results, date_str)
        
        # Create release with all attachments
        attachments = [r['report_html'] for r in topic_results]
        
        subprocess.run([
            "gh", "release", "create",
            f"weekly-digest-{date_str}",
            "--title", f"Weekly Intelligence Digest - {date_str}",
            "--notes-file", notes_file,
            *attachments
        ], check=True)
    
    def _generate_combined_notes(self, results, date_str):
        """Markdown release notes with all topics"""
        notes = f"# Weekly Intelligence Digest\n**{date_str}**\n\n"
        
        for result in results:
            stats = result['stats']
            notes += f"## {result['name']}\n\n"
            notes += f"- **{stats['articles']}** articles analyzed\n"
            notes += f"- **{stats['posts']}** community discussions\n"
            notes += f"- [View Full Report](https://say-das.github.io/PM-RADAR/{result['id']}/{date_str}.html)\n\n"
        
        notes += "\n---\n\n"
        notes += "## 📬 Subscribe\n"
        notes += "Watch this repo and enable **Releases** to get notified.\n"
        
        return notes
```

#### 3.2 Landing Page

**Create:** `docs/index.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>PM Radar - Multi-Topic Intelligence Platform</title>
    <style>
        /* Twilio branding */
        :root {
            --twilio-red: #F22F46;
            --twilio-blue: #0263E0;
        }
        body { font-family: 'Inter', sans-serif; max-width: 1200px; margin: 0 auto; padding: 40px; }
        .topic-card { border: 2px solid #E8EAED; border-radius: 8px; padding: 24px; margin: 20px 0; }
        .topic-card h2 { margin-top: 0; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; }
    </style>
</head>
<body>
    <h1>📡 PM Radar</h1>
    <p>Multi-Topic Weekly Intelligence Digests</p>
    
    <h2>Latest Reports</h2>
    
    <div class="topic-card">
        <h2>🔒 Fraud & Security Intelligence</h2>
        <p>Telecom fraud trends, security threats, and competitive intelligence</p>
        <a href="fraud/latest.html">Latest Report →</a> | 
        <a href="fraud/">Archive</a>
    </div>
    
    <div class="topic-card">
        <h2>📊 Product Management Best Practices</h2>
        <p>Frameworks, case studies, and tools for product leaders</p>
        <a href="pm-practices/latest.html">Latest Report →</a> | 
        <a href="pm-practices/">Archive</a>
    </div>
    
    <div class="topic-card">
        <h2>🤖 AI Innovation Digest</h2>
        <p>Breakthroughs, enterprise adoption, and tooling updates</p>
        <a href="ai-innovations/latest.html">Latest Report →</a> | 
        <a href="ai-innovations/">Archive</a>
    </div>
    
    <hr>
    
    <h2>🔔 Subscribe</h2>
    <p><a href="https://github.com/say-das/PM-RADAR">Watch on GitHub</a> → Custom → Releases</p>
</body>
</html>
```

#### 3.3 Topic Archive Pages

**Generate:** `docs/{topic_id}/index.html` (auto-generated)
```python
def generate_topic_archive(topic_id, reports):
    """List all reports for a topic"""
    html = f"<h1>{topic_name} - Archive</h1>\n<ul>\n"
    for report in sorted(reports, reverse=True):
        date = report.stem
        html += f"<li><a href='{date}.html'>{date}</a></li>\n"
    html += "</ul>"
    return html
```

---

### Phase 4: Management Tools (Week 4)

#### 4.1 Topic Management CLI

**Create:** `scripts/manage_topics.py`
```python
#!/usr/bin/env python3
"""Topic management CLI"""

import click
import json

@click.group()
def cli():
    """PM Radar Topic Manager"""
    pass

@cli.command()
@click.option('--id', required=True)
@click.option('--name', required=True)
@click.option('--rss-config', required=True)
def add(id, name, rss_config):
    """Add a new topic"""
    with open('config/topics.json') as f:
        config = json.load(f)
    
    topic = {
        "id": id,
        "name": name,
        "enabled": True,
        "rss_config": rss_config,
        "categories": [],
        "reddit": None,
        "fallback_days": 7
    }
    
    config['topics'].append(topic)
    
    with open('config/topics.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo(f"✓ Added topic: {name}")

@cli.command()
@click.option('--id', required=True)
def disable(id):
    """Disable a topic"""
    # ... update enabled flag

@cli.command()
@click.option('--id', required=True)
def test(id):
    """Test a single topic pipeline"""
    # ... run pipeline for one topic

@cli.command()
def list():
    """List all topics"""
    with open('config/topics.json') as f:
        config = json.load(f)
    
    for topic in config['topics']:
        status = "✓" if topic['enabled'] else "⊘"
        click.echo(f"{status} {topic['id']}: {topic['name']}")

if __name__ == '__main__':
    cli()
```

**Usage:**
```bash
python scripts/manage_topics.py list
python scripts/manage_topics.py add --id=ai --name="AI Innovations" --rss-config=config/topics/ai/rss-feeds.json
python scripts/manage_topics.py test --id=fraud
python scripts/manage_topics.py disable --id=pm-practices
```

#### 4.2 Update Collection Script

**Update:** `scripts/collect_and_commit.sh`
```bash
#!/bin/bash
# Collect data for all enabled topics

echo "📡 Collecting data for all topics..."

python3 scripts/manage_topics.py list | while read line; do
    if [[ $line == ✓* ]]; then
        topic_id=$(echo $line | awk '{print $2}' | tr -d ':')
        echo "Collecting: $topic_id"
        python3 -c "
from scripts.core.topic_pipeline import TopicPipeline
import json

with open('config/topics.json') as f:
    config = json.load(f)

topic = next(t for t in config['topics'] if t['id'] == '$topic_id')
pipeline = TopicPipeline(topic, '$(date +%Y-%m-%d)')
pipeline._collect()
"
    fi
done

git add data/*/raw/*.json
git commit -m "Prepopulate fallback data for all topics - $(date +%Y-%m-%d)"
git push
```

---

## 🚀 Migration Path

### Step 1: Single Topic Migration
```bash
# Create new structure
mkdir -p config/topics/fraud
mv config/rss_feeds.json config/topics/fraud/rss-feeds.json

# Create topics.json with fraud only
cat > config/topics.json << EOF
{
  "topics": [{
    "id": "fraud",
    "name": "Fraud & Security Intelligence",
    "enabled": true,
    "rss_config": "config/topics/fraud/rss-feeds.json",
    "categories": ["telecom_fraud", "general_fraud", "competitive"],
    "reddit": {
      "subreddits": ["twilio"],
      "queries": ["fraud", "security"]
    }
  }]
}
EOF

# Test
python scripts/main.py
```

### Step 2: Add Second Topic
```bash
python scripts/manage_topics.py add \
  --id=pm-practices \
  --name="PM Best Practices" \
  --rss-config=config/topics/pm-practices/rss-feeds.json
```

### Step 3: Full Platform
- Add remaining topics
- Update landing page
- Monitor performance

---

## 📊 Success Metrics

- ✅ Add new topic in < 30 minutes
- ✅ Zero code changes required (config only)
- ✅ Topics fail independently
- ✅ Backward compatible with fraud research
- ✅ Single combined release notification

---

## 🔍 Key Files Modified

| File | Change |
|------|--------|
| `config/topics.json` | New: Master registry |
| `scripts/main.py` | Refactor: Multi-topic loop |
| `scripts/core/topic_pipeline.py` | New: Per-topic pipeline |
| `scripts/analyze/summarizer.py` | Update: Load prompts from JSON |
| `scripts/deliver/multi_topic_release.py` | New: Combined release |
| `docs/index.html` | New: Landing page |
| `.github/workflows/weekly-report.yml` | Update: Run all topics |

---

**Next Steps:** Start Phase 1 → Refactor for single topic, test backward compatibility
