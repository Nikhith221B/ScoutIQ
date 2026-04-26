from __future__ import annotations

from typing import Any, Dict, List, Optional
import csv
import io
import json
import re

from app.services.matcher import SKILL_ALIASES


def _split_skills(raw: str) -> List[str]:
    if not isinstance(raw, str):
        return []
    # Support: "python; sql; react" or "python, sql, react"
    parts = re.split(r"[;,]\s*|\n", raw.strip())
    skills = []
    for p in parts:
        s = p.strip()
        if s:
            skills.append(s)
    return skills


def _normalize_candidate_dict(c: Dict[str, Any], fallback_id: str) -> Dict[str, Any]:
    """
    Normalize incoming candidate records to the shape expected by matcher/outreach.
    """
    cid = c.get("id")
    if cid is None or str(cid).strip() == "":
        cid = fallback_id

    name = c.get("name") or f"Candidate {cid}"
    title = c.get("title") or c.get("candidate_title") or "Candidate"
    location = c.get("location") or ""

    years_experience = c.get("years_experience")
    if years_experience is None:
        years_experience = c.get("experience_years")
    try:
        years_experience = int(years_experience) if years_experience is not None else 0
    except Exception:
        years_experience = 0

    skills = c.get("skills")
    if isinstance(skills, str):
        skills = _split_skills(skills)
    if not isinstance(skills, list):
        skills = []

    industries = c.get("industries")
    if isinstance(industries, str):
        industries = _split_skills(industries)
    if not isinstance(industries, list):
        industries = []

    # Outreach simulator looks at a few preference-like fields; set safe defaults.
    desired_roles = c.get("desired_roles") or c.get("preferred_roles") or [title]
    if isinstance(desired_roles, str):
        desired_roles = [desired_roles]
    if not isinstance(desired_roles, list):
        desired_roles = [title]

    availability = c.get("availability") or "2-4 weeks"
    work_preference = c.get("work_preference") or ("remote" if c.get("open_to_remote") else "hybrid")

    comp = c.get("compensation_expectation")
    if comp is None:
        comp = c.get("salary_expectation")
    try:
        comp = int(comp) if comp is not None else 3000000
    except Exception:
        comp = 3000000

    return {
        "id": str(cid),
        "name": str(name),
        "title": str(title),
        "years_experience": years_experience,
        "location": str(location),
        "skills": [str(s) for s in skills if isinstance(s, (str, int, float))],
        "industries": [str(i) for i in industries if isinstance(i, (str, int, float))],
        "desired_roles": [str(r) for r in desired_roles if isinstance(r, (str, int, float))],
        "availability": str(availability),
        "compensation_expectation": comp,
        "work_preference": str(work_preference),
    }


def parse_candidates_csv_bytes(raw: bytes) -> List[Dict[str, Any]]:
    text = raw.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    out: List[Dict[str, Any]] = []
    for idx, row in enumerate(reader):
        if not isinstance(row, dict):
            continue
        out.append(_normalize_candidate_dict(row, fallback_id=str(idx + 1)))
    return out


def parse_candidates_json_bytes(raw: bytes) -> List[Dict[str, Any]]:
    text = raw.decode("utf-8", errors="ignore")
    data = json.loads(text)
    if isinstance(data, dict) and isinstance(data.get("candidates"), list):
        data = data["candidates"]
    if not isinstance(data, list):
        raise ValueError("JSON must be a list of candidates or an object with a 'candidates' list")
    out: List[Dict[str, Any]] = []
    for idx, item in enumerate(data):
        if isinstance(item, dict):
            out.append(_normalize_candidate_dict(item, fallback_id=str(idx + 1)))
    return out


def _extract_skills_from_text(text: str) -> List[str]:
    """
    Simple deterministic skill extraction: match SKILL_ALIASES keys/aliases in text.
    """
    t = (text or "").lower()
    found = set()
    for canonical, aliases in SKILL_ALIASES.items():
        for a in [canonical, *aliases]:
            a_norm = a.lower().strip()
            if not a_norm:
                continue
            # word-ish boundary match to reduce false positives
            if re.search(rf"(^|[^a-z0-9\+#\.]){re.escape(a_norm)}([^a-z0-9\+#\.]|$)", t):
                found.add(canonical)
                break
    return sorted(found)


def _extract_years_experience(text: str) -> Optional[int]:
    """
    Extract a rough years-of-experience signal from resume text.
    Examples: "5 years", "5+ years", "7 yrs"
    """
    t = (text or "").lower()
    m = re.search(r"(\d{1,2})\s*\+?\s*(years|yrs)\b", t)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def candidate_from_resume_text(
    resume_text: str,
    *,
    name: Optional[str] = None,
    title: Optional[str] = None,
    location: Optional[str] = None,
    years_experience: Optional[int] = None,
) -> Dict[str, Any]:
    skills = _extract_skills_from_text(resume_text)
    yrs = years_experience if isinstance(years_experience, int) else _extract_years_experience(resume_text) or 0
    base = {
        "id": "uploaded_1",
        "name": name or "Uploaded Candidate",
        "title": title or "Candidate",
        "years_experience": yrs,
        "location": location or "",
        "skills": skills,
        "industries": [],
        "desired_roles": [title] if title else [],
        "availability": "2-4 weeks",
        "compensation_expectation": 3000000,
        "work_preference": "hybrid",
    }
    return _normalize_candidate_dict(base, fallback_id="uploaded_1")


def extract_text_from_pdf_bytes(raw: bytes) -> str:
    """
    Extract text from a *text-based* PDF.

    Notes:
    - This will not work well for scanned/image PDFs (OCR is intentionally out of scope for this prototype).
    - Returns extracted text (may be empty).
    """
    try:
        from pypdf import PdfReader
    except Exception as e:  # pragma: no cover
        raise RuntimeError("PDF support is not installed. Add 'pypdf' to requirements.") from e

    reader = PdfReader(io.BytesIO(raw))
    parts: List[str] = []
    for page in reader.pages:
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        if t.strip():
            parts.append(t)
    return "\n\n".join(parts).strip()

