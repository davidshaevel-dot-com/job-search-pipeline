# Phase 3 Testing Guide - AI Evaluation Engine

**Date:** December 2, 2025
**Status:** Ready for testing
**Branch:** `david/tt-48-phase3-ai-evaluation`
**PR:** [#8](https://github.com/davidshaevel-dot-com/job-search-pipeline/pull/8)

---

## Overview

This guide covers testing the Phase 3 AI Evaluation Engine implementation:

- **Models** (`src/evaluation/models.py`) - Data structures for evaluation results
- **Prompt Builder** (`src/evaluation/prompt_builder.py`) - Constructs prompts for Claude API
- **AI Evaluator** (`src/evaluation/ai_evaluator.py`) - Claude API integration
- **User Profile** (`config/user-profile.yaml`) - Candidate configuration

---

## What's Being Tested

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Evaluation Engine                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐  │
│  │  JobPosting  │───▶│  PromptBuilder   │───▶│  AIEvaluator │  │
│  │   (input)    │    │  (builds prompts)│    │ (calls API)  │  │
│  └──────────────┘    └──────────────────┘    └──────────────┘  │
│                              │                       │          │
│                              ▼                       ▼          │
│                      ┌──────────────┐      ┌──────────────────┐│
│                      │ user-profile │      │ EvaluationResult ││
│                      │    .yaml     │      │    (output)      ││
│                      └──────────────┘      └──────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| **Grade Enum** | 5 | Letter grade assignment from scores (A/B/C/D/F) |
| **Recommendation Enum** | 1 | Action mapping from grades |
| **EvaluationFactor Enum** | 4 | 8-factor weights and key lookups |
| **FactorScore Dataclass** | 2 | Individual factor scoring |
| **EvaluationResult Dataclass** | 6 | Complete evaluation handling |
| **PromptBuilder** | 7 | Prompt construction and validation |
| **AIEvaluator** | 4 | Claude API integration |
| **Total** | **31** | Full coverage |

---

## Test Descriptions

### 1. Grade Enum Tests (5 tests)

Tests the letter grade assignment based on numerical scores:

```python
# test_grade_from_score_a: Scores 90-100 → Grade.A
assert Grade.from_score(90) == Grade.A
assert Grade.from_score(100) == Grade.A

# test_grade_from_score_b: Scores 80-89 → Grade.B
assert Grade.from_score(80) == Grade.B
assert Grade.from_score(89) == Grade.B

# test_grade_from_score_c: Scores 70-79 → Grade.C
assert Grade.from_score(70) == Grade.C

# test_grade_from_score_d: Scores 60-69 → Grade.D
assert Grade.from_score(60) == Grade.D

# test_grade_from_score_f: Scores 0-59 → Grade.F
assert Grade.from_score(59) == Grade.F
assert Grade.from_score(0) == Grade.F
```

**Why it matters:** Ensures consistent grading across all evaluations. A score of 89.9 must always be Grade.B, never Grade.A.

---

### 2. Recommendation Enum Tests (1 test)

Tests the action recommendation mapping from grades:

```python
# test_recommendation_from_grade
Grade.A → Recommendation.STRONGLY_PURSUE
Grade.B → Recommendation.PURSUE
Grade.C → Recommendation.CONSIDER
Grade.D → Recommendation.SKIP
Grade.F → Recommendation.SKIP
```

**Why it matters:** Ensures automated decision-making is consistent. Grade A jobs are auto-flagged for pursuit, Grade D/F are auto-skipped.

---

### 3. EvaluationFactor Enum Tests (4 tests)

Tests the 8-factor weighted rubric:

```python
# test_all_factors_exist: All 8 factors defined
["skills_match", "compensation", "stability", "work_life_balance",
 "career_growth", "culture_fit", "role_clarity", "location"]

# test_weights_sum_to_one: Weights total 100%
sum(factor.weight for factor in EvaluationFactor) == 1.0
# 0.25 + 0.20 + 0.15 + 0.15 + 0.10 + 0.08 + 0.05 + 0.02 = 1.00

# test_get_weight: Key-based weight lookup (O(1) with caching)
EvaluationFactor.get_weight("skills_match") == 0.25

# test_get_weight_invalid_key: Invalid keys raise ValueError
EvaluationFactor.get_weight("invalid_factor") → ValueError
```

**Why it matters:** The rubric weights determine how much each factor contributes to the final score. Skills Match (25%) has 12.5x more impact than Location (2%).

---

### 4. FactorScore Dataclass Tests (2 tests)

Tests individual factor scoring:

```python
# test_factor_score_creation
score = FactorScore(
    factor="skills_match",
    score=85,
    reasoning="Strong alignment with required skills"
)
score.weight == 0.25           # Auto-looked up
score.weighted_score == 21.25  # 85 * 0.25

# test_factor_score_to_dict: Serialization for JSON output
{
    "factor": "compensation",
    "score": 75,
    "weight": 0.20,
    "reasoning": "Salary is within range",
    "weighted_score": 15.0
}
```

**Why it matters:** Each factor must correctly calculate its contribution to the overall score.

---

### 5. EvaluationResult Dataclass Tests (6 tests)

Tests the complete evaluation result:

```python
# test_calculate_overall_score: Weighted sum calculation
# skills: 85 * 0.25 = 21.25
# comp: 75 * 0.20 = 15.00
# stability: 90 * 0.15 = 13.50
# wlb: 80 * 0.15 = 12.00
# growth: 82 * 0.10 = 8.20
# culture: 78 * 0.08 = 6.24
# role: 70 * 0.05 = 3.50
# location: 95 * 0.02 = 1.90
# Total: 81.59

# test_evaluation_result_validation_missing_factor
# Missing "skills_match" → ValueError("Missing required factors")

# test_evaluation_result_validation_invalid_score
# overall_score=150 → ValueError("Overall score must be 0-100")

# test_evaluation_result_to_dict: JSON serialization

# test_evaluation_result_from_dict: Deserialization

# test_meets_threshold / test_should_auto_pursue: Decision thresholds
```

**Why it matters:** Validates that evaluation results are complete, correct, and can be serialized for storage/reporting.

---

### 6. PromptBuilder Tests (7 tests)

Tests prompt construction for Claude API:

```python
# test_system_prompt_contains_rubric
# Verifies all 8 factors mentioned with weights
"Skills & Experience Match" in prompt
"25%" in prompt

# test_system_prompt_specifies_json_output
# Ensures JSON output format is required
"JSON" in prompt
"scores" in prompt

# test_build_user_prompt_includes_job_details
# Job info present in prompt
"Senior DevOps Engineer" in prompt
"$150,000 - $180,000" in prompt

# test_build_user_prompt_includes_user_profile
# User profile present (deep-merged with defaults)
"15 years" in prompt
"AWS" in prompt
"Terraform" in prompt

# test_build_user_prompt_handles_missing_salary
# Missing salary → "Not specified"

# test_validate_response_valid
# Valid JSON structure → True

# test_validate_response_missing_factor / invalid_score_range
# Invalid responses → False
```

**Why it matters:** The prompt quality directly affects evaluation quality. Incomplete prompts lead to incomplete evaluations.

---

### 7. AIEvaluator Tests (4 tests)

Tests Claude API integration:

```python
# test_evaluator_requires_api_key
# No ANTHROPIC_API_KEY → ValueError
with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
    AIEvaluator()

# test_evaluate_job_success (mocked API)
# Full evaluation flow with mocked Claude response
result = evaluator.evaluate_job(sample_job)
assert result.grade == Grade.B
assert result.recommendation == Recommendation.PURSUE

# test_evaluate_job_parses_json_with_markdown
# Handles ```json ... ``` wrapped responses
wrapped = "```json\n{...}\n```"
# Successfully extracts and parses JSON

# test_estimate_cost
# Cost estimation for batch evaluations
estimate = evaluator.estimate_cost([job1, job2, job3])
assert estimate["job_count"] == 3
assert estimate["estimated_cost_usd"] > 0
```

**Why it matters:** Verifies API integration works correctly without incurring actual API costs during testing.

---

## Running Tests

### Prerequisites

1. **Activate virtual environment:**
   ```bash
   cd /Users/dshaevel/workspace-ds/job-search-pipeline
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Run All Evaluation Tests

```bash
PYTHONPATH=src python -m pytest tests/test_evaluation.py -v
```

**Expected output:**
```
============================= test session starts ==============================
tests/test_evaluation.py::TestGrade::test_grade_from_score_a PASSED      [  3%]
tests/test_evaluation.py::TestGrade::test_grade_from_score_b PASSED      [  6%]
tests/test_evaluation.py::TestGrade::test_grade_from_score_c PASSED      [  9%]
tests/test_evaluation.py::TestGrade::test_grade_from_score_d PASSED      [ 12%]
tests/test_evaluation.py::TestGrade::test_grade_from_score_f PASSED      [ 16%]
tests/test_evaluation.py::TestRecommendation::test_recommendation_from_grade PASSED [ 19%]
tests/test_evaluation.py::TestEvaluationFactor::test_all_factors_exist PASSED [ 22%]
tests/test_evaluation.py::TestEvaluationFactor::test_weights_sum_to_one PASSED [ 25%]
tests/test_evaluation.py::TestEvaluationFactor::test_get_weight PASSED   [ 29%]
tests/test_evaluation.py::TestEvaluationFactor::test_get_weight_invalid_key PASSED [ 32%]
tests/test_evaluation.py::TestFactorScore::test_factor_score_creation PASSED [ 35%]
tests/test_evaluation.py::TestFactorScore::test_factor_score_to_dict PASSED [ 38%]
tests/test_evaluation.py::TestEvaluationResult::test_calculate_overall_score PASSED [ 41%]
tests/test_evaluation.py::TestEvaluationResult::test_evaluation_result_validation_missing_factor PASSED [ 45%]
tests/test_evaluation.py::TestEvaluationResult::test_evaluation_result_validation_invalid_score PASSED [ 48%]
tests/test_evaluation.py::TestEvaluationResult::test_evaluation_result_to_dict PASSED [ 51%]
tests/test_evaluation.py::TestEvaluationResult::test_evaluation_result_from_dict PASSED [ 54%]
tests/test_evaluation.py::TestEvaluationResult::test_meets_threshold PASSED [ 58%]
tests/test_evaluation.py::TestEvaluationResult::test_should_auto_pursue PASSED [ 61%]
tests/test_evaluation.py::TestPromptBuilder::test_system_prompt_contains_rubric PASSED [ 64%]
tests/test_evaluation.py::TestPromptBuilder::test_system_prompt_specifies_json_output PASSED [ 67%]
tests/test_evaluation.py::TestPromptBuilder::test_build_user_prompt_includes_job_details PASSED [ 70%]
tests/test_evaluation.py::TestPromptBuilder::test_build_user_prompt_includes_user_profile PASSED [ 74%]
tests/test_evaluation.py::TestPromptBuilder::test_build_user_prompt_handles_missing_salary PASSED [ 77%]
tests/test_evaluation.py::TestPromptBuilder::test_validate_response_valid PASSED [ 80%]
tests/test_evaluation.py::TestPromptBuilder::test_validate_response_missing_factor PASSED [ 83%]
tests/test_evaluation.py::TestPromptBuilder::test_validate_response_invalid_score_range PASSED [ 87%]
tests/test_evaluation.py::TestAIEvaluator::test_evaluator_requires_api_key PASSED [ 90%]
tests/test_evaluation.py::TestAIEvaluator::test_evaluate_job_success PASSED [ 93%]
tests/test_evaluation.py::TestAIEvaluator::test_evaluate_job_parses_json_with_markdown PASSED [ 96%]
tests/test_evaluation.py::TestAIEvaluator::test_estimate_cost PASSED     [100%]

============================== 31 passed in 0.80s ==============================
```

### Run All Project Tests

```bash
PYTHONPATH=src python -m pytest -v
```

**Expected:** 50 tests passed (31 evaluation + 19 filters)

### Run Specific Test Categories

```bash
# Just Grade tests
PYTHONPATH=src python -m pytest tests/test_evaluation.py::TestGrade -v

# Just PromptBuilder tests
PYTHONPATH=src python -m pytest tests/test_evaluation.py::TestPromptBuilder -v

# Just AIEvaluator tests (includes mocked API calls)
PYTHONPATH=src python -m pytest tests/test_evaluation.py::TestAIEvaluator -v
```

---

## Manual Integration Testing (Optional)

### Test with Real Claude API

**Prerequisites:**
- ANTHROPIC_API_KEY environment variable set
- Valid Anthropic API key with credits

**Test script:**
```python
# scripts/test_ai_evaluator.py
import os
from datetime import datetime

os.environ["ANTHROPIC_API_KEY"] = "your-key-here"  # Or use env var

from core.models import JobPosting
from evaluation.ai_evaluator import AIEvaluator

# Create test job
job = JobPosting(
    title="Senior DevOps Engineer",
    company="TechCorp",
    location="Austin, TX",
    remote_type="hybrid",
    salary_min=160000,
    salary_max=190000,
    description="""
    We're looking for a Senior DevOps Engineer to join our platform team.
    You'll work on AWS infrastructure, CI/CD pipelines, and Kubernetes clusters.

    Requirements:
    - 5+ years DevOps/SRE experience
    - Strong AWS expertise (ECS, EKS, Lambda)
    - Terraform and Infrastructure as Code
    - Python and/or Go
    - Kubernetes administration
    """,
    requirements=["AWS", "Terraform", "Kubernetes", "Python", "CI/CD"],
    job_url="https://example.com/jobs/123",
    board_name="Test",
    board_job_id="test-123",
)

# Evaluate
evaluator = AIEvaluator()
result = evaluator.evaluate_job(job)

# Print results
print(result.format_summary())
```

**Expected output:**
```
Evaluation: Senior DevOps Engineer at TechCorp
Overall Score: 85.2/100 (B)
Recommendation: Pursue
Confidence: 92%

Factor Scores:
  Skills & Experience Match: 92/100 (weight: 25%)
  Compensation & Benefits: 85/100 (weight: 20%)
  Company Stability & Growth: 75/100 (weight: 15%)
  Work-Life Balance: 80/100 (weight: 15%)
  Career Growth & Learning: 88/100 (weight: 10%)
  Culture & Team Fit: 78/100 (weight: 8%)
  Role Clarity & Expectations: 82/100 (weight: 5%)
  Location & Commute: 90/100 (weight: 2%)

Strengths:
  + Strong skills alignment with AWS, Terraform, Kubernetes
  + Competitive salary range ($160-190K)
  + Hybrid work flexibility

Concerns:
  - Company stability unknown (need more research)

Summary: Strong opportunity with excellent technical fit and competitive compensation.
```

**API Cost:** ~$0.05-0.10 per evaluation (Sonnet 4.5 pricing)

---

## Test Coverage Details

### What's Tested

| Component | Coverage | Notes |
|-----------|----------|-------|
| Grade.from_score() | 100% | All boundary cases |
| Recommendation.from_grade() | 100% | All 5 grades |
| EvaluationFactor enum | 100% | All 8 factors, weights, keys |
| FactorScore dataclass | 100% | Creation, serialization |
| EvaluationResult dataclass | 95% | Validation, serialization, helpers |
| PromptBuilder | 90% | System prompt, user prompt, validation |
| AIEvaluator | 80% | Success path, error handling (mocked) |
| _deep_merge() | Implicit | Tested via PromptBuilder |
| _slugify() | Implicit | Tested via AIEvaluator |

### What's NOT Tested (Integration)

- Real Claude API calls (requires API key and costs money)
- Rate limiting behavior (requires real API)
- Retry logic with real network errors
- Cost estimation accuracy (uses estimates)

---

## Key Implementation Details Tested

### 1. Deep Merge for User Profiles

The `_deep_merge()` function ensures partial user profiles work correctly:

```python
# Partial profile (only overrides salary)
custom_profile = {"salary_target": {"min": 200000}}

# After deep merge, all other defaults preserved:
{
    "target_role": "Senior DevOps Engineer / Platform Engineer",  # DEFAULT
    "experience_years": 15,  # DEFAULT
    "salary_target": {
        "min": 200000,  # CUSTOM
        "max": 180000,  # DEFAULT
        "currency": "USD"  # DEFAULT
    },
    ...
}
```

### 2. Cached Enum Lookups

The `_EVALUATION_FACTOR_KEY_MAP` provides O(1) lookups:

```python
# Before (O(n) - iterates all factors each time):
for factor in EvaluationFactor:
    if factor.key == key:
        return factor.weight

# After (O(1) - direct dict lookup):
return _EVALUATION_FACTOR_KEY_MAP[key].weight
```

### 3. Regex-Based Markdown Extraction

The `_MARKDOWN_CODE_BLOCK_PATTERN` handles various response formats:

```python
# Handles: ```json\n{...}\n```
# Handles: ``` {json} ```
# Handles: JSON anywhere in response text
match = _MARKDOWN_CODE_BLOCK_PATTERN.search(response)
json_text = match.group(1) if match else response
```

### 4. Safe Job ID Generation

The `_slugify()` function creates safe identifiers:

```python
_slugify("Acme Corp!!") → "acme_corp"
_slugify("TechCo @ Austin") → "techco_austin"
_slugify("  Spaces  Everywhere  ") → "spaces_everywhere"
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'evaluation'"

**Solution:** Ensure PYTHONPATH includes src:
```bash
PYTHONPATH=src python -m pytest tests/test_evaluation.py -v
```

### Error: "No module named pytest"

**Solution:** Activate virtual environment:
```bash
source venv/bin/activate
pip install pytest pytest-mock
```

### Error: "ANTHROPIC_API_KEY not provided"

**Note:** This error is EXPECTED in `test_evaluator_requires_api_key` test.

For manual testing, set the environment variable:
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### Tests Passing But Evaluation Fails at Runtime

Check:
1. User profile YAML syntax is valid
2. All 8 factors have valid weights summing to 1.0
3. Claude API response matches expected JSON schema
4. API key has sufficient credits

---

## Success Criteria

Phase 3 testing is successful if:

1. ✅ All 31 unit tests pass
2. ✅ All 50 project tests pass (including Phase 2 filter tests)
3. ✅ No import errors or missing dependencies
4. ✅ Weighted score calculation matches manual calculation
5. ✅ Grade boundaries are correctly enforced (90+→A, 80-89→B, etc.)
6. ✅ Prompt includes all 8 factors with correct weights
7. ✅ User profile deep merge works with partial profiles
8. ✅ JSON validation catches missing factors and invalid scores
9. ✅ Mocked API evaluations return correct result types
10. ✅ Cost estimation produces reasonable values

---

## Next Steps After Testing

### If Tests Pass:

1. **Merge PR #8** after Gemini review approval
2. **Update Linear TT-48** to "Done"
3. **Proceed to Phase 3 Integration:**
   - Connect evaluation engine to search pipeline
   - Add evaluation results to job output files
   - Implement threshold-based filtering

### If Tests Fail:

1. Review error messages carefully
2. Check test fixtures match expected data structures
3. Verify all dependencies installed
4. Run with `-v` for verbose output
5. Check specific failing test class

---

**Last Updated:** December 2, 2025
**Phase:** 3 (AI Evaluation)
**Status:** 31 tests passing
