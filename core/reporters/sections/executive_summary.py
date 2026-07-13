"""Executive Summary Section"""

from ..base_section import BaseSection


class ExecutiveSummarySection(BaseSection):
    """Renders executive summary from analysis"""

    def render(self) -> str:
        """Render executive summary section

        Returns:
            Markdown string with executive summary
        """
        # Generate stats-based summary
        categorized_counts = self.analysis_data.get("categorized_counts", {})
        telecom_count = categorized_counts.get("telecom", 0)
        general_count = categorized_counts.get("general", 0)
        competitive_count = categorized_counts.get("competitive", 0)

        # Count Reddit posts if available
        reddit_summary = self.analysis_data.get("reddit_community_summary")
        reddit_count = 1 if reddit_summary else 0

        output = ["## Executive Summary\n"]
        output.append("**This Week's Intelligence:**\n")
        output.append(f"- 🔴 **{telecom_count} telecom fraud threats** identified")
        output.append(f"- 🟡 **{general_count} general security threats** identified")

        if competitive_count > 0:
            output.append(f"- 📊 **{competitive_count} competitor features** analyzed")

        if reddit_count > 0:
            output.append(f"- 💬 **{reddit_count} community discussions** reviewed")

        output.append("\n---\n")

        return "\n".join(output)
