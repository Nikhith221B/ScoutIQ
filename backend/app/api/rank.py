"""
API route for ranking and shortlisting candidates.
POST /api/rank-shortlist
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

router = APIRouter()


class RankRequest(BaseModel):
    """Request schema for ranking candidates"""
    matched_candidates: List[dict] = Field(..., description="Matched candidates from /match-candidates")
    weights: Optional[dict] = Field(
        {"match_score_weight": 0.65, "interest_score_weight": 0.35},
        description="Custom weights for scoring: {match_score_weight, interest_score_weight}"
    )


class ScoredCandidate(BaseModel):
    """Candidate with all scoring details"""
    candidate_id: str
    name: str
    title: str
    location: str
    match_score: float
    interest_score: float
    combined_score: float
    score_breakdown: dict
    strengths: List[str]
    concerns: List[str]
    recommendation: str


class RankResponse(BaseModel):
    """Response schema for rank-shortlist"""
    job_title: str
    total_candidates: int
    shortlist: List[dict]
    top_candidate: dict
    scoring_summary: dict
    ranked_at: str


# Interest score factors (mock evaluation)
INTEREST_FACTORS = {
    "notice_period": {"1-15 days": 90, "16-30 days": 70, "31-60 days": 50, "60+ days": 30},
    "work_preference": {"remote": 85, "hybrid": 90, "onsite": 70},
    "seniority": {"junior": 60, "mid": 75, "senior": 85, "lead": 90, "principal": 95},
    "availability": {"immediate": 90, "2 weeks": 80, "1 month": 70, "2 months": 50}
}


@router.post("/rank-shortlist", response_model=RankResponse)
def rank_shortlist(request: RankRequest):
    """
    Rank and shortlist candidates based on match and interest scores.
    Returns scored and sorted candidates with explainability data.
    """
    # Default weights
    weights = request.weights or {"match_score_weight": 0.6, "interest_score_weight": 0.4}
    
    shortlist = []
    
    for candidate in request.matched_candidates:
        # Calculate Interest Score (mock factors)
        interest_factors = candidate.get("interest_factors", {})
        
        notice_score = INTEREST_FACTORS["notice_period"].get(
            interest_factors.get("notice_period", "16-30 days"), 50
        )
        work_score = INTEREST_FACTORS["work_preference"].get(
            interest_factors.get("work_preference", "hybrid"), 70
        )
        seniority_score = INTEREST_FACTORS["seniority"].get(
            interest_factors.get("seniority", "mid"), 75
        )
        availability_score = INTEREST_FACTORS["availability"].get(
            interest_factors.get("availability", "2 weeks"), 80
        )
        
        interest_score = (notice_score + work_score + seniority_score + availability_score) / 4
        
        # Calculate Combined Score
        match_score = candidate.get("match_score", 0)
        combined_score = (
            match_score * weights["match_score_weight"] +
            interest_score * weights["interest_score_weight"]
        )
        
        # Generate strengths and concerns
        strengths = []
        concerns = []
        
        if match_score >= 75:
            strengths.append("Strong skill match")
        if candidate.get("experience_match", False):
            strengths.append("Experience aligned")
        if candidate.get("location_match", False):
            strengths.append("Location suitable")
        
        missing_skills = candidate.get("missing_skills", [])
        if len(missing_skills) > 2:
            concerns.append(f"Missing {len(missing_skills)} key skills")
        if interest_score < 60:
            concerns.append("Lower interest indicators")
        
        # Generate recommendation
        if combined_score >= 80:
            recommendation = "Strong recommend"
        elif combined_score >= 65:
            recommendation = "Recommend"
        elif combined_score >= 50:
            recommendation = "Consider"
        else:
            recommendation = "Not recommended"
        
        scored_candidate = {
            "candidate_id": candidate.get("candidate_id"),
            "name": candidate.get("name"),
            "title": candidate.get("title"),
            "location": candidate.get("location", "Unknown"),
            "match_score": round(match_score, 2),
            "interest_score": round(interest_score, 2),
            "combined_score": round(combined_score, 2),
            "score_breakdown": {
                "match_score": round(match_score, 2),
                "interest_score": round(interest_score, 2),
                "weights": weights,
                "factors": {
                    "notice_period": notice_score,
                    "work_preference": work_score,
                    "seniority": seniority_score,
                    "availability": availability_score
                }
            },
            "strengths": strengths,
            "concerns": concerns,
            "recommendation": recommendation,
            "skills": candidate.get("skills", [])
        }
        
        shortlist.append(scored_candidate)
    
    # Sort by combined score
    shortlist.sort(key=lambda x: x["combined_score"], reverse=True)
    
    # Get top candidate
    top_candidate = shortlist[0] if shortlist else {}
    
    # Generate scoring summary
    scoring_summary = {
        "totalevaluated": len(shortlist),
        "strong_recommend": len([c for c in shortlist if c["recommendation"] == "Strong recommend"]),
        "recommend": len([c for c in shortlist if c["recommendation"] == "Recommend"]),
        "consider": len([c for c in shortlist if c["recommendation"] == "Consider"]),
        "not_recommended": len([c for c in shortlist if c["recommendation"] == "Not recommended"]),
        "average_combined_score": round(
            sum(c["combined_score"] for c in shortlist) / len(shortlist), 2
        ) if shortlist else 0
    }
    
    return RankResponse(
        job_title=request.matched_candidates[0].get("title", "Unknown") if request.matched_candidates else "Unknown",
        total_candidates=len(shortlist),
        shortlist=shortlist,
        top_candidate=top_candidate,
        scoring_summary=scoring_summary,
        ranked_at=datetime.utcnow().isoformat()
    )