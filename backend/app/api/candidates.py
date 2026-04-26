"""
API route for candidate management.
GET /api/candidates
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
from pathlib import Path
from app.models.schemas import Candidate

router = APIRouter()

# Get the backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FILE = BACKEND_DIR / "app" / "data" / "candidates.json"


def load_candidates():
    """Load candidates from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


@router.get("/candidates", response_model=List[dict])
def list_candidates(
    skills: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[int] = None,
    max_experience: Optional[int] = None,
    title: Optional[str] = None
):
    """
    List all candidates with optional filters.
    
    Query parameters:
    - skills: comma-separated list of skills to filter by
    - location: filter by location
    - min_experience: minimum years of experience
    - max_experience: maximum years of experience
    - title: filter by job title
    """
    candidates = load_candidates()
    
    # Apply filters
    if skills:
        skill_list = [s.strip().lower() for s in skills.split(",")]
        candidates = [c for c in candidates if any(
            s.lower() in [skill.lower() for skill in c.get("skills", [])]
            for s in skill_list
        )]
    
    if location:
        candidates = [c for c in candidates if location.lower() in c.get("location", "").lower()]
    
    if min_experience is not None:
        candidates = [c for c in candidates if c.get("years_experience", 0) >= min_experience]
    
    if max_experience is not None:
        candidates = [c for c in candidates if c.get("years_experience", 0) <= max_experience]
    
    if title:
        candidates = [c for c in candidates if title.lower() in c.get("title", "").lower()]
    
    return candidates


@router.get("/candidates/{candidate_id}", response_model=dict)
def get_candidate(candidate_id: str):
    """Get a specific candidate by ID"""
    candidates = load_candidates()
    for candidate in candidates:
        if str(candidate.get("id")) == candidate_id:
            return candidate
    raise HTTPException(status_code=404, detail="Candidate not found")