"""
Email Sender
Sends formatted intelligence reports via Brevo (formerly Sendinblue).
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path


class EmailSender:
    def __init__(self, config_path="config/email-config.json"):
        """Initialize email sender with configuration."""
        with open(config_path) as f:
            self.config = json.load(f)

        # Check for Brevo API key
        self.api_key = os.getenv("BREVO_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Brevo API key not found. "
                "Set BREVO_API_KEY in .env file"
            )

        self.api_url = "https://api.brevo.com/v3/smtp/email"

    def markdown_to_html(self, markdown_content):
        """
        Convert markdown to basic HTML for email.
        Simple conversion - handles common markdown patterns.
        """
        html = markdown_content

        # Headers
        html = html.replace("# ", "<h1>")
        html = html.replace("\n## ", "</h1>\n<h2>")
        html = html.replace("\n### ", "</h2>\n<h3>")

        # Close headers at end of line
        lines = []
        for line in html.split("\n"):
            if line.startswith("<h1>") and not line.endswith("</h1>"):
                line = line + "</h1>"
            elif line.startswith("<h2>") and not line.endswith("</h2>"):
                line = line + "</h2>"
            elif line.startswith("<h3>") and not line.endswith("</h3>"):
                line = line + "</h3>"
            lines.append(line)
        html = "\n".join(lines)

        # Bold
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # Horizontal rules
        html = html.replace("\n---\n", "\n<hr>\n")

        # Lists - numbered
        html = re.sub(r'\n(\d+)\. ', r'\n<li>', html)

        # Lists - bullets
        html = re.sub(r'\n- ', r'\n<li>', html)

        # Paragraphs (double line breaks)
        html = html.replace("\n\n", "</p>\n<p>")

        # Wrap in HTML structure
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        strong {{
            color: #2c3e50;
        }}
        li {{
            margin: 8px 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ecf0f1;
            margin: 30px 0;
        }}
        p {{
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <p>{html}</p>
</body>
</html>
"""
        return html

    def send_report(self, report_path, date_str):
        """
        Send intelligence report via email.

        Args:
            report_path: Path to markdown report file
            date_str: Date string for email subject

        Returns:
            dict with success status and details
        """
        print("Preparing email...")

        # Read markdown report
        with open(report_path, 'r') as f:
            markdown_content = f.read()

        # Convert to HTML
        print("  → Converting markdown to HTML...")
        html_content = self.markdown_to_html(markdown_content)

        # Build email
        subject = self.config["subject_template"].format(date=date_str)

        email_data = {
            "sender": {
                "name": self.config["sender"]["name"],
                "email": self.config["sender"]["email"]
            },
            "to": [
                {
                    "email": recipient["email"],
                    "name": recipient["name"]
                }
                for recipient in self.config["recipients"]
            ],
            "subject": subject,
            "htmlContent": html_content
        }

        print(f"  → Sending to {len(self.config['recipients'])} recipient(s)...")

        # Send via Brevo API
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=email_data,
                timeout=30
            )

            if response.status_code in [200, 201]:
                print("  ✓ Email sent successfully")
                return {
                    "success": True,
                    "message_id": response.json().get("messageId"),
                    "recipients": len(self.config["recipients"])
                }
            else:
                print(f"  ✗ Email failed: {response.status_code}")
                print(f"     {response.text}")
                return {
                    "success": False,
                    "error": response.text
                }

        except requests.exceptions.RequestException as e:
            print(f"  ✗ Network error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Test email sender."""
    print("=" * 60)
    print("EMAIL SENDER TEST")
    print("=" * 60 + "\n")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    try:
        sender = EmailSender()

        # Find most recent report
        reports_dir = Path("data/reports")
        report_files = list(reports_dir.glob("*.md"))

        if not report_files:
            print("✗ No reports found in data/reports/")
            print("  Run the main pipeline first: python -m scripts.main")
            return

        # Use most recent report
        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        date_str = latest_report.stem  # filename without .md

        print(f"Testing with report: {latest_report}\n")

        result = sender.send_report(latest_report, date_str)

        print("\n" + "=" * 60)
        print("RESULT")
        print("=" * 60)

        if result["success"]:
            print(f"✓ Email sent successfully")
            print(f"  Message ID: {result['message_id']}")
            print(f"  Recipients: {result['recipients']}")
        else:
            print(f"✗ Email failed: {result['error']}")

    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nTo fix:")
        print("1. Get Brevo API key from: https://app.brevo.com/settings/keys/api")
        print("2. Add BREVO_API_KEY to .env file")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
