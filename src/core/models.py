"""
Core data models for job search pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


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
    requirements: List[str] = field(default_factory=list)
    posted_date: Optional[datetime] = None
    job_url: str = ""
    board_name: str = ""
    board_job_id: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)

