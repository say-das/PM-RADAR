import pytest
from core.analyzers.summarizer import ContentSummarizer


def test_summarizer_initializes():
    """Test ContentSummarizer initializes correctly"""
    summarizer = ContentSummarizer("fraud")

    assert summarizer.topic_id == "fraud"
    assert summarizer.prompts is not None
    assert summarizer.llm_provider is not None


def test_summarizer_analyze_empty_data():
    """Test analyze with empty data"""
    summarizer = ContentSummarizer("fraud")

    result = summarizer.analyze({
        "rss_articles": [],
        "reddit_posts": [],
        "competitor_changelogs": []
    })

    assert "analyzed_at" in result
    assert "categorized_counts" in result
    assert result["categorized_counts"]["telecom"] == 0


def test_summarizer_categorize_with_real_articles():
    """Test categorization with sample articles (makes LLM call)"""
    summarizer = ContentSummarizer("fraud")

    sample_data = {
        "rss_articles": [
            {
                "source": "Test Source",
                "category": "general",
                "title": "Major SMS phishing campaign targets banks",
                "url": "https://example.com/article",
                "published": "2026-07-01T00:00:00",
                "summary": "A widespread SMS phishing campaign is targeting bank customers with fake authentication requests. The attack uses social engineering to steal credentials."
            }
        ],
        "reddit_posts": [],
        "competitor_changelogs": []
    }

    result = summarizer.analyze(sample_data)

    # Should categorize the article
    assert "categorized_counts" in result
    # Article about SMS phishing should be categorized
    assert result["categorized_counts"]["telecom"] + result["categorized_counts"]["general"] > 0

    print(f"Categorized: telecom={result['categorized_counts']['telecom']}, general={result['categorized_counts']['general']}")
