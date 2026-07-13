"""Reporter Utilities - Shared helper functions for report generation"""

import json
from typing import Any, Optional


def safe_parse_json(data: str, section_name: str = "unknown") -> Optional[Any]:
    """
    Safely parse JSON from LLM response, handling markdown fences and format variations.

    This handles common LLM response variations:
    - JSON wrapped in ```json...``` markdown fences
    - JSON wrapped in plain ``` fences
    - Raw JSON without fences
    - Invalid/malformed JSON

    Args:
        data: String containing JSON (possibly wrapped in markdown)
        section_name: Name of section for error logging

    Returns:
        Parsed JSON object/array, or None if parsing fails

    Example:
        >>> safe_parse_json('```json\\n[{"key": "value"}]\\n```')
        [{'key': 'value'}]

        >>> safe_parse_json('invalid json', 'test')
        None
    """
    if not data or not isinstance(data, str):
        return None

    try:
        # Strip markdown code fences
        clean_data = data.strip()

        # Remove opening fences
        if clean_data.startswith('```json'):
            clean_data = clean_data[7:]  # len('```json') = 7
        elif clean_data.startswith('```'):
            clean_data = clean_data[3:]   # len('```') = 3

        # Remove closing fences
        if clean_data.endswith('```'):
            clean_data = clean_data[:-3]

        clean_data = clean_data.strip()

        # Parse JSON
        return json.loads(clean_data)

    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error in {section_name}: {e}")
        return None
    except Exception as e:
        print(f"    ⚠️  Unexpected error parsing {section_name}: {e}")
        return None


def extract_from_json_variants(data: Any, keys: list, section_name: str = "unknown") -> Optional[Any]:
    """
    Try to extract data from JSON that may be in different formats.

    Handles:
    - String containing JSON (parses it)
    - Dict/List already parsed
    - Multiple possible keys for same data

    Args:
        data: Data to extract from (string, dict, list, or None)
        keys: List of possible keys to try (in order of preference)
        section_name: Name for logging

    Returns:
        Extracted data, or None if not found

    Example:
        >>> data = '{"top_threats": [...], "threats": [...]}'
        >>> extract_from_json_variants(data, ["top_threats", "threats", "items"])
        [...]  # Returns value from "top_threats"
    """
    # If string, try to parse as JSON first
    if isinstance(data, str):
        data = safe_parse_json(data, section_name)

    # If it's already a list/primitive, return it
    if not isinstance(data, dict):
        return data

    # Try each key in order
    for key in keys:
        if key in data and data[key]:
            return data[key]

    return None
