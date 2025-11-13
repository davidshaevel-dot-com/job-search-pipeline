"""
Core data models for job search pipeline.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class JobPosting:
    """Standardized job posting data structure."""
    title: str
    company: str
    location: str
    remote_type: str  # "remote", "hybrid", "onsite"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: str = ""
    requirements: List[str] = None
    posted_date: Optional[datetime] = None
    job_url: str = ""
    board_name: str = ""
    board_job_id: str = ""
    raw_data: dict = None
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.raw_data is None:
            self.raw_data = {}

