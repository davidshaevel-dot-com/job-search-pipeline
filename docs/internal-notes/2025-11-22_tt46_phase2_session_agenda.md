# Work Session Agenda - Saturday, November 22, 2025
## Phase 2: Deduplication & Filtering (TT-46)

**Date:** Saturday, November 22, 2025
**Linear Issue:** [TT-46 - Phase 2: Deduplication & Filtering](https://linear.app/davidshaevel-dot-com/issue/TT-46)
**Branch:** `david/tt-46-phase-2-deduplication-filtering`
**Status:** Starting Phase 2 implementation

---

## Session Goals

**Primary Goal:** Implement deduplication and filtering system to remove duplicate jobs and filter unwanted opportunities.

**Why This Phase Matters:**
- Better to perfect filtering with single data source (JSearch from Phase 1) before adding more boards
- Deduplication logic is simpler with one source initially
- Multi-board support (Phase 3) will multiply data volume, so filtering must be robust first
- Follows YAGNI principle - start simple, add complexity when needed

---

## Linear Issue Overview

**TT-46 Tasks:**
1. ⏳ Implement deduplication logic
2. ⏳ Company blacklist filtering
3. ⏳ Title/keyword filtering
4. ⏳ Similarity matching (fuzzy)
5. ⏳ Track processed jobs to avoid re-processing

**Deliverables:**
- Deduplication system
- Filtering rules engine
- Processed jobs database/cache

---

## Implementation Plan

### Part 1: Project Setup (15 minutes)

**Tasks:**
1. ✅ Checkout main and pull latest changes
2. ⏳ Create feature branch: `david/tt-46-phase-2-deduplication-filtering`
3. ⏳ Update Linear TT-46 status to "In Progress"
4. ⏳ Review existing config: `config/filters.yaml`
5. ⏳ Review Phase 2 requirements in PLAN.md

**Files to Review:**
- `config/filters.yaml` - Existing filter configuration
- `PLAN.md` - Phase 2 details (lines 602-617)
- `src/core/models.py` - JobPosting dataclass

---

### Part 2: Core Architecture Design (30 minutes)

**Component 1: Deduplication Engine**
- Location: `src/filtering/deduplicator.py`
- Responsibilities:
  - Fuzzy title matching (85% similarity threshold)
  - Exact company name matching
  - Board-specific job ID tracking
  - Composite key generation for uniqueness

**Component 2: Filter Engine**
- Location: `src/filtering/filter_engine.py`
- Responsibilities:
  - Company blacklist filtering
  - Title/keyword blacklist filtering
  - Complex search criteria filtering (salary, experience, tech stack)
  - Configurable filter rules from YAML

**Component 3: Processed Jobs Tracker**
- Location: `src/filtering/job_tracker.py`
- Responsibilities:
  - Track processed job IDs (prevent re-processing)
  - Persistence to JSON file: `data/processed_jobs.json`
  - Efficient lookup (set-based or dict-based)

**Component 4: Filter Orchestrator**
- Location: `src/filtering/orchestrator.py`
- Responsibilities:
  - Coordinate deduplication and filtering
  - Apply filters in correct order
  - Return filtered job list

**Design Decisions:**
- Use `fuzzywuzzy` library for string similarity (already in requirements.txt)
- Store processed jobs in JSON for simplicity (Phase 1 approach)
- Use dataclass for filter results to track why jobs were filtered
- Keep filters stateless and testable

---

### Part 3: Implementation - Deduplication (1.5 hours)

**Step 1: Create Base Infrastructure**
```python
# src/filtering/__init__.py
# src/filtering/deduplicator.py
# src/filtering/models.py (FilterResult dataclass)
```

**Step 2: Implement Fuzzy Title Matching**
- Use `fuzzywuzzy.fuzz.ratio()` for similarity
- 85% threshold from config
- Case-insensitive matching

**Step 3: Implement Company Name Matching**
- Exact match (case-insensitive)
- Handle company name variations (Inc., LLC, etc.)

**Step 4: Implement Job ID Tracking**
- Track board_name + board_job_id composite key
- Prevent duplicates from same board

**Step 5: Composite Deduplication**
- Combine all three methods
- Return first duplicate found (with reason)

**Testing Approach:**
- Unit tests for each deduplication method
- Test cases with known duplicates
- Edge cases: empty strings, None values, special characters

---

### Part 4: Implementation - Filtering (1.5 hours)

**Step 1: Company Blacklist Filter**
```python
# src/filtering/filter_engine.py
class FilterEngine:
    def filter_by_company_blacklist(self, jobs: List[JobPosting]) -> List[JobPosting]
    def filter_by_title_blacklist(self, jobs: List[JobPosting]) -> List[JobPosting]
    def filter_by_keyword_blacklist(self, jobs: List[JobPosting]) -> List[JobPosting]
    def filter_by_search_criteria(self, jobs: List[JobPosting]) -> List[JobPosting]  # NEW
```

**Step 2: Title Blacklist Filter**
- Check job title against blacklist
- Case-insensitive matching
- Partial match support ("Junior" matches "Junior Engineer")

**Step 3: Keyword Blacklist Filter**
- Check job description for blacklisted keywords
- Case-insensitive matching
- Full-word matching (not substring)

**Step 4: Complex Search Criteria Filter (NEW)**
- Support `search-criteria-complex.yaml` structure
- Salary range filtering (min/max)
- Experience level matching
- Tech stack matching (required vs preferred)
- Company stage filtering
- Location preference scoring

**Configuration Loading:**
- Load from `config/filters.yaml`
- Load from `config/search-criteria-complex.yaml`
- Use existing Config class pattern from Phase 1
- Default values if config missing

---

### Part 5: Implementation - Job Tracker (45 minutes)

**Step 1: Processed Jobs Storage**
```python
# src/filtering/job_tracker.py
class JobTracker:
    def __init__(self, storage_path: Path)
    def is_processed(self, job: JobPosting) -> bool
    def mark_processed(self, job: JobPosting) -> None
    def load_from_disk(self) -> None
    def save_to_disk(self) -> None
```

**Step 2: JSON Persistence**
- File: `data/processed_jobs.json`
- Format: `{"job_id": {"board": "...", "company": "...", "title": "...", "processed_at": "..."}}`
- Create `data/` directory if doesn't exist

**Step 3: Efficient Lookup**
- Use set for O(1) lookup
- Generate composite key: `f"{board_name}:{board_job_id}"`
- Lazy load on first access

---

### Part 6: Implementation - Orchestrator (45 minutes)

**Step 1: Filter Orchestrator**
```python
# src/filtering/orchestrator.py
class FilterOrchestrator:
    def __init__(self, config: Config)
    def filter_and_deduplicate(self, jobs: List[JobPosting]) -> FilteredJobsResult
```

**Step 2: Filter Pipeline**
Order of operations:
1. Remove already-processed jobs (job tracker)
2. Apply company blacklist filter (fast exact match)
3. Apply title blacklist filter (fast exact/partial match)
4. Apply keyword blacklist filter (slower - searches description)
5. Apply complex search criteria filter (salary, experience, tech stack)
6. Apply deduplication (slowest - fuzzy matching)
7. Mark surviving jobs as processed

**Step 3: Results Tracking**
```python
@dataclass
class FilteredJobsResult:
    accepted_jobs: List[JobPosting]
    rejected_jobs: List[RejectedJob]
    total_input: int
    total_accepted: int
    total_rejected: int
```

```python
@dataclass
class RejectedJob:
    job: JobPosting
    reason: str  # "already_processed", "company_blacklist", "duplicate", etc.
```

---

### Part 7: Integration with Phase 1 (30 minutes)

**Update main.py:**
```python
# After search orchestrator returns jobs
from filtering.orchestrator import FilterOrchestrator

filter_orchestrator = FilterOrchestrator(config)
filter_result = filter_orchestrator.filter_and_deduplicate(jobs)

# Only write accepted jobs
writer.write_jobs(filter_result.accepted_jobs)

# Log filter statistics
logger.info(f"Filtered {filter_result.total_rejected} jobs")
logger.info(f"Accepted {filter_result.total_accepted} jobs")
```

**Update Config to Load Filters:**
```python
# src/core/config.py
class Config:
    @property
    def filters(self) -> dict:
        return self.data.get('filters', {})
```

---

### Part 8: Testing (1 hour)

**Unit Tests:**
- `tests/test_deduplicator.py`
  - Test fuzzy title matching
  - Test company matching
  - Test job ID matching
  - Test edge cases

- `tests/test_filter_engine.py`
  - Test company blacklist
  - Test title blacklist
  - Test keyword blacklist

- `tests/test_job_tracker.py`
  - Test persistence
  - Test lookup performance
  - Test concurrent access (future)

- `tests/test_filter_orchestrator.py`
  - Test full pipeline
  - Test filter order
  - Test results tracking

**Integration Test:**
```bash
# Run with Phase 1 pipeline
python src/main.py
# Should see filter statistics in output
```

**Test Data:**
- Create sample jobs with known duplicates
- Create jobs with blacklisted companies
- Create jobs with blacklisted titles

---

### Part 9: Documentation (30 minutes)

**Files to Create/Update:**
1. `docs/filtering-system.md` - Architecture and usage guide
2. `config/filters.yaml` - Add comments explaining options
3. `PLAN.md` - Update Phase 2 task checkboxes
4. `README.md` - Add filtering system to features list
5. Code docstrings - Comprehensive docstrings for all classes

**Documentation Content:**
- How deduplication works
- How to configure filters
- How to add custom filter rules
- Performance considerations
- Examples

---

### Part 10: Code Review & PR (30 minutes)

**Pre-PR Checklist:**
- [ ] All unit tests passing
- [ ] Integration test passing
- [ ] Code follows project conventions
- [ ] Docstrings complete
- [ ] Type hints added
- [ ] No hardcoded values
- [ ] Error handling complete
- [ ] Logging added

**PR Creation:**
1. Commit all changes with conventional commits
2. Push branch to origin
3. Create PR with comprehensive description
4. Request gemini-code-assist review
5. Address feedback

**PR Description Template:**
```markdown
## Summary
Implements Phase 2 deduplication and filtering system.

## Changes
- Deduplication engine (fuzzy matching, company, job ID)
- Filter engine (blacklist filtering)
- Job tracker (processed jobs persistence)
- Filter orchestrator (pipeline coordination)
- Integration with Phase 1 pipeline

## Testing
- Unit tests for all components
- Integration test with full pipeline
- Sample data validation

## Related Issues
- TT-46
```

---

## File Structure (New Files)

```
job-search-pipeline/
├── src/
│   └── filtering/                    # NEW
│       ├── __init__.py
│       ├── deduplicator.py          # Deduplication logic
│       ├── filter_engine.py         # Blacklist filtering
│       ├── job_tracker.py           # Processed jobs tracking
│       ├── orchestrator.py          # Filter pipeline coordination
│       └── models.py                # FilterResult, RejectedJob dataclasses
├── tests/
│   ├── test_deduplicator.py        # NEW
│   ├── test_filter_engine.py       # NEW
│   ├── test_job_tracker.py         # NEW
│   └── test_filter_orchestrator.py # NEW
├── data/
│   └── processed_jobs.json         # NEW - Processed jobs cache
└── docs/
    └── filtering-system.md          # NEW - Documentation
```

---

## Success Metrics

**Functional:**
- [ ] Duplicates successfully removed (fuzzy + exact matching)
- [ ] Blacklisted companies filtered out
- [ ] Blacklisted titles filtered out
- [ ] Blacklisted keywords filtered out
- [ ] Processed jobs tracked and skipped on re-run
- [ ] Filter statistics logged
- [ ] All tests passing

**Quality:**
- [ ] Code coverage > 80% for filtering module
- [ ] Type hints on all public methods
- [ ] Comprehensive docstrings
- [ ] No pylint/mypy errors
- [ ] Performance: Filter 1000 jobs in < 1 second

**Documentation:**
- [ ] Architecture documented
- [ ] Usage examples provided
- [ ] Configuration options explained
- [ ] Edge cases documented

---

## Technical Decisions

### Why fuzzywuzzy for similarity?
- Industry standard for fuzzy string matching
- Simple API: `fuzz.ratio(str1, str2)` returns 0-100
- Already in requirements.txt
- Good balance of speed and accuracy

### Why JSON for processed jobs?
- Simple, human-readable format
- No external database dependency (YAGNI)
- Easy to inspect and debug
- Fast enough for expected volume (< 10K jobs)
- Can migrate to SQLite in Phase 7 if needed

### Why separate deduplicator and filter engine?
- Single Responsibility Principle
- Easier to test independently
- Different use cases (dedup = within results, filter = against rules)
- Allows different implementations later

### Filter Order Rationale
1. **Already processed** - Most efficient, eliminates work
2. **Company blacklist** - Fast exact match
3. **Title blacklist** - Fast exact/partial match
4. **Keyword blacklist** - Slower (searches description)
5. **Complex search criteria** - Medium speed (salary, experience, tech stack matching)
6. **Deduplication** - Slowest (fuzzy matching)

### Complex Search Criteria Support

**Why This Matters:**
- `search-criteria-complex.yaml` contains rich filtering rules saved during Phase 1
- Enables more sophisticated job filtering beyond simple blacklists
- Allows salary range, experience level, tech stack, and company stage filtering

**Implementation Approach:**
```python
class FilterEngine:
    def filter_by_search_criteria(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Filter jobs based on complex search criteria."""
        filtered = []
        for job in jobs:
            # Salary range check
            if not self._matches_salary_range(job):
                continue

            # Experience level check
            if not self._matches_experience_level(job):
                continue

            # Required tech stack check
            if not self._has_required_tech(job):
                continue

            # Company stage filter
            if not self._matches_company_stage(job):
                continue

            filtered.append(job)
        return filtered
```

**Criteria Supported:**
1. **Salary Range** - Filter by min/max salary expectations
2. **Experience Level** - Match "Senior", "Staff", "Lead", "Principal"
3. **Tech Stack** - Required (must have) vs Preferred (nice to have)
4. **Company Stage** - Exclude "Pre-seed", prefer "Series A+", "Profitable"
5. **Location** - Prefer "Austin, TX", "Remote", accept "Hybrid"

**Configuration Loading:**
```python
# src/core/config.py
class Config:
    @property
    def search_criteria(self) -> dict:
        """Load search-criteria-complex.yaml if it exists."""
        complex_path = self.config_dir / "search-criteria-complex.yaml"
        if complex_path.exists():
            return yaml.safe_load(complex_path.read_text())
        return self.data.get('search', {})
```

**Testing Complex Criteria:**
- Test salary filtering (min, max, missing salary data)
- Test experience level matching (title parsing)
- Test tech stack matching (required vs preferred)
- Test company stage filtering
- Test location preference scoring

---

## Time Estimates

| Task | Estimated Time | Notes |
|------|---------------|-------|
| Part 1: Setup | 15 min | Quick setup |
| Part 2: Design | 30 min | Architecture planning |
| Part 3: Deduplication | 1.5 hours | Core logic + tests |
| Part 4: Filtering | 1.5 hours | Blacklist filters + complex criteria |
| Part 5: Job Tracker | 45 min | Persistence layer |
| Part 6: Orchestrator | 45 min | Pipeline coordination |
| Part 7: Integration | 30 min | Wire into main.py |
| Part 8: Testing | 1.5 hours | Comprehensive tests + complex criteria |
| Part 9: Documentation | 30 min | Docs and comments |
| Part 10: PR | 30 min | Review and submit |
| **Total** | **~8 hours** | Full day session |

**Break Schedule:**
- After Part 3 (15 min break)
- After Part 5 (15 min break)
- After Part 8 (lunch/longer break)

---

## Dependencies & Prerequisites

**Required:**
- ✅ Phase 1 complete (JSearch adapter working)
- ✅ `fuzzywuzzy` in requirements.txt
- ✅ `config/filters.yaml` exists
- ✅ `src/core/models.py` has JobPosting dataclass

**Optional:**
- Sample job data for testing (can use Phase 1 results)
- Real duplicate examples from JSearch

---

## Potential Challenges & Solutions

**Challenge 1: Fuzzy matching too slow**
- **Solution:** Implement caching, use faster algorithm, or limit comparisons
- **Mitigation:** Profile first, optimize only if needed

**Challenge 2: Job ID not unique across boards**
- **Solution:** Use composite key `{board}:{job_id}`
- **Status:** Already planned in design

**Challenge 3: Blacklist config too rigid**
- **Solution:** Support regex patterns in future phase
- **Status:** Start simple, iterate based on usage

**Challenge 4: JSON file grows too large**
- **Solution:** Implement rotation (keep last N days)
- **Status:** Can add in Phase 7 if needed

---

## Post-Session Deliverables

**Code:**
- [ ] 5 new Python modules in `src/filtering/`
- [ ] 4 test files with comprehensive coverage
- [ ] Updated `src/main.py` with filter integration

**Documentation:**
- [ ] `docs/filtering-system.md` - Architecture guide
- [ ] Updated docstrings throughout
- [ ] Updated PLAN.md with completed tasks

**Git:**
- [ ] Feature branch created and pushed
- [ ] All commits use conventional commit format
- [ ] PR created with comprehensive description

**Linear:**
- [ ] TT-46 status updated to "In Progress" → "In Review"
- [ ] Comment added with implementation summary

---

## Next Steps (After This Session)

**If PR Approved:**
1. Merge PR #4 (or whatever number)
2. Update Linear TT-46 to "Done"
3. Move to Phase 3: Multi-Board Support (TT-47)

**If Changes Requested:**
1. Address gemini-code-assist feedback
2. Push updates to PR branch
3. Re-request review

**Future Enhancements (Not This Phase):**
- Regex pattern matching for blacklists
- ML-based duplicate detection
- Performance optimization for large datasets
- SQLite database for processed jobs
- Web UI for blacklist management

---

## References

**Code:**
- `src/core/models.py` - JobPosting dataclass
- `src/core/config.py` - Config loading pattern
- `config/filters.yaml` - Filter configuration

**Documentation:**
- `PLAN.md` - Phase 2 requirements (lines 602-617)
- `docs/BEST_JOB_SEARCH_APIS.md` - API research

**External:**
- fuzzywuzzy docs: https://github.com/seatgeek/fuzzywuzzy
- Python pathlib: https://docs.python.org/3/library/pathlib.html

---

**Status:** Ready to begin implementation! 🚀
**Linear Issue:** [TT-46](https://linear.app/davidshaevel-dot-com/issue/TT-46)
**Estimated Completion:** End of day (7 hours total)
