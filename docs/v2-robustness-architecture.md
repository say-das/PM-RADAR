# V2 Report Generation - Robustness Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         REPORT GENERATION FLOW                       │
└─────────────────────────────────────────────────────────────────────┘

INPUT: analysis_data.json
    │
    ├─ [VALIDATION] JSON Schema Check (future)
    │       ├─ Valid? → Continue
    │       └─ Invalid? → Log error, use safe defaults
    │
    ▼
┌──────────────────────────┐
│  ReportGenerator.generate()  │
└──────────────────────────┘
    │
    ├─ PHASE 1: Render Sections (except Sources)
    │   │
    │   ├─ ExecutiveSummarySection
    │   │   └─ [SAFE PARSE] safe_parse_json() ✓
    │   │
    │   ├─ TopItemsSection (telecom)
    │   │   └─ [SAFE PARSE] safe_parse_json() ✓
    │   │   └─ [FALLBACK] Multiple key attempts
    │   │   └─ [GRACEFUL] Returns empty if no data
    │   │
    │   ├─ TopItemsSection (general)
    │   │   └─ [SAFE PARSE] safe_parse_json() ✓
    │   │
    │   ├─ RedditCommunitySection
    │   │   └─ [SAFE PARSE] safe_parse_json() ✓
    │   │   └─ [SKIP] Returns "" if no data
    │   │
    │   └─ CompetitiveIntelSection
    │       └─ [SKIP] Returns "" if no data
    │
    ├─ PHASE 2: Post-Process Citations
    │   │
    │   └─ _convert_citations()
    │       ├─ [ARTICLE_1] → [\[A1\]](#a1)
    │       ├─ [REDDIT_1] → [\[R1\]](#r1)
    │       └─ [COMP_1] → [\[C1\]](#c1)
    │
    ├─ PHASE 3: Render Sources Section
    │   │
    │   └─ SourcesSection
    │       └─ _extract_used_citations()
    │           ├─ Parse converted citations
    │           ├─ Filter to only cited articles
    │           └─ Generate anchor links
    │
    ├─ PHASE 4: Health Check ✓ NEW!
    │   │
    │   └─ check_report_health()
    │       ├─ Check: Minimum length
    │       ├─ Check: Required sections
    │       ├─ Check: No error markers
    │       ├─ Check: Citation consistency
    │       ├─ Check: Empty sections
    │       └─ Collect: Metrics
    │           │
    │           ├─ Status: ok / warning / error
    │           ├─ Warnings: []
    │           ├─ Errors: []
    │           └─ Metrics: {length, sections, citations}
    │
    ▼
OUTPUT: report.md
    │
    └─ [OPTIONAL] HTML Conversion → report.html


┌─────────────────────────────────────────────────────────────────────┐
│                         ERROR HANDLING                                │
└─────────────────────────────────────────────────────────────────────┘

    JSON Parse Fails
         │
         ├─ safe_parse_json() catches error
         ├─ Logs warning with section name
         ├─ Returns None
         └─ Section shows: "*No items identified*"
              (graceful degradation)

    Citation ID > Article Count
         │
         ├─ Health check detects mismatch
         ├─ Logs error: "Citation ID 99 exceeds article count (20)"
         └─ Report still generated (allows debugging)

    Section Rendering Fails
         │
         ├─ try/catch in report_generator
         ├─ Logs error with traceback
         ├─ Shows: "## Section\n*Error rendering section*"
         └─ Other sections continue rendering


┌─────────────────────────────────────────────────────────────────────┐
│                    SAFETY LAYERS (Defense in Depth)                   │
└─────────────────────────────────────────────────────────────────────┘

    Layer 1: INPUT VALIDATION (future)
        └─ JSON Schema validation on analysis_data

    Layer 2: SAFE PARSING ✓
        └─ safe_parse_json() handles markdown fences, malformed JSON

    Layer 3: GRACEFUL DEGRADATION ✓
        └─ Missing data → empty section (not crash)

    Layer 4: ERROR ISOLATION ✓
        └─ One section fails → others continue

    Layer 5: HEALTH CHECK ✓
        └─ Validates output before saving

    Layer 6: MONITORING (future)
        └─ Log metrics, alert on degradation


┌─────────────────────────────────────────────────────────────────────┐
│                         TESTING PYRAMID                               │
└─────────────────────────────────────────────────────────────────────┘

                        E2E Tests
                      (Full Pipeline)
                     ╱              ╲
                Integration Tests
              (Section → Report)
            ╱                        ╲
        Unit Tests
    (Individual Functions)
    - safe_parse_json() ✓
    - citation conversion ✓
    - health checks ✓


┌─────────────────────────────────────────────────────────────────────┐
│                      ROLLBACK STRATEGY                                │
└─────────────────────────────────────────────────────────────────────┘

    Production Issue Detected
         │
         ├─ IMMEDIATE: Set feature_flag_v2: false
         │             (reverts to v1 in <1 minute)
         │
         ├─ DEBUG: Check logs & health check output
         │         tail -100 data/logs/pipeline-*.log
         │
         ├─ REPRODUCE: Run with latest analysis file
         │             python3 scripts/run_v2_pipeline.py fraud \
         │                     --skip-collection --skip-analysis
         │
         ├─ FIX: Address root cause
         │       (health check output guides diagnosis)
         │
         └─ VALIDATE: Run test suite before re-deploy
                      pytest tests/core/reporters/test_robustness.py


┌─────────────────────────────────────────────────────────────────────┐
│                    KEY DESIGN PRINCIPLES                              │
└─────────────────────────────────────────────────────────────────────┘

    1. FAIL GRACEFULLY
       └─ Never crash → always generate something

    2. VALIDATE EARLY
       └─ Check format before processing

    3. LOG EVERYTHING
       └─ Make debugging easy

    4. ISOLATE ERRORS
       └─ One failure doesn't cascade

    5. MONITOR METRICS
       └─ Detect degradation early

    6. EASY ROLLBACK
       └─ Feature flag → instant revert
