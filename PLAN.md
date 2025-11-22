# Job Search Automation Pipeline - Implementation Plan

**Created:** November 7, 2025  
**Updated:** November 8, 2025  
**Status:** Planning Phase - Ready for Implementation  
**Repository:** [davidshaevel-dot-com/job-search-pipeline](https://github.com/davidshaevel-dot-com/job-search-pipeline)  
**Goal:** Automate job discovery and initial evaluation using background AI agents, GitHub Actions, GCP Cloud Run, and Slack integration

---

## Executive Summary

This plan outlines the design and implementation of an automated job search pipeline that can:
- Search multiple job boards based on configurable criteria
- Run ad-hoc or on a scheduled basis (e.g., daily at 8:00 AM CT)
- Execute via GitHub Actions workflows, GCP Cloud Run, or local execution
- Automatically evaluate and organize discovered opportunities
- Integrate with Linear tracking and Slack notifications/triggers
- Deploy as containerized workload on GCP

**Key Benefits:**
- Proactive job discovery without manual searching
- Consistent application of evaluation criteria
- Reduced time spent on initial opportunity screening
- Scalable pipeline expansion as new job boards emerge
- Cloud-native deployment options
- Slack integration for notifications and manual triggers

---

## Architecture Overview

### High-Level Flow

```
┌─────────────────┐
│  Config File     │  Defines search criteria and job boards
│  (YAML/JSON)     │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Search Engine  │  Executes searches across configured boards
│  (Python)       │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Job Scraper    │  Extracts job details from each board
│  (Per Board)    │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Deduplication  │  Removes duplicates and known companies
│  & Filtering    │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  AI Evaluator   │  Initial evaluation using rubric
│  (Claude API)   │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  File Organizer │  Creates folder structure
│  & Linear Sync  │  Creates Linear issues for promising roles
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Slack Notify   │  Sends notifications and reports
└─────────────────┘
```

### Execution Options

1. **GitHub Actions** (Recommended for scheduled runs)
   - Scheduled workflows (cron)
   - Manual workflow dispatch
   - Slack trigger via webhook

2. **GCP Cloud Run** (Recommended for containerized deployment)
   - Containerized Python application
   - HTTP endpoint for manual triggers
   - Scheduled via Cloud Scheduler

3. **Local Execution** (Development and testing)
   - Direct Python execution
   - CLI interface
   - Development and debugging

4. **Slack Integration**
   - Receive notifications about pipeline status
   - Trigger pipeline runs via Slack commands
   - Get summaries of discovered opportunities

### Components

1. **Configuration System** (`config/`)
   - Search criteria definitions
   - Job board configurations
   - Filtering rules
   - Evaluation thresholds

2. **Search Engine** (`src/search/`)
   - Multi-board search orchestration
   - Rate limiting and retry logic
   - Error handling and logging

3. **Job Board Adapters** (`src/adapters/`)
   - Individual adapters for each job board
   - Standardized job data format
   - Board-specific scraping logic

4. **Evaluation Engine** (`src/evaluation/`)
   - AI-powered initial evaluation
   - Rubric application
   - Scoring and ranking

5. **Organization System** (`src/organization/`)
   - Folder structure creation
   - File naming conventions
   - Linear integration

6. **Integrations** (`src/integrations/`)
   - Slack integration (notifications and triggers)
   - Linear API integration
   - GitHub Actions workflow support

7. **Deployment** (`docker/`, `.github/workflows/`)
   - Docker containerization
   - GitHub Actions workflows
   - GCP Cloud Run configuration

---

## Detailed Component Design

### 1. Configuration System

**Location:** `config/`

**Files:**
- `search-criteria.yaml` - Search parameters
- `job-boards.yaml` - Board configurations
- `filters.yaml` - Deduplication and filtering rules
- `evaluation-thresholds.yaml` - Minimum scores for pursuit

**Example `search-criteria.yaml`:**
```yaml
search:
  keywords:
    primary:
      - "DevOps Engineer"
      - "Platform Engineer"
      - "Infrastructure Engineer"
      - "Site Reliability Engineer"
    secondary:
      - "Cloud Engineer"
      - "Backend Engineer"
      - "Software Engineer Infrastructure"
  
  location:
    preferred:
      - "Austin, TX"
      - "Remote"
      - "United States"
    acceptable:
      - "Texas"
      - "Hybrid"
  
  salary_range:
    min: 140000
    max: 200000
  
  experience_level:
    - "Senior"
    - "Staff"
    - "Lead"
    - "Principal"
  
  company_stage:
    exclude:
      - "Pre-seed"
      - "Idea stage"
    prefer:
      - "Series A+"
      - "Profitable"
      - "Established"
  
  tech_stack:
    required:
      - "AWS"
      - "Terraform"
    preferred:
      - "Python"
      - "Kubernetes"
      - "CI/CD"
  
  exclude_companies:
    - "Current Employer"
    - "Companies Already Evaluated"
  
  date_range:
    posted_within_days: 7  # Only new postings
```

**Example `job-boards.yaml`:**
```yaml
boards:
  - name: "LinkedIn"
    enabled: true
    adapter: "linkedin"
    api_key: "${LINKEDIN_API_KEY}"
    rate_limit:
      requests_per_minute: 30
    search_params:
      sort_by: "date"
      experience_level: ["3", "4", "5"]  # Senior, Director, Executive
  
  - name: "Indeed"
    enabled: true
    adapter: "indeed"
    api_key: "${INDEED_API_KEY}"
    rate_limit:
      requests_per_minute: 20
  
  - name: "Built In Austin"
    enabled: true
    adapter: "builtin"
    rate_limit:
      requests_per_minute: 10
  
  - name: "AngelList"
    enabled: true
    adapter: "angellist"
    api_key: "${ANGELIST_API_KEY}"
    rate_limit:
      requests_per_minute: 15
  
  - name: "RemoteOK"
    enabled: true
    adapter: "remoteok"
    rate_limit:
      requests_per_minute: 10
```

**Example `filters.yaml`:**
```yaml
deduplication:
  enabled: true
  methods:
    - "title_similarity"  # Fuzzy match on job titles
    - "company_name"     # Exact match on company
    - "job_id"           # Board-specific job IDs
  
  similarity_threshold: 0.85  # 85% similarity = duplicate

blacklist:
  companies:
    - "Current Employer Name"
    - "Companies Already Evaluated"
  
  titles:
    - "Intern"
    - "Junior"
    - "Entry Level"
  
  keywords:
    - "Contract Only"
    - "No Benefits"
    - "Commission Only"
```

**Example `evaluation-thresholds.yaml`:**
```yaml
evaluation:
  minimum_score: 70  # C grade minimum to pursue
  
  auto_pursue_threshold: 85  # B+ or higher - auto-create Linear issue
  
  require_manual_review:
    - score_below: 80
    - score_above: 90  # High scores still need human review
    - missing_compensation: true
    - missing_location: true
  
  scoring:
    use_ai_evaluation: true
    ai_model: "claude-sonnet-4-5"
    fallback_to_manual: true
```

### 2. Search Engine

**Location:** `src/search/`

**Key Files:**
- `orchestrator.py` - Main search coordinator
- `rate_limiter.py` - Rate limiting per board
- `retry_handler.py` - Retry logic with exponential backoff
- `logger.py` - Structured logging

**Features:**
- Parallel search execution across enabled boards
- Rate limiting per board to avoid bans
- Retry logic with exponential backoff
- Comprehensive error handling and logging
- Progress tracking and reporting

### 3. Job Board Adapters

**Location:** `src/adapters/`

**Updated API Strategy (Nov 19, 2025):**
Based on comprehensive research (`docs/best-job-search-apis-for-automated-pipelines-in-2024-2025.md`):

**Phase 1 (Current):**
- **JSearch via RapidAPI** - Google for Jobs aggregator, 40+ fields, $10-50/month

**Phase 2 (Planned):**
- **Adzuna** - Best free alternative, comprehensive US coverage
- **RemoteOK** - 50,000+ remote jobs, completely free
- **Remotive** - 2,000+ curated remote jobs, free
- **The Muse** - Curated quality jobs, free
- **USAJobs** - Federal jobs, free

**APIs Not Available:**
- ❌ Indeed API - Deprecated since 2020
- ❌ LinkedIn API - No public job search API exists
- ❌ Glassdoor API - Deprecated since 2021
- ❌ Wellfound/AngelList API - No public API

**Standardized Job Data Format:**
```python
@dataclass
class JobPosting:
    title: str
    company: str
    location: str
    remote_type: str  # "remote", "hybrid", "onsite"
    salary_min: Optional[int]
    salary_max: Optional[int]
    description: str
    requirements: List[str]
    posted_date: datetime
    job_url: str
    board_name: str
    board_job_id: str
    raw_data: dict  # Original board data for debugging
```

### 4. Evaluation Engine

**Location:** `src/evaluation/`

**Key Files:**
- `ai_evaluator.py` - Claude API integration
- `rubric_applicator.py` - Applies 8-factor rubric
- `scorer.py` - Calculates weighted scores
- `prompt_builder.py` - Constructs evaluation prompts

Uses Claude API to evaluate jobs against the 8-factor rubric (see `docs/evaluation_rubric.md`).

### 5. Organization System

**Location:** `src/organization/`

**Folder Structure (Hybrid Approach):**
```
jobs/
├── active/              # Currently pursuing
│   ├── aravo/
│   └── beakon/
├── evaluating/          # Under evaluation
│   └── 2025-week-45/
│       ├── company_a/
│       └── company_b/
├── archived/            # Not pursuing or completed
│   └── base_power/
└── pipeline/           # Auto-discovered, pending review
    ├── 2025-11-07/
    └── 2025-11-08/
```

### 6. Slack Integration

**Location:** `src/integrations/slack/`

**Features:**

**Notifications:**
- Pipeline start/completion status
- Summary of discovered opportunities
- High-scoring opportunities alerts
- Error notifications

**Triggers:**
- `/trigger-job-search` - Manual pipeline run
- `/job-search-status` - Check current status
- `/job-search-summary` - Get summary of recent runs

**Implementation:**
- Slack Webhook for outgoing notifications
- Slack Slash Commands API for incoming triggers
- Slack Block Kit for rich message formatting

**Example Slack Notification:**
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🔍 Job Search Pipeline Complete"
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
        }
      ]
    }
  ]
}
```

**Slack Configuration:**
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

### 7. GitHub Actions Workflows

**Location:** `.github/workflows/`

**Workflows:**

**1. Scheduled Daily Run** (`job-search-daily.yml`):
```yaml
name: Daily Job Search
on:
  schedule:
    - cron: '0 8 * * *'  # 8:00 AM CT daily
  workflow_dispatch:  # Manual trigger

