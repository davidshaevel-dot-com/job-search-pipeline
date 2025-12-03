"""
Integration tests for Phase 3 AI Evaluation pipeline.

Tests the integration between:
- SearchOrchestrator with evaluation
- EvaluationWriter for result storage
- SearchResult dataclass
"""

import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys

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
from organization.evaluation_writer import (
    EvaluationWriter,
    format_evaluation_json,
    get_evaluation_filename,
)
from search.orchestrator import SearchResult


def create_sample_job(
    title: str = "DevOps Engineer",
    company: str = "Acme Corp",
    board_job_id: str = "job-123",
) -> JobPosting:
    """Create a sample job posting for testing."""
    return JobPosting(
        title=title,
        company=company,
        location="Austin, TX",
        remote_type="hybrid",
        salary_min=150000,
        salary_max=180000,
        description="A great DevOps role with modern tech stack.",
        requirements=["AWS", "Terraform", "Python"],
        job_url="https://example.com/job",
        board_name="JSearch",
        board_job_id=board_job_id,
    )


def create_sample_evaluation(overall_score: float = 85.0) -> EvaluationResult:
    """Create a sample evaluation result for testing."""
    # Note: FactorScore uses factor key strings and scores 0-100
    # factor_scores must be a dict, not a list
    factor_scores = {
        "skills_match": FactorScore(
            factor="skills_match",
            score=85,
            reasoning="Good skills alignment",
        ),
        "compensation": FactorScore(
            factor="compensation",
            score=80,
            reasoning="Competitive salary",
        ),
        "stability": FactorScore(
            factor="stability",
            score=75,
            reasoning="Established company",
        ),
        "work_life_balance": FactorScore(
            factor="work_life_balance",
            score=80,
            reasoning="Good WLB policies",
        ),
        "career_growth": FactorScore(
            factor="career_growth",
            score=70,
            reasoning="Growth opportunities",
        ),
        "culture_fit": FactorScore(
            factor="culture_fit",
            score=85,
            reasoning="Great culture",
        ),
        "role_clarity": FactorScore(
            factor="role_clarity",
            score=90,
            reasoning="Clear expectations",
        ),
        "location": FactorScore(
            factor="location",
            score=80,
            reasoning="Good location",
        ),
    }

    # Calculate the overall score from factor scores
    calc_overall = EvaluationResult.calculate_overall_score(factor_scores)

    return EvaluationResult(
        job_id="test-job-123",
        job_title="DevOps Engineer",
        company="Acme Corp",
        evaluation_timestamp=datetime.now(),
        model="claude-sonnet-4-5-20250929",
        factor_scores=factor_scores,
        overall_score=calc_overall,
        grade=Grade.from_score(calc_overall),
        recommendation=Recommendation.from_grade(Grade.from_score(calc_overall)),
        confidence=0.85,
        summary="A strong opportunity with good alignment.",
        strengths=["Tech stack", "Compensation"],
        concerns=["None significant"],
    )


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_search_result_creation(self):
        """Test creating a SearchResult with all fields."""
        jobs = [create_sample_job()]
        evaluations = [create_sample_evaluation()]
        errors = ["Failed job 1"]
        stats = {"jobs_found": 1}

        result = SearchResult(
            jobs=jobs,
            evaluations=evaluations,
            evaluation_errors=errors,
            stats=stats,
        )

        assert len(result.jobs) == 1
        assert len(result.evaluations) == 1
        assert len(result.evaluation_errors) == 1
        assert result.stats["jobs_found"] == 1

    def test_search_result_defaults(self):
        """Test SearchResult default values."""
        jobs = [create_sample_job()]
        result = SearchResult(jobs=jobs)

        assert result.evaluations is None
        assert result.evaluation_errors == []
        assert result.stats == {}


