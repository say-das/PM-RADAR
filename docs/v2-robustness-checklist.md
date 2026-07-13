# V2 Report Generation Robustness Checklist

## Current Vulnerabilities & Solutions

### 1. JSON Parsing Fragility

**Problem:** LLM responses can vary in format (with/without markdown fences, different JSON structures)

**Solutions:**
- ✅ Already implemented: Markdown fence stripping in `top_items.py`, `executive_summary.py`, `reddit_community.py`
- ⚠️ TODO: Extract to shared utility function to ensure consistency

**Action Items:**
```python
# Create: core/reporters/utils.py
def safe_parse_json(data: str, section_name: str = "unknown") -> Any:
    """
    Safely parse JSON from LLM response, handling markdown fences and format variations.
    
    Returns:
        Parsed JSON object/array, or None if parsing fails
    """
    if not data or not isinstance(data, str):
        return None
    
    try:
        # Strip markdown code fences
        clean_data = data.strip()
        if clean_data.startswith('```json'):
            clean_data = clean_data[7:]
        if clean_data.startswith('```'):
            clean_data = clean_data[3:]
        if clean_data.endswith('```'):
            clean_data = clean_data[:-3]
        clean_data = clean_data.strip()
        
        return json.loads(clean_data)
    except json.JSONDecodeError as e:
        print(f"    ⚠️ JSON parse error in {section_name}: {e}")
        return None
    except Exception as e:
        print(f"    ⚠️ Unexpected error parsing {section_name}: {e}")
        return None
```

### 2. Data Format Variations (v1 vs v2)

**Problem:** Analysis data structure differs between v1 (object with executive_summary) and v2 (array)

**Current Handling:**
- ✅ `top_items.py` checks for both list and object formats
- ✅ Tries multiple keys: `top_threats`, `threats`, `items`, `trends`, `top_trends`

**TODO: Add version detection**
```python
def detect_analysis_version(analysis_data: Dict) -> str:
    """Detect if analysis data is v1 or v2 format"""
    telecom = analysis_data.get("telecom_fraud_summary", "")
    if isinstance(telecom, str):
        try:
            data = json.loads(telecom)
            if isinstance(data, dict) and "executive_summary" in data:
                return "v1"
            elif isinstance(data, list):
                return "v2"
        except:
            pass
    return "unknown"
```

### 3. Citation Format Inconsistencies

**Problem:** Different analysis runs produce different citation formats ([ARTICLE_1] vs [A1])

**Solution:**
- ✅ Already implemented: `_convert_citations()` in report_generator.py
- ✅ Handles: ARTICLE_#, REDDIT_#, COMP_#
- ✅ Converts to: [\[A#\]](#a#), [\[R#\]](#r#), [\[C#\]](#c#)

**TODO: Add validation**
```python
def validate_citations(report_content: str, analysis_data: Dict) -> Dict[str, Any]:
    """
    Validate that all citations in report match available articles.
    
    Returns:
        {
            "valid": bool,
            "issues": [list of citation mismatches],
            "stats": {article_count, citation_count, broken_links}
        }
    """
    # Check for broken citation links
    # Verify citation IDs don't exceed article count
    # Warn about unreferenced articles
```

### 4. Missing Data Handling

**Problem:** Sections fail silently or show generic errors when data is missing

**Current State:**
- ✅ Most sections return empty string if no data
- ⚠️ Some show "*No items identified this period.*"

**TODO: Standardize empty state handling**
```python
class BaseSection(ABC):
    def get_empty_message(self) -> str:
        """Override in subclasses to customize empty state message"""
        return ""  # Default: skip section entirely
    
    def should_render(self) -> bool:
        """Check if section has required data before rendering"""
        return True  # Override in subclasses
```

### 5. Section Rendering Errors

**Problem:** If one section fails, it shouldn't break the entire report

**Current State:**
- ✅ report_generator.py has try/catch around section rendering
- ✅ Shows "*Error rendering section*" placeholder

**TODO: Improve error reporting**
```python
# Add structured error tracking
self.rendering_errors = []

try:
    section_markdown = section.render()
except Exception as e:
    error_detail = {
        "section": section_type,
        "error": str(e),
        "traceback": traceback.format_exc()
    }
    self.rendering_errors.append(error_detail)
    
    # Log to file for debugging
    with open(f"data/logs/render-errors-{date}.json", "a") as f:
        json.dump(error_detail, f)
        f.write("\n")
```

### 6. LLM Response Quality Variations

**Problem:** LLM might return incomplete, malformed, or unexpected response formats

**TODO: Add response validation**
```python
# Create: core/analyzers/validators.py

