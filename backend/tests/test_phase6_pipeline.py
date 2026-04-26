from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


JD_TEXT = """
Senior Backend Engineer - TechCorp India

Location: Bangalore (Hybrid)
Experience: 4-6 years

Requirements:
- 4-6 years of experience in backend development
- Strong proficiency in Python (Django/FastAPI) or Java (Spring Boot)
- Experience with microservices architecture
- Knowledge of PostgreSQL, Redis, Kafka
- Experience with AWS/GCP cloud platforms
- Familiarity with Docker and Kubernetes
""".strip()


def test_run_pipeline_returns_top10_sorted_with_explanations_and_preview():
    resp = client.post(
        "/api/run-pipeline",
        json={
            "raw_jd": JD_TEXT,
            "company": "TechCorp India",
            "job_title": "Senior Backend Engineer",
            "candidate_limit": 20,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"

    final_output = body["final_output"]
    shortlist = final_output["shortlist"]

    # Top-10 shortlist enforced
    assert len(shortlist) <= 10

    # Sorted by combined_score desc
    combined_scores = [c["combined_score"] for c in shortlist]
    assert combined_scores == sorted(combined_scores, reverse=True)

    # Combined score formula + explainability fields presence
    for c in shortlist:
        match_score = c["match_score"]
        interest_score = c["interest_score"]
        expected = round(match_score * 0.65 + interest_score * 0.35, 2)
        assert c["combined_score"] == expected

        assert "match_explanation" in c and isinstance(c["match_explanation"], str) and c["match_explanation"].strip()
        assert "interest_explanation" in c and isinstance(c["interest_explanation"], str) and c["interest_explanation"].strip()
        assert "conversation_preview" in c and isinstance(c["conversation_preview"], str) and c["conversation_preview"].strip()

