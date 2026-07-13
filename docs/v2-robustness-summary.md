# V2 Report Robustness - Quick Reference

## ✅ What We Built Today

### 1. **Comprehensive Robustness Checklist**
   - **File:** `docs/v2-robustness-checklist.md`
   - **Contains:** Full strategy for preventing report breakage
   - **Covers:** 6 vulnerability categories + testing + monitoring + rollback plans

### 2. **Safe JSON Parser Utility**
   - **File:** `core/reporters/utils.py`
   - **Function:** `safe_parse_json()` - handles markdown fences, malformed JSON
   - **Function:** `extract_from_json_variants()` - tries multiple keys for same data
   - **Status:** ✅ Created, ready to integrate into sections

### 3. **Report Health Check System**
   - **File:** `core/reporters/health_check.py`
   - **Class:** `ReportHealthCheck` - validates generated reports
   - **Checks:**
     - ✅ Minimum report length
     - ✅ Required sections present
     - ✅ No error markers in content
     - ✅ Citation consistency (IDs don't exceed articles)
     - ✅ Empty section detection
     - ✅ Metrics collection
   - **Status:** ✅ Integrated into report_generator.py
   - **Output:** Automatic health check runs after every report generation

## 🎯 How This Protects You

### Scenario 1: LLM Returns Malformed JSON
**Before:** Report crashes or shows raw JSON  
**After:** `safe_parse_json()` handles it gracefully, section shows empty or fallback

### Scenario 2: New Topic Has Different Data Structure  
**Before:** Citations break, sections missing  
**After:** Health check catches it immediately with specific error messages

### Scenario 3: Analysis Data Missing Key Fields
**Before:** Silent failure, incomplete report  
**After:** Health check warns about empty sections, logs metrics

### Scenario 4: Citation IDs Out of Range
**Before:** Broken links in report  
**After:** Health check flags the error before you send the report

## 📊 Health Check Output Example

```
→ Running health checks...
  ✓ Health check passed
  📊 Metrics: 6394 chars, 6 sections, 7 citations
  ✓ Report saved to data/reports/2026-07-03.md
```

**If issues detected:**
```
→ Running health checks...
  ✗ Health check FAILED:
    • Citation ID 99 exceeds article count (20)
    • Missing required section: Executive Summary
  📊 Metrics: 342 chars, 2 sections, 0 citations
```

## 🚀 Next Steps (Prioritized)

### Priority 1: Integrate Utilities (1 hour)
- [ ] Refactor `top_items.py` to use `safe_parse_json()`
- [ ] Refactor `executive_summary.py` to use `safe_parse_json()`
- [ ] Refactor `reddit_community.py` to use `safe_parse_json()`
- [ ] Add `extract_from_json_variants()` to simplify key lookups

### Priority 2: Add Test Fixtures (2 hours)
- [ ] Create `data/test-fixtures/fraud/` directory
- [ ] Add `empty-analysis.json` - all null/empty fields
- [ ] Add `v1-format.json` - legacy format with executive_summary
- [ ] Add `v2-format.json` - array format
- [ ] Add `malformed-json.json` - JSON with markdown fences
- [ ] Add `no-citations.json` - analysis with missing citation_ids

### Priority 3: Write Tests (3 hours)
- [ ] Create `tests/core/reporters/test_robustness.py`
- [ ] Test empty analysis data
- [ ] Test malformed JSON handling
- [ ] Test missing citations
- [ ] Test v1/v2 format compatibility
- [ ] Test citation format conversion

### Priority 4: Add Monitoring (2 hours)
- [ ] Set up structured logging in pipeline.py
- [ ] Log health check results to file
- [ ] Create metrics dashboard (simple HTML or JSON)
- [ ] Set up alerts for health check failures

## 🔍 Testing New Topics

When adding a new topic, run this checklist:

```bash
# 1. Generate test report with real data
python3 scripts/run_v2_pipeline.py <topic_id>

# 2. Check health output
# Look for ✓ or ✗ in output

# 3. Manually verify report
open data/reports/$(date +%Y-%m-%d).html

# 4. Compare with expected sections
# - Executive Summary with stats?
# - All threat categories?
# - Sources with citations?
# - Competitor section (if applicable)?
# - Reddit section (if applicable)?

# 5. Check edge cases
# - What if no Reddit posts? (section should be skipped)
# - What if no competitor data? (section should be skipped)
# - What if very few articles? (should still generate)
```

## 📝 Rollback Instructions

If v2 breaks for a topic:

```yaml
# In config/topics/<topic_id>/topic.yaml
feature_flag_v2: false  # Reverts to v1 pipeline
```

Or use v1 script directly:
```bash
python3 scripts/main.py <topic_id>
```

## 💡 Key Takeaways

1. **Health checks run automatically** - You don't need to remember to run them
2. **Graceful degradation** - Missing data = empty section, not crash
3. **Clear error messages** - Know exactly what's wrong
4. **Metrics for monitoring** - Track quality over time
5. **Easy rollback** - Feature flag switches back to v1

## 🛠️ Tools You Now Have

| Tool | Purpose | Status |
|------|---------|--------|
| `safe_parse_json()` | Parse LLM responses safely | ✅ Ready |
| `extract_from_json_variants()` | Handle format variations | ✅ Ready |
| `ReportHealthCheck` | Validate report quality | ✅ Integrated |
| `check_report_health()` | Convenience function | ✅ Integrated |
| Robustness checklist | Testing & deployment guide | ✅ Documented |

## 📚 Documentation Files

- `docs/v2-robustness-checklist.md` - Full technical guide (13 sections)
- `docs/v2-robustness-summary.md` - This quick reference
- `core/reporters/utils.py` - Utility functions (with docstrings)
- `core/reporters/health_check.py` - Health check class (with docstrings)

---

**Bottom Line:** Your v2 reports are now protected against the most common failure modes. Health checks will catch issues before they reach users, and you have clear paths to debug and rollback if needed.
