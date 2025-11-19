# Phase 1 Testing Guide - JSearch Adapter Implementation

**Date:** November 19, 2025
**Status:** Ready for testing
**Branch:** `david/tt-45-jsearch-adapter-implementation`

---

## Overview

This guide covers testing the Phase 1 implementation:
- ✅ JSearch adapter (src/adapters/jsearch.py)
- ✅ Search orchestrator (src/search/orchestrator.py)
- ✅ Main entry point (src/main.py)
- ✅ End-to-end pipeline execution

---

## Prerequisites

### 1. RapidAPI Account Setup

**Sign up for RapidAPI:**
1. Go to https://rapidapi.com/
2. Create a free account
3. Verify your email

**Subscribe to JSearch API:**
1. Visit https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Click "Subscribe to Test"
3. Select the **Free tier**:
   - 50 requests over 7 days
   - No credit card required
   - Perfect for Phase 1 testing
4. Copy your RapidAPI key from the "Code Snippets" section
   - Look for `X-RapidAPI-Key` header value

**Set environment variable:**
```bash
export RAPIDAPI_KEY="your-rapidapi-key-here"
```

**Verify it's set:**
```bash
echo $RAPIDAPI_KEY
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

**Key dependencies:**
- requests>=2.31.0 (for API calls)
- pyyaml>=6.0.1 (for configuration)
- python-dateutil>=2.8.2 (for date parsing)

---

## Testing Strategy

### Test 1: JSearch Adapter Validation (Recommended First Test)

**Purpose:** Verify JSearch adapter works correctly with RapidAPI

**Script:** `scripts/test_jsearch_adapter.py`

**What it tests:**
- Configuration loading
- RAPIDAPI_KEY validation
- JSearch adapter initialization
- API request execution
- Response parsing to JobPosting objects
- Field mapping (title, company, location, remote_type, salary, requirements, etc.)

**Run the test:**
```bash
python scripts/test_jsearch_adapter.py
```

**Expected output:**
```
============================================================
JSearch Adapter Test - Phase 1 Validation
============================================================

✅ RAPIDAPI_KEY is set (ending in ...abcd)

Enabled boards: JSearch

🔍 Searching JSearch for: 'DevOps Engineer'
   (This will use 1 request from your free tier quota)

============================================================
✅ TEST SUCCESSFUL
============================================================
Total jobs found: 10

Sample results (first 3):

1. Senior DevOps Engineer
   Company:     Example Corp
   Location:    Austin, TX, US
   Remote Type: hybrid
   Salary:      $140,000 - $180,000
   URL:         https://...
   Skills:      AWS, Terraform, Docker, Kubernetes, Python

...

============================================================
JSearch adapter is working correctly!
Phase 1 implementation validated successfully.
============================================================
```

**If it fails:**
- Check RAPIDAPI_KEY is set correctly
- Verify you're subscribed to JSearch API free tier
- Check config/job-boards.yaml has `enabled: true` for JSearch
- Review error messages for specific issues

**Free tier quota:** This test uses **1 request** (49 remaining for the week)

---

### Test 2: Full Pipeline Execution

**Purpose:** Test end-to-end pipeline with file output

**What it tests:**
- Configuration loading
- Search orchestrator coordination
- JSearch API integration
- File writer output
- Date-based directory structure
- Logging and error handling

**Run the pipeline:**
```bash
python src/main.py
```

**Expected output:**
```
============================================================
Job Search Pipeline - Phase 1 (JSearch via RapidAPI)
============================================================
Date/Time: 2025-11-19 14:30:00
Board:     All enabled boards
============================================================

Enabled boards: JSearch

🔍 Searching all enabled boards...

📝 Writing 10 jobs to files...

============================================================
✅ SEARCH COMPLETE
============================================================
Total jobs found:     10
Files created:        10
Output directory:     jobs/pipeline/2025-11-19
============================================================

Created files:
  - jobs/pipeline/2025-11-19/example_corp_senior_devops_engineer_001.txt
  - jobs/pipeline/2025-11-19/tech_co_devops_engineer_002.txt
  ...
```

**Verify output:**
```bash
# Check files were created
ls -la jobs/pipeline/$(date +%Y-%m-%d)/

# View a sample job file
cat jobs/pipeline/$(date +%Y-%m-%d)/*.txt | head -50
```

**Free tier quota:** This test uses **1 request** (uses same search as Test 1)

---

### Test 3: Debug Mode

**Purpose:** Test with verbose logging to see detailed operation

**Run with debug logging:**
```bash
python src/main.py --debug
```

**Expected behavior:**
- More detailed log messages
- DEBUG-level logs from all components
- Request/response details
- Configuration parsing details

**Use for:**
- Troubleshooting issues
- Understanding data flow
- Verifying rate limiting
- Checking field mappings

---

### Test 4: Specific Board Search

**Purpose:** Test searching JSearch board explicitly

**Run specific board search:**
```bash
python src/main.py --board JSearch
```

**Expected behavior:**
- Only searches JSearch board
- Skips any other enabled boards
- Same output as full pipeline (since JSearch is only enabled board in Phase 1)

**Free tier quota:** Uses **1 request**

---

## Configuration Validation

### Verify job-boards.yaml

**Check JSearch configuration:**
```bash
cat config/job-boards.yaml | grep -A 20 "name: \"JSearch\""
```

**Expected configuration:**
```yaml
- name: "JSearch"
  enabled: true
  adapter: "jsearch"
  api_key: "${RAPIDAPI_KEY}"
  api_host: "jsearch.p.rapidapi.com"
  rate_limit:
    requests_per_second: 20
  search_params:
    num_pages: 1
    date_posted: "week"
    remote_jobs_only: false
    employment_types: "FULLTIME"
```

**Verify search-criteria.yaml:**
```bash
cat config/search-criteria.yaml
```

**Expected criteria:**
```yaml
search:
  keywords:
    - "DevOps Engineer"
    - "Platform Engineer"
    - "SRE"
  location: "Austin, TX"
  remote: true
  employment_type: "FULLTIME"
```

---

## Troubleshooting

### Error: "RAPIDAPI_KEY environment variable not set"

**Problem:** Environment variable not set or not visible to Python

**Solutions:**
1. Set it in current shell:
   ```bash
   export RAPIDAPI_KEY="your-key-here"
   ```

2. Verify it's set:
   ```bash
   echo $RAPIDAPI_KEY
   ```

3. Add to ~/.bashrc or ~/.zshrc for persistence:
   ```bash
   echo 'export RAPIDAPI_KEY="your-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Error: "No job boards are enabled"

**Problem:** JSearch not enabled in config/job-boards.yaml

**Solution:**
1. Edit config/job-boards.yaml
2. Find JSearch section
3. Change `enabled: false` to `enabled: true`

### Error: "401 Unauthorized" or "403 Forbidden"

**Problem:** Invalid or unsubscribed RapidAPI key

**Solutions:**
1. Verify you're subscribed to JSearch API free tier
2. Check your RapidAPI key is correct
3. Try regenerating your RapidAPI key in the dashboard
4. Verify key has no extra spaces or quotes

### Error: "No jobs found"

**Problem:** Search criteria too restrictive or API returned no results

**Not a problem if:**
- The test script runs without errors
- API returned status "OK"
- Just means no matching jobs for the criteria

**Solutions (if you want results):**
1. Broaden search criteria in config/search-criteria.yaml
2. Try different keywords (e.g., just "Engineer")
3. Remove location restriction
4. Try date_posted: "month" instead of "week"

### Error: "Module not found"

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

---

## Success Criteria

Phase 1 implementation is successful if:

1. ✅ Test script runs without errors
2. ✅ JSearch adapter can execute API requests
3. ✅ API responses are parsed into JobPosting objects
4. ✅ Search orchestrator coordinates search successfully
5. ✅ Main entry point executes full pipeline
6. ✅ Files are created in jobs/pipeline/YYYY-MM-DD/
7. ✅ Job data is correctly formatted in output files
8. ✅ Logging shows appropriate progress messages
9. ✅ Error handling works (try with RAPIDAPI_KEY unset)

---

## Free Tier Quota Management

**Total quota:** 50 requests over 7 days

**Quota used per test:**
- Test 1 (adapter validation): 1 request
- Test 2 (full pipeline): 1 request
- Test 3 (debug mode): 1 request
- Test 4 (specific board): 1 request

**Estimated usage for full Phase 1 testing:** 4-5 requests

**Check remaining quota:**
- Visit https://rapidapi.com/developer/billing/subscriptions
- Look for JSearch API
- View "Requests Made" vs "Quota Limit"

**Quota resets:** 7 days after first request

**What to do if quota exceeded:**
- Wait for 7-day reset (free tier)
- Upgrade to paid tier ($10-50/month for 10K-50K requests)
- Use mock data for development (Phase 2 will add testing framework)

---

## Next Steps After Testing

### If Tests Pass:

1. **Commit and create PR:**
   ```bash
   git add scripts/test_jsearch_adapter.py docs/TESTING_PHASE1.md
   git commit -m "test: add Phase 1 validation script and testing documentation"
   git push origin david/tt-45-jsearch-adapter-implementation
   ```

2. **Create Pull Request:**
   - Title: "feat: Phase 1 - JSearch Adapter, Search Orchestrator, and Main Entry Point"
   - Description: Implementation details, testing performed, next steps

3. **Update Linear TT-45:**
   - Mark as "Done"
   - Add comment with test results
   - Link to PR

4. **Update CLAUDE.md:**
   - Phase 1 status: Complete
   - Next: Phase 2 planning

### If Tests Fail:

1. **Review error messages carefully**
2. **Check troubleshooting section above**
3. **Run with --debug for detailed logs**
4. **Check configuration files**
5. **Verify environment variables**
6. **Review implementation code if needed**

---

## Testing Checklist

Before creating PR, verify:

- [ ] RapidAPI account created and JSearch subscribed
- [ ] RAPIDAPI_KEY environment variable set
- [ ] Test script runs successfully
- [ ] Full pipeline executes without errors
- [ ] Output files created in correct directory structure
- [ ] Job data parsed correctly (check sample files)
- [ ] Debug mode shows detailed logging
- [ ] Error handling works (test with missing RAPIDAPI_KEY)
- [ ] Configuration files are correct
- [ ] All commits have descriptive messages

---

## Contact & Support

**Questions or issues?**
- Review error messages and logs first
- Check troubleshooting section above
- Consult JSearch API documentation: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
- Check PLAN.md for Phase 1 details
- Review Linear TT-45 for implementation notes

---

**Last Updated:** November 19, 2025
**Phase:** 1 (Foundation)
**Status:** Ready for testing
