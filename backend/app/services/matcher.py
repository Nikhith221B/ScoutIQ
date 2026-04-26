"""
Candidate Matcher Service - Rule-based candidate matching for MVP.

Provides structured matching of candidates to parsed job descriptions:
- candidate_id
- match_score (0-100)
- score_breakdown
- matched_skills
- missing_required_skills
- preferred_skill_hits
- explanation
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ScoreBreakdown:
    """Detailed breakdown of match score."""
    skills_score: float = 0.0
    experience_score: float = 0.0
    seniority_score: float = 0.0
    role_score: float = 0.0
    location_score: float = 0.0
    domain_score: float = 0.0


@dataclass
class MatchResult:
    """Structured match result for a candidate."""
    candidate_id: str
    name: str
    title: str
    match_score: float
    score_breakdown: ScoreBreakdown
    matched_skills: List[str] = field(default_factory=list)
    missing_required_skills: List[str] = field(default_factory=list)
    preferred_skill_hits: List[str] = field(default_factory=list)
    explanation: str = ""


# =============================================================================
# Weight Configuration
# =============================================================================

# Weights for each scoring dimension (must sum to 1.0)
DEFAULT_WEIGHTS = {
    "skills": 0.35,
    "experience": 0.20,
    "seniority": 0.15,
    "role": 0.10,
    "location": 0.10,
    "domain": 0.10
}


# =============================================================================
# Skill Mapping (normalize variations)
# =============================================================================

SKILL_ALIASES = {
    "python": ["python", "python3", "py"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "reactjs", "react.js", "react native"],
    "angular": ["angular", "angularjs", "angular.js"],
    "vue": ["vue", "vuejs", "vue.js"],
    "node.js": ["node.js", "nodejs", "node", "express"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "java": ["java", "j2ee", "j2se"],
    "spring": ["spring", "spring boot", "springboot"],
    "golang": ["golang", "go"],
    "rust": ["rust"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c#": ["c#", "csharp", "c sharp", ".net", "dotnet"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "oracle", "sqlite"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "aws": ["aws", "amazon web services", "amazon aws"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker", "container"],
    "kubernetes": ["kubernetes", "k8s", "kubes"],
    "terraform": ["terraform", "tf"],
    "jenkins": ["jenkins", "ci/cd", "cicd"],
    "machine learning": ["machine learning", "ml", "ai", "artificial intelligence"],
    "deep learning": ["deep learning", "dl", "neural network"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "pyTorch"],
    "data science": ["data science", "data scientist"],
    "data analysis": ["data analysis", "data analyst", "analytics"],
    "etl": ["etl", "extract transform load"],
    "spark": ["spark", "pyspark", "apache spark"],
    "hadoop": ["hadoop", "hdfs"],
    "kafka": ["kafka", "apache kafka"],
    "airflow": ["airflow", "apache airflow"],
    "agile": ["agile", "scrum", "kanban"],
    "scrum": ["scrum", "agile"],
}


# =============================================================================
# Main Matcher Function
# =============================================================================

def match_candidates(
    parsed_jd: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    weights: Optional[Dict[str, float]] = None,
    limit: int = 20
) -> List[MatchResult]:
    """
    Match candidates against a parsed job description.
    
    Args:
        parsed_jd: Parsed job description from JD parser
        candidates: List of candidate dictionaries
        weights: Optional custom weights for scoring dimensions
        limit: Maximum number of results to return
        
    Returns:
        List of MatchResult objects sorted by match_score descending
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()
    
    results = []
    
    for candidate in candidates:
        result = _score_candidate(parsed_jd, candidate, weights)
        results.append(result)
    
    # Sort by match score descending
    results.sort(key=lambda x: x.match_score, reverse=True)
    
    return results[:limit]


