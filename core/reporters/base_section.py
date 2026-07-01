"""Base Section Interface - Abstract class for report sections"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseSection(ABC):
    """Abstract base class for report sections

    Each section renders a portion of the final report (markdown format).
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, analysis_data: Optional[Dict[str, Any]] = None):
        """Initialize section

        Args:
            config: Section-specific configuration from topic.yaml
            analysis_data: Analysis results from ContentSummarizer
        """
        self.config = config or {}
        self.analysis_data = analysis_data or {}

    @abstractmethod
    def render(self) -> str:
        """Render section as markdown

        Returns:
            Markdown string for this section
        """
        pass

    def format_citation(self, citation_id: int) -> str:
        """Format citation reference

        Args:
            citation_id: Citation number (1-indexed)

        Returns:
            Formatted citation like [A1], [A2], etc.
        """
        return f"[A{citation_id}]"

    def format_date(self, date_str: str, format: str = "%Y-%m-%d") -> str:
        """Format ISO date string

        Args:
            date_str: ISO format date string
            format: strftime format string

        Returns:
            Formatted date string
        """
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime(format)
        except:
            return date_str

    def truncate(self, text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to max length

        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    def extract_citations(self, text: str) -> List[int]:
        """Extract citation IDs from text

        Args:
            text: Text containing citations like [A1], [A2]

        Returns:
            List of citation IDs
        """
        import re
        matches = re.findall(r'\[A(\d+)\]', text)
        return [int(m) for m in matches]
