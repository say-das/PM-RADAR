import pytest
import os
from core.analyzers.llm_providers import OpenAIProvider, AnthropicProvider, get_llm_provider


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="No OpenAI API key")
def test_openai_provider_generates_text():
    """Test OpenAI provider generates text"""
    provider = OpenAIProvider()

    result = provider.generate(
        prompt="Say 'hello world' in exactly two words.",
        temperature=0.1,
        max_tokens=10
    )

    assert isinstance(result, str)
    assert len(result) > 0
    print(f"OpenAI result: {result}")


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="No OpenAI API key")
def test_openai_provider_generates_json():
    """Test OpenAI provider generates JSON"""
    provider = OpenAIProvider()

    result = provider.generate(
        prompt='Return JSON with one field "status" set to "ok"',
        response_format="json",
        temperature=0.1,
        max_tokens=50
    )

    assert isinstance(result, str)
    # Should be valid JSON
    import json
    data = json.loads(result)
    assert "status" in data
    print(f"OpenAI JSON result: {data}")


def test_get_llm_provider_returns_openai():
    """Test factory returns OpenAI provider"""
    # Skip actual instantiation if no key
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("No OpenAI API key")

    provider = get_llm_provider("openai", "gpt-4o")
    assert isinstance(provider, OpenAIProvider)


def test_get_llm_provider_invalid_raises_error():
    """Test factory raises error for invalid provider"""
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm_provider("invalid", "model")
