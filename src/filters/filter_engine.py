"""
FilterEngine for deduplication and filtering of job postings.
"""

import re
from typing import Dict, List, Set
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta

try:
    from core.models import JobPosting
except ImportError:
    from ..core.models import JobPosting


class FilterEngine:
    """Handles deduplication and filtering of job postings."""

    def __init__(
        self,
        filters_config: Dict,
        search_criteria_config: Dict = None,
        similarity_threshold: float = 0.85
    ):
        """
        Initialize FilterEngine with configuration.

        Args:
            filters_config: Configuration from filters.yaml
            search_criteria_config: Configuration from search-criteria-complex.yaml
            similarity_threshold: Threshold for fuzzy matching (0-1)
        """
        self.filters_config = filters_config
        self.search_criteria_config = search_criteria_config or {}
        self.similarity_threshold = similarity_threshold

        # Extract filter settings
        # Note: Config loader already unwraps the top-level "filters" key
        self.dedup_config = filters_config.get("deduplication", {})
        self.blacklist_config = filters_config.get("blacklist", {})

        # Seen jobs tracking for deduplication
        self.seen_job_ids: Set[str] = set()
        self.seen_company_titles: Set[str] = set()
        self.seen_titles: List[str] = []

    def filter_jobs(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """
        Apply all filters to job postings in order.

        Filter pipeline:
        1. Company blacklist
        2. Title/keyword blacklist
        3. Complex search criteria (salary, experience, tech stack, company stage)
        4. Deduplication (fuzzy matching)

        Args:
            jobs: List of job postings to filter

        Returns:
            Filtered list of job postings
        """
        filtered = jobs

        # Step 1: Company blacklist
        filtered = self._filter_by_company_blacklist(filtered)

        # Step 2: Title and keyword blacklist
        filtered = self._filter_by_title_keywords(filtered)

        # Step 3: Complex search criteria (if configured)
        if self.search_criteria_config:
            filtered = self.filter_by_search_criteria(filtered)

        # Step 4: Deduplication
        filtered = self._deduplicate(filtered)

        return filtered

    def _filter_by_company_blacklist(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Filter out jobs from blacklisted companies."""
        blacklisted_companies = self.blacklist_config.get("companies", [])
        if not blacklisted_companies:
            return jobs

        # Convert to lowercase for case-insensitive matching
        blacklisted_lower = [c.lower() for c in blacklisted_companies]

        return [
            job for job in jobs
            if job.company.lower() not in blacklisted_lower
        ]

    def _filter_by_title_keywords(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Filter out jobs with blacklisted titles or keywords."""
        blacklisted_titles = self.blacklist_config.get("titles", [])
        blacklisted_keywords = self.blacklist_config.get("keywords", [])

        if not blacklisted_titles and not blacklisted_keywords:
            return jobs

        filtered = []
        for job in jobs:
            # Check title blacklist
            if any(title.lower() in job.title.lower() for title in blacklisted_titles):
                continue

            # Check keyword blacklist in description
            if any(kw.lower() in job.description.lower() for kw in blacklisted_keywords):
                continue

            filtered.append(job)

        return filtered

    def filter_by_search_criteria(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """
        Filter jobs based on complex search criteria from search-criteria-complex.yaml.

        Applies filters for:
        - Salary range
        - Experience level
        - Required tech stack
        - Company stage
        - Location preferences
        - Posted date range
        """
        filtered = []
        search_config = self.search_criteria_config.get("search", {})

        for job in jobs:
            # Salary range check
            if not self._matches_salary_range(job, search_config):
                continue

            # Experience level check
            if not self._matches_experience_level(job, search_config):
                continue

            # Required tech stack check
            if not self._has_required_tech(job, search_config):
                continue

            # Company stage filter
            if not self._matches_company_stage(job, search_config):
                continue

            # Posted date range check
            if not self._matches_date_range(job, search_config):
                continue

            filtered.append(job)

        return filtered

    def _matches_salary_range(self, job: JobPosting, search_config: Dict) -> bool:
        """Check if job salary matches required range."""
        salary_range = search_config.get("salary_range", {})
        if not salary_range:
            return True  # No salary filter configured

        min_salary = salary_range.get("min")
        max_salary = salary_range.get("max")

        # If job has no salary info, be lenient (allow it through)
        if not job.salary_min and not job.salary_max:
            return True

        # If job has salary, check if it overlaps with our range
        if job.salary_max and min_salary:
            if job.salary_max < min_salary:
                return False  # Job pays less than we want

        if job.salary_min and max_salary:
            if job.salary_min > max_salary:
                return False  # Job requires more than we want to pay

        return True

    def _matches_experience_level(self, job: JobPosting, search_config: Dict) -> bool:
        """Check if job experience level matches required levels."""
        required_levels = search_config.get("experience_level", [])
        if not required_levels:
            return True  # No experience filter configured

        # Check if any required level appears in title or description
        job_text = f"{job.title} {job.description}".lower()
        return any(level.lower() in job_text for level in required_levels)

    def _has_required_tech(self, job: JobPosting, search_config: Dict) -> bool:
        """Check if job mentions required technologies."""
        tech_stack = search_config.get("tech_stack", {})
        required_tech = tech_stack.get("required", [])

        if not required_tech:
            return True  # No tech requirements configured

        # Check if all required tech appears in description or requirements
        job_text = f"{job.description} {' '.join(job.requirements)}".lower()
        return all(tech.lower() in job_text for tech in required_tech)

    def _matches_company_stage(self, job: JobPosting, search_config: Dict) -> bool:
        """Check if company stage matches preferences."""
        company_stage = search_config.get("company_stage", {})
        excluded_stages = company_stage.get("exclude", [])

        if not excluded_stages:
            return True  # No stage filter configured

        # Check if any excluded stage appears in description
        job_text = f"{job.description}".lower()
        return not any(stage.lower() in job_text for stage in excluded_stages)

    def _matches_date_range(self, job: JobPosting, search_config: Dict) -> bool:
        """Check if job was posted within the required date range."""
        date_range = search_config.get("date_range", {})
        posted_within_days = date_range.get("posted_within_days")

        if not posted_within_days or not job.posted_date:
            return True  # No date filter or no posted date

        cutoff_date = datetime.now() - timedelta(days=posted_within_days)
        return job.posted_date >= cutoff_date

    def _deduplicate(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """
        Remove duplicate job postings using multiple strategies.

        Deduplication methods (in order):
        1. Board-specific job ID (exact match)
        2. Company + title exact match
        3. Title fuzzy matching (85% similarity threshold)
        """
        if not self.dedup_config.get("enabled", True):
            return jobs

        dedup_methods = self.dedup_config.get("methods", [])
        threshold = self.dedup_config.get("similarity_threshold", self.similarity_threshold)

        unique_jobs = []

        for job in jobs:
            # Method 1: Job ID deduplication
            if "job_id" in dedup_methods:
                if job.board_job_id and job.board_job_id in self.seen_job_ids:
                    continue
                if job.board_job_id:
                    self.seen_job_ids.add(job.board_job_id)

            # Method 2: Company + title exact match
            if "company_name" in dedup_methods:
                company_title_key = f"{job.company.lower()}::{job.title.lower()}"
                if company_title_key in self.seen_company_titles:
                    continue
                self.seen_company_titles.add(company_title_key)

            # Method 3: Fuzzy title matching
            if "title_similarity" in dedup_methods:
                is_duplicate = False
                for seen_title in self.seen_titles:
                    similarity = fuzz.ratio(job.title.lower(), seen_title.lower()) / 100.0
                    if similarity >= threshold:
                        is_duplicate = True
                        break

                if is_duplicate:
                    continue

                self.seen_titles.append(job.title)

            unique_jobs.append(job)

        return unique_jobs

    def reset(self):
        """Reset seen jobs tracking for new search session."""
        self.seen_job_ids.clear()
        self.seen_company_titles.clear()
        self.seen_titles.clear()