def _score_candidate(
    parsed_jd: Dict[str, Any],
    candidate: Dict[str, Any],
    weights: Dict[str, float]
) -> MatchResult:
    """Score a single candidate against a JD."""
    
    # Extract JD fields
    required_skills = _normalize_skills(parsed_jd.get("required_skills", []))
    preferred_skills = _normalize_skills(parsed_jd.get("preferred_skills", []))
    jd_experience = parsed_jd.get("minimum_experience")
    jd_seniority = parsed_jd.get("seniority")
    jd_location = parsed_jd.get("location", "").lower() if parsed_jd.get("location") else ""
    jd_work_mode = parsed_jd.get("work_mode")
    jd_domain = parsed_jd.get("domain")
    jd_keywords = parsed_jd.get("keywords", [])
    
    # Extract candidate fields
    cand_skills = _normalize_skills(candidate.get("skills", []))
    cand_exp = candidate.get("years_experience", 0)
    cand_title = candidate.get("title", "").lower()
    cand_location = candidate.get("location", "").lower() if candidate.get("location") else ""
    cand_industries = [i.lower() for i in candidate.get("industries", [])]
    
    # Calculate dimension scores
    skills_result = _calculate_skills_score(required_skills, preferred_skills, cand_skills)
    
    experience_score = _calculate_experience_score(jd_experience, cand_exp)
    seniority_score = _calculate_seniority_score(jd_seniority, cand_exp, cand_title)
    role_score = _calculate_role_score(parsed_jd.get("role_title", ""), cand_title)
    location_score = _calculate_location_score(jd_location, jd_work_mode, cand_location)
    domain_score = _calculate_domain_score(jd_domain, jd_keywords, cand_industries)
    
    # Build score breakdown
    breakdown = ScoreBreakdown(
        skills_score=skills_result["score"],
        experience_score=experience_score,
        seniority_score=seniority_score,
        role_score=role_score,
        location_score=location_score,
        domain_score=domain_score
    )
    
    # Calculate weighted total
    total_score = (
        (breakdown.skills_score * weights["skills"]) +
        (breakdown.experience_score * weights["experience"]) +
        (breakdown.seniority_score * weights["seniority"]) +
        (breakdown.role_score * weights["role"]) +
        (breakdown.location_score * weights["location"]) +
        (breakdown.domain_score * weights["domain"])
    )
    
    # Round to 2 decimal places
    total_score = round(total_score, 2)
    
    # Generate explanation
    explanation = _generate_explanation(
        skills_result, breakdown, candidate, parsed_jd
    )
    
    return MatchResult(
        candidate_id=str(candidate.get("id", "")),
        name=candidate.get("name", ""),
        title=candidate.get("title", ""),
        match_score=total_score,
        score_breakdown=breakdown,
        matched_skills=skills_result["matched"],
        missing_required_skills=skills_result["missing_required"],
        preferred_skill_hits=skills_result["preferred_hits"],
        explanation=explanation
    )


# =============================================================================
# Scoring Functions
# =============================================================================

def _normalize_skills(skills: List[str]) -> set:
    """Normalize skills to canonical form."""
    normalized = set()
    for skill in skills:
        skill_lower = skill.lower().strip()
        normalized.add(skill_lower)
    return normalized


def _calculate_skills_score(
    required: set,
    preferred: set,
    candidate_skills: set
) -> Dict[str, Any]:
    """Calculate skills match score."""
    matched_required = []
    missing_required = []
    preferred_hits = []
    
    # Check required skills
    for skill in required:
        if skill in candidate_skills:
            matched_required.append(skill)
        else:
            # Check aliases
            found = False
            for canonical, aliases in SKILL_ALIASES.items():
                if skill in aliases or skill == canonical:
                    for alias in aliases:
                        if alias in candidate_skills:
                            matched_required.append(skill)
                            found = True
                            break
            if not found:
                missing_required.append(skill)
    
    # Check preferred skills
    for skill in preferred:
        if skill in candidate_skills:
            preferred_hits.append(skill)
        else:
            for canonical, aliases in SKILL_ALIASES.items():
                if skill in aliases or skill == canonical:
                    for alias in aliases:
                        if alias in candidate_skills:
                            preferred_hits.append(skill)
                            break
    
    # Calculate score
    total_required = len(required) if required else 1
    required_score = (len(matched_required) / total_required) * 100 if required else 50
    
    # Bonus for preferred skills (up to 10 points)
    preferred_bonus = min(len(preferred_hits) * 2, 10)
    
    score = min(required_score + preferred_bonus, 100)
    
    return {
        "score": round(score, 2),
        "matched": matched_required,
        "missing_required": missing_required,
        "preferred_hits": preferred_hits
    }


