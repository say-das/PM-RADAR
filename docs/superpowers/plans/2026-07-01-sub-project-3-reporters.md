# PM Radar v2 - Sub-Project 3: Reporters & Section Library

**Goal:** Build configurable report generation with reusable section components

**Duration:** ~4 days (estimated)

**Branch:** `feature/v2-multi-topic-platform` (continue)

---

## Success Criteria

- ✅ BaseSection interface for report sections
- ✅ Section implementations (executive_summary, top_items, competitive_intel, etc.)
- ✅ ReportGenerator assembles reports from topic config
- ✅ Generated reports match v1 quality
- ✅ Global styling applied from config/global.yaml

---

## Architecture

```
core/reporters/
├── base_section.py          # BaseSection interface
├── report_generator.py      # ReportGenerator orchestrator
└── sections/
    ├── executive_summary.py
    ├── top_items.py
    ├── competitive_intel.py
    ├── reddit_community.py
    └── sources.py
```

**Report Flow:**
1. ReportGenerator loads topic config
2. For each section in `topic.yaml`: `report.sections`
3. Instantiate section class with config + analysis data
4. Call `section.render()` → markdown string
5. Assemble all sections into full report
6. Apply global styling (colors, fonts from global.yaml)
7. Save as markdown

---

## Task Breakdown

### Task 1: BaseSection Interface
**Goal:** Define abstract base class for report sections

**Files:**
- `core/reporters/base_section.py`
- `core/reporters/__init__.py`
- `tests/core/reporters/test_base_section.py`

**Steps:**
1. Create BaseSection abstract class
2. Add `render()` abstract method
3. Add helper methods (format_citation, format_date)
4. Test with mock section

---

### Task 2: Core Section Implementations
**Goal:** Implement essential report sections

**Files:**
- `core/reporters/sections/executive_summary.py`
- `core/reporters/sections/top_items.py`
- `core/reporters/sections/sources.py`
- `tests/core/reporters/sections/test_sections.py`

**Steps:**
1. ExecutiveSummarySection - renders analysis executive summary
2. TopItemsSection - renders top threats/trends with citations
3. SourcesSection - renders article references with links
4. Test each section with sample data

---

### Task 3: ReportGenerator
**Goal:** Orchestrate report assembly from config

**Files:**
- `core/reporters/report_generator.py`
- `tests/core/reporters/test_report_generator.py`

**Steps:**
1. Load topic config + global config
2. Section factory (type → class mapping)
3. Render each configured section
4. Assemble into full markdown report
5. Apply metadata (date, title)
6. Save to file
7. Test with fraud topic

---

### Task 4: Integration Test
**Goal:** Verify end-to-end collect → analyze → report

**Files:**
- `tests/test_integration_sub_project_3.py`

**Steps:**
1. Full pipeline: collect → analyze → report
2. Verify report structure
3. Verify report content quality
4. Compare with v1 report format

---

## Section Details

**ExecutiveSummarySection:**
- Input: `analysis["telecom_fraud_summary"]` executive_summary field
- Output: "## Executive Summary" with formatted text

**TopItemsSection (configurable):**
- Config: `title`, `category`, `limit`
- Input: analysis summary for category (telecom/general)
- Output: "## {title}" with top threats list + citations

**SourcesSection:**
- Input: `analysis["filtered_articles"]`
- Output: "## Sources" with numbered citations `[A1], [A2], ...`

**CompetitiveIntelSection (optional):**
- Input: `analysis["competitive_intelligence_summary"]`
- Output: "## Competition Watch" with competitor insights

**RedditCommunitySection (optional):**
- Input: `analysis["reddit_community_summary"]`
- Output: "## Community Discussions" with Reddit insights

---

## Deferred Features

**To Sub-Project 4:**
- Email delivery (use existing v1 script)
- GitHub Pages publishing
- PDF generation

**Future Enhancements:**
- Chart/visualization sections
- Custom CSS per topic
- Section templates (Jinja2)

---

## Estimated Timeline

- Task 1: BaseSection - 1 hour
- Task 2: Core Sections - 2 hours
- Task 3: ReportGenerator - 2 hours
- Task 4: Integration Test - 1 hour

**Total: ~6 hours (1 focused day)**
