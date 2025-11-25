# Session Agenda - Tuesday, November 25, 2025

**Project:** Job Search Pipeline Development
**Focus:** Phase 3 Planning - AI Evaluation
**Linear Issue:** [TT-48](https://linear.app/davidshaevel-dot-com/issue/TT-48) - Phase 3: AI Evaluation

---

## Session Overview

With Phase 2 (Deduplication & Filtering) now merged and complete, this session focuses on planning and preparing for Phase 3: AI Evaluation.

**Phase Reorganization (Nov 25):**
- **OLD:** Phase 3 = Multi-Board Support, Phase 4 = AI Evaluation
- **NEW:** Phase 3 = AI Evaluation (TT-48), Phase 4 = Multi-Board Support (TT-47)
- **Rationale:** Prioritize AI evaluation to enable better analysis of jobs from the single JSearch source before adding more job boards

**Previous Session Accomplishments (Nov 24):**
- Resolved all Gemini Round 2 code review issues (7 fixes)
- PR #4 merged to main
- Phase 2 complete

---

## Priorities

### 1. Phase 3 Planning (HIGH - 60 min)

**Goal:** Create detailed implementation plan for AI evaluation

**Tasks:**
- [ ] Review Phase 3 requirements from PLAN.md
- [ ] Design evaluation prompt templates for Claude API
- [ ] Define 8-factor rubric implementation details
- [ ] Plan score calculation and grading logic
- [ ] Design evaluation result storage format
- [ ] Define success criteria for Phase 3

**Key Considerations:**
- Claude API integration (model selection, token limits, cost)
- Prompt engineering for accurate job evaluation
- Structured output parsing (JSON or structured format)
- Handling incomplete job descriptions
- Confidence scoring for evaluation quality

### 2. Evaluation Framework Design (MEDIUM - 45 min)

**Goal:** Design the AI evaluation engine architecture

**Tasks:**
- [ ] Review existing 8-factor rubric from `docs/evaluation_rubric.md`
- [ ] Design prompt template structure
- [ ] Plan scoring normalization (0-100 scale)
- [ ] Design grade assignment logic (A/B/C/D/F)
- [ ] Plan evaluation caching/deduplication
- [ ] Design evaluation result schema

**8-Factor Rubric:**
1. Skills & Experience Match (25%)
2. Compensation & Benefits (20%)
3. Company Stability & Growth (15%)
4. Work-Life Balance (15%)
5. Career Growth & Learning (10%)
6. Culture & Team Fit (8%)
7. Role Clarity & Expectations (5%)
8. Location & Commute (2%)

### 3. Claude API Integration Planning (MEDIUM - 30 min)

**Goal:** Plan Claude API integration details

**Tasks:**
- [ ] Select Claude model (Sonnet 4.5 recommended for cost/quality)
- [ ] Design API client wrapper
- [ ] Plan rate limiting for API calls
- [ ] Design error handling and retry logic
- [ ] Estimate cost per evaluation
- [ ] Plan batch processing strategy

**API Considerations:**
- Model: claude-sonnet-4-5-20250929 (recommended)
- Token limits: Input/output constraints
- Cost optimization: Batch vs individual evaluations
- Error handling: Rate limits, API errors, timeouts

### 4. Linear Updates (LOW - 15 min)

**Goal:** Update Linear with Phase 3 planning details

**Tasks:**
- [ ] Update TT-48 with implementation plan
- [ ] Add sub-tasks for each component
- [ ] Update project status
- [ ] Set estimated timeline

---

## Technical Notes

### Phase 3 Scope (from PLAN.md)

**AI Evaluation includes:**
1. Integrate Claude API
2. Build evaluation prompt templates
3. Implement rubric application
4. Score calculation and grading
5. Evaluation result storage
6. Confidence scoring

### Evaluation Result Schema (Example)

```json
{
  "job_id": "some-job-id-123",
  "evaluation_timestamp": "2025-11-26T10:00:00Z",
  "model": "claude-sonnet-4-5-20250929",
  "scores": {
    "skills_match": {"score": 85, "weight": 0.25, "reasoning": "Strong alignment with required skills..."},
    "compensation": {"score": 75, "weight": 0.20, "reasoning": "Salary is within market range..."},
    "stability": {"score": 90, "weight": 0.15, "reasoning": "Company is well-funded..."},
    "work_life_balance": {"score": 80, "weight": 0.15, "reasoning": "Standard PTO and flexible hours mentioned..."},
    "career_growth": {"score": 82, "weight": 0.10, "reasoning": "Clear path for advancement..."},
    "culture_fit": {"score": 78, "weight": 0.08, "reasoning": "Company values align with profile..."},
    "role_clarity": {"score": 70, "weight": 0.05, "reasoning": "Responsibilities are somewhat vague..."},
    "location": {"score": 95, "weight": 0.02, "reasoning": "Fully remote role matches preference..."}
  },
  "overall_score": 82.46,
  "grade": "B",
  "confidence": 0.95,
  "summary": "A strong opportunity with good alignment on skills and company stability, though role clarity could be better.",
  "recommendation": "pursue"
}
```

### Success Metrics for Phase 3

- [ ] Claude API integration working
- [ ] All 8 evaluation factors implemented
- [ ] Scores calculated with weighted averages
- [ ] Grades assigned based on thresholds
- [ ] Evaluation results saved to JSON
- [ ] Confidence scoring implemented
- [ ] Integration test with real job data

---

## Files to Reference

- `PLAN.md` - Full implementation plan
- `docs/evaluation_rubric.md` - 8-factor evaluation framework
- `src/filters/filter_engine.py` - Reference for pipeline integration
- `config/evaluation-thresholds.yaml` - Scoring thresholds config
- Anthropic API docs: https://docs.anthropic.com/

---

## Questions to Address

1. Should evaluations be synchronous or async/batch?
2. How to handle jobs with missing information (salary, benefits)?
3. Should we cache evaluations to avoid re-evaluating unchanged jobs?
4. What confidence threshold triggers manual review?
5. How to validate evaluation accuracy?

---

## End of Session Goals

By the end of this session:
1. Clear implementation plan for Phase 3
2. Evaluation prompt template drafted
3. Result schema finalized
4. Linear TT-48 updated with plan
5. Ready to begin Phase 3 implementation