def _calculate_experience_score(
    jd_experience: Optional[int],
    cand_exp: int
) -> float:
    """Calculate experience fit score."""
    if jd_experience is None:
        return 50.0  # Neutral if not specified
    
    # Perfect match
    if cand_exp == jd_experience:
        return 100.0
    
    # Within range (jd_experience to jd_experience + 2)
    if cand_exp >= jd_experience and cand_exp <= jd_experience + 2:
        return 100.0
    
    # Slightly under (1-2 years less)
    if cand_exp >= jd_experience - 2 and cand_exp < jd_experience:
        return 70.0
    
    # Significantly under (3+ years less)
    if cand_exp < jd_experience - 2:
        return 40.0
    
    # Over-qualified (3+ years more)
    if cand_exp > jd_experience + 2:
        return 60.0
    
    return 50.0


def _calculate_seniority_score(
    jd_seniority: Optional[str],
    cand_exp: int,
    cand_title: str
) -> float:
    """Calculate seniority fit score."""
    if jd_seniority is None:
        return 50.0
    
    seniority_map = {
        "entry": (0, 2),
        "mid": (2, 5),
        "senior": (5, 8),
        "lead": (8, 12),
        "director": (12, 20)
    }
    
    jd_range = seniority_map.get(jd_seniority, (0, 20))
    
    # Check title hints
    title_lower = cand_title.lower()
    if "senior" in title_lower or "lead" in title_lower:
        cand_exp = max(cand_exp, 5)
    if "principal" in title_lower or "architect" in title_lower:
        cand_exp = max(cand_exp, 8)
    if "director" in title_lower or "vp" in title_lower:
        cand_exp = max(cand_exp, 12)
    if "junior" in title_lower or "intern" in title_lower:
        cand_exp = min(cand_exp, 2)
    
    # Within range
    if jd_range[0] <= cand_exp <= jd_range[1]:
        return 100.0
    
    # One level off
    if jd_range[0] - 2 <= cand_exp <= jd_range[1] + 2:
        return 70.0
    
    return 40.0


def _calculate_role_score(jd_title: str, cand_title: str) -> float:
    """Calculate role relevance score."""
    if not jd_title or not cand_title:
        return 50.0
    
    jd_lower = jd_title.lower()
    cand_lower = cand_title.lower()
    
    # Exact or close match
    if jd_lower == cand_lower:
        return 100.0
    
    # Key role words
    role_words = ["engineer", "developer", "manager", "analyst", "architect", "lead", "director"]
    
    jd_words = set(jd_lower.split())
    cand_words = set(cand_lower.split())
    
    common = jd_words & cand_words
    if common:
        return 80.0
    
    # Check role word overlap
    jd_roles = [w for w in role_words if w in jd_lower]
    cand_roles = [w for w in role_words if w in cand_lower]
    
    if jd_roles and cand_roles:
        if jd_roles[0] == cand_roles[0]:
            return 90.0
        return 60.0
    
    return 40.0


