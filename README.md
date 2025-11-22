# Job Search Automation Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Automated job discovery and initial evaluation pipeline that searches multiple job boards, evaluates opportunities using AI, and integrates with Linear and Slack.

## 🎯 Overview

This pipeline automates the discovery and initial evaluation of job opportunities by:
- 🔍 Searching multiple job boards based on configurable criteria
- ⏰ Running ad-hoc or on a scheduled basis (e.g., daily at 8:00 AM CT)
- 🤖 Executing via GitHub Actions workflows or GCP Cloud Run
- 📊 Automatically evaluating opportunities using an 8-factor rubric
- 📁 Organizing discovered jobs in structured folders
- 🔗 Creating Linear issues for promising opportunities
- 💬 Sending Slack notifications and accepting Slack triggers

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key (for Claude evaluation)
- Job board API keys (LinkedIn, Indeed, etc.)
- Linear API key (for issue creation)
- Slack webhook URL (for notifications)
- Google Cloud Platform account (optional, for containerized deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/davidshaevel-dot-com/job-search-pipeline.git
cd job-search-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file (see .env.example template below)
# Create .env file with your API keys:
# ANTHROPIC_API_KEY=sk-ant-...
# LINKEDIN_API_KEY=...
# LINEAR_API_KEY=...
# SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

### Configuration

Edit configuration files in `config/`:
- `search-criteria.yaml` - Define your job search parameters
- `job-boards.yaml` - Configure which boards to search
- `filters.yaml` - Set up deduplication and filtering rules
- `evaluation-thresholds.yaml` - Define scoring thresholds

### Running Locally

```bash
# Ad-hoc execution
python src/main.py

# Run with specific config
python src/main.py --config config/custom-criteria.yaml

# Run single board
python src/main.py --board linkedin
```

### Running via GitHub Actions

1. Set up repository secrets in GitHub:
   - `ANTHROPIC_API_KEY`
   - `LINKEDIN_API_KEY`
   - `INDEED_API_KEY`
   - `LINEAR_API_KEY`
   - `SLACK_WEBHOOK_URL`

2. Trigger manually via Actions tab or use scheduled runs (see `.github/workflows/`)

### Running via GCP Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/job-search-pipeline
gcloud run deploy job-search-pipeline \
  --image gcr.io/PROJECT_ID/job-search-pipeline \
  --platform managed \
  --region us-central1 \
  --set-env-vars="ANTHROPIC_API_KEY=..."
```

### Running via Slack

Send a message to your Slack bot:
```
/trigger-job-search
```

Or use Slack slash commands (see `docs/slack-integration.md`)

## 📋 Features

- **Multi-Board Search**: LinkedIn, Indeed, Built In Austin, RemoteOK, AngelList, and more
- **AI-Powered Evaluation**: Automated evaluation using Claude API and 8-factor rubric
- **Smart Deduplication**: Fuzzy matching to avoid duplicate opportunities
- **Linear Integration**: Auto-create issues for promising roles
- **Slack Integration**: Notifications and manual triggers
- **GitHub Actions**: Scheduled and manual workflow execution
- **GCP Deployment**: Containerized workload support
- **Configurable**: YAML-based configuration for easy customization

## 📁 Project Structure

```
job-search-pipeline/
├── README.md                   # This file
├── CLAUDE.md                   # AI agent context
├── PLAN.md                     # Comprehensive implementation plan
├── config/                     # Configuration files
│   ├── search-criteria.yaml
│   ├── job-boards.yaml
│   ├── filters.yaml
│   └── evaluation-thresholds.yaml
├── src/                        # Source code
│   ├── main.py                 # Entry point
│   ├── search/                  # Search orchestration
│   ├── adapters/                # Job board adapters
│   ├── evaluation/             # AI evaluation engine
│   ├── organization/           # File organization & Linear sync
│   ├── scheduler/              # Scheduling and automation
│   └── integrations/           # Slack, Linear, etc.
├── tests/                      # Test suite
├── data/                       # Processed jobs tracking
├── logs/                       # Execution logs
├── .github/
│   └── workflows/              # GitHub Actions workflows
├── docker/                     # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
└── docs/                       # Documentation
    ├── evaluation_rubric.md
    ├── slack-integration.md
    └── deployment.md
```

## 🔧 Configuration

See `PLAN.md` for comprehensive configuration examples. Key files:

- **search-criteria.yaml**: Keywords, location, salary range, experience level
- **job-boards.yaml**: Board configurations, API keys, rate limits
- **filters.yaml**: Deduplication rules, blacklists, whitelists
- **evaluation-thresholds.yaml**: Minimum scores, auto-pursuit thresholds

## 📊 Evaluation Framework

Jobs are evaluated using an 8-factor weighted rubric:

1. **Skills & Experience Match** (25%)
2. **Compensation & Benefits** (20%)
3. **Company Stability & Growth** (15%)
4. **Work-Life Balance** (15%)
5. **Career Growth & Learning** (10%)
6. **Culture & Team Fit** (8%)
7. **Role Clarity & Expectations** (5%)
8. **Location & Commute** (2%)

See `docs/evaluation_rubric.md` for details.

## 🔄 Workflows

### Scheduled Execution

Daily at 8:00 AM CT via GitHub Actions (see `.github/workflows/job-search-daily.yml`)

### Manual Execution

- GitHub Actions: Use "Run workflow" button
- Slack: `/trigger-job-search` command
- Local: `python src/main.py`
- GCP: Trigger Cloud Run job

### Slack Integration

- **Notifications**: Receive pipeline status updates
- **Triggers**: Start pipeline runs via Slack commands
- **Reports**: Get summaries of discovered opportunities

See `docs/slack-integration.md` for setup instructions.

## 🚢 Deployment

### GitHub Actions

Workflows are configured in `.github/workflows/`. Set up repository secrets and enable workflows.

### GCP Cloud Run

1. Build container: `docker build -t job-search-pipeline .`
2. Push to GCR: `gcloud builds submit --tag gcr.io/PROJECT_ID/job-search-pipeline`
3. Deploy: `gcloud run deploy job-search-pipeline --image gcr.io/PROJECT_ID/job-search-pipeline`

See `docs/deployment.md` for detailed instructions.

## 📈 Implementation Status

**Phase 1:** Foundation - Core infrastructure and single board integration
**Phase 2:** Deduplication & Filtering - Remove duplicates and filter unwanted
**Phase 3:** Multi-Board Support - Rate limiting and parallel execution
**Phase 4:** AI Evaluation - Automated evaluation using Claude API
**Phase 5:** Organization & Linear Integration - Folder structure and auto-issues
**Phase 6:** Scheduling & Automation - GitHub Actions, GCP, Slack
**Phase 7:** Testing & Refinement - Test suite, performance, documentation

See `PLAN.md` for detailed phase breakdowns and Linear issues.

## 🔗 Linear Tracking

**Project:** [Job Search Pipeline Development](https://linear.app/davidshaevel-dot-com/project/job-search-pipeline-development-94abc44631e5)

**Issues:**
- [TT-45](https://linear.app/davidshaevel-dot-com/issue/TT-45) - Phase 1: Foundation
- [TT-46](https://linear.app/davidshaevel-dot-com/issue/TT-46) - Phase 2: Deduplication & Filtering
- [TT-47](https://linear.app/davidshaevel-dot-com/issue/TT-47) - Phase 3: Multi-Board Support
- [TT-48](https://linear.app/davidshaevel-dot-com/issue/TT-48) - Phase 4: AI Evaluation
- [TT-49](https://linear.app/davidshaevel-dot-com/issue/TT-49) - Phase 5: Organization & Linear Integration
- [TT-50](https://linear.app/davidshaevel-dot-com/issue/TT-50) - Phase 6: Scheduling & Automation
- [TT-51](https://linear.app/davidshaevel-dot-com/issue/TT-51) - Phase 7: Testing & Refinement

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome! Please open an issue or submit a pull request.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for automating job search workflows
- Uses Claude API (Anthropic) for AI-powered evaluation
- Integrates with Linear for issue tracking
- Slack integration for notifications and triggers

---

**Repository:** [davidshaevel-dot-com/job-search-pipeline](https://github.com/davidshaevel-dot-com/job-search-pipeline)  
**Last Updated:** November 7, 2025  
**Status:** Planning Phase - Implementation in Progress
