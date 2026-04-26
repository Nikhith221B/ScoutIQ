"""
API route for parsing job descriptions.
POST /api/parse-jd
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import JobDescriptionInput, ParsedJD
from app.services.jd_parser import parse_jd as service_parse_jd, to_dict
from typing import List
import re
from datetime import datetime

router = APIRouter()


# Common skills database for parsing
COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "node.js", "django", "flask", "fastapi", "spring", "golang", "rust", "c++",
    "c#", ".net", "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "machine learning", "deep learning", "tensorflow", "pytorch", "nlp",
    "data science", "data analysis", "data engineering", "etl", "spark",
    "hadoop", "hive", "kafka", "airflow", "tableau", "power bi",
    "agile", "scrum", "jira", "git", "ci/cd", "rest api", "graphql",
    "leadership", "team management", "project management", "product management"
]


@router.post("/parse-jd", response_model=ParsedJD)
def parse_jd(input: JobDescriptionInput):
    """
    Parse a job description and extract structured requirements.
    Uses the rule-based JD parser service.
    """
    # Use the new service for parsing
    parsed_result = service_parse_jd(input.raw_text)
    parsed_dict = to_dict(parsed_result)
    
    # Map to the existing ParsedJD schema
    parsed = ParsedJD(
        raw_text=input.raw_text,
        title=parsed_dict.get("role_title", input.title or "Software Engineer"),
        company=input.company,
        required_skills=parsed_dict.get("required_skills", []),
        preferred_skills=parsed_dict.get("preferred_skills", []),
        experience_min=parsed_dict.get("minimum_experience"),
        experience_max=None,
        location=parsed_dict.get("location"),
        remote_policy=parsed_dict.get("work_mode"),
        salary_min=None,
        salary_max=None,
        job_type="full-time",
        description=input.raw_text[:500] if input.raw_text else None,
        responsibilities=parsed_dict.get("responsibilities", []),
        requirements=parsed_dict.get("required_skills", []),
        nice_to_have=parsed_dict.get("preferred_skills", []),
        parsed_at=datetime.utcnow()
    )
    
    return parsed