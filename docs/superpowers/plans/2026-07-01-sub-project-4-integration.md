# PM Radar v2 - Sub-Project 4: Integration & Migration

**Goal:** Complete v2 pipeline with full orchestration and v1/v2 coexistence

**Duration:** ~3 days (estimated)

**Branch:** `feature/v2-multi-topic-platform` (final phase)

---

## Success Criteria

- ✅ TopicPipeline orchestrates full collect → analyze → report → deliver flow
- ✅ Feature flag system enables v1/v2 coexistence
- ✅ End-to-end test produces complete report from real data
- ✅ v2 report quality matches or exceeds v1
- ✅ Documentation for running v2 pipeline

---

## Architecture

```
core/
├── pipeline.py              # TopicPipeline orchestrator
└── delivery/
    └── email_sender.py      # Email delivery (light wrapper around v1)

scripts/
└── run_v2_pipeline.py       # CLI entry point for v2
```

**Pipeline Flow:**
1. TopicPipeline loads topic config
2. Collect: CollectorOrchestrator → raw data
3. Analyze: ContentSummarizer → analysis results
4. Report: ReportGenerator → markdown report
5. Deliver: EmailSender → send to recipients (optional)
6. Save outputs at each stage

---

## Task Breakdown

### Task 1: TopicPipeline Orchestrator
**Goal:** Create main pipeline that connects all components

**Files:**
- `core/pipeline.py`
- `tests/core/test_pipeline.py`

**Steps:**
1. Load topic config
2. Run collection phase (save raw data)
3. Run analysis phase (save analysis)
4. Run report phase (save markdown)
5. Optional delivery phase
6. Return pipeline results
7. Test with fraud topic

---

### Task 2: Email Delivery Integration
**Goal:** Add email delivery to v2 pipeline

**Files:**
- `core/delivery/__init__.py`
- `core/delivery/email_sender.py`
- `tests/core/delivery/test_email_sender.py`

**Steps:**
1. Create EmailSender class (wrapper around v1)
2. Load recipients from topic config
3. Send report via Brevo API
4. Test with dry-run mode

---

### Task 3: CLI Entry Point
**Goal:** Create command-line interface for v2 pipeline

**Files:**
- `scripts/run_v2_pipeline.py`

**Steps:**
1. Argument parsing (topic, flags)
2. Run pipeline with options
3. Display progress and results
4. Test manual execution

---

### Task 4: End-to-End Validation
**Goal:** Verify complete v2 pipeline matches v1 quality

**Files:**
- `tests/test_integration_final.py`

**Steps:**
1. Run full pipeline on fraud topic
2. Verify all outputs created
3. Compare v2 report quality with latest v1 report
4. Validate report content and structure
5. Document any differences

---

## Feature Flag Strategy

**Current Approach (Deferred):**
- v1 and v2 pipelines are separate scripts
- v1: `scripts/main.py` (unchanged, on main branch)
- v2: `scripts/run_v2_pipeline.py` (on feature branch)
- No runtime feature flags needed yet
- Migration: switch script invocation when ready

**Future Enhancement:**
- Add `feature_flag_v2` to topic.yaml
- Single entry point that routes to v1 or v2
- Gradual topic-by-topic migration

---

## Delivery Options

**Implemented:**
- Save report to `data/reports/{date}.md`
- Save raw data to `data/raw/{date}.json`
- Save analysis to `data/raw/{date}-analysis.json`

**Optional (Deferred to Post-Launch):**
- Email delivery (can use v1 script)
- GitHub Pages publishing
- PDF generation
- Slack notifications

---

## Success Metrics

**Pipeline Completeness:**
- ✅ Collects data from all sources
- ✅ Analyzes with LLM providers
- ✅ Generates formatted report
- ✅ All outputs saved properly

**Quality Comparison (v1 vs v2):**
- Same or more articles collected
- Similar categorization accuracy
- Comparable analysis depth
- Equivalent or better report formatting

**Performance:**
- Pipeline completes in reasonable time (<5 min)
- Caching reduces redundant API calls
- Error handling prevents partial failures

---

## Estimated Timeline

- Task 1: TopicPipeline - 2 hours
- Task 2: Email Delivery - 1 hour
- Task 3: CLI Entry Point - 1 hour
- Task 4: Final Validation - 2 hours

**Total: ~6 hours (1 focused day)**

---

## Post-Launch Enhancements

**Phase 2 Features (Future):**
- Multi-topic support (run multiple topics in parallel)
- Scheduling/automation (cron integration)
- Report diff/comparison tools
- Analytics dashboard
- Custom section plugins
- Template system (Jinja2)
- A/B testing for prompts

**Phase 3 Features (Long-term):**
- Web UI for configuration
- Real-time monitoring dashboard
- AI-powered summarization improvements
- Custom LLM fine-tuning
- Integration with internal tools