jobs:
  search:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Job Search Pipeline
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          LINKEDIN_API_KEY: ${{ secrets.LINKEDIN_API_KEY }}
          LINEAR_API_KEY: ${{ secrets.LINEAR_API_KEY }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: python src/main.py
```

**2. Slack Trigger Workflow** (`job-search-slack-trigger.yml`):
```yaml
name: Job Search - Slack Trigger
on:
  repository_dispatch:
    types: [slack-trigger]

jobs:
  search:
    runs-on: ubuntu-latest
    # ... same as daily workflow
```

**3. Manual Trigger Workflow** (`job-search-manual.yml`):
```yaml
name: Job Search - Manual Trigger
on:
  workflow_dispatch:
    inputs:
      board:
        description: 'Specific board to search (optional)'
        required: false
      config:
        description: 'Config file to use'
        required: false
        default: 'config/search-criteria.yaml'
```

### 8. GCP Cloud Run Deployment

**Location:** `docker/`

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
```

**Cloud Run Configuration:**
- Containerized Python application
- HTTP endpoint for manual triggers
- Environment variables from Secret Manager
- Cloud Scheduler for cron jobs

**Deployment:**
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/job-search-pipeline

# Deploy
gcloud run deploy job-search-pipeline \
  --image gcr.io/PROJECT_ID/job-search-pipeline \
  --platform managed \
  --region us-central1 \
  --set-env-vars="ANTHROPIC_API_KEY=..." \
  --allow-unauthenticated  # For manual triggers
```

**Cloud Scheduler:**
```bash
gcloud scheduler jobs create http job-search-daily \
  --schedule="0 8 * * *" \
  --uri="https://job-search-pipeline-xxx.run.app/trigger" \
  --http-method=POST \
  --time-zone="America/Chicago"
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal:** Core infrastructure and single board integration

**Status:** In Progress (Updated Nov 19, 2025)
- ✅ PR #1 Merged - Configuration system and file writer complete
- ⏳ JSearch adapter implementation in progress

**Tasks:**
1. ✅ Create repository structure
2. ✅ Set up configuration system (YAML files)
3. ✅ Implement base adapter interface
4. ⏳ Integrate JSearch API via RapidAPI (Updated: was LinkedIn/Indeed)
5. ✅ Create standardized job data format
6. ⏳ Basic search execution (orchestrator)
7. ⏳ Simple file output to `jobs/pipeline/YYYY-MM-DD/`

**API Selection Update (Nov 19, 2025):**
After comprehensive research (see `docs/best-job-search-apis-for-automated-pipelines-in-2024-2025.md`), implementing **JSearch via RapidAPI** instead of Indeed/LinkedIn:
- **Why:** Indeed API deprecated (2020), LinkedIn has no public job search API
- **JSearch Benefits:** Google for Jobs aggregator, 40+ data points, explicit remote designation
- **Authentication:** Simple RapidAPI key (X-RapidAPI-Key header)
- **Pricing:** Free tier (50 requests/7 days), Paid ($10-50/month for 10K-50K requests)

**Deliverables:**
- ✅ Working config system with environment variable substitution
- ⏳ JSearch adapter via RapidAPI
- ⏳ Basic search execution script (orchestrator)
- ⏳ Job descriptions saved to date-based folders

**Linear Issue:** [TT-45](https://linear.app/davidshaevel-dot-com/issue/TT-45)
**Current Branch:** `david/tt-45-jsearch-adapter-implementation`

### Phase 2: Multi-Board Support (Week 2)
**Goal:** Support multiple job boards with rate limiting

**Updated Plan (Nov 19, 2025):**
Based on API research, focusing on **viable APIs** (LinkedIn, Indeed, Glassdoor APIs are deprecated/unavailable):

**Priority Adapters to Add:**
1. **Adzuna** - Best free alternative, 14-day trial, comprehensive US coverage
2. **RemoteOK** - 50,000+ remote jobs, completely free, no auth required
3. **Remotive** - 2,000+ curated remote jobs, free public API (24hr delay)
4. **The Muse** - Curated quality jobs, 3,600 requests/hour free
5. **USAJobs** - Federal government jobs, completely free

**Tasks:**
1. ⏳ Implement rate limiter with per-API configuration
2. ⏳ Add retry logic with exponential backoff
3. ⏳ Integrate Adzuna adapter (app_id + app_key auth)
4. ⏳ Integrate RemoteOK adapter (no auth, JSON endpoint)
5. ⏳ Integrate Remotive adapter (no auth, 2 req/min limit)
6. ⏳ Parallel search execution across multiple boards
7. ⏳ Comprehensive error handling per adapter
8. ⏳ Logging and progress tracking

**Deliverables:**
- 4-5 functional job board adapters (JSearch + Adzuna + RemoteOK + Remotive + optional The Muse)
- Per-API rate limiting (JSearch: 20/sec, Remotive: 2/min, others: generous)
- Parallel search execution
- Error handling and logging
- Unified data normalization across different API schemas

**Linear Issue:** [TT-46](https://linear.app/davidshaevel-dot-com/issue/TT-46)

### Phase 3: Deduplication & Filtering (Week 2-3)
**Goal:** Remove duplicates and filter unwanted opportunities

**Tasks:**
1. ✅ Implement deduplication logic
2. ✅ Company blacklist filtering
3. ✅ Title/keyword filtering
4. ✅ Similarity matching (fuzzy)
5. ✅ Track processed jobs to avoid re-processing

**Deliverables:**
- Deduplication system
- Filtering rules engine
- Processed jobs database/cache

**Linear Issue:** [TT-47](https://linear.app/davidshaevel-dot-com/issue/TT-47)

### Phase 4: AI Evaluation (Week 3-4)
**Goal:** Automated initial evaluation using Claude API

**Tasks:**
1. ✅ Integrate Claude API
2. ✅ Build evaluation prompt templates
3. ✅ Implement rubric application
4. ✅ Score calculation and grading
5. ✅ Evaluation result storage
6. ✅ Confidence scoring

**Deliverables:**
- AI evaluation engine
- Evaluation result files
- Scoring and grading system

**Linear Issue:** [TT-48](https://linear.app/davidshaevel-dot-com/issue/TT-48)

### Phase 5: Organization & Linear Integration (Week 4)
**Goal:** Organize files and create Linear issues

**Tasks:**
1. ✅ Implement folder structure manager
2. ✅ File naming convention enforcement
3. ✅ Linear API integration
4. ✅ Auto-create Linear issues for promising roles
5. ✅ Update existing Linear issues if job reposted
6. ✅ Archive system for declined opportunities

**Deliverables:**
- Folder organization system
- Linear integration
- Auto-issue creation
- Archive system

**Linear Issue:** [TT-49](https://linear.app/davidshaevel-dot-com/issue/TT-49)

### Phase 6: Scheduling & Automation (Week 5)
**Goal:** Scheduled execution, GitHub Actions, GCP, and Slack integration

**Tasks:**
1. ✅ Implement GitHub Actions workflows
2. ✅ Docker containerization
3. ✅ GCP Cloud Run deployment
4. ✅ Slack integration (notifications and triggers)
5. ✅ Notification system
6. ✅ Execution logging and monitoring
7. ✅ Manual trigger support

**Deliverables:**
- GitHub Actions workflows
- Docker container
- GCP Cloud Run deployment
- Slack integration
- Notification system

**Linear Issue:** [TT-50](https://linear.app/davidshaevel-dot-com/issue/TT-50)

### Phase 7: Testing & Refinement (Week 5-6)
**Goal:** Testing, bug fixes, and optimization

**Tasks:**
1. ✅ Unit tests for core components
2. ✅ Integration tests for full pipeline
3. ✅ Performance optimization
4. ✅ Error handling improvements
5. ✅ Documentation updates
6. ✅ User guide creation

**Deliverables:**
- Test suite
- Performance optimizations
- Complete documentation
- User guide

**Linear Issue:** [TT-51](https://linear.app/davidshaevel-dot-com/issue/TT-51)

---

## Technical Stack

### Languages & Frameworks
- **Python 3.11+** - Primary language
- **YAML** - Configuration files
- **JSON** - Data interchange

### Libraries
- **requests** - HTTP requests for APIs
- **beautifulsoup4** - HTML parsing for scraping
- **playwright** - Browser automation (if needed)
- **anthropic** - Claude API client
- **slack-sdk** - Slack API client
- **python-dateutil** - Date parsing
- **fuzzywuzzy** - String similarity for deduplication
- **pydantic** - Data validation
- **pyyaml** - YAML parsing
- **gunicorn** - WSGI server (for Cloud Run)

### External Services
- **Claude API** (Anthropic) - AI evaluation
- **LinkedIn API** - Job search
- **Indeed API** - Job search
- **Linear API** - Issue tracking
- **Slack API** - Notifications and triggers
- **GitHub Actions** - Scheduled execution
- **GCP Cloud Run** - Containerized deployment
- **GCP Secret Manager** - Secrets management

### Infrastructure
- **GitHub** - Version control and CI/CD
- **Docker** - Containerization
- **GCP Cloud Run** - Serverless container execution
- **GCP Cloud Scheduler** - Cron jobs
- **GCP Secret Manager** - API keys and secrets

---

## File Structure

```
job-search-pipeline/
├── README.md                    # Main README
├── CLAUDE.md                    # AI agent context
├── PLAN.md                      # This file
├── LICENSE                      # MIT License
├── .gitignore
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── config/
│   ├── search-criteria.yaml
│   ├── job-boards.yaml
│   ├── filters.yaml
│   └── evaluation-thresholds.yaml
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── search/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── rate_limiter.py
│   │   ├── retry_handler.py
│   │   └── logger.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── linkedin.py
│   │   ├── indeed.py
│   │   ├── builtin.py
│   │   ├── angellist.py
│   │   └── remoteok.py
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── ai_evaluator.py
│   │   ├── rubric_applicator.py
│   │   ├── scorer.py
│   │   └── prompt_builder.py
│   ├── organization/
│   │   ├── __init__.py
│   │   ├── folder_manager.py
│   │   ├── file_writer.py
│   │   ├── linear_sync.py
│   │   └── naming_conventions.py
│   └── integrations/
│       ├── __init__.py
│       ├── slack/
│       │   ├── __init__.py
│       │   ├── notifier.py
│       │   ├── trigger_handler.py
│       │   └── formatter.py
│       └── linear/
│           ├── __init__.py
│           └── client.py
├── tests/
│   ├── __init__.py
│   ├── test_search.py
│   ├── test_adapters.py
│   ├── test_evaluation.py
│   └── test_organization.py
├── data/
│   ├── processed_jobs.json      # Track processed jobs
│   └── cache/                   # Cached responses
├── logs/
│   └── .gitignore
├── docs/
│   ├── evaluation_rubric.md      # 8-factor rubric
│   ├── slack-integration.md      # Slack setup guide
│   └── deployment.md             # Deployment guide
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
└── .github/
    └── workflows/
        ├── job-search-daily.yml
        ├── job-search-manual.yml
        └── job-search-slack-trigger.yml
```

---

## Success Metrics

### Quantitative
- **Jobs Discovered:** Target 20-50 new opportunities per week
- **Evaluation Accuracy:** 80%+ alignment with manual evaluation
- **Processing Time:** < 30 minutes for full pipeline run
- **Uptime:** 95%+ successful executions
- **Slack Response Time:** < 5 seconds for trigger acknowledgment

### Qualitative
- Reduces manual job board browsing time by 80%
- Consistent application of evaluation criteria
- Easy to add new job boards
- Clear organization of discovered opportunities
- Seamless Slack integration

---

## Risks & Mitigations

### Risk 1: Job Board API Changes
**Impact:** High - Pipeline breaks  
**Mitigation:** 
- Abstract adapter interface
- Version pinning for APIs
- Fallback to web scraping
- Regular monitoring and updates

### Risk 2: Rate Limiting / Bans
**Impact:** Medium - Temporary pipeline failure  
**Mitigation:**
- Aggressive rate limiting
- Respect robots.txt
- Rotating user agents
- Exponential backoff retries

### Risk 3: AI Evaluation Accuracy
**Impact:** Medium - False positives/negatives  
**Mitigation:**
- Human review for high-scoring opportunities
- Confidence scoring
- Continuous prompt refinement
- Manual override capability

### Risk 4: GCP Costs
**Impact:** Low - Unexpected charges  
**Mitigation:**
- Cloud Run pay-per-use model
- Set budget alerts
- Monitor usage
- Optimize container size

### Risk 5: Slack Rate Limits
**Impact:** Low - Notification delays  
**Mitigation:**
- Batch notifications
- Respect rate limits
- Queue system for high volume
- Fallback to email

---

## Future Enhancements

### Phase 8+ (Post-MVP)
1. **Application Automation**
   - Auto-apply to high-scoring opportunities
   - Resume tailoring per role
   - Cover letter generation

2. **Advanced Filtering**
   - ML-based relevance scoring
   - Learning from user feedback
   - Custom filter rules

3. **Analytics Dashboard**
   - Job market trends
   - Salary insights
   - Company growth tracking

4. **Integration Expansions**
   - Email summaries
   - Calendar integration for interviews
   - CRM integration

5. **Multi-User Support**
   - User-specific configs
   - Shared opportunity pool
   - Team collaboration features

---

## Next Steps

1. **Review & Approve Plan** (This document)
2. **Set up GitHub Repository** - Create `davidshaevel-dot-com/job-search-pipeline`
3. **Configure Secrets** - Set up GitHub Secrets and GCP Secret Manager
4. **Begin Phase 1** - Foundation and single board integration

---

**Document Status:** Ready for Implementation  
**Last Updated:** November 8, 2025  
**Repository:** [davidshaevel-dot-com/job-search-pipeline](https://github.com/davidshaevel-dot-com/job-search-pipeline)
