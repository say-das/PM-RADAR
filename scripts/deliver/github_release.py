"""
GitHub Release Publisher for PM Radar
Creates GitHub releases with report attachments and publishes HTML to GitHub Pages.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime


class GitHubReleasePublisher:
    """Publishes PM Radar reports via GitHub Releases and Pages."""

    def __init__(self):
        self.repo = "twilio-internal/ig-fraud-research"
        self.pages_base = "https://twilio-internal.github.io/ig-fraud-research/reports"

    def publish_report(self, report_md_path, date_str):
        """
        Publish report to GitHub Release and Pages.

        Args:
            report_md_path: Path to markdown report file
            date_str: Report date string (YYYY-MM-DD)

        Returns:
            dict with success status and details
        """
        result = {
            "success": False,
            "release_url": None,
            "pages_url": None,
            "error": None
        }

        try:
            report_md_path = Path(report_md_path)

            if not report_md_path.exists():
                result["error"] = f"Report file not found: {report_md_path}"
                return result

            # Find corresponding HTML file
            html_path = report_md_path.parent / f"{date_str}.html"

            if not html_path.exists():
                result["error"] = f"HTML report not found: {html_path}"
                return result

            # Step 1: Copy HTML to GitHub Pages directory
            pages_dir = Path("docs/reports")
            pages_dir.mkdir(parents=True, exist_ok=True)

            pages_html = pages_dir / f"{date_str}.html"

            import shutil
            shutil.copy(html_path, pages_html)

            print(f"✓ Copied HTML to GitHub Pages: {pages_html}")

            # Step 2: Create release summary from markdown
            release_notes = self._generate_release_notes(report_md_path, date_str)

            # Step 3: Commit and push Pages update
            self._commit_and_push_pages(date_str, pages_html)

            # Step 4: Create GitHub Release
            release_url = self._create_github_release(
                date_str,
                release_notes,
                html_path,
                report_md_path
            )

            result["success"] = True
            result["release_url"] = release_url
            result["pages_url"] = f"{self.pages_base}/{date_str}.html"

            print(f"\n✓ Release published: {release_url}")
            print(f"✓ Report viewable at: {result['pages_url']}")

        except Exception as e:
            result["error"] = str(e)
            import traceback
            traceback.print_exc()

        return result

    def _generate_release_notes(self, report_md_path, date_str):
        """Extract executive summary from markdown report for release notes."""
        with open(report_md_path, 'r') as f:
            content = f.read()

        # Extract executive summary section
        lines = content.split('\n')
        summary_lines = []
        in_summary = False

        for line in lines:
            if '## Executive Summary' in line:
                in_summary = True
                continue
            elif line.startswith('##') and in_summary:
                break
            elif in_summary and line.strip():
                summary_lines.append(line)

        summary = '\n'.join(summary_lines[:10])  # First 10 lines

        release_notes = f"""# PM Radar Weekly Intelligence Digest
**Week of {date_str}**

{summary}

---

## 📊 View Full Report

**[Click here to view the full HTML report](https://twilio-internal.github.io/ig-fraud-research/reports/{date_str}.html)**

Or download the attachments below:
- `{date_str}.html` - Styled HTML report with clickable citations
- `{date_str}.md` - Plain markdown version

---

## 📬 Subscribe to Updates

To receive notifications for future reports:
1. Click **Watch** (top right) → **Custom**
2. Check **Releases**
3. Click **Apply**

You'll get an email notification every Monday when new reports are published!
"""

        return release_notes

    def _commit_and_push_pages(self, date_str, pages_html):
        """Commit and push GitHub Pages update."""
        try:
            # Stage the new report
            subprocess.run(
                ["git", "add", str(pages_html)],
                check=True,
                capture_output=True
            )

            # Commit
            subprocess.run(
                ["git", "commit", "-m", f"Publish report: {date_str}"],
                check=True,
                capture_output=True
            )

            # Push
            subprocess.run(
                ["git", "push", "origin", "main"],
                check=True,
                capture_output=True
            )

            print(f"✓ Pushed GitHub Pages update")

        except subprocess.CalledProcessError as e:
            print(f"⚠ Git commit/push warning: {e}")
            # Non-fatal - release can still be created

    def _create_github_release(self, date_str, release_notes, html_path, md_path):
        """Create GitHub release with gh CLI."""

        # Check if gh CLI is available
        try:
            subprocess.run(
                ["gh", "--version"],
                check=True,
                capture_output=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception(
                "GitHub CLI (gh) not found. Install from: https://cli.github.com/"
            )

        # Create release with attachments
        tag_name = f"report-{date_str}"
        title = f"PM Radar Report - {date_str}"

        # Write release notes to temp file
        notes_file = Path(f"/tmp/release-notes-{date_str}.md")
        with open(notes_file, 'w') as f:
            f.write(release_notes)

        try:
            # Create release
            result = subprocess.run(
                [
                    "gh", "release", "create",
                    tag_name,
                    "--repo", self.repo,
                    "--title", title,
                    "--notes-file", str(notes_file),
                    str(html_path),
                    str(md_path)
                ],
                check=True,
                capture_output=True,
                text=True
            )

            # Extract release URL from output
            release_url = result.stdout.strip()

            return release_url

        finally:
            # Cleanup temp file
            if notes_file.exists():
                notes_file.unlink()

    def check_prerequisites(self):
        """Check if required tools are available."""
        issues = []

        # Check git
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Git not found")

        # Check gh CLI
        try:
            subprocess.run(["gh", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("GitHub CLI (gh) not found - install from https://cli.github.com/")

        # Check gh authentication
        try:
            subprocess.run(
                ["gh", "auth", "status"],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            issues.append("GitHub CLI not authenticated - run: gh auth login")

        return issues


if __name__ == "__main__":
    """Test the GitHub Release publisher."""
    publisher = GitHubReleasePublisher()

    # Check prerequisites
    issues = publisher.check_prerequisites()
    if issues:
        print("Prerequisites check failed:")
        for issue in issues:
            print(f"  ✗ {issue}")
        exit(1)

    print("✓ All prerequisites met")

    # Test with most recent report (if exists)
    reports_dir = Path("data/reports")
    md_files = sorted(reports_dir.glob("*.md"), reverse=True)

    if md_files:
        latest_report = md_files[0]
        date_str = latest_report.stem

        print(f"\nTesting with report: {date_str}")
        print("This will create a real GitHub release. Continue? (y/n): ", end="")

        response = input().strip().lower()
        if response == 'y':
            result = publisher.publish_report(latest_report, date_str)

            if result["success"]:
                print("\n✓ Release published successfully!")
                print(f"  Release: {result['release_url']}")
                print(f"  Report: {result['pages_url']}")
            else:
                print(f"\n✗ Release failed: {result['error']}")
        else:
            print("Cancelled")
    else:
        print("No reports found in data/reports/")
