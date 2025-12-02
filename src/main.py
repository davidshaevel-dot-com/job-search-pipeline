#!/usr/bin/env python3
"""
Job Search Pipeline - Main Entry Point

Executes the job search pipeline by:
1. Loading configuration
2. Searching job boards via orchestrator
3. Optionally evaluating jobs with AI (Phase 3)
4. Writing results to files
5. Logging summary

Usage:
    # Search all enabled boards (no evaluation)
    python src/main.py

    # Search with AI evaluation
    python src/main.py --evaluate

    # Limit number of jobs to evaluate (for cost control)
    python src/main.py --evaluate --limit 5

    # Search specific board
    python src/main.py --board JSearch

    # Search specific board with evaluation
    python src/main.py --board JSearch --evaluate

    # Debug mode with verbose logging
    python src/main.py --debug
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

def _validate_project_structure():
    """
    Validate we're running from correct project location.

    Ensures expected files exist before attempting to run the pipeline.
    This helps catch errors early if the script is run from the wrong directory.

    Exits with error code 1 if validation fails.
    """
    src_dir = Path(__file__).parent
    project_root = src_dir.parent

    expected_files = [
        project_root / "config" / "job-boards.yaml",
        project_root / "config" / "search-criteria.yaml",
    ]

    for expected_file in expected_files:
        if not expected_file.exists():
            print(f"ERROR: Project structure validation failed", file=sys.stderr)
            print(f"Expected file not found: {expected_file}", file=sys.stderr)
            print(f"", file=sys.stderr)
            print(f"Make sure you're running from the project root:", file=sys.stderr)
            print(f"  cd /path/to/job-search-pipeline", file=sys.stderr)
            print(f"  python src/main.py", file=sys.stderr)
            sys.exit(1)

# Validate project structure before modifying sys.path
_validate_project_structure()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from config.loader import load_config
from organization.file_writer import FileWriter
from organization.evaluation_writer import EvaluationWriter
from search.orchestrator import SearchOrchestrator


def setup_logging(debug: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        debug: Enable debug-level logging if True
    """
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_banner(args: argparse.Namespace) -> None:
    """
    Print application banner with configuration details.

    Args:
        args: Parsed command-line arguments
    """
    print("\n" + "=" * 60)
    if args.evaluate:
        print("Job Search Pipeline - Phase 3 (Search + AI Evaluation)")
    else:
        print("Job Search Pipeline - Phase 1 (Search Only)")
    print("=" * 60)
    print(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.board:
        print(f"Board:     {args.board} (specific board search)")
    else:
        print("Board:     All enabled boards")
    if args.evaluate:
        print(f"Evaluate:  Yes (AI-powered job scoring)")
        if args.limit:
            print(f"Limit:     {args.limit} jobs max")
    if args.debug:
        print("Log Level: DEBUG")
    print("=" * 60)
    print()


def main() -> int:
    """
    Main entry point for job search pipeline.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Job Search Pipeline - Automated job board search and organization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Search all enabled boards (no evaluation)
  %(prog)s --evaluate               Search with AI evaluation
  %(prog)s --evaluate --limit 5     Evaluate max 5 jobs (cost control)
  %(prog)s --board JSearch          Search specific board only
  %(prog)s --debug                  Enable debug logging
        """
    )
    parser.add_argument(
        "--board",
        type=str,
        help="Specific board to search (searches all enabled boards if not specified)",
    )
    parser.add_argument(
        "--config-dir",
        type=str,
        help="Configuration directory path (default: config/)",
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Enable AI-powered job evaluation using Claude API",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of jobs to evaluate (for cost control)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug-level logging",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    # Print banner
    print_banner(args)

    try:
        # Load configuration
        logger.info("Loading configuration...")
        if args.config_dir:
            config_dir = Path(args.config_dir)
            config = load_config(config_dir=config_dir)
        else:
            config = load_config()

        logger.info("Configuration loaded successfully")

        # Initialize search orchestrator
        logger.info("Initializing search orchestrator...")
        orchestrator = SearchOrchestrator(config)

        # Display enabled boards
        enabled_boards = orchestrator.get_enabled_boards()
        if not enabled_boards:
            logger.error("No job boards are enabled in configuration")
            print("\n❌ ERROR: No job boards enabled")
            print("   Please enable at least one board in config/job-boards.yaml")
            return 1

        logger.info(f"Enabled boards: {', '.join(enabled_boards)}")
        print(f"Enabled boards: {', '.join(enabled_boards)}\n")

        # Execute search (with or without evaluation)
        if args.evaluate:
            # Phase 3: Search with AI evaluation
            logger.info("Running search with AI evaluation...")
            print("🔍 Searching job boards...")
            print("🤖 AI evaluation enabled\n")

            result = orchestrator.run_search_with_evaluation()
            jobs = result.jobs
            evaluations = result.evaluations or []

            # Apply limit if specified
            if args.limit and len(jobs) > args.limit:
                jobs = jobs[:args.limit]
                evaluations = evaluations[:args.limit] if evaluations else []
                logger.info(f"Limited to {args.limit} jobs")

            # Log evaluation stats
            if result.stats:
                logger.info(f"Search stats: {result.stats}")
                if result.stats.get('grade_distribution'):
                    print(f"Grade distribution: {result.stats['grade_distribution']}")
        else:
            # Phase 1: Search only (no evaluation)
            if args.board:
                logger.info(f"Searching specific board: {args.board}")
                print(f"🔍 Searching {args.board}...\n")
                jobs = orchestrator.search_specific_board(args.board)
            else:
                logger.info("Searching all enabled boards...")
                print("🔍 Searching all enabled boards...\n")
                jobs = orchestrator.run_search()
            evaluations = []

        # Check if any jobs were found
        if not jobs:
            logger.warning("No jobs found")
            print("\n⚠️  No jobs found")
            print("   Try adjusting search criteria in config/search-criteria.yaml")
            return 0

        # Write job files
        logger.info(f"Writing {len(jobs)} jobs to files...")
        print(f"\n📝 Writing {len(jobs)} job files...")

        writer = FileWriter()
        output_files = writer.write_jobs(jobs)

        # Write evaluation files if we have evaluations
        eval_files = []
        summary_path = None
        if evaluations:
            logger.info(f"Writing {len(evaluations)} evaluation files...")
            print(f"📊 Writing {len(evaluations)} evaluation files...")

            eval_writer = EvaluationWriter()
            jobs_and_evals = list(zip(jobs[:len(evaluations)], evaluations))
            eval_files = eval_writer.write_evaluations(jobs_and_evals)
            summary_path = eval_writer.write_summary(jobs_and_evals)

        # Print summary
        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Total jobs found:     {len(jobs)}")
        print(f"Job files created:    {len(output_files)}")
        if evaluations:
            print(f"Jobs evaluated:       {len(evaluations)}")
            print(f"Eval files created:   {len(eval_files)}")
            if summary_path:
                print(f"Summary file:         {summary_path.name}")
        print(f"Output directory:     {writer.base_path}")
        print("=" * 60)

        # Print top evaluated jobs if we have evaluations
        if evaluations:
            print("\n📈 Top Evaluated Jobs:")
            # Sort by score descending
            sorted_evals = sorted(
                zip(jobs[:len(evaluations)], evaluations),
                key=lambda x: x[1].overall_score,
                reverse=True
            )
            for i, (job, eval_result) in enumerate(sorted_evals[:5], 1):
                print(f"   {i}. {job.title} at {job.company}")
                print(f"      Grade: {eval_result.grade.value} ({eval_result.overall_score:.1f})")
                print(f"      Recommendation: {eval_result.recommendation.value}")

        # Print output file paths
        if output_files and not evaluations:
            print("\nCreated files:")
            for file_path in output_files[:10]:  # Show first 10
                print(f"  - {file_path}")
            if len(output_files) > 10:
                print(f"  ... and {len(output_files) - 10} more files")

        print()
        logger.info("Pipeline execution completed successfully")
        return 0

    except ValueError as e:
        logger.error(f"Configuration or validation error: {e}")
        print(f"\n❌ ERROR: {e}")
        return 1

    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        print(f"\n❌ ERROR: {e}")
        return 1

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("   See logs for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
