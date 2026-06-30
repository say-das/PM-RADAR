# SocialCrawl API Integration - Findings & Implementation Guide

**Date:** 2026-06-30  
**API Version:** v1  
**Replaces:** SociaVault API (expired)

---

## Executive Summary

SocialCrawl API successfully tested and validated for PM Radar v2 Reddit integration. Key difference from SociaVault: searches **all of Reddit** by default, requires client-side filtering to specific subreddits.

**Status:** ✅ Ready for implementation  
**Credits Available:** 97 remaining  
**Cost:** 1 credit per search query

---

## API Endpoints

### ✅ Subreddit-Specific Search (RECOMMENDED)
```bash
https://www.socialcrawl.dev/v1/reddit/subreddit/search
```
**Use this for PM Radar** - searches within a specific subreddit, just like SociaVault.

### Global Reddit Search
```bash
https://www.socialcrawl.dev/v1/reddit/search
```
Searches all of Reddit - not recommended for our use case (requires client-side filtering).

### Authentication

```python
headers = {
    "x-api-key": os.getenv("SOCIALCRAWL_API_KEY"),
    "Cache-Control": "no-cache",
    "Idempotency-Key": f"pmradar-{uuid.uuid4()}"  # Optional but recommended
}
```

### Request Parameters

```python
params = {
    "subreddit": "twilio",                  # Target subreddit (no r/ prefix)
    "query": "fraud OR scam OR security",   # Boolean OR supported
    "sort": "relevance",                    # or "new", "top"
    "timeframe": "week",                    # or "day", "month", "year", "all"
    "cursor": ""                            # For pagination (empty for first page)
}
```

### Response Structure

```json
{
  "success": true,
  "platform": "reddit",
  "endpoint": "/v1/reddit/search",
  "credits_used": 1,
  "credits_remaining": 97,
  "cached": false,
  "request_id": "...",
  "data": {
    "items": [
      {
        "post": {
          "id": "1ui92i8",
          "url": null,
          "content": {
            "text": "Post content here...",
            "media_urls": null,
            "thumbnail_url": null,
            "duration_seconds": null
          },
          "author": {
            "username": "example_user",
            "display_name": "t2_xxxxx",
            "avatar_url": null,
            "verified": null
          },
          "engagement": {
            "views": null,
            "likes": 15,
            "comments": 8,
            "shares": null,
            "saves": null
          },
          "flags": {
            "nsfw": null,
            "spoiler": null,
            "pinned": null,
            "deleted": false
          },
          "published_at": 1782681448,
          "ext": {
            "subreddit": "twilio"
          }
        },
        "computed": {
          "engagement_rate": null,
          "language": "en",
          "content_category": "tech",
          "estimated_reach": null
        }
      }
    ]
  }
}
```

---

## Key Differences from SociaVault

| Feature | SociaVault | SocialCrawl | Impact |
|---------|------------|-------------|--------|
| **Subreddit filtering** | Per-subreddit API calls | ✅ Same - per-subreddit endpoint | No change needed |
| **Post URL** | Included | `null` (must construct) | Generate from `id` + `subreddit` |
| **Comments** | Included | Not available | Need separate Reddit API call |
| **Timestamp format** | ISO string | Unix epoch | Convert to ISO |
| **Response structure** | Flat | Nested `data.items[].post` | Update parser |
| **Auth header** | `X-API-Key` | `x-api-key` | Update header name |
| **Endpoint** | `/subreddit/search` | ✅ Same - `/reddit/subreddit/search` | Update base URL only |

---

## Implementation Changes Required

### 1. ~~Client-Side Subreddit Filtering~~ ✅ NOT NEEDED

**Update:** SocialCrawl has `/v1/reddit/subreddit/search` endpoint that works per-subreddit (just like SociaVault). No client-side filtering needed!

```python
def collect(self):
    all_posts = []
    
    for subreddit in self.config["subreddits"]:
        # One API call per subreddit
        response = self._api_call(subreddit=subreddit, query="fraud OR scam")
        posts = response["data"]["items"]
        all_posts.extend(posts)
    
    return all_posts
```

### 2. Construct Post URLs

```python
def _build_post_url(self, post_data):
    """Generate Reddit URL from post ID and subreddit"""
    post_id = post_data["id"]
    subreddit = post_data["ext"]["subreddit"]
    return f"https://reddit.com/r/{subreddit}/comments/{post_id}"
```

### 3. Fetch Comments Separately

SocialCrawl doesn't return comments. Use Reddit's public JSON API (same as v1):

```python
def _fetch_comments(self, post_url):
    """Fetch comments from Reddit's JSON API"""
    json_url = f"{post_url}.json"
    headers = {"User-Agent": "PMRadar/2.0"}
    response = requests.get(json_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        comments_data = data[1]["data"]["children"]
        return self._parse_comments(comments_data)
    
    return []
```

### 4. Response Mapping

Map SocialCrawl format to PM Radar internal format:

```python
def _map_to_internal_format(self, item):
    """Convert SocialCrawl response to internal format"""
    post = item["post"]
    
    return {
        "id": post["id"],
        "title": post["content"]["text"][:200],  # Use first 200 chars as title
        "selftext": post["content"]["text"],
        "author": post["author"]["username"],
        "subreddit": post["ext"]["subreddit"],
        "score": post["engagement"]["likes"],
        "num_comments": post["engagement"]["comments"],
        "created_utc": datetime.fromtimestamp(post["published_at"]).isoformat(),
        "url": self._build_post_url(post),
        "is_self": True,
        "upvote_ratio": None,  # Not provided by SocialCrawl
        "comments": []  # Populated separately if needed
    }
```

---

## Caching Strategy

**Recommended:** Same as v1 (24-hour cache)

```python
def should_use_cache(self):
    """Check if cached data is < 24 hours old"""
    if not self.cache_file.exists():
        return False
    
    cached_data = json.loads(self.cache_file.read_text())
    cached_time = datetime.fromisoformat(cached_data["cached_at"])
    age = datetime.now() - cached_time
    
    return age < timedelta(hours=24)
```

**Cost savings:** 
- Without cache: 1 credit per pipeline run × 52 weeks = 52 credits/year per topic
- With 24h cache: 1 credit per week (manual runs hit cache)

---

## Query Optimization

### For Fraud Topic (r/twilio focus)

**Current config:** `"fraud OR scam OR hacked OR breach OR compromise OR vulnerability OR attack OR phishing"`

**Problem:** Too broad, returns mostly non-Twilio posts (0 r/twilio in test)

**Optimized:** `"twilio AND (fraud OR scam OR security OR breach)"`

**Result:** More likely to hit r/twilio posts, reduce wasted credits

### Multi-Query Strategy

Instead of one broad query, make multiple focused queries:

```python
queries = [
    "twilio fraud",           # Twilio-specific fraud
    "twilio security breach", # Security incidents
    "twilio scam",           # Scam reports
]

all_posts = []
for query in queries:
    posts = self._api_call(query=query)
    all_posts.extend(posts)

# Deduplicate by post ID
unique_posts = {post["id"]: post for post in all_posts}.values()
```

**Trade-off:** Uses more credits (3 queries = 3 credits) but higher quality results.

---

## Error Handling

### Timeout Errors

SocialCrawl occasionally times out (observed during testing). Implement retry with exponential backoff:

```python
def _api_call_with_retry(self, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(wait_time)
            else:
                raise
```

### Rate Limiting

Monitor `credits_remaining` in response:

```python
def _check_credits(self, response_data):
    remaining = response_data.get("credits_remaining", 0)
    
    if remaining < 10:
        print(f"⚠️  Low credits: {remaining} remaining")
    
    if remaining == 0:
        raise ValueError("SocialCrawl API credits exhausted")
```

---

## Test Results

### Test 1: Fraud Keywords (All Reddit)

**Query:** `"fraud OR scam OR hacked OR breach OR compromise OR vulnerability OR attack OR phishing"`

**Results:**
- 7 posts found
- Subreddits: r/EmailSecurity, r/computerviruses, r/cybersecurity_help, r/CryptoScams, r/cybersecurity, r/pwnhub
- **0 posts from r/twilio**

