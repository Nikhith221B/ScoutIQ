# Architecture

This document describes the **actual runtime architecture** implemented in this repository (frontend + backend + local JSON data).

## High-level flow (what the UI uses)

The frontend calls **one** backend endpoint for the end-to-end flow:

```
Next.js UI  ──POST /api/run-pipeline──▶  FastAPI pipeline orchestrator
  (frontend/app/page.tsx)                  (backend/app/api/pipeline.py)
```

Inside the pipeline request, the backend executes these stages:

```
parse_jd  →  match_candidates  →  rank_shortlist  →  simulate_outreach  →  compile shortlist
```

## Components and where they live

- **Frontend (Next.js)**: `frontend/app/page.tsx`
  - Collects free-form JD text and calls `POST /api/run-pipeline`
  - Renders shortlist, candidate drawer, and explanation fields returned by the API

- **Backend (FastAPI)**: `backend/app/main.py`
  - Mounts routers under `/api`:
    - `health`, `talents`, `candidates`, `parse_jd`, `match`, `rank`, `outreach`, `pipeline`

- **JD parsing**: `backend/app/api/parse_jd.py` + `backend/app/services/jd_parser.py`
  - Produces a `ParsedJD` object with fields like `required_skills`, `preferred_skills`, `experience_min`, `location`, `remote_policy`

- **Matching (match score + explainability)**: `backend/app/services/matcher.py`
  - Computes a weighted match score across dimensions:
    - `skills_score`, `experience_score`, `seniority_score`, `role_score`, `location_score`, `domain_score`
  - Emits explainability fields used by the pipeline/UI:
    - `matched_skills`, `missing_required_skills`, `score_breakdown`, `explanation`

- **Outreach simulation (interest score + explainability)**: `backend/app/services/outreach_simulator.py`
  - Generates outreach message + simulated response
  - Computes a deterministic interest score (sum of 5 factors) and returns:
    - `interest_score`, `interest_breakdown`, `interest_label`, `explanation`

- **Ranking**: `backend/app/api/rank.py`
  - Provides a standalone ranking endpoint (`POST /api/rank-shortlist`)
  - The pipeline uses it to get a shortlist ordering, then compiles the final shortlist payload

## Data sources (local JSON)

These are the source-of-truth files used at runtime:

- **Candidates** (used by matching + pipeline): `backend/app/data/candidates.json`
- **Sample JDs** (used by outreach simulation when `job_id` is provided): `backend/app/data/sample_jds.json`
- **Talents** (served by `/api/talents`, separate from pipeline): `backend/app/data/talents.json`

## Key request/response boundary

For submission/demo purposes, the most important contract is:

- **`POST /api/run-pipeline`**: takes free-form `raw_jd` text and returns:
  - parsed JD summary
  - ranked shortlist
  - match + interest breakdowns
  - recruiter-friendly explanation strings

See [api-contract.md](api-contract.md) for the payload shapes.