# Local Testing Guide - Job Search Pipeline

**Last Updated:** November 22, 2025
**Current Phase:** Phase 2 Complete (Deduplication & Filtering)

---

## Overview

This guide walks you through testing the job search pipeline locally, including:
- Environment setup
- Configuration validation
- Unit testing (Phase 2 filters)
- Integration testing (JSearch adapter with filtering)
- Manual testing workflows
- Troubleshooting common issues

**Estimated Time:** 15-30 minutes for full testing suite

---

## Prerequisites

### 1. System Requirements

- **Python:** 3.11+ (recommended 3.12.11)
- **Git:** For version control
- **Virtual Environment:** venv or similar
- **API Access:** RapidAPI account with JSearch subscription

### 2. API Keys Required

- **RAPIDAPI_KEY:** For JSearch API access
  - Free tier: 50 requests / 7 days
  - Sign up: https://rapidapi.com/
  - Subscribe to JSearch: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

### 3. Repository Setup

```bash
# Clone repository (if not already cloned)
git clone https://github.com/davidshaevel-dot-com/job-search-pipeline.git
cd job-search-pipeline

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 1: Environment Configuration (5 minutes)

### 1.1 Create .env File

```bash
# Copy example file
cp .env.example .env
```

### 1.2 Add Your API Keys

Edit `.env` and add your RapidAPI key:

```bash
# RapidAPI Key for JSearch
RAPIDAPI_KEY="your-actual-rapidapi-key-here"

# Placeholder keys for future phases (not needed yet)
ANTHROPIC_API_KEY="sk-ant-placeholder"
LINEAR_API_KEY="lin-placeholder"
SLACK_WEBHOOK_URL="https://placeholder.com"
SLACK_BOT_TOKEN="xoxb-placeholder"
GOOGLE_APPLICATION_CREDENTIALS="/tmp/placeholder.json"
```

⚠️ **IMPORTANT:** Replace `your-actual-rapidapi-key-here` with your actual key!

### 1.3 Verify Environment Variables

```bash
# Load .env file (if not already loaded)
source venv/bin/activate

# Check that RAPIDAPI_KEY is set
python -c "from dotenv import load_dotenv; import os; load_dotenv(); key = os.getenv('RAPIDAPI_KEY'); print(f'✅ Key set (ends with ...{key[-4:]})' if key else '❌ Key not set')"
```

**Expected output:**
```
✅ Key set (ends with ...abc8)
```

---

## Step 2: Configuration Validation (3 minutes)

### 2.1 Verify Configuration Files

Check that all required config files exist:

```bash
ls -la config/
```

**Expected files:**
```
config/
├── evaluation-thresholds.yaml
├── filters.yaml
├── job-boards.yaml
├── search-criteria-complex.yaml
├── search-criteria.yaml
└── slack.yaml
```

### 2.2 Validate JSearch Board Configuration

```bash
# Check JSearch is enabled
grep -A 5 "name: JSearch" config/job-boards.yaml
```

**Expected output:**
```yaml
  - name: JSearch
    adapter: jsearch
    enabled: true
    api_key: ${RAPIDAPI_KEY}
```

### 2.3 Test Configuration Loading

```bash
python -c "
from dotenv import load_dotenv
load_dotenv()
from src.config.loader import load_config
config = load_config()
print('✅ Configuration loaded successfully')
print(f'   Boards: {len(config.get(\"boards\", []))}')
print(f'   Filters enabled: {config.get(\"filters\", {}).get(\"filters\", {}).get(\"deduplication\", {}).get(\"enabled\")}')
print(f'   Complex criteria loaded: {\"search_criteria\" in config.to_dict()}')
"
```

**Expected output:**
```
✅ Configuration loaded successfully
   Boards: 1
   Filters enabled: True
   Complex criteria loaded: True
```

---

## Step 3: Unit Testing (5 minutes)

### 3.1 Run All Unit Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests with verbose output
python -m pytest tests/ -v
```

**Expected output:**
```
============================= test session starts ==============================
platform darwin -- Python 3.12.11, pytest-9.0.1, pluggy-1.6.0
collected 19 items

tests/test_filters.py::TestFilterEngine::test_initialization PASSED      [  5%]
tests/test_filters.py::TestFilterEngine::test_company_blacklist_filter PASSED [ 10%]
tests/test_filters.py::TestFilterEngine::test_title_keyword_filter PASSED [ 15%]
tests/test_filters.py::TestFilterEngine::test_salary_range_filter PASSED [ 21%]
tests/test_filters.py::TestFilterEngine::test_experience_level_filter PASSED [ 26%]
tests/test_filters.py::TestFilterEngine::test_required_tech_filter PASSED [ 31%]
tests/test_filters.py::TestFilterEngine::test_date_range_filter PASSED   [ 36%]
tests/test_filters.py::TestFilterEngine::test_deduplication_by_job_id PASSED [ 42%]
tests/test_filters.py::TestFilterEngine::test_deduplication_by_company_title PASSED [ 47%]
tests/test_filters.py::TestFilterEngine::test_deduplication_by_fuzzy_matching PASSED [ 52%]
tests/test_filters.py::TestFilterEngine::test_full_filter_pipeline PASSED [ 57%]
tests/test_filters.py::TestFilterEngine::test_reset PASSED               [ 63%]
tests/test_filters.py::TestJobTracker::test_initialization PASSED        [ 68%]
tests/test_filters.py::TestJobTracker::test_mark_and_check_processed PASSED [ 73%]
tests/test_filters.py::TestJobTracker::test_persistence PASSED           [ 78%]
tests/test_filters.py::TestJobTracker::test_filter_unprocessed PASSED    [ 84%]
tests/test_filters.py::TestJobTracker::test_batch_processing PASSED      [ 89%]
tests/test_filters.py::TestJobTracker::test_get_processed_by_board PASSED [ 94%]
tests/test_filters.py::TestJobTracker::test_clear_processed PASSED       [100%]

============================== 19 passed in 0.11s ==============================
```

✅ **Success Criteria:** All 19 tests pass

### 3.2 Run Specific Test Suites

```bash
# Test FilterEngine only
python -m pytest tests/test_filters.py::TestFilterEngine -v

# Test JobTracker only
python -m pytest tests/test_filters.py::TestJobTracker -v

# Test with coverage report
python -m pytest tests/test_filters.py --cov=src/filters --cov-report=term-missing
```

### 3.3 Test a Specific Feature

```bash
# Test deduplication
python -m pytest tests/test_filters.py::TestFilterEngine::test_deduplication_by_fuzzy_matching -v

# Test complex criteria filtering
python -m pytest tests/test_filters.py::TestFilterEngine::test_salary_range_filter -v
```

---

## Step 4: Integration Testing (5-10 minutes)

### 4.1 Run JSearch Adapter Test Script

This test uses **1 API request** from your free tier quota (50 requests / 7 days).

```bash
# Activate virtual environment
source venv/bin/activate

# Run integration test
python scripts/test_jsearch_adapter.py
```

**Expected output:**
```
============================================================
JSearch Adapter Test - Phase 1 Validation
============================================================

✅ RAPIDAPI_KEY is set (ending in ...abc8)

Enabled boards: JSearch

🔍 Searching JSearch for: 'DevOps Engineer'
   (This will use 1 request from your free tier quota)

2025-11-22 17:40:20,676 - search.orchestrator - INFO - Searching specific board: JSearch
2025-11-22 17:40:32,554 - search.orchestrator - INFO - JSearch: Found 10 job(s)
2025-11-22 17:40:32,554 - search.orchestrator - INFO - Applying filters and deduplication...
2025-11-22 17:40:32,554 - search.orchestrator - INFO - Filtered out 0 previously processed job(s)
2025-11-22 17:40:32,554 - search.orchestrator - INFO - Filtered: 10 → 10 jobs after blacklist, criteria, and deduplication
2025-11-22 17:40:32,555 - search.orchestrator - INFO - Marked 10 new job(s) as processed

============================================================
✅ TEST SUCCESSFUL
============================================================
Total jobs found: 10

Sample results (first 3):
------------------------------------------------------------

1. DevOps Engineer
   Company:     Tech Company
   Location:    Austin, TX
   Remote Type: hybrid
   Salary:      $150,000 - $180,000
   URL:         https://example.com/job1
   Skills:      AWS, Terraform, Python, Kubernetes, CI/CD

...

============================================================
JSearch adapter is working correctly!
Phase 1 implementation validated successfully.
============================================================
```

✅ **Success Criteria:**
- ✅ API key validated
- ✅ 10 jobs found
- ✅ Filtering applied (10 → 10 jobs on first run)
- ✅ Jobs marked as processed
- ✅ Sample results displayed

### 4.2 Test Filtering on Second Run

Run the test script again to verify processed jobs tracking:

```bash
python scripts/test_jsearch_adapter.py
```

**Expected output (second run):**
```
2025-11-22 17:45:32,554 - search.orchestrator - INFO - JSearch: Found 10 job(s)
2025-11-22 17:45:32,554 - search.orchestrator - INFO - Applying filters and deduplication...
2025-11-22 17:45:32,554 - search.orchestrator - INFO - Filtered out 10 previously processed job(s)
2025-11-22 17:45:32,554 - search.orchestrator - INFO - Filtered: 0 → 0 jobs after blacklist, criteria, and deduplication
2025-11-22 17:45:32,555 - search.orchestrator - INFO - Marked 0 new job(s) as processed

Total jobs found: 0
```

✅ **Success Criteria:** All 10 jobs filtered out as previously processed

### 4.3 Clear Processed Jobs Cache

```bash
# Remove processed jobs cache
rm -f data/processed_jobs.json

# Verify it's gone
ls data/
```

Now run the test again - you should get 10 jobs again.

---

## Step 5: Manual Testing Workflows (10 minutes)

### 5.1 Test Custom Search Criteria

Create a custom search configuration:

```bash
# Create test config
cat > config/search-criteria-test.yaml << 'EOF'
search:
  keywords:
    - "Senior DevOps Engineer"
  location: "Austin, TX"
  remote: true

  salary_range:
    min: 160000
    max: 200000

  experience_level:
    - "Senior"
    - "Staff"

  tech_stack:
    required:
      - "AWS"
      - "Kubernetes"
EOF
```

Modify `scripts/test_jsearch_adapter.py` to use this config, or create a custom test script.

### 5.2 Test Blacklist Filtering

Edit `config/filters.yaml` to add test blacklists:

```yaml
filters:
  deduplication:
    enabled: true
    methods:
      - "title_similarity"
      - "company_name"
      - "job_id"
    similarity_threshold: 0.85

  blacklist:
    companies:
      - "Test Blacklisted Company"
    titles:
      - "Junior"
      - "Intern"
    keywords:
      - "Contract Only"
      - "No Benefits"
```

Run the integration test and verify jobs are filtered out.

### 5.3 Test Complex Criteria Filtering

Edit `config/search-criteria-complex.yaml` to be more restrictive:

```yaml
search:
  salary_range:
    min: 180000  # Raise minimum
    max: 250000

  experience_level:
    - "Staff"      # Only Staff+ (excludes Senior)
    - "Principal"

  tech_stack:
    required:
      - "AWS"
      - "Terraform"
      - "Kubernetes"  # Add third requirement
```

Run the integration test and observe more jobs being filtered out.

### 5.4 Test Deduplication Threshold

Edit `config/filters.yaml` to adjust fuzzy matching:

```yaml
filters:
  deduplication:
    enabled: true
    methods:
      - "title_similarity"
      - "company_name"
      - "job_id"
    similarity_threshold: 0.70  # Lower threshold (70% instead of 85%)
```

