"""Competitive Intelligence Section - Renders competitor changelog analysis"""

from ..base_section import BaseSection


class CompetitiveIntelSection(BaseSection):
    """Renders competitive intelligence from competitor changelogs"""

    def render(self) -> str:
        """Render competitive intelligence section

        Returns:
            Markdown string with competitive intelligence insights
        """
        # Get competitive intel from analysis data
        # First try the summary field
        competitive_summary = (
            self.analysis_data.get("competitive_intelligence_summary") or
            self.analysis_data.get("competitive_intel_summary")
        )

        # If no summary, try competitor_analysis array
        competitor_analysis = self.analysis_data.get("competitor_analysis", [])

        # Skip if no data
        if not competitive_summary and not competitor_analysis:
            return ""

        title = self.config.get("title", "## Competition Watch")
        subtitle = self.config.get("subtitle", "*Recent fraud & security developments from messaging competitors*")

        output = [f"{title}\n"]
        output.append(f"{subtitle}\n")

        # If we have a summary, use it
        if competitive_summary:
            output.append(competitive_summary)
        # Otherwise format the competitor_analysis array
        elif competitor_analysis:
            for item in competitor_analysis:
                competitor = item.get("competitor", "Unknown")
                product = item.get("product", "")
                feature_title = item.get("title", "New Feature")
                date = item.get("date", "")
                analysis = item.get("analysis", "")

                # Format: **Competitor Product** (Date): *Feature Title*
                product_line = f"**{competitor}"
                if product:
                    product_line += f" {product}"
                product_line += "**"

                if date:
                    product_line += f" ({date})"

                product_line += f": *{feature_title}*"

                output.append(f"{product_line}\n")
                output.append(f"{analysis}\n")
                output.append("---\n")

        return "\n".join(output)
