# PM Radar MVP: Competitive Intelligence Agent
## 6-Week Implementation Plan

**Goal**: Launch platform + Competitive Intelligence Agent with 20-30 beta users

**Timeline**: Weeks 1-6
**Team**: 2 engineers (1 backend, 1 frontend) + 1 PM

---

## Week 1: Platform Foundation & Database

### Backend (3 days)
```sql
-- Core schema
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  plan TEXT DEFAULT 'starter',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  organization_id UUID REFERENCES organizations(id),
  role TEXT DEFAULT 'pm',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID REFERENCES organizations(id),
  name TEXT NOT NULL,
  product_name TEXT,
  product_description TEXT,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE competitors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id),
  name TEXT NOT NULL,
  website_url TEXT NOT NULL,
  priority TEXT DEFAULT 'medium',
  monitor_homepage BOOLEAN DEFAULT true,
  monitor_pricing BOOLEAN DEFAULT true,
  monitor_features BOOLEAN DEFAULT false,
  monitor_blog BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE competitor_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id),
  competitor_id UUID REFERENCES competitors(id),
  url TEXT NOT NULL,
  page_type TEXT NOT NULL,
  html_content TEXT,
  screenshot_url TEXT,
  metadata JSONB,
  captured_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE competitor_changes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id),
  competitor_id UUID REFERENCES competitors(id),
  change_type TEXT,
  significance INTEGER,
  title TEXT,
  summary TEXT,
  implications TEXT,
  diff_before TEXT,
  diff_after TEXT,
  reviewed_by UUID REFERENCES users(id),
  reviewed_at TIMESTAMPTZ,
  detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row-level security
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_changes ENABLE ROW LEVEL SECURITY;

-- Policies (workspace isolation)
CREATE POLICY workspace_isolation ON workspaces
  FOR ALL
  USING (organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ));
```

**Tasks:**
- [ ] Set up Supabase project
- [ ] Create database schema
- [ ] Set up row-level security policies
- [ ] Create API endpoints (Express/FastAPI)
  - [ ] POST /api/workspaces
  - [ ] GET /api/workspaces/:id
  - [ ] POST /api/competitors
  - [ ] GET /api/competitors/:workspace_id
  - [ ] DELETE /api/competitors/:id

### Frontend (2 days)
**Tasks:**
- [ ] Set up Next.js project with TypeScript
- [ ] Install dependencies (Tailwind, Clerk/Auth0, React Query)
- [ ] Create basic layouts
  - [ ] Navigation sidebar
  - [ ] Header with workspace switcher
  - [ ] Empty states
- [ ] Build authentication pages
  - [ ] Sign up
  - [ ] Login
  - [ ] Onboarding flow

**Deliverable**: Users can sign up and create a workspace

---

## Week 2: Competitor Configuration UI

### Frontend (4 days)
**Pages to build:**

#### 1. Workspace Settings Page
```tsx
/workspace/:id/settings

Components:
- WorkspaceProfile
  - Product name input
  - Description textarea
  - Save button

- CompetitorList
  - Table of competitors
  - Add competitor button
  - Edit/delete actions
```

#### 2. Add Competitor Modal
```tsx
<AddCompetitorModal>
  Fields:
  - Competitor name (text)
  - Website URL (text with validation)
  - Priority (select: high/medium/low)
  - Pages to monitor:
    [x] Homepage
    [x] Pricing page
    [ ] Features page
    [ ] Blog
  - Monitoring frequency (select: daily/twice-daily)
</AddCompetitorModal>
```

#### 3. Competitor Detail View
```tsx
/workspace/:id/competitors/:competitor_id

Sections:
- Competitor header (name, website, status)
- Configuration panel
- Activity timeline (placeholder for now)
- Detected changes (placeholder)
```

**Tasks:**
- [ ] Build workspace settings page
- [ ] Create competitor list component
- [ ] Build add/edit competitor modal
- [ ] Implement form validation
- [ ] Connect to backend APIs
- [ ] Add toast notifications (success/error)

**Deliverable**: Users can add 3-5 competitors with monitoring configuration

---

## Week 3: Web Scraping Infrastructure

### Backend (5 days)

#### 1. Scraping Service
```typescript
// services/scraper.ts
import { chromium } from 'playwright';

export class CompetitorScraper {
  async captureSnapshot(url: string) {
    const browser = await chromium.launch();
    const page = await browser.newPage();

    await page.goto(url, { waitUntil: 'networkidle' });

    const snapshot = {
      html: await page.content(),
      title: await page.title(),
      description: await page.$eval(
        'meta[name="description"]',
        el => el.getAttribute('content')
      ),
      screenshot: await page.screenshot({ fullPage: true })
    };

    await browser.close();
    return snapshot;
  }

  async detectChanges(oldHtml: string, newHtml: string) {
    // Text-based diff
    const diff = Diff.diffWords(oldHtml, newHtml);

    const changes = {
      additions: diff.filter(d => d.added).length,
      deletions: diff.filter(d => d.removed).length,
      changePercentage: this.calculateChangePercentage(diff)
    };

    return changes;
  }
}
```

#### 2. Snapshot Storage
```typescript
// services/storage.ts
export class SnapshotStorage {
  async store(workspace_id, competitor_id, snapshot) {
    // Store HTML in database
    await db.insert('competitor_snapshots', {
      workspace_id,
      competitor_id,
      html_content: snapshot.html,
      metadata: {
        title: snapshot.title,
        description: snapshot.description
      }
    });

    // Store screenshot in S3/Supabase storage
    const screenshotUrl = await this.uploadScreenshot(
      snapshot.screenshot,
      `${workspace_id}/${competitor_id}/${Date.now()}.png`
    );

    return screenshotUrl;
  }
}
```

#### 3. Scraping Orchestrator
```typescript
// jobs/scrape-competitors.ts
export async function scrapeCompetitors() {
  // Get all workspaces with active monitoring
  const workspaces = await db.query(`
    SELECT DISTINCT w.id, w.organization_id
    FROM workspaces w
    JOIN competitors c ON c.workspace_id = w.id
    WHERE c.monitor_homepage = true OR c.monitor_pricing = true
  `);

  for (const workspace of workspaces) {
    const competitors = await getCompetitorsForWorkspace(workspace.id);

    for (const competitor of competitors) {
      try {
        await scrapeCompetitor(workspace.id, competitor);
      } catch (error) {
        console.error(`Failed to scrape ${competitor.name}:`, error);
        // Continue with next competitor
      }
    }
  }
}
```

**Tasks:**
- [ ] Install Playwright and dependencies
- [ ] Build scraper service
- [ ] Implement snapshot storage
- [ ] Create scraping orchestrator
- [ ] Add error handling and retries
- [ ] Set up cron job (daily at 2am)
- [ ] Test with 5-10 real competitor websites

**Deliverable**: System can scrape competitor websites daily and store snapshots

---

## Week 4: Diff Detection & LLM Analysis

### Backend (5 days)

#### 1. Diff Analysis Engine
```typescript
// services/diff-analyzer.ts
import * as Diff from 'diff';
import pixelmatch from 'pixelmatch';

export class DiffAnalyzer {
  async analyzeChanges(oldSnapshot, newSnapshot) {
    // Text diff
    const textDiff = Diff.diffWords(
      this.stripHtml(oldSnapshot.html_content),
      this.stripHtml(newSnapshot.html_content)
    );

    const textChanges = {
      added: textDiff.filter(d => d.added).map(d => d.value),
      removed: textDiff.filter(d => d.removed).map(d => d.value),
      changePercentage: this.calculatePercentage(textDiff)
    };

    // Screenshot diff (if significant text changes)
    if (textChanges.changePercentage > 5) {
      const visualDiff = await this.compareScreenshots(
        oldSnapshot.screenshot_url,
        newSnapshot.screenshot_url
      );

      return { textChanges, visualDiff };
    }

    return { textChanges };
  }

  stripHtml(html: string): string {
    return html.replace(/<[^>]*>/g, '').trim();
  }
}
```

#### 2. LLM Analysis Service
```typescript
// services/llm-analyzer.ts
import Anthropic from '@anthropic-ai/sdk';

export class LLMAnalyzer {
  async analyzeChange(competitor, oldContent, newContent, diff) {
    const prompt = `You are a competitive intelligence analyst.

COMPETITOR: ${competitor.name}
URL: ${competitor.url}

CONTENT BEFORE:
${this.truncate(oldContent, 2000)}

CONTENT AFTER:
${this.truncate(newContent, 2000)}

CHANGES DETECTED:
Added: ${diff.added.join('\n')}
Removed: ${diff.removed.join('\n')}

Analyze this change and provide:

1. CHANGE TYPE (choose one):
   - feature_launch (new product feature announced)
   - pricing_change (pricing updated)
   - messaging_shift (marketing copy changed)
   - design_update (visual/layout change)
   - blog_post (new content published)
   - trivial (minor update, not significant)

2. SIGNIFICANCE (1-10 scale):
   1-3: Trivial (typo fixes, minor copy edits)
   4-6: Moderate (new blog post, small feature)
   7-8: Important (major feature, pricing change)
   9-10: Critical (major product launch, significant pivot)

3. SUMMARY (2-3 sentences):
   What changed and why it matters.

4. IMPLICATIONS (2-3 bullets):
   What this means for our product strategy.

5. RECOMMENDED ACTIONS (1-2 bullets):
   Specific steps we should consider.

Format your response as JSON:
{
  "change_type": "...",
  "significance": 7,
  "summary": "...",
  "implications": ["...", "..."],
  "recommended_actions": ["...", "..."]
}`;

    const response = await this.claude.messages.create({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 1000,
      messages: [{ role: 'user', content: prompt }]
    });

    return JSON.parse(response.content[0].text);
  }
}
```

#### 3. Change Detection Pipeline
```typescript
// jobs/detect-changes.ts
export async function detectChanges() {
  const recentSnapshots = await db.query(`
    SELECT
      s1.id as new_snapshot_id,
      s1.workspace_id,
      s1.competitor_id,
      s1.html_content as new_html,
      s2.html_content as old_html,
      c.name as competitor_name,
      c.website_url
    FROM competitor_snapshots s1
    LEFT JOIN LATERAL (
      SELECT html_content
      FROM competitor_snapshots s2
      WHERE s2.competitor_id = s1.competitor_id
        AND s2.captured_at < s1.captured_at
      ORDER BY s2.captured_at DESC
      LIMIT 1
    ) s2 ON true
    JOIN competitors c ON c.id = s1.competitor_id
    WHERE s1.captured_at > NOW() - INTERVAL '2 hours'
      AND s2.html_content IS NOT NULL
  `);

  for (const snapshot of recentSnapshots) {
    // Run diff analysis
    const diff = await diffAnalyzer.analyzeChanges(
      { html_content: snapshot.old_html },
      { html_content: snapshot.new_html }
    );

    // Skip if no significant changes
    if (diff.textChanges.changePercentage < 2) continue;

    // Run LLM analysis
    const analysis = await llmAnalyzer.analyzeChange(
      { name: snapshot.competitor_name, url: snapshot.website_url },
      snapshot.old_html,
      snapshot.new_html,
      diff.textChanges
    );

    // Skip trivial changes
    if (analysis.significance < 4) continue;

    // Store detected change
    await db.insert('competitor_changes', {
      workspace_id: snapshot.workspace_id,
      competitor_id: snapshot.competitor_id,
      change_type: analysis.change_type,
      significance: analysis.significance,
      title: this.generateTitle(analysis),
      summary: analysis.summary,
      implications: JSON.stringify(analysis.implications),
      diff_before: snapshot.old_html,
      diff_after: snapshot.new_html,
      detected_at: new Date()
    });

    // Send notification if high priority
    if (analysis.significance >= 7) {
      await notificationService.sendAlert(snapshot.workspace_id, analysis);
    }
  }
}
```

**Tasks:**
- [ ] Build diff analyzer
- [ ] Implement LLM analysis service
- [ ] Create change detection pipeline
- [ ] Test with sample competitor changes
- [ ] Tune significance thresholds
- [ ] Add job scheduling (runs after scraping)

**Deliverable**: System detects meaningful changes and generates insights

---

## Week 5: Dashboard & Notifications

### Frontend (4 days)

#### 1. Competitive Intelligence Dashboard
```tsx
// pages/workspace/[id]/competitive-intel.tsx

export default function CompetitiveIntelDashboard() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1>Competitive Intelligence</h1>
        <button>Run Manual Check</button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <select>
          <option>All Competitors</option>
          {competitors.map(c => <option>{c.name}</option>)}
        </select>
        <select>
          <option>All Priorities</option>
          <option>High Priority Only</option>
          <option>Medium+</option>
        </select>
        <select>
          <option>Last 7 Days</option>
          <option>Last 30 Days</option>
          <option>All Time</option>
        </select>
      </div>

      {/* Activity Feed */}
      <div className="space-y-4">
        {changes.map(change => (
          <ChangeCard key={change.id} change={change} />
        ))}
      </div>
    </div>
  );
}
```

#### 2. Change Card Component
```tsx
function ChangeCard({ change }) {
  const priorityColors = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800'
  };

  return (
    <div className="border rounded-lg p-4 hover:shadow-lg">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <span className={`badge ${priorityColors[change.priority]}`}>
            {change.significance >= 7 ? '🔴 HIGH' :
             change.significance >= 4 ? '🟡 MEDIUM' : '🟢 LOW'}
          </span>
          <h3 className="font-semibold mt-2">{change.title}</h3>
          <p className="text-sm text-gray-500">
            {change.competitor_name} • {formatDate(change.detected_at)}
          </p>
        </div>

        <button onClick={() => markAsReviewed(change.id)}>
          Mark as Reviewed
        </button>
      </div>

      {/* Summary */}
      <p className="mt-3">{change.summary}</p>

      {/* Implications */}
      {change.implications && (
        <div className="mt-3">
          <strong>Implications:</strong>
          <ul className="list-disc ml-5 mt-1">
            {JSON.parse(change.implications).map((imp, i) => (
              <li key={i}>{imp}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="mt-3 flex gap-2">
        <button onClick={() => viewDiff(change)}>
          View Changes
        </button>
        <button onClick={() => viewCompetitor(change.competitor_id)}>
          View Competitor
        </button>
      </div>
    </div>
  );
}
```

#### 3. Diff Viewer Modal
```tsx
function DiffViewerModal({ change, isOpen, onClose }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <div className="flex h-[600px]">
        {/* Before */}
        <div className="w-1/2 p-4 border-r">
          <h3 className="font-semibold mb-2">Before</h3>
          <div className="prose overflow-auto h-full">
            <ReactDiffViewer
              oldValue={change.diff_before}
              newValue={change.diff_after}
              splitView={true}
            />
          </div>
        </div>

        {/* After */}
        <div className="w-1/2 p-4">
          <h3 className="font-semibold mb-2">After</h3>
          <div className="prose overflow-auto h-full">
            {/* Rendered after content */}
          </div>
        </div>
      </div>
    </Modal>
  );
}
```

### Backend (1 day)

#### Notification Service
```typescript
// services/notifications.ts
import { Resend } from 'resend';
import { WebClient } from '@slack/web-api';

export class NotificationService {
  async sendDailyDigest(workspace_id: string) {
    const changes = await db.query(`
      SELECT *
      FROM competitor_changes
      WHERE workspace_id = $1
        AND detected_at > NOW() - INTERVAL '24 hours'
      ORDER BY significance DESC, detected_at DESC
    `, [workspace_id]);

    if (changes.length === 0) return;

    const user = await getWorkspaceOwner(workspace_id);

    // Email digest
    await this.sendEmail(user.email, {
      subject: `PM Radar: ${changes.length} competitive updates`,
      html: this.renderDigest(changes)
    });

    // Slack notification (if configured)
    if (user.slack_webhook) {
      await this.sendSlack(user.slack_webhook, changes);
    }
  }

  async sendAlert(workspace_id: string, change) {
    // Real-time alert for high-priority changes
    const user = await getWorkspaceOwner(workspace_id);

    await this.sendEmail(user.email, {
      subject: `🚨 ${change.competitor_name} - Important Update`,
      html: this.renderAlert(change)
    });
  }
}
```

**Tasks:**
- [ ] Build competitive intelligence dashboard
- [ ] Create change card component
- [ ] Implement diff viewer modal
- [ ] Add mark as reviewed functionality
- [ ] Build notification service
- [ ] Design email templates
- [ ] Set up Slack integration
- [ ] Test notification delivery

**Deliverable**: Users can view changes in dashboard and receive notifications

---

## Week 6: Polish, Testing & Beta Launch

### Testing (2 days)
**Tasks:**
- [ ] End-to-end testing
  - [ ] User signup → workspace creation → add competitors
  - [ ] Scraping pipeline execution
  - [ ] Change detection and analysis
  - [ ] Dashboard display
  - [ ] Notifications delivery
- [ ] Load testing
  - [ ] 50 workspaces with 5 competitors each
  - [ ] Concurrent scraping
  - [ ] Database performance
- [ ] Error handling review
  - [ ] Failed scrapes
  - [ ] LLM API errors
  - [ ] Notification failures

### Polish (2 days)
**Tasks:**
- [ ] UI/UX improvements
  - [ ] Loading states
  - [ ] Empty states
  - [ ] Error messages
  - [ ] Toast notifications
- [ ] Onboarding flow
  - [ ] Welcome screen
  - [ ] Sample competitors pre-populated
  - [ ] Interactive tour
  - [ ] First change notification
- [ ] Documentation
  - [ ] Help center (in-app)
  - [ ] Video walkthrough
  - [ ] FAQ page

### Beta Launch (1 day)
**Tasks:**
- [ ] Create beta invite list (20-30 users)
- [ ] Send personalized invites
- [ ] Set up user feedback form
- [ ] Schedule weekly check-ins
- [ ] Monitor usage analytics
- [ ] Create support channel (Slack/Discord)

**Deliverable**: 20-30 beta users actively using Competitive Intelligence Agent

---

## Success Criteria (Week 6)

### Technical Metrics
- [ ] 95%+ scraping success rate
- [ ] <5% false positives (trivial changes marked as significant)
- [ ] <1 hour detection latency (from change to notification)
- [ ] 99% uptime for platform

### User Engagement Metrics
- [ ] 80%+ of beta users add 3+ competitors
- [ ] 60%+ open daily digest emails
- [ ] 40%+ mark at least one change as "reviewed"
- [ ] 30%+ enable Slack notifications

### Qualitative Validation
- [ ] 5+ users say "I can't live without this"
- [ ] At least 2 stories of "caught competitor launch early"
- [ ] 70%+ would recommend to another PM
- [ ] Clear feature requests for agent #2

---

## Tech Stack Summary

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Query (data fetching)
- Clerk or Auth0 (authentication)

**Backend:**
- Node.js + Express OR Python + FastAPI
- Supabase (PostgreSQL + Auth + Storage)
- Playwright (web scraping)
- Anthropic Claude API (LLM analysis)

**Infrastructure:**
- Vercel (frontend hosting)
- Railway or Render (backend hosting)
- Supabase (database + storage)
- Resend (email)
- Cron-job.org or built-in cron (scheduling)

**Monitoring:**
- Sentry (error tracking)
- PostHog (product analytics)
- Supabase logs (database queries)

---

## Budget Estimate (Monthly, at scale)

**Infrastructure:**
- Supabase Pro: $25/month
- Vercel Pro: $20/month
- Railway: $20/month
- Total: **$65/month**

**Per Workspace Costs:**
- Claude API (Haiku): ~$5-10/month
- Resend (emails): ~$1/month
- Storage (screenshots): ~$2/month
- Total: **~$10/workspace/month**

**At 20 workspaces:** $65 + ($10 × 20) = **$265/month**
**At $99/workspace pricing:** $99 × 20 = **$1,980/month revenue**
**Gross margin:** 87%

---

## Risk Mitigation

### Risk: Websites block scraping
**Mitigation:**
- Rotate user agents
- Use residential proxies if needed
- Add delays between requests (10-30 sec)
- Fallback: Manual URL submission by user

### Risk: LLM misclassifies changes
**Mitigation:**
- Human review first 50 analyses
- A/B test different prompts
- Add confidence scores
- Allow user feedback (thumbs up/down)

### Risk: Low user engagement
**Mitigation:**
- Send "first change detected" email immediately
- Weekly progress emails ("3 changes detected this week")
- Gamification (streak counter)
- Personal onboarding calls with first 10 users

### Risk: Too many false positives
**Mitigation:**
- Tune significance threshold (start at 6+)
- Add "smart filtering" (ignore cookie banners, ads)
- Let users configure alert thresholds
- Learn from user feedback (ML model later)

---

## Post-Launch (Week 7+)

### Iteration Plan
**Week 7: User Feedback & Iteration**
- Conduct 10 user interviews
- Analyze usage patterns
- Identify pain points
- Prioritize improvements

**Week 8: Quick Wins**
- Fix top 5 bugs
- Add most requested features
- Improve LLM prompt based on feedback
- Optimize scraping reliability

**Week 9-10: Decision Point**
- Are users engaged daily/weekly?
- Would they pay $99/month?
- What's missing?
- **Decision:** Build agent #2 OR improve agent #1

---

**Document Owner:** Engineering Lead
**Last Updated:** 2026-03-20
**Status:** Ready for execution
