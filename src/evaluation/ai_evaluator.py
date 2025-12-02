"""
AI Evaluator - Claude API integration for job evaluation.

Evaluates job postings using Claude API and the 8-factor weighted rubric.
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import anthropic

# Regex pattern to extract JSON from markdown code blocks
# Matches ```json or ``` followed by content and ending ```
_MARKDOWN_CODE_BLOCK_PATTERN = re.compile(
    r"```(?:json)?\s*([\s\S]*?)\s*```",
    re.MULTILINE
)

# Regex pattern for slugifying strings (removes unsafe characters)
_SLUGIFY_PATTERN = re.compile(r"[^a-z0-9]+")


def _slugify(text: str) -> str:
    """
    Convert text to a safe slug for use as identifiers.

    Converts to lowercase, replaces non-alphanumeric characters with underscores,
    and removes leading/trailing underscores.

    Args:
        text: Input text to slugify

    Returns:
        Safe slug string (e.g., "Acme Corp!!" -> "acme_corp")
    """
    return _SLUGIFY_PATTERN.sub("_", text.lower()).strip("_")

from core.models import JobPosting
from .models import (
    EvaluationFactor,
    EvaluationResult,
    FactorScore,
    Grade,
    Recommendation,
)
from .prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class AIEvaluator:
    """Evaluates job postings using Claude API."""

    # Default model to use
    DEFAULT_MODEL = "claude-sonnet-4-5-20250514"

    # API configuration
    MAX_TOKENS = 2000
    TEMPERATURE = 0  # Deterministic for consistent evaluations

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 2  # Base delay in seconds for exponential backoff

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize AI evaluator.

        Args:
            api_key: Anthropic API key. If not provided, reads from
                     ANTHROPIC_API_KEY environment variable.
            model: Claude model to use. Defaults to claude-sonnet-4-5-20250514.
            user_profile: Custom user profile for evaluation context.

        Raises:
            ValueError: If API key is not provided and not in environment.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not provided. "
                "Set it via parameter or ANTHROPIC_API_KEY environment variable."
            )

        self.model = model or self.DEFAULT_MODEL
        self.prompt_builder = PromptBuilder(user_profile=user_profile)
        self.client = anthropic.Anthropic(api_key=self.api_key)

        logger.info(f"AIEvaluator initialized with model: {self.model}")

    def evaluate_job(self, job: JobPosting) -> EvaluationResult:
        """
        Evaluate a single job posting.

        Args:
            job: JobPosting to evaluate

        Returns:
            EvaluationResult with scores, grade, and recommendation

        Raises:
            RuntimeError: If evaluation fails after all retries
        """
        logger.info(f"Evaluating job: {job.title} at {job.company}")

        # Build prompts
        system_prompt = self.prompt_builder.get_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(job)

        # Call Claude API with retry logic
        response_text = self._call_api_with_retry(system_prompt, user_prompt)

        # Parse and validate response
        evaluation_data = self._parse_response(response_text)

        # Build EvaluationResult
        result = self._build_evaluation_result(job, evaluation_data, response_text)

        logger.info(
            f"Evaluation complete: {result.overall_score:.1f}/100 "
            f"({result.grade.value}) - {result.recommendation.value}"
        )

        return result

    def evaluate_jobs(
        self,
        jobs: List[JobPosting],
        continue_on_error: bool = True,
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple job postings.

        Args:
            jobs: List of JobPostings to evaluate
            continue_on_error: If True, continue with remaining jobs on error.
                              If False, raise on first error.

        Returns:
            List of EvaluationResult objects (may be shorter than input if errors)

        Raises:
            RuntimeError: If continue_on_error is False and any evaluation fails
        """
        results = []
        failed_count = 0

        for i, job in enumerate(jobs, 1):
            logger.info(f"Evaluating job {i}/{len(jobs)}: {job.title}")

            try:
                result = self.evaluate_job(job)
                results.append(result)
            except Exception as e:
                failed_count += 1
                logger.error(
                    f"Failed to evaluate '{job.title}' at '{job.company}': {e}"
                )

                if not continue_on_error:
                    raise RuntimeError(
                        f"Evaluation failed for '{job.title}': {e}"
                    ) from e

        logger.info(
            f"Batch evaluation complete: {len(results)} successful, "
            f"{failed_count} failed"
        )

        return results

    def _call_api_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Call Claude API with exponential backoff retry.

        Args:
            system_prompt: System prompt for Claude
            user_prompt: User prompt with job details

        Returns:
            Response text from Claude

        Raises:
            RuntimeError: If all retries fail
        """
        last_exception = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.debug(f"API call attempt {attempt}/{self.MAX_RETRIES}")

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.MAX_TOKENS,
                    temperature=self.TEMPERATURE,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                )

                # Extract text from response
                if response.content and len(response.content) > 0:
                    return response.content[0].text

                raise ValueError("Empty response from Claude API")

            except anthropic.RateLimitError as e:
                last_exception = e
                delay = self.RETRY_DELAY_BASE ** attempt
                logger.warning(
                    f"Rate limited. Retrying in {delay} seconds... "
                    f"(attempt {attempt}/{self.MAX_RETRIES})"
                )
                time.sleep(delay)

            except anthropic.APIStatusError as e:
                last_exception = e
                if e.status_code >= 500:
                    # Server error, retry
                    delay = self.RETRY_DELAY_BASE ** attempt
                    logger.warning(
                        f"API server error ({e.status_code}). "
                        f"Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                else:
                    # Client error, don't retry
                    raise RuntimeError(f"API client error: {e}") from e

            except anthropic.APIConnectionError as e:
                last_exception = e
                delay = self.RETRY_DELAY_BASE ** attempt
                logger.warning(
                    f"Connection error. Retrying in {delay} seconds... "
                    f"(attempt {attempt}/{self.MAX_RETRIES})"
                )
                time.sleep(delay)

        raise RuntimeError(
            f"API call failed after {self.MAX_RETRIES} attempts: {last_exception}"
        )

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse and validate Claude's JSON response.

        Args:
            response_text: Raw response text from Claude

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If response is not valid JSON or fails validation
        """
        # Try to extract JSON from response
        # Claude may include markdown code blocks anywhere in response
        json_text = response_text.strip()

        # Use regex to extract content from markdown code blocks
        match = _MARKDOWN_CODE_BLOCK_PATTERN.search(json_text)
        if match:
            json_text = match.group(1).strip()
        # If no code block found, try parsing the raw text as JSON

        # Parse JSON
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response: {e}") from e

        # Validate response schema
        if not self.prompt_builder.validate_response(data):
            logger.error("Response failed schema validation")
            logger.debug(f"Response data: {data}")
            raise ValueError("Response does not match expected schema")

        return data

    def _build_evaluation_result(
        self,
        job: JobPosting,
        data: Dict[str, Any],
        raw_response: str,
    ) -> EvaluationResult:
        """
        Build EvaluationResult from parsed API response.

        Args:
            job: Original JobPosting
            data: Parsed response dictionary
            raw_response: Raw API response for debugging

        Returns:
            Complete EvaluationResult
        """
        # Build factor scores
        factor_scores = {}
        for factor in EvaluationFactor:
            score_data = data["scores"][factor.key]
            factor_scores[factor.key] = FactorScore(
                factor=factor.key,
                score=int(round(float(score_data["score"]))),
                reasoning=score_data["reasoning"],
            )

        # Calculate overall score
        overall_score = EvaluationResult.calculate_overall_score(factor_scores)

        # Determine grade and recommendation
        grade = Grade.from_score(overall_score)
        recommendation = Recommendation.from_grade(grade)

        # Generate job_id from board_job_id or create a safe slug
        job_id = job.board_job_id or _slugify(f"{job.company}_{job.title}")

        return EvaluationResult(
            job_id=job_id,
            job_title=job.title,
            company=job.company,
            evaluation_timestamp=datetime.now(),
            model=self.model,
            factor_scores=factor_scores,
            overall_score=overall_score,
            grade=grade,
            recommendation=recommendation,
            confidence=float(data["confidence"]),
            summary=data["summary"],
            strengths=data.get("strengths", []),
            concerns=data.get("concerns", []),
            raw_response=raw_response,
        )

    def estimate_cost(self, jobs: List[JobPosting]) -> Dict[str, Any]:
        """
        Estimate API cost for evaluating jobs.

        Args:
            jobs: List of jobs to evaluate

        Returns:
            Dictionary with cost estimates
        """
        # Rough token estimates based on typical job descriptions
        AVG_INPUT_TOKENS = 2000  # System prompt + user prompt + job description
        AVG_OUTPUT_TOKENS = 800  # JSON response

        # Sonnet 4.5 pricing (as of late 2024)
        # $3 per million input tokens, $15 per million output tokens
        INPUT_COST_PER_M = 3.0
        OUTPUT_COST_PER_M = 15.0

        total_input_tokens = AVG_INPUT_TOKENS * len(jobs)
        total_output_tokens = AVG_OUTPUT_TOKENS * len(jobs)

        input_cost = (total_input_tokens / 1_000_000) * INPUT_COST_PER_M
        output_cost = (total_output_tokens / 1_000_000) * OUTPUT_COST_PER_M
        total_cost = input_cost + output_cost

        return {
            "job_count": len(jobs),
            "estimated_input_tokens": total_input_tokens,
            "estimated_output_tokens": total_output_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "cost_per_job_usd": round(total_cost / len(jobs), 4) if jobs else 0,
            "model": self.model,
            "note": "Estimates based on average token usage. Actual cost may vary.",
        }
