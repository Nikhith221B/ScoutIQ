"""
Pydantic schemas for the Deccan AI recruitment platform.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal
from datetime import datetime


# =============================================================================
# Job Description Schemas
# =============================================================================

class JobDescriptionInput(BaseModel):
    """Input schema for job description parsing."""
    raw_text: str = Field(..., description="Raw job description text")
    company: Optional[str] = Field(None, description="Company name")
    title: Optional[str] = Field(None, description="Job title")


class ParsedJD(BaseModel):
    """Parsed job description with extracted requirements."""
    raw_text: str
    title: str
    company: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_min: Optional[int] = Field(None, description="Minimum years of experience")
    experience_max: Optional[int] = Field(None, description="Maximum years of experience")
    location: Optional[str] = None
    remote_policy: Optional[Literal["onsite", "remote", "hybrid"]] = None
    salary_min: Optional[int] = Field(None, description="Minimum salary in INR")
    salary_max: Optional[int] = Field(None, description="Maximum salary in INR")
    job_type: Optional[Literal["full-time", "part-time", "contract", "intern"]] = None
    description: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    nice_to_have: List[str] = Field(default_factory=list)
    parsed_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Candidate Schemas
# =============================================================================

class Candidate(BaseModel):
    """Candidate profile schema."""
    id: str
    name: str
    title: str
    years_experience: int
    location: str
    skills: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    education: str
    previous_companies: List[str] = Field(default_factory=list)
    summary: str
    preferred_roles: List[str] = Field(default_factory=list)
    salary_expectation: int = Field(..., description="Expected annual salary in INR")
    notice_period_days: int
    work_authorization: str
    open_to_remote: bool
    linkedin_url: str
    email: EmailStr
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CandidateCreate(BaseModel):
    """Schema for creating a new candidate."""
    name: str
    title: str
    years_experience: int
    location: str
    skills: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    education: str
    previous_companies: List[str] = Field(default_factory=list)
    summary: str
    preferred_roles: List[str] = Field(default_factory=list)
    salary_expectation: int
    notice_period_days: int = 30
    work_authorization: str = "Indian Citizen"
    open_to_remote: bool = True
    linkedin_url: str = ""
    email: EmailStr
    tags: List[str] = Field(default_factory=list)


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate."""
    name: Optional[str] = None
    title: Optional[str] = None
    years_experience: Optional[int] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    education: Optional[str] = None
    previous_companies: Optional[List[str]] = None
    summary: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    salary_expectation: Optional[int] = None
    notice_period_days: Optional[int] = None
    work_authorization: Optional[str] = None
    open_to_remote: Optional[bool] = None
    linkedin_url: Optional[str] = None
    email: Optional[EmailStr] = None
    tags: Optional[List[str]] = None


# =============================================================================
# Matching Schemas
# =============================================================================

class MatchResult(BaseModel):
    """Result of matching a candidate to a job description."""
    candidate_id: str
    candidate_name: str
    score: float = Field(..., description="Match score from 0-100")
    skill_match: float = Field(..., description="Skill match percentage")
    experience_match: float = Field(..., description="Experience match percentage")
    location_match: float = Field(..., description="Location compatibility score")
    salary_match: Optional[float] = Field(None, description="Salary alignment score")
    missing_skills: List[str] = Field(default_factory=list)
    matching_skills: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    overall_assessment: str


class RankedCandidate(BaseModel):
    """Ranked candidate with detailed match information."""
    rank: int
    candidate: Candidate
    match_result: MatchResult
    recommendation: str = Field(..., description="Hiring recommendation")
    next_steps: List[str] = Field(default_factory=list)


# =============================================================================
# Outreach Schemas
# =============================================================================

class OutreachMessage(BaseModel):
    """Generated outreach message for candidate."""
    candidate_id: str
    candidate_name: str
    subject: str
    body: str
    tone: Literal["formal", "casual", "professional"]
    personalization_points: List[str] = Field(default_factory=list)
    cta: str = Field(..., description="Call to action")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class InterestResult(BaseModel):
    """Result of checking candidate interest."""
    candidate_id: str
    candidate_name: str
    interest_level: Literal["high", "medium", "low", "not_interested"]
    reason: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    availability_for_call: Optional[str] = None
    notes: Optional[str] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Search and Filter Schemas
# =============================================================================

class CandidateSearchParams(BaseModel):
    """Parameters for searching candidates."""
    skills: Optional[List[str]] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    location: Optional[str] = None
    open_to_remote: Optional[bool] = None
    salary_max: Optional[int] = None
    industries: Optional[List[str]] = None
    notice_period_max: Optional[int] = None
    tags: Optional[List[str]] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class CandidateListResponse(BaseModel):
    """Response for candidate list endpoint."""
    total: int
    limit: int
    offset: int
    candidates: List[Candidate]