# Agent-Ready PRD Framework
## Writing Specifications That Enable Smooth AI Agent Collaboration

---

## The Problem

AI agents excel at execution but struggle when specifications are:
- **Implicit** - "Make it work" means different things to humans vs agents
- **Incomplete** - Missing context about why decisions were made
- **Ambiguous** - "Better" or "fixed" are subjective without measurable criteria
- **Unconstrained** - What NOT to change is as important as what to change

**Result:** Back-and-forth questions, multiple iterations, wasted time.

---

## The Golden Rule

> **"If the agent needs to ask a clarifying question, the PRD was incomplete."**

Every clarifying question indicates missing:
- **Context** - Why this matters, current state
- **Behavior** - How it should work, edge cases
- **Validation** - How to verify success
- **Constraints** - What must NOT change

---

## The 4-Layer Specification Model

```
┌─────────────────────────────────────────────┐
│  1. CONTEXT LAYER                           │
│  Why it matters + Current state             │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│  2. BEHAVIOR LAYER                          │
│  How it should work + Edge cases            │
└─────────────────────────────────────────────┐
            ↓
┌─────────────────────────────────────────────┐
│  3. VALIDATION LAYER                        │
│  How to verify + Acceptance tests           │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│  4. CONSTRAINTS LAYER                       │
│  What NOT to change + Dependencies          │
└─────────────────────────────────────────────┘
```

---

## Layer 1: CONTEXT (Why & Current State)

### Purpose
Set the stage so the agent understands:
- **Why** this work matters
- **What** currently exists
- **Who** is affected
- **Where** relevant code lives

### What to Include

**1. Problem Statement**
- What's broken or missing?
- Why does it matter?
- Who is affected?
- Business impact if not fixed

**2. Current State** ⚠️ **Critical!**
- **File paths** where relevant code lives
- **Current implementation** (code snippet if < 20 lines)
- **What works** vs what doesn't
- **Dependencies** that affect this component

**3. Desired State**
- **Concrete example** of success
- **Sample input/output** with real data
- **Visual mockup** if UI-related
- **Success metrics** (numbers, not adjectives)

**4. Background Context**
- **Domain knowledge** agent needs to know
- **Historical decisions** that constrain solutions
- **Why previous approach** was chosen
- **Related systems** that interact with this

---

### Good vs Bad Examples

#### ❌ BAD (Implicit, No Context):
```
"Fix the categorization issue"
```

Problems:
- What categorization?
- What's the issue?
- Where is the code?
- Why does it matter?

#### ✅ GOOD (Explicit Context):
```
**Problem:** Articles from specialized sources not appearing in correct report section

**Current State:**
- File: `scripts/analyze/categorizer.py` lines 45-67
- Logic: Keyword-based matching only
- Issue: "Telecom Weekly" source publishes monthly, last article 20 days ago
- Collection window: 7 days (config: `sources.json`)
- Result: 0 articles in "Telecom" section despite being telecom source

**Why it matters:**
- Telecom section is primary use case for stakeholders
- Empty section makes weekly report incomplete
- "Telecom Weekly" is authoritative industry source

**Desired State:**
- Report shows 2-3 articles in Telecom section weekly
- Source metadata (not just keywords) determines category
- Example: All articles from "Telecom Weekly" → Telecom category

**Domain Knowledge:**
- "Telecom Weekly" publishes first Monday of each month
- Content is ALWAYS telecom-related (no keyword filtering needed)
- Adding daily source "TelecomDaily.com" would supplement weekly source
```

---

## Layer 2: BEHAVIOR (How It Works)

### Purpose
Eliminate ambiguity about:
- **How** the system should behave
- **What** happens in edge cases
- **When** different logic paths execute
- **Format** of inputs/outputs

### What to Include

**1. Data Flow** (Input → Processing → Output)
- **Input format** with example
- **Processing steps** (numbered, sequential)
- **Output format** with example
- **Where data goes** (file paths, databases)

**2. Decision Rules** (If/Then Logic)
- **Priority order** (what gets checked first)
- **Edge case handling** (explicitly state behavior)
- **Default behavior** (what happens if nothing matches)
- **Why this order** (explain non-obvious decisions)

**3. Expected Format**
- **Exact structure** (JSON schema, markdown format, etc.)
- **Required vs optional** fields
- **Sample with real data** (not Lorem Ipsum)
- **Error format** (what happens on failure)

---

### Good vs Bad Examples

#### ❌ BAD (Vague Logic):
```
"Categorize articles by checking if they're telecom-related"
```

