"""
Prompt builder for AI job evaluation.

Constructs structured prompts for Claude API to evaluate job postings
using the 8-factor weighted rubric.
"""

import copy
from typing import Any, Dict, Optional

from core.models import JobPosting
from .models import EvaluationFactor


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with override values taking precedence.

    Args:
        base: Base dictionary with default values
        override: Dictionary with values to override

    Returns:
        New dictionary with merged values
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class PromptBuilder:
    """Builds prompts for AI-powered job evaluation."""

    # Default user profile for evaluation context
    DEFAULT_USER_PROFILE = {
        "target_role": "Senior DevOps Engineer / Platform Engineer",
        "experience_years": 15,
        "key_skills": [
            "AWS", "Terraform", "Kubernetes", "Docker",
            "CI/CD", "Python", "Infrastructure as Code",
            "Monitoring", "Prometheus", "Grafana"
        ],
        "salary_target": {
            "min": 150000,
            "max": 180000,
            "currency": "USD"
        },
        "location_preference": {
            "preferred": ["Austin, TX", "Remote"],
            "acceptable": ["Texas", "Hybrid"],
            "willing_to_relocate": False
        },
        "work_style_preference": {
            "remote_preference": "remote_preferred",  # remote_only, remote_preferred, hybrid_ok, onsite_ok
            "max_office_days_per_week": 3
        },
        "company_preferences": {
            "preferred_stages": ["Series A+", "Profitable", "Established"],
            "avoid_stages": ["Pre-seed", "Idea stage"],
            "preferred_sizes": ["50-500", "500+"],
            "industries_of_interest": ["Tech", "Fintech", "Climate Tech", "SaaS"]
        },
        "priorities": [
            "Technical challenge and growth",
            "Compensation and equity",
            "Work-life balance",
            "Remote flexibility",
            "Company stability"
        ]
    }

    SYSTEM_PROMPT = """You are an expert job opportunity evaluator. Your task is to evaluate job postings against a candidate's profile using an 8-factor weighted rubric.

## Evaluation Rubric

You must score each of these 8 factors on a scale of 0-100:

1. **Skills & Experience Match (25% weight)**
   - How well do the candidate's skills align with role requirements?
   - Is the experience level appropriate?
   - Domain knowledge relevance
   - Can they hit the ground running vs. steep learning curve?

2. **Compensation & Benefits (20% weight)**
   - Base salary competitiveness for market and experience
   - Equity/stock options value and vesting
   - Health insurance, 401k, and benefits quality
   - Total compensation vs. market rate

3. **Company Stability & Growth (15% weight)**
   - Funding status and runway
   - Revenue/business model viability
   - Market opportunity and competition
   - Leadership team track record

4. **Work-Life Balance (15% weight)**
   - Expected working hours and on-call requirements
   - Remote work flexibility
   - PTO policy and actual usage culture
   - Meeting load and work intensity

5. **Career Growth & Learning (10% weight)**
   - Opportunities to learn new technologies
   - Path for advancement
   - Mentorship and professional development
   - Scope of impact and visibility

6. **Culture & Team Fit (8% weight)**
   - Team collaboration style
   - Diversity and inclusion
   - Mission alignment with values
   - Employee satisfaction indicators

7. **Role Clarity & Expectations (5% weight)**
   - Clear definition of responsibilities
   - Realistic expectations
   - Well-defined success metrics
   - Organizational structure clarity

8. **Location & Commute (2% weight)**
   - Remote work options match preferences
   - Office location if applicable
   - Travel requirements
   - Commute feasibility

## Scoring Guidelines

- **90-100 (A)**: Excellent - Exceeds expectations, strong positive factor
- **80-89 (B)**: Good - Meets expectations well, positive factor
- **70-79 (C)**: Acceptable - Meets minimum expectations, neutral factor
- **60-69 (D)**: Below Average - Concerning, negative factor
- **0-59 (F)**: Poor - Major red flag, significant negative factor

## Output Format

You MUST respond with valid JSON in exactly this format:
```json
{
  "scores": {
    "skills_match": {"score": <0-100>, "reasoning": "<brief explanation>"},
    "compensation": {"score": <0-100>, "reasoning": "<brief explanation>"},
    "stability": {"score": <0-100>, "reasoning": "<brief explanation>"},
    "work_life_balance": {"score": <0-100>, "reasoning": "<brief explanation>"},
    "career_growth": {"score": <0-100>, "reasoning": "<brief explanation>"},
    "culture_fit": {"score": <0-100>, "reasoning": "<brief explanation>"},
    "role_clarity": {"score": <0-100>, "reasoning": "<brief explanation>"},
    "location": {"score": <0-100>, "reasoning": "<brief explanation>"}
  },
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "concerns": ["<concern 1>", "<concern 2>"],
  "confidence": <0.0-1.0>
}
```

## Important Notes

- If information is missing for a factor, make reasonable inferences based on available data and note this in the reasoning
- Lower confidence score if significant information is missing
- Be objective and consistent in scoring
- Reasoning should be concise (1-2 sentences max)
- Confidence reflects how complete the job posting information is (1.0 = complete info, 0.5 = significant gaps)
"""

    USER_PROMPT_TEMPLATE = """Please evaluate this job opportunity for the candidate.

## Candidate Profile

**Target Role:** {target_role}
**Experience:** {experience_years} years
**Key Skills:** {key_skills}
**Salary Target:** {salary_min:,} - {salary_max:,} {currency}
**Location Preference:** {location_preference}
**Remote Preference:** {remote_preference}
**Company Preferences:** {company_preferences}
**Priorities:** {priorities}

## Job Posting

**Title:** {job_title}
**Company:** {company}
**Location:** {location}
**Remote Type:** {remote_type}
**Salary Range:** {salary_range}
**Posted Date:** {posted_date}

**Description:**
{description}

**Requirements:**
{requirements}

**Job URL:** {job_url}

---

Please provide your evaluation in the specified JSON format.
"""

    def __init__(self, user_profile: Optional[Dict[str, Any]] = None):
        """
        Initialize prompt builder.

        Args:
            user_profile: Custom user profile dict. If provided, it is deep-merged
                         with DEFAULT_USER_PROFILE so partial profiles work correctly.
                         If None, uses DEFAULT_USER_PROFILE directly.
        """
        if user_profile is None:
            self.user_profile = self.DEFAULT_USER_PROFILE
        else:
            # Deep merge to ensure all nested defaults are present
            self.user_profile = _deep_merge(self.DEFAULT_USER_PROFILE, user_profile)

    def get_system_prompt(self) -> str:
        """Get the system prompt for job evaluation."""
        return self.SYSTEM_PROMPT

    def build_user_prompt(self, job: JobPosting) -> str:
        """
        Build user prompt for evaluating a specific job.

        Args:
            job: JobPosting to evaluate

        Returns:
            Formatted user prompt string
        """
        # Format salary range
        if job.salary_min and job.salary_max:
            salary_range = f"${job.salary_min:,} - ${job.salary_max:,}"
        elif job.salary_min:
            salary_range = f"${job.salary_min:,}+"
        elif job.salary_max:
            salary_range = f"Up to ${job.salary_max:,}"
        else:
            salary_range = "Not specified"

        # Format requirements list
        if job.requirements:
            requirements = "\n".join(f"- {req}" for req in job.requirements)
        else:
            requirements = "Not specified"

        # Format posted date
        if job.posted_date:
            posted_date = job.posted_date.strftime("%Y-%m-%d")
        else:
            posted_date = "Not specified"

        # Format user profile fields
        # Profile is guaranteed to have all fields via deep merge with defaults
        profile = self.user_profile
        salary_target = profile["salary_target"]
        location_pref = profile["location_preference"]
        work_style = profile["work_style_preference"]
        company_pref = profile["company_preferences"]

        return self.USER_PROMPT_TEMPLATE.format(
            # Candidate profile - all fields guaranteed present via deep merge
            target_role=profile["target_role"],
            experience_years=profile["experience_years"],
            key_skills=", ".join(profile["key_skills"]),
            salary_min=salary_target["min"],
            salary_max=salary_target["max"],
            currency=salary_target["currency"],
            location_preference=", ".join(location_pref["preferred"]),
            remote_preference=work_style["remote_preference"],
            company_preferences=", ".join(company_pref["preferred_stages"]),
            priorities=", ".join(profile["priorities"]),
            # Job details
            job_title=job.title,
            company=job.company,
            location=job.location,
            remote_type=job.remote_type,
            salary_range=salary_range,
            posted_date=posted_date,
            description=job.description[:4000] if job.description else "Not provided",
            requirements=requirements,
            job_url=job.job_url,
        )

    def get_expected_output_schema(self) -> Dict[str, Any]:
        """
        Get the expected JSON output schema for validation.

        Returns:
            Dictionary representing the expected schema structure
        """
        return {
            "scores": {
                factor.key: {
                    "score": "integer (0-100)",
                    "reasoning": "string"
                }
                for factor in EvaluationFactor
            },
            "summary": "string (2-3 sentences)",
            "strengths": ["string", "..."],
            "concerns": ["string", "..."],
            "confidence": "float (0.0-1.0)"
        }

    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate that response matches expected schema.

        Args:
            response: Parsed JSON response from Claude

        Returns:
            True if valid, False otherwise
        """
        # Check required top-level keys
        required_keys = {"scores", "summary", "strengths", "concerns", "confidence"}
        if not required_keys.issubset(response.keys()):
            return False

        # Check all factors are present
        required_factors = set(EvaluationFactor.get_all_keys())
        if not required_factors.issubset(response.get("scores", {}).keys()):
            return False

        # Check each factor has score and reasoning
        for factor_key in required_factors:
            factor_data = response["scores"].get(factor_key, {})
            if "score" not in factor_data or "reasoning" not in factor_data:
                return False
            if not isinstance(factor_data["score"], (int, float)):
                return False
            if not 0 <= factor_data["score"] <= 100:
                return False

        # Check confidence is valid
        confidence = response.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            return False

        return True
