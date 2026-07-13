"""Sources Section - Renders article references"""

import re
from ..base_section import BaseSection
from typing import List, Dict, Any, Set


class SourcesSection(BaseSection):
    """Renders sources/citations section"""

    def _extract_used_citations(self, report_content: str) -> Set[int]:
        """Extract citation IDs that are actually used in the report

        Args:
            report_content: Full report markdown content

        Returns:
            Set of citation IDs (integers) that appear in the content
        """
        # Find all citations in various formats:
        # [\[A1\]](#a1) - markdown link format (post-conversion)
        # [A1] - direct format
        article_citations = set()

        # Pattern 1: [\[A#\]](#a#) markdown link format
        # Match the whole link and extract the number
        matches = re.findall(r'\[\\?\[A(\d+)\\?\]\]\(#a\d+\)', report_content)
        article_citations.update(int(m) for m in matches)

        # Pattern 2: [A#] simple format (without escapes or links)
        matches = re.findall(r'(?<!\[)\[A(\d+)\](?!\()', report_content)
        article_citations.update(int(m) for m in matches)

        return article_citations

    def render(self) -> str:
        """Render sources section with only cited sources

        Returns:
            Markdown string with sources list
        """
        # Get filtered articles from analysis
        articles = self.analysis_data.get("filtered_articles", [])

        if not articles:
            return "## Sources\n\n*No sources cited.*\n"

        # Get the full report content to find which citations are used
        # This is available in config if passed by report generator
        report_content = self.config.get("_report_content", "")

        if report_content:
            # Extract used citation IDs
            used_citation_ids = self._extract_used_citations(report_content)
        else:
            # Fallback: show all articles (shouldn't happen with proper config)
            used_citation_ids = set(range(1, len(articles) + 1))

        if not used_citation_ids:
            return "## Sources\n\n*No sources cited.*\n"

        output = ["## Sources\n"]

        # Only render articles that are cited
        for citation_id in sorted(used_citation_ids):
            # citation_id is 1-indexed, article list is 0-indexed
            if citation_id <= len(articles):
                article = articles[citation_id - 1]
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
                citation_label = self.format_citation(citation_id)
                output.append(
                    f'<a id="a{citation_id}"></a>**{citation_label}** [{source}] {title}{date_str} - [{url}]({url})'
                )

        return "\n\n".join(output) + "\n"
