# Recent Changes

## SociaVault Integration (2026-04-03)

Switched from PRAW (Reddit API) to SociaVault for Reddit data collection.

### What Changed:

**✅ Updated Files:**
- `scripts/collect/reddit_collector.py` - Now uses SociaVault API
- `.env.example` - Replaced Reddit credentials with SociaVault API key
- `requirements.txt` - Removed `praw`, kept `requests`
- `docs/setup-guide.md` - Updated setup instructions
- `.github/workflows/weekly-collection.yml` - Updated secrets

### Why SociaVault?

- **Simpler authentication**: Single API key vs OAuth credentials
- **No rate limit complexity**: Managed by SociaVault
- **Cleaner API**: Purpose-built for social data scraping
- **Better for automation**: More reliable for GitHub Actions

### API Key Required:

```bash
# In .env file
SOCIAVAULT_API_KEY=sk_live_your_key_here
```

Get your key from: https://sociavault.com

### Code Changes:

**Before (PRAW):**
```python
reddit = praw.Reddit(
    client_id=self.client_id,
    client_secret=self.client_secret,
    user_agent=self.user_agent
)
```

**After (SociaVault):**
```python
response = requests.get(
    'https://api.sociavault.com/v1/scrape/reddit/search',
    headers={'X-API-Key': self.api_key},
    params={'query': query, 'timeframe': timeframe}
)
```

### Testing:

```bash
# Set API key in .env
SOCIAVAULT_API_KEY=sk_live_...

# Test collector
python -m scripts.collect.reddit_collector
```

Expected output:
```
Connecting to SociaVault API...
Searching Reddit via SociaVault: 'Twilio SMS pumping OR telecom fraud'
  ✓ Found 15 posts
```

### Note:

The SociaVault response format may need adjustment based on their actual API response structure. The collector includes mapping logic to convert their format to our internal schema.