Problems:
- How do you check?
- What defines "telecom-related"?
- What if ambiguous?
- Order of checking?

#### ✅ GOOD (Explicit Logic with Priority):
```
**Categorization Logic** (Priority Order):

**Priority 1: Source Metadata** (NEW - highest priority)
```python
if article.get('source_category') == 'telecom':
    → categorize as TELECOM
    → Skip keyword matching
    → Reason: Source specialization is stronger signal than keywords
```

**Priority 2: Keyword Matching** (existing logic)
```python
elif contains_any(article.text, TELECOM_KEYWORDS):
    → categorize as TELECOM
elif contains_any(article.text, GENERAL_KEYWORDS):
    → categorize as GENERAL
```

**Priority 3: Default**
```python
else:
    → categorize as UNCATEGORIZED
    → Log: "No category match for: {article.title}"
    → Do NOT include in report
```

**Why This Order:**
- Source category = editorial focus (strongest signal)
- Keywords alone unreliable ("mobile" could be mobile phones or mobile homes)
- Uncategorized better than miscategorized (false negatives > false positives)

**Edge Cases:**
1. Source has category but article is off-topic (e.g., hiring announcement)
   → Still use source category (rare, acceptable false positive)
   
2. Article matches both telecom AND general keywords
   → Telecom wins (priority order)
   
3. Source category missing in config
   → Fall back to keywords
   → Log warning: "Source {name} missing category metadata"

**Files to Modify:**
- `scripts/analyze/categorizer.py` lines 45-67 (add source category check)
- `config/sources.json` (add "category" field to each source)
```

---

#### ❌ BAD (No Sample Data):
```
"Add citations to the report"
```

Problems:
- Where do citations come from?
- What format?
- How are they linked?

#### ✅ GOOD (Complete Flow with Samples):
```
**Citation System** (3-Part Flow):

**Part 1: Number sources during collection**
```python
# In scripts/collect/collector.py
citations = {}
for i, article in enumerate(articles, 1):
    citations[f"ARTICLE_{i}"] = {
        "title": article["title"],
        "url": article["url"],
        "source": article["source"],
        "date": article["published"]
    }
# Save to: data/citations.json
```

**Sample Output (citations.json):**
```json
{
  "ARTICLE_1": {
    "title": "New Security Vulnerability Discovered",
    "url": "https://example.com/article1",
    "source": "TechNews",
    "date": "2026-04-10"
  },
  "ARTICLE_2": {...}
}
```

**Part 2: AI includes citations in analysis**
```python
# Prompt to GPT:
"For each claim, include inline citation using [ARTICLE_N] notation.
Example: 'Recent vulnerability affects 40% of systems [ARTICLE_1][ARTICLE_3]'"

# AI Output:
"The security landscape saw major developments [ARTICLE_1]. 
Companies are now required to patch within 48 hours [ARTICLE_2]."
```

**Part 3: Generate Sources section**
```python
# Extract used citations
used_citations = set(re.findall(r'\[ARTICLE_\d+\]', report_text))

# Build Sources section
for citation_key in sorted(used_citations):
    key = citation_key.strip('[]')  # "ARTICLE_1"
    info = citations[key]
    output += f"- {citation_key}: [{info['title']}]({info['url']}) - {info['source']} ({info['date']})\n"
```

**Expected Final Output:**
```markdown
Recent vulnerability affects systems [ARTICLE_1][ARTICLE_3].

## Sources

- [ARTICLE_1]: [New Security Vulnerability](https://example.com/article1) - TechNews (2026-04-10)
- [ARTICLE_3]: [Patch Requirements Updated](https://example.com/article3) - SecurityBlog (2026-04-09)
```

**Edge Cases:**
1. AI forgets citation → Log warning, include in Sources anyway with note "(mentioned but not cited)"
2. AI cites non-existent [ARTICLE_99] → Validation catches it, error: "Invalid citation"
3. No articles collected → Skip citations, report says "No sources this week"
```

---

## Layer 3: VALIDATION (How to Verify)

### Purpose
Define success objectively:
- **What** to test
- **How** to test it
- **What values** indicate success
- **What** indicates failure

### What to Include

**1. Acceptance Tests** (Given/When/Then)
- **Specific scenarios** with inputs
- **Expected outcomes** with numbers
- **Edge cases** explicitly tested
- **Failure conditions** defined

**2. Verification Commands**
- **Exact bash/python** commands to run
- **What output** confirms success
- **What to grep/count** to verify
- **Copy-pasteable** (no placeholders)

**3. Sample Test Data**
- **Actual test input** (not "sample data")
- **Expected output** for that input
- **Failure cases** to test error handling

---

### Good vs Bad Examples

#### ❌ BAD (Subjective):
```
"Test if the categorization works better"
```

Problems:
- What does "better" mean?
- How do you test?
- What's the threshold?

#### ✅ GOOD (Measurable Tests):
```
**Acceptance Tests:**

**Test 1: Source Category Priority**
```bash
# Given: Test data with 3 articles
# - Article A: source_category="telecom", text has no telecom keywords
# - Article B: source_category="general", text contains "mobile phone"
# - Article C: source_category missing, text contains "telecom fraud"

# Create test file:
cat > test_data.json << 'EOF'
{
  "articles": [
    {"id": "A", "source": "TelecomWeekly", "source_category": "telecom", 
     "text": "Company announces new CEO"},
    {"id": "B", "source": "TechNews", "source_category": "general",
     "text": "New mobile phone released"},
    {"id": "C", "source": "BlogPost", "text": "Telecom fraud on the rise"}
  ]
}
EOF

# When: Run categorization
python3 -c "
from scripts.analyze.categorizer import categorize
import json
with open('test_data.json') as f:
    articles = json.load(f)['articles']
result = categorize(articles)
print(f'Telecom: {len(result[\"telecom\"])}')
print(f'General: {len(result[\"general\"])}')
print(f'Telecom IDs: {[a[\"id\"] for a in result[\"telecom\"]]}')
"

# Then: Expect
# Telecom: 2 (Articles A and C)
# General: 1 (Article B)
# Telecom IDs: ['A', 'C']

# Verify priority: Article A has NO telecom keywords but still categorized as telecom
```

**Test 2: Empty Collection Handling**
```bash
# Given: No articles collected this week
echo '{"articles": []}' > test_empty.json

# When: Run full pipeline
python -m scripts.main --input test_empty.json

# Then: Verify graceful handling
# - Pipeline completes (exit code 0)
# - Report generated with message "No articles this week"
# - No Python errors/exceptions
# - Check: grep "No articles" data/reports/latest.md
```

**Test 3: Report Generation End-to-End**
```bash
# Given: Real data from last week
cp data/raw/2026-04-10.json test_real.json

# When: Generate report
python -m scripts.main

# Then: Verify
# 1. Report file exists
test -f data/reports/2026-04-13.md && echo "✓ Report created" || echo "✗ Report missing"

# 2. Contains Telecom section
grep -q "## Telecom Digest" data/reports/2026-04-13.md && echo "✓ Section present" || echo "✗ Section missing"

# 3. Section has content (not empty)
CONTENT=$(grep -A 20 "## Telecom Digest" data/reports/2026-04-13.md | wc -l)
[ $CONTENT -gt 5 ] && echo "✓ Has content ($CONTENT lines)" || echo "✗ Empty section"

# 4. All citations have sources
CITATIONS=$(grep -o '\[ARTICLE_[0-9]*\]' data/reports/2026-04-13.md | sort -u | wc -l)
SOURCES=$(grep "^- \[ARTICLE_" data/reports/2026-04-13.md | wc -l)
[ $CITATIONS -eq $SOURCES ] && echo "✓ Citations match sources" || echo "✗ Missing sources"
```

**Acceptance Criteria Checklist:**
- [ ] Test 1 passes: Source category takes priority over keywords
- [ ] Test 2 passes: Empty collection handled gracefully
- [ ] Test 3 passes: All 4 sub-checks succeed
- [ ] No regression: Existing general categorization still works
- [ ] Performance: Runs in < 3 minutes (same as before)
```

---

## Layer 4: CONSTRAINTS (What NOT to Change)

### Purpose
Protect existing functionality:
- **What** must remain unchanged
- **Why** it can't change
- **Dependencies** that would break
- **Cost/performance** limits

### What to Include

**1. Sacred Cows** (Do NOT Modify)
- **Config formats** that users edit manually
- **API contracts** other systems depend on
- **Database schemas** with production data
- **File paths** deployment scripts reference
- **Why each is sacred** (explain dependency)

**2. Dependencies**
- **Which files/modules** depend on this change
- **External systems** that integrate
- **Backward compatibility** requirements
- **Migration path** if breaking change needed

**3. Cost/Performance Limits**
- **API call limits** (daily/monthly quotas)
- **Token limits** (LLM context windows)
- **Response time** (user-facing timeouts)
- **Memory limits** (large file processing)
- **Why these limits** (cost, user experience, etc.)

---

### Good vs Bad Examples

#### ❌ BAD (No Constraints):
```
"Fix the categorization system"
```

Problems:
- Can I change the config format?
- Can I add database?
- Can I make API calls?
- What about existing reports?

#### ✅ GOOD (Clear Boundaries):
```
**Constraints:**

**DO NOT Change:**

1. **Config file structure** (`config/sources.json`)
   ```json
   {
     "sources": [
       {"name": "...", "url": "...", "category": "..."}
     ]
   }
   ```
   **Why:** Non-technical users edit this file manually
   **Can add:** New optional fields (e.g., "category")
   **Cannot:** Change required fields, nest structure deeper, change to YAML

2. **Report file paths** (`data/reports/YYYY-MM-DD.md`)
   **Why:** Email system expects this path pattern
   **Cannot:** Change directory, date format, or extension
   **Can change:** File contents, internal structure

3. **Citation format** (`[\[A1\]](#a1)`)
   **Why:** Markdown renderer in email client requires this exact format
   **Cannot:** Use different brackets, change anchor format
   **Can change:** Citation numbering scheme (A1/A2 vs ARTICLE_1/ARTICLE_2)

4. **Existing category names** ("telecom", "general")
   **Why:** Historical reports use these in URLs and analytics
   **Cannot:** Rename existing categories
   **Can add:** New categories (e.g., "security", "regulatory")

**Must Maintain:**

1. **Backward compatibility:**
   - Old reports (2026-04-01 onwards) must still render correctly
   - Don't break links in already-sent emails
   - New config format must be superset (old configs still work)

2. **Error handling:**
   - If source categorization fails, fall back to keywords (don't crash)
   - If no articles match, generate report saying "No articles" (don't skip report)
   - Log errors to `logs/categorization.log` for debugging

3. **Sync requirements:**
   - Article numbering in collector must match numbering in report generator
   - If you change one, change both (files: `collector.py`, `reporter.py`)
   - Document: "These files must stay in sync" in code comments

**Performance Limits:**

1. **Token budget:** 
   - Current: 8K tokens per run
   - Limit: 12K tokens (GPT-4 context window safety margin)
   - Adding source category check: +200 tokens (acceptable)
   - **Do NOT:** Send all articles to AI for categorization (would exceed limit)

2. **Execution time:**
   - Current: 2-3 minutes end-to-end
   - Limit: 5 minutes (GitHub Actions timeout)
   - Adding source check: +50ms (negligible)
   - **Do NOT:** Add network calls in categorization loop (would timeout)

3. **API calls:**
   - Current: 1 API call per run (AI analysis)
   - Limit: 100 calls/day (cost constraints)
   - **Do NOT:** Call external API for each article categorization
   - **OK:** Use local logic (keywords, source metadata)

**Cost Implications:**
- Current cost: $0.05-0.10 per run
- Monthly: $0.20-0.40 (4 runs/month)
- Adding source category: $0 additional (no new API calls)
- **Threshold:** Do not exceed $1/month without approval
```

---

## Red Flags: When PRD Will Cause Issues

### 🚩 Vague Problem Statement
❌ "Make the reports better"
✅ "Reports missing Telecom section due to monthly source publication cadence"

### 🚩 No Current State
❌ "Add citations to articles"
✅ "Current: Articles display without sources. File: `reporter.py` lines 45-67. Want: Inline [1] citations linking to Sources section at end."

### 🚩 Implicit Edge Cases
❌ "Parse JSON from LLM"
✅ "Parse JSON from LLM. Edge cases: (1) JSON wrapped in ```json fences, (2) Malformed JSON with missing bracket, (3) Empty response. Handle: Strip fences, try-catch with default empty dict, log errors."

### 🚩 Subjective Success Criteria
❌ "Fix the formatting"
✅ "Success: `grep '^\*\*[0-9]' report.md` shows sequential numbering (1, 2, 3) not all (1, 1, 1). Test with last week's data."

### 🚩 Missing Constraints
❌ "Switch from OpenAI to Claude"
✅ "Constraint: Keep OpenAI (already approved cost model). Cannot switch without finance approval. Can: Optimize prompts to reduce tokens."

### 🚩 No File Paths
❌ "Update the categorization logic"
✅ "Update categorization in `scripts/analyze/categorizer.py` lines 45-67. Also update tests in `tests/test_categorizer.py` lines 23-45."

### 🚩 No Test Commands
❌ "Make sure it works"
✅ "Test: `python -m pytest tests/test_categorizer.py::test_source_category_priority`. Expect: 3 tests pass. Verify: All use source_category before keywords."

---

## Pre-Submit Checklist

Before handing PRD to agent, verify:

### Context Layer
- [ ] Problem clearly stated with business impact
- [ ] Current state includes file paths and line numbers
- [ ] Code snippets provided for relevant sections (< 20 lines each)
- [ ] Domain knowledge explained (no industry jargon without definition)
- [ ] Sample input/output with real data (not placeholders)
- [ ] "Why it matters" section explains stakeholder impact

### Behavior Layer
- [ ] Data flow documented: Input → Processing → Output
- [ ] Decision logic has priority order (1, 2, 3...)
- [ ] Edge cases explicitly handled (at least 3 cases)
- [ ] Expected format with JSON schema or markdown example
- [ ] "Why" explained for non-obvious design choices
- [ ] File paths where changes needed

### Validation Layer
- [ ] At least 3 acceptance tests in Given/When/Then format
- [ ] Verification commands are copy-pasteable (no placeholders)
- [ ] Expected output includes actual values (numbers, not "success")
- [ ] Failure conditions explicitly defined
- [ ] Sample test data provided (can save to file and run)
- [ ] Tests cover: happy path, edge case, error handling

### Constraints Layer
- [ ] "Do NOT change" list with at least 3 items
- [ ] Each constraint explains WHY (dependencies, cost, etc.)
- [ ] Dependencies documented (which files affect each other)
- [ ] Performance limits specified (time, tokens, API calls, cost)
- [ ] Backward compatibility considered
- [ ] Sync requirements documented (if any)

### Meta Quality
- [ ] No ambiguous words ("better", "fix", "improve", "enhance")
- [ ] No assumptions about agent's domain knowledge
- [ ] Success is measurable with objective criteria
- [ ] Agent can execute without asking clarifying questions
- [ ] Estimated time to implement stated (if known)
- [ ] Links to related docs/PRDs (if dependencies exist)

---

## Common Patterns for AI-Friendly Specs

### Pattern 1: "Show, Don't Tell"
❌ "The output is wrong"
✅ "Current output: `{'status': 'ok'}`. Expected: `{'status': 'success', 'count': 5}`. Difference: Missing 'count' field."

### Pattern 2: "Priority Order for Decisions"
❌ "Check multiple conditions"
✅ "Priority: (1) Check cache, (2) If cache miss, call API, (3) If API fails, use default. Never call API if cache exists."

### Pattern 3: "Sample Data is Real Data"
❌ "Test with sample data"
✅ "Test data: Use `data/test_fixtures/articles_2026-04-10.json` (5 articles, 2 telecom, 3 general). Expected: Telecom count = 2."

### Pattern 4: "Files + Line Numbers"
❌ "Update the analyzer"
✅ "Update `scripts/analyze/analyzer.py` lines 67-89 (the `categorize()` function). Also update `tests/test_analyzer.py` lines 23-34."

### Pattern 5: "Edge Cases Are Explicit"
❌ "Handle errors"
✅ "Edge cases: (1) Empty input → return empty list, (2) Malformed JSON → log error, return default, (3) Missing field → use null, continue processing."

### Pattern 6: "Success is a Number"
❌ "Make sure performance is good"
✅ "Performance target: < 3 seconds end-to-end. Measure with `time python script.py`. Current: 2.8s. After change: must stay < 3s."

---

## Summary

**Agent-ready PRDs have 4 layers:**

1. **CONTEXT** - Why it matters, current state, domain knowledge
2. **BEHAVIOR** - Data flow, decision logic, edge cases
3. **VALIDATION** - Tests, commands, expected values
4. **CONSTRAINTS** - What NOT to change, dependencies, limits

**Follow the golden rule:**
> "If the agent asks a clarifying question, the PRD was incomplete."

**Use the checklist** before submitting to catch common gaps.

**Prefer concrete over abstract:**
- File paths over "the code"
- Numbers over "better"
- Commands over "test it"
- Examples over descriptions

---

## Next Steps

1. **Read the example:** See [`PM_RADAR_EXAMPLE_PRD.md`](PM_RADAR_EXAMPLE_PRD.md) for a complete worked example applying this framework
2. **Use the template:** Copy structure from example for your own PRDs
3. **Iterate:** Each project teaches new patterns—update framework as you learn

---

**Version:** 1.0  
**Date:** 2026-04-13  
**Status:** Living framework - update as patterns emerge
