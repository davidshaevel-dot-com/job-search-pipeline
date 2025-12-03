# AI Agent Handoff - Job Search Pipeline

**Last Updated:** December 2, 2025
**Project Status:** Phase 3 Complete ✅ - Phase 4 (Organization & Linear) Up Next
**Repository:** [davidshaevel-dot-com/job-search-pipeline](https://github.com/davidshaevel-dot-com/job-search-pipeline)
**Current Branch:** `main`

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

**Phase:** Phase 3 Complete ✅ - Phase 4 (Organization & Linear) Up Next

### Phase 3 Complete (Dec 2, 2025)

**Summary:** Full AI evaluation pipeline integrated and tested

**Accomplishments:**
- [PR #8](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/8) merged - AI Evaluation Engine
- [PR #9](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/9) merged - Integration with SearchOrchestrator
- AI-powered job evaluation using Claude Sonnet 4.5
- 8-factor weighted rubric fully implemented
- `EvaluationResult`, `FactorScore`, and `Grade` models (`src/evaluation/models.py`)
- `PromptBuilder` for structured evaluation prompts with JSON output (`src/evaluation/prompt_builder.py`)
- `AIEvaluator` with retry logic and error handling (`src/evaluation/ai_evaluator.py`)
- `EvaluationWriter` for structured file output (`src/organization/evaluation_writer.py`)
- `SearchOrchestrator.run_search_with_evaluation()` - integrated pipeline
- `--evaluate` flag in main.py for AI evaluation mode
- `--limit` flag for cost control (applied BEFORE evaluation)
- User profile configuration (`config/user-profile.yaml`)
- 64 unit tests (45 new + 19 existing) with 100% passing
- Four rounds of Gemini code review completed (PR #8: 9 issues, PR #9: 4 issues)

### Upcoming: Phase 4 - Organization & Linear Integration

**Focus:** Folder structure management and automatic Linear issue creation

**Planned Tasks:**
1. **Folder Structure Manager** - Organize jobs into active/evaluating/archived/pipeline folders
2. **File Naming Conventions** - Enforce consistent naming across all job files
3. **Linear API Integration** - Connect to Linear for issue management
4. **Auto-Create Issues** - Create Linear issues for high-scoring opportunities (≥85)
5. **Update Existing Issues** - Update if job is reposted or re-evaluated
6. **Archive System** - Move declined opportunities to archive folder

**Known Enhancement for Phase 4:**
- **Timestamped Summaries:** Support multiple pipeline runs per day without overwriting `evaluation_summary.json`

### Completed Phases

**Phase 2: Deduplication & Filtering** ✅ (Nov 24, 2025)
- [PR #4](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/4) merged
- FilterEngine with blacklist, criteria, and deduplication filters
- JobTracker for persistent tracking of processed jobs
- Dual-key deduplication (board_job_id + company::title)
- Fuzzy matching for near-duplicate detection (80% threshold)
- 19 unit tests with 100% passing
- Two rounds of Gemini code review completed (11 issues resolved)

**Phase 1: Foundation** ✅ (Nov 19, 2025)
- [PR #2](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/2) merged
- JSearch adapter via RapidAPI (Google for Jobs aggregator)
- Search orchestrator for coordinating board searches
- Configuration system with YAML and environment variable support
- File writer with date-based directory structure
- Core models (`JobPosting` dataclass)

### Implementation Phases

| Phase | Description | Status | PR |
|-------|-------------|--------|-----|
| 1 | Foundation - Core infrastructure and JSearch integration | ✅ Complete | [#2](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/2) |
| 2 | Deduplication & Filtering | ✅ Complete | [#4](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/4) |
| 3 | AI Evaluation - Claude API integration | ✅ Complete | [#8](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/8), [#9](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/9) |
| 4 | Organization & Linear Integration | 📋 Planned | - |
| 5 | Multi-Board Support - Rate limiting and parallel execution | 📋 Planned | - |
| 6 | Scheduling & Automation - GitHub Actions, GCP, Slack | 📋 Planned | - |
| 7 | Testing & Refinement | 📋 Planned | - |

**Phase Renumbering (Dec 2, 2025):**
- Organization & Linear Integration moved from Phase 5 to Phase 4
- Multi-Board Support moved from Phase 4 to Phase 5
- Rationale: Better to organize and track discovered jobs before adding more sources

**Linear Project:** [Job Search Pipeline Development](https://linear.app/davidshaevel-dot-com/project/job-search-pipeline-development-94abc44631e5)

**Linear Issues:**
- [TT-45](https://linear.app/davidshaevel-dot-com/issue/TT-45) - Phase 1: Foundation ✅
- [TT-46](https://linear.app/davidshaevel-dot-com/issue/TT-46) - Phase 2: Deduplication & Filtering ✅
- [TT-48](https://linear.app/davidshaevel-dot-com/issue/TT-48) - Phase 3: AI Evaluation ✅
- [TT-49](https://linear.app/davidshaevel-dot-com/issue/TT-49) - Phase 4: Organization & Linear Integration (was Phase 5)
- [TT-47](https://linear.app/davidshaevel-dot-com/issue/TT-47) - Phase 5: Multi-Board Support (was Phase 4)
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
Uses 8-factor weighted rubric (see `docs/EVALUATION_RUBRIC.md`):
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
- **Research:** See `docs/BEST_JOB_SEARCH_APIS.md` for comprehensive analysis

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
- `docs/EVALUATION_RUBRIC.md` - 8-factor evaluation rubric
- `docs/SLACK_INTEGRATION.md` - Slack setup guide
- `docs/DEPLOYMENT.md` - Deployment instructions

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
3. Update `docs/SLACK_INTEGRATION.md`
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
- **Evaluation:** `docs/EVALUATION_RUBRIC.md` - 8-factor rubric
- **Slack:** `docs/SLACK_INTEGRATION.md` - Slack setup
- **Deployment:** `docs/DEPLOYMENT.md` - Deployment guide

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

**Last Updated:** December 2, 2025
**Status:** Phase 3 Complete ✅ - Phase 4 (Organization & Linear) Up Next
**Last Merged PRs:**
- [#8 - Phase 3: AI Evaluation Engine with Claude API](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/8) - Merged ✅
- [#9 - Phase 3: AI Evaluation Integration](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/9) - Merged ✅
**Current Branch:** `main`
**Next Steps:** Phase 4 - Organization & Linear Integration

**Phase 3 Complete (Dec 2, 2025):**
- AI-powered job evaluation using Claude Sonnet 4.5
- 8-factor weighted rubric with `EvaluationResult`, `FactorScore`, `Grade` models
- `PromptBuilder` for structured JSON output prompts
- `AIEvaluator` with retry logic, error handling, and cost estimation
- `EvaluationWriter` for structured file output (individual + summary JSON)
- `SearchOrchestrator.run_search_with_evaluation()` - integrated pipeline
- `--evaluate` flag in main.py for AI evaluation mode
- `--limit` flag for cost control (applied BEFORE evaluation)
- User profile configuration (`config/user-profile.yaml`)
- 64 unit tests (45 new + 19 existing), four rounds of Gemini code review (13 issues resolved)
- Generated output in `jobs/pipeline/YYYY-MM-DD/` with individual evaluations and summary

**Phase 2 Accomplishments (Nov 24, 2025):**
- FilterEngine with blacklist, criteria, and deduplication filters
- JobTracker for persistent tracking with dual-key deduplication
- 19 unit tests, two rounds of Gemini code review (11 issues resolved)
- Pipeline now filters duplicates and tracks processed jobs across sessions

**Phase Renumbering (Dec 2, 2025):**
- Organization & Linear Integration moved from Phase 5 to Phase 4
- Multi-Board Support moved from Phase 4 to Phase 5
- Rationale: Better to organize and track discovered jobs before adding more sources

