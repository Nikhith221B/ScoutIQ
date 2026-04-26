"""
Models package for Deccan AI recruitment platform.
"""
from .schemas import (
    JobDescriptionInput,
    ParsedJD,
    Candidate,
    CandidateCreate,
    CandidateUpdate,
    MatchResult,
    RankedCandidate,
    OutreachMessage,
    InterestResult,
    CandidateSearchParams,
    CandidateListResponse,
)

__all__ = [
    "JobDescriptionInput",
    "ParsedJD",
    "Candidate",
    "CandidateCreate",
    "CandidateUpdate",
    "MatchResult",
    "RankedCandidate",
    "OutreachMessage",
    "InterestResult",
    "CandidateSearchParams",
    "CandidateListResponse",
]