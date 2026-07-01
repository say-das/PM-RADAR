"""Base Analyzer Interface - Abstract class for all analyzers"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import yaml
from pathlib import Path

from .llm_providers import get_llm_provider, BaseLLMProvider
from ..config_loader import ConfigLoader


class BaseAnalyzer(ABC):
    """Abstract base class for content analyzers

    Analyzers process collected data and generate insights using LLMs.
    """

    def __init__(self, topic_id: str):
        """Initialize analyzer for a topic

        Args:
            topic_id: Topic identifier (e.g., "fraud")
        """
        self.topic_id = topic_id
        self.config_loader = ConfigLoader()
        self.topic_config = self.config_loader.load_topic_config(topic_id)
        self.prompts = self._load_prompts()
        self.llm_provider = self._initialize_llm_provider()

    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from topic's prompts.yaml

        Returns:
            Dictionary of prompts by category
        """
        prompts_path = self.config_loader.config_dir / "topics" / self.topic_id / "prompts.yaml"

        if not prompts_path.exists():
            raise FileNotFoundError(f"Prompts file not found: {prompts_path}")

        with open(prompts_path) as f:
            return yaml.safe_load(f)

    def _initialize_llm_provider(self) -> BaseLLMProvider:
        """Initialize LLM provider from topic config

        Returns:
            LLM provider instance (OpenAI or Anthropic)
        """
        llm_config = self.topic_config.get("llm", {})
        provider_name = llm_config.get("provider", "openai")
        model = llm_config.get("model", "gpt-4o")

        import os
        api_key_env = llm_config.get("api_key_env", "OPENAI_API_KEY")
        api_key = os.getenv(api_key_env)

        return get_llm_provider(provider_name, model, api_key)

    @abstractmethod
    def analyze(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected data

        Args:
            collected_data: Data from collectors (RSS, Reddit, etc.)

        Returns:
            Analysis results dictionary
        """
        pass
