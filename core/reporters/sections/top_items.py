"""Top Items Section - Renders top threats/trends from a category"""

import json
from ..base_section import BaseSection


class TopItemsSection(BaseSection):
    """Renders top threats/trends for a category"""

    def render(self) -> str:
        """Render top items section

        Config:
            title: Section title (e.g., "🔴 Top Threats")
            category: Category key (telecom_fraud, general_fraud)
            limit: Max items to show (default 5)

        Returns:
            Markdown string with top items list
        """
        title = self.config.get("title", "Top Items")
        category = self.config.get("category", "telecom_fraud")
        limit = self.config.get("limit", 5)

        # Get summary for this category
        summary_key = f"{category}_summary"
        summary_data = self.analysis_data.get(summary_key)

        if not summary_data:
            return f"## {title}\n\n*No items identified this period.*\n"

        # Try to parse as JSON
        items = []
        try:
            if isinstance(summary_data, str):
                data = json.loads(summary_data)
            else:
                data = summary_data

            # Look for common keys: top_threats, threats, items, trends
            items = (
                data.get("top_threats") or
                data.get("threats") or
                data.get("items") or
                data.get("trends") or
                []
            )

        except:
            # If not JSON, render plain text summary
            return f"## {title}\n\n{summary_data}\n"

        if not items:
            return f"## {title}\n\n*No items identified this period.*\n"

        # Limit items
        items = items[:limit]

        # Render as numbered list
        output = [f"## {title}\n"]

        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                item_title = item.get("title", "Unknown")
                description = item.get("description", "")
                citations = item.get("citation_ids") or item.get("citations") or []

                output.append(f"{i}. **{item_title}**: {description}")

                # Add citations if present
                if citations:
                    citation_str = ", ".join([self.format_citation(c) for c in citations])
                    output[-1] += f" {citation_str}"

            else:
                # Plain string item
                output.append(f"{i}. {item}")

        return "\n\n".join(output) + "\n"
