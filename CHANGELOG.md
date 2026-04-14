# Changelog

All notable changes to PM Radar are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - 2026-04-10

### Added
- **Commsrisk RSS feed** - Active telecom fraud news source (3-4 articles/week)
- **Globe Teleservices RSS feed** - A2P SMS fraud and network security content
- **Source category prioritization** - Articles from telecom_fraud sources automatically categorized as telecom
- **Enhanced telecom keywords** - Added 15+ keywords: SMS blaster, scam block, phone scam, voip fraud, etc.
- **Project structure reorganization** - Proper folder structure for git upload
- **Comprehensive documentation** - Updated README, created docs index, setup guides

### Changed
- **Categorization logic** - Source category now takes priority over keyword matching
- **Telecom keywords refined** - Removed overly broad terms (email, call, account takeover)
- **Documentation structure** - Moved docs to organized folders (setup/, architecture/, history/)
- **.gitignore updated** - Better exclusion rules for runtime data and cache files

### Fixed
- **Missing Telecom Fraud section** - CFCA articles were outside 7-day window
- **GSMA feed removed** - Feed broken since 2022, replaced with active Commsrisk
- **Citation format issues** - Fixed comma-separated citations in Reddit analysis
- **Missing Reddit citations** - R11-R15 were missing from Sources section

### Removed
- GSMA Security RSS feed (broken since 2022)
- Test and cache files from data/raw/
- Root-level planning documents (moved to docs/history/)

## [1.0.0] - 2026-04-09

### Added
- **Reddit Community separate section** - Reddit discussions analyzed separately from fraud categories
- **Citation-Sources synchronization** - Citations now properly mapped to Sources section
- **Reddit comments in analysis** - Top 10 comments per post included in GPT-4o analysis
- **Trending concerns identification** - Groups similar issues from Reddit discussions
- **Community sentiment analysis** - Overall sentiment (Frustrated/Neutral/Positive)
- **Competitor mentions tracking** - Identifies alternatives users discuss (Infobip, Vonage, etc.)

### Changed
- **Reddit posts limit increased** - From 10 to 15 posts for analysis
- **MAX_REDDIT_POSTS_FOR_ANALYSIS constant** - Single source of truth for post limits
- **Trending concerns formatting** - Removed numbered lists, use bold headings instead
- **Citation regex enhanced** - Handles comma-separated citations from GPT-4o

### Fixed
- **Broken Reddit citations** - R14 and other citations missing from Sources
- **Citation format in Key Insights** - Plain text `[REDDIT_2, REDDIT_14]` now converts to clickable links
- **Numbered list rendering** - All topics showing as "1." fixed by removing list format
- **Extra commas between citations** - Cleaned up `[\[R2\]](#r2), [\[R14\]](#r14)` formatting

## [0.9.0] - 2026-04-06

### Added
- **RSS feed collection** - 14 sources including CISA, Unit 42, BleepingComputer, Krebs
- **Reddit social listening** - Collects posts and comments from r/twilio
- **GPT-4o content analysis** - Categorizes articles, generates summaries
- **Email delivery** - HTML emails via Brevo/SendInBlue
- **GitHub Actions automation** - Weekly runs every Monday 6am UTC
- **HTML/PDF export** - Print-ready reports
- **Citation system** - Inline citations with Sources bibliography
- **Glossary generation** - Technical term definitions

### Features
- Collects 30+ articles weekly from security and fraud sources
- Analyzes 25 Reddit posts with sentiment analysis
- Categorizes content: Telecom Fraud, General Fraud, Competitive Intelligence
- Executive summaries with top threats and trends
- Regulatory changes and immediate attention items
- Professional HTML email formatting

## [0.1.0] - 2026-03-20

### Added
- Initial project structure
- Basic RSS collector proof of concept
- OpenAI integration for summarization
- Configuration files for sources

---

## Version Numbering

- **Major version (X.0.0)** - Breaking changes, major features
- **Minor version (0.X.0)** - New features, non-breaking changes
- **Patch version (0.0.X)** - Bug fixes, documentation updates

## Categories

- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements
