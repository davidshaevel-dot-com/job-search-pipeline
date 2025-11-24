"""
Search Orchestrator - Coordinates searches across multiple job boards.

The orchestrator loads enabled job board adapters from configuration,
executes searches based on criteria, and aggregates results with
comprehensive error handling and logging.
"""

import logging
from typing import Dict, List

from adapters import JSearchAdapter
from config.loader import Config
from core.models import JobPosting
from filters import FilterEngine, JobTracker

logger = logging.getLogger(__name__)


class SearchOrchestrator:
    """Coordinates searches across multiple job board adapters."""

    # Mapping of adapter names to adapter classes
    ADAPTER_REGISTRY = {
        "jsearch": JSearchAdapter,
        # Future adapters will be registered here:
        # "adzuna": AdzunaAdapter,
        # "remoteok": RemoteOKAdapter,
        # "remotive": RemotiveAdapter,
        # "themuse": TheMuseAdapter,
        # "usajobs": USAJobsAdapter,
    }

    def __init__(self, config: Config):
        """
        Initialize search orchestrator with configuration.

        Args:
            config: Configuration object containing job boards and search criteria
        """
        self.config = config
        self.adapters = []
        self._initialize_adapters()

        # Initialize filtering components (Phase 2)
        filters_config = config.get("filters", {})
        search_criteria_config = config.get("search_criteria", {})
        self.filter_engine = FilterEngine(
            filters_config=filters_config,
            search_criteria_config=search_criteria_config
        )
        self.job_tracker = JobTracker(data_dir=config.get("data_dir", "data"))

    def _initialize_adapters(self):
        """
        Initialize enabled job board adapters from configuration.

        Loads each enabled board's configuration and creates the corresponding
        adapter instance. Skips boards that are disabled or have missing adapters.
        """
        boards = self.config.get("boards", [])

        for board_config in boards:
            # Skip disabled boards
            if not board_config.get("enabled", False):
                logger.debug(f"Skipping disabled board: {board_config.get('name')}")
                continue

            # Get adapter class name
            adapter_name = board_config.get("adapter")
            if not adapter_name:
                logger.warning(f"Board '{board_config.get('name')}' has no adapter specified")
                continue

            # Look up adapter class
            adapter_class = self.ADAPTER_REGISTRY.get(adapter_name)
            if not adapter_class:
                logger.warning(
                    f"No adapter implementation found for '{adapter_name}'. "
                    f"Skipping board '{board_config.get('name')}'"
                )
                continue

            # Initialize adapter
            try:
                adapter = adapter_class(board_config)
                self.adapters.append(adapter)
                logger.info(f"Initialized adapter for board: {board_config.get('name')}")
            except Exception as e:
                logger.error(
                    f"Failed to initialize adapter for board '{board_config.get('name')}': {e}"
                )
                continue

        if not self.adapters:
            logger.warning("No adapters initialized. No job boards are enabled.")
        else:
            logger.info(f"Successfully initialized {len(self.adapters)} adapter(s)")

    def _build_search_criteria(self) -> dict:
        """
        Build search criteria dictionary from configuration.

        PHASE 1 NOTE: This method currently builds JSearch-specific parameter names
        (remote_jobs_only, employment_types). This is intentional for Phase 1 with
        a single adapter and follows the YAGNI principle (You Aren't Gonna Need It).

        PHASE 2 REFACTOR PLAN: When adding additional adapters (Adzuna, RemoteOK,
        The Muse, USAJobs), we will:
        1. Define generic criteria interface (keywords, location, remote, type)
        2. Pass generic criteria to all adapters
        3. Each adapter implements translate_criteria() to convert generic → specific
        4. Move parameter translation to BaseAdapter with adapter-specific overrides

        This follows the Rule of Three: don't abstract until you have ≥2 concrete
        implementations to guide the abstraction design. Currently we have 1 adapter
        (JSearch), so premature abstraction would be counterproductive.

        Returns:
            Search criteria dictionary (currently JSearch-specific parameters)
        """
        search_config = self.config.get("search", {})

        criteria = {
            "keywords": search_config.get("keywords", []),
            "location": search_config.get("location", ""),
        }

        # Add optional parameters if present
        # TODO Phase 2: Move these JSearch-specific mappings to adapter translation
        if "remote" in search_config:
            criteria["remote_jobs_only"] = search_config["remote"]  # JSearch-specific

        if "employment_type" in search_config:
            criteria["employment_types"] = search_config["employment_type"]  # JSearch-specific

        logger.debug(f"Built search criteria: {criteria}")
        return criteria

    def _filter_and_track_jobs(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """
        Helper method to apply filtering and track processed jobs.

        Args:
            jobs: List of job postings to filter and track

        Returns:
            List of filtered job postings
        """
        # Filter out previously processed jobs
        unprocessed = self.job_tracker.filter_unprocessed(jobs)
        logger.info(
            f"Filtered out {len(jobs) - len(unprocessed)} "
            f"previously processed job(s)"
        )

        # Apply filters (blacklists, criteria, deduplication)
        filtered = self.filter_engine.filter_jobs(unprocessed)
        logger.info(
            f"Filtered: {len(unprocessed)} → {len(filtered)} jobs after "
            f"blacklist, criteria, and deduplication"
        )

        # Mark filtered jobs as processed
        if filtered:
            self.job_tracker.mark_batch_processed(filtered, action="discovered")
            logger.info(f"Marked {len(filtered)} new job(s) as processed")

        return filtered

    def run_search(self) -> List[JobPosting]:
        """
        Execute search across all enabled job boards.

        Coordinates searches across all initialized adapters, collecting
        results and handling errors gracefully. If one adapter fails,
        continues with remaining adapters.

        Phase 2 additions:
        - Filters results (blacklists, complex criteria, deduplication)
        - Tracks processed jobs to avoid re-processing

        Returns:
            List of JobPosting objects from all successful searches (filtered and deduplicated)

        Raises:
            RuntimeError: If no adapters are available to search
        """
        if not self.adapters:
            raise RuntimeError(
                "No job board adapters available. "
                "Check configuration and ensure at least one board is enabled."
            )

        logger.info(f"Starting search across {len(self.adapters)} job board(s)")

        # Reset filter engine state for new search
        self.filter_engine.reset()

        # Build search criteria from configuration
        criteria = self._build_search_criteria()

        # Execute searches and collect results
        all_results = []
        successful_boards = 0
        failed_boards = 0

        for adapter in self.adapters:
            board_name = adapter.board_name
            logger.info(f"Searching {board_name}...")

            try:
                # Execute search
                results = adapter.search(criteria)

                # Collect results
                all_results.extend(results)
                successful_boards += 1

                logger.info(f"{board_name}: Found {len(results)} job(s)")

            except Exception as e:
                logger.error(f"{board_name}: Search failed - {e}")
                failed_boards += 1
                # Continue with next adapter rather than failing completely
                continue

        # Log initial results count
        logger.info(
            f"Search complete: {len(all_results)} total job(s) from "
            f"{successful_boards} board(s) ({failed_boards} failed)"
        )

        # Phase 2: Apply filtering and deduplication
        logger.info("Applying filters and deduplication...")
        filtered = self._filter_and_track_jobs(all_results)

        return filtered

    def search_specific_board(self, board_name: str) -> List[JobPosting]:
        """
        Execute search on a specific job board only.

        Useful for testing individual boards or selective searching.

        Phase 2 additions:
        - Applies same filtering and deduplication as run_search()

        Args:
            board_name: Name of the job board to search

        Returns:
            List of JobPosting objects from the specified board (filtered and deduplicated)

        Raises:
            ValueError: If board name not found or not enabled
        """
        # Find adapter for specified board
        adapter = None
        for a in self.adapters:
            if a.board_name.lower() == board_name.lower():
                adapter = a
                break

        if not adapter:
            available_boards = [a.board_name for a in self.adapters]
            raise ValueError(
                f"Board '{board_name}' not found or not enabled. "
                f"Available boards: {', '.join(available_boards)}"
            )

        logger.info(f"Searching specific board: {board_name}")

        # Reset filter engine state for new search
        self.filter_engine.reset()

        # Build search criteria
        criteria = self._build_search_criteria()

        # Execute search
        results = adapter.search(criteria)
        logger.info(f"{board_name}: Found {len(results)} job(s)")

        # Phase 2: Apply filtering and deduplication
        logger.info("Applying filters and deduplication...")
        filtered = self._filter_and_track_jobs(results)

        return filtered

    def get_enabled_boards(self) -> List[str]:
        """
        Get list of enabled job board names.

        Returns:
            List of board names that are currently enabled and initialized
        """
        return [adapter.board_name for adapter in self.adapters]

    def get_board_count(self) -> Dict[str, int]:
        """
        Get count of enabled boards by adapter type.

        Returns:
            Dictionary mapping adapter names to count of enabled boards
        """
        counts = {}
        for adapter in self.adapters:
            adapter_type = adapter.__class__.__name__
            counts[adapter_type] = counts.get(adapter_type, 0) + 1
        return counts