This will catch more similar titles as duplicates.

---

## Step 6: Debugging and Troubleshooting

### 6.1 Enable Debug Logging

```bash
# Run with debug logging
python scripts/test_jsearch_adapter.py 2>&1 | grep -E "(DEBUG|INFO|WARNING|ERROR)"
```

Or edit the script to set logging level:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### 6.2 Inspect Processed Jobs Cache

```bash
# View processed jobs
cat data/processed_jobs.json | python -m json.tool | head -50

# Count processed jobs
python -c "import json; print(f'Processed jobs: {len(json.load(open(\"data/processed_jobs.json\")))}')"
```

### 6.3 Common Issues and Solutions

#### Issue: "ModuleNotFoundError: No module named 'fuzzywuzzy'"

**Solution:**
```bash
pip install fuzzywuzzy python-Levenshtein
```

#### Issue: "RAPIDAPI_KEY environment variable not set"

**Solution:**
```bash
# Verify .env file exists
cat .env | grep RAPIDAPI_KEY

# Reload environment
source venv/bin/activate
```

#### Issue: "401 Unauthorized" from JSearch API

**Solution:**
- Verify API key is correct in `.env`
- Check RapidAPI subscription is active
- Verify you haven't exceeded free tier quota (50 requests / 7 days)

#### Issue: "No jobs found after filtering"

**Solution:**
```bash
# Clear processed jobs cache
rm data/processed_jobs.json

# Reset filters to permissive defaults
git checkout config/filters.yaml config/search-criteria-complex.yaml

# Run test again
python scripts/test_jsearch_adapter.py
```

#### Issue: Tests fail with import errors

**Solution:**
```bash
# Make sure you're in the project root
pwd  # Should show: /Users/dshaevel/workspace-ds/job-search-pipeline

# Make sure virtual environment is activated
which python  # Should show: .../venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Step 7: Performance Testing (Optional)

### 7.1 Test Rate Limiting

```bash
# Time a single search
time python scripts/test_jsearch_adapter.py
```

**Expected:** ~10-15 seconds for 1 page of results

### 7.2 Test Large Result Sets

Edit `config/job-boards.yaml` to increase results:

```yaml
  - name: JSearch
    adapter: jsearch
    enabled: true
    api_key: ${RAPIDAPI_KEY}
    rate_limit:
      requests_per_second: 0.5
    search_params:
      num_pages: 5  # Increase from 1 to 5 (50 results)
      results_per_page: 10
```

**Warning:** This uses 5 API requests instead of 1!

### 7.3 Test Deduplication Performance

```bash
# Run with many duplicates
python -c "
from src.filters import FilterEngine
from src.core.models import JobPosting
from datetime import datetime

# Create 100 similar jobs
jobs = [
    JobPosting(
        title=f'DevOps Engineer {i}',
        company='Company A',
        location='Austin, TX',
        remote_type='remote',
        board_name='JSearch',
        board_job_id=f'id_{i}'
    )
    for i in range(100)
]

# Time deduplication
import time
start = time.time()

engine = FilterEngine({'filters': {'deduplication': {'enabled': True, 'methods': ['title_similarity', 'company_name', 'job_id'], 'similarity_threshold': 0.85}}})
filtered = engine.filter_jobs(jobs)

elapsed = time.time() - start
print(f'Processed {len(jobs)} jobs in {elapsed:.3f}s')
print(f'Result: {len(filtered)} unique jobs')
"
```

---

## Step 8: Continuous Testing Workflow

### 8.1 Pre-Commit Testing

Before committing code:

```bash
# Run full test suite
python -m pytest tests/ -v

# Run linting (if configured)
flake8 src/ tests/

# Run type checking (if configured)
mypy src/
```

### 8.2 Branch Testing

Before creating a PR:

```bash
# 1. Run unit tests
python -m pytest tests/ -v

