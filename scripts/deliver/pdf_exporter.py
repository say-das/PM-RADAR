"""
PDF Exporter
Converts markdown reports to PDF format for distribution.

Note: Uses markdown + HTML export. Can optionally use wkhtmltopdf if installed.
"""

import os
import markdown
from datetime import datetime


class PDFExporter:
    def __init__(self):
        """Initialize PDF exporter."""
        pass

    def markdown_to_html(self, markdown_path, html_path=None, include_css=True):
        """
        Convert markdown file to print-ready HTML.

        Args:
            markdown_path: Path to markdown file
            html_path: Output HTML path (optional, auto-generated if not provided)
            include_css: Apply custom CSS styling

        Returns:
            Path to generated HTML file
        """
        # Auto-generate HTML path if not provided
        if html_path is None:
            html_path = markdown_path.replace('.md', '.html')

        # Read markdown file
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.extra'
            ]
        )

        # Post-process: Convert citation references to clickable links
        html_content = self._add_citation_links(html_content)

        # Wrap in HTML document with styling
        styled_html = self._wrap_html(html_content, include_css)

        # Save HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(styled_html)

        return html_path

    def markdown_to_pdf(self, markdown_path, pdf_path=None, include_css=True):
        """
        Convert markdown file to PDF.

        Args:
            markdown_path: Path to markdown file
            pdf_path: Output PDF path (optional, auto-generated if not provided)
            include_css: Apply custom CSS styling

        Returns:
            Path to generated PDF file
        """
        # Auto-generate PDF path if not provided
        if pdf_path is None:
            pdf_path = markdown_path.replace('.md', '.pdf')

        # Read markdown file
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.extra'
            ]
        )

        # Post-process: Convert citation references to clickable links
        html_content = self._add_citation_links(html_content)

        # Wrap in HTML document with styling
        styled_html = self._wrap_html(html_content, include_css)

        # Try multiple PDF conversion methods
        try:
            # Method 1: Try wkhtmltopdf (if installed)
            import pdfkit
            pdfkit.from_string(styled_html, pdf_path)
            return pdf_path
        except (ImportError, OSError):
            pass

        try:
            # Method 2: Try WeasyPrint (requires system deps)
            from weasyprint import HTML, CSS
            HTML(string=styled_html).write_pdf(
                pdf_path,
                stylesheets=[CSS(string=self._get_css())] if include_css else None
            )
            return pdf_path
        except (ImportError, OSError):
            pass

        # Fallback: Save as HTML with PDF-like styling
        html_path = pdf_path.replace('.pdf', '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(styled_html)

        raise ImportError(
            f"PDF generation requires either:\n"
            f"  1. wkhtmltopdf (install: brew install wkhtmltopdf)\n"
            f"  2. WeasyPrint with system dependencies (brew install pango)\n"
            f"Generated HTML instead: {html_path}\n"
            f"Open in browser and Print to PDF manually."
        )

    def _add_citation_links(self, html_content):
        """Convert citation references like [A1] or [R1] to clickable anchor links."""
        import re

        # Pattern to match citation references in body text (not in sources list)
        # Replace [A1] with <a href="#A1">[A1]</a>
        def replace_citation(match):
            citation = match.group(0)
            citation_id = citation.strip('[]')
            return f'<a href="#{citation_id}">{citation}</a>'

        # Find citations in text (not in <li> tags that start with the citation)
        # This regex finds [A1-99] or [R1-99] not at the start of list items
        html_content = re.sub(
            r'(?<!\>)\[([AR]\d+)\]',
            replace_citation,
            html_content
        )

        # Add id attributes to source list items
        # Find list items that start with [A1]: or [R1]:
        def add_source_id(match):
            citation = match.group(1)
            citation_id = citation.strip('[]').rstrip(':')
            rest_of_line = match.group(2)
            # Add id to the <li> tag
            return f'<li id="{citation_id}">{citation}{rest_of_line}'

        html_content = re.sub(
            r'<li>(\[[AR]\d+\]:)(.*?)</li>',
            add_source_id,
            html_content,
            flags=re.DOTALL
        )

        # Clean up any double <li> tags that might have been created
        html_content = re.sub(
            r'<li id="([AR]\d+)\]:">\s*<li id="\1">',
            r'<li id="\1">',
            html_content
        )

        return html_content

    def _wrap_html(self, body_content, include_css):
        """Wrap HTML content in full document structure with Twilio theme."""
        css_link = '<link rel="preconnect" href="https://fonts.googleapis.com">\n    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">' if include_css else ''

        style_tag = f'<style>\n{self._get_css()}\n    </style>' if include_css else ''

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PM Radar Intelligence Report</title>
    {css_link}
    {style_tag}
</head>
<body>
    <div class="container">
        {body_content}
    </div>

    <!-- Twilio Branding Footer -->
    <div style="margin-top: 3em; padding: 1.5em 0; text-align: center; border-top: 2px solid #E1E3EA;">
        <svg width="80" height="24" viewBox="0 0 80 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity: 0.5;">
            <path d="M12 0C5.4 0 0 5.4 0 12C0 18.6 5.4 24 12 24C18.6 24 24 18.6 24 12C24 5.4 18.6 0 12 0ZM8.4 8.4C9.6 8.4 10.8 9.6 10.8 10.8C10.8 12 9.6 13.2 8.4 13.2C7.2 13.2 6 12 6 10.8C6 9.6 7.2 8.4 8.4 8.4ZM15.6 8.4C16.8 8.4 18 9.6 18 10.8C18 12 16.8 13.2 15.6 13.2C14.4 13.2 13.2 12 13.2 10.8C13.2 9.6 14.4 8.4 15.6 8.4ZM8.4 15.6C9.6 15.6 10.8 16.8 10.8 18C10.8 19.2 9.6 20.4 8.4 20.4C7.2 20.4 6 19.2 6 18C6 16.8 7.2 15.6 8.4 15.6ZM15.6 15.6C16.8 15.6 18 16.8 18 18C18 19.2 16.8 20.4 15.6 20.4C14.4 20.4 13.2 19.2 13.2 18C13.2 16.8 14.4 15.6 15.6 15.6Z" fill="#F22F46"/>
        </svg>
        <p style="margin: 0.5em 0 0 0; font-size: 9pt; color: #606B85;">Powered by PM Radar • Twilio Product Intelligence</p>
    </div>
</body>
</html>
"""

    def _get_css(self):
        """Get CSS styling for PDF (Twilio-themed, A4 format with red branding)."""
        return """
        /* Twilio Brand Colors */
        :root {
            --twilio-red: #F22F46;
            --twilio-blue: #0263E0;
            --twilio-dark-blue: #001489;
            --twilio-blue-60: #0D61D8;
            --twilio-blue-10: #E1EFFC;
            --twilio-gray-100: #121C2D;
            --twilio-gray-90: #18222E;
            --twilio-gray-80: #1F2933;
            --twilio-gray-70: #3E4C59;
            --twilio-gray-60: #606B85;
            --twilio-gray-50: #8891AA;
            --twilio-gray-40: #C4C7D1;
            --twilio-gray-30: #D9DBE5;
            --twilio-gray-20: #E8EAED;
            --twilio-gray-10: #F4F5F6;
        }

        @page {
            size: Letter;
            margin: 0.75in 1in;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 14px;
            line-height: 1.4;
            color: var(--twilio-gray-90);
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            max-width: 210mm;
            margin: 0 auto;
            padding: 40px 60px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            min-height: 297mm;
        }

        @media screen and (max-width: 992px) {
            body {
                padding: 12px;
            }
            .container {
                padding: 24px 32px;
            }
        }

        @media print {
            body {
                padding: 0;
                background: white;
            }
            .container {
                box-shadow: none;
                max-width: 100%;
            }
        }

        /* Typography with Twilio Red Start */
        h1 {
            color: var(--twilio-red);
            font-size: 32px;
            font-weight: 700;
            line-height: 1.1;
            margin: 0 0 6px 0;
            letter-spacing: -0.02em;
        }

        h1 + p {
            color: var(--twilio-gray-60);
            font-size: 13px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 3px solid var(--twilio-red);
            line-height: 1.3;
        }

        h2 {
            color: var(--twilio-blue-60);
            font-size: 24px;
            font-weight: 700;
            line-height: 1.2;
            margin: 24px 0 8px 0;
            page-break-after: avoid;
        }

        h3 {
            color: var(--twilio-gray-90);
            font-size: 18px;
            font-weight: 600;
            line-height: 1.3;
            margin: 16px 0 6px 0;
            page-break-after: avoid;
        }

        /* Paragraphs with hierarchy */
        p {
            margin: 6px 0;
            line-height: 1.5;
            color: var(--twilio-gray-60);
            font-weight: 400;
            font-size: 14px;
        }

        /* Section labels like "Executive Summary:" */
        p strong:first-child {
            color: var(--twilio-gray-80);
            font-weight: 600;
            font-size: 14px;
        }

        /* Default strong styling - subtle */
        strong {
            font-weight: 500;
            color: var(--twilio-gray-70);
        }

        em {
            font-style: italic;
            color: var(--twilio-gray-50);
            font-weight: 400;
        }

        /* Compact lists */
        ul, ol {
            margin: 8px 0;
            padding-left: 24px;
        }

        li {
            margin: 4px 0;
            line-height: 1.5;
            color: var(--twilio-gray-60);
            font-weight: 400;
            font-size: 14px;
        }

        li::marker {
            color: var(--twilio-gray-40);
            font-weight: 400;
        }

        /* All strong tags in lists should be normal weight by default */
        li strong {
            font-weight: 400;
            color: var(--twilio-gray-60);
        }

        /* Only the very first strong in a list item gets emphasis */
        li > strong:first-child {
            font-weight: 500;
            color: var(--twilio-gray-80);
            font-size: 14px;
        }

        /* Executive Summary - Twilio branded */
        #executive-summary + ul {
            background: var(--twilio-blue-10);
            padding: 16px 20px;
            border-radius: 6px;
            border-left: 4px solid var(--twilio-red);
            margin: 12px 0 20px 0;
        }

        #executive-summary + ul li {
            font-weight: 600;
            color: var(--twilio-gray-90);
            font-size: 14px;
            margin: 3px 0;
        }

        #executive-summary + ul li strong {
            font-weight: 700;
            color: var(--twilio-red);
        }

        /* Blockquotes with Twilio accent */
        blockquote {
            margin: 12px 0;
            padding: 10px 16px;
            border-left: 4px solid var(--twilio-blue);
            background: var(--twilio-blue-10);
            font-style: italic;
            color: var(--twilio-gray-70);
            line-height: 1.4;
        }

        /* Code styling */
        code {
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            background-color: var(--twilio-gray-10);
            color: var(--twilio-dark-blue);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
        }

        pre {
            background: var(--twilio-gray-10);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid var(--twilio-gray-20);
        }

        pre code {
            background: transparent;
            padding: 0;
        }

        /* Links - Twilio primary blue */
        a {
            color: var(--twilio-blue);
            text-decoration: none;
            font-weight: 500;
        }

        a:hover {
            color: var(--twilio-blue-60);
            text-decoration: underline;
        }

        /* Compact horizontal rules */
        hr {
            border: none;
            border-top: 1px solid var(--twilio-gray-30);
            margin: 16px 0;
        }

        /* Table styling with Twilio colors */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
        }

        th, td {
            padding: 8px 10px;
            text-align: left;
            border-bottom: 1px solid var(--twilio-gray-30);
            line-height: 1.4;
        }

        th {
            font-weight: 700;
            color: white;
            background: var(--twilio-red);
        }

        tr:hover {
            background: var(--twilio-blue-10);
        }

        /* Inline Citations - smaller and clickable */
        a[href^="#"] {
            color: var(--twilio-blue);
            font-size: 10px;
            font-weight: 600;
            vertical-align: super;
            text-decoration: none;
            padding: 0 1px;
            transition: all 0.2s ease;
        }

        a[href^="#"]:hover {
            color: var(--twilio-red);
            text-decoration: underline;
        }

        /* Make citation brackets appear as superscript links */
        p a[href^="#"],
        li a[href^="#"] {
            font-size: 10px;
            line-height: 0;
        }

        /* Glossary emphasis */
        #glossary + p {
            color: var(--twilio-gray-50);
            font-style: italic;
            margin-bottom: 8px;
            font-size: 12px;
            line-height: 1.4;
        }

        #glossary + p + ul li {
            margin: 5px 0;
        }

        /* Glossary terms should stand out */
        #glossary + p + ul li > strong:first-child {
            color: var(--twilio-red);
            font-weight: 700;
            font-size: 14px;
        }

        /* But the rest of glossary text should be normal */
        #glossary + p + ul li strong:not(:first-child) {
            font-weight: 400;
            color: var(--twilio-gray-60);
        }

        /* Sources section - everything smaller and lighter */
        #sources + p + ul li {
            font-size: 12px;
            color: var(--twilio-gray-50);
            font-weight: 400;
            line-height: 1.4;
            margin: 3px 0;
            scroll-margin-top: 20px; /* Offset for smooth scroll */
            list-style-type: none; /* Remove default bullets */
            padding-left: 0;
        }

        #sources + p + ul li strong {
            font-weight: 400;
            color: var(--twilio-gray-50);
        }

        #sources + p + ul li a {
            font-weight: 500;
            color: var(--twilio-blue);
        }

        /* Citation reference targets in sources list */
        #sources + p + ul li[id] {
            background: transparent;
            transition: background 0.3s ease;
        }

        #sources + p + ul li[id]:target {
            background: var(--twilio-blue-10);
            padding: 4px 8px;
            margin-left: -8px;
            border-radius: 4px;
        }

        /* Footer */
        body > p:last-of-type {
            text-align: center;
            color: var(--twilio-gray-60);
            font-size: 11px;
            margin-top: 24px;
            padding-top: 12px;
            border-top: 1px solid var(--twilio-gray-30);
        }

        /* Print optimizations */
        p, li {
            orphans: 3;
            widows: 3;
        }

        h1, h2, h3 {
            page-break-after: avoid;
        }

        @media print {
            body {
                background: white;
            }
            a {
                color: var(--twilio-blue) !important;
            }
        }
        """


def main():
    """Test PDF exporter."""
    print("=" * 60)
    print("PDF EXPORTER TEST")
    print("=" * 60 + "\n")

    # Find most recent report
    reports_dir = "data/reports"
    if not os.path.exists(reports_dir):
        print(f"✗ Reports directory not found: {reports_dir}")
        print("Run the pipeline first to generate a report.")
        return

    # Get all markdown files
    md_files = [f for f in os.listdir(reports_dir) if f.endswith('.md')]
    if not md_files:
        print(f"✗ No markdown reports found in {reports_dir}")
        return

    # Sort by filename (date) and get most recent
    md_files.sort(reverse=True)
    latest_report = os.path.join(reports_dir, md_files[0])

    print(f"Input: {latest_report}")

    # Generate PDF
    exporter = PDFExporter()
    try:
        pdf_path = exporter.markdown_to_pdf(latest_report)
        print(f"✓ PDF generated: {pdf_path}")

        # Check file size
        file_size = os.path.getsize(pdf_path) / 1024  # KB
        print(f"  File size: {file_size:.1f} KB")

    except Exception as e:
        print(f"✗ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
