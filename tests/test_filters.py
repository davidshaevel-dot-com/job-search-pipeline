"""
Tests for filtering and deduplication functionality.
"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from src.core.models import JobPosting
from src.filters import FilterEngine, JobTracker


@pytest.fixture
def sample_jobs():
    """Create sample job postings for testing."""
    return [
        JobPosting(
            title="Senior DevOps Engineer",
            company="Tech Corp",
            location="Austin, TX",
            remote_type="hybrid",
            salary_min=150000,
            salary_max=180000,
            description="AWS, Terraform, Python, Kubernetes, CI/CD experience required.",
            requirements=["AWS", "Terraform", "Python"],
            posted_date=datetime.now() - timedelta(days=2),
            job_url="https://example.com/job1",
            board_name="JSearch",
            board_job_id="job_123"
        ),
        JobPosting(
            title="Junior Developer",
            company="Startup Inc",
            location="Remote",
            remote_type="remote",
            salary_min=60000,
            salary_max=80000,
            description="Entry level position for new graduates.",
            requirements=[],
            posted_date=datetime.now() - timedelta(days=1),
            job_url="https://example.com/job2",
            board_name="JSearch",
            board_job_id="job_456"
        ),
        JobPosting(
            title="DevOps Engineer",
            company="Tech Corp",
            location="Austin, TX",
            remote_type="hybrid",
            salary_min=150000,
            salary_max=180000,
            description="Similar position to our Senior DevOps role.",
            requirements=["AWS"],
            posted_date=datetime.now(),
            job_url="https://example.com/job3",
            board_name="JSearch",
            board_job_id="job_789"
        ),
        JobPosting(
            title="Platform Engineer",
            company="Blacklisted Company",
            location="San Francisco, CA",
            remote_type="onsite",
            salary_min=160000,
            salary_max=200000,
            description="Contract Only - AWS and Kubernetes.",
            requirements=["AWS", "Kubernetes"],
            posted_date=datetime.now() - timedelta(days=10),
            job_url="https://example.com/job4",
            board_name="JSearch",
            board_job_id="job_101"
        ),
    ]


@pytest.fixture
def filters_config():
    """Sample filters configuration."""
    return {
        "filters": {
            "deduplication": {
                "enabled": True,
                "methods": ["title_similarity", "company_name", "job_id"],
                "similarity_threshold": 0.85
            },
            "blacklist": {
                "companies": ["Blacklisted Company"],
                "titles": ["Junior", "Intern"],
                "keywords": ["Contract Only", "No Benefits"]
            }
        }
    }


@pytest.fixture
def search_criteria_config():
    """Sample complex search criteria configuration."""
    return {
        "search": {
            "salary_range": {
                "min": 140000,
                "max": 200000
            },
            "experience_level": ["Senior", "Staff", "Lead"],
            "tech_stack": {
                "required": ["AWS", "Terraform"]
            },
            "date_range": {
                "posted_within_days": 7
            }
        }
    }


class TestFilterEngine:
    """Tests for FilterEngine class."""

    def test_initialization(self, filters_config, search_criteria_config):
        """Test FilterEngine initialization."""
        engine = FilterEngine(filters_config, search_criteria_config)
        assert engine.similarity_threshold == 0.85
        assert engine.dedup_config == filters_config["filters"]["deduplication"]
        assert engine.blacklist_config == filters_config["filters"]["blacklist"]

    def test_company_blacklist_filter(self, sample_jobs, filters_config):
        """Test company blacklist filtering."""
        engine = FilterEngine(filters_config)
        filtered = engine._filter_by_company_blacklist(sample_jobs)

        # Should remove "Blacklisted Company"
        company_names = [job.company for job in filtered]
        assert "Blacklisted Company" not in company_names
        assert len(filtered) == 3  # 4 jobs - 1 blacklisted = 3

    def test_title_keyword_filter(self, sample_jobs, filters_config):
        """Test title and keyword blacklist filtering."""
        engine = FilterEngine(filters_config)
        filtered = engine._filter_by_title_keywords(sample_jobs)

        # Should remove "Junior Developer" (has "Junior" in title)
        # Should remove job with "Contract Only" in description
        titles = [job.title for job in filtered]
        assert "Junior Developer" not in titles
        assert len(filtered) == 2  # Removed Junior + Contract Only

    def test_salary_range_filter(self, sample_jobs, search_criteria_config):
        """Test salary range filtering."""
        engine = FilterEngine({}, search_criteria_config)
        search_config = search_criteria_config["search"]

        # Test job with salary below minimum
        low_salary_job = sample_jobs[1]  # Junior Developer: 60k-80k
        assert not engine._matches_salary_range(low_salary_job, search_config)

        # Test job with salary in range
        good_salary_job = sample_jobs[0]  # Senior DevOps: 150k-180k
        assert engine._matches_salary_range(good_salary_job, search_config)

    def test_experience_level_filter(self, sample_jobs, search_criteria_config):
        """Test experience level filtering."""
        engine = FilterEngine({}, search_criteria_config)
        search_config = search_criteria_config["search"]

        # Test job with "Senior" in title
        senior_job = sample_jobs[0]  # "Senior DevOps Engineer"
        assert engine._matches_experience_level(senior_job, search_config)

        # Test job without required experience level
        junior_job = sample_jobs[1]  # "Junior Developer"
        assert not engine._matches_experience_level(junior_job, search_config)

    def test_required_tech_filter(self, sample_jobs, search_criteria_config):
        """Test required tech stack filtering."""
        engine = FilterEngine({}, search_criteria_config)
        search_config = search_criteria_config["search"]

        # Test job with all required tech (AWS + Terraform)
        has_tech_job = sample_jobs[0]  # Has AWS, Terraform in description
        assert engine._has_required_tech(has_tech_job, search_config)

        # Test job missing required tech
        missing_tech_job = sample_jobs[2]  # Has only AWS, missing Terraform
        assert not engine._has_required_tech(missing_tech_job, search_config)

    def test_date_range_filter(self, sample_jobs, search_criteria_config):
        """Test posted date range filtering."""
        engine = FilterEngine({}, search_criteria_config)
        search_config = search_criteria_config["search"]

        # Test job posted within 7 days
        recent_job = sample_jobs[0]  # Posted 2 days ago
        assert engine._matches_date_range(recent_job, search_config)

        # Test job posted 10 days ago (outside 7-day window)
        old_job = sample_jobs[3]  # Posted 10 days ago
        assert not engine._matches_date_range(old_job, search_config)

    def test_deduplication_by_job_id(self, filters_config):
        """Test deduplication using board job IDs."""
        engine = FilterEngine(filters_config)

        # Create duplicate jobs with same job ID
        job1 = JobPosting(
            title="DevOps Engineer",
            company="Company A",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="duplicate_id"
        )
        job2 = JobPosting(
            title="DevOps Engineer (Reposted)",
            company="Company A",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="duplicate_id"
        )

        deduplicated = engine._deduplicate([job1, job2])
        assert len(deduplicated) == 1  # Should keep only first occurrence

    def test_deduplication_by_company_title(self, filters_config):
        """Test deduplication using company + title combination."""
        engine = FilterEngine(filters_config)

        # Create duplicate jobs with same company + title
        job1 = JobPosting(
            title="Senior DevOps Engineer",
            company="Tech Corp",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="id1"
        )
        job2 = JobPosting(
            title="Senior DevOps Engineer",
            company="Tech Corp",
            location="San Francisco, CA",  # Different location
            remote_type="hybrid",
            board_name="JSearch",
            board_job_id="id2"
        )

        deduplicated = engine._deduplicate([job1, job2])
        assert len(deduplicated) == 1  # Should deduplicate based on company + title

    def test_deduplication_by_fuzzy_matching(self, filters_config):
        """Test fuzzy title matching for deduplication."""
        engine = FilterEngine(filters_config)

        # Create similar titles (>85% similarity)
        job1 = JobPosting(
            title="Senior DevOps Engineer",
            company="Company A",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="id1"
        )
        job2 = JobPosting(
            title="Sr. DevOps Engineer",  # Very similar
            company="Company B",  # Different company
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="id2"
        )

        deduplicated = engine._deduplicate([job1, job2])
        # These are 85%+ similar, should deduplicate
        assert len(deduplicated) == 1

    def test_full_filter_pipeline(self, sample_jobs, filters_config, search_criteria_config):
        """Test complete filter pipeline."""
        engine = FilterEngine(filters_config, search_criteria_config)

        # Apply all filters
        filtered = engine.filter_jobs(sample_jobs)

        # Verify results
        # - Blacklisted Company removed
        # - Junior Developer removed (title blacklist + salary + experience level)
        # - Contract Only job removed (keyword blacklist + old posting date)
        # - DevOps Engineer might be removed (missing Terraform or fuzzy duplicate)
        # Expected: 0-1 jobs remaining (Senior DevOps Engineer if passes all filters)

        # Check no blacklisted companies
        companies = [job.company for job in filtered]
        assert "Blacklisted Company" not in companies

        # Check no blacklisted titles
        titles = [job.title for job in filtered]
        assert not any("Junior" in title for title in titles)

    def test_reset(self, filters_config):
        """Test resetting filter engine state."""
        engine = FilterEngine(filters_config)

        # Add some jobs
        job1 = JobPosting(
            title="DevOps Engineer",
            company="Company A",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="id1"
        )

        engine._deduplicate([job1])
        assert len(engine.seen_job_ids) > 0

        # Reset
        engine.reset()
        assert len(engine.seen_job_ids) == 0
        assert len(engine.seen_company_titles) == 0
        assert len(engine.seen_titles) == 0


class TestJobTracker:
    """Tests for JobTracker class."""

    def test_initialization(self, tmp_path):
        """Test JobTracker initialization."""
        tracker = JobTracker(data_dir=str(tmp_path))
        assert tracker.data_dir == tmp_path
        assert tracker.processed_file == tmp_path / "processed_jobs.json"
        assert isinstance(tracker.processed_jobs, dict)

    def test_mark_and_check_processed(self, tmp_path):
        """Test marking and checking processed jobs."""
        tracker = JobTracker(data_dir=str(tmp_path))

        job = JobPosting(
            title="DevOps Engineer",
            company="Tech Corp",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="job_123"
        )

        # Initially not processed
        assert not tracker.is_processed(job)

        # Mark as processed
        tracker.mark_processed(job, action="evaluated")

        # Now should be processed
        assert tracker.is_processed(job)

    def test_persistence(self, tmp_path):
        """Test that processed jobs persist across tracker instances."""
        job = JobPosting(
            title="DevOps Engineer",
            company="Tech Corp",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="job_123"
        )

        # Create first tracker and mark job
        tracker1 = JobTracker(data_dir=str(tmp_path))
        tracker1.mark_processed(job, action="evaluated")

        # Create second tracker and verify job is still marked
        tracker2 = JobTracker(data_dir=str(tmp_path))
        assert tracker2.is_processed(job)

    def test_filter_unprocessed(self, tmp_path):
        """Test filtering out processed jobs."""
        tracker = JobTracker(data_dir=str(tmp_path))

        job1 = JobPosting(
            title="DevOps Engineer",
            company="Company A",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="id1"
        )
        job2 = JobPosting(
            title="Platform Engineer",
            company="Company B",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="id2"
        )

        # Mark job1 as processed
        tracker.mark_processed(job1)

        # Filter should return only job2
        unprocessed = tracker.filter_unprocessed([job1, job2])
        assert len(unprocessed) == 1
        assert unprocessed[0].board_job_id == "id2"

    def test_batch_processing(self, tmp_path):
        """Test marking multiple jobs in a batch."""
        tracker = JobTracker(data_dir=str(tmp_path))

        jobs = [
            JobPosting(
                title=f"Job {i}",
                company="Company A",
                location="Austin, TX",
                remote_type="remote",
                board_name="JSearch",
                board_job_id=f"id_{i}"
            )
            for i in range(5)
        ]

        # Mark all as processed
        tracker.mark_batch_processed(jobs, action="discovered")

        # Verify all are processed
        for job in jobs:
            assert tracker.is_processed(job)

        assert tracker.get_processed_count() >= 5  # At least 5 (may have company+title keys too)

    def test_get_processed_by_board(self, tmp_path):
        """Test getting processed jobs by board."""
        tracker = JobTracker(data_dir=str(tmp_path))

        job1 = JobPosting(
            title="Job 1",
            company="Company A",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="id1"
        )
        job2 = JobPosting(
            title="Job 2",
            company="Company B",
            location="Austin, TX",
            remote_type="remote",
            board_name="Indeed",
            board_job_id="id2"
        )

        tracker.mark_processed(job1)
        tracker.mark_processed(job2)

        # Get JSearch jobs
        jsearch_jobs = tracker.get_processed_by_board("JSearch")
        assert len(jsearch_jobs) >= 1
        assert any(j["board_name"] == "JSearch" for j in jsearch_jobs)

    def test_clear_processed(self, tmp_path):
        """Test clearing all processed jobs."""
        tracker = JobTracker(data_dir=str(tmp_path))

        job = JobPosting(
            title="DevOps Engineer",
            company="Tech Corp",
            location="Austin, TX",
            remote_type="remote",
            board_name="JSearch",
            board_job_id="job_123"
        )

        tracker.mark_processed(job)
        assert tracker.get_processed_count() > 0

        # Clear
        tracker.clear_processed()
        assert tracker.get_processed_count() == 0
        assert not tracker.is_processed(job)