# 2. Run integration test (uses 1 API request)
python scripts/test_jsearch_adapter.py

# 3. Clear cache and re-test
rm data/processed_jobs.json
python scripts/test_jsearch_adapter.py

# 4. Verify git status
git status
```

### 8.3 Daily Testing Routine

```bash
#!/bin/bash
# save as scripts/daily_test.sh

echo "🧪 Running daily test suite..."

# Activate venv
source venv/bin/activate

# Run unit tests
echo "📋 Unit tests..."
python -m pytest tests/ -v || exit 1

# Clear cache
echo "🧹 Clearing processed jobs cache..."
rm -f data/processed_jobs.json

# Run integration test (uses 1 API request)
echo "🔍 Integration test..."
python scripts/test_jsearch_adapter.py || exit 1

echo "✅ All tests passed!"
```

Make it executable:
```bash
chmod +x scripts/daily_test.sh
./scripts/daily_test.sh
```

---

## Quick Reference Commands

### Essential Commands

```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt

# Unit Tests
python -m pytest tests/ -v

# Integration Test (uses 1 API request)
python scripts/test_jsearch_adapter.py

# Clear Cache
rm data/processed_jobs.json

# Check Configuration
python -c "from dotenv import load_dotenv; load_dotenv(); from src.config.loader import load_config; config = load_config(); print('✅ Config loaded')"
```

### Debugging Commands

```bash
# View processed jobs
cat data/processed_jobs.json | python -m json.tool

# Check API key
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('RAPIDAPI_KEY')[-4:])"

# Test single module
python -m pytest tests/test_filters.py::TestFilterEngine::test_deduplication_by_fuzzy_matching -v
```

---

## Test Coverage Matrix

| Component | Unit Tests | Integration Tests | Manual Tests |
|-----------|-----------|-------------------|--------------|
| FilterEngine | ✅ 12 tests | ✅ JSearch integration | ✅ Config variations |
| JobTracker | ✅ 7 tests | ✅ Persistence verified | ✅ Cache clearing |
| SearchOrchestrator | ⏳ Coming Phase 3 | ✅ Filtering pipeline | ✅ Multi-board (Phase 3) |
| Config Loader | ⏳ Coming Phase 3 | ✅ All configs loaded | ✅ Environment vars |
| JSearch Adapter | ⏳ Coming Phase 3 | ✅ API calls working | ✅ Rate limiting |

**Total Coverage:** 19 unit tests, 1 integration test, multiple manual tests

---

## Success Checklist

Before marking testing complete, verify:

- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with valid `RAPIDAPI_KEY`
- [ ] All 19 unit tests pass
- [ ] Integration test returns 10 jobs (first run)
- [ ] Integration test returns 0 jobs (second run - all processed)
- [ ] Processed jobs persisted to `data/processed_jobs.json`
- [ ] Configuration files validated
- [ ] Custom search criteria tested
- [ ] Blacklist filtering tested
- [ ] Deduplication verified

---

## Next Steps

After completing local testing:

1. **Create PR:** If implementing new features
2. **Update documentation:** If behavior changed
3. **Deploy to production:** After PR approval
4. **Monitor:** Watch logs and metrics

---

## Additional Resources

- **Main Documentation:** [README.md](../README.md)
- **Implementation Plan:** [PLAN.md](../PLAN.md)
- **RapidAPI Setup:** [docs/RAPIDAPI_SETUP_GUIDE.md](RAPIDAPI_SETUP_GUIDE.md)
- **Configuration Reference:** [config/](../config/)
- **Linear Issues:** [Project Board](https://linear.app/davidshaevel-dot-com/project/job-search-pipeline-development-94abc44631e5)

---

**Last Updated:** November 22, 2025
**Phase Status:** Phase 2 Complete (Deduplication & Filtering)
**Test Count:** 19 unit tests, 1 integration test
**Test Coverage:** FilterEngine (100%), JobTracker (100%)
