"""
Evaluation writer for saving AI evaluation results to JSON files.

Phase 3: Saves EvaluationResult objects alongside job posting files.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.models import JobPosting
from evaluation import EvaluationResult

from .file_writer import get_output_directory, sanitize_filename

logger = logging.getLogger(__name__)


def format_evaluation_json(
    job: JobPosting,
    evaluation: EvaluationResult,
    include_job_summary: bool = True,
) -> Dict[str, Any]:
    """
    Format evaluation result for JSON output.

    Args:
        job: JobPosting that was evaluated
        evaluation: EvaluationResult from AI evaluation
        include_job_summary: Whether to include job details in output

    Returns:
        Dictionary ready for JSON serialization
    """
    output: Dict[str, Any] = {
        "evaluation": evaluation.to_dict(),
        "metadata": {
            "evaluated_at": datetime.now().isoformat(),
            "board_job_id": job.board_job_id,
            "board_name": job.board_name,
        },
    }

    if include_job_summary:
        output["job_summary"] = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "remote_type": job.remote_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "job_url": job.job_url,
        }

    return output


def get_evaluation_filename(job: JobPosting, counter: Optional[int] = None) -> str:
    """
    Generate filename for evaluation result.

    Uses same naming convention as job files but with _evaluation suffix.

    Args:
        job: JobPosting that was evaluated
        counter: Optional counter to append if filename would be duplicate

    Returns:
        Filename string (without extension)
    """
    company = sanitize_filename(job.company)
    title = sanitize_filename(job.title)

    filename = f"{company}_{title}_evaluation"

    if counter is not None:
        filename = f"{filename}_{counter}"

    return filename


class EvaluationWriter:
    """Handles writing evaluation results to JSON files."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize evaluation writer.

        Args:
            base_path: Base path for evaluation files (defaults to jobs/pipeline/)
        """
        if base_path is None:
            # Default to jobs/pipeline/ relative to project root
            project_root = Path(__file__).parent.parent.parent
            base_path = project_root / "jobs" / "pipeline"

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write_evaluations(
        self,
        jobs_and_evaluations: List[Tuple[JobPosting, EvaluationResult]],
        date: Optional[datetime] = None,
        include_job_summary: bool = True,
    ) -> List[Path]:
        """
        Write multiple evaluation results to JSON files.

        Args:
            jobs_and_evaluations: List of (JobPosting, EvaluationResult) tuples
            date: Date to use for directory (defaults to today)
            include_job_summary: Whether to include job details in output

        Returns:
            List of Path objects for written files
        """
        if not jobs_and_evaluations:
            return []

        output_dir = get_output_directory(self.base_path, date)
        output_dir.mkdir(parents=True, exist_ok=True)

        written_files = []
        existing_filenames = {p.name for p in output_dir.glob("*.json")}

        for job, evaluation in jobs_and_evaluations:
            # Generate unique filename
            filename = f"{get_evaluation_filename(job)}.json"

            # Handle filename collisions
            counter = 1
            while filename in existing_filenames:
                filename = f"{get_evaluation_filename(job, counter=counter)}.json"
                counter += 1

            file_path = output_dir / filename

            # Format and write JSON
            content = format_evaluation_json(
                job, evaluation, include_job_summary=include_job_summary
            )

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

            written_files.append(file_path)
            existing_filenames.add(filename)

            logger.debug(
                f"Wrote evaluation for '{job.title}' at {job.company}: "
                f"{evaluation.grade.value} ({evaluation.overall_score:.1f})"
            )

        logger.info(f"Wrote {len(written_files)} evaluation file(s) to {output_dir}")

        return written_files

    def write_evaluation(
        self,
        job: JobPosting,
        evaluation: EvaluationResult,
        date: Optional[datetime] = None,
        include_job_summary: bool = True,
    ) -> Optional[Path]:
        """
        Write single evaluation result to JSON file.

        Args:
            job: JobPosting that was evaluated
            evaluation: EvaluationResult from AI evaluation
            date: Date to use for directory (defaults to today)
            include_job_summary: Whether to include job details in output

        Returns:
            Path object for written file
        """
        files = self.write_evaluations(
            [(job, evaluation)], date, include_job_summary=include_job_summary
        )
        return files[0] if files else None

    def write_summary(
        self,
        jobs_and_evaluations: List[Tuple[JobPosting, EvaluationResult]],
        date: Optional[datetime] = None,
    ) -> Optional[Path]:
        """
        Write a summary file containing all evaluations in a single JSON.

        Useful for quick review of all jobs found in a search run.

        Args:
            jobs_and_evaluations: List of (JobPosting, EvaluationResult) tuples
            date: Date to use for directory (defaults to today)

        Returns:
            Path object for summary file
        """
        if not jobs_and_evaluations:
            return None

        output_dir = get_output_directory(self.base_path, date)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build summary
        summary: Dict[str, Any] = {
            "generated_at": datetime.now().isoformat(),
            "total_jobs": len(jobs_and_evaluations),
            "grade_distribution": {},
            "jobs": [],
        }

        # Count grades
        grade_counts: Dict[str, int] = {}
        for job, evaluation in jobs_and_evaluations:
            grade = evaluation.grade.value
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

            summary["jobs"].append(
                {
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "grade": grade,
                    "overall_score": evaluation.overall_score,
                    "recommendation": evaluation.recommendation.value,
                    "job_url": job.job_url,
                }
            )

        summary["grade_distribution"] = grade_counts

        # Sort jobs by score (highest first)
        summary["jobs"].sort(key=lambda x: x["overall_score"], reverse=True)

        # Write summary file
        summary_path = output_dir / "evaluation_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Wrote evaluation summary to {summary_path}")

        return summary_path
