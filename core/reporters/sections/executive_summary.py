"""Executive Summary Section"""

from ..base_section import BaseSection


class ExecutiveSummarySection(BaseSection):
    """Renders executive summary from analysis"""

    def render(self) -> str:
        """Render executive summary section

        Returns:
            Markdown string with executive summary
        """
        # Get summary from analysis (could be from any category)
        summary_text = None

        # Try telecom fraud summary first
        telecom_summary = self.analysis_data.get("telecom_fraud_summary")
        if telecom_summary and isinstance(telecom_summary, str):
            # Extract executive summary if it's in JSON format
            try:
                import json
                data = json.loads(telecom_summary)
                summary_text = data.get("executive_summary")
            except:
                # Plain text summary
                summary_text = telecom_summary

        # Fallback to general fraud
        if not summary_text:
            general_summary = self.analysis_data.get("general_fraud_summary")
            if general_summary and isinstance(general_summary, str):
                try:
                    import json
                    data = json.loads(general_summary)
                    summary_text = data.get("executive_summary")
                except:
                    summary_text = general_summary

        if not summary_text:
            return "## Executive Summary\n\n*No analysis available this period.*\n"

        # Truncate if too long
        if len(summary_text) > 1000:
            summary_text = self.truncate(summary_text, 1000)

        return f"## Executive Summary\n\n{summary_text}\n"
