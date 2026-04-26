"""
API route for matching candidates to job descriptions.
POST /api/match-candidates
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import json
from pathlib import Path
from datetime import datetime

from app.services.matcher import match_candidates, to_list_dict, load_candidates_from_file

router = APIRouter()


class MatchRequest(BaseModel):
    """Request schema for matching candidates"""
    parsed_jd: dict = Field(..., description="Parsed job description from /parse-jd")
    candidate_ids: Optional[List[str]] = Field(None, description="Specific candidate IDs to match (optional)")
    candidates_override: Optional[List[dict]] = Field(
        None,
        description="Optional candidate list to match instead of loading from local JSON dataset",
    )
    limit: int = Field(20, description="Maximum number of candidates to return")


class MatchResult(BaseModel):
    """Individual match result"""
    candidate_id: str
    name: str
    title: str
    match_score: float
    skill_match: List[str]
    missing_skills: List[str]
    experience_match: bool
    location_match: bool


class MatchResponse(BaseModel):
    """Response schema for match-candidates"""
    job_title: str
    company: Optional[str]
    total_candidates: int
    matched_candidates: List[dict]
    matched_at: str


@router.post("/match-candidates", response_model=MatchResponse)
def match_candidates_endpoint(request: MatchRequest):
    """
    Match candidates against a parsed job description.
    Uses the rule-based matcher service for scoring.
    """
    # Load candidates from file (default) or use caller-provided override
    candidates = request.candidates_override if request.candidates_override is not None else load_candidates_from_file()
    
    # Filter by specific candidate IDs if provided
    if request.candidate_ids:
        candidates = [c for c in candidates if str(c.get("id")) in request.candidate_ids]
    
    # Use the matcher service
    results = match_candidates(
        parsed_jd=request.parsed_jd,
        candidates=candidates,
        limit=request.limit
    )
    
    # Convert to list of dicts
    matched_candidates = to_list_dict(results)

    # Enrich match payload with candidate profile fields needed by rank + UI.
    # Without this, later stages can lose `skills` and the UI will have to derive values.
    try:
        by_id = {str(c.get("id")): c for c in candidates if isinstance(c, dict) and c.get("id") is not None}
        for m in matched_candidates:
            cid = str(m.get("candidate_id"))
            c = by_id.get(cid)
            if not isinstance(c, dict):
                continue
            if "skills" not in m:
                m["skills"] = c.get("skills", [])
            if "location" not in m:
                m["location"] = c.get("location")
    except Exception:
        # Best-effort enrichment only
        pass
    
    return MatchResponse(
        job_title=request.parsed_jd.get("title", request.parsed_jd.get("role_title", "Unknown")),
        company=request.parsed_jd.get("company"),
        total_candidates=len(candidates),
        matched_candidates=matched_candidates,
        matched_at=datetime.utcnow().isoformat() + "Z"
    )