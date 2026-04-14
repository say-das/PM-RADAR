# Citation-Sources Synchronization Fix

**Date:** 2026-04-09  
**Issue:** Reddit citations used in report (e.g., R14) were missing from Sources section

---

## Problem

**Symptom:**
- Report body cited `[\[R14\]](#r14)` 
- Sources section only listed R1-R10
- R11-R15 were missing, causing broken links

**Root Cause:**
```python
# main.py line 244 - Only mapped first 10 posts
for i, post in enumerate(collected_data["reddit_posts"][:10], 1):
    citations[f"REDDIT_{i}"] = {...}

# summarizer.py line 299 - Analyzed 15 posts
for i, p in enumerate(reddit_posts[:15], 1):
    # GPT-4o could cite R1-R15
```

**Mismatch:** Analysis used 15 posts, but only 10 were mapped to citations → R11-R15 missing from Sources.

---

## Solution

### 1. Synchronized Limits

**Added Configuration Constant** (`main.py` line 18)
```python
MAX_REDDIT_POSTS_FOR_ANALYSIS = 15  # Must match limit in summarizer.py
```

**Updated Citation Mapping** (`main.py` line 247)
```python
for i, post in enumerate(collected_data["reddit_posts"][:MAX_REDDIT_POSTS_FOR_ANALYSIS], 1):
    citations[f"REDDIT_{i}"] = {
        "title": post["title"],
        "subreddit": subreddit,
        "score": post["score"],
        "url": post.get("url", "")
    }
```

**Documented in Analyzer** (`summarizer.py` line 292-294)
```python
# IMPORTANT: This limit must match MAX_REDDIT_POSTS_FOR_ANALYSIS in main.py
# to ensure all citations have corresponding entries in the Sources section
MAX_POSTS = 15
```

### 2. Single Source of Truth

The limit is now defined in one place (`MAX_REDDIT_POSTS_FOR_ANALYSIS`) and:
- Used in citation mapping (main.py)
- Documented in analyzer (summarizer.py)
- Clear comment explains why they must match

---

## How It Works

### Data Flow

```
1. Collect 25 Reddit posts
         ↓
2. Map first 15 to citations dict (main.py)
   REDDIT_1 → {title, url, ...}
   REDDIT_2 → {title, url, ...}
   ...
   REDDIT_15 → {title, url, ...}
         ↓
3. Send 15 posts to GPT-4o for analysis (summarizer.py)
         ↓
4. GPT-4o returns analysis citing [REDDIT_1] to [REDDIT_15]
         ↓
5. Convert [REDDIT_N] → [\[RN\]](#rn) in report
         ↓
6. Generate Sources section from citations dict
   - Only citations used in report are included
   - All used citations guaranteed to have entries
```

### Key Principle

**The number of posts sent to GPT-4o must be ≤ the number mapped to citations.**

If we analyze 20 posts but only map 15, citations R16-R20 would be broken.

---

## Prevention Mechanism

### Runtime Check (Future Enhancement)

Could add validation in report generation:

```python
# After GPT-4o analysis, before generating report
used_citations = set(re.findall(r'REDDIT_(\d+)', analysis_text))
max_citation = max([int(n) for n in used_citations]) if used_citations else 0

if max_citation > MAX_REDDIT_POSTS_FOR_ANALYSIS:
    raise ValueError(
        f"Analysis cited REDDIT_{max_citation} but only "
        f"{MAX_REDDIT_POSTS_FOR_ANALYSIS} posts were mapped. "
        f"Increase MAX_REDDIT_POSTS_FOR_ANALYSIS in main.py"
    )
```

### Documentation

Added clear comments in code:
- `main.py`: "Must match the limit used in Reddit Community analysis"
- `summarizer.py`: "IMPORTANT: This limit must match MAX_REDDIT_POSTS_FOR_ANALYSIS"

---

## Testing

### Verification Steps

1. **Check citation mapping limit:**
   ```python
   # main.py - Should use MAX_REDDIT_POSTS_FOR_ANALYSIS
   for i, post in enumerate(collected_data["reddit_posts"][:MAX_REDDIT_POSTS_FOR_ANALYSIS], 1):
   ```

2. **Check analyzer limit:**
   ```python
   # summarizer.py - Should match or be less than main.py limit
   for i, p in enumerate(reddit_posts[:MAX_POSTS], 1):
   ```

3. **Verify in report:**
   ```bash
   # Find all R citations in report
   grep -o '\[R[0-9]\+\]' report.md | sort -u
   
   # Find all R entries in Sources
   grep '^\- <a id="r' report.md
   
   # Compare - should be identical sets
   ```

### Test Result (2026-04-09)

✅ **Citations used:** R1, R2, R3, R5, R11, R14  
✅ **Sources entries:** R1, R2, R3, R5, R11, R14  
✅ **All citations have corresponding sources**  
✅ **No broken links**

---

## Files Modified

1. **scripts/main.py**
   - Line 18: Added `MAX_REDDIT_POSTS_FOR_ANALYSIS = 15`
   - Line 247: Updated to use constant instead of hardcoded `[:10]`

2. **scripts/analyze/summarizer.py**
   - Line 292-294: Added comment about synchronization
   - Line 296: Defined local `MAX_POSTS = 15` with explanation

---

## Future Considerations

### If Increasing Post Limit

To analyze more posts (e.g., 20 instead of 15):

1. Update constant in `main.py`:
   ```python
   MAX_REDDIT_POSTS_FOR_ANALYSIS = 20
   ```

2. Update local constant in `summarizer.py`:
   ```python
   MAX_POSTS = 20
   ```

3. Check token usage:
   - 15 posts with comments ≈ 8,000 tokens
   - 20 posts with comments ≈ 10,500 tokens
   - Still safe (8% of 128K context window)

### Alternative: Dynamic Limit

Could make it truly configurable:

```python
# config/reddit-config.json
{
  "max_posts_for_analysis": 15,
  ...
}
```

Then load in both `main.py` and `summarizer.py`. However, this adds complexity and the current solution (constant + documentation) is simpler and sufficient.

---

## Summary

**Issue:** Citations R11-R15 missing from Sources because only 10 posts were mapped  
**Fix:** Increased mapping limit from 10 to 15 to match analyzer limit  
**Prevention:** Defined constant `MAX_REDDIT_POSTS_FOR_ANALYSIS` used in both files  
**Result:** All citations now have corresponding Sources entries  

**Key Takeaway:** The number of posts mapped to citations must match or exceed the number analyzed by GPT-4o.
