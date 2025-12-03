# Tuesday December 2, 2025 - Work Session Agenda

**Date:** Tuesday, December 2, 2025
**Focus:** Phase 3 Integration - Wire Evaluator into Pipeline
**Branch:** `david/tt-48-phase3-integration-dec2`
**Linear Issue:** [TT-48](https://linear.app/davidshaevel-dot-com/issue/TT-48)

---

## Session Goals

Complete the Phase 3 integration work:
1. **Integration** - Wire `AIEvaluator` into `SearchOrchestrator` pipeline
2. **Storage** - Save `EvaluationResult` JSON files alongside job files
3. **End-to-End Test** - Test with real JSearch job data

---

## Context: Phase 3 Core Implementation Complete

**PR #8 Merged (Dec 2, 2025):**
- `EvaluationResult`, `FactorScore`, `Grade` models
- `PromptBuilder` for structured evaluation prompts
- `AIEvaluator` with Claude Sonnet 4.5 integration
- `config/user-profile.yaml` for candidate preferences
- 50 unit tests (31 new + 19 existing)
- Three rounds of Gemini code review completed

**What's Missing:**
- Evaluator is not yet wired into the search pipeline
- Evaluation results are not persisted to disk
- No end-to-end test with real job data

---

## Task 1: Integration - Wire AIEvaluator into SearchOrchestrator

**Goal:** Add optional evaluation step to `SearchOrchestrator.search()` pipeline

**Approach:**
1. Add `evaluate_results: bool = False` parameter to `SearchOrchestrator.search()`
2. If `evaluate_results=True`, instantiate `AIEvaluator` and call `evaluate_jobs()`
3. Return both `JobPosting` list and optional `EvaluationResult` list

**Files to Modify:**
- `src/search/orchestrator.py` - Add evaluation step
- `src/search/__init__.py` - Update exports if needed

**Considerations:**
- Keep evaluation optional (don't break existing behavior)
- Handle evaluation errors gracefully (continue_on_error=True)
- Log evaluation progress and results
- Consider cost estimation before running (user confirmation?)

**Sample Code:**
```python
# In SearchOrchestrator.search()
if evaluate_results:
    from evaluation import AIEvaluator
    evaluator = AIEvaluator(user_profile=self.config.get("user_profile"))
    evaluations = evaluator.evaluate_jobs(filtered_jobs, continue_on_error=True)
    return SearchResult(jobs=filtered_jobs, evaluations=evaluations)
```

---

## Task 2: Storage - Save Evaluation Results

**Goal:** Persist `EvaluationResult` objects to JSON files

**Approach:**
1. Create `EvaluationWriter` class in `src/evaluation/writer.py`
2. Save as `{company}_{job_title}_evaluation.json` alongside job files
3. Include both structured data and human-readable summary

**File Structure:**
```
jobs/pipeline/2025-12-02/
├── company_a_senior_devops_engineer.txt        # Job posting
├── company_a_senior_devops_engineer_eval.json  # Evaluation result
├── company_b_platform_engineer.txt
└── company_b_platform_engineer_eval.json
```

**JSON Schema:**
```json
{
  "job_id": "abc123",
  "job_title": "Senior DevOps Engineer",
  "company": "Company A",
  "evaluation_timestamp": "2025-12-02T10:30:00",
  "model": "claude-sonnet-4-5-20250929",
  "overall_score": 85.5,
  "grade": "B",
  "recommendation": "pursue",
  "factor_scores": {
    "skills_match": {"score": 90, "reasoning": "..."},
    ...
  },
  "summary": "...",
  "strengths": ["...", "..."],
  "concerns": ["...", "..."],
  "confidence": 0.85
}
```

**Files to Create/Modify:**
- `src/evaluation/writer.py` - New file for `EvaluationWriter`
- `src/evaluation/__init__.py` - Export `EvaluationWriter`
- `tests/test_evaluation.py` - Add tests for `EvaluationWriter`

---

## Task 3: End-to-End Test

**Goal:** Validate full pipeline with real JSearch data

**Test Plan:**
1. Run JSearch query with small result set (5-10 jobs)
2. Filter through `FilterEngine`
3. Evaluate remaining jobs with `AIEvaluator`
4. Save results to `jobs/pipeline/2025-12-02/`
5. Verify JSON files are valid and complete

**Command:**
```bash
# Test search + evaluation
PYTHONPATH=src python src/main.py --evaluate --limit 5
```

**Verification Checklist:**
- [ ] Jobs fetched from JSearch
- [ ] Duplicates filtered out
- [ ] Evaluations generated with valid scores
- [ ] JSON files saved correctly
- [ ] Human-readable summary in output

---

## Time Estimates

| Task | Estimated Time |
|------|----------------|
| Task 1: Integration | 1-2 hours |
| Task 2: Storage | 1-2 hours |
| Task 3: End-to-End Test | 1 hour |
| **Total** | **3-5 hours** |

---

## Success Criteria

1. ✅ `SearchOrchestrator.search(evaluate_results=True)` works
2. ✅ `EvaluationWriter.write()` saves JSON files
3. ✅ End-to-end test completes successfully
4. ✅ All tests pass (50+ tests)
5. ✅ Code reviewed and ready for PR

---

## Notes

- **ANTHROPIC_API_KEY** required for real evaluations
- Cost estimate: ~$0.01 per job evaluation (2000 input + 800 output tokens)
- For testing, consider mocking API calls initially
- Real API calls should be done with small batches first

---

## PR Readiness Checklist

When ready for PR:
- [ ] All new code has tests
- [ ] Documentation updated (TESTING_PHASE3.md)
- [ ] No hardcoded paths or secrets
- [ ] Error handling is robust
- [ ] Logging is informative
- [ ] README.md updated if needed
