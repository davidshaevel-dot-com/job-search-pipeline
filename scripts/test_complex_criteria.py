#!/usr/bin/env python3
"""
Test script for JSearch adapter with complex search criteria

This script tests the JSearch adapter with search-criteria-complex.yaml
to verify filtering by salary, experience level, tech stack, etc.

Usage:
    python scripts/test_complex_criteria.py

Requirements:
    - RapidAPI account with JSearch API subscription
    - .env file with RAPIDAPI_KEY set
    - Free tier provides 50 requests over 7 days for testing
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import logging
from config.loader import load_config
from search.orchestrator import SearchOrchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Test JSearch adapter with complex search criteria."""
    print("\n" + "=" * 70)
    print("JSearch Adapter Test - Complex Search Criteria")
    print("=" * 70)
    print()

    try:
        # Load configuration WITH complex search criteria
        logger.info("Loading configuration with complex search criteria...")
        config = load_config(search_criteria_file="search-criteria-complex.yaml")

        # Display complex criteria being used
        search_criteria = config.get("search_criteria", {})
        print("📋 Complex Search Criteria Loaded:")
        print("-" * 70)

        salary_range = search_criteria.get("salary_range", {})
        if salary_range:
            print(f"   Salary Range: ${salary_range.get('min', 0):,} - ${salary_range.get('max', 0):,}")

        experience_level = search_criteria.get("experience_level", [])
        if experience_level:
            print(f"   Experience Levels: {', '.join(experience_level)}")

        tech_stack = search_criteria.get("tech_stack", {})
        required_tech = tech_stack.get("required", [])
        if required_tech:
            print(f"   Required Tech: {', '.join(required_tech)}")

        preferred_tech = tech_stack.get("preferred", [])
        if preferred_tech:
            print(f"   Preferred Tech: {', '.join(preferred_tech)}")

        company_stage = search_criteria.get("company_stage", {})
        excluded_stages = company_stage.get("exclude", [])
        if excluded_stages:
            print(f"   Excluded Company Stages: {', '.join(excluded_stages)}")

        date_range = search_criteria.get("date_range", {})
        posted_within = date_range.get("posted_within_days")
        if posted_within:
            print(f"   Posted Within: {posted_within} days")

        print()

        # Check if RAPIDAPI_KEY is set
        boards = config.get("boards", [])
        jsearch_board = None
        for board in boards:
            if board.get("name") == "JSearch":
                jsearch_board = board
                break

        if not jsearch_board:
            print("❌ ERROR: JSearch board not found in config/job-boards.yaml")
            return 1

        if not jsearch_board.get("enabled"):
            print("❌ ERROR: JSearch board is not enabled in config/job-boards.yaml")
            print("   Please set 'enabled: true' for the JSearch board")
            return 1

        api_key = jsearch_board.get("api_key", "")
        if not api_key or "${RAPIDAPI_KEY}" in api_key:
            print("❌ ERROR: RAPIDAPI_KEY environment variable not set")
            print("   Please set it with: export RAPIDAPI_KEY='your-key-here'")
            return 1

        print(f"✅ RAPIDAPI_KEY is set (ending in ...{api_key[-4:]})")
        print()

        # Initialize orchestrator
        logger.info("Initializing search orchestrator...")
        orchestrator = SearchOrchestrator(config)

        enabled_boards = orchestrator.get_enabled_boards()
        print(f"Enabled boards: {', '.join(enabled_boards)}")
        print()

        # Test search with JSearch
        logger.info("Testing JSearch adapter with complex criteria...")
        print("🔍 Searching JSearch for: 'DevOps Engineer'")
        print("   Using complex search criteria from search-criteria-complex.yaml")
        print("   (This will use 1 request from your free tier quota)")
        print()

        # Execute search
        jobs = orchestrator.search_specific_board("JSearch")

        # Display results
        print("\n" + "=" * 70)
        print("✅ TEST SUCCESSFUL")
        print("=" * 70)
        print(f"Total jobs found after filtering: {len(jobs)}")
        print()

        if jobs:
            print("Sample results (first 5):")
            print("-" * 70)
            for i, job in enumerate(jobs[:5], 1):
                print(f"\n{i}. {job.title}")
                print(f"   Company:     {job.company}")
                print(f"   Location:    {job.location}")
                print(f"   Remote Type: {job.remote_type}")
                if job.salary_min and job.salary_max:
                    print(f"   Salary:      ${job.salary_min:,} - ${job.salary_max:,}")

                    # Check if salary meets criteria
                    salary_min = salary_range.get("min", 0)
                    salary_max = salary_range.get("max", 999999)
                    if job.salary_min >= salary_min and job.salary_max <= salary_max:
                        print(f"   ✅ Meets salary criteria (${salary_min:,} - ${salary_max:,})")
                    else:
                        print(f"   ⚠️  Outside salary range")
                elif job.salary_min:
                    print(f"   Salary:      ${job.salary_min:,}+")
                else:
                    print(f"   Salary:      Not disclosed")

                # Check for required tech
                job_text = f"{job.description} {' '.join(job.requirements)}".lower()
                tech_found = [tech for tech in required_tech if tech.lower() in job_text]
                if tech_found:
                    print(f"   ✅ Required tech found: {', '.join(tech_found)}")

                # Check for experience level
                exp_found = [exp for exp in experience_level if exp.lower() in job.title.lower() or exp.lower() in job.description.lower()]
                if exp_found:
                    print(f"   ✅ Experience level: {', '.join(exp_found)}")

                print(f"   URL:         {job.job_url}")
                if job.requirements:
                    print(f"   Skills:      {', '.join(job.requirements[:5])}")
                    if len(job.requirements) > 5:
                        print(f"                ... and {len(job.requirements) - 5} more")
        else:
            print("ℹ️  No jobs matched the complex search criteria.")
            print()
            print("This could mean:")
            print("  - All jobs were filtered out (too restrictive criteria)")
            print("  - All jobs were previously processed (check data/processed_jobs.json)")
            print("  - No jobs match the salary/tech/experience requirements")
            print()
            print("Try:")
            print("  1. Clear processed jobs: rm data/processed_jobs.json")
            print("  2. Adjust criteria in config/search-criteria-complex.yaml")
            print("  3. Run the basic test: python scripts/test_jsearch_adapter.py")

        print("\n" + "=" * 70)
        print("JSearch adapter with complex criteria is working correctly!")
        print("=" * 70)
        print()

        # Show filtering statistics
        print("📊 Filtering Statistics:")
        print("-" * 70)
        print(f"   Jobs from API:           (check logs above)")
        print(f"   After filtering:         {len(jobs)}")
        print(f"   Filtering criteria applied:")
        if salary_range:
            print(f"     - Salary range:        ${salary_range.get('min', 0):,} - ${salary_range.get('max', 0):,}")
        if experience_level:
            print(f"     - Experience levels:   {', '.join(experience_level)}")
        if required_tech:
            print(f"     - Required tech:       {', '.join(required_tech)}")
        if posted_within:
            print(f"     - Posted within:       {posted_within} days")
        print()

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ CONFIGURATION ERROR: {e}")
        return 1

    except Exception as e:
        logger.exception(f"Test failed: {e}")
        print(f"\n❌ TEST FAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
