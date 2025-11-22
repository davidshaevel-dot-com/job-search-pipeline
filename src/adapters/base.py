"""
Base Adapter - Abstract base class for job board adapters.
"""

from abc import ABC, abstractmethod
from typing import List

from core.models import JobPosting


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

