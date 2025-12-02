#!/usr/bin/env python3
"""
End-to-End Integration Test for Phase 3 AI Evaluation.

This script tests the complete pipeline:
1. Search jobs via JSearch adapter
2. Filter and deduplicate results
3. Evaluate jobs using AI (Claude API)
4. Write job files and evaluation results
5. Generate evaluation summary

Usage:
    # Run from project root with venv activated
    PYTHONPATH=src python scripts/test_e2e_with_evaluation.py

    # With debug logging
    PYTHONPATH=src python scripts/test_e2e_with_evaluation.py --debug

    # Limit number of jobs to evaluate (for cost savings)
    PYTHONPATH=src python scripts/test_e2e_with_evaluation.py --limit 3

Requirements:
    - ANTHROPIC_API_KEY environment variable set
    - RAPIDAPI_KEY environment variable set (for JSearch)
    - Config files in config/ directory
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from config.loader import load_config
from organization import FileWriter, EvaluationWriter
from search import SearchOrchestrator


def setup_logging(debug: bool = False) -> None:
    """Configure logging."""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=log_level, format=log_format)


def validate_api_keys() -> bool:
    """Check that required API keys are set."""
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    rapidapi_key = os.environ.get("RAPIDAPI_KEY")

    missing = []
    if not anthropic_key:
        missing.append("ANTHROPIC_API_KEY")
    if not rapidapi_key:
        missing.append("RAPIDAPI_KEY")

    if missing:
        print(f"❌ Missing required API keys: {', '.join(missing)}")
        print("   Set these environment variables or add them to .env file")
        return False

    print("✅ API keys validated")
    return True


def main() -> int:
    """Run end-to-end test."""
    parser = argparse.ArgumentParser(description="E2E test for Phase 3 AI Evaluation")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--limit", type=int, default=5,
                        help="Max jobs to evaluate (default: 5)")
    args = parser.parse_args()

    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    # Banner
    print("\n" + "=" * 70)
    print("Phase 3 End-to-End Integration Test")
    print("Search → Filter → Evaluate → Write")
    print("=" * 70)
    print(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Job Limit: {args.limit}")
    print("=" * 70 + "\n")

    # Validate API keys
    if not validate_api_keys():
        return 1

    try:
        # Step 1: Load configuration
        print("\n📋 Step 1: Loading configuration...")
        config = load_config()
        print(f"   Config loaded successfully")

        # Step 2: Initialize orchestrator and search
        print("\n🔍 Step 2: Searching for jobs...")
        orchestrator = SearchOrchestrator(config)

        enabled_boards = orchestrator.get_enabled_boards()
        print(f"   Enabled boards: {', '.join(enabled_boards)}")

        # Run search with evaluation
        print("\n🤖 Step 3: Running search with AI evaluation...")
        result = orchestrator.run_search_with_evaluation()

        print(f"   Jobs found: {result.stats.get('jobs_found', 0)}")
        print(f"   Jobs evaluated: {result.stats.get('jobs_evaluated', 0)}")
        print(f"   Evaluation errors: {result.stats.get('evaluation_errors', 0)}")

        if result.stats.get('grade_distribution'):
            print(f"   Grade distribution: {result.stats['grade_distribution']}")

        if not result.jobs:
            print("\n⚠️  No jobs found. Try adjusting search criteria.")
            return 0

        # Limit jobs for evaluation if specified
        jobs_to_write = result.jobs[:args.limit]
        evaluations_to_write = result.evaluations[:args.limit] if result.evaluations else []

        # Step 4: Write job files
        print(f"\n📝 Step 4: Writing {len(jobs_to_write)} job files...")
        file_writer = FileWriter()
        job_files = file_writer.write_jobs(jobs_to_write)
        print(f"   Created {len(job_files)} job files")

        # Step 5: Write evaluation files
        if evaluations_to_write:
            print(f"\n📊 Step 5: Writing {len(evaluations_to_write)} evaluation files...")
            eval_writer = EvaluationWriter()

            # Pair jobs with their evaluations
            jobs_and_evals = list(zip(jobs_to_write, evaluations_to_write))

            # Write individual evaluation files
            eval_files = eval_writer.write_evaluations(jobs_and_evals)
            print(f"   Created {len(eval_files)} evaluation files")

            # Write summary
            summary_path = eval_writer.write_summary(jobs_and_evals)
            print(f"   Created summary: {summary_path}")
        else:
            print("\n⚠️  No evaluations to write (all failed or skipped)")

        # Summary
        print("\n" + "=" * 70)
        print("✅ END-TO-END TEST COMPLETE")
        print("=" * 70)
        print(f"Jobs found:        {len(result.jobs)}")
        print(f"Jobs evaluated:    {len(result.evaluations) if result.evaluations else 0}")
        print(f"Jobs written:      {len(jobs_to_write)}")
        print(f"Output directory:  {file_writer.base_path}")

        if result.evaluations:
            # Show top jobs
            print("\n📈 Top Evaluated Jobs:")
            sorted_evals = sorted(
                zip(jobs_to_write, evaluations_to_write),
                key=lambda x: x[1].overall_score,
                reverse=True
            )
            for i, (job, eval_result) in enumerate(sorted_evals[:5], 1):
                print(f"   {i}. {job.title} at {job.company}")
                print(f"      Grade: {eval_result.grade.value} ({eval_result.overall_score:.1f})")
                print(f"      Recommendation: {eval_result.recommendation.value}")

        print("\n" + "=" * 70)

        # Show any evaluation errors
        if result.evaluation_errors:
            print("\n⚠️  Evaluation Errors:")
            for error in result.evaluation_errors:
                print(f"   - {error}")

        return 0

    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"\n❌ ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
