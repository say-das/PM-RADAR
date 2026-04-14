# Reddit Comments Fix - Now Sent to OpenAI

**Date:** 2026-04-09  
**Issue:** Comments were collected but NOT sent to GPT-4o for analysis

---

## Problem Discovered

While Reddit comments were successfully collected (69 comments from 16 posts), they were **NOT being sent to OpenAI** for analysis.

**Original Code (Line 230-233):**
```python
post_text = "\n\n".join([
    f"[REDDIT_{i}] r/{p['subreddit']} - {p['title']}\n"
    f"Score: {p['score']} | Comments: {p['num_comments']}\n"
    f"Full text: {p.get('selftext', 'N/A')}"
    for i, p in enumerate(posts[:10], 1)
])
```

**What was sent:**
- ✓ Title
- ✓ Score
- ✓ Comment COUNT (number only)
- ✓ Post text
- ❌ Actual comments (MISSING!)

---

## Solution Implemented

### Optimized Format Sent to OpenAI

**File:** `scripts/analyze/summarizer.py:229-248`

```python
for i, p in enumerate(posts[:10], 1):
    post_str = (
        f"[REDDIT_{i}]\n"
        f"Title: {p['title']}\n"
        f"Post: {p.get('selftext', '(no text)')}\n"
        f"Score: {p['score']} | URL: {p.get('url', 'N/A')}"
    )

    # Add top 10 comments if present
    comments = p.get('comments', [])
    if comments:
        post_str += f"\nComments ({len(comments)}):"
        for comment in comments[:10]:  # Top 10 comments
            post_str += f"\n  - [{comment['score']} pts] {comment['body']}"
```

### What Gets Sent Now

**Included (Essential):**
- ✅ Title (full)
- ✅ Post text (full)
- ✅ Score
- ✅ URL
- ✅ **Top 10 comments with scores** (NEW!)

**Excluded (Unnecessary):**
- ❌ Author names (not needed for analysis)
- ❌ Subreddit (already in citation context)
- ❌ Upvote ratio (score is sufficient)
- ❌ Timestamps (not relevant for weekly analysis)
- ❌ Comment author names (content matters, not who said it)

---

## Example: What GPT-4o Receives

```
[REDDIT_1]
Title: Twilio Fraud Operations suspended my solo‑dev account, any alternatives in USA?
Post: 
Score: 0 | URL: https://www.reddit.com/r/twilio/comments/1s0bmjf/twilio_fraud_operations_suspended_my_solodev/
Comments (5):
  - [2 pts] Infobip
  - [2 pts] Blooio no a2p and you'll be sending instantly. No approvals no wait period no bs
  - [1 pts] I've used twilio for years. Never had any issues. They require the items from ctia best practices iirc...
  - [1 pts] I've been round and round with fraud team trying to get my business account activated...
  - [1 pts] Twilio's support is overseas. If your site is behind security that restricts connection from overseas...
```

---

## Updated Prompt

Also updated the prompt to explicitly tell GPT-4o about comments:

**New Instructions (Line 256-266):**
```
2. For Reddit: Include specific verbatim quotes from posts AND comments using [REDDIT_N] notation
   - Reddit posts include both the original post text and community comments
   - Use actual quotes from users and commenters to show real customer sentiment

5. If Reddit discussions present: key concerns with VERBATIM QUOTES from posts AND comments
   - Pay special attention to comments as they reveal additional customer pain points, 
     workarounds, and validation of issues
```

---

## Impact on Analysis Quality

### Before (Without Comments)
```
Community Sentiment:
- Users frustrated with account suspensions
```

Generic, surface-level insight from titles only.

### After (With Comments)
```
Community Sentiment:
- **Twilio Account Security**: "I've been round and round with fraud team 
  trying to get my business account activated. Provided my EIN paperwork 3x..."
  
- **Alternative Providers**: Comments mention "Infobip", "Blooio" as alternatives
  with "no approvals no wait period no bs"
  
- **Support Issues**: "Twilio's support is overseas. If your site is behind 
  security that restricts connection from overseas, then they can't access your site"
```

Rich, specific insights with:
- ✅ Actual customer pain points
- ✅ Workarounds attempted (paperwork submitted 3x)
- ✅ Competitor mentions (Infobip, Blooio)
- ✅ Root cause analysis (overseas support + security)

---

## Token Usage

### Per Reddit Post (with comments)

**Before:**
- Title: ~15 tokens
- Post text: ~50 tokens
- Metadata: ~10 tokens
- **Total: ~75 tokens**

**After:**
- Title: ~15 tokens
- Post text: ~50 tokens
- Metadata: ~10 tokens
- 5 comments avg @ 30 tokens each: ~150 tokens
- **Total: ~225 tokens** (+200% increase)

### Per API Call (10 posts)

**Before:** ~750 tokens  
**After:** ~2,250 tokens (+1,500 tokens)

### Context Window Safety

- GPT-4o limit: 128,000 tokens
- Current usage: ~5,000 tokens per call
- **With comments: ~7,000 tokens per call**
- Safety margin: **121,000 tokens (94.5% remaining)**

✅ Still plenty of headroom!

---

## Verification

Tested on 2026-04-09 data:
- ✅ 16 posts had comments
- ✅ 69 total comments collected
- ✅ Comments now sent to GPT-4o
- ✅ Analysis shows comment-derived insights
- ✅ Report includes quotes from comments

Example from generated report:
```
"I've been round and round with fraud team trying to get my business 
account activated. Provided my EIN paperwork 3x. Provided my articles 
of incorporation and other paperwork 3x..."
```

This level of detail was ONLY possible because comments are now analyzed!

---

## Files Modified

1. **scripts/analyze/summarizer.py**
   - Lines 229-248: Updated `_analyze_category()` to include comments
   - Lines 256-266: Updated prompt to instruct GPT-4o about comments

---

## Summary

**Issue:** ❌ Comments collected but not analyzed  
**Solution:** ✅ Send top 10 comments per post to GPT-4o  
**Format:** Optimized (only essential fields)  
**Impact:** Much richer customer problem insights  
**Cost:** +~1,500 tokens per API call (~$0.03 more per report)  
**Safety:** Still using only 5-7% of context window  

**Result:** GPT-4o now analyzes actual customer conversations, not just post titles!
