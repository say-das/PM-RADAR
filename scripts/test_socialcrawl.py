"""
SocialCrawl API Test Script
Test Reddit search endpoint to understand response format and integration requirements.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def test_socialcrawl_api():
    """Test SocialCrawl Reddit search endpoint"""

    api_key = os.getenv('SOCIALCRAWL_API_KEY')

    if not api_key:
        print("❌ SOCIALCRAWL_API_KEY not found in .env")
        return False

    print("=" * 70)
    print("SOCIALCRAWL API TEST")
    print("=" * 70)
    print(f"\n✓ API Key found: {api_key[:10]}...{api_key[-5:]}\n")

    # Test 1: Basic search
    print("[Test 1] Basic Reddit Search")
    print("-" * 70)

    # Correct endpoint from SocialCrawl docs
    url = "https://www.socialcrawl.dev/v1/reddit/search"

    # Correct headers per SocialCrawl docs
    headers = {
        "x-api-key": api_key,
        "Cache-Control": "no-cache",
        "Idempotency-Key": "test-" + os.urandom(16).hex()  # Random UUID for testing
    }

    params = {
        "query": "twilio fraud",
        "sort": "relevance",
        "timeframe": "week",
        "trim": "true"
    }

    auth_methods = [
        {"name": "x-api-key header (correct)", "headers": headers, "params": params}
    ]

    for method in auth_methods:
        print(f"\nTrying: {method['name']}")

        try:
            response = requests.get(
                url,
                headers=method["headers"],
                params=method["params"],
                timeout=15
            )

            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print(f"  ✓ SUCCESS with {method['name']}")
                data = response.json()
                print(f"\n  Response structure:")
                print(f"    Type: {type(data)}")
                if isinstance(data, dict):
                    print(f"    Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"    Length: {len(data)}")
                    if len(data) > 0:
                        print(f"    First item keys: {list(data[0].keys())}")

                # Save successful response
                output_file = "data/raw/socialcrawl-test-response.json"
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"\n  ✓ Saved full response to: {output_file}")

                # Show sample
                print(f"\n  Sample response (first 500 chars):")
                print(f"  {json.dumps(data, indent=2)[:500]}...")

                return True
            else:
                print(f"  ✗ Failed: {response.status_code}")
                print(f"  Response: {response.text[:200]}")

        except requests.exceptions.SSLError as e:
            print(f"  ✗ SSL Error: {str(e)[:100]}")
        except requests.exceptions.Timeout:
            print(f"  ✗ Timeout (15s)")
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {str(e)[:100]}")

    print("\n❌ All authentication methods failed")
    return False


def test_alternative_endpoints():
    """Test alternative endpoint formats"""

    api_key = os.getenv('SOCIALCRAWL_API_KEY')

    print("\n" + "=" * 70)
    print("[Test 2] Alternative Endpoints")
    print("=" * 70 + "\n")

    endpoints = [
        "https://www.socialcrawl.dev/v1/reddit/search",
        "https://socialcrawl.dev/v1/reddit/search",
        "https://api.socialcrawl.dev/v1/reddit/search",
    ]

    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        try:
            response = requests.get(
                endpoint,
                headers={
                    "x-api-key": api_key,
                    "Cache-Control": "no-cache"
                },
                params={"query": "test", "sort": "relevance", "timeframe": "week"},
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ Working endpoint found!")
                return endpoint
        except Exception as e:
            print(f"  ✗ {type(e).__name__}")

    return None


def check_api_documentation():
    """Check if we can fetch API documentation"""

    print("\n" + "=" * 70)
    print("[Test 3] Fetch API Documentation")
    print("=" * 70 + "\n")

    doc_urls = [
        "https://socialcrawl.dev/docs/api",
        "https://docs.socialcrawl.dev",
        "https://www.socialcrawl.dev/docs/api-reference",
    ]

    for url in doc_urls:
        print(f"Checking: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✓ Documentation accessible")
                print(f"  Content length: {len(response.text)} bytes")

                # Save for manual review
                doc_file = "data/raw/socialcrawl-docs.html"
                with open(doc_file, 'w') as f:
                    f.write(response.text)
                print(f"  ✓ Saved to: {doc_file}")
                return True
        except Exception as e:
            print(f"  ✗ {type(e).__name__}")

    return False


if __name__ == "__main__":
    print("\n")

    # Ensure output directory exists
    os.makedirs("data/raw", exist_ok=True)

    # Run tests
    success = test_socialcrawl_api()

    if not success:
        test_alternative_endpoints()
        check_api_documentation()

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

    if success:
        print("\n✓ SocialCrawl API is working and ready for integration")
    else:
        print("\n⚠ API validation failed - see errors above")
        print("\nNext steps:")
        print("1. Check API key is correct")
        print("2. Verify endpoint URL with SocialCrawl docs")
        print("3. Check if API requires signup/activation")
        print("4. Contact SocialCrawl support if issues persist")
