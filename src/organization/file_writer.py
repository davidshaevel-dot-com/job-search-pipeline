"""
File writer for saving job postings to organized directory structure.

Creates date-based directories and writes job descriptions to files.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..adapters.base import JobPosting


def sanitize_filename(text: str, max_length: int = 100) -> str:
    """
    Sanitize text for use as filename.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length of filename
        
    Returns:
        Sanitized filename-safe string
    """
    # Remove or replace invalid filename characters
    # Keep alphanumeric, spaces, hyphens, underscores
    sanitized = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('_')
    
    return sanitized


def format_job_content(job: JobPosting) -> str:
    """
    Format job posting content for file output.
    
    Args:
        job: JobPosting object
        
    Returns:
        Formatted string with job details
    """
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append(f"JOB POSTING: {job.title}")
    lines.append("=" * 80)
    lines.append("")
    
    # Basic Information
    lines.append(f"Company: {job.company}")
    lines.append(f"Location: {job.location}")
    lines.append(f"Remote Type: {job.remote_type.title()}")
    
    if job.salary_min or job.salary_max:
        salary_str = ""
        if job.salary_min:
            salary_str = f"${job.salary_min:,}"
        if job.salary_min and job.salary_max:
            salary_str += " - "
        if job.salary_max:
            salary_str += f"${job.salary_max:,}"
        lines.append(f"Salary: {salary_str}")
    
    if job.posted_date:
        lines.append(f"Posted Date: {job.posted_date.strftime('%Y-%m-%d')}")
    
    lines.append(f"Job URL: {job.job_url}")
    lines.append(f"Board: {job.board_name}")
    lines.append(f"Board Job ID: {job.board_job_id}")
    lines.append("")
    
    # Description
    if job.description:
        lines.append("-" * 80)
        lines.append("DESCRIPTION")
        lines.append("-" * 80)
        lines.append(job.description)
        lines.append("")
    
    # Requirements
    if job.requirements:
        lines.append("-" * 80)
        lines.append("REQUIREMENTS")
        lines.append("-" * 80)
        for req in job.requirements:
            lines.append(f"• {req}")
        lines.append("")
    
    # Footer
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def get_output_directory(base_path: Path, date: Optional[datetime] = None) -> Path:
    """
    Get output directory path for date-based organization.
    
    Args:
        base_path: Base path for job files (e.g., jobs/pipeline/)
        date: Date to use for directory (defaults to today)
        
    Returns:
        Path object for date-based directory
    """
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime("%Y-%m-%d")
    return base_path / date_str


def get_job_filename(job: JobPosting, counter: Optional[int] = None) -> str:
    """
    Generate filename for job posting.
    
    Args:
        job: JobPosting object
        counter: Optional counter to append if filename would be duplicate
        
    Returns:
        Filename string (without extension)
    """
    company = sanitize_filename(job.company)
    title = sanitize_filename(job.title)
    
    filename = f"{company}_{title}"
    
    if counter is not None:
        filename = f"{filename}_{counter}"
    
    return filename


class FileWriter:
    """Handles writing job postings to organized file structure."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize file writer.
        
        Args:
            base_path: Base path for job files (defaults to jobs/pipeline/)
        """
        if base_path is None:
            # Default to jobs/pipeline/ relative to project root
            project_root = Path(__file__).parent.parent.parent
            base_path = project_root / "jobs" / "pipeline"
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def write_jobs(self, jobs: List[JobPosting], date: Optional[datetime] = None) -> List[Path]:
        """
        Write multiple job postings to files.
        
        Args:
            jobs: List of JobPosting objects
            date: Date to use for directory (defaults to today)
            
        Returns:
            List of Path objects for written files
        """
        if not jobs:
            return []
        
        output_dir = get_output_directory(self.base_path, date)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        written_files = []
        
        for job in jobs:
            # Generate base filename
            base_filename = get_job_filename(job)
            filename = base_filename
            file_path = output_dir / f"{filename}.txt"
            
            # Check filesystem for existing files and ensure unique filename
            # Note: This approach has a potential race condition if multiple processes
            # run concurrently. For Phase 1 (single-process execution), this is acceptable.
            # In Phase 6 (concurrent execution), this should be replaced with atomic
            # file creation using exclusive file creation mode ('x' flag) or similar.
            counter = 1
            while file_path.exists():
                filename = f"{base_filename}_{counter}"
                file_path = output_dir / f"{filename}.txt"
                counter += 1
            
            # Write file
            content = format_job_content(job)
            file_path.write_text(content, encoding="utf-8")
            
            written_files.append(file_path)
        
        return written_files
    
    def write_job(self, job: JobPosting, date: Optional[datetime] = None) -> Optional[Path]:
        """
        Write single job posting to file.
        
        Args:
            job: JobPosting object
            date: Date to use for directory (defaults to today)
            
        Returns:
            Path object for written file
        """
        files = self.write_jobs([job], date)
        return files[0] if files else None

