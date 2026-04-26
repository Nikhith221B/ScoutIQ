"""
API route for simulating outreach to candidates.
POST /api/simulate-outreach
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.outreach_simulator import get_simulator

router = APIRouter()


class OutreachRequest(BaseModel):
    """Request schema for outreach simulation"""
    candidate_ids: List[str] = Field(..., description="List of candidate IDs to outreach")
    candidates_override: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Optional candidate list (used instead of local JSON dataset)",
    )
    job_title: str = Field(..., description="Job title being recruited for")
    company: str = Field(..., description="Company name")
    job_description: Optional[str] = Field(None, description="Job description text")
    job_id: Optional[str] = Field(None, description="Job ID to fetch JD details")
    message_tone: Optional[str] = Field("professional", description="Tone: professional, friendly, or casual")


class OutreachMessage(BaseModel):
    """Individual outreach message"""
    candidate_id: str
    candidate_name: str
    subject: str
    message: str
    generated_at: str


class SimulatedOutreachResult(BaseModel):
    """Result for a single candidate outreach simulation"""
    candidate_id: str
    candidate_name: str
    outreach_message: str
    candidate_response: str
    interest_score: int
    interest_breakdown: Dict[str, int]
    interest_label: str
    explanation: str


class OutreachResponse(BaseModel):
    """Response schema for simulate-outreach"""
    job_title: str
    company: str
    results: List[Dict[str, Any]]
    total_outreach: int
    generated_at: str


# Template messages for different tones
MESSAGE_TEMPLATES = {
    "professional": {
        "subject": "Opportunity at {company} - {title} Role",
        "body": """Dear {name},

I hope this email finds you well. I am reaching out regarding an exciting opportunity at {company} for the position of {title}.

Based on your impressive background in {skills}, we believe you could be a great fit for this role. The position offers competitive compensation, hybrid work flexibility, and an opportunity to work on cutting-edge projects.

Would you be interested in exploring this opportunity? I would love to schedule a brief call to discuss the role details and answer any questions you may have.

Best regards,
Recruiter Team"""
    },
    "friendly": {
        "subject": "Hey {name}! Exciting opportunity at {company} 🚀",
        "body": """Hi {name}!

Hope you're doing great! I came across your profile and was really impressed by your experience in {skills}.

We're hiring for an exciting {title} role at {company}, and I thought you'd be a perfect fit! The team is amazing, the work is super interesting, and we offer great flexibility.

Would you be up for a quick chat to learn more? No pressure at all - just a casual conversation to see if it's a good match!

Cheers,
Recruiter"""
    },
    "casual": {
        "subject": "{title} role at {company} - interested?",
        "body": """Hey {name},

Quick question - are you looking for a new role? We've got a {title} position at {company} that could be a great fit given your background in {skills}.

The vibe here is pretty cool - hybrid setup, good pay, and awesome team to work with. Let me know if you want to hear more!

- Recruiter"""
    }
}


@router.post("/simulate-outreach", response_model=OutreachResponse)
def simulate_outreach(request: OutreachRequest):
    """
    Simulate outreach messages to candidates with interest scoring.
    Returns generated email templates, candidate responses, and interest scores.
    """
    import json
    import os
    
    # Load candidate data from JSON file (default) or use caller-provided override
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    if request.candidates_override is not None:
        candidates_data = request.candidates_override
    else:
        with open(os.path.join(data_dir, "candidates.json"), "r") as f:
            candidates_data = json.load(f)
    
    with open(os.path.join(data_dir, "sample_jds.json"), "r") as f:
        jds_data = json.load(f)
    
    # Get job details
    job = None
    if request.job_id:
        job = next((j for j in jds_data if j.get("id") == request.job_id), None)
    
    if job is None:
        # Create a job dict from request parameters
        job = {
            "id": "manual",
            "title": request.job_title,
            "company": request.company,
            "raw_text": request.job_description or f"{request.job_title} at {request.company}",
            "required_skills": [],
            "preferred_skills": [],
            "salary_min": 2000000,
            "salary_max": 4000000,
            "remote_policy": "hybrid"
        }
    
    # Get simulator
    simulator = get_simulator()
    tone = request.message_tone or "professional"
    
    results = []
    # Build fast lookup for override datasets (ids are strings in the pipeline)
    candidates_lookup = {}
    try:
        candidates_lookup = {str(c.get("id")): c for c in candidates_data if isinstance(c, dict) and c.get("id") is not None}
    except Exception:
        candidates_lookup = {}

    for candidate_id in request.candidate_ids:
        # Find candidate data
        candidate = candidates_lookup.get(str(candidate_id))
        
        if candidate is None:
            # Use mock data for unknown candidates
            candidate = {
                "id": candidate_id,
                "name": f"Candidate {candidate_id}",
                "skills": ["Python", "JavaScript"],
                "desired_roles": [request.job_title],
                "availability": "2 weeks",
                "compensation_expectation": 3000000,
                "work_preference": "hybrid"
            }
        
        # Run simulation
        simulation = simulator.simulate(
            candidate=candidate,
            job=job,
            tone=tone
        )
        
        results.append({
            "candidate_id": candidate_id,
            "candidate_name": candidate.get("name", f"Candidate {candidate_id}"),
            "outreach_message": simulation["outreach_message"],
            "candidate_response": simulation["candidate_response"],
            "interest_score": simulation["interest_score"],
            "interest_breakdown": simulation["interest_breakdown"],
            "interest_label": simulation["interest_label"],
            "explanation": simulation["explanation"]
        })
    
    return OutreachResponse(
        job_title=request.job_title,
        company=request.company,
        results=results,
        total_outreach=len(results),
        generated_at=datetime.utcnow().isoformat()
    )