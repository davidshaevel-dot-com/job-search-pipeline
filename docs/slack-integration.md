# Slack Integration Guide

This guide explains how to set up Slack integration for the job search pipeline, including notifications and manual triggers.

## Overview

The Slack integration provides:
- **Notifications:** Pipeline status updates, summaries, and high-score alerts
- **Triggers:** Manual pipeline runs via Slack commands
- **Reports:** Summaries of discovered opportunities

## Setup

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app: "Job Search Pipeline"
4. Select your workspace
5. Click "Create App"

### 2. Configure Incoming Webhooks

1. In your app settings, go to "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" to On
3. Click "Add New Webhook to Workspace"
4. Select the channel (e.g., `#job-search`)
5. Copy the Webhook URL
6. Add to GitHub Secrets as `SLACK_WEBHOOK_URL`

### 3. Configure Slash Commands (Optional)

1. In your app settings, go to "Slash Commands"
2. Click "Create New Command"
3. Configure commands:

**Command 1: `/trigger-job-search`**
- Command: `/trigger-job-search`
- Request URL: `https://your-github-repo.github.io/api/slack/trigger`
- Short description: "Trigger job search pipeline"
- Usage hint: "[board] (optional)"

**Command 2: `/job-search-status`**
- Command: `/job-search-status`
- Request URL: `https://your-github-repo.github.io/api/slack/status`
- Short description: "Check pipeline status"

**Command 3: `/job-search-summary`**
- Command: `/job-search-summary`
- Request URL: `https://your-github-repo.github.io/api/slack/summary`
- Short description: "Get summary of recent runs"

### 4. Install App to Workspace

1. Go to "OAuth & Permissions"
2. Add Bot Token Scopes:
   - `chat:write`
   - `commands`
   - `chat:write.public`
3. Click "Install to Workspace"
4. Copy "Bot User OAuth Token" (starts with `xoxb-`)
5. Add to GitHub Secrets as `SLACK_BOT_TOKEN`

### 5. Set Up GitHub Secrets

In your GitHub repository settings → Secrets and variables → Actions:

- `SLACK_WEBHOOK_URL` - Incoming webhook URL
- `SLACK_BOT_TOKEN` - Bot user OAuth token

## Usage

### Notifications

The pipeline automatically sends notifications to Slack:

**Pipeline Start:**
```
🔍 Job Search Pipeline Started
Searching: LinkedIn, Indeed, Built In Austin
```

**Pipeline Complete:**
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "✅ Job Search Pipeline Complete"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Jobs Found:* 23"
        },
        {
          "type": "mrkdwn",
          "text": "*High Score:* 87 (B+)"
        },
        {
          "type": "mrkdwn",
          "text": "*Linear Issues Created:* 5"
        }
      ]
    }
  ]
}
```

**High-Score Opportunity Alert:**
```
🎯 High-Score Opportunity Found!

*Company:* Acme Corp
*Role:* Senior DevOps Engineer
*Score:* 92 (A)
*Location:* Austin, TX (Remote)

View details: [Linear Issue](https://linear.app/...)
```

### Manual Triggers

**Via Slack Command:**
```
/trigger-job-search
```

**Via GitHub Actions:**
1. Go to Actions tab
2. Select "Job Search - Manual Trigger"
3. Click "Run workflow"
4. Optionally select specific board

**Via Repository Dispatch (for Slack webhook):**
```bash
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/davidshaevel-dot-com/job-search-pipeline/dispatches \
  -d '{"event_type":"slack-trigger"}'
```

## Configuration

Edit `config/job-boards.yaml` to configure Slack:

```yaml
slack:
  enabled: true
  webhook_url: "${SLACK_WEBHOOK_URL}"
  channel: "#job-search"
  notifications:
    pipeline_start: true
    pipeline_complete: true
    high_score_opportunities: true
    errors: true
  triggers:
    enabled: true
    slash_commands:
      - "/trigger-job-search"
      - "/job-search-status"
      - "/job-search-summary"
```

## Troubleshooting

### Notifications Not Working

1. Verify `SLACK_WEBHOOK_URL` is set correctly
2. Check webhook URL is active in Slack app settings
3. Review pipeline logs for errors
4. Test webhook manually:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test"}' \
     YOUR_WEBHOOK_URL
   ```

### Commands Not Responding

1. Verify `SLACK_BOT_TOKEN` is set correctly
2. Check bot has required scopes
3. Verify Request URL is accessible
4. Review Slack app logs

### Rate Limits

Slack has rate limits:
- Webhooks: 1 message per second
- API calls: Tier 2 (20+ requests per minute)

The pipeline batches notifications to respect rate limits.

## Security

- Never commit Slack tokens to repository
- Use GitHub Secrets for all tokens
- Rotate tokens regularly
- Use workspace-specific tokens (not personal tokens)

---

**Last Updated:** November 8, 2025  
**See Also:** `PLAN.md` for architecture details

