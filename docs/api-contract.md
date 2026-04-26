## API contract (submission-focused)

This document captures the **actual request/response shapes** used by the frontend and implemented by the FastAPI backend.

### Base URL

- Backend: `http://localhost:8000`
- All routes are mounted under the `/api` prefix.

### `GET /api/health`

Response:

```json
{
  "status": "healthy",
  "service": "AI-Powered Talent Scouting & Engagement Agent",
  "version": "0.1.0"
}
```

### `POST /api/run-pipeline` (primary demo endpoint)

Used by: `frontend/app/page.tsx` via `frontend/app/api/client.ts`.

Request body:

```json
{
  "raw_jd": "string (required)",
  "company": "string | null (optional)",
  "job_title": "string | null (optional)",
  "candidates_override": "array<object> | null (optional)",
  "candidate_limit": 20
}
```

Response shape (high level):

```json
{
  "pipeline_id": "pipeline_<unix_ts>",
  "status": "completed | failed",
  "stages": [
    {
      "stage_name": "parse_jd | match_candidates | rank_shortlist | simulate_outreach | compile_output",
      "status": "completed | failed",
      "duration_ms": 123,
      "output": {},
      "error": "string (only when failed)"
    }
  ],
  "final_output": {
    "parsed_jd": {
      "title": "string",
      "company": "string | null",
      "required_skills": ["string"],
      "preferred_skills": ["string"],
      "experience_range": "string"
    },
    "shortlist": [
      {
        "candidate_id": "string",
        "candidate_name": "string",
        "candidate_title": "string",
        "location": "string | null",
        "skills": ["string"],

        "match_score": 0,
        "interest_score": 0,
        "combined_score": 0,

        "final_recommendation": "string",
        "match_explanation": "string",
        "interest_explanation": "string",
        "conversation_preview": "string",

        "matched_skills": ["string"],
        "missing_required_skills": ["string"],
        "match_score_breakdown": {
          "skills_score": 0,
          "experience_score": 0,
          "seniority_score": 0,
          "role_score": 0,
          "location_score": 0,
          "domain_score": 0
        },

        "interest_breakdown": {
          "enthusiasm_score": 0,
          "availability_score": 0,
          "compensation_score": 0,
          "role_fit_score": 0,
          "response_positivity_score": 0
        },
        "interest_label": "high | medium | low",

        "recruiter_explanation": {
          "why_matched": "string",
          "missing_requirements": "string",
          "interest_signal": "string",
          "recommendation_summary": "string"
        },

        "outreach_message": "string | null",
        "candidate_response": "string | null"
      }
    ],
    "scoring_weights": {
      "match_score_weight": 0.65,
      "interest_score_weight": 0.35
    }
  },
  "total_duration_ms": 1234,
  "started_at": "ISO datetime",
  "completed_at": "ISO datetime"
}
```

Notes:

- The pipeline returns **top 10** candidates in `final_output.shortlist`.
- `match_score_breakdown` is sourced from the matcher service output (`score_breakdown`).
- `interest_breakdown` / `interest_label` are sourced from the outreach simulator output.

### Other implemented endpoints (used for debugging / exploration)

- `POST /api/parse-jd`: parse free-form JD to structured fields
- `POST /api/match-candidates`: compute match scores + breakdowns for candidates
- `POST /api/simulate-outreach`: generate outreach + interest score breakdown
- `POST /api/rank-shortlist`: rank matched candidates (standalone)
- `POST /api/ingest-candidates/file`: upload CSV/JSON and get normalized candidate objects
- `POST /api/ingest-candidates/file`: upload PDF resume and get a single candidate object (text-based PDFs)
- `POST /api/ingest-candidates/resume`: paste resume text and get a single candidate object
- `GET /api/candidates` and `GET /api/candidates/{id}`: candidate dataset access
- `GET /api/talents` and `GET /api/talents/{id}`: demo “talents” dataset access

