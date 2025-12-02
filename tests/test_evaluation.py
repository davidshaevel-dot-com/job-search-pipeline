"""
Unit tests for evaluation module.

Tests the AI evaluation engine including models, prompt builder, and evaluator.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.models import JobPosting
from evaluation.models import (
    EvaluationFactor,
    EvaluationResult,
    FactorScore,
    Grade,
    Recommendation,
)
from evaluation.prompt_builder import PromptBuilder


class TestGrade:
    """Tests for Grade enum."""

    def test_grade_from_score_a(self):
        """Test Grade.A for scores 90-100."""
        assert Grade.from_score(90) == Grade.A
        assert Grade.from_score(95) == Grade.A
        assert Grade.from_score(100) == Grade.A

    def test_grade_from_score_b(self):
        """Test Grade.B for scores 80-89."""
        assert Grade.from_score(80) == Grade.B
        assert Grade.from_score(85) == Grade.B
        assert Grade.from_score(89) == Grade.B

    def test_grade_from_score_c(self):
        """Test Grade.C for scores 70-79."""
        assert Grade.from_score(70) == Grade.C
        assert Grade.from_score(75) == Grade.C
        assert Grade.from_score(79) == Grade.C

    def test_grade_from_score_d(self):
        """Test Grade.D for scores 60-69."""
        assert Grade.from_score(60) == Grade.D
        assert Grade.from_score(65) == Grade.D
        assert Grade.from_score(69) == Grade.D

    def test_grade_from_score_f(self):
        """Test Grade.F for scores below 60."""
        assert Grade.from_score(0) == Grade.F
        assert Grade.from_score(30) == Grade.F
        assert Grade.from_score(59) == Grade.F


class TestRecommendation:
    """Tests for Recommendation enum."""

    def test_recommendation_from_grade(self):
        """Test recommendation mapping from grades."""
        assert Recommendation.from_grade(Grade.A) == Recommendation.STRONGLY_PURSUE
        assert Recommendation.from_grade(Grade.B) == Recommendation.PURSUE
        assert Recommendation.from_grade(Grade.C) == Recommendation.CONSIDER
        assert Recommendation.from_grade(Grade.D) == Recommendation.SKIP
        assert Recommendation.from_grade(Grade.F) == Recommendation.SKIP


class TestEvaluationFactor:
    """Tests for EvaluationFactor enum."""

    def test_all_factors_exist(self):
        """Test all 8 evaluation factors are defined."""
        expected_factors = [
            "skills_match",
            "compensation",
            "stability",
            "work_life_balance",
            "career_growth",
            "culture_fit",
            "role_clarity",
            "location",
        ]
        assert EvaluationFactor.get_all_keys() == expected_factors

    def test_weights_sum_to_one(self):
        """Test all factor weights sum to 1.0 (100%)."""
        total_weight = sum(factor.weight for factor in EvaluationFactor)
        assert abs(total_weight - 1.0) < 0.001  # Allow small floating point error

    def test_get_weight(self):
        """Test getting weight by factor key."""
        assert EvaluationFactor.get_weight("skills_match") == 0.25
        assert EvaluationFactor.get_weight("compensation") == 0.20
        assert EvaluationFactor.get_weight("location") == 0.02

    def test_get_weight_invalid_key(self):
        """Test getting weight with invalid key raises ValueError."""
        with pytest.raises(ValueError):
            EvaluationFactor.get_weight("invalid_factor")


class TestFactorScore:
    """Tests for FactorScore dataclass."""

    def test_factor_score_creation(self):
        """Test creating a FactorScore."""
        score = FactorScore(
            factor="skills_match",
            score=85,
            reasoning="Strong alignment with required skills",
        )
        assert score.factor == "skills_match"
        assert score.score == 85
        assert score.weight == 0.25
        assert score.weighted_score == 85 * 0.25

    def test_factor_score_to_dict(self):
        """Test converting FactorScore to dictionary."""
        score = FactorScore(
            factor="compensation",
            score=75,
            reasoning="Salary is within range",
        )
        result = score.to_dict()

        assert result["factor"] == "compensation"
        assert result["score"] == 75
        assert result["weight"] == 0.20
        assert result["reasoning"] == "Salary is within range"
        assert result["weighted_score"] == 15.0  # 75 * 0.20


class TestEvaluationResult:
    """Tests for EvaluationResult dataclass."""

    @pytest.fixture
    def sample_factor_scores(self):
        """Create sample factor scores for testing."""
        return {
            "skills_match": FactorScore("skills_match", 85, "Good match"),
            "compensation": FactorScore("compensation", 75, "Within range"),
            "stability": FactorScore("stability", 90, "Well-funded"),
            "work_life_balance": FactorScore("work_life_balance", 80, "Flexible"),
            "career_growth": FactorScore("career_growth", 82, "Growth path"),
            "culture_fit": FactorScore("culture_fit", 78, "Aligned values"),
            "role_clarity": FactorScore("role_clarity", 70, "Somewhat clear"),
            "location": FactorScore("location", 95, "Remote"),
        }

    @pytest.fixture
    def sample_evaluation_result(self, sample_factor_scores):
        """Create a sample evaluation result."""
        overall = EvaluationResult.calculate_overall_score(sample_factor_scores)
        grade = Grade.from_score(overall)

        return EvaluationResult(
            job_id="test-job-123",
            job_title="Senior DevOps Engineer",
            company="TestCo",
            evaluation_timestamp=datetime(2025, 12, 1, 10, 0, 0),
            model="claude-sonnet-4-5-20250514",
            factor_scores=sample_factor_scores,
            overall_score=overall,
            grade=grade,
            recommendation=Recommendation.from_grade(grade),
            confidence=0.95,
            summary="Strong opportunity overall",
            strengths=["Good skills match", "Remote work"],
            concerns=["Role clarity could be better"],
        )

    def test_calculate_overall_score(self, sample_factor_scores):
        """Test weighted score calculation."""
        overall = EvaluationResult.calculate_overall_score(sample_factor_scores)

        # Manual calculation:
        # skills: 85 * 0.25 = 21.25
        # comp: 75 * 0.20 = 15.00
        # stability: 90 * 0.15 = 13.50
        # wlb: 80 * 0.15 = 12.00
        # growth: 82 * 0.10 = 8.20
        # culture: 78 * 0.08 = 6.24
        # role: 70 * 0.05 = 3.50
        # location: 95 * 0.02 = 1.90
        # Total: 81.59
        expected = 21.25 + 15.00 + 13.50 + 12.00 + 8.20 + 6.24 + 3.50 + 1.90
        assert abs(overall - expected) < 0.01

    def test_evaluation_result_validation_missing_factor(self, sample_factor_scores):
        """Test validation catches missing factors."""
        # Remove one factor
        del sample_factor_scores["skills_match"]

        with pytest.raises(ValueError, match="Missing required factors"):
            EvaluationResult(
                job_id="test",
                job_title="Test",
                company="Test",
                evaluation_timestamp=datetime.now(),
                model="test",
                factor_scores=sample_factor_scores,
                overall_score=80,
                grade=Grade.B,
                recommendation=Recommendation.PURSUE,
                confidence=0.9,
                summary="Test",
            )

    def test_evaluation_result_validation_invalid_score(self, sample_factor_scores):
        """Test validation catches invalid overall score."""
        with pytest.raises(ValueError, match="Overall score must be 0-100"):
            EvaluationResult(
                job_id="test",
                job_title="Test",
                company="Test",
                evaluation_timestamp=datetime.now(),
                model="test",
                factor_scores=sample_factor_scores,
                overall_score=150,  # Invalid!
                grade=Grade.A,
                recommendation=Recommendation.STRONGLY_PURSUE,
                confidence=0.9,
                summary="Test",
            )

    def test_evaluation_result_to_dict(self, sample_evaluation_result):
        """Test converting EvaluationResult to dictionary."""
        result = sample_evaluation_result.to_dict()

        assert result["job_id"] == "test-job-123"
        assert result["job_title"] == "Senior DevOps Engineer"
        assert result["company"] == "TestCo"
        assert result["grade"] == "B"
        assert result["recommendation"] == "pursue"
        assert result["confidence"] == 0.95
        assert len(result["factor_scores"]) == 8
        assert len(result["strengths"]) == 2
        assert len(result["concerns"]) == 1

    def test_evaluation_result_from_dict(self, sample_evaluation_result):
        """Test creating EvaluationResult from dictionary."""
        data = sample_evaluation_result.to_dict()
        restored = EvaluationResult.from_dict(data)

        assert restored.job_id == sample_evaluation_result.job_id
        assert restored.grade == sample_evaluation_result.grade
        assert restored.overall_score == sample_evaluation_result.overall_score
        assert len(restored.factor_scores) == 8

    def test_meets_threshold(self, sample_evaluation_result):
        """Test threshold checking."""
        # Sample result has score ~81.59
        assert sample_evaluation_result.meets_threshold(70)
        assert sample_evaluation_result.meets_threshold(80)
        assert not sample_evaluation_result.meets_threshold(85)

    def test_should_auto_pursue(self, sample_evaluation_result):
        """Test auto-pursue threshold checking."""
        # Sample result has score ~81.59
        assert not sample_evaluation_result.should_auto_pursue(85)
        assert sample_evaluation_result.should_auto_pursue(80)


class TestPromptBuilder:
    """Tests for PromptBuilder."""

    @pytest.fixture
    def sample_job(self):
        """Create a sample job posting."""
        return JobPosting(
            title="Senior DevOps Engineer",
            company="TechCorp Inc",
            location="Austin, TX",
            remote_type="hybrid",
            salary_min=150000,
            salary_max=180000,
            description="We are looking for a Senior DevOps Engineer...",
            requirements=["5+ years experience", "AWS expertise", "Terraform"],
            posted_date=datetime(2025, 11, 30),
            job_url="https://example.com/job/123",
            board_name="JSearch",
            board_job_id="jsearch-123",
        )

    def test_system_prompt_contains_rubric(self):
        """Test system prompt includes all evaluation factors."""
        builder = PromptBuilder()
        prompt = builder.get_system_prompt()

        # Check all factors are mentioned
        assert "Skills & Experience Match" in prompt
        assert "Compensation & Benefits" in prompt
        assert "Company Stability" in prompt
        assert "Work-Life Balance" in prompt
        assert "Career Growth" in prompt
        assert "Culture" in prompt
        assert "Role Clarity" in prompt
        assert "Location" in prompt

        # Check weights are mentioned
        assert "25%" in prompt
        assert "20%" in prompt
        assert "15%" in prompt

    def test_system_prompt_specifies_json_output(self):
        """Test system prompt requires JSON output."""
        builder = PromptBuilder()
        prompt = builder.get_system_prompt()

        assert "JSON" in prompt
        assert "scores" in prompt

    def test_build_user_prompt_includes_job_details(self, sample_job):
        """Test user prompt includes job information."""
        builder = PromptBuilder()
        prompt = builder.build_user_prompt(sample_job)

        assert sample_job.title in prompt
        assert sample_job.company in prompt
        assert sample_job.location in prompt
        assert "$150,000 - $180,000" in prompt

    def test_build_user_prompt_includes_user_profile(self, sample_job):
        """Test user prompt includes user profile."""
        builder = PromptBuilder()
        prompt = builder.build_user_prompt(sample_job)

        # Default profile values
        assert "15 years" in prompt or "Experience: 15" in prompt
        assert "AWS" in prompt
        assert "Terraform" in prompt

    def test_build_user_prompt_handles_missing_salary(self, sample_job):
        """Test user prompt handles jobs without salary."""
        sample_job.salary_min = None
        sample_job.salary_max = None

        builder = PromptBuilder()
        prompt = builder.build_user_prompt(sample_job)

        assert "Not specified" in prompt

    def test_validate_response_valid(self):
        """Test response validation with valid response."""
        builder = PromptBuilder()

        valid_response = {
            "scores": {
                "skills_match": {"score": 85, "reasoning": "Good"},
                "compensation": {"score": 75, "reasoning": "OK"},
                "stability": {"score": 90, "reasoning": "Good"},
                "work_life_balance": {"score": 80, "reasoning": "OK"},
                "career_growth": {"score": 82, "reasoning": "Good"},
                "culture_fit": {"score": 78, "reasoning": "OK"},
                "role_clarity": {"score": 70, "reasoning": "OK"},
                "location": {"score": 95, "reasoning": "Great"},
            },
            "summary": "Good opportunity",
            "strengths": ["Remote work"],
            "concerns": ["Salary"],
            "confidence": 0.9,
        }

        assert builder.validate_response(valid_response) is True

    def test_validate_response_missing_factor(self):
        """Test response validation catches missing factor."""
        builder = PromptBuilder()

        invalid_response = {
            "scores": {
                "skills_match": {"score": 85, "reasoning": "Good"},
                # Missing other factors
            },
            "summary": "Good",
            "strengths": [],
            "concerns": [],
            "confidence": 0.9,
        }

        assert builder.validate_response(invalid_response) is False

    def test_validate_response_invalid_score_range(self):
        """Test response validation catches out-of-range scores."""
        builder = PromptBuilder()

        invalid_response = {
            "scores": {
                "skills_match": {"score": 150, "reasoning": "Good"},  # Invalid!
                "compensation": {"score": 75, "reasoning": "OK"},
                "stability": {"score": 90, "reasoning": "Good"},
                "work_life_balance": {"score": 80, "reasoning": "OK"},
                "career_growth": {"score": 82, "reasoning": "Good"},
                "culture_fit": {"score": 78, "reasoning": "OK"},
                "role_clarity": {"score": 70, "reasoning": "OK"},
                "location": {"score": 95, "reasoning": "Great"},
            },
            "summary": "Good",
            "strengths": [],
            "concerns": [],
            "confidence": 0.9,
        }

        assert builder.validate_response(invalid_response) is False


class TestAIEvaluator:
    """Tests for AIEvaluator."""

    @pytest.fixture
    def mock_anthropic_response(self):
        """Create a mock Anthropic API response."""
        response_content = {
            "scores": {
                "skills_match": {"score": 85, "reasoning": "Strong alignment"},
                "compensation": {"score": 75, "reasoning": "Within range"},
                "stability": {"score": 90, "reasoning": "Well-funded"},
                "work_life_balance": {"score": 80, "reasoning": "Flexible"},
                "career_growth": {"score": 82, "reasoning": "Growth path"},
                "culture_fit": {"score": 78, "reasoning": "Good fit"},
                "role_clarity": {"score": 70, "reasoning": "Clear enough"},
                "location": {"score": 95, "reasoning": "Remote"},
            },
            "summary": "Strong opportunity overall",
            "strengths": ["Good skills match", "Remote work"],
            "concerns": ["Salary could be higher"],
            "confidence": 0.92,
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(response_content))]
        return mock_response

    @pytest.fixture
    def sample_job(self):
        """Create a sample job posting."""
        return JobPosting(
            title="Senior DevOps Engineer",
            company="TechCorp",
            location="Austin, TX",
            remote_type="remote",
            salary_min=150000,
            salary_max=180000,
            description="Looking for an experienced DevOps engineer...",
            requirements=["AWS", "Terraform", "Kubernetes"],
            job_url="https://example.com/job",
            board_name="JSearch",
            board_job_id="job-123",
        )

    def test_evaluator_requires_api_key(self):
        """Test evaluator raises error without API key."""
        # Clear environment variable
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                from evaluation.ai_evaluator import AIEvaluator
                AIEvaluator()

    @patch("evaluation.ai_evaluator.anthropic.Anthropic")
    def test_evaluate_job_success(
        self, mock_anthropic_class, mock_anthropic_response, sample_job
    ):
        """Test successful job evaluation."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_response
        mock_anthropic_class.return_value = mock_client

        from evaluation.ai_evaluator import AIEvaluator
        evaluator = AIEvaluator(api_key="test-key")
        result = evaluator.evaluate_job(sample_job)

        # Verify result
        assert isinstance(result, EvaluationResult)
        assert result.job_title == "Senior DevOps Engineer"
        assert result.company == "TechCorp"
        assert result.grade == Grade.B  # Score ~81.59
        assert result.recommendation == Recommendation.PURSUE
        assert result.confidence == 0.92
        assert len(result.factor_scores) == 8

    @patch("evaluation.ai_evaluator.anthropic.Anthropic")
    def test_evaluate_job_parses_json_with_markdown(
        self, mock_anthropic_class, sample_job
    ):
        """Test evaluator handles JSON wrapped in markdown code block."""
        response_content = {
            "scores": {
                "skills_match": {"score": 85, "reasoning": "Good"},
                "compensation": {"score": 75, "reasoning": "OK"},
                "stability": {"score": 90, "reasoning": "Good"},
                "work_life_balance": {"score": 80, "reasoning": "OK"},
                "career_growth": {"score": 82, "reasoning": "Good"},
                "culture_fit": {"score": 78, "reasoning": "OK"},
                "role_clarity": {"score": 70, "reasoning": "OK"},
                "location": {"score": 95, "reasoning": "Great"},
            },
            "summary": "Good",
            "strengths": ["A"],
            "concerns": ["B"],
            "confidence": 0.9,
        }

        # Wrap in markdown code block
        wrapped_response = f"```json\n{json.dumps(response_content)}\n```"

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=wrapped_response)]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        from evaluation.ai_evaluator import AIEvaluator
        evaluator = AIEvaluator(api_key="test-key")
        result = evaluator.evaluate_job(sample_job)

        assert isinstance(result, EvaluationResult)
        assert result.overall_score > 0

    @patch("evaluation.ai_evaluator.anthropic.Anthropic")
    def test_estimate_cost(self, mock_anthropic_class, sample_job):
        """Test cost estimation."""
        mock_anthropic_class.return_value = MagicMock()

        from evaluation.ai_evaluator import AIEvaluator
        evaluator = AIEvaluator(api_key="test-key")

        jobs = [sample_job, sample_job, sample_job]  # 3 jobs
        estimate = evaluator.estimate_cost(jobs)

        assert estimate["job_count"] == 3
        assert estimate["estimated_input_tokens"] > 0
        assert estimate["estimated_output_tokens"] > 0
        assert estimate["estimated_cost_usd"] > 0
        assert estimate["cost_per_job_usd"] > 0
