# PM Radar v2 - Sub-Project 2: Analyzers & LLM Providers

**Goal:** Refactor content analysis to use pluggable LLM providers with prompts from YAML

**Duration:** ~1 week (estimated)

**Branch:** `feature/v2-multi-topic-platform` (continue from Sub-Project 1)

---

## Success Criteria

- ✅ BaseAnalyzer abstract interface
- ✅ LLM provider abstraction (OpenAI + Anthropic support)
- ✅ ContentSummarizer loads prompts from YAML
- ✅ Analysis output matches v1 quality
- ✅ Can switch LLM providers via topic config

---

## Architecture

```
core/analyzers/
├── base.py              # BaseAnalyzer interface
├── llm_providers.py     # LLMProvider abstraction
└── summarizer.py        # ContentSummarizer (refactored from v1)
```

**LLM Provider Abstraction:**
- Unified interface: `generate(prompt, schema)` → structured output
- OpenAI adapter: GPT-4o with response_format json_object
- Anthropic adapter: Claude Sonnet with JSON parsing
- Provider selected via `topic.yaml`: `llm.provider`

**Prompt Loading:**
- Load from `config/topics/{topic}/prompts.yaml`
- Categories: categorization, analysis.*, executive_summary, competitive_intel
- String interpolation for dynamic content

---

## Task Breakdown

### Task 1: LLM Provider Abstraction
**Goal:** Create unified LLM interface supporting OpenAI and Anthropic

**Files:**
- `core/analyzers/llm_providers.py`
- `tests/core/analyzers/test_llm_providers.py`

**Steps:**
1. Create BaseLLMProvider abstract class
2. Implement OpenAIProvider (GPT-4o)
3. Implement AnthropicProvider (Claude Sonnet)
4. Add provider factory function
5. Test both providers with sample prompts

---

### Task 2: BaseAnalyzer Interface
**Goal:** Define analyzer base class with prompt loading

**Files:**
- `core/analyzers/base.py`
- `tests/core/analyzers/test_base.py`

**Steps:**
1. Create BaseAnalyzer abstract class
2. Add prompt loading from YAML
3. Add LLM provider initialization
4. Add abstract `analyze()` method
5. Test prompt loading

---

### Task 3: ContentSummarizer Refactor
**Goal:** Migrate v1 summarizer to v2 architecture

**Files:**
- `core/analyzers/summarizer.py` (refactored from scripts/analyze/summarizer.py)
- `tests/core/analyzers/test_summarizer.py`

**Steps:**
1. Create ContentSummarizer class extending BaseAnalyzer
2. Migrate categorization logic (GPT scoring)
3. Migrate category analysis (telecom, general, regulatory)
4. Migrate competitive intelligence analysis
5. Migrate Reddit community analysis
6. Migrate changelog analysis
7. Test with fraud topic

---

### Task 4: Integration Test
**Goal:** Verify end-to-end analysis pipeline

**Files:**
- `tests/test_integration_analysis.py`

**Steps:**
1. Test full collect → analyze flow
2. Verify output structure matches v1
3. Verify analysis quality (manual spot-check)
4. Test LLM provider switching (OpenAI ↔ Anthropic)

---

## Implementation Notes

**Deferred to Sub-Project 3:**
- Report generation (that's Sub-Project 3's focus)
- Email delivery (Sub-Project 4)

**Reuse from v1:**
- Fallback data loading logic
- Date filtering (last 30 days for Reddit)
- Deduplication logic (already in prompts)

**New in v2:**
- Prompts externalized to YAML
- LLM provider swappable via config
- Structured output validation

---

## Estimated Timeline

- Task 1: LLM Providers - 2 hours
- Task 2: BaseAnalyzer - 1 hour
- Task 3: ContentSummarizer - 4 hours (complex, lots of logic)
- Task 4: Integration Test - 1 hour

**Total: ~8 hours (1 day focused work)**

---

## Next Steps After Completion

Once Sub-Project 2 complete:
- **Sub-Project 3:** Reporters & Section Library (~4 days)
- **Sub-Project 4:** Integration & Migration (~3 days)
- **v2.0 Launch:** Feature flag enabled, fraud topic on v2