class TestEvaluationWriter:
    """Tests for EvaluationWriter."""

    def test_get_evaluation_filename(self):
        """Test filename generation for evaluations."""
        job = create_sample_job(title="DevOps Engineer", company="Acme Corp")
        filename = get_evaluation_filename(job)
        assert filename == "Acme_Corp_DevOps_Engineer_evaluation"

    def test_get_evaluation_filename_with_counter(self):
        """Test filename generation with counter."""
        job = create_sample_job()
        filename = get_evaluation_filename(job, counter=2)
        assert "_evaluation_2" in filename

    def test_format_evaluation_json(self):
        """Test JSON formatting for evaluation."""
        job = create_sample_job()
        evaluation = create_sample_evaluation()

        output = format_evaluation_json(job, evaluation)

        assert "evaluation" in output
        assert "metadata" in output
        assert "job_summary" in output
        assert output["metadata"]["board_job_id"] == "job-123"
        assert output["job_summary"]["title"] == "DevOps Engineer"

    def test_format_evaluation_json_without_job_summary(self):
        """Test JSON formatting without job summary."""
        job = create_sample_job()
        evaluation = create_sample_evaluation()

        output = format_evaluation_json(job, evaluation, include_job_summary=False)

        assert "evaluation" in output
        assert "metadata" in output
        assert "job_summary" not in output

    def test_write_single_evaluation(self):
        """Test writing a single evaluation file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = EvaluationWriter(base_path=Path(tmpdir))

            job = create_sample_job()
            evaluation = create_sample_evaluation()

            path = writer.write_evaluation(job, evaluation)

            assert path is not None
            assert path.exists()
            assert path.suffix == ".json"

            # Verify content
            with open(path) as f:
                content = json.load(f)
            assert "evaluation" in content
            assert content["job_summary"]["company"] == "Acme Corp"

    def test_write_multiple_evaluations(self):
        """Test writing multiple evaluation files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = EvaluationWriter(base_path=Path(tmpdir))

            jobs_and_evals = [
                (
                    create_sample_job(title="DevOps Engineer", board_job_id="1"),
                    create_sample_evaluation(85.0),
                ),
                (
                    create_sample_job(title="Platform Engineer", board_job_id="2"),
                    create_sample_evaluation(90.0),
                ),
            ]

            paths = writer.write_evaluations(jobs_and_evals)

            assert len(paths) == 2
            for path in paths:
                assert path.exists()

    def test_write_summary(self):
        """Test writing evaluation summary file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = EvaluationWriter(base_path=Path(tmpdir))

            jobs_and_evals = [
                (
                    create_sample_job(title="DevOps Engineer", board_job_id="1"),
                    create_sample_evaluation(85.0),
                ),
                (
                    create_sample_job(title="Platform Engineer", board_job_id="2"),
                    create_sample_evaluation(90.0),
                ),
            ]

            summary_path = writer.write_summary(jobs_and_evals)

            assert summary_path is not None
            assert summary_path.exists()
            assert summary_path.name == "evaluation_summary.json"

            # Verify content
            with open(summary_path) as f:
                summary = json.load(f)
            assert summary["total_jobs"] == 2
            assert "grade_distribution" in summary
            assert len(summary["jobs"]) == 2
            # Jobs should be sorted by score (highest first)
            assert summary["jobs"][0]["overall_score"] >= summary["jobs"][1]["overall_score"]

    def test_write_empty_evaluations(self):
        """Test writing with empty list returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = EvaluationWriter(base_path=Path(tmpdir))

            paths = writer.write_evaluations([])
            assert paths == []

    def test_filename_collision_handling(self):
        """Test that duplicate filenames get numbered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = EvaluationWriter(base_path=Path(tmpdir))

            # Same job details but different board_job_id
            job1 = create_sample_job(board_job_id="1")
            job2 = create_sample_job(board_job_id="2")

            jobs_and_evals = [
                (job1, create_sample_evaluation()),
                (job2, create_sample_evaluation()),
            ]

            paths = writer.write_evaluations(jobs_and_evals)

            assert len(paths) == 2
            # Check that files have different names
            filenames = [p.name for p in paths]
            assert len(set(filenames)) == 2


class TestOrchestratorEvaluateJobs:
    """Tests for SearchOrchestrator._evaluate_jobs method."""

    def test_evaluate_jobs_empty_list(self):
        """Test evaluating empty list returns empty results."""
        from config.loader import Config
        from search.orchestrator import SearchOrchestrator

        # Create minimal config
        config = Config({
            "boards": [],
            "filters": {},
            "search_criteria": {},
        })

        # Create orchestrator (will have no adapters)
        with patch.object(SearchOrchestrator, "_initialize_adapters"):
            orchestrator = SearchOrchestrator(config)
            orchestrator.adapters = []

            evaluations, errors = orchestrator._evaluate_jobs([])

            assert evaluations == []
            assert errors == []

    def test_evaluate_jobs_success(self):
        """Test successful job evaluation."""
        from config.loader import Config
        from search.orchestrator import SearchOrchestrator

        # Create config and orchestrator
        config = Config({
            "boards": [],
            "filters": {},
            "search_criteria": {},
        })

        with patch.object(SearchOrchestrator, "_initialize_adapters"):
            orchestrator = SearchOrchestrator(config)
            orchestrator.adapters = []

            # Patch AIEvaluator where it's imported in _evaluate_jobs
            with patch("evaluation.AIEvaluator") as mock_evaluator_class:
                mock_evaluator = MagicMock()
                mock_result = create_sample_evaluation()
                mock_evaluator.evaluate_job.return_value = mock_result
                mock_evaluator_class.return_value = mock_evaluator

                jobs = [create_sample_job()]
                evaluations, errors = orchestrator._evaluate_jobs(jobs)

                assert len(evaluations) == 1
                assert errors == []
                mock_evaluator.evaluate_job.assert_called_once_with(jobs[0])

    def test_evaluate_jobs_with_errors(self):
        """Test job evaluation handles errors gracefully."""
        from config.loader import Config
        from search.orchestrator import SearchOrchestrator

        # Create config and orchestrator
        config = Config({
            "boards": [],
            "filters": {},
            "search_criteria": {},
        })

        with patch.object(SearchOrchestrator, "_initialize_adapters"):
            orchestrator = SearchOrchestrator(config)
            orchestrator.adapters = []

            # Patch AIEvaluator where it's imported in _evaluate_jobs
            with patch("evaluation.AIEvaluator") as mock_evaluator_class:
                mock_evaluator = MagicMock()
                mock_result = create_sample_evaluation()
                mock_evaluator.evaluate_job.side_effect = [
                    mock_result,
                    Exception("API error"),
                ]
                mock_evaluator_class.return_value = mock_evaluator

                jobs = [
                    create_sample_job(board_job_id="1"),
                    create_sample_job(board_job_id="2"),
                ]
                evaluations, errors = orchestrator._evaluate_jobs(jobs)

                assert len(evaluations) == 1
                assert len(errors) == 1
                assert "API error" in errors[0]
