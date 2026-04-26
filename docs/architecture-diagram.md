## Architecture diagram (Mermaid)

```mermaid
flowchart LR
  R[Recruiter] -->|Enters job description| FE[Frontend (Next.js UI)]

  FE -->|POST /api/run-pipeline\n(raw_jd, candidate_limit)| BE[Backend (FastAPI)]

  BE --> P[JD Parser\n(parse_jd)]
  P --> M[Matching engine\n(matcher scores candidates)]
  M -->|Reads candidates| DS[(Local dataset\nbackend/app/data/candidates.json)]

  M --> O[Outreach simulator\n(interest score + message/response)]
  O -->|May read sample JDs| JDS[(Local dataset\nbackend/app/data/sample_jds.json)]

  O --> K[Ranking/combiner\n(match×0.65 + interest×0.35)]
  K -->|Ranked shortlist + explainability| FE

  FE -->|Displays ranked shortlist| UI[Shortlist UI\n(table + candidate drawer)]
```

