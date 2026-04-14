# PM Radar Documentation

Complete documentation for the PM Radar automated intelligence system.

## Setup Guides

**Getting started with PM Radar:**

- [**Complete Setup Guide**](setup/setup-guide.md) - Full installation and configuration
- [**Email Configuration**](setup/email-setup-guide.md) - Setting up Brevo email delivery
- [**Reddit Configuration**](setup/reddit-config-guide.md) - Reddit API setup and configuration

## Architecture & Design

**Understanding how PM Radar works:**

- [**Agent Directory**](architecture/AGENTS.md) - Overview of AI agents in the system
- [**Design Guide**](architecture/DESIGN_GUIDE.md) - System architecture and design principles

## Feature Documentation

**Detailed feature explanations:**

- [**Citation-Sources Synchronization**](citation-sources-sync.md) - How citations are mapped to sources
- [**Reddit Community Section**](reddit-community-section.md) - Separate Reddit analysis feature
- [**Reddit Comments Enhancement**](reddit-enhancement-summary.md) - Including comments in analysis
- [**OpenAI Invocation Strategy**](openai-invocation-strategy.md) - GPT-4o usage patterns
- [**Competitor Scanning Guide**](competitor-scanning-guide.md) - Competitor content collection

## Development History

**Project evolution and changes:**

Located in [`history/`](history/) folder:
- [**Product Proposal**](history/product-research-automation-proposal.md) - Original project proposal
- [**PR-FAQ**](history/pr-faq-pm-radar.md) - Product press release and FAQ
- [**MVP Implementation**](history/mvp-implementation.md) - MVP development details
- [**Project Plan**](history/plan.md) - Original project plan
- [**Changes Log**](history/CHANGES.md) - Development changes
- [**Technical Debt**](history/TECH_DEBT.md) - Known technical debt
- [**Session Summary**](history/SESSION_SUMMARY.md) - Development session notes

## Quick Links

- [Main README](../README.md) - Project overview
- [CHANGELOG](../CHANGELOG.md) - Version history
- [Configuration Files](../config/) - RSS sources, Reddit config, email settings

## Getting Help

**Common issues:**

1. **No articles collected?**
   - Check RSS feed availability
   - Verify API keys in `.env`
   - See [Setup Guide](setup/setup-guide.md)

2. **Citations broken?**
   - See [Citation-Sources Sync](citation-sources-sync.md)

3. **Email not sending?**
   - See [Email Setup Guide](setup/email-setup-guide.md)

4. **Reddit errors?**
   - See [Reddit Config Guide](setup/reddit-config-guide.md)

## Contributing

When adding new features or documentation:

1. Update relevant documentation
2. Add entry to [CHANGELOG](../CHANGELOG.md)
3. Update this index if adding new docs
4. Test locally before committing

## Documentation Standards

- Use markdown for all documentation
- Include code examples where relevant
- Add links to related docs
- Keep examples up to date
- Use clear section headings
