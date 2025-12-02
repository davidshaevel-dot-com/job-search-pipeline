# Session Agenda - Monday, December 1, 2025

**Project:** Job Search Pipeline Development
**Focus:** Phase 3 Implementation - AI Evaluation Engine
**Linear Issue:** [TT-48](https://linear.app/davidshaevel-dot-com/issue/TT-48) - Phase 3: AI Evaluation
**Branch:** `david/tt-48-phase3-ai-evaluation`

---

## Session Overview

Phase 2 (Deduplication & Filtering) is complete and merged. This session begins Phase 3 implementation: building the AI Evaluation Engine that uses Claude API to automatically evaluate job opportunities using the 8-factor weighted rubric.

**Previous Session (Nov 25):**
- Phase reorganization completed (swapped Phase 3 and Phase 4)
- Docs reorganization merged (PR #7)
- Planning documents created for Phase 3

**Repository Status:**
- Branch: `david/tt-48-phase3-ai-evaluation` (created today)
- Main is up-to-date with all Phase 2 work merged

---

## Phase 3 Implementation Plan

### Core Components to Build

1. **AI Evaluator** (`src/evaluation/ai_evaluator.py`)
   - Claude API integration using `anthropic` SDK
   - Evaluation prompt engineering
   - Response parsing and validation
   - Error handling and retry logic

2. **Rubric Applicator** (`src/evaluation/rubric_applicator.py`)
   - 8-factor weighted scoring implementation
   - Score normalization (0-100 scale)
   - Grade assignment (A/B/C/D/F)
   - Weighted average calculation

3. **Prompt Builder** (`src/evaluation/prompt_builder.py`)
   - Structured prompt templates for job evaluation
   - Context injection (job details, rubric, user profile)
   - Output format specification (JSON)

4. **Result Storage** (`src/evaluation/models.py`)
   - `EvaluationResult` dataclass
   - Per-factor score storage with reasoning
   - Overall score, grade, and recommendation
   - Confidence scoring

5. **Integration** - Update orchestrator and main.py
   - Add evaluation step after filtering
   - Save evaluation results with job files

---

## Today's Goals

### Goal 1: Project Setup (15 min)

**Tasks:**
- [x] Create feature branch `david/tt-48-phase3-ai-evaluation`
- [x] Review existing code structure
- [ ] Add `anthropic` to requirements.txt
- [ ] Update TT-48 status to "In Progress"

### Goal 2: Core Models (30 min)

**Tasks:**
- [ ] Create `src/evaluation/models.py` with:
  - `FactorScore` dataclass (score, weight, reasoning)
  - `EvaluationResult` dataclass (all 8 factors, overall, grade, confidence)
- [ ] Define grading thresholds (A: 90+, B: 80-89, C: 70-79, D: 60-69, F: <60)

**Schema (Example):**
```python
@dataclass
class FactorScore:
    factor_name: str
    score: int  # 0-100
    weight: float  # e.g., 0.25 for 25%
    reasoning: str

@dataclass
class EvaluationResult:
    job_id: str
    evaluation_timestamp: datetime
    model: str  # e.g., "claude-sonnet-4-5-20250929"
    scores: Dict[str, FactorScore]  # 8 factors
    overall_score: float
    grade: str  # A/B/C/D/F
    confidence: float  # 0.0-1.0
    summary: str
    recommendation: str  # "strongly_pursue", "pursue", "consider", "skip"
    raw_response: Optional[str] = None  # For debugging
```

### Goal 3: Prompt Builder (45 min)

**Tasks:**
- [ ] Create `src/evaluation/prompt_builder.py`
- [ ] Design system prompt with rubric criteria
- [ ] Design user prompt template for job details
- [ ] Define JSON output schema
- [ ] Handle missing job information gracefully

**Key Prompt Elements:**
1. **System Prompt:**
   - Role definition (expert job evaluator)
   - Evaluation rubric with all 8 factors and weights
   - Scoring guidelines (0-100 scale per factor)
   - Output format requirements (strict JSON)

2. **User Prompt:**
   - Job posting details (title, company, description, requirements, etc.)
   - User profile summary (skills, preferences, target salary, location)
   - Request for structured evaluation

3. **Output Schema:**
   - Scores for each factor with reasoning
   - Overall weighted score
   - Grade and recommendation
   - Confidence level

### Goal 4: AI Evaluator Core (60 min)

**Tasks:**
- [ ] Create `src/evaluation/ai_evaluator.py`
- [ ] Implement Claude API client initialization
- [ ] Implement `evaluate_job(job: JobPosting) -> EvaluationResult`
- [ ] Parse and validate JSON response
- [ ] Handle API errors (rate limits, timeouts, invalid responses)
- [ ] Add logging throughout

**API Details:**
- Model: `claude-sonnet-4-5-20250929` (cost-effective, capable)
- Max tokens: ~2000 for response
- Temperature: 0 (deterministic for consistent evaluations)
- Response format: JSON

### Goal 5: Unit Tests (30 min)

**Tasks:**
- [ ] Create `tests/test_evaluation.py`
- [ ] Test FactorScore and EvaluationResult models
- [ ] Test prompt builder output
- [ ] Mock Claude API for evaluator tests
- [ ] Test grade calculation logic

---

## Technical Decisions

### Model Selection
- **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`)
- Rationale: Best balance of cost and capability
- Alternative: Claude Haiku for cost-sensitive batch processing

### Prompt Strategy
- Use structured JSON output (not free-form text)
- Include rubric in system prompt for consistency
- Provide clear examples for each score range
- Request confidence score for self-assessment

### Error Handling
- Retry on rate limits (exponential backoff)
- Fallback to "unknown" grade if parsing fails
- Log raw responses for debugging
- Set reasonable timeouts (30 seconds)

### Caching Strategy (Future)
- Cache evaluations by job ID
- Re-evaluate only if job details change
- Store cache in `data/evaluations.json`

---

## 8-Factor Rubric Summary

| Factor | Weight | Description |
|--------|--------|-------------|
| Skills & Experience Match | 25% | Technical alignment, domain experience |
| Compensation & Benefits | 20% | Base salary, equity, benefits |
| Company Stability & Growth | 15% | Funding, revenue, leadership |
| Work-Life Balance | 15% | Hours, flexibility, PTO |
| Career Growth & Learning | 10% | Advancement, skill development |
| Culture & Team Fit | 8% | Values alignment, team dynamics |
| Role Clarity & Expectations | 5% | JD clarity, success metrics |
| Location & Commute | 2% | Remote options, travel |

---

## Files to Create

```
src/evaluation/
├── __init__.py           # Update exports
├── models.py             # NEW: EvaluationResult, FactorScore
├── prompt_builder.py     # NEW: Prompt template construction
├── ai_evaluator.py       # NEW: Claude API integration
└── rubric_applicator.py  # NEW: Score calculation (if needed separately)

tests/
└── test_evaluation.py    # NEW: Unit tests for evaluation module

config/
└── user-profile.yaml     # NEW: User skills/preferences for evaluation context
```

---

## Dependencies to Add

```
# requirements.txt additions
anthropic>=0.39.0  # Claude API client
```

---

## Success Criteria

By end of session:
1. [ ] `EvaluationResult` model defined with all fields
2. [ ] Prompt builder creates valid evaluation prompts
3. [ ] AI evaluator can call Claude API and parse response
4. [ ] Basic unit tests passing
5. [ ] TT-48 updated with progress

Stretch goals:
- [ ] Integration with orchestrator
- [ ] End-to-end test with real job data

---

## Questions to Resolve

1. **User Profile:** Should we create a separate config file for user preferences (skills, salary target, location preference)?
   - Recommendation: Yes, create `config/user-profile.yaml`

2. **Batch vs Single:** Evaluate jobs one-by-one or batch?
   - Phase 3: Single evaluation (simpler)
   - Future: Batch for efficiency

3. **API Key Management:** How to handle ANTHROPIC_API_KEY?
   - Use existing pattern: Load from environment via dotenv
   - Add to `.env.example`

---

## End of Session Goals

1. Core evaluation models defined
2. Prompt builder implemented
3. AI evaluator functional (at least with mock/test)
4. Ready for integration in next session

---

**Session Start:** Monday, December 1, 2025
**Branch:** `david/tt-48-phase3-ai-evaluation`
**Linear Issue:** TT-48
**Status:** Implementation starting
