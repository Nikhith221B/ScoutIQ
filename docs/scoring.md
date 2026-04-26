# Scoring

This document describes the **implemented scoring logic** used by the pipeline (`POST /api/run-pipeline`). It is intentionally deterministic and explainable for demo/submission use.

## Overview

For each shortlisted candidate the pipeline returns:

- **Match score** (0–100): technical fit computed by the matcher service
- **Interest score** (0–100): deterministic outreach/interest score from the outreach simulator
- **Combined score** (0–100): weighted combination used for final ordering

Pipeline weights (source of truth: `backend/app/api/pipeline.py`):

\[
\text{Combined} = \text{Match}\times 0.65 + \text{Interest}\times 0.35
\]

## Match score (matcher service)

Source of truth: `backend/app/services/matcher.py`

The matcher computes per-dimension scores (each 0–100) and then a weighted total using:

```python
DEFAULT_WEIGHTS = {
  "skills": 0.35,
  "experience": 0.20,
  "seniority": 0.15,
  "role": 0.10,
  "location": 0.10,
  "domain": 0.10
}
```

### Dimensions returned (`score_breakdown`)

- `skills_score`
- `experience_score`
- `seniority_score`
- `role_score`
- `location_score`
- `domain_score`

### Skills scoring (what “matched/missing” means)

The skills dimension is based on:

- **Required skills**: exact match or alias match counts as matched
- **Preferred skills**: small bonus on top of required score

Implemented behavior:

- Required score: \(\frac{\#\text{matched required}}{\#\text{required}}\times 100\)
- Preferred bonus: `2 points per preferred hit`, capped at `+10`
- Final `skills_score` is capped at 100

Explainability fields returned for skills:

- `matched_skills`: required skills found on the candidate (after alias handling)
- `missing_required_skills`: required skills not found
- `preferred_skill_hits`: preferred skills found

## Interest score (outreach simulator)

Source of truth: `backend/app/services/outreach_simulator.py`

The outreach simulator computes **five factors**, each scored **0–20**, then sums them:

- `enthusiasm_score` (role alignment)
- `availability_score`
- `compensation_score`
- `role_fit_score` (skills overlap with job’s required/preferred skills when available)
- `response_positivity_score` (work preference alignment)

The simulator returns:

- `interest_score`: sum of the five factors (0–100)
- `interest_breakdown`: the five factor scores
- `interest_label`: `high` / `medium` / `low` based on thresholds in code
- `explanation`: a single sentence explanation string

## Combined score (pipeline)

Source of truth: `backend/app/api/pipeline.py`

For each shortlisted candidate:

- `combined_score = round(match_score * 0.65 + interest_score * 0.35, 2)`

## Explainability payload returned by the pipeline

Each item in `final_output.shortlist[]` includes:

- `match_score_breakdown`: the matcher’s dimension scores (see above)
- `interest_breakdown`, `interest_label`: outreach simulator outputs
- `match_explanation`, `interest_explanation`: existing short text strings
- `recruiter_explanation`: concise, recruiter-friendly strings grounded in breakdowns:
  - `why_matched`
  - `missing_requirements`
  - `interest_signal`
  - `recommendation_summary`