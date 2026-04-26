"""
Scoring Utilities - Helper functions for candidate scoring.

Provides deterministic scoring helpers:
- Weight validation
- Score normalization
- Score explanation generation
- Debug/trace utilities
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


# =============================================================================
# Score Constants
# =============================================================================

MIN_SCORE = 0.0
MAX_SCORE = 100.0
PASS_THRESHOLD = 60.0
GOOD_THRESHOLD = 80.0


# =============================================================================
# Weight Validation
# =============================================================================

def validate_weights(weights: Dict[str, float]) -> Tuple[bool, str]:
    """
    Validate that weights are properly configured.
    
    Args:
        weights: Dictionary of dimension weights
        
    Returns:
        (is_valid, error_message)
    """
    required_keys = {"skills", "experience", "seniority", "role", "location", "domain"}
    
    # Check all required keys present
    if not required_keys.issubset(weights.keys()):
        missing = required_keys - set(weights.keys())
        return False, f"Missing weight keys: {missing}"
    
    # Check weights are positive
    for key, value in weights.items():
        if value < 0:
            return False, f"Negative weight for {key}: {value}"
    
    # Check weights sum to 1.0 (with tolerance)
    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        return False, f"Weights sum to {total}, expected 1.0"
    
    return True, ""


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize weights to sum to 1.0.
    
    Args:
        weights: Raw weights dictionary
        
    Returns:
        Normalized weights
    """
    total = sum(weights.values())
    if total == 0:
        return {
            "skills": 0.35,
            "experience": 0.20,
            "seniority": 0.15,
            "role": 0.10,
            "location": 0.10,
            "domain": 0.10
        }
    
    return {k: v / total for k, v in weights.items()}


# =============================================================================
# Score Helpers
# =============================================================================

def clamp_score(score: float, min_val: float = MIN_SCORE, max_val: float = MAX_SCORE) -> float:
    """Clamp score to valid range."""
    return max(min_val, min(max_val, score))


def score_to_rating(score: float) -> str:
    """Convert numeric score to rating label."""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Very Good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 50:
        return "Below Average"
    else:
        return "Poor"


def calculate_percentile(score: float, all_scores: List[float]) -> float:
    """Calculate percentile rank of a score."""
    if not all_scores:
        return 50.0
    
    below = sum(1 for s in all_scores if s < score)
    return round((below / len(all_scores)) * 100, 1)


# =============================================================================
# Score Breakdown Helpers
# =============================================================================

@dataclass
class DimensionScore:
    """Individual dimension score with metadata."""
    name: str
    score: float
    weight: float
    weighted_score: float
    details: str


def format_breakdown(breakdown: Dict[str, float], weights: Dict[str, float]) -> List[DimensionScore]:
    """Format score breakdown into readable dimension scores."""
    results = []
    
    for dim in ["skills", "experience", "seniority", "role", "location", "domain"]:
        score = breakdown.get(dim, 0.0)
        weight = weights.get(dim, 0.0)
        weighted = score * weight
        
        results.append(DimensionScore(
            name=dim.capitalize(),
            score=score,
            weight=weight,
            weighted_score=weighted,
            details=_get_dimension_details(dim, score)
        ))
    
    return results


def _get_dimension_details(dimension: str, score: float) -> str:
    """Get human-readable details for a dimension score."""
    if score >= 90:
        detail = "Excellent match"
    elif score >= 70:
        detail = "Good match"
    elif score >= 50:
        detail = "Partial match"
    else:
        detail = "Weak match"
    
    return f"{detail} ({score:.0f}%)"


# =============================================================================
# Debug/Trace Utilities
# =============================================================================

@dataclass
class ScoringTrace:
    """Trace information for debugging scoring."""
    candidate_id: str
    dimension: str
    input_value: Any
    calculated_score: float
    reasoning: str


def create_trace(
    candidate_id: str,
    dimension: str,
    input_value: Any,
    score: float,
    reasoning: str
) -> ScoringTrace:
    """Create a scoring trace entry."""
    return ScoringTrace(
        candidate_id=candidate_id,
        dimension=dimension,
        input_value=input_value,
        calculated_score=score,
        reasoning=reasoning
    )


def format_trace(traces: List[ScoringTrace]) -> str:
    """Format traces into readable string."""
    lines = ["Scoring Trace:"]
    for trace in traces:
        lines.append(
            f"  [{trace.dimension}] {trace.input_value} -> "
            f"{trace.calculated_score:.1f}: {trace.reasoning}"
        )
    return "\n".join(lines)


# =============================================================================
# Summary Generation
# =============================================================================

def generate_summary(
    results: List[Dict[str, Any]],
    parsed_jd: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate summary statistics for match results."""
    if not results:
        return {
            "total_candidates": 0,
            "average_score": 0.0,
            "top_score": 0.0,
            "passing_count": 0
        }
    
    scores = [r["match_score"] for r in results]
    
    return {
        "total_candidates": len(results),
        "average_score": round(sum(scores) / len(scores), 2),
        "top_score": max(scores),
        "passing_count": sum(1 for s in scores if s >= PASS_THRESHOLD),
        "good_count": sum(1 for s in scores if s >= GOOD_THRESHOLD),
        "job_title": parsed_jd.get("role_title", "Unknown"),
        "required_skills_count": len(parsed_jd.get("required_skills", [])),
        "preferred_skills_count": len(parsed_jd.get("preferred_skills", []))
    }


# =============================================================================
# Filter Helpers
# =============================================================================

def filter_by_threshold(
    results: List[Dict[str, Any]],
    threshold: float = PASS_THRESHOLD
) -> List[Dict[str, Any]]:
    """Filter results by minimum score threshold."""
    return [r for r in results if r["match_score"] >= threshold]


def get_top_skills_gap(
    results: List[Dict[str, Any]],
    top_n: int = 5
) -> List[Tuple[str, int]]:
    """Analyze most common missing skills across top candidates."""
    skill_gaps = {}
    
    for result in results[:top_n]:
        for skill in result.get("missing_required_skills", []):
            skill_gaps[skill] = skill_gaps.get(skill, 0) + 1
    
    # Sort by frequency
    sorted_gaps = sorted(skill_gaps.items(), key=lambda x: x[1], reverse=True)
    return sorted_gaps


# =============================================================================
# Export Functions
# =============================================================================

__all__ = [
    "validate_weights",
    "normalize_weights",
    "clamp_score",
    "score_to_rating",
    "calculate_percentile",
    "format_breakdown",
    "generate_summary",
    "filter_by_threshold",
    "get_top_skills_gap",
    "MIN_SCORE",
    "MAX_SCORE",
    "PASS_THRESHOLD",
    "GOOD_THRESHOLD"
]