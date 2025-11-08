#!/usr/bin/env python3
"""
Job Search Pipeline - Main Entry Point

Usage:
    python src/main.py
    python src/main.py --board linkedin
    python src/main.py --config config/custom-criteria.yaml
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# TODO: Import modules when implemented
# from search.orchestrator import SearchOrchestrator
# from config.loader import load_config


def main():
    """Main entry point for job search pipeline."""
    parser = argparse.ArgumentParser(description="Job Search Pipeline")
    parser.add_argument(
        "--board",
        type=str,
        help="Specific board to search (optional, searches all if not specified)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/search-criteria.yaml",
        help="Configuration file path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (don't create files or Linear issues)",
    )
    
    args = parser.parse_args()
    
    print("Job Search Pipeline")
    print("=" * 50)
    print(f"Config: {args.config}")
    if args.board:
        print(f"Board: {args.board}")
    if args.dry_run:
        print("Mode: DRY RUN")
    print("=" * 50)
    
    # TODO: Implement pipeline execution
    # config = load_config(args.config)
    # orchestrator = SearchOrchestrator(config)
    # if args.board:
    #     results = orchestrator.search_board(args.board)
    # else:
    #     results = orchestrator.search_all_boards()
    
    print("\nPipeline execution not yet implemented.")
    print("See PLAN.md for implementation phases.")


if __name__ == "__main__":
    main()

