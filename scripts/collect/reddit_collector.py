"""
Reddit Collector
Searches Reddit for relevant posts using SocialCrawl API.
"""

import json
import os
import requests
import hashlib
import time
import urllib3
from datetime import datetime, timedelta
from pathlib import Path

# Disable SSL warnings when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RedditCollector:
    def __init__(self, config_path="config/reddit-config.json"):
        """Initialize Reddit collector with configuration."""
        with open(config_path) as f:
            self.config = json.load(f)

        self.subreddits = self.config.get("subreddits", ["all"])
        self.queries = self.config["queries"]

        # Configuration for comment fetching
        self.fetch_comments = self.config.get("fetch_comments", True)
        self.comments_threshold = self.config.get("comments_threshold", {
            "min_score": 5,  # Fetch comments for posts with score >= 5
            "min_comments": 3  # Or posts with >= 3 comments
        })
        self.max_comments_per_post = self.config.get("max_comments_per_post", 10)

        # Check for SocialCrawl API key
        self.api_key = os.getenv("SOCIALCRAWL_API_KEY")

        if not self.api_key:
            raise ValueError(
                "SocialCrawl API key not found. "
                "Set SOCIALCRAWL_API_KEY in .env file"
            )

        # SocialCrawl endpoint: /v1/reddit/subreddit/search
        # Requires separate API call per subreddit (like SociaVault)
        self.base_url = "https://www.socialcrawl.dev/v1/reddit/subreddit/search"

    def _get_cache_key(self, query_config):
        """Generate a cache key based on query parameters."""
        # Create a hash of the query parameters
        cache_data = {
            "subreddits": self.subreddits,
            "keywords": query_config["keywords"],
            "timeframe": query_config["timeframe"]
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _get_cached_posts(self, cache_key):
        """Check if we have a valid cached response for this query."""
        cache_dir = Path("data/raw/.reddit_cache")
        cache_file = cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)

            # Check if cache is less than 24 hours old AND less than 7 days old
            cached_time = datetime.fromisoformat(cached["cached_at"])
            age = datetime.now() - cached_time

            # Reject cache older than 7 days (stale data protection)
            if age >= timedelta(days=7):
                print(f"  → Cache too old (age: {age.days} days), deleting")
                cache_file.unlink()
                return None

            if age < timedelta(hours=24):
                return cached["posts"]
            else:
                print(f"  → Cache expired (age: {age.total_seconds() / 3600:.1f} hours)")
                return None

        except Exception as e:
            print(f"  → Cache read error: {e}")
            return None

    def _save_to_cache(self, cache_key, posts, query_config):
        """Save posts to cache with metadata."""
        cache_dir = Path("data/raw/.reddit_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / f"{cache_key}.json"

        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "query_config": query_config,
            "subreddits": self.subreddits,
            "posts": posts
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def _fetch_comments_from_reddit(self, post_url):
        """
        Fetch top comments from a Reddit post using Reddit's public JSON API.

        Args:
            post_url: Reddit post URL (e.g., https://reddit.com/r/twilio/comments/abc123/...)

        Returns:
            List of comment dictionaries with author, body, score
        """
        try:
            # Add .json to URL to get JSON response
            if not post_url.endswith('.json'):
                json_url = post_url.rstrip('/') + '.json'
            else:
                json_url = post_url

            # Make request with user agent (Reddit requires this)
            headers = {
                'User-Agent': 'ProductResearch/1.0 (PM Radar Intelligence System)'
            }

            response = requests.get(json_url, headers=headers, timeout=10, verify=False)

            if response.status_code != 200:
                return []

            data = response.json()

            # Reddit JSON structure: [post_data, comments_data]
            if not isinstance(data, list) or len(data) < 2:
                return []

            comments_data = data[1].get('data', {}).get('children', [])

            comments = []
            for comment in comments_data[:self.max_comments_per_post]:
                comment_data = comment.get('data', {})

                # Skip deleted/removed comments and AutoModerator
                if comment_data.get('author') in ['[deleted]', 'AutoModerator']:
                    continue

                body = comment_data.get('body', '')
                if body and body != '[removed]':
                    comments.append({
                        'author': comment_data.get('author', '[deleted]'),
                        'body': body,
                        'score': comment_data.get('score', 0),
                        'created_utc': comment_data.get('created_at_iso', '')
                    })

            return comments

        except Exception as e:
            print(f" (comment fetch failed: {e})", end="")
            return []

    def collect(self):
        """
        Collect posts from Reddit based on configured queries.
        Uses cache if same query was made within last 24 hours.

        Returns:
            List of post dictionaries
        """
        posts = []

        print("Connecting to SociaVault API...")
        print(f"Target subreddits: r/{', r/'.join(self.subreddits)}\n")

        for query_config in self.queries:
            query_name = query_config.get("name", "Query")
            keywords = query_config["keywords"]
            timeframe = query_config["timeframe"]
            limit = query_config["limit"]

            # Construct search query from keywords (OR logic)
            search_query = " OR ".join(keywords)

            print(f"[{query_name}]")
            print(f"  Query: {search_query}")
            print(f"  Timeframe: {timeframe}, Limit: {limit}")

            # Check cache first
            cache_key = self._get_cache_key(query_config)
            cached_posts = self._get_cached_posts(cache_key)

            if cached_posts is not None:
                print(f"  ✓ Using cached response ({len(cached_posts)} posts)")
                posts.extend(cached_posts)
                continue

            # No valid cache, make API call
            # SocialCrawl API requires separate call per subreddit (same as SociaVault)
            print(f"  → Making API calls (one per subreddit)...")

            query_posts = []  # Collect posts from all subreddits for this query

            for subreddit in self.subreddits:
                print(f"    • r/{subreddit}...", end=" ")

                try:
                    # Build request parameters
                    # NOTE: subreddit format is "twilio" not "r/twilio"
                    import uuid

                    params = {
                        "subreddit": subreddit,
                        "query": search_query,
                        "timeframe": timeframe,
                        "sort": "relevance",
                        "cursor": ""  # For pagination (empty = first page)
                    }

                    # Make API request
                    response = requests.get(
                        self.base_url,
                        headers={
                            "x-api-key": self.api_key,  # lowercase for SocialCrawl
                            "Cache-Control": "no-cache",
                            "Idempotency-Key": f"pmradar-{uuid.uuid4()}"
                        },
                        params=params,
                        timeout=30
                    )

                    # Check response
                    if response.status_code != 200:
                        error_msg = response.text[:200] if response.text else "No error message"
                        print(f"✗ API error: {response.status_code} - {error_msg}")
                        continue

                    data = response.json()

                    # Parse SocialCrawl response structure
                    items = data.get("data", {}).get("items", [])

                    print(f"✓ {len(items)} posts")

                    # Map posts to our format
                    for item in items[:limit]:
                        # SocialCrawl response structure: nested post object
                        post = item.get("post", {})

                        # Extract data from nested structure
                        post_id = post.get("id", "")
                        subreddit_name = post.get("ext", {}).get("subreddit", subreddit)

                        # Construct Reddit URL (not provided by SocialCrawl)
                        post_url = f"https://reddit.com/r/{subreddit_name}/comments/{post_id}" if post_id else ""

                        # Extract engagement data
                        engagement = post.get("engagement", {})
                        score = engagement.get("likes", 0)
                        num_comments = engagement.get("comments", 0)

                        # Convert Unix timestamp to ISO format
                        published_at = post.get("published_at", 0)
                        created_utc = datetime.fromtimestamp(published_at).isoformat() if published_at else datetime.now().isoformat()

                        # Extract content
                        content = post.get("content", {})
                        text = content.get("text", "")

                        # Extract author
                        author_data = post.get("author", {})
                        author = author_data.get("username", "[deleted]")

                        post_data = {
                            "query": query_name,
                            "search_terms": search_query,
                            "subreddit": subreddit_name,
                            "title": text[:200] if text else "",  # Use first 200 chars as title
                            "author": author,
                            "score": score,
                            "upvote_ratio": None,  # Not provided by SocialCrawl
                            "num_comments": num_comments,
                            "created_utc": created_utc,
                            "url": post_url,
                            "selftext": text,  # Full text
                            "is_self": True,  # Assume all are self posts
                            "comments": []  # Will be populated if enabled
                        }

                        # Fetch comments if enabled and post meets threshold
                        if self.fetch_comments and post_url:
                            meets_score = score >= self.comments_threshold.get("min_score", 5)
                            meets_comments = num_comments >= self.comments_threshold.get("min_comments", 3)

                            if meets_score or meets_comments:
                                print(f"      → Fetching comments...", end="")
                                comments = self._fetch_comments_from_reddit(post_url)
                                post_data["comments"] = comments
                                print(f" ✓ {len(comments)} comments")
                                # Rate limit: be respectful to Reddit's servers
                                time.sleep(1)

                        query_posts.append(post_data)

                except requests.exceptions.RequestException as e:
                    print(f"✗ Network error: {str(e)[:100]}")
                    continue
                except Exception as e:
                    print(f"✗ Error: {type(e).__name__}: {str(e)[:100]}")
                    import traceback
                    print(f"      Details: {traceback.format_exc()[:200]}")
                    continue

            # Add all posts from this query to main list
            posts.extend(query_posts)
            print(f"  ✓ Total from query: {len(query_posts)} posts")

            # Save to cache
            self._save_to_cache(cache_key, query_posts, query_config)
            print(f"  ✓ Cached for 24 hours")

        print(f"\nTotal collected: {len(posts)} posts")

        # Warn if no posts collected
        if len(posts) == 0:
            print("\n⚠️  WARNING: No Reddit posts collected!")
            print("   Possible causes:")
            print("   - API errors (check logs above)")
            print("   - No posts matching query in timeframe")
            print("   - SociaVault API rate limit")
            print("   - API key issues")

        return posts


def main():
    """Test Reddit collector."""
    print("=" * 60)
    print("REDDIT COLLECTOR TEST")
    print("=" * 60 + "\n")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Check for cached response
    cache_path = "data/raw/test-reddit-cache.json"
    use_cache = os.path.exists(cache_path)

    if use_cache:
        print(f"Using cached API response from: {cache_path}\n")
        with open(cache_path) as f:
            cached = json.load(f)
            posts = cached.get("posts", [])
    else:
        print("No cache found - making live API call\n")

    try:
        if not use_cache:
            collector = RedditCollector()
            posts = collector.collect()

            # Cache the response
            Path("data/raw").mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'w') as f:
                json.dump({
                    "collected_at": datetime.now().isoformat(),
                    "source_type": "reddit",
                    "posts": posts
                }, f, indent=2)
            print(f"\n✓ Cached response to: {cache_path}")
        else:
            print(f"✓ Loaded {len(posts)} posts from cache")

        if posts:
            print("\n" + "=" * 60)
            print("SAMPLE POSTS")
            print("=" * 60)

            # Show first 3 posts
            for post in posts[:3]:
                print(f"\nTitle: {post['title']}")
                print(f"Subreddit: r/{post['subreddit']}")
                print(f"Score: {post['score']} | Comments: {post['num_comments']}")
                print(f"URL: {post['url']}")
                if post['selftext']:
                    print(f"Text: {post['selftext'][:150]}...")

            # Save to test file
            output_path = "data/raw/test-reddit-collection.json"
            Path("data/raw").mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump({
                    "collected_at": datetime.now().isoformat(),
                    "source_type": "reddit",
                    "posts": posts
                }, f, indent=2)

            print(f"\n✓ Saved to: {output_path}")
        else:
            print("\n✗ No posts collected")

    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nTo fix:")
        print("1. Copy .env.example to .env")
        print("2. Get SocialCrawl API key from: https://socialcrawl.dev")
        print("3. Add SOCIALCRAWL_API_KEY to .env")

    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
