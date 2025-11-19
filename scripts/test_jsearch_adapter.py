#!/usr/bin/env python3
"""
Test script for JSearch adapter - Phase 1 validation

This script tests the JSearch adapter implementation with a minimal search
to verify the integration is working correctly.

Usage:
    # Set your RapidAPI key first:
    export RAPIDAPI_KEY="your-rapidapi-key-here"

    # Run the test:
    python scripts/test_jsearch_adapter.py

Requirements:
    - RapidAPI account with JSearch API subscription
    - RAPIDAPI_KEY environment variable set
    - Free tier provides 50 requests over 7 days for testing
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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
    """Test JSearch adapter with minimal search."""
    print("\n" + "=" * 60)
    print("JSearch Adapter Test - Phase 1 Validation")
    print("=" * 60)
    print()

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()

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
        logger.info("Testing JSearch adapter with sample search...")
        print("🔍 Searching JSearch for: 'DevOps Engineer'")
        print("   (This will use 1 request from your free tier quota)")
        print()

        # Execute search
        jobs = orchestrator.search_specific_board("JSearch")

        # Display results
        print("\n" + "=" * 60)
        print("✅ TEST SUCCESSFUL")
        print("=" * 60)
        print(f"Total jobs found: {len(jobs)}")
        print()

        if jobs:
            print("Sample results (first 3):")
            print("-" * 60)
            for i, job in enumerate(jobs[:3], 1):
                print(f"\n{i}. {job.title}")
                print(f"   Company:     {job.company}")
                print(f"   Location:    {job.location}")
                print(f"   Remote Type: {job.remote_type}")
                if job.salary_min and job.salary_max:
                    print(f"   Salary:      ${job.salary_min:,} - ${job.salary_max:,}")
                elif job.salary_min:
                    print(f"   Salary:      ${job.salary_min:,}+")
                else:
                    print(f"   Salary:      Not disclosed")
                print(f"   URL:         {job.job_url}")
                if job.requirements:
                    print(f"   Skills:      {', '.join(job.requirements[:5])}")
                    if len(job.requirements) > 5:
                        print(f"                ... and {len(job.requirements) - 5} more")

        print("\n" + "=" * 60)
        print("JSearch adapter is working correctly!")
        print("Phase 1 implementation validated successfully.")
        print("=" * 60)
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