**Conclusion:** Need more specific queries for Twilio focus.

### Test 2: API Performance

- ✅ Response time: <2 seconds (when not timing out)
- ✅ Credits system working
- ⚠️ Occasional timeouts (1 in 3 requests during test session)

---

## Migration Checklist

- [x] Test SocialCrawl API endpoint
- [x] Validate authentication method
- [x] Document response structure
- [x] Identify differences from SociaVault
- [ ] Implement client-side subreddit filtering
- [ ] Implement post URL construction
- [ ] Implement comment fetching (Reddit JSON API)
- [ ] Implement response mapping
- [ ] Add retry logic for timeouts
- [ ] Optimize queries for better targeting
- [ ] Update caching logic for new structure
- [ ] Test end-to-end with fraud topic
- [ ] Validate credit usage monitoring

---

## Code Example: Complete Collector

```python
class SocialCrawlRedditCollector(BaseCollector):
    """Reddit collector using SocialCrawl API"""
    
    def __init__(self, config: dict, api_key: str):
        self.config = config
        self.api_key = api_key
        self.base_url = "https://www.socialcrawl.dev/v1/reddit/search"
    
    def collect(self) -> List[dict]:
        """Collect Reddit posts filtered to configured subreddits"""
        
        # Check cache first (24h TTL)
        if self.should_use_cache():
            return self._load_from_cache()
        
        all_posts = []
        
        for query_config in self.config["queries"]:
            keywords = query_config["keywords"]
            
            # Build focused query (include "twilio" for better targeting)
            base_terms = ["twilio"] if "twilio" in self.config["subreddits"] else []
            query = " AND ".join(base_terms) if base_terms else ""
            if query:
                query += " AND "
            query += "(" + " OR ".join(keywords) + ")"
            
            # Make API call
            response = self._api_call_with_retry(
                query=query,
                timeframe=query_config["timeframe"],
                sort="relevance"
            )
            
            # Extract posts
            items = response["data"]["items"]
            
            # Filter to configured subreddits
            filtered = [
                item for item in items
                if item["post"]["ext"]["subreddit"] in self.config["subreddits"]
            ]
            
            # Map to internal format
            posts = [self._map_to_internal_format(item) for item in filtered]
            
            all_posts.extend(posts)
        
        # Deduplicate
        unique_posts = {post["id"]: post for post in all_posts}.values()
        posts_list = list(unique_posts)
        
        # Fetch comments if enabled
        if self.config.get("fetch_comments"):
            for post in posts_list:
                if self._should_fetch_comments(post):
                    post["comments"] = self._fetch_comments(post["url"])
        
        # Save to cache
        self._save_to_cache(posts_list)
        
        return posts_list
    
    def _api_call_with_retry(self, query: str, timeframe: str, sort: str, max_retries: int = 3):
        """Make API call with retry logic"""
        headers = {
            "x-api-key": self.api_key,
            "Cache-Control": "no-cache",
            "Idempotency-Key": f"pmradar-{uuid.uuid4()}"
        }
        
        params = {
            "query": query,
            "sort": sort,
            "timeframe": timeframe,
            "trim": "true"
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self._check_credits(data)
                    return data
                else:
                    raise ValueError(f"API error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"  → Timeout, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
```

---

## Recommendations

1. **Query Strategy:** Use "twilio AND (fraud OR scam)" instead of broad OR queries
2. **Cache Aggressively:** 24-hour cache to minimize credit usage
3. **Monitor Credits:** Alert when < 10 credits remaining
4. **Retry Logic:** Implement exponential backoff for timeouts
5. **Fallback:** If SocialCrawl fails, fall back to Reddit's search API or skip Reddit data

---

## Next Steps

1. Update design spec with SocialCrawl integration details
2. Implement RedditCollector with client-side filtering
3. Test with fraud topic (expect low yield from r/twilio)
4. Consider expanding subreddit list (r/cybersecurity, r/fraud for better intel)
5. Monitor credit usage over first month

---

**Documentation Complete** ✅
