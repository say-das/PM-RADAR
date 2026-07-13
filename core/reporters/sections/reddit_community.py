"""Reddit Community Section - Renders community discussion insights"""

import json
from ..base_section import BaseSection


class RedditCommunitySection(BaseSection):
    """Renders Reddit community discussion insights"""

    def render(self) -> str:
        """Render Reddit community section

        Returns:
            Markdown string with Reddit insights
        """
        # Get Reddit analysis from analysis data
        reddit_summary = self.analysis_data.get("reddit_community_summary")

        if not reddit_summary:
            return ""  # Skip section if no Reddit data

        title = self.config.get("title", "## Twilio Community Discussions (Reddit)")

        # Check if it's JSON that needs parsing (v1 format)
        if isinstance(reddit_summary, str) and (
            reddit_summary.strip().startswith('```json') or
            reddit_summary.strip().startswith('{')
        ):
            try:
                # Strip markdown code fences if present
                clean_data = reddit_summary.strip()
                if clean_data.startswith('```json'):
                    clean_data = clean_data[7:]
                if clean_data.startswith('```'):
                    clean_data = clean_data[3:]
                if clean_data.endswith('```'):
                    clean_data = clean_data[:-3]
                clean_data = clean_data.strip()

                # Parse JSON and format nicely
                data = json.loads(clean_data)

                # Format the structured data
                output = [f"{title}\n"]
                output.append("**Trending Concerns & Topics:**\n")

                concerns = data.get("trending_concerns", [])
                for i, concern in enumerate(concerns, 1):
                    topic = concern.get("topic", "Unknown")
                    description = concern.get("description", "")

                    output.append(f"**{i}. {topic}**")
                    output.append(f"{description}")

                    examples = concern.get("examples", [])
                    if examples:
                        output.append("\n**Examples:**")
                        for ex in examples:
                            quote = ex.get("quote", "")
                            post_num = ex.get("post_num", "")
                            if post_num:
                                output.append(f'- "{quote}" [[R{post_num}]](#r{post_num})]')
                            else:
                                output.append(f'- "{quote}"')
                        output.append("")

                # Add sentiment if present
                sentiment = data.get("sentiment", "")
                if sentiment:
                    output.append(f"**Overall Sentiment:** {sentiment}\n")

                # Add insights if present
                insights = data.get("insights", [])
                if insights:
                    output.append("**Key Insights:**")
                    for insight in insights:
                        output.append(f"- {insight}")

                return "\n".join(output) + "\n"

            except Exception as e:
                # If parsing fails, return as plain text
                print(f"    ⚠ Could not parse Reddit JSON: {e}")
                pass

        # Render as plain text (v2 format)
        output = [f"{title}\n"]
        output.append(reddit_summary)

        return "\n".join(output) + "\n"
