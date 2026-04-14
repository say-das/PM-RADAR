# PM Radar Report Design Guide

## Overview
This document describes the visual design system used for PM Radar intelligence reports.

## Design Philosophy
- **Twilio-branded**: Bold use of Twilio Red (#F22F46) and Blue (#0263E0)
- **A4 paper layout**: 210mm × 297mm with generous margins (40px/60px)
- **Compact spacing**: Reduced whitespace for information density
- **Clear hierarchy**: Color-coded sections with proper font weights

## Color System

### Primary Colors
- **Twilio Red** (`#F22F46`): H1 titles, executive summary accents, table headers, glossary terms
- **Twilio Blue** (`#0263E0`): Primary links, citations
- **Twilio Blue 60** (`#0D61D8`): H2 section headers
- **Twilio Blue 10** (`#E1EFFC`): Background tints for callouts

### Text Colors (Gray Scale)
- **Gray 100** (`#121C2D`): Darkest - reserved for maximum emphasis
- **Gray 90** (`#18222E`): Main body text, H3 headers
- **Gray 80** (`#1F2933`): Section labels (e.g., "Executive Summary:")
- **Gray 70** (`#3E4C59`): Secondary text emphasis
- **Gray 60** (`#606B85`): Primary body text color
- **Gray 50** (`#8891AA`): De-emphasized text (sources, italics)
- **Gray 40** (`#C4C7D1`): List markers
- **Gray 30** (`#D9DBE5`): Borders, dividers
- **Gray 20** (`#E8EAED`): Subtle borders
- **Gray 10** (`#F4F5F6`): Background tints

## Typography

### Font Family
- **Primary**: Inter (Google Fonts)
- **Fallbacks**: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
- **Code**: 'SF Mono', 'Monaco', 'Consolas', monospace

### Type Scale
- **H1**: 32px, 700 weight, Red color, 1.1 line-height
- **H2**: 24px, 700 weight, Blue-60 color, 1.2 line-height
- **H3**: 18px, 600 weight, Gray-90 color, 1.3 line-height
- **Body**: 14px, 400 weight, Gray-60 color, 1.5 line-height
- **Citations**: 10px, 600 weight, superscript
- **Sources**: 12px, 400 weight, Gray-50 color

### Visual Hierarchy Rules
1. **H1 border**: 3px solid red bottom border
2. **Only first `<strong>` in list items is bold**: Creates proper hierarchy
3. **Remaining bold text**: Treated as 400 weight to avoid visual noise
4. **Section labels**: 600 weight, Gray-80
5. **List markers**: Gray-40, normal weight

## Layout

### Container
```css
max-width: 210mm;        /* A4 width */
padding: 40px 60px;      /* Generous margins */
background: white;
box-shadow: 0 2px 8px rgba(0,0,0,0.1);
min-height: 297mm;       /* A4 height */
```

### Body
```css
background-color: #f5f5f5;  /* Paper background effect */
padding: 20px;
```

### Spacing Scale
- **Sections**: 24px top, 8px bottom margin
- **Paragraphs**: 6px vertical margin
- **Lists**: 8px vertical margin, 4px per item
- **List indentation**: 24px
- **Horizontal rules**: 16px vertical margin

## Special Elements

### Executive Summary Box
- Background: Blue-10 (`#E1EFFC`)
- Border: 4px solid red on left
- Padding: 16px 20px
- Border radius: 6px
- Bold numbers in red

### Citations
- **Format**: Short notation (A1, A2, R1, R2 instead of ARTICLE_1, REDDIT_1)
- **Inline**: 10px, superscript, blue links
- **Hover**: Changes to red with underline
- **Clickable**: Links to sources section with `#A1`, `#R1` anchors
- **Target highlight**: Light blue background when clicked
- **Example**: `[A1]` links to article 1, `[R5]` links to Reddit post 5

### Blockquotes
- Border: 4px solid blue on left
- Background: Blue-10
- Padding: 10px 16px
- Italic text

### Code Blocks
- Background: Gray-10
- Border: 1px solid Gray-20
- Padding: 16px
- Border radius: 8px

### Tables
- Headers: Red background, white text
- Row hover: Blue-10 background
- Borders: Gray-30
- Padding: 8px 10px

### Glossary Terms
- Term name: Red, 700 weight
- Definition: Gray-60, 400 weight

### Sources List
- Font size: 12px
- Color: Gray-50
- Scroll margin: 20px for smooth navigation
- Target state: Blue-10 background with padding

## Print Optimization

```css
@media print {
    body {
        background: white;
    }
    .container {
        box-shadow: none;
        max-width: 100%;
    }
}
```

### Print Settings
- Page size: Letter (8.5" × 11")
- Margins: 0.75in top/bottom, 1in left/right
- Orphans/widows: 3 lines minimum
- Page breaks: Avoid after headings

## Implementation Files

1. **PDF Exporter**: `scripts/deliver/pdf_exporter.py`
   - Contains `_get_css()` method with complete stylesheet
   - Contains `_add_citation_links()` for post-processing

2. **Template**: `templates/report-template.html`
   - Standalone HTML template with full CSS

3. **Current Report**: `data/reports/YYYY-MM-DD.html`
   - Generated reports automatically use this design

## Future Maintenance

When updating the design:
1. Update CSS in `pdf_exporter.py` `_get_css()` method
2. Update template in `templates/report-template.html`
3. Test with a sample report
4. Update this guide if adding new design elements

## Design Principles

1. **Information density**: Compact spacing for maximum content per page
2. **Scanability**: Clear visual hierarchy with color coding
3. **Professional**: Clean Twilio branding without being overwhelming
4. **Readable**: Proper contrast ratios and line heights
5. **Interactive**: Clickable citations and smooth scrolling
6. **Print-ready**: Optimized for PDF export and printing

## Citation Format Reference

### Short Citation Notation
Reports use a compact citation format for better readability:

- **Articles**: `[A1]`, `[A2]`, `[A3]`, etc.
- **Reddit**: `[R1]`, `[R2]`, `[R3]`, etc.

### Technical Implementation
The report generator (`main.py`) automatically converts:
- `[ARTICLE_1]` → `[A1]`
- `[ARTICLE_12]` → `[A12]`
- `[REDDIT_1]` → `[R1]`
- `[REDDIT_5]` → `[R5]`

The PDF exporter (`pdf_exporter.py`) then:
1. Converts inline citations to clickable links: `[A1]` → `<a href="#A1">[A1]</a>`
2. Adds anchor IDs to source list items: `<li id="A1">[A1]: ...`

## Version History

- **2026-04-08**: Initial design with Twilio red branding, A4 layout, compact spacing
- **2026-04-08**: Added clickable citations with 10px font size
- **2026-04-08**: Switched to short citation format (A1, R1 instead of ARTICLE_1, REDDIT_1)
