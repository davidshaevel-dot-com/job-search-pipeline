"""
JobTracker for persisting processed job postings to avoid re-processing.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

try:
    from core.models import JobPosting
except ImportError:
    from ..core.models import JobPosting


class JobTracker:
    """Tracks processed job postings to avoid re-processing."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize JobTracker.

        Args:
            data_dir: Directory for storing processed jobs data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.processed_file = self.data_dir / "processed_jobs.json"
        self.processed_jobs: Dict[str, Dict] = {}  # Canonical storage by board_job_id or company::title
        self.seen_job_ids: Set[str] = set()  # Track board_job_ids for fast lookup
        self.seen_company_titles: Set[str] = set()  # Track company::title keys for fast lookup

        self._load_processed_jobs()

    def _load_processed_jobs(self):
        """Load previously processed jobs from disk and rebuild lookup sets."""
        if self.processed_file.exists():
            try:
                with open(self.processed_file, 'r') as f:
                    self.processed_jobs = json.load(f)

                # Rebuild lookup sets from loaded data
                for key, job_data in self.processed_jobs.items():
                    board_job_id = job_data.get("board_job_id")
                    if board_job_id:
                        self.seen_job_ids.add(board_job_id)

                    # Always rebuild company::title from job data (not key format)
                    company = job_data.get("company", "").lower()
                    title = job_data.get("title", "").lower()
                    if company and title:
                        company_title_key = f"{company}::{title}"
                        self.seen_company_titles.add(company_title_key)

            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load processed jobs: {e}")
                self.processed_jobs = {}
                self.seen_job_ids = set()
                self.seen_company_titles = set()
        else:
            self.processed_jobs = {}
            self.seen_job_ids = set()
            self.seen_company_titles = set()

    def _save_processed_jobs(self):
        """Save processed jobs to disk."""
        try:
            with open(self.processed_file, 'w') as f:
                json.dump(self.processed_jobs, f, indent=2, default=str)
        except IOError as e:
            logger.warning(f"Could not save processed jobs: {e}")

    def is_processed(self, job: JobPosting) -> bool:
        """
        Check if a job has been processed before.

        Uses multiple identifiers:
        1. Board-specific job ID
        2. Company + title combination

        Args:
            job: Job posting to check

        Returns:
            True if job has been processed before
        """
        # Check by job ID in set (fast O(1) lookup)
        if job.board_job_id and job.board_job_id in self.seen_job_ids:
            return True

        # Check by company + title in set (fast O(1) lookup)
        company_title_key = self._get_company_title_key(job)
        if company_title_key in self.seen_company_titles:
            return True

        return False

    def _mark_single_job(self, job: JobPosting, action: str):
        """
        Helper method to mark a single job as processed (without saving).

        Args:
            job: Job posting to mark
            action: Action taken (e.g., "evaluated", "applied", "rejected")
        """
        job_data = {
            "title": job.title,
            "company": job.company,
            "board_name": job.board_name,
            "board_job_id": job.board_job_id,
            "action": action,
            "processed_at": datetime.now().isoformat()
        }

        # Store once under canonical key (prefer board_job_id if available)
        canonical_key = job.board_job_id if job.board_job_id else self._get_company_title_key(job)
        self.processed_jobs[canonical_key] = job_data

        # Track both identifiers in lookup sets for fast checking
        if job.board_job_id:
            self.seen_job_ids.add(job.board_job_id)
        company_title_key = self._get_company_title_key(job)
        self.seen_company_titles.add(company_title_key)

    def mark_processed(self, job: JobPosting, action: str = "evaluated"):
        """
        Mark a job as processed.

        Args:
            job: Job posting to mark
            action: Action taken (e.g., "evaluated", "applied", "rejected")
        """
        self._mark_single_job(job, action)
        self._save_processed_jobs()

    def mark_batch_processed(self, jobs: List[JobPosting], action: str = "evaluated"):
        """
        Mark multiple jobs as processed in a batch.

        Args:
            jobs: List of job postings to mark
            action: Action taken for all jobs
        """
        for job in jobs:
            self._mark_single_job(job, action)

        self._save_processed_jobs()

    def filter_unprocessed(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """
        Filter out jobs that have been processed before.

        Args:
            jobs: List of job postings to filter

        Returns:
            List of jobs that haven't been processed
        """
        return [job for job in jobs if not self.is_processed(job)]

    def get_processed_count(self) -> int:
        """
        Get count of unique processed jobs.

        Note: Since we now store each job only once, this accurately reflects
        the number of unique jobs processed (no duplicates).
        """
        return len(self.processed_jobs)

    def get_processed_by_board(self, board_name: str) -> List[Dict]:
        """
        Get all processed jobs from a specific board.

        Args:
            board_name: Name of the job board

        Returns:
            List of processed job data dictionaries (no duplicates - each job stored once)
        """
        return [
            job_data for job_data in self.processed_jobs.values()
            if job_data.get("board_name") == board_name
        ]

    def clear_processed(self):
        """Clear all processed jobs tracking (use with caution)."""
        self.processed_jobs = {}
        self.seen_job_ids = set()
        self.seen_company_titles = set()
        self._save_processed_jobs()

    @staticmethod
    def _get_company_title_key(job: JobPosting) -> str:
        """
        Generate a composite key from company and title.

        Args:
            job: Job posting

        Returns:
            Normalized company::title key
        """
        return f"{job.company.lower()}::{job.title.lower()}"
