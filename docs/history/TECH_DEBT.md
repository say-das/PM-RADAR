# Technical Debt Tracker

Issues deferred for post-MVP cleanup.

---

## High Priority

*None currently*

---

## Medium Priority

### 1. SSL Certificate Verification

**Issue:** RSS collector disables SSL verification (`verify=False`) to avoid macOS certificate issues

**Current Impact:**
- Generates warning messages during collection
- Not a security risk (only reading public RSS feeds)
- All 12 RSS sources working correctly

**Why Deferred:**
- Doesn't affect functionality
- Low security risk (public read-only data)
- Warnings are cosmetic

**Proper Fix:**
- Install proper CA certificates in production environment
- Use `verify=True` with correct cert bundle path
- Alternative: Use `certifi` library for cross-platform certs

**Temporary Fix (if warnings are annoying):**
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

**Estimated Effort:** 2-3 hours (testing across environments)

**References:**
- Code: `scripts/collect/rss_collector.py` line ~45
- Decision documented: thought-process.md, Session 2

**Date Added:** 2026-04-03

---

## Low Priority

*None currently*

---

## Resolved

*None yet*

---

## How to Use This File

**Adding tech debt:**
1. Document the issue clearly
2. Explain why it's deferred
3. Provide proper fix approach
4. Estimate effort
5. Link to relevant code/docs

**Prioritization:**
- **High:** Blocks production, security risk, or affects data quality
- **Medium:** Cosmetic issues, performance optimization, code quality
- **Low:** Nice-to-have improvements, future features

**Resolution:**
When fixed, move to "Resolved" section with date and PR/commit reference.
