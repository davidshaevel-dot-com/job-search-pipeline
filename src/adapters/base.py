"""
Base Adapter - Abstract base class for job board adapters.
"""

from abc import ABC, abstractmethod
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


class BaseAdapter(ABC):
    """Abstract base class for job board adapters."""
    
    def __init__(self, config: dict):
        """Initialize adapter with configuration."""
        self.config = config
        self.board_name = config.get("name", "unknown")
    
    @abstractmethod
    def search(self, criteria: dict) -> List[JobPosting]:
        """
        Execute search and return standardized job postings.
        
        Args:
            criteria: Search criteria dictionary
            
        Returns:
            List of JobPosting objects
        """
        pass
    
    @abstractmethod
    def get_job_details(self, job_id: str) -> JobPosting:
        """
        Fetch full job details for a specific posting.
        
        Args:
            job_id: Board-specific job ID
            
        Returns:
            JobPosting object with full details
        """
        pass

