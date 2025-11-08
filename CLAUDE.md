# AI Agent Handoff - Job Search Pipeline

**Last Updated:** November 8, 2025  
**Project Status:** Planning Phase - Ready for Implementation  
**Repository:** [davidshaevel-dot-com/job-search-pipeline](https://github.com/davidshaevel-dot-com/job-search-pipeline)

---

## Project Overview

This is an automated job search pipeline that discovers and evaluates job opportunities from multiple job boards. It uses AI-powered evaluation, integrates with Linear for tracking, and supports multiple deployment options including GitHub Actions and GCP Cloud Run.

**Key Features:**
- Multi-board job search (LinkedIn, Indeed, Built In Austin, RemoteOK, etc.)
- AI-powered evaluation using Claude API and 8-factor rubric
- Automated Linear issue creation for promising opportunities
- Slack integration for notifications and manual triggers
- GitHub Actions workflows for scheduled and manual execution
- GCP Cloud Run deployment support

**Project Management:**
- **Issue Tracking:** Linear (Team Tacocat)
- **Version Control:** GitHub (public repository - davidshaevel-dot-com/job-search-pipeline)
- **Deployment:** GitHub Actions, GCP Cloud Run
- **Integrations:** Linear API, Slack API, Claude API

---

## Repository Structure

```
job-search-pipeline/
├── README.md                    # Main documentation
├── CLAUDE.md                    # This file - AI agent context
├── PLAN.md                      # Comprehensive implementation plan
├── LICENSE                      # MIT License
├── .gitignore
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── config/                      # Configuration files (YAML)
│   ├── search-criteria.yaml
│   ├── job-boards.yaml
│   ├── filters.yaml
│   └── evaluation-thresholds.yaml
├── src/                         # Source code
│   ├── main.py                  # Entry point
│   ├── search/                  # Search orchestration
│   ├── adapters/                # Job board adapters
│   ├── evaluation/              # AI evaluation engine
│   ├── organization/            # File organization & Linear sync
│   └── integrations/            # Slack, Linear integrations
├── tests/                       # Test suite
├── data/                        # Processed jobs tracking
├── logs/                        # Execution logs
├── docs/                        # Documentation
│   ├── evaluation_rubric.md    # 8-factor evaluation rubric
│   ├── slack-integration.md     # Slack setup guide
│   └── deployment.md            # Deployment guide
├── docker/                      # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
└── .github/
    └── workflows/               # GitHub Actions workflows
```

---

## Current Status

**Phase:** Planning Complete - Ready for Implementation

**Implementation Phases:**
1. **Phase 1:** Foundation - Core infrastructure and single board integration
2. **Phase 2:** Multi-Board Support - Rate limiting and parallel execution
3. **Phase 3:** Deduplication & Filtering - Remove duplicates and filter unwanted
4. **Phase 4:** AI Evaluation - Automated evaluation using Claude API
5. **Phase 5:** Organization & Linear Integration - Folder structure and auto-issues
6. **Phase 6:** Scheduling & Automation - GitHub Actions, GCP, Slack
7. **Phase 7:** Testing & Refinement - Test suite, performance, documentation

**Linear Project:** [Job Search Pipeline Development](https://linear.app/davidshaevel-dot-com/project/job-search-pipeline-development-94abc44631e5)

**Linear Issues:**
- [TT-45](https://linear.app/davidshaevel-dot-com/issue/TT-45) - Phase 1: Foundation
- [TT-46](https://linear.app/davidshaevel-dot-com/issue/TT-46) - Phase 2: Multi-Board Support
- [TT-47](https://linear.app/davidshaevel-dot-com/issue/TT-47) - Phase 3: Deduplication & Filtering
- [TT-48](https://linear.app/davidshaevel-dot-com/issue/TT-48) - Phase 4: AI Evaluation
- [TT-49](https://linear.app/davidshaevel-dot-com/issue/TT-49) - Phase 5: Organization & Linear Integration
- [TT-50](https://linear.app/davidshaevel-dot-com/issue/TT-50) - Phase 6: Scheduling & Automation
- [TT-51](https://linear.app/davidshaevel-dot-com/issue/TT-51) - Phase 7: Testing & Refinement

---

## Key Conventions

### File Naming
- **Config files:** `{descriptive-name}.yaml`
- **Job descriptions:** `{company}_{job_title}.txt`
- **Evaluations:** `{company}_evaluation.md`
- **Auto-discovered:** `{company}_{job_title}_auto_{date}.txt`

### Folder Organization
**Hybrid Structure:**
```
jobs/
├── active/              # Currently pursuing
├── evaluating/         # Under evaluation (2025-week-45/company_name/)
├── archived/           # Not pursuing or completed
└── pipeline/           # Auto-discovered, pending review (2025-11-07/)
```

### Configuration
- All configuration in `config/` directory (YAML format)
- Environment variables for API keys (see `.env.example`)
- Secrets stored in GitHub Secrets or GCP Secret Manager

### Evaluation Framework
Uses 8-factor weighted rubric (see `docs/evaluation_rubric.md`):
1. Skills & Experience Match (25%)
2. Compensation & Benefits (20%)
3. Company Stability & Growth (15%)
4. Work-Life Balance (15%)
5. Career Growth & Learning (10%)
6. Culture & Team Fit (8%)
7. Role Clarity & Expectations (5%)
8. Location & Commute (2%)

**Grading Scale:**
- A (90-100): Exceptional opportunity - Strongly pursue
- B (80-89): Strong opportunity - Definitely pursue
- C (70-79): Acceptable opportunity - Consider carefully
- D (60-69): Questionable opportunity - Significant concerns
- F (0-59): Poor opportunity - Do not pursue

---

## Development Workflow

### Local Development
```bash
# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Run locally
python src/main.py
```

### Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Deployment

**GitHub Actions:**
- Workflows in `.github/workflows/`
- Scheduled runs: `job-search-daily.yml`
- Manual triggers: `job-search-manual.yml`
- Slack triggers: `job-search-slack-trigger.yml`

**GCP Cloud Run:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/job-search-pipeline
gcloud run deploy job-search-pipeline \
  --image gcr.io/PROJECT_ID/job-search-pipeline \
  --platform managed \
  --region us-central1
```

---

## Integration Points

### Linear API
- **Purpose:** Create issues for promising opportunities
- **Threshold:** Auto-create for scores ≥ 85 (B+)
- **Location:** `src/integrations/linear/client.py`

### Slack Integration
- **Notifications:** Pipeline status, summaries, high-score alerts
- **Triggers:** Manual pipeline runs via Slack commands
- **Location:** `src/integrations/slack/`

### Claude API
- **Purpose:** AI-powered job evaluation
- **Model:** Claude Sonnet 4.5
- **Location:** `src/evaluation/ai_evaluator.py`

### Job Boards
- **Supported:** LinkedIn, Indeed, Built In Austin, RemoteOK, AngelList
- **Location:** `src/adapters/`
- **Interface:** `src/adapters/base.py`

---

## Important Files

### Configuration
- `config/search-criteria.yaml` - Search parameters
- `config/job-boards.yaml` - Board configurations
- `config/filters.yaml` - Deduplication and filtering rules
- `config/evaluation-thresholds.yaml` - Scoring thresholds

### Documentation
- `README.md` - Main documentation and quick start
- `PLAN.md` - Comprehensive implementation plan
- `docs/evaluation_rubric.md` - 8-factor evaluation rubric
- `docs/slack-integration.md` - Slack setup guide
- `docs/deployment.md` - Deployment instructions

### Source Code
- `src/main.py` - Entry point
- `src/search/orchestrator.py` - Search coordination
- `src/evaluation/ai_evaluator.py` - Claude API integration
- `src/integrations/slack/` - Slack integration
- `src/integrations/linear/` - Linear integration

---

## Environment Variables

Required environment variables (see `.env.example`):

```bash
# AI Evaluation
ANTHROPIC_API_KEY=sk-ant-...

# Job Boards
LINKEDIN_API_KEY=...
INDEED_API_KEY=...
ANGELLIST_API_KEY=...

# Integrations
LINEAR_API_KEY=...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SLACK_BOT_TOKEN=xoxb-...

# GCP (if using Cloud Run)
GOOGLE_CLOUD_PROJECT=...
```

---

## Common Tasks

### Adding a New Job Board
1. Create adapter in `src/adapters/{board_name}.py`
2. Extend `BaseAdapter` class
3. Add configuration to `config/job-boards.yaml`
4. Test adapter locally
5. Update documentation

### Modifying Evaluation Criteria
1. Update `config/search-criteria.yaml`
2. Adjust `config/evaluation-thresholds.yaml` if needed
3. Test evaluation with sample jobs
4. Update prompts in `src/evaluation/prompt_builder.py` if needed

### Adding Slack Commands
1. Create command handler in `src/integrations/slack/trigger_handler.py`
2. Register command in Slack app configuration
3. Update `docs/slack-integration.md`
4. Test command locally

### Deploying to GCP
1. Build Docker image: `docker build -t job-search-pipeline .`
2. Push to GCR: `gcloud builds submit --tag gcr.io/PROJECT_ID/job-search-pipeline`
3. Deploy: `gcloud run deploy job-search-pipeline --image gcr.io/PROJECT_ID/job-search-pipeline`
4. Set up Cloud Scheduler for cron jobs

---

## Troubleshooting

### Common Issues

**API Rate Limits:**
- Check rate limiting configuration in `config/job-boards.yaml`
- Review logs in `logs/` directory
- Implement exponential backoff (already in retry_handler.py)

**Evaluation Failures:**
- Verify ANTHROPIC_API_KEY is set correctly
- Check Claude API quota and limits
- Review evaluation prompts in `src/evaluation/prompt_builder.py`

**Slack Integration Issues:**
- Verify SLACK_WEBHOOK_URL and SLACK_BOT_TOKEN
- Check Slack app permissions
- Review Slack API rate limits

**GCP Deployment Issues:**
- Verify service account permissions
- Check Cloud Run logs: `gcloud run logs read job-search-pipeline`
- Ensure environment variables are set correctly

---

## Resources

### Documentation
- **Plan:** `PLAN.md` - Comprehensive implementation plan
- **Evaluation:** `docs/evaluation_rubric.md` - 8-factor rubric
- **Slack:** `docs/slack-integration.md` - Slack setup
- **Deployment:** `docs/deployment.md` - Deployment guide

### External Links
- **Repository:** https://github.com/davidshaevel-dot-com/job-search-pipeline
- **Linear Project:** https://linear.app/davidshaevel-dot-com/project/job-search-pipeline-development-94abc44631e5
- **Claude API:** https://docs.anthropic.com/
- **Slack API:** https://api.slack.com/
- **Linear API:** https://developers.linear.app/

---

## Questions for AI Agents

When working on this project, consider:

1. **Configuration:** Are search criteria and board configs appropriate?
2. **Evaluation:** Is the AI evaluation prompt effective?
3. **Integration:** Are Linear and Slack integrations working correctly?
4. **Performance:** Is the pipeline running efficiently?
5. **Error Handling:** Are errors being caught and logged properly?

---

**Last Updated:** November 8, 2025  
**Status:** Planning Complete - Ready for Implementation  
**Next Phase:** Phase 1 - Foundation and single board integration