def validate_threat_analysis(data: Any) -> Tuple[bool, List[str]]:
    """
    Validate that threat analysis response has required structure.
    
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    if not isinstance(data, list):
        issues.append("Expected array of threats")
        return False, issues
    
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            issues.append(f"Threat {i}: Not a dict")
            continue
        
        if "title" not in item:
            issues.append(f"Threat {i}: Missing title")
        if "description" not in item:
            issues.append(f"Threat {i}: Missing description")
        if "citation_ids" not in item:
            issues.append(f"Threat {i}: Missing citations")
    
    return len(issues) == 0, issues
```

## Testing Strategy

### Unit Tests Needed

```python
# tests/core/reporters/test_robustness.py

class TestReportRobustness:
    """Test report generation against various edge cases"""
    
    def test_empty_analysis_data(self):
        """Report should handle completely empty analysis"""
        report = generate({})
        assert "## Executive Summary" in report
        assert report_is_valid_markdown(report)
    
    def test_malformed_json_in_summary(self):
        """Should gracefully handle unparseable JSON"""
        analysis = {"telecom_fraud_summary": "```json\n{invalid json"}
        report = generate(analysis)
        assert report is not None
    
    def test_missing_citations(self):
        """Should handle articles with no citation_ids"""
        analysis = {
            "telecom_fraud_summary": json.dumps([
                {"title": "Test", "description": "Test"}  # No citations
            ])
        }
        report = generate(analysis)
        assert "Test" in report
    
    def test_citation_id_out_of_range(self):
        """Should handle citation IDs that exceed article count"""
        analysis = {
            "telecom_fraud_summary": json.dumps([
                {"title": "Test", "description": "Test", "citation_ids": [999]}
            ]),
            "filtered_articles": []  # No articles!
        }
        report = generate(analysis)
        # Should not crash
    
    def test_v1_format_compatibility(self):
        """Should handle v1 analysis format"""
        analysis = {
            "telecom_fraud_summary": json.dumps({
                "executive_summary": "Test summary",
                "top_trends": [...]
            })
        }
        report = generate(analysis)
        assert "Test summary" in report or len(report) > 0
    
    def test_mixed_citation_formats(self):
        """Should handle both [ARTICLE_1] and [A1] formats"""
        content = "Test [ARTICLE_1] and [A2]"
        converted = convert_citations(content)
        assert "[\[A1\]](#a1)" in converted
        assert "[\[A2\]](#a2)" in converted
```

### Integration Tests

```python
# tests/integration/test_end_to_end.py

def test_fraud_topic_full_pipeline():
    """Test complete pipeline with fraud topic"""
    # Use fixture data from data/test-fixtures/
    result = run_pipeline("fraud", use_fixture=True)
    assert result["success"]
    assert os.path.exists(result["report_path"])

def test_multiple_topics():
    """Ensure report generation works for all configured topics"""
    topics = ["fraud", "compliance", "product_intel"]
    for topic in topics:
        result = run_pipeline(topic, use_fixture=True)
        assert result["success"], f"Failed for topic: {topic}"
```

### Data Fixtures

Create test fixtures that cover edge cases:

```
data/test-fixtures/
├── fraud/
│   ├── empty-analysis.json          # All fields empty/null
│   ├── v1-format.json               # Legacy v1 structure
│   ├── v2-format.json               # New v2 structure
│   ├── no-citations.json            # Analysis with no citation_ids
│   ├── malformed-json.json          # JSON with markdown fences
│   └── missing-fields.json          # Some required fields missing
```

## Monitoring & Alerts

### Add Health Checks

```python
# Create: core/reporters/health_check.py

def check_report_health(report: str, analysis_data: Dict) -> Dict[str, Any]:
    """
    Run health checks on generated report.
    
    Returns health status with warnings/errors
    """
    health = {
        "status": "ok",
        "warnings": [],
        "errors": [],
        "metrics": {}
    }
    
    # Check 1: Minimum report length
    if len(report) < 500:
        health["warnings"].append("Report suspiciously short")
    
    # Check 2: Verify sections present
    required_sections = ["Executive Summary", "Sources"]
    for section in required_sections:
        if section not in report:
            health["errors"].append(f"Missing section: {section}")
    
    # Check 3: Check for error messages in report
    if "*Error rendering" in report:
        health["errors"].append("Section rendering failed")
    
    # Check 4: Citation consistency
    article_count = len(analysis_data.get("filtered_articles", []))
    citation_count = len(re.findall(r'\[\[A\d+\]\]', report))
    
    if citation_count > article_count:
        health["errors"].append(
            f"Citation count ({citation_count}) exceeds articles ({article_count})"
        )
    
    health["metrics"] = {
        "length": len(report),
        "section_count": report.count("##"),
        "citation_count": citation_count,
        "article_count": article_count
    }
    
    if health["errors"]:
        health["status"] = "error"
    elif health["warnings"]:
        health["status"] = "warning"
    
    return health
```

### Logging Improvements

```python
# Add to core/pipeline.py

import logging
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    filename=f'data/logs/pipeline-{datetime.now():%Y%m%d}.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log key metrics
logger.info("Report generated", extra={
    "topic": self.topic_id,
    "report_length": len(report),
    "sections": section_count,
    "citations": citation_count,
    "duration_ms": duration
})
```

## Schema Validation

### Add JSON Schema for Analysis Data

```python
# Create: core/schemas/analysis_schema.json

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["analyzed_at", "filtered_articles"],
  "properties": {
    "analyzed_at": {"type": "string", "format": "date-time"},
    "telecom_fraud_summary": {"type": "string"},
    "general_fraud_summary": {"type": "string"},
    "competitive_intelligence_summary": {"type": ["string", "null"]},
    "reddit_community_summary": {"type": ["string", "null"]},
    "filtered_articles": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["title", "source", "url"],
        "properties": {
          "title": {"type": "string"},
          "source": {"type": "string"},
          "url": {"type": "string", "format": "uri"},
          "published": {"type": "string"},
          "summary": {"type": "string"}
        }
      }
    },
    "categorized_counts": {
      "type": "object",
      "properties": {
        "telecom": {"type": "integer", "minimum": 0},
        "general": {"type": "integer", "minimum": 0},
        "competitive": {"type": "integer", "minimum": 0}
      }
    }
  }
}
```

### Validate Before Report Generation

```python
from jsonschema import validate, ValidationError

def validate_analysis_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """Validate analysis data against schema before generating report"""
    try:
        with open('core/schemas/analysis_schema.json') as f:
            schema = json.load(f)
        
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)
```

## Pre-Deployment Checklist

Before running for new topics:

- [ ] Generate test report with fixture data
- [ ] Run health checks on generated report
- [ ] Verify all sections render
- [ ] Check citation links work
- [ ] Test HTML conversion
- [ ] Validate email delivery
- [ ] Review error logs
- [ ] Compare with v1 output (if migrating)

## Emergency Rollback Plan

If v2 reports break in production:

1. **Immediate:** Switch back to v1 pipeline
   ```bash
   # Set feature flag in topic.yaml
   feature_flag_v2: false
   ```

2. **Debug:** Check logs
   ```bash
   tail -100 data/logs/pipeline-*.log
   cat data/logs/render-errors-*.json
   ```

3. **Reproduce:** Use latest analysis file
   ```bash
   python3 scripts/run_v2_pipeline.py fraud --skip-collection --skip-analysis
   ```

4. **Fix & Test:** Run full test suite
   ```bash
   pytest tests/core/reporters/test_robustness.py -v
   ```

## Gradual Rollout Strategy

To minimize risk when deploying to new topics:

1. **Week 1:** Run v2 in parallel (don't send), compare with v1
2. **Week 2:** Send v2 to test recipients only
3. **Week 3:** A/B test (50% v1, 50% v2)
4. **Week 4:** Full v2 rollout if metrics good
5. **Week 5+:** Deprecate v1

## Metrics to Monitor

Track these metrics to detect issues early:

- Report generation success rate (should be 100%)
- Average report length (sudden drop = problem)
- Section count (should be consistent)
- Citation count vs article count ratio
- Error log entries
- Email delivery rate
- User feedback/complaints

## Summary

**Key Principles for Robustness:**

1. **Fail Gracefully** - Never crash, always generate *something*
2. **Validate Early** - Check data format before processing
3. **Log Everything** - Make debugging easy
4. **Test Edge Cases** - Empty data, malformed JSON, missing fields
5. **Monitor Metrics** - Detect degradation before users complain
6. **Plan Rollback** - Always have escape hatch to v1

**Next Actions:**

Priority 1 (This Sprint):
- [ ] Extract `safe_parse_json()` utility
- [ ] Add health checks to pipeline
- [ ] Create test fixtures for edge cases
- [ ] Write robustness unit tests

Priority 2 (Next Sprint):
- [ ] Add JSON schema validation
- [ ] Improve error logging
- [ ] Set up monitoring dashboard
- [ ] Document rollback procedures
