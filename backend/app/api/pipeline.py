"""
API route for running the full pipeline.
POST /api/run-pipeline
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()


class PipelineRequest(BaseModel):
    """Request schema for running the full pipeline"""
    raw_jd: str = Field(..., description="Raw job description text")
    company: Optional[str] = Field(None, description="Company name")
    job_title: Optional[str] = Field(None, description="Job title")
    candidate_limit: int = Field(20, description="Maximum candidates to process")
    candidates_override: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Optional candidate list to use instead of the local JSON dataset",
    )


class PipelineStage(BaseModel):
    """Information about each pipeline stage"""
    stage_name: str
    status: str
    duration_ms: int
    output: Optional[dict] = None
    error: Optional[str] = None


class PipelineResponse(BaseModel):
    """Response schema for run-pipeline"""
    pipeline_id: str
    status: str
    stages: List[dict]
    final_output: dict
    total_duration_ms: int
    started_at: str
    completed_at: str


@router.post("/run-pipeline", response_model=PipelineResponse)
def run_pipeline(request: PipelineRequest):
    """
    Run the complete talent scouting pipeline:
    1. Parse JD
    2. Match Candidates
    3. Simulate Outreach
    4. Rank & Shortlist
    
    Returns results from all stages.
    """
    import time
    start_time = time.time()
    
    stages = []
    pipeline_id = f"pipeline_{int(datetime.utcnow().timestamp())}"
    
    # Stage 1: Parse JD
    stage_start = time.time()
    try:
        from app.api.parse_jd import parse_jd
        from app.models.schemas import JobDescriptionInput
        
        jd_input = JobDescriptionInput(
            raw_text=request.raw_jd,
            company=request.company,
            title=request.job_title
        )
        parsed_jd = parse_jd(jd_input)
        
        stages.append({
            "stage_name": "parse_jd",
            "status": "completed",
            "duration_ms": int((time.time() - stage_start) * 1000),
            "output": {
                "title": parsed_jd.title,
                "company": parsed_jd.company,
                "required_skills": parsed_jd.required_skills,
                "preferred_skills": parsed_jd.preferred_skills,
                "experience_min": parsed_jd.experience_min,
                "experience_max": parsed_jd.experience_max,
                "location": parsed_jd.location,
                "remote_policy": parsed_jd.remote_policy
            }
        })
    except Exception as e:
        stages.append({
            "stage_name": "parse_jd",
            "status": "failed",
            "duration_ms": int((time.time() - stage_start) * 1000),
            "error": str(e)
        })
        return PipelineResponse(
            pipeline_id=pipeline_id,
            status="failed",
            stages=stages,
            final_output={},
            total_duration_ms=int((time.time() - start_time) * 1000),
            started_at=datetime.utcnow().isoformat(),
            completed_at=datetime.utcnow().isoformat()
        )
    
    # Stage 2: Match Candidates
    stage_start = time.time()
    try:
        from app.api.match import match_candidates_endpoint, MatchRequest
        
        match_request = MatchRequest(
            parsed_jd=parsed_jd.dict(),
            candidates_override=request.candidates_override,
            limit=request.candidate_limit
        )
        match_result = match_candidates_endpoint(match_request)
        
        stages.append({
            "stage_name": "match_candidates",
            "status": "completed",
            "duration_ms": int((time.time() - stage_start) * 1000),
            "output": {
                "total_candidates": match_result.total_candidates,
                "matched_candidates": len(match_result.matched_candidates)
            }
        })
    except Exception as e:
        stages.append({
            "stage_name": "match_candidates",
            "status": "failed",
            "duration_ms": int((time.time() - stage_start) * 1000),
            "error": str(e)
        })
        return PipelineResponse(
            pipeline_id=pipeline_id,
            status="failed",
            stages=stages,
            final_output={},
            total_duration_ms=int((time.time() - start_time) * 1000),
            started_at=datetime.utcnow().isoformat(),
            completed_at=datetime.utcnow().isoformat()
        )
    
    # Stage 3: Rank & Shortlist (select top 10 by match score)
    stage_start = time.time()
    rank_result = None
    try:
        from app.api.rank import rank_shortlist, RankRequest
        
        # Use weights 0.65/0.35 as specified
        rank_request = RankRequest(
            matched_candidates=match_result.matched_candidates,
            weights={"match_score_weight": 0.65, "interest_score_weight": 0.35}
        )
        rank_result = rank_shortlist(rank_request)
        
        stages.append({
            "stage_name": "rank_shortlist",
            "status": "completed",
            "duration_ms": int((time.time() - stage_start) * 1000),
            "output": {
                "total_candidates": rank_result.total_candidates,
                "shortlist_size": len(rank_result.shortlist),
                "top_candidate": rank_result.top_candidate.get("name") if rank_result.top_candidate else None
            }
        })
    except Exception as e:
        stages.append({
            "stage_name": "rank_shortlist",
            "status": "failed",
            "duration_ms": int((time.time() - stage_start) * 1000),
            "error": str(e)
        })
    
    # Stage 4: Simulate Outreach (for top 10 by match score)
    stage_start = time.time()
    outreach_result = None
    top_10_by_match = []
    try:
        from app.api.outreach import simulate_outreach, OutreachRequest
        
        # Select top 10 by match score for outreach
        top_10_by_match = sorted(match_result.matched_candidates, key=lambda x: x.get("match_score", 0), reverse=True)[:10]
        top_10_ids = [c["candidate_id"] for c in top_10_by_match]
        
        outreach_request = OutreachRequest(
            candidate_ids=top_10_ids,
            candidates_override=request.candidates_override,
            job_title=parsed_jd.title,
            company=request.company or "Company",
            job_description=request.raw_jd,
            message_tone="professional"
        )
        outreach_result = simulate_outreach(outreach_request)
        
        stages.append({
            "stage_name": "simulate_outreach",
            "status": "completed",
            "duration_ms": int((time.time() - stage_start) * 1000),
            "output": {
                "messages_generated": len(outreach_result.results)
            }
        })
    except Exception as e:
        stages.append({
            "stage_name": "simulate_outreach",
            "status": "failed",
            "duration_ms": int((time.time() - stage_start) * 1000),
            "error": str(e)
        })
    
    # Compile final output with combined scores
    # Create a lookup for outreach results (default to empty if failed)
    outreach_lookup = {}
    if outreach_result and hasattr(outreach_result, 'results'):
        outreach_lookup = {r["candidate_id"]: r for r in outreach_result.results}

    # Create a lookup for match details so the frontend can show explainability
    # (skills matched / missing skills / score breakdown). This does not change
    # pipeline scoring; it only exposes already-computed stage outputs.
    match_lookup = {}
    try:
        if match_result and hasattr(match_result, "matched_candidates"):
            match_lookup = {c.get("candidate_id"): c for c in match_result.matched_candidates}
    except Exception:
        match_lookup = {}
    
    # Build final shortlist with combined scores
    final_shortlist = []
    if not rank_result:
        stages.append({
            "stage_name": "compile_output",
            "status": "failed",
            "error": "Rank stage failed, cannot compile output"
        })
    else:
        def _safe_list(v: Any) -> List[str]:
            return [x for x in v if isinstance(x, str)] if isinstance(v, list) else []

        def _safe_num(v: Any) -> float:
            try:
                return float(v)
            except Exception:
                return 0.0

        def _top_match_dimensions(score_breakdown: Dict[str, Any], top_n: int = 2) -> List[str]:
            if not isinstance(score_breakdown, dict):
                return []
            dims = []
            for k, v in score_breakdown.items():
                if isinstance(k, str) and k.endswith("_score"):
                    dims.append((k.replace("_score", "").replace("_", " "), _safe_num(v)))
            dims.sort(key=lambda x: x[1], reverse=True)
            return [f"{name} {val:.0f}/100" for name, val in dims[:top_n] if val > 0]

        def _top_interest_signals(interest_breakdown: Dict[str, Any], top_n: int = 2) -> List[str]:
            if not isinstance(interest_breakdown, dict):
                return []
            label_map = {
                "enthusiasm_score": "role alignment",
                "availability_score": "availability",
                "compensation_score": "compensation",
                "role_fit_score": "skills fit",
                "response_positivity_score": "work preference",
            }
            items = []
            for k, v in interest_breakdown.items():
                if not isinstance(k, str):
                    continue
                items.append((label_map.get(k, k.replace("_", " ")), _safe_num(v)))
            items.sort(key=lambda x: x[1], reverse=True)
            return [f"{name} {val:.0f}/20" for name, val in items[:top_n] if val > 0]

        for candidate in rank_result.shortlist:
            candidate_id = candidate.get("candidate_id")
            outreach_data = outreach_lookup.get(candidate_id, {})
            match_data = match_lookup.get(candidate_id, {})
            
            # Get interest score from outreach (or use existing interest_score)
            interest_score = outreach_data.get("interest_score", candidate.get("interest_score", 0))
            match_score = candidate.get("match_score", 0)
            
            # Compute combined score: match_score * 0.65 + interest_score * 0.35
            combined_score = round(match_score * 0.65 + interest_score * 0.35, 2)
            
            # Build match explanation
            match_explanation = f"Match score of {match_score}% based on skill alignment and experience fit."
            if candidate.get("strengths"):
                match_explanation += f" Strengths: {', '.join(candidate['strengths'])}."
            
            # Build interest explanation
            interest_explanation = outreach_data.get(
                "explanation",
                f"Interest score of {interest_score}/100 based on overall fit."
            )
            
            # Generate final recommendation
            if combined_score >= 80:
                final_recommendation = "Strong recommend - high match and high interest"
            elif combined_score >= 65:
                final_recommendation = "Recommend - good match and interest"
            elif combined_score >= 50:
                final_recommendation = "Consider - moderate fit"
            else:
                final_recommendation = "Not recommended - below threshold"
            
            # Build conversation preview
            conversation_preview = (
                f"Recruiter: {outreach_data.get('outreach_message', 'Outreach message generated')[:200]}... | "
                f"Candidate: {outreach_data.get('candidate_response', 'Response pending')[:150]}..."
            )

            # Phase 8: recruiter-friendly explainability (grounded in breakdowns)
            matched_skills = _safe_list(match_data.get("matched_skills", []))
            missing_required = _safe_list(match_data.get("missing_required_skills", []))
            match_dims = _top_match_dimensions(match_data.get("score_breakdown", {}), top_n=2)

            interest_label = outreach_data.get("interest_label")
            interest_breakdown = outreach_data.get("interest_breakdown", {})
            interest_signals = _top_interest_signals(interest_breakdown, top_n=2)

            why_matched = "Matched on core requirements."
            if matched_skills:
                why_matched = f"Matched {len(matched_skills)} required skill(s): {', '.join(matched_skills[:3])}."
            if match_dims:
                why_matched = f"{why_matched} Strongest dimensions: {', '.join(match_dims)}."

            missing_text = "No major missing required skills detected."
            if missing_required:
                missing_text = f"Missing required: {', '.join(missing_required[:3])}."
                if len(missing_required) > 3:
                    missing_text = f"{missing_text} (+{len(missing_required) - 3} more)"

            interest_preface = f"Interest looks {interest_label or 'unknown'} ({int(_safe_num(interest_score))}/100)."
            if interest_label == "high":
                interest_preface = f"Likely interested ({int(_safe_num(interest_score))}/100)."
            elif interest_label == "low":
                interest_preface = f"May be less interested ({int(_safe_num(interest_score))}/100)."

            interest_text = interest_preface
            if interest_signals:
                interest_text = f"{interest_text} Top signals: {', '.join(interest_signals)}."

            # Keep this grounded: mention combined and the weighting used
            recommendation_summary = (
                f"{final_recommendation}. Combined {combined_score:.2f} = "
                f"{match_score:.0f}×0.65 + {int(_safe_num(interest_score))}×0.35."
            )
            
            final_shortlist.append({
                "candidate_id": candidate_id,
                "candidate_name": candidate.get("name"),
                "candidate_title": candidate.get("title"),
                "location": candidate.get("location"),
                "skills": match_data.get("skills", candidate.get("skills", [])),
                "match_score": match_score,
                "interest_score": interest_score,
                "combined_score": combined_score,
                "match_explanation": match_explanation,
                "interest_explanation": interest_explanation,
                "final_recommendation": final_recommendation,
                "conversation_preview": conversation_preview,
                # Additional detail fields for the Phase 7 frontend (non-breaking additions)
                "matched_skills": match_data.get("matched_skills", []),
                "missing_required_skills": match_data.get("missing_required_skills", []),
                "match_score_breakdown": match_data.get("score_breakdown", {}),
                "interest_breakdown": outreach_data.get("interest_breakdown", {}),
                "interest_label": outreach_data.get("interest_label"),
                "recruiter_explanation": {
                    "why_matched": why_matched,
                    "missing_requirements": missing_text,
                    "interest_signal": interest_text,
                    "recommendation_summary": recommendation_summary,
                },
                "outreach_message": outreach_data.get("outreach_message"),
                "candidate_response": outreach_data.get("candidate_response"),
            })
    
    # Sort by combined score descending
    final_shortlist.sort(key=lambda x: x["combined_score"], reverse=True)
    # Enforce top 10 shortlist
    final_shortlist = final_shortlist[:10]
    
    # Compile final output
    final_output = {
        "parsed_jd": {
            "title": parsed_jd.title,
            "company": parsed_jd.company,
            "required_skills": parsed_jd.required_skills,
            "preferred_skills": parsed_jd.preferred_skills,
            "experience_range": f"{parsed_jd.experience_min or 'Not specified'}-{parsed_jd.experience_max or 'Not specified'} years"
        },
        "matching": {
            "total_candidates_matched": len(match_result.matched_candidates),
            "top_matches": [
                {"name": c["name"], "score": c["match_score"]}
                for c in match_result.matched_candidates[:5]
            ]
        },
        "outreach": {
            "candidates_contacted": len(outreach_lookup),
            "top_10_by_match": [c["candidate_id"] for c in top_10_by_match]
        },
        "shortlist": final_shortlist,
        "scoring_weights": {
            "match_score_weight": 0.65,
            "interest_score_weight": 0.35
        }
    }
    
    return PipelineResponse(
        pipeline_id=pipeline_id,
        status="completed",
        stages=stages,
        final_output=final_output,
        total_duration_ms=int((time.time() - start_time) * 1000),
        started_at=datetime.utcnow().isoformat(),
        completed_at=datetime.utcnow().isoformat()
    )