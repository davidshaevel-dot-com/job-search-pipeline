# Session Agenda - November 19, 2025 (Wednesday)

**Working Directory:** `/Users/dshaevel/workspace-ds/job-search-pipeline`
**Current Branch:** `main`
**Last Session:** November 12, 2025 (PR #1 merged)
**Project Status:** Phase 1 In Progress - Configuration System and File Writer Complete

---

## Session Overview

This session focuses on continuing Phase 1 implementation by building the remaining components: job board adapter, search orchestrator, and main entry point wiring.

---

## Project Context

### What We Have Accomplished

**PR #1 - MERGED ✅** (November 12, 2025)
- ✅ Configuration system with YAML loader and environment variable substitution
- ✅ File writer with date-based directory structure
- ✅ Core data models (`JobPosting` in `src/core/models.py`)
- ✅ All gemini-code-assist feedback addressed (18 review comments resolved)

**Key Features Implemented:**
- Config loader with fail-fast environment variable substitution
- Consistent YAML schema across all config files
- File writer with optimized filename uniqueness checking
- Robust error handling and documentation

**Files Created:**
- `src/config/loader.py` - Configuration system
- `src/organization/file_writer.py` - File output
- `src/core/models.py` - JobPosting dataclass
- `config/*.yaml` - All configuration files (search-criteria, job-boards, slack, filters, evaluation-thresholds)

### What Remains for Phase 1

**Phase 1 (Foundation) - Linear Issue TT-45**

**Completed:**
1. ✅ Repository structure
2. ✅ Configuration system (YAML files)
3. ✅ Base adapter interface (`src/adapters/base.py`)
4. ✅ Standardized job data format (`JobPosting`)
5. ✅ File output system

**Remaining:**
6. ⏳ **Integrate one job board** (LinkedIn or Indeed API)
7. ⏳ **Basic search execution** (orchestrator)
8. ⏳ **Simple file output** (wire everything together)

---

## Today's Goals

### Goal 1: Implement JSearch Job Board Adapter (via RapidAPI)
**Priority:** HIGH
**Estimated Time:** 2-3 hours

**Updated Decision:** Based on comprehensive API research (see `docs/best-job-search-apis-for-automated-pipelines-in-2024-2025.md`), we're implementing **JSearch via RapidAPI** instead of Indeed API (which is deprecated).

**Why JSearch:**
- ✅ Indeed API is **deprecated** since 2020 for job search
- ✅ JSearch provides **most comprehensive coverage** via Google for Jobs
- ✅ Sources from LinkedIn, Indeed, Glassdoor, ZipRecruiter, Monster, Dice, etc.
- ✅ **40+ data points per job** including explicit remote designation
- ✅ **Simple API key authentication** via RapidAPI
- ✅ **Real-time data** with 1-3 second response times
- ✅ **Proven reliability** with active Discord community support
- ✅ **Free tier:** 50 requests over 7 days for testing
- ✅ **Paid tier:** $10-50/month for 10,000-50,000 requests

**Future-Proof Design:**
- Architecture will support adding **Adzuna** in Phase 2 (best free alternative)
- Multi-API abstraction layer from start

**Tasks:**
1. Update configuration for JSearch
   - Add JSearch configuration to `config/job-boards.yaml`
   - Set up RapidAPI account and get API key
   - Configure `RAPIDAPI_KEY` environment variable

2. Create JSearch adapter (`src/adapters/jsearch.py`)
   - Extend `BaseAdapter` class
   - Implement `search()` method
   - Handle RapidAPI authentication (X-RapidAPI-Key header)
   - Parse JSearch API responses into `JobPosting` objects
   - Map 40+ JSearch fields to our `JobPosting` model
   - Implement error handling and logging

3. Test adapter locally
   - Create test script to verify RapidAPI connection
   - Test search with sample criteria
   - Verify `JobPosting` objects are created correctly
   - Test with free tier (50 requests)

**Deliverable:** Working JSearch adapter that can search for jobs via RapidAPI and return `JobPosting` objects

### Goal 2: Implement Search Orchestrator
**Priority:** HIGH
**Estimated Time:** 1-2 hours

**Tasks:**
1. Create search orchestrator (`src/search/orchestrator.py`)
   - Load configuration
   - Initialize enabled job board adapters
   - Execute searches based on criteria
   - Collect and aggregate results
   - Handle errors gracefully

2. Implement basic rate limiting (for Phase 2 preparation)
   - Simple delay between requests
   - Respect configured rate limits

3. Add logging
   - Log search start/completion
   - Log job counts per board
   - Log errors and warnings

**Deliverable:** Search orchestrator that coordinates searches across enabled boards

### Goal 3: Wire Main Entry Point
**Priority:** HIGH
**Estimated Time:** 30-60 minutes

**Tasks:**
1. Update `src/main.py`
   - Load configuration
   - Initialize orchestrator
   - Execute search
   - Write results to files
   - Log summary

2. Add command-line argument parsing (optional)
   - `--config` - Specify config file
   - `--board` - Search single board
   - `--debug` - Enable debug logging

3. Test end-to-end execution
   - Run full pipeline locally
   - Verify files are created in correct structure
   - Review output for correctness

**Deliverable:** Working end-to-end pipeline that searches Indeed and saves results

---

## Technical Details

### JSearch API Integration (via RapidAPI)

**Authentication:**
- RapidAPI Key-based authentication
- Set `RAPIDAPI_KEY` environment variable
- Add header: `X-RapidAPI-Key: ${RAPIDAPI_KEY}`
- Add header: `X-RapidAPI-Host: jsearch.p.rapidapi.com`
- Reference in `config/job-boards.yaml`: `${RAPIDAPI_KEY}`

**API Endpoint:**
```
GET https://jsearch.p.rapidapi.com/search
```

**Key Parameters:**
- `query` - Search query (keywords + location, e.g., "DevOps Engineer in Austin, TX")
- `page` - Page number (default: 1)
- `num_pages` - Number of pages to fetch (default: 1, max: 20)
- `date_posted` - Filter by posting date (all, today, 3days, week, month)
- `remote_jobs_only` - Boolean for remote-only filtering (true/false)
- `employment_types` - Filter by type (FULLTIME, CONTRACTOR, PARTTIME, INTERN)

**Response Format (40+ fields):**
```json
{
  "status": "OK",
  "request_id": "...",
  "parameters": {...},
  "data": [
    {
      "job_id": "unique-id",
      "employer_name": "Example Corp",
      "employer_logo": "https://...",
      "employer_website": "https://...",
      "employer_company_type": "Private",
      "job_publisher": "LinkedIn",
      "job_employment_type": "FULLTIME",
      "job_title": "Senior DevOps Engineer",
      "job_apply_link": "https://...",
      "job_apply_quality_score": 0.8,
      "job_description": "Full description...",
      "job_is_remote": true,
      "job_posted_at_timestamp": 1700000000,
      "job_posted_at_datetime_utc": "2025-11-15T12:00:00Z",
      "job_city": "Austin",
      "job_state": "TX",
      "job_country": "US",
      "job_latitude": 30.2672,
      "job_longitude": -97.7431,
      "job_google_link": "https://...",
      "job_offer_expiration_datetime_utc": "2025-12-15T12:00:00Z",
      "job_required_experience": {
        "no_experience_required": false,
        "required_experience_in_months": 60,
        "experience_mentioned": true,
        "experience_preferred": true
      },
      "job_required_skills": ["AWS", "Terraform", "Python"],
      "job_required_education": {
        "postgraduate_degree": false,
        "professional_certification": false,
        "high_school": false,
        "associates_degree": false,
        "bachelors_degree": true,
        "degree_mentioned": true,
        "degree_preferred": true,
        "professional_certification_mentioned": false
      },
      "job_experience_in_place_of_education": false,
      "job_min_salary": 140000,
      "job_max_salary": 180000,
      "job_salary_currency": "USD",
      "job_salary_period": "YEAR",
      "job_highlights": {
        "Qualifications": ["5+ years DevOps", "AWS certified"],
        "Responsibilities": ["Manage infrastructure", "CI/CD pipelines"],
        "Benefits": ["Health insurance", "401k"]
      },
      "job_job_title": null,
      "job_posting_language": "en",
      "job_onet_soc": "15113200",
      "job_onet_job_zone": "4",
      "job_naics_code": "541511",
      "job_naics_name": "Custom Computer Programming Services"
    }
  ]
}
```

**Mapping to JobPosting:**
- `title` ← `job_title`
- `company` ← `employer_name`
- `location` ← `f"{job_city}, {job_state}, {job_country}"`
- `remote_type` ← `"remote" if job_is_remote else "hybrid" if "hybrid" in job_description.lower() else "onsite"`
- `salary_min` ← `job_min_salary`
- `salary_max` ← `job_max_salary`
- `description` ← `job_description`
- `requirements` ← `job_required_skills + job_highlights.Qualifications`
- `posted_date` ← `datetime.fromtimestamp(job_posted_at_timestamp)`
- `job_url` ← `job_apply_link`
- `board_name` ← `"JSearch"`
- `board_job_id` ← `job_id`
- `raw_data` ← Full JSON response for debugging/future use

**Future: Adzuna Support**
The adapter interface will support adding Adzuna in Phase 2:
- Similar RESTful design
- Free tier with 14-day trial
- Different authentication (app_id + app_key)
- Different response schema but similar data points

### Search Orchestrator Flow

```python
def run_search(config: Config) -> List[JobPosting]:
    """Run search across all enabled boards."""
    # 1. Load config
    # 2. Initialize adapters for enabled boards
    # 3. For each adapter:
    #    - Execute search
    #    - Collect results
    #    - Log progress
    # 4. Aggregate and return all results
```

### Main Entry Point Flow

```python
def main():
    """Main entry point."""
    # 1. Load config
    config = load_config()

    # 2. Run search
    orchestrator = SearchOrchestrator(config)
    jobs = orchestrator.run_search()

    # 3. Write results
    writer = FileWriter()
    writer.write_jobs(jobs)

    # 4. Log summary
    print(f"Found {len(jobs)} jobs")
```

---

## Implementation Order

### Phase 1: JSearch Adapter (2-3 hours)
1. **Set up RapidAPI account** (15 min)
   - Sign up at rapidapi.com
   - Subscribe to JSearch API (use free tier: 50 requests/7 days)
   - Get RapidAPI key
   - Test API with curl or Postman

2. **Create adapter skeleton** (30 min)
   - Create `src/adapters/jsearch.py`
   - Extend `BaseAdapter`
   - Define `search()` method signature
   - Set up RapidAPI headers (X-RapidAPI-Key, X-RapidAPI-Host)

3. **Implement authentication** (20 min)
   - Load RapidAPI key from config
   - Set up request headers
   - Test authentication with simple search

4. **Implement search** (90 min)
   - Build query string from config (keywords + location)
   - Build query parameters (page, date_posted, remote_jobs_only, etc.)
   - Execute HTTP request to jsearch.p.rapidapi.com/search
   - Parse JSON response
   - Map 40+ JSearch fields to `JobPosting` objects
   - Handle pagination (if needed)

5. **Add error handling** (30 min)
   - Handle HTTP errors (rate limits, auth failures)
   - Handle parsing errors (missing fields, unexpected formats)
   - Add logging (requests, responses, errors)
   - Test with various inputs
   - Test with free tier limits

### Phase 2: Search Orchestrator (1-2 hours)
1. **Create orchestrator skeleton** (20 min)
   - Create `src/search/orchestrator.py`
   - Define `SearchOrchestrator` class
   - Define `run_search()` method

2. **Implement board initialization** (20 min)
   - Load config
   - Initialize enabled adapters
   - Handle missing adapters gracefully

3. **Implement search execution** (40 min)
   - Loop through adapters
   - Execute searches
   - Aggregate results
   - Add logging

4. **Add rate limiting** (20 min)
   - Simple delay between requests
   - Log rate limit info

### Phase 3: Main Entry Point (30-60 min)
1. **Update main.py** (30 min)
   - Load config
   - Initialize orchestrator
   - Execute search
   - Write results
   - Log summary

2. **Add CLI arguments** (optional) (20 min)
   - Parse arguments
   - Override config as needed

3. **Test end-to-end** (30 min)
   - Run full pipeline
   - Verify output
   - Test error cases

---

## Testing Strategy

### Unit Testing (Defer to Phase 7)
For Phase 1, manual testing is sufficient. Unit tests will be added in Phase 7.

### Manual Testing

**Test 1: JSearch Adapter**
```python
# Test script: test_jsearch_adapter.py
from src.adapters.jsearch import JSearchAdapter
from src.config.loader import load_config

config = load_config()
adapter = JSearchAdapter(config)
jobs = adapter.search()
print(f"Found {len(jobs)} jobs")
for job in jobs[:3]:
    print(f"- {job.title} at {job.company}")
    print(f"  Location: {job.location}")
    print(f"  Remote: {job.remote_type}")
    print(f"  Salary: ${job.salary_min:,} - ${job.salary_max:,}" if job.salary_min else "  Salary: Not disclosed")
    print()
```

**Test 2: Search Orchestrator**
```python
# Test script: test_orchestrator.py
from src.search.orchestrator import SearchOrchestrator
from src.config.loader import load_config

config = load_config()
orchestrator = SearchOrchestrator(config)
jobs = orchestrator.run_search()
print(f"Found {len(jobs)} jobs across all boards")
```

**Test 3: End-to-End**
```bash
# Set environment variable
export RAPIDAPI_KEY="your-rapidapi-key"

# Run pipeline
python src/main.py

# Check output
ls -la jobs/pipeline/$(date +%Y-%m-%d)/

# Verify file contents
cat jobs/pipeline/$(date +%Y-%m-%d)/*.txt | head -50
```

---

## PR Strategy

### When to Create PR #2

After completing all three goals:
- ✅ Indeed adapter working
- ✅ Search orchestrator working
- ✅ Main entry point working
- ✅ End-to-end test successful

**PR Title:** "Phase 1: Job Board Adapter, Search Orchestrator, and Main Entry Point"

**PR Description:**
- Overview of changes
- Indeed adapter implementation
- Search orchestrator implementation
- Main entry point wiring
- Testing considerations
- Next steps (Phase 2)

**Estimated PR Size:** 400-600 lines (reasonable for review)

---

## Questions Resolved

### 1. ✅ Job Board API Selection
- **Decision:** JSearch via RapidAPI (not Indeed - deprecated)
- **Free Tier:** 50 requests over 7 days for testing
- **Paid Tier:** $10-50/month for 10,000-50,000 requests
- **Setup:** Create RapidAPI account, subscribe to JSearch

### 2. ✅ Future API Support
- **Phase 1:** JSearch only
- **Phase 2:** Add Adzuna (best free alternative)
- **Architecture:** Design for multi-API from start

### 3. Search Criteria
- Use config/search-criteria.yaml as-is
- JSearch combines keywords + location in single query string
- **Example:** "DevOps Engineer in Austin, TX"

### 4. Rate Limiting
- JSearch: 20 requests/second on paid tiers
- Implement simple delay for Phase 1
- Full rate limiter in Phase 2
- **Recommendation:** Simple delay (0.5-1 second between requests)

### 5. Logging
- Use Python `logging` module from start
- Log requests, responses, errors
- **Recommendation:** INFO level for normal operation, DEBUG for development

---

## Success Criteria

### Phase 1 Complete When:
- ✅ JSearch adapter can search via RapidAPI and return jobs
- ✅ JSearch adapter correctly maps 40+ fields to `JobPosting`
- ✅ Search orchestrator coordinates searches
- ✅ Main entry point executes full pipeline
- ✅ Jobs are saved to `jobs/pipeline/YYYY-MM-DD/`
- ✅ End-to-end test successful with free tier (50 requests)
- ✅ Code follows project conventions
- ✅ Ready for PR #2 review

---

## Next Steps After Phase 1

**Phase 2: Multi-Board Support**
- Add Adzuna adapter (best free alternative to JSearch)
- Add RemoteOK adapter (50,000+ remote jobs, free)
- Add Remotive adapter (2,000+ curated remote jobs, free)
- Implement full rate limiting with exponential backoff
- Add parallel search execution
- Comprehensive error handling

**Note:** LinkedIn, Indeed, Glassdoor, and Wellfound APIs are deprecated or don't exist for job search

**Phase 3: Deduplication & Filtering**
- Implement deduplication logic
- Add filtering rules
- Track processed jobs

---

## Notes

- Keep PR #2 focused and reviewable (~400-600 lines)
- Follow conventional commit format
- Update Linear TT-45 with progress
- Update CLAUDE.md after PR #2 merge
- Address gemini-code-assist feedback promptly

---

**Created:** November 19, 2025
**Status:** Ready to begin implementation
**Estimated Session Time:** 4-6 hours
