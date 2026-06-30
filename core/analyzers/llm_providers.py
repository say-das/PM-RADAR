"""LLM Provider Abstraction - Unified interface for OpenAI and Anthropic"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import os


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, model: str, api_key: Optional[str] = None):
        """Initialize LLM provider

        Args:
            model: Model identifier (e.g., "gpt-4o", "claude-sonnet-4")
            api_key: API key (optional, can load from env)
        """
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        response_format: Optional[str] = None
    ) -> str:
        """Generate completion from prompt

        Args:
            prompt: User prompt
            system_prompt: System/role prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: "json" for structured output, None for text

        Returns:
            Generated text or JSON string
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None):
        super().__init__(model, api_key)

        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key required (OPENAI_API_KEY env var)")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        response_format: Optional[str] = None
    ) -> str:
        """Generate completion using OpenAI API"""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Add response format if JSON requested
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, model: str = "claude-sonnet-4", api_key: Optional[str] = None):
        super().__init__(model, api_key)

        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("Anthropic API key required (ANTHROPIC_API_KEY env var)")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        response_format: Optional[str] = None
    ) -> str:
        """Generate completion using Anthropic API"""
        from anthropic import Anthropic

        client = Anthropic(api_key=self.api_key)

        # Add JSON instruction to prompt if requested
        if response_format == "json":
            prompt = f"{prompt}\n\nRespond with valid JSON only."

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = client.messages.create(**kwargs)
        return response.content[0].text


def get_llm_provider(provider_name: str, model: str, api_key: Optional[str] = None) -> BaseLLMProvider:
    """Factory function to get LLM provider instance

    Args:
        provider_name: "openai" or "anthropic"
        model: Model identifier
        api_key: Optional API key

    Returns:
        LLM provider instance

    Raises:
        ValueError: If provider not supported
    """
    if provider_name.lower() == "openai":
        return OpenAIProvider(model, api_key)
    elif provider_name.lower() == "anthropic":
        return AnthropicProvider(model, api_key)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
