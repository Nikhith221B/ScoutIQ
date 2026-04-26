"""
Bring-your-own-candidates ingestion helpers.

This route exists to support hackathon-grade "candidate discovery" without
scraping external sources: recruiters can upload a CSV/JSON file or paste
resume text to create candidate profiles for matching + outreach simulation.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal
import json

from app.services.candidate_ingest import (
    parse_candidates_csv_bytes,
    parse_candidates_json_bytes,
    candidate_from_resume_text,
    extract_text_from_pdf_bytes,
)


router = APIRouter()


class ResumeToCandidateRequest(BaseModel):
    resume_text: str = Field(..., description="Raw resume text pasted by user")
    name: Optional[str] = Field(None, description="Optional candidate name override")
    title: Optional[str] = Field(None, description="Optional candidate title override")
    location: Optional[str] = Field(None, description="Optional candidate location override")
    years_experience: Optional[int] = Field(None, description="Optional years of experience override")


class IngestCandidatesResponse(BaseModel):
    source: str
    total: int
    candidates: List[Dict[str, Any]]


@router.post("/ingest-candidates/file", response_model=IngestCandidatesResponse)
async def ingest_candidates_file(file: UploadFile = File(...)):
    """
    Upload a CSV/JSON file (candidate list) or a PDF (single resume) and receive normalized candidate dicts.

    Accepted formats:
    - CSV: columns like id,name,title,years_experience,location,skills
           where skills can be "python;react;sql" or "python, react, sql"
    - JSON: either a list of candidates, or { "candidates": [ ... ] }
    - PDF: resume PDF (text-based) -> converted to a single candidate via deterministic extraction
    """
    filename = (file.filename or "").lower()
    raw = await file.read()

    try:
        if filename.endswith(".csv"):
            candidates = parse_candidates_csv_bytes(raw)
            return IngestCandidatesResponse(source="csv", total=len(candidates), candidates=candidates)
        if filename.endswith(".json"):
            candidates = parse_candidates_json_bytes(raw)
            return IngestCandidatesResponse(source="json", total=len(candidates), candidates=candidates)
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf_bytes(raw)
            if not text.strip():
                raise ValueError("No extractable text found in PDF. If this is a scanned PDF, paste resume text instead.")
            candidate = candidate_from_resume_text(text)
            return IngestCandidatesResponse(source="pdf", total=1, candidates=[candidate])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    raise HTTPException(status_code=400, detail="Unsupported file type. Upload a .csv, .json, or .pdf file.")


@router.post("/ingest-candidates/resume", response_model=IngestCandidatesResponse)
def ingest_candidates_resume(payload: ResumeToCandidateRequest):
    """
    Convert pasted resume text into a single candidate profile.
    """
    try:
        candidate = candidate_from_resume_text(
            payload.resume_text,
            name=payload.name,
            title=payload.title,
            location=payload.location,
            years_experience=payload.years_experience,
        )
        return IngestCandidatesResponse(source="resume_text", total=1, candidates=[candidate])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume text: {e}")

