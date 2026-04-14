# Git Upload Checklist

Final checklist before uploading PM Radar to git repository.

## ✅ Completed Tasks

### Project Structure
- [x] Reorganized folder structure
  - [x] Moved planning docs to `docs/history/`
  - [x] Moved architecture docs to `docs/architecture/`
  - [x] Moved setup guides to `docs/setup/`
  - [x] Created documentation index at `docs/README.md`

### Files Cleaned Up
- [x] Removed test files from `data/raw/`
- [x] Added `.gitkeep` files for empty directories
- [x] Created `data/README.md` to document data structure

### Documentation Updated
- [x] **README.md** - Complete project overview with:
  - Quick start guide
  - Configuration instructions
  - Project structure diagram
  - Feature list
  - Troubleshooting section
  - Cost estimates
- [x] **CHANGELOG.md** - Version history (v1.1.0, v1.0.0, v0.9.0)
- [x] **docs/README.md** - Documentation index
- [x] **.env.example** - Updated with all required API keys and comments

### Configuration Files
- [x] All config files verified and up to date:
  - [x] `config/rss-sources.json` - 14 RSS feeds (including Commsrisk)
  - [x] `config/reddit-config.json` - Reddit configuration
  - [x] `config/email-config.json` - Email settings
  - [x] `config/competitors.json` - Competitor list

### .gitignore
- [x] Updated to exclude:
  - [x] Secrets (.env, *.key)
  - [x] Python artifacts (__pycache__, *.pyc)
  - [x] Virtual environments (venv/, env/)
  - [x] IDE files (.vscode/, .idea/)
  - [x] OS files (.DS_Store)
  - [x] Runtime data (data/raw/*.json, data/reports/*)
  - [x] Logs and backups

## 📋 Pre-Upload Verification

Before running `git init` and pushing to remote, verify:

### 1. Sensitive Data Check

```bash
# Make sure .env is NOT tracked
cat .gitignore | grep "\.env"

# Verify no API keys in tracked files
grep -r "sk-" . --exclude-dir=venv --exclude-dir=.git --exclude=".env"
grep -r "xkeysib-" . --exclude-dir=venv --exclude-dir=.git --exclude=".env"
```

### 2. Structure Verification

```bash
# Check project structure
tree -L 2 -I 'venv|__pycache__|*.pyc|.DS_Store'
```

Expected structure:
```
.
├── config/              ← Configuration files
├── data/                ← Runtime data (mostly gitignored)
├── docs/                ← Documentation
│   ├── setup/
│   ├── architecture/
│   └── history/
├── scripts/             ← Source code
│   ├── collect/
│   ├── analyze/
│   └── deliver/
├── templates/           ← HTML templates
├── tests/               ← Tests (empty for now)
├── .gitignore
├── .env.example
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

### 3. Documentation Links Check

Verify all links in README.md work:
```bash
# Check for broken relative links
grep -o '\[.*\](.*\.md)' README.md
```

### 4. Dependencies Check

```bash
# Verify requirements.txt is up to date
pip freeze | grep -E 'openai|feedparser|praw|requests|markdown|weasyprint'
```

## 🚀 Git Upload Steps

Once all checks pass:

### 1. Initialize Repository

```bash
git init
git add .
git status  # Review what will be committed
```

**Verify gitignore is working:**
- `.env` should NOT appear in `git status`
- `data/raw/*.json` should NOT appear
- `venv/` should NOT appear

### 2. Initial Commit

```bash
git commit -m "Initial commit: PM Radar v1.1.0

- Automated intelligence digest system
- RSS feeds: 14 sources (Commsrisk, CFCA, CISA, etc.)
- Reddit social listening (r/twilio)
- GPT-4o content analysis
- Email delivery via Brevo
- GitHub Actions automation

Features:
- Telecom fraud digest
- General fraud & security digest
- Reddit community sentiment analysis
- Professional HTML/PDF reports
- Citation system with sources
"
```

### 3. Add Remote and Push

```bash
# Add remote repository
git remote add origin <your-repo-url>

# Push to main branch
git branch -M main
git push -u origin main
```

### 4. Configure GitHub Secrets

In repo Settings → Secrets → Actions, add:

```
OPENAI_API_KEY=<your-key>
REDDIT_CLIENT_ID=<your-id>
REDDIT_CLIENT_SECRET=<your-secret>
BREVO_API_KEY=<your-key>
```

### 5. Verify GitHub Actions

- Check `.github/workflows/weekly-collection.yml` runs successfully
- Verify email is sent on first run
- Check logs for any errors

## 🔐 Security Notes

**Files that MUST stay secret:**
- `.env` - Contains actual API keys
- `config/secrets/` - Any future secret files

**Public repository considerations:**
- If making repo public, review all docs for internal company references
- Remove any sensitive customer data
- Consider making repo private initially

## 📝 Post-Upload Tasks

After successful upload:

1. [ ] Update repository description and topics
2. [ ] Add README badges (build status, license)
3. [ ] Test GitHub Actions workflow
4. [ ] Share repo link with team
5. [ ] Document contribution guidelines (if needed)

## ✨ Project Ready for Git!

All tasks completed. Project is organized, documented, and ready for version control.

**Next step:** Follow "Git Upload Steps" section above.
