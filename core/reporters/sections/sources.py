"""Sources Section - Renders article references"""

from ..base_section import BaseSection
from typing import List, Dict, Any


class SourcesSection(BaseSection):
    """Renders sources/citations section"""

    def render(self) -> str:
        """Render sources section with numbered citations

        Returns:
            Markdown string with sources list
        """
        # Get filtered articles from analysis
        articles = self.analysis_data.get("filtered_articles", [])

        if not articles:
            return "## Sources\n\n*No sources cited.*\n"

        output = ["## Sources\n"]

        for i, article in enumerate(articles, 1):
            source = article.get("source", "Unknown Source")
            title = article.get("title", "Untitled")
            url = article.get("url", "#")
            published = article.get("published", "")

            # Format date if present
            date_str = ""
            if published:
                try:
                    date_str = f" ({self.format_date(published, '%b %d, %Y')})"
                except:
                    pass

            # Format as: <a id="a1"></a>**[A1]** [Source] Title - URL
            citation_id = self.format_citation(i)
            output.append(
                f'<a id="a{i}"></a>**{citation_id}** [{source}] {title}{date_str} - [{url}]({url})'
            )

        return "\n\n".join(output) + "\n"
