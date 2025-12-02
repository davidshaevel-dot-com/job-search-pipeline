"""
Evaluation data models for job search pipeline.

Defines the data structures for storing AI-powered job evaluations
using the 8-factor weighted rubric.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class Grade(Enum):
    """Letter grade for job evaluation."""
    A = "A"  # 90-100: Exceptional opportunity - Strongly pursue
    B = "B"  # 80-89: Strong opportunity - Definitely pursue
    C = "C"  # 70-79: Acceptable opportunity - Consider carefully
    D = "D"  # 60-69: Questionable opportunity - Significant concerns
    F = "F"  # 0-59: Poor opportunity - Do not pursue

    @classmethod
    def from_score(cls, score: float) -> "Grade":
        """
        Determine grade from numerical score.

        Args:
            score: Overall weighted score (0-100)

        Returns:
            Corresponding Grade enum value
        """
        if score >= 90:
            return cls.A
        elif score >= 80:
            return cls.B
        elif score >= 70:
            return cls.C
        elif score >= 60:
            return cls.D
        else:
            return cls.F


class Recommendation(Enum):
    """Recommendation for how to proceed with opportunity."""
    STRONGLY_PURSUE = "strongly_pursue"  # Grade A
    PURSUE = "pursue"                     # Grade B
    CONSIDER = "consider"                 # Grade C
    SKIP = "skip"                         # Grade D or F

    @classmethod
    def from_grade(cls, grade: Grade) -> "Recommendation":
        """
        Determine recommendation from grade.

        Args:
            grade: Letter grade

        Returns:
            Corresponding Recommendation enum value
        """
        mapping = {
            Grade.A: cls.STRONGLY_PURSUE,
            Grade.B: cls.PURSUE,
            Grade.C: cls.CONSIDER,
            Grade.D: cls.SKIP,
            Grade.F: cls.SKIP,
        }
        return mapping[grade]


# Module-level cache for EvaluationFactor key lookups (populated on first access)
_EVALUATION_FACTOR_KEY_MAP: Optional[Dict[str, "EvaluationFactor"]] = None


class EvaluationFactor(Enum):
    """
    The 8 evaluation factors with their weights.

    Each factor has a weight that sums to 1.0 (100%).
    """
    SKILLS_MATCH = ("skills_match", 0.25, "Skills & Experience Match")
    COMPENSATION = ("compensation", 0.20, "Compensation & Benefits")
    STABILITY = ("stability", 0.15, "Company Stability & Growth")
    WORK_LIFE_BALANCE = ("work_life_balance", 0.15, "Work-Life Balance")
    CAREER_GROWTH = ("career_growth", 0.10, "Career Growth & Learning")
    CULTURE_FIT = ("culture_fit", 0.08, "Culture & Team Fit")
    ROLE_CLARITY = ("role_clarity", 0.05, "Role Clarity & Expectations")
    LOCATION = ("location", 0.02, "Location & Commute")

    def __init__(self, key: str, weight: float, display_name: str):
        self.key = key
        self.weight = weight
        self.display_name = display_name

    @classmethod
    def _get_key_map(cls) -> Dict[str, "EvaluationFactor"]:
        """Get or build the cached key -> factor lookup map."""
        global _EVALUATION_FACTOR_KEY_MAP
        if _EVALUATION_FACTOR_KEY_MAP is None:
            _EVALUATION_FACTOR_KEY_MAP = {factor.key: factor for factor in cls}
        return _EVALUATION_FACTOR_KEY_MAP

    @classmethod
    def get_all_keys(cls) -> List[str]:
        """Get list of all factor keys."""
        return list(cls._get_key_map().keys())

    @classmethod
    def get_by_key(cls, key: str) -> "EvaluationFactor":
        """
        Get factor by key with O(1) lookup.

        Args:
            key: Factor key (e.g., "skills_match")

        Returns:
            Corresponding EvaluationFactor enum value

        Raises:
            ValueError: If key is not found
        """
        key_map = cls._get_key_map()
        if key not in key_map:
            raise ValueError(f"Unknown factor key: {key}")
        return key_map[key]

    @classmethod
    def get_weight(cls, key: str) -> float:
        """Get weight for a factor by key with O(1) lookup."""
        return cls.get_by_key(key).weight


@dataclass
class FactorScore:
    """
    Score for a single evaluation factor.

    Attributes:
        factor: The evaluation factor being scored
        score: Numerical score (0-100)
        reasoning: Brief explanation for the score
    """
    factor: str  # Factor key (e.g., "skills_match")
    score: int   # 0-100
    reasoning: str

    @property
    def weight(self) -> float:
        """Get the weight for this factor."""
        return EvaluationFactor.get_weight(self.factor)

    @property
    def weighted_score(self) -> float:
        """Calculate weighted contribution to overall score."""
        return self.score * self.weight

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "factor": self.factor,
            "score": self.score,
            "weight": self.weight,
            "reasoning": self.reasoning,
            "weighted_score": round(self.weighted_score, 2),
        }


@dataclass
class EvaluationResult:
    """
    Complete evaluation result for a job posting.

    Stores all 8 factor scores, overall score, grade, and recommendation.

    Attributes:
        job_id: Unique identifier for the job (board_job_id or generated)
        job_title: Title of the job posting
        company: Company name
        evaluation_timestamp: When the evaluation was performed
        model: Claude model used for evaluation
        factor_scores: Dictionary of factor key -> FactorScore
        overall_score: Weighted average of all factor scores (0-100)
        grade: Letter grade (A/B/C/D/F)
        recommendation: Action recommendation
        confidence: AI's confidence in the evaluation (0.0-1.0)
        summary: Brief summary of the evaluation
        strengths: Key strengths identified
        concerns: Key concerns identified
        raw_response: Raw API response for debugging (optional)
    """
    job_id: str
    job_title: str
    company: str
    evaluation_timestamp: datetime
    model: str
    factor_scores: Dict[str, FactorScore]
    overall_score: float
    grade: Grade
    recommendation: Recommendation
    confidence: float
    summary: str
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    raw_response: Optional[str] = None

    def __post_init__(self):
        """Validate the evaluation result after initialization."""
        # Ensure all required factors are present
        required_factors = set(EvaluationFactor.get_all_keys())
        provided_factors = set(self.factor_scores.keys())

        missing = required_factors - provided_factors
        if missing:
            raise ValueError(f"Missing required factors: {missing}")

        extra = provided_factors - required_factors
        if extra:
            raise ValueError(f"Unknown factors provided: {extra}")

        # Validate score ranges
        if not 0 <= self.overall_score <= 100:
            raise ValueError(f"Overall score must be 0-100, got {self.overall_score}")

        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")

        for factor_key, factor_score in self.factor_scores.items():
            if not 0 <= factor_score.score <= 100:
                raise ValueError(
                    f"Factor '{factor_key}' score must be 0-100, "
                    f"got {factor_score.score}"
                )

    @classmethod
    def calculate_overall_score(cls, factor_scores: Dict[str, FactorScore]) -> float:
        """
        Calculate weighted overall score from factor scores.

        Args:
            factor_scores: Dictionary of factor key -> FactorScore

        Returns:
            Weighted average score (0-100)
        """
        total = sum(fs.weighted_score for fs in factor_scores.values())
        return round(total, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "job_id": self.job_id,
            "job_title": self.job_title,
            "company": self.company,
            "evaluation_timestamp": self.evaluation_timestamp.isoformat(),
            "model": self.model,
            "factor_scores": {
                key: score.to_dict()
                for key, score in self.factor_scores.items()
            },
            "overall_score": self.overall_score,
            "grade": self.grade.value,
            "recommendation": self.recommendation.value,
            "confidence": self.confidence,
            "summary": self.summary,
            "strengths": self.strengths,
            "concerns": self.concerns,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationResult":
        """
        Create EvaluationResult from dictionary.

        Args:
            data: Dictionary representation of evaluation result

        Returns:
            EvaluationResult instance
        """
        # Parse factor scores
        factor_scores = {}
        for key, score_data in data["factor_scores"].items():
            factor_scores[key] = FactorScore(
                factor=score_data["factor"],
                score=score_data["score"],
                reasoning=score_data["reasoning"],
            )

        return cls(
            job_id=data["job_id"],
            job_title=data["job_title"],
            company=data["company"],
            evaluation_timestamp=datetime.fromisoformat(data["evaluation_timestamp"]),
            model=data["model"],
            factor_scores=factor_scores,
            overall_score=data["overall_score"],
            grade=Grade(data["grade"]),
            recommendation=Recommendation(data["recommendation"]),
            confidence=data["confidence"],
            summary=data["summary"],
            strengths=data.get("strengths", []),
            concerns=data.get("concerns", []),
            raw_response=data.get("raw_response"),
        )

    def get_factor_score(self, factor_key: str) -> FactorScore:
        """Get score for a specific factor."""
        if factor_key not in self.factor_scores:
            raise ValueError(f"Factor not found: {factor_key}")
        return self.factor_scores[factor_key]

    def meets_threshold(self, threshold: float = 70.0) -> bool:
        """Check if evaluation meets minimum threshold."""
        return self.overall_score >= threshold

    def should_auto_pursue(self, threshold: float = 85.0) -> bool:
        """Check if evaluation meets auto-pursue threshold (B+ or higher)."""
        return self.overall_score >= threshold

    def format_summary(self) -> str:
        """Format a human-readable summary of the evaluation."""
        lines = [
            f"Evaluation: {self.job_title} at {self.company}",
            f"Overall Score: {self.overall_score:.1f}/100 ({self.grade.value})",
            f"Recommendation: {self.recommendation.value.replace('_', ' ').title()}",
            f"Confidence: {self.confidence:.0%}",
            "",
            "Factor Scores:",
        ]

        # Sort factors by weight (highest first)
        sorted_factors = sorted(
            self.factor_scores.items(),
            key=lambda x: EvaluationFactor.get_weight(x[0]),
            reverse=True,
        )

        for factor_key, score in sorted_factors:
            factor = EvaluationFactor.get_by_key(factor_key)
            lines.append(
                f"  {factor.display_name}: {score.score}/100 "
                f"(weight: {score.weight:.0%})"
            )

        if self.strengths:
            lines.append("")
            lines.append("Strengths:")
            for strength in self.strengths:
                lines.append(f"  + {strength}")

        if self.concerns:
            lines.append("")
            lines.append("Concerns:")
            for concern in self.concerns:
                lines.append(f"  - {concern}")

        lines.append("")
        lines.append(f"Summary: {self.summary}")

        return "\n".join(lines)
