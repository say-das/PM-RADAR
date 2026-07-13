# Email Configuration Guide

**How to configure email recipients privately.**

---

## 🔐 Security First

Email addresses are now stored in a **gitignored file** to keep them private. This means:

✅ Your email addresses won't be committed to git  
✅ They won't appear in public repositories  
✅ Each developer can have their own recipient list

---

## 📝 Quick Setup

### Step 1: Create Recipients File

```bash
# Option A: Use setup script (recommended)
python3 scripts/setup_recipients.py

# Option B: Copy manually
cp config/recipients.yaml.example config/recipients.yaml
```

### Step 2: Add Your Email Addresses

Edit `config/recipients.yaml`:

```yaml
# Default sender
sender:
  name: "PM Radar Intelligence"
  email: "your-email@company.com"  # Must be verified in Brevo

# Topic-specific recipients
topics:
  fraud:
    - team-member1@company.com
    - team-member2@company.com
    - manager@company.com
  
  compliance:
    - compliance-team@company.com

# Global recipients (receive all reports)
global:
  - all-hands@company.com
```

### Step 3: Verify Sender Email

The sender email must be verified in Brevo:

1. Go to https://app.brevo.com/senders
2. Add your sender email
3. Verify via confirmation email

---

## 📧 Configuration Options

### Topic-Specific Recipients

Each topic can have its own recipient list:

```yaml
topics:
  fraud:
    - fraud-team@company.com
  
  product-intel:
    - product-team@company.com
  
  security:
    - security-team@company.com
```

When you run:
```bash
python3 scripts/run_v2_pipeline.py fraud --deliver
```

Only `fraud-team@company.com` will receive the report.

### Global Recipients

Some people should receive all reports:

```yaml
global:
  - ceo@company.com
  - vp-product@company.com
```

These recipients get reports from **all topics**.

### Multiple Recipients Per Topic

Add as many as needed:

```yaml
topics:
  fraud:
    - analyst1@company.com
    - analyst2@company.com
    - team-lead@company.com
    - manager@company.com
    - director@company.com
```

---

## 🔧 Loading Recipients in Code

If you're customizing the platform, use the recipients loader:

```python
from core.recipients_loader import get_recipients_loader

# Get loader
loader = get_recipients_loader()

# Get sender info
sender = loader.get_sender()
# Returns: {"name": "...", "email": "..."}

# Get recipients for a topic
recipients = loader.get_recipients_for_topic("fraud")
# Returns: ["email1@company.com", "email2@company.com", ...]

# Get all recipients
all_recipients = loader.get_all_recipients()
# Returns: {"fraud": [...], "compliance": [...]}
```

---

## 🚨 Troubleshooting

### Error: Recipients config not found

```
FileNotFoundError: Recipients config not found: config/recipients.yaml
```

**Solution:**
```bash
python3 scripts/setup_recipients.py
# Then edit config/recipients.yaml
```

### Email Not Sending

**Check these:**

1. **Sender email verified?**
   - Go to https://app.brevo.com/senders
   - Verify your sender email

2. **Brevo API key set?**
   ```bash
   echo $BREVO_API_KEY
   ```

3. **Recipients file exists?**
   ```bash
   ls -la config/recipients.yaml
   ```

4. **Valid email format?**
   - Must be `user@domain.com`
   - No spaces or special characters

---

## 📋 Migration from Old Config

If you have old configs with email addresses:

### From topic.yaml

**Old:**
```yaml
email:
  recipients:
    - user1@company.com
    - user2@company.com
```

**New:**
```yaml
email:
  recipients_from_config: true
```

Then add to `config/recipients.yaml`:
```yaml
topics:
  your-topic:
    - user1@company.com
    - user2@company.com
```

### From email-config.json

**Old:**
```json
{
  "sender": {
    "email": "sender@company.com"
  },
  "recipients": [
    {"email": "user@company.com"}
  ]
}
```

**New:** Add to `config/recipients.yaml`:
```yaml
sender:
  email: "sender@company.com"

topics:
  your-topic:
    - user@company.com
```

---

## 🔒 Security Best Practices

### ✅ Do This

- ✅ Use `config/recipients.yaml` (gitignored)
- ✅ Keep work emails in recipients config
- ✅ Verify sender email in Brevo
- ✅ Use descriptive sender name

### ❌ Don't Do This

- ❌ Put emails in `topic.yaml` (tracked by git)
- ❌ Commit `recipients.yaml` to git
- ❌ Use personal emails for sender
- ❌ Share your `recipients.yaml` file

---

## 📊 Example Configurations

### Small Team

```yaml
sender:
  name: "Product Intelligence"
  email: "intel@startup.com"

topics:
  fraud:
    - team@startup.com

global: []
```

### Large Organization

```yaml
sender:
  name: "Security Intelligence Team"
  email: "security-intel@bigcorp.com"

topics:
  fraud:
    - fraud-analysts@bigcorp.com
    - security-team@bigcorp.com
  
  compliance:
    - compliance@bigcorp.com
    - legal@bigcorp.com
  
  product-intel:
    - product-managers@bigcorp.com
    - engineering-leads@bigcorp.com

global:
  - vp-security@bigcorp.com
  - ciso@bigcorp.com
```

### Multiple Teams

```yaml
sender:
  name: "PM Radar"
  email: "pmradar@company.com"

topics:
  fraud:
    - fraud-team@company.com
    - security-ops@company.com
  
  security:
    - security-team@company.com
    - incident-response@company.com
  
  market-intel:
    - product-marketing@company.com
    - strategy@company.com

global:
  - leadership@company.com
```

---

## ✅ Verification Checklist

Before sending your first report:

- [ ] Created `config/recipients.yaml`
- [ ] Added sender email
- [ ] Added recipient emails for your topic
- [ ] Verified sender email in Brevo dashboard
- [ ] Set `BREVO_API_KEY` in `.env`
- [ ] Tested with `--deliver` flag

---

**Need Help?**

- Brevo Dashboard: https://app.brevo.com
- Brevo API Keys: https://app.brevo.com/settings/keys/api
- Main README: [../README.md](../README.md)
