## Demo script (5–7 minutes)

This is a practical run-through using the repo as-is (local JSON data, no external services).

### 0) Start the services

- **Backend** (FastAPI):
  - From `backend/`, install dependencies and start the server on port 8000.
  - Confirm it’s up via `GET /api/health`.

- **Frontend** (Next.js):
  - From `frontend/`, install dependencies and run the dev server on port 3000.

### 1) Run the full pipeline from the UI

1. Open the frontend in the browser.
2. In **Recruiter Dashboard**, select one of the built-in sample JDs (e.g. “Full‑Stack (React + FastAPI)”).
3. Click **Run pipeline**.
4. Point out the **Pipeline stages** list:
   - `parse_jd`
   - `match_candidates`
   - `rank_shortlist`
   - `simulate_outreach`

### 2) Review the ranked shortlist

1. In **Ranked shortlist**, point out:
   - `Match`, `Interest`, and `Combined` scores
   - the pipeline weights: `0.65` match / `0.35` interest
2. Click the top candidate row to open the candidate drawer.

### 3) Explainability (grounded in breakdowns)

In the candidate drawer, highlight:

- **Skills matched** and **Missing required skills**
  - Directly sourced from the matcher output (`matched_skills`, `missing_required_skills`)
- **Score breakdown**
  - Shows match vs interest and the combined formula
  - Includes match dimension breakdown (`match_score_breakdown`)
- **Outreach**
  - Shows the generated outreach message and simulated candidate response
- **Recruiter-friendly summary**
  - **Why matched**: derived from matched required skills and strongest match dimensions
  - **Missing**: derived from missing required skills
  - **Interest**: derived from `interest_label` + top interest breakdown signals
  - **Summary**: includes the final recommendation and the combined-score calculation

### 4) Optional: show the raw API response

Use browser devtools or an API client to call:

- `POST /api/run-pipeline` with the same JD text

Then show that the same fields rendered in the UI exist in `final_output.shortlist[]`.

### 5) Close

Summarize the value:

- One endpoint (`/api/run-pipeline`) returns a shortlist with **transparent scoring** and **human-readable explainability**
- Deterministic demo behavior (local JSON + deterministic interest scoring)

