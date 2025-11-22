# AI Agent Handoff - Job Search Pipeline

**Last Updated:** November 19, 2025
**Project Status:** Phase 1 In Progress - JSearch Adapter Implementation
**Repository:** [davidshaevel-dot-com/job-search-pipeline](https://github.com/davidshaevel-dot-com/job-search-pipeline)
**Current Branch:** `david/tt-45-jsearch-adapter-implementation`

---

## Project Overview

This is an automated job search pipeline that discovers and evaluates job opportunities from multiple job boards. It uses AI-powered evaluation, integrates with Linear for tracking, and supports multiple deployment options including GitHub Actions and GCP Cloud Run.

**Key Features:**
- Multi-board job search (JSearch, Adzuna, RemoteOK, Remotive, The Muse, USAJobs)
- AI-powered evaluation using Claude API and 8-factor rubric
- Automated Linear issue creation for promising opportunities
- Slack integration for notifications and manual triggers
- GitHub Actions workflows for scheduled and manual execution
- GCP Cloud Run deployment support

**Note:** LinkedIn, Indeed, Glassdoor, and Wellfound APIs are deprecated or unavailable for job search

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

**Phase:** Phase 1 In Progress - JSearch Adapter Implementation ⏳

**Completed:**
- ✅ **PR #1 Merged** - Configuration System and File Writer Implementation
  - Configuration loader with YAML support and environment variable substitution
  - File writer with date-based directory structure and filename sanitization
  - Core models (`JobPosting` dataclass in `src/core/models.py`)
  - All code review feedback addressed and merged (18 review comments resolved)
- ✅ **API Research Complete** (Nov 19, 2025)
  - Comprehensive analysis documented in `docs/best-job-search-apis-for-automated-pipelines-in-2024-2025.md`
  - Identified JSearch as best option for Phase 1
  - Documented that Indeed API is deprecated (2020), LinkedIn has no public job search API

**In Progress:**
- ⏳ **JSearch Adapter Implementation** (Current Branch: `david/tt-45-jsearch-adapter-implementation`)
  - Implementing JSearch via RapidAPI instead of Indeed API (deprecated)
  - 40+ data points per job including explicit remote designation
  - Google for Jobs aggregator (sources from LinkedIn, Indeed, Glassdoor, ZipRecruiter, Monster, Dice, etc.)
- ⏳ **Search Orchestrator**
- ⏳ **Main Entry Point Wiring**

**API Selection Update (Nov 19, 2025):**
After comprehensive research, we're implementing **JSearch via RapidAPI** for Phase 1:
- **Why:** Indeed API deprecated (2020), LinkedIn has no public job search API
- **JSearch Benefits:** Google for Jobs aggregator, 40+ data points per job, explicit remote designation
- **Authentication:** Simple RapidAPI key (X-RapidAPI-Key header)
- **Pricing:** Free tier (50 requests/7 days for testing), Paid ($10-50/month for 10K-50K requests)
- **Future:** Architecture supports adding Adzuna, RemoteOK, Remotive in Phase 2

**Implementation Phases:**
1. **Phase 1:** Foundation - Core infrastructure and single board integration ⏳ (In Progress)
2. **Phase 2:** Deduplication & Filtering - Remove duplicates and filter unwanted
3. **Phase 3:** Multi-Board Support - Rate limiting and parallel execution
4. **Phase 4:** AI Evaluation - Automated evaluation using Claude API
5. **Phase 5:** Organization & Linear Integration - Folder structure and auto-issues
6. **Phase 6:** Scheduling & Automation - GitHub Actions, GCP, Slack
7. **Phase 7:** Testing & Refinement - Test suite, performance, documentation

**Linear Project:** [Job Search Pipeline Development](https://linear.app/davidshaevel-dot-com/project/job-search-pipeline-development-94abc44631e5)

**Linear Issues:**
- [TT-45](https://linear.app/davidshaevel-dot-com/issue/TT-45) - Phase 1: Foundation (In Progress)
- [TT-46](https://linear.app/davidshaevel-dot-com/issue/TT-46) - Phase 2: Deduplication & Filtering
- [TT-47](https://linear.app/davidshaevel-dot-com/issue/TT-47) - Phase 3: Multi-Board Support
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

### Git Commit Message Format

We use **Conventional Commit** format for all commit messages:

```
<type>: <brief description>

<optional detailed explanation>

related-issues: TT-XX, TT-YY, TT-ZZ
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `style`: Code style changes (formatting, whitespace)
- `perf`: Performance improvements

**Examples:**
```
feat: implement configuration system with YAML loader

- Create actual config files from examples
- Implement config loader module with environment variable substitution
- Add Config class for easy config access with dot notation

related-issues: TT-45
```

```
fix: handle missing optional config files gracefully

related-issues: TT-45
```

**Important:**
- Always include `related-issues:` at the end with Linear issue identifiers
- Use present tense ("add" not "added")
- Keep first line under 72 characters
- Provide detailed explanation for complex changes

### Pull Request Management

**PR Size Guidelines:**
- Keep PRs focused and reviewable (typically 200-500 lines changed)
- Aim for 1-3 logical components per PR
- Avoid mixing unrelated changes

**When to Create a PR:**
- After completing 1-2 major components or features
- After implementing a logical unit of work (e.g., config system + file writer)
- Before starting a new major component that will add significant code
- When reaching ~300-500 lines of changes

**PR Creation Process:**
1. **Pause Implementation** - After completing logical units of work
2. **Check with User** - Ask if we should create a PR for review
3. **Create PR** - If approved, create PR with comprehensive overview
4. **Wait for Review** - Use gemini-code-assist for code review
5. **Address Feedback** - Make changes based on review comments
6. **Continue** - Resume implementation after PR is merged or approved

**PR Description Template:**
- Overview of changes
- What's included (components, files changed)
- Testing considerations
- Dependencies
- Next steps (not in this PR)
- Review checklist
- Questions for reviewers

**Example Checkpoint:**
> "We've completed the config system and file writer (2 major components, ~560 lines). Should we pause here for a PR review, or continue with the job board adapter?"

### Working with gemini-code-assist Reviews

**Review Feedback Analysis:**
1. **Read All Comments** - Carefully review all feedback from gemini-code-assist
2. **Categorize Feedback** - Identify priority levels (HIGH, MEDIUM, LOW)
3. **Evaluate Each Comment** - Think critically about whether feedback is valid
4. **Create Resolution Plan** - For each piece of feedback:
   - **If Agree:** Create implementation plan with specific changes
   - **If Disagree:** Provide detailed explanation why (with technical reasoning)
   - **If Partially Agree:** Explain what we'll change and what we'll keep

**Addressing Feedback:**
1. **Prioritize Fixes** - Address HIGH priority issues first (bugs, data loss, security)
2. **Implement Changes** - Make code changes following conventional commit format
3. **Test Changes** - Verify fixes work correctly
4. **Commit Changes** - Use `fix:` commit type with clear description
5. **Create Response Comment** - Explain how feedback was addressed

**PR Comment Response Format:**
- **Mention Reviewer:** Always `@gemini-code-assist` to notify them
- **Address Each Comment:** Reference specific comment numbers or issues
- **Show Before/After:** Include code snippets showing changes
- **Explain Reasoning:** For disagreements, provide technical justification
- **Confirm Completion:** State that changes are committed and pushed

**Example Response Structure:**
```
@gemini-code-assist Thank you for the thorough code review! I've addressed all feedback:

## ✅ Comment 1 (HIGH): [Issue Title]
**Issue:** [Brief description]
**Resolution:** [What was changed]
**Code Change:**
```python
# Before
[old code]

# After  
[new code]
```

## ✅ Comment 2 (MEDIUM): [Issue Title]
[Similar format]

## ⚠️ Comment 3 (MEDIUM): [Issue Title]
**Issue:** [Brief description]
**Decision:** [Agree/Partially Agree/Disagree]
**Reasoning:** [Detailed explanation]
**Action Taken:** [What was done]
```

**Feedback Evaluation Guidelines:**
- **HIGH Priority (Bugs, Data Loss, Security):** Always fix immediately
- **MEDIUM Priority (Code Quality, Type Hints, Architecture):** Fix if valid, document if deferring
- **LOW Priority (Style, Naming, Future Improvements):** Document for future consideration

**When to Disagree:**
- Provide detailed technical reasoning
- Explain trade-offs considered
- Show alternative approaches evaluated
- Document decision for future reference
- Be respectful and constructive

**After Addressing Feedback:**
1. Push changes to PR branch
2. Create response comment with `@gemini-code-assist`
3. Wait for re-review or approval
4. Continue implementation after PR is approved/merged

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
- **Phase 1 (Current):** JSearch via RapidAPI
- **Phase 2 (Planned):** Adzuna, RemoteOK, Remotive, The Muse, USAJobs
- **Location:** `src/adapters/`
- **Interface:** `src/adapters/base.py`
- **Note:** LinkedIn, Indeed, Glassdoor, and Wellfound APIs are deprecated or unavailable for job search
- **Research:** See `docs/best-job-search-apis-for-automated-pipelines-in-2024-2025.md` for comprehensive analysis

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

**Last Updated:** November 19, 2025
**Status:** Phase 1 In Progress - JSearch Adapter Implementation ⏳
**Last Merged PR:** [#1 - Phase 1: Configuration System and File Writer](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/1) - Merged ✅
**Current Branch:** `david/tt-45-jsearch-adapter-implementation`
**Next Steps:** Implement JSearch adapter via RapidAPI, search orchestrator, and main.py wiring

**API Research Complete (Nov 19, 2025):**
Comprehensive research documented in `docs/best-job-search-apis-for-automated-pipelines-in-2024-2025.md` identified JSearch as the best option for Phase 1, with Adzuna, RemoteOK, and Remotive as excellent free additions for Phase 2.

