from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, talents, parse_jd, candidates, match, outreach, rank, pipeline, ingest
import os

app = FastAPI(
    title="AI-Powered Talent Scouting & Engagement Agent",
    description="Backend API for talent scouting and engagement",
    version="0.1.0"
)

# Configure CORS
cors_origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000")
cors_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]
# Allow Vercel preview/prod domains by default (override via env if needed)
cors_origin_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX", r"https://.*\.vercel\.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(talents.router, prefix="/api", tags=["talents"])
app.include_router(parse_jd.router, prefix="/api", tags=["parse-jd"])
app.include_router(candidates.router, prefix="/api", tags=["candidates"])
app.include_router(match.router, prefix="/api", tags=["match"])
app.include_router(outreach.router, prefix="/api", tags=["outreach"])
app.include_router(rank.router, prefix="/api", tags=["rank"])
app.include_router(pipeline.router, prefix="/api", tags=["pipeline"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])