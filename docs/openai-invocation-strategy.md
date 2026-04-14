# OpenAI Invocation Strategy - Content Analyzer Agent

**Date:** 2026-04-09

## Executive Summary

The Content Analyzer Agent uses a **chunked, category-based approach** to send data to GPT-4o, with built-in safeguards to prevent context overload. Data is **NOT** sent as one massive document.

---

## How OpenAI is Invoked

### Architecture Overview

```
Collected Data (Articles + Reddit)
         ↓
   [1] Categorize Locally (keyword matching - NO API call)
         ↓
    Split into 3 categories:
    - Telecom Fraud
    - General Fraud  
    - Competitive Intelligence
         ↓
   [2] Analyze Each Category Separately (3 API calls max)
         ↓
    Combine results into final report
```

### Step-by-Step Process

#### Step 1: Local Categorization (No API Call)
**Location:** `scripts/analyze/summarizer.py:22-82`

```python
def _categorize_content(self, collected_data):
    # Uses keyword matching - runs locally
    # NO OpenAI API call
```

**Process:**
- Keyword matching on article/post text
- Splits into 3 buckets: Telecom, General, Competitive
- Zero API cost

#### Step 2: Analyze by Category (Separate API Calls)
**Location:** `scripts/analyze/summarizer.py:84-158`

Each category gets its own API call:

**A. Telecom Fraud Analysis**
```python
# Line 132-136
if telecom_count > 0:
    analysis["telecom_fraud_summary"] = self._analyze_category(
        client,
        categorized['telecom'],
        "Telecom Fraud"
    )
```

**B. General Fraud Analysis**
```python
# Line 140-146
if general_count > 0:
    analysis["general_fraud_summary"] = self._analyze_category(
        client,
        categorized['general'],
        "General Fraud & Security"
    )
```

**C. Competitive Intelligence Analysis**
```python
# Line 150-156
if competitive_count > 0:
    analysis["competitive_intelligence_summary"] = self._analyze_competitive(
        client,
        categorized['competitive']
    )
```

---

## Context Overload Protection

### Built-in Safeguards

| Protection | Implementation | Purpose |
|------------|----------------|---------|
| **Article Limit** | 15 per category (Line 225) | Prevent too many articles |
| **Reddit Limit** | 10 posts per category (Line 232) | Limit Reddit data volume |
| **Separate Calls** | 1 call per category | Isolate analysis by topic |
| **Max Response** | 1,500 tokens (Line 209, 268) | Cap GPT-4o output length |
| **Temperature** | 0.3 | Reduce verbosity, focus on facts |

### Context Window Usage

**GPT-4o Specifications:**
- **Model:** `gpt-4o`
- **Context Window:** 128,000 tokens
- **Max Output:** 1,500 tokens (configured)

**Current Usage (2026-04-09 data):**

| Category | Articles | Reddit Posts | Est. Tokens | % of Context |
|----------|----------|--------------|-------------|--------------|
| Telecom Fraud | 4 | 3 | ~2,000 | 1.6% |
| General Fraud | 15 | 10 | ~5,000 | 3.9% |
| Competitive | 0 | 0 | 0 | 0% |

**Safety Margin:** >120,000 tokens per call (93%+ headroom)

---

## What Gets Sent to GPT-4o

### For Articles (Max 15 per call)

```
[ARTICLE_1] Article Title
Source: CISA Advisories
URL: https://...
Published: 2026-04-08
Summary: Full article summary text
```

### For Reddit Posts (Max 10 per call)

```
[REDDIT_1] r/subreddit - Post Title
Score: 10 | Comments: 8
Full text: Complete post body (no truncation!)

Top comments included (up to 10):
- Comment 1 text
- Comment 2 text
...
```

**Key Enhancement:** With the Reddit enrichment we added today, GPT-4o now receives:
- ✅ Full post body (was truncated to 1000 chars)
- ✅ Top 10 comments per post (was 0 comments)
- ✅ Much richer context about customer problems

---

## Prompts Used

### Telecom/General Fraud Analysis Prompt

**System Message:**
```
You are a fraud intelligence analyst specializing in {category_name}. 
Provide actionable insights for product and security teams.
```

**User Prompt Structure:**
```
Analyze this {category_name} intelligence from the past week.

INDUSTRY NEWS:
[ARTICLE_1] ... (up to 15 articles)

SOCIAL DISCUSSIONS:
[REDDIT_1] ... (up to 10 posts with full text + comments)

IMPORTANT INSTRUCTIONS:
1. Include inline citations using [ARTICLE_N] or [REDDIT_N]
2. Use verbatim quotes from Reddit posts
3. Cite multiple sources when applicable

Provide:
1. Executive summary with citations
2. Top 3 trends/threats with citations
3. Regulatory changes with citations
4. Immediate attention items with citations
5. Community sentiment with VERBATIM QUOTES

Format as JSON: executive_summary, top_trends, regulatory_changes, 
                immediate_attention, community_sentiment
```

**Temperature:** 0.3 (factual, less creative)
**Max Tokens:** 1,500

---

## Why This Approach Works

### ✅ Advantages

1. **No Context Overflow**
   - Data is chunked by category
   - Hard limits on articles (15) and posts (10)
   - Each call uses <5% of available context

2. **Better Analysis Quality**
   - Focused prompts per category
   - GPT-4o can deeply analyze each category
   - Citations are category-specific

3. **Cost Efficiency**
   - Only 2-3 API calls per report (not per item)
   - Skip empty categories (no wasted calls)

4. **Scalability**
   - Can add more sources without context issues
   - Limits prevent runaway token usage
   - Predictable costs

5. **Resilience**
   - If one category fails, others still complete
   - Isolated error handling per category

### ⚠️ Limitations & Trade-offs

1. **Cross-Category Insights**
   - GPT-4o analyzes each category independently
   - Cannot connect patterns across Telecom vs General
   - Mitigated by: Good categorization ensures related items are together

2. **Hard Limits May Truncate**
   - If 20 telecom articles collected, only 15 analyzed
   - Reddit posts beyond 10 are ignored
   - Mitigated by: Limits are generous (15/10) and we collect ~35-60 items total

3. **Multiple API Calls = Cost**
   - 2-3 calls per report vs 1 mega-call
   - Mitigated by: Still only ~$0.10-0.30 per report at GPT-4o pricing

---

## Token Estimation

**Formula Used:** 1 token ≈ 4 characters (rough approximation)

**Actual Usage (2026-04-09):**
- 35 RSS articles → ~2,844 tokens
- 25 Reddit posts (with comments) → ~6,829 tokens
- **Total raw data:** ~9,673 tokens

**Per API Call (after limits applied):**
- Telecom Fraud: ~2,000 tokens (4 articles, 3 posts)
- General Fraud: ~5,000 tokens (15 articles, 10 posts)
- Competitive: 0 tokens (no data this week)

**Including Prompt + Response:**
- Prompt overhead: ~500 tokens
- Response: ~1,500 tokens
- **Total per call:** ~7,000 tokens max
- **Cost per call:** ~$0.10 (at GPT-4o rates)

---

## Potential Improvements

### If Context Becomes an Issue

1. **Tiered Limits by Priority**
   ```python
   # Prioritize recent articles
   articles_sorted = sorted(articles, key=lambda x: x['published'], reverse=True)
   top_articles = articles_sorted[:15]
   ```

2. **Summarize Before Sending**
   ```python
   # Pre-compress long articles
   if len(article['summary']) > 500:
       article['summary'] = article['summary'][:500] + "..."
   ```

3. **Two-Pass Analysis**
   ```python
   # Pass 1: Extract key facts (all data)
   # Pass 2: Deep analysis (top 10 items)
   ```

4. **Adaptive Limits**
   ```python
   # Adjust limits based on total data volume
   max_articles = min(15, 100000 // estimated_tokens_per_article)
   ```

### To Improve Cross-Category Insights

1. **Final Synthesis Call**
   ```python
   # After category analysis, send all summaries for meta-analysis
   final_synthesis = gpt4o.analyze([
       telecom_summary,
       general_summary,
       competitive_summary
   ])
   ```

2. **Shared Themes Extraction**
   ```python
   # Identify patterns across categories
   themes = extract_common_themes(all_categories)
   ```

---

## Monitoring Recommendations

### Add Logging for Token Usage

```python
# In _analyze_category()
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o")
input_tokens = len(encoder.encode(combined_content))
print(f"  → Input tokens: {input_tokens:,}")

# After API call
output_tokens = len(encoder.encode(response.choices[0].message.content))
print(f"  → Output tokens: {output_tokens:,}")
print(f"  → Total tokens: {input_tokens + output_tokens:,}")
print(f"  → Context usage: {(input_tokens + output_tokens) / 128000 * 100:.1f}%")
```

### Alert if Approaching Limits

```python
if input_tokens > 100000:  # 78% of context
    print("⚠️  WARNING: Approaching context limit!")
    print(f"   Consider reducing article/post limits")
```

---

## Summary

**Current Strategy: ✅ Well-Designed**

The chunked, category-based approach is appropriate for this use case:
- ✅ Prevents context overflow
- ✅ Maintains quality analysis  
- ✅ Cost-efficient
- ✅ Room to scale

**Is There Risk of Context Overload?** 

**No.** Current usage is ~5,000 tokens per call out of 128,000 available (4%). Even if data volume 10x'd, we'd still be under 50% context usage.

**Key Safeguards:**
- Hard limits: 15 articles, 10 Reddit posts per category
- Separate API calls per category
- Only 2-3 calls per report
- 93%+ headroom in context window

The architecture is production-ready and can handle significant growth before needing optimization.
