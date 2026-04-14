# Reddit Configuration Guide

How to customize Reddit search queries for PM Radar.

## Configuration File

**Location:** `config/reddit-config.json`

## Structure

```json
{
  "subreddits": ["telecom", "fraud", "SaaS", "Twilio"],
  "queries": [
    {
      "name": "Telecom Fraud",
      "keywords": ["telecom fraud", "SMS pumping", "IRSF", "IPRN"],
      "timeframe": "week",
      "limit": 50
    }
  ],
  "user_agent": "TwilioProductResearch/1.0"
}
```

---

## Subreddits

**Purpose:** Target specific Reddit communities

**Format:** Array of subreddit names (without "r/" prefix)

**Example:**
```json
"subreddits": ["telecom", "fraud", "SaaS", "Twilio"]
```

**How it works:**
- All queries search across these subreddits
- Reddit combines them: r/telecom+fraud+SaaS+Twilio
- Use `["all"]` to search all of Reddit (not recommended - too noisy)

**Common subreddits by topic:**

**Telecom/Communications:**
- `telecom` - Telecom industry discussions
- `voip` - VoIP technology
- `sms` - SMS-specific topics

**Security/Fraud:**
- `fraud` - Fraud discussions
- `netsec` - Network security
- `cybersecurity` - General security

**Business:**
- `SaaS` - SaaS products and industry
- `entrepreneur` - Entrepreneurs and startups
- `sales` - Sales discussions

**Competitors/Products:**
- `Twilio` - Twilio-specific
- `aws` - AWS discussions
- `vonage` - Vonage (competitor)

---

## Queries

**Purpose:** Define search terms grouped by theme

Each query searches for ANY of its keywords (OR logic) across ALL subreddits.

### Query Structure

```json
{
  "name": "Query Name",
  "keywords": ["term1", "term2", "term3"],
  "timeframe": "week",
  "limit": 50
}
```

**Fields:**

- **name** (string): Label for this query group (for reporting)
- **keywords** (array): Search terms - posts matching ANY keyword are returned
- **timeframe** (string): How far back to search
  - `"day"` - Last 24 hours
  - `"week"` - Last 7 days (recommended)
  - `"month"` - Last 30 days
  - `"year"` - Last 365 days
  - `"all"` - All time
- **limit** (number): Max posts to return per query (1-100)

---

## Example Configurations

### Current Configuration (Fraud Focus)

```json
{
  "subreddits": ["telecom", "fraud", "SaaS", "Twilio"],
  "queries": [
    {
      "name": "Telecom Fraud",
      "keywords": ["telecom fraud", "SMS pumping", "IRSF", "IPRN"],
      "timeframe": "week",
      "limit": 50
    },
    {
      "name": "Security Threats",
      "keywords": ["phishing", "account takeover", "artificially inflated traffic"],
      "timeframe": "week",
      "limit": 50
    }
  ]
}
```

**What this does:**
- Searches r/telecom, r/fraud, r/SaaS, r/Twilio
- Two query groups:
  1. Telecom Fraud terms (4 keywords)
  2. Security Threats (3 keywords)
- Returns up to 50 posts per query group (100 total max)
- Only posts from last 7 days

---

### Alternative: Competitor Monitoring

```json
{
  "subreddits": ["SaaS", "entrepreneur", "telecom"],
  "queries": [
    {
      "name": "Twilio Mentions",
      "keywords": ["Twilio", "Twilio SMS", "Twilio messaging"],
      "timeframe": "week",
      "limit": 30
    },
    {
      "name": "Competitor Mentions",
      "keywords": ["Vonage", "Sinch", "MessageBird", "Bandwidth"],
      "timeframe": "week",
      "limit": 30
    }
  ]
}
```

**Use case:** Monitor what people say about you vs competitors

---

### Alternative: Customer Pain Points

```json
{
  "subreddits": ["SaaS", "programming", "webdev"],
  "queries": [
    {
      "name": "SMS Pain Points",
      "keywords": ["SMS API issues", "SMS delivery problems", "SMS integration"],
      "timeframe": "month",
      "limit": 50
    },
    {
      "name": "Pricing Complaints",
      "keywords": ["SMS pricing expensive", "Twilio cost", "messaging API cost"],
      "timeframe": "month",
      "limit": 30
    }
  ]
}
```

**Use case:** Find customer pain points and complaints

---

## Keyword Best Practices

### 1. Use Specific Phrases

**Good:**
```json
"keywords": ["SMS pumping attack", "telecom fraud detection"]
```

**Bad:**
```json
"keywords": ["SMS", "fraud"]  // Too broad, noisy results
```

### 2. Include Variations

**Good:**
```json
"keywords": ["account takeover", "account take over", "ATO attack"]
```

Captures different spellings and abbreviations.

### 3. Mix Technical and Business Terms

**Good:**
```json
"keywords": ["IRSF", "international revenue share fraud", "premium rate fraud"]
```

Catches both technical discussions and business impact posts.

### 4. Use Acronyms AND Full Terms

**Good:**
```json
"keywords": ["IPRN", "International Premium Rate Number", "IRSF", "International Revenue Share Fraud"]
```

Different audiences use different terminology.

---

## Testing Your Configuration

### 1. Edit the config file

```bash
nano config/reddit-config.json
```

### 2. Clear the cache (force fresh API call)

```bash
rm data/raw/test-reddit-cache.json
```

### 3. Test the collector

```bash
source venv/bin/activate
python -m scripts.collect.reddit_collector
```

### 4. Review results

Check `data/raw/test-reddit-collection.json` for:
- Are results relevant?
- Too many/too few results?
- Missing expected topics?

### 5. Iterate

Adjust subreddits, keywords, or timeframe and retest.

---

## Troubleshooting

### Problem: No results

**Causes:**
- Keywords too specific
- Subreddits don't discuss these topics
- Timeframe too short

**Solutions:**
- Try broader keywords
- Add more subreddits
- Extend timeframe to "month"

---

### Problem: Too many irrelevant results

**Causes:**
- Keywords too broad
- Wrong subreddits

**Solutions:**
- Use more specific phrases
- Remove noisy subreddits
- Add qualifying terms (e.g., "SMS fraud" not just "fraud")

---

### Problem: Missing important posts

**Causes:**
- Keywords don't match how users write
- Missing key subreddits

**Solutions:**
- Search Reddit manually to see how people discuss the topic
- Add common misspellings and variations
- Ask: "What would someone actually type?"

---

## Tips

1. **Start narrow, then broaden**: Easier to add keywords than filter noise
2. **Monitor one topic first**: Perfect one query before adding more
3. **Check weekly**: Topics evolve, update keywords monthly
4. **Use the cache**: Test keyword changes without wasting API credits

---

## Current Fraud Keywords Explained

### Telecom Fraud Terms

- **"telecom fraud"** - General telecom fraud discussions
- **"SMS pumping"** - Traffic pumping attacks on SMS systems
- **"IRSF"** - International Revenue Share Fraud (premium rate scams)
- **"IPRN"** - International Premium Rate Numbers (used in fraud)

### Security Threats

- **"phishing"** - Social engineering attacks
- **"account takeover"** - ATO attacks, credential theft
- **"artificially inflated traffic"** - Traffic pumping, fake usage

All relevant to messaging fraud prevention and detection.

---

**Questions?** See main setup guide: `docs/setup-guide.md`
