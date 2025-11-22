"""
JSearch Adapter - Job board adapter for JSearch API via RapidAPI.

JSearch aggregates job postings from Google for Jobs, which includes
LinkedIn, Indeed, Glassdoor, ZipRecruiter, Monster, Dice, and more.

API Documentation: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
"""

import logging
import threading
import time
from datetime import datetime
from typing import List, Optional

import requests

from adapters.base import BaseAdapter
from core.models import JobPosting

logger = logging.getLogger(__name__)


class JSearchAdapter(BaseAdapter):
    """Adapter for JSearch API via RapidAPI."""

    API_BASE_URL = "https://jsearch.p.rapidapi.com"

    def __init__(self, config: dict):
        """
        Initialize JSearch adapter with configuration.

        Args:
            config: Configuration dictionary containing:
                - api_key: RapidAPI key (required)
                - api_host: RapidAPI host (default: jsearch.p.rapidapi.com)
                - rate_limit: Rate limit configuration
                - search_params: Default search parameters
        """
        super().__init__(config)

        # Required configuration
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ValueError("JSearch adapter requires 'api_key' in configuration")

        # Optional configuration with defaults
        self.api_host = config.get("api_host", "jsearch.p.rapidapi.com")
        self.rate_limit = config.get("rate_limit", {})
        self.search_params = config.get("search_params", {})

        # Rate limiting
        self.requests_per_second = self.rate_limit.get("requests_per_second", 1)
        self.last_request_time = 0.0
        self._rate_limit_lock = threading.Lock()  # Thread-safe rate limiting

        # Warn if rate limit seems too high for typical RapidAPI tiers
        if self.requests_per_second > 5:
            logger.warning(
                f"JSearch rate limit set to {self.requests_per_second} req/sec. "
                f"This is only safe for RapidAPI Pro tier ($50/mo) or higher. "
                f"Free tier: 50 req/7 days. Basic ($10): 10K req/month. Pro ($50): 50K req/month. "
                f"Verify your subscription at https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch/pricing"
            )

        logger.info(f"Initialized JSearch adapter for board '{self.board_name}'")

    def _get_headers(self) -> dict:
        """
        Get HTTP headers for RapidAPI authentication.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }

    def _enforce_rate_limit(self):
        """
        Enforce rate limiting between requests (thread-safe).

        Uses a lock to prevent race conditions when multiple threads
        make concurrent requests. This ensures rate limits are respected
        even during parallel execution in Phase 2+.
        """
        if self.requests_per_second <= 0:
            return

        min_interval = 1.0 / self.requests_per_second

        with self._rate_limit_lock:
            elapsed = time.time() - self.last_request_time

            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)

            self.last_request_time = time.time()

    def _build_query_string(self, criteria: dict) -> str:
        """
        Build JSearch query string from search criteria.

        JSearch uses a single 'query' parameter that combines keywords and location.
        Example: "DevOps Engineer in Austin, TX"

        Args:
            criteria: Search criteria dictionary

        Returns:
            Query string for JSearch API
        """
        keywords = criteria.get("keywords", [])
        location = criteria.get("location", "")

        # Combine keywords
        if isinstance(keywords, list):
            keywords_str = " ".join(keywords)
        else:
            keywords_str = str(keywords)

        # Build query string
        if location:
            query = f"{keywords_str} in {location}"
        else:
            query = keywords_str

        logger.debug(f"Built query string: '{query}'")
        return query

    def _build_search_params(self, criteria: dict) -> dict:
        """
        Build JSearch API query parameters.

        Args:
            criteria: Search criteria dictionary

        Returns:
            Dictionary of query parameters for JSearch API
        """
        # Start with configured default parameters
        params = self.search_params.copy()

        # Required: query string
        params["query"] = self._build_query_string(criteria)

        # Optional parameters from criteria (override defaults)
        if "num_pages" in criteria:
            params["num_pages"] = criteria["num_pages"]

        if "date_posted" in criteria:
            params["date_posted"] = criteria["date_posted"]

        if "remote_jobs_only" in criteria:
            params["remote_jobs_only"] = str(criteria["remote_jobs_only"]).lower()

        if "employment_types" in criteria:
            params["employment_types"] = criteria["employment_types"]

        logger.debug(f"Built search params: {params}")
        return params

    def _parse_remote_type(self, job_data: dict) -> str:
        """
        Determine remote type from JSearch job data.

        Args:
            job_data: JSearch job data dictionary

        Returns:
            Remote type: "remote", "hybrid", or "onsite"
        """
        # Check explicit is_remote flag
        if job_data.get("job_is_remote", False):
            return "remote"

        # Check description for hybrid mentions
        description = job_data.get("job_description", "").lower()
        if "hybrid" in description:
            return "hybrid"

        # Default to onsite
        return "onsite"

    def _parse_requirements(self, job_data: dict) -> List[str]:
        """
        Extract requirements from JSearch job data.

        Combines required skills and qualifications from job highlights.

        Args:
            job_data: JSearch job data dictionary

        Returns:
            List of requirement strings
        """
        requirements = []

        # Add required skills
        required_skills = job_data.get("job_required_skills")
        if required_skills and isinstance(required_skills, list):
            requirements.extend(required_skills)

        # Add qualifications from highlights
        highlights = job_data.get("job_highlights", {})
        if isinstance(highlights, dict):
            qualifications = highlights.get("Qualifications", [])
            if isinstance(qualifications, list):
                requirements.extend(qualifications)

        return requirements

    def _parse_posted_date(self, job_data: dict) -> Optional[datetime]:
        """
        Parse posted date from JSearch job data.

        Args:
            job_data: JSearch job data dictionary

        Returns:
            Datetime object or None if not available
        """
        # Try timestamp first (most accurate)
        timestamp = job_data.get("job_posted_at_timestamp")
        if timestamp:
            try:
                return datetime.fromtimestamp(timestamp)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse timestamp {timestamp}: {e}")

        # Try datetime string as fallback
        datetime_str = job_data.get("job_posted_at_datetime_utc")
        if datetime_str:
            try:
                return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse datetime {datetime_str}: {e}")

        return None

    def _parse_location(self, job_data: dict) -> str:
        """
        Build location string from JSearch job data.

        Args:
            job_data: JSearch job data dictionary

        Returns:
            Location string (e.g., "Austin, TX, US")
        """
        city = job_data.get("job_city", "")
        state = job_data.get("job_state", "")
        country = job_data.get("job_country", "")

        # Build location string with available components
        location_parts = [p for p in [city, state, country] if p]
        return ", ".join(location_parts) if location_parts else "Location not specified"

    def _convert_to_job_posting(self, job_data: dict) -> JobPosting:
        """
        Convert JSearch job data to JobPosting object.

        Maps 40+ JSearch fields to standardized JobPosting model.

        Args:
            job_data: JSearch job data dictionary

        Returns:
            JobPosting object
        """
        return JobPosting(
            title=job_data.get("job_title", ""),
            company=job_data.get("employer_name", ""),
            location=self._parse_location(job_data),
            remote_type=self._parse_remote_type(job_data),
            salary_min=job_data.get("job_min_salary"),
            salary_max=job_data.get("job_max_salary"),
            description=job_data.get("job_description", ""),
            requirements=self._parse_requirements(job_data),
            posted_date=self._parse_posted_date(job_data),
            job_url=job_data.get("job_apply_link", ""),
            board_name=self.board_name,
            board_job_id=job_data.get("job_id", ""),
            raw_data=job_data  # Store full response for debugging/future use
        )

    def search(self, criteria: dict) -> List[JobPosting]:
        """
        Execute search and return standardized job postings.

        Args:
            criteria: Search criteria dictionary containing:
                - keywords: List of keywords or string
                - location: Location string (optional)
                - num_pages: Number of pages to fetch (optional, default from config)
                - date_posted: Filter by date (optional, default from config)
                - remote_jobs_only: Boolean for remote-only (optional, default from config)
                - employment_types: Employment type filter (optional, default from config)

        Returns:
            List of JobPosting objects

        Raises:
            requests.RequestException: If API request fails
        """
        self._enforce_rate_limit()

        # Build API request
        url = f"{self.API_BASE_URL}/search"
        headers = self._get_headers()
        params = self._build_search_params(criteria)

        logger.info(f"Searching JSearch with query: '{params.get('query')}'")

        try:
            # Execute API request
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            # Parse response
            data = response.json()

            # Check API status
            if data.get("status") != "OK":
                logger.error(f"JSearch API returned non-OK status: {data.get('status')}")
                return []

            # Extract job data
            jobs_data = data.get("data", [])
            logger.info(f"JSearch returned {len(jobs_data)} jobs")

            # Convert to JobPosting objects
            job_postings = []
            for job_data in jobs_data:
                try:
                    job_posting = self._convert_to_job_posting(job_data)
                    job_postings.append(job_posting)
                except Exception as e:
                    logger.error(f"Failed to convert job data: {e}")
                    logger.debug(f"Problematic job data: {job_data}")
                    continue

            logger.info(f"Successfully converted {len(job_postings)} jobs to JobPosting objects")
            return job_postings

        except requests.RequestException as e:
            logger.error(f"JSearch API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during JSearch search: {e}")
            raise

    def get_job_details(self, job_id: str) -> JobPosting:
        """
        Fetch full job details for a specific posting.

        Note: JSearch's /search endpoint already provides comprehensive job details
        (40+ fields), so this method uses the same endpoint with job_id filter.

        Args:
            job_id: JSearch job ID

        Returns:
            JobPosting object with full details

        Raises:
            requests.RequestException: If API request fails
            ValueError: If job not found
        """
        self._enforce_rate_limit()

        # Build API request to search by job_id
        url = f"{self.API_BASE_URL}/job-details"
        headers = self._get_headers()
        params = {"job_id": job_id}

        logger.info(f"Fetching JSearch job details for job_id: {job_id}")

        try:
            # Execute API request
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            # Parse response
            data = response.json()

            # Check API status
            if data.get("status") != "OK":
                logger.error(f"JSearch API returned non-OK status: {data.get('status')}")
                raise ValueError(f"Job not found: {job_id}")

            # Extract job data
            jobs_data = data.get("data", [])
            if not jobs_data:
                raise ValueError(f"Job not found: {job_id}")

            # Convert first result to JobPosting
            job_posting = self._convert_to_job_posting(jobs_data[0])
            logger.info(f"Successfully fetched job details for {job_id}")
            return job_posting

        except requests.RequestException as e:
            logger.error(f"JSearch API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching job details: {e}")
            raise