def _calculate_location_score(
    jd_location: str,
    jd_work_mode: Optional[str],
    cand_location: str
) -> float:
    """Calculate location/work mode fit score."""
    # No location preference
    if not jd_location and not jd_work_mode:
        return 50.0
    
    score = 50.0
    
    # Check work mode preference
    if jd_work_mode:
        if jd_work_mode == "remote":
            if "remote" in cand_location or "anywhere" in cand_location:
                return 100.0
            return 60.0
        elif jd_work_mode == "hybrid":
            return 80.0
        elif jd_work_mode == "onsite":
            if jd_location and jd_location in cand_location:
                return 100.0
            return 50.0
    
    # Check location match
    if jd_location and jd_location in cand_location:
        return 100.0
    
    # Partial match
    if jd_location:
        jd_city = jd_location.split()[0] if jd_location else ""
        if jd_city and jd_city in cand_location:
            return 80.0
    
    return score


def _calculate_domain_score(
    jd_domain: Optional[str],
    jd_keywords: List[str],
    cand_industries: List[str]
) -> float:
    """Calculate domain/industry relevance score."""
    if not jd_domain and not jd_keywords:
        return 50.0
    
    if not cand_industries:
        return 50.0
    
    # Direct domain match
    if jd_domain and jd_domain in cand_industries:
        return 100.0
    
    # Keyword matching
    if jd_keywords:
        matches = sum(1 for kw in jd_keywords if kw in cand_industries)
        if matches > 0:
            return min(50 + (matches * 15), 100)
    
    return 40.0


def _generate_explanation(
    skills_result: Dict[str, Any],
    breakdown: ScoreBreakdown,
    candidate: Dict[str, Any],
    parsed_jd: Dict[str, Any]
) -> str:
    """Generate human-readable explanation."""
    parts = []
    
    # Skills summary
    matched = skills_result["matched"]
    missing = skills_result["missing_required"]
    
    if matched:
        parts.append(f"Matched {len(matched)} required skill(s): {', '.join(matched[:3])}")
    if missing:
        parts.append(f"Missing {len(missing)} required skill(s): {', '.join(missing[:2])}")
    
    # Experience
    cand_exp = candidate.get("years_experience", 0)
    jd_exp = parsed_jd.get("minimum_experience")
    if jd_exp:
        if cand_exp >= jd_exp:
            parts.append(f"Meets {jd_exp}+ years experience requirement")
        else:
            parts.append(f"Has {cand_exp} years (needs {jd_exp}+)")
    
    # Overall score
    if breakdown.skills_score >= 80:
        parts.append("Strong skill match")
    elif breakdown.skills_score >= 60:
        parts.append("Good skill match")
    else:
        parts.append("Partial skill match")
    
    return ". ".join(parts) if parts else "No significant match factors found"


# =============================================================================
# Output Conversion
# =============================================================================

def to_dict(result: MatchResult) -> Dict[str, Any]:
    """Convert MatchResult to dictionary for JSON serialization."""
    return {
        "candidate_id": result.candidate_id,
        "name": result.name,
        "title": result.title,
        "match_score": result.match_score,
        "score_breakdown": {
            "skills_score": result.score_breakdown.skills_score,
            "experience_score": result.score_breakdown.experience_score,
            "seniority_score": result.score_breakdown.seniority_score,
            "role_score": result.score_breakdown.role_score,
            "location_score": result.score_breakdown.location_score,
            "domain_score": result.score_breakdown.domain_score
        },
        "matched_skills": result.matched_skills,
        "missing_required_skills": result.missing_required_skills,
        "preferred_skill_hits": result.preferred_skill_hits,
        "explanation": result.explanation
    }


def to_list_dict(results: List[MatchResult]) -> List[Dict[str, Any]]:
    """Convert list of MatchResults to list of dictionaries."""
    return [to_dict(r) for r in results]


# =============================================================================
# Candidate Loading
# =============================================================================

def load_candidates_from_file(filepath: str = None) -> List[Dict[str, Any]]:
    """Load candidates from JSON file."""
    if filepath is None:
        # Default to candidates.json in data folder
        base_path = Path(__file__).resolve().parent.parent
        filepath = str(base_path / "data" / "candidates.json")
    
    path = Path(filepath)
    if path.exists():
        with open(path, "r") as f:
            data = json.load(f)
            # Handle both list and dict formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "candidates" in data:
                return data["candidates"]
    return []