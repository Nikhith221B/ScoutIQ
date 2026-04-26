# ScoutIQ: AI - Talent Scouting & Engagement Agent

## Overview

ScoutIQ: AI - Talent Scouting & Engagement Agent is a full‑stack, recruiter-facing demo app that turns a free‑form job description into a **ranked shortlist** of candidates with **transparent scoring** and **concise, recruiter-friendly explanations**.

- **Frontend**: Next.js 14 + Tailwind CSS (`frontend/`)
- **Backend**: FastAPI (`backend/`)
- **Data**: local JSON files (`backend/app/data/*.json`)

## Key features

- **End-to-end pipeline**: `POST /api/run-pipeline` parses JD → matches candidates → simulates outreach → ranks shortlist
- **Explainable scoring**:
  - Match breakdown (`matched_skills`, `missing_required_skills`, `match_score_breakdown`)
  - Interest breakdown (`interest_breakdown`, `interest_label`)
  - Recruiter-friendly summary (`recruiter_explanation`)
- **Deterministic demo behavior**: runs locally with no external services
- **Recruiter UI**: ranked shortlist table + candidate detail drawer

## Project Structure

```
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Configuration
│   │   └── data/     # JSON data files (candidates)
│   ├── requirements.txt
│   └── README.md
├── frontend/          # Next.js frontend
│   ├── app/          # Next.js app directory
│   ├── package.json
│   └── README.md
├── docs/              # Documentation
│   ├── architecture.md   # System architecture
│   ├── architecture-diagram.md # Mermaid architecture diagram
│   ├── scoring.md        # Scoring formulas
│   ├── api-contract.md   # API request/response shapes
│   └── demo-script.md    # Live demo run-through
└── README.md          # This file
```

## Architecture summary

High-level flow:

```
Recruiter (UI) → POST /api/run-pipeline → parse JD → match candidates (local JSON) → simulate outreach → combine scores → ranked shortlist (UI)
```

Docs:

- `docs/architecture.md`
- `docs/architecture-diagram.md`
- `docs/scoring.md`
- `docs/api-contract.md`

## Setup (local)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Screenshots

Optional. Screenshots are not required to run the project.

## Sample input/output

### Sample input (JD text)

Use any free-form JD. Example excerpt:

```text
Role: Full-Stack Engineer (React + FastAPI)
Required:
- React / TypeScript
- Python (FastAPI preferred)
- SQL (PostgreSQL)
Preferred:
- Docker
- AWS
Experience: 3-6 years
Location: Bengaluru (Hybrid)
```

### Sample API call

```bash
curl -X POST "http://localhost:8000/api/run-pipeline" ^
  -H "Content-Type: application/json" ^
  -d "{\"raw_jd\":\"Role: Full-Stack Engineer (React + FastAPI)\",\"candidate_limit\":20}"
```

### Sample output (shortened)

```json
{
  "status": "completed",
  "final_output": {
    "shortlist": [
      {
        "candidate_id": "1",
        "candidate_name": "…",
        "match_score": 78.5,
        "interest_score": 72,
        "combined_score": 76.23,
        "matched_skills": ["react", "typescript"],
        "missing_required_skills": ["sql"],
        "match_score_breakdown": { "skills_score": 80, "experience_score": 70, "role_score": 80 },
        "interest_label": "medium",
        "interest_breakdown": { "availability_score": 18, "role_fit_score": 16 },
        "recruiter_explanation": {
          "why_matched": "…",
          "missing_requirements": "…",
          "interest_signal": "…",
          "recommendation_summary": "…"
        }
      }
    ]
  }
}
```

Notes:

- **Combined score** uses the pipeline weights: \(match×0.65 + interest×0.35\).
- Full contract is documented in `docs/api-contract.md`.

## Demo Data

Demo data is stored locally:

- `backend/app/data/candidates.json`: used by matching + pipeline
- `backend/app/data/talents.json`: served by the `/api/talents` endpoint
- `backend/app/data/sample_jds.json`: used by outreach simulation when `job_id` is provided

## Environment Variables

See `.env.example` in both backend and frontend directories.

## Deployment (free + simple)

This project is split into two services.

### Backend (Render)

- Create a Render **Web Service** from this repo.
- **Root directory**: `backend`
- **Build command**: `pip install -r requirements.txt`
- **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- (Optional) Set `CORS_ALLOW_ORIGINS` if you want to lock CORS to specific domains.

### Frontend (Vercel)

- Import the same repo into Vercel.
- **Root directory**: `frontend`
- Set `NEXT_PUBLIC_API_URL` to your deployed Render backend URL (example: `https://your-backend.onrender.com`).

## Development

- Backend runs on: `http://localhost:8000`
- Frontend runs on: `http://localhost:3000`
- Frontend calls the backend directly via `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`)

## Future improvements (not implemented)

These are deliberate next steps, not current features:

- Replace rule-based JD parsing/matching with embeddings/LLM-assisted extraction
- Add persistent storage (DB) and an admin UI for managing candidate data
- Add authentication and multi-tenant org separation
- Add richer outreach workflows (follow-ups, sequencing, response states)
- Add evaluations/tests for scoring stability and regression checks

## Documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/architecture-diagram.md](docs/architecture-diagram.md)
- [docs/scoring.md](docs/scoring.md)
- [docs/api-contract.md](docs/api-contract.md)
- [docs/demo-script.md](docs/demo-script.md)

## License

MIT
