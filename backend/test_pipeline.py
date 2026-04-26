from app.api.pipeline import run_pipeline, PipelineRequest

jd = '''
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

Compensation:
₹25L - ₹40L per annum
'''

request = PipelineRequest(
    raw_jd=jd,
    company='TechCorp India',
    job_title='Senior Backend Engineer',
    candidate_limit=20
)

if __name__ == "__main__":
    result = run_pipeline(request)
    print('Status:', result.status)
    for stage in result.stages:
        print(f"Stage: {stage['stage_name']} - Status: {stage['status']}")
        if stage.get('error'):
            print(f"  Error: {stage['error']}")