# Email Delivery Setup Guide

## Overview
PM Radar uses Brevo (formerly Sendinblue) to send weekly intelligence digest emails.

---

## Setup Steps

### 1. Get Brevo API Key

1. Sign up for Brevo: https://app.brevo.com/account/register
2. Go to: https://app.brevo.com/settings/keys/api
3. Create a new API key (v3)
4. Copy the key (starts with `xkeysib-`)

**Free Tier:** 300 emails/day (more than enough for weekly digests)

---

### 2. Configure Environment

Add to `.env` file:
```bash
BREVO_API_KEY=xkeysib-your-actual-key-here
```

---

### 3. Configure Recipients

Edit `config/email-config.json`:

```json
{
  "sender": {
    "email": "noreply@yourdomain.com",
    "name": "PM Radar"
  },
  "recipients": [
    {
      "email": "your-email@example.com",
      "name": "Your Name"
    },
    {
      "email": "teammate@example.com",
      "name": "Teammate Name"
    }
  ],
  "subject_template": "PM Radar Weekly Intelligence Digest - {date}"
}
```

**Important:**
- Use a verified sender email in Brevo
- Add multiple recipients by adding more objects to the array

---

### 4. Verify Sender Email

Brevo requires sender email verification:

1. Go to: https://app.brevo.com/senders
2. Add your sender email address
3. Verify via email confirmation link

---

## Testing Email Delivery

### Test Standalone
```bash
python -m scripts.deliver.email_sender
```

This will:
- Load the most recent report from `data/reports/`
- Convert markdown to HTML
- Send via Brevo API
- Show message ID on success

### Test Full Pipeline
```bash
python -m scripts.main
```

The pipeline will:
1. Collect data (RSS + Reddit)
2. Analyze with GPT-4o
3. Generate report
4. **Send email automatically**

---

## Email Features

### HTML Conversion
- Markdown report is automatically converted to styled HTML
- Preserves formatting: headings, lists, bold, links
- Mobile-responsive design
- Professional styling

### Email Structure
```
Subject: PM Radar Weekly Intelligence Digest - 2026-04-06

Body:
- Executive Summary
- Telecom Fraud Digest
  - Executive Summary
  - Top Threats & Trends
  - Regulatory Changes
  - Immediate Attention Required
- General Fraud & Security Digest
  - (same sections)
```

---

## Troubleshooting

### Error: "Brevo API key not found"
**Solution:** Add `BREVO_API_KEY` to `.env` file

### Error: "Sender email not verified"
**Solution:** Verify sender email in Brevo dashboard

### Error: "API key invalid"
**Solution:**
- Check for typos in `.env`
- Regenerate API key in Brevo dashboard
- Make sure you're using v3 API key (starts with `xkeysib-`)

### Email not received
**Check:**
1. Spam folder
2. Recipient email is correct in `config/email-config.json`
3. Brevo dashboard for delivery status
4. API response shows `"success": true`

---

## Cost

**Brevo Free Tier:**
- 300 emails/day
- Unlimited contacts
- Perfect for PM Radar (4 emails/month for weekly digests)

**Pricing if scaling:**
- Lite: $25/month (10K emails)
- Premium: $65/month (20K emails)

---

## GitHub Actions Integration

Email delivery works automatically in GitHub Actions:

1. Add `BREVO_API_KEY` to GitHub Secrets
2. Weekly workflow runs and sends emails
3. No manual intervention needed

---

## Security Notes

- API key stored in `.env` (gitignored)
- Never commit API keys to repository
- Use GitHub Secrets for CI/CD
- Brevo uses TLS encryption for email delivery

---

## Next Steps

1. ✅ Add Brevo API key to `.env`
2. ✅ Update `config/email-config.json` with your emails
3. ✅ Verify sender email in Brevo
4. ✅ Test: `python -m scripts.deliver.email_sender`
5. ✅ Run full pipeline: `python -m scripts.main`

---

**Questions?** Check Brevo docs: https://developers.brevo.com/docs
