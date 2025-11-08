# Deployment Guide

This guide covers deploying the job search pipeline to various platforms.

## Deployment Options

1. **GitHub Actions** (Recommended for scheduled runs)
2. **GCP Cloud Run** (Recommended for containerized deployment)
3. **Local Execution** (Development and testing)

## GitHub Actions Deployment

### Prerequisites

- GitHub repository: `davidshaevel-dot-com/job-search-pipeline`
- GitHub Actions enabled
- Repository secrets configured

### Setup Secrets

In repository settings → Secrets and variables → Actions, add:

- `ANTHROPIC_API_KEY`
- `LINKEDIN_API_KEY`
- `INDEED_API_KEY`
- `ANGELIST_API_KEY`
- `LINEAR_API_KEY`
- `SLACK_WEBHOOK_URL`
- `SLACK_BOT_TOKEN`

### Workflows

Three workflows are available:

1. **Daily Scheduled Run** (`.github/workflows/job-search-daily.yml`)
   - Runs daily at 8:00 AM CT
   - Can be triggered manually

2. **Manual Trigger** (`.github/workflows/job-search-manual.yml`)
   - Manual execution via Actions UI
   - Optional board selection

3. **Slack Trigger** (`.github/workflows/job-search-slack-trigger.yml`)
   - Triggered via repository_dispatch event
   - Can be called from Slack webhook

### Enable Workflows

1. Go to Actions tab in GitHub
2. Workflows should appear automatically
3. Enable workflows if prompted
4. Test with manual trigger

## GCP Cloud Run Deployment

### Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed
- Docker installed (for local builds)

### Setup

1. **Create GCP Project:**
   ```bash
   gcloud projects create job-search-pipeline
   gcloud config set project job-search-pipeline
   ```

2. **Enable APIs:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable cloudscheduler.googleapis.com
   ```

3. **Set up Service Account:**
   ```bash
   gcloud iam service-accounts create job-search-pipeline \
     --display-name="Job Search Pipeline"
   ```

4. **Grant Permissions:**
   ```bash
   gcloud projects add-iam-policy-binding job-search-pipeline \
     --member="serviceAccount:job-search-pipeline@job-search-pipeline.iam.gserviceaccount.com" \
     --role="roles/run.invoker"
   ```

### Build and Deploy

1. **Build Container:**
   ```bash
   gcloud builds submit --tag gcr.io/job-search-pipeline/job-search-pipeline
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy job-search-pipeline \
     --image gcr.io/job-search-pipeline/job-search-pipeline \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="ANTHROPIC_API_KEY=..." \
     --set-env-vars="LINKEDIN_API_KEY=..." \
     --set-env-vars="LINEAR_API_KEY=..." \
     --set-env-vars="SLACK_WEBHOOK_URL=..."
   ```

3. **Set up Cloud Scheduler (for cron):**
   ```bash
   gcloud scheduler jobs create http job-search-daily \
     --schedule="0 8 * * *" \
     --uri="https://job-search-pipeline-xxx.run.app/trigger" \
     --http-method=POST \
     --time-zone="America/Chicago" \
     --oidc-service-account-email="job-search-pipeline@job-search-pipeline.iam.gserviceaccount.com"
   ```

### Using Secret Manager

For better security, use Secret Manager:

1. **Create Secrets:**
   ```bash
   echo -n "your-api-key" | gcloud secrets create anthropic-api-key --data-file=-
   echo -n "your-api-key" | gcloud secrets create linkedin-api-key --data-file=-
   ```

2. **Grant Access:**
   ```bash
   gcloud secrets add-iam-policy-binding anthropic-api-key \
     --member="serviceAccount:job-search-pipeline@job-search-pipeline.iam.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

3. **Deploy with Secrets:**
   ```bash
   gcloud run deploy job-search-pipeline \
     --image gcr.io/job-search-pipeline/job-search-pipeline \
     --update-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
     --update-secrets="LINKEDIN_API_KEY=linkedin-api-key:latest"
   ```

## Local Deployment

### Prerequisites

- Python 3.11+
- Virtual environment

### Setup

1. **Clone Repository:**
   ```bash
   git clone https://github.com/davidshaevel-dot-com/job-search-pipeline.git
   cd job-search-pipeline
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run:**
   ```bash
   python src/main.py
   ```

## Docker Deployment

### Build Image

```bash
docker build -f docker/Dockerfile -t job-search-pipeline .
```

### Run Container

```bash
docker run --env-file .env job-search-pipeline
```

### Using Docker Compose

```bash
cd docker
docker-compose up
```

## Monitoring

### GitHub Actions

- View workflow runs in Actions tab
- Check logs for each run
- Download artifacts (logs) on failure

### GCP Cloud Run

- View logs: `gcloud run logs read job-search-pipeline`
- Monitor metrics in Cloud Console
- Set up alerts for failures

### Local

- Check `logs/` directory
- Review console output
- Monitor data files in `data/`

## Troubleshooting

### GitHub Actions Failures

1. Check workflow logs
2. Verify secrets are set correctly
3. Review Python version compatibility
4. Check timeout settings

### Cloud Run Failures

1. Check logs: `gcloud run logs read job-search-pipeline`
2. Verify environment variables
3. Check service account permissions
4. Review container logs

### Local Execution Issues

1. Verify Python version: `python --version`
2. Check dependencies: `pip list`
3. Verify environment variables: `env | grep API_KEY`
4. Review logs in `logs/` directory

---

**Last Updated:** November 8, 2025  
**See Also:** `PLAN.md` for architecture details

