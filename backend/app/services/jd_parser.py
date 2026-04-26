"""
JD Parser Service - Rule-based job description parser for MVP.

Provides structured parsing of raw job description text into:
- role_title
- required_skills
- preferred_skills
- minimum_experience
- seniority
- location
- work_mode
- domain
- keywords
- responsibilities
"""
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


# =============================================================================
# Skill Databases
# =============================================================================

TECHNICAL_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab",
    
    # Web Frameworks
    "react", "angular", "vue", "django", "flask", "fastapi", "spring",
    "express", "next.js", "nuxt", "svelte", "node.js", "nodejs",
    
    # Databases
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "oracle", "sqlite", "cassandra", "dynamodb", "firebase",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform",
    "jenkins", "gitlab", "github actions", "circleci", "ansible",
    
    # Data & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "nlp", "natural language processing", "computer vision",
    "data science", "data analysis", "data engineering", "etl",
    "spark", "hadoop", "hive", "kafka", "airflow", "tableau", "power bi",
    
    # Other Tech
    "rest api", "graphql", "microservices", "graphql", "ci/cd", "agile", "scrum"
}

DOMAIN_KEYWORDS = {
    "fintech": ["fintech", "financial", "banking", "payment", "investment", "trading"],
    "healthcare": ["healthcare", "health", "medical", "hospital", "pharma", "biotech"],
    "e-commerce": ["e-commerce", "ecommerce", "retail", "shopping", "marketplace"],
    "edtech": ["edtech", "education", "learning", "elearning", "online learning"],
    "saas": ["saas", "software as a service", "b2b", "enterprise"],
    "logistics": ["logistics", "supply chain", "delivery", "transportation"],
    "ai/ml": ["artificial intelligence", "ai", "ml", "machine learning", "deep learning"]
}

SENIORITY_KEYWORDS = {
    "entry": ["entry level", "fresher", "graduate", "junior", "trainee", "intern"],
    "mid": ["mid-level", "2-4 years", "3-5 years", "software engineer", "developer"],
    "senior": ["senior", "5+ years", "6+ years", "7+ years", "staff engineer"],
    "lead": ["lead", "principal", "architect", "head of", "manager"],
    "director": ["director", "vp", "vice president", "chief", "head"]
}

LOCATION_KEYWORDS = {
    "bangalore": ["bangalore", "bengaluru", "bangalore"],
    "hyderabad": ["hyderabad", "secunderabad"],
    "mumbai": ["mumbai", "bombay"],
    "pune": ["pune"],
    "chennai": ["chennai", "madras"],
    "delhi": ["delhi", "ncr", "gurgaon", "gurugram", "noida"],
    "kolkata": ["kolkata", "calcutta"]
}

WORK_MODE_KEYWORDS = {
    "remote": ["remote", "work from home", "wfh", "from home"],
    "hybrid": ["hybrid", "flexible", "3 days", "2 days", "partial remote"],
    "onsite": ["onsite", "on-site", "in office", "in-office", "office based"]
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ParsedJDResult:
    """Structured output for parsed job description."""
    role_title: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    minimum_experience: Optional[int] = None
    seniority: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    domain: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)


# =============================================================================
# Core Parser Functions
# =============================================================================

def parse_jd(raw_text: str) -> ParsedJDResult:
    """
    Main entry point for parsing a job description.
    
    Args:
        raw_text: Raw job description text
        
    Returns:
        ParsedJDResult with structured fields
    """
    text_lower = raw_text.lower()
    
    # Extract all components
    role = _extract_role_title(raw_text)
    required = _extract_required_skills(text_lower)
    preferred = _extract_preferred_skills(text_lower, required)
    experience = _extract_experience(text_lower)
    seniority = _extract_seniority(text_lower)
    location = _extract_location(text_lower)
    work_mode = _extract_work_mode(text_lower)
    domain = _extract_domain(text_lower)
    keywords = _extract_keywords(text_lower)
    responsibilities = _extract_responsibilities(raw_text)
    
    return ParsedJDResult(
        role_title=role,
        required_skills=required,
        preferred_skills=preferred,
        minimum_experience=experience,
        seniority=seniority,
        location=location,
        work_mode=work_mode,
        domain=domain,
        keywords=keywords,
        responsibilities=responsibilities
    )


def _extract_role_title(text: str) -> str:
    """Extract job title from JD text."""
    # Common title patterns
    title_patterns = [
        r'(?:role|position|job title|designation)[:\s]*([^\n]+)',
        r'^([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Manager|Lead|Architect|Analyst))',
        r'(?:we are looking for|hiring|seeking)\s+(?:a|an)?\s*([^\n]+)',
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            if len(title) > 3 and len(title) < 100:
                return title.title()
    
    # Fallback: first non-empty line that's likely a title
    lines = text.split('\n')
    for line in lines[:5]:
        cleaned = line.strip()
        if 5 < len(cleaned) < 80 and not cleaned.endswith('.'):
            return cleaned.title()
    
    return "Software Engineer"


def _extract_required_skills(text: str) -> List[str]:
    """Extract required skills from JD text."""
    skills = []
    text_lower = text.lower()
    
    # Check for explicit required section
    required_section = _extract_section(text, "required", "preferred")
    
    for skill in TECHNICAL_SKILLS:
        if _contains_skill(text_lower, skill):
            # Check if in required section or has explicit required markers
            is_required = False
            
            if required_section and _contains_skill(required_section.lower(), skill):
                is_required = True
            elif _has_required_marker(text, skill):
                is_required = True
            # If no explicit section, add any found skill as required for MVP
            elif not required_section:
                is_required = True
                
            if is_required and skill not in skills:
                skills.append(skill)
    
    return skills[:10]  # Limit to top 10


def _extract_preferred_skills(text: str, required_skills: List[str]) -> List[str]:
    """Extract preferred/nice-to-have skills."""
    preferred = []
    text_lower = text.lower()
    
    # Extract preferred section if exists
    preferred_section = _extract_section(text, "preferred", "nice")
    
    for skill in TECHNICAL_SKILLS:
        if _contains_skill(text_lower, skill) and skill not in required_skills:
            if preferred_section and _contains_skill(preferred_section.lower(), skill):
                if skill not in preferred:
                    preferred.append(skill)
            elif "nice to have" in text_lower or "plus" in text_lower:
                if skill not in preferred:
                    preferred.append(skill)
    
    return preferred[:5]


def _extract_experience(text: str) -> Optional[int]:
    """Extract minimum years of experience."""
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
        r'(\d+)\s*-\s*\d+\s*(?:years?|yrs?)',
        r'minimum\s*(\d+)\s*(?:years?|yrs?)',
        r'at least\s*(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\s*years?\s+of\s+relevant\s+experience',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return None


def _extract_seniority(text: str) -> Optional[str]:
    """Detect seniority level from JD text."""
    for level, keywords in SENIORITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return level
    return None


def _extract_location(text: str) -> Optional[str]:
    """Extract location from JD text."""
    for city, keywords in LOCATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return city.title()
    return None


def _extract_work_mode(text: str) -> Optional[str]:
    """Extract work mode (remote/hybrid/onsite)."""
    for mode, keywords in WORK_MODE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return mode
    return None


def _extract_domain(text: str) -> Optional[str]:
    """Detect industry/domain from JD text."""
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return domain
    return None


def _extract_keywords(text: str) -> List[str]:
    """Extract additional keywords from JD."""
    keywords = []
    
    # Add all matched technical skills
    for skill in TECHNICAL_SKILLS:
        if _contains_skill(text, skill):
            keywords.append(skill)
    
    # Add domain if found
    for domain in DOMAIN_KEYWORDS:
        if domain in text:
            keywords.append(domain)
    
    return list(set(keywords))[:15]


def _extract_responsibilities(text: str) -> List[str]:
    """Extract responsibilities from JD text."""
    responsibilities = []
    
    # Find responsibilities section
    resp_section = _extract_section(text, "responsibilit", "requirement")
    
    if resp_section:
        lines = resp_section.split('\n')
        for line in lines:
            cleaned = line.strip()
            # Filter to meaningful bullet points
            if len(cleaned) > 20 and len(cleaned) < 200:
                # Clean up bullet points
                cleaned = re.sub(r'^[\-\*\•\d\.]+\s*', '', cleaned)
                if cleaned and not cleaned.startswith('http'):
                    responsibilities.append(cleaned)
    
    return responsibilities[:5] if responsibilities else _default_responsibilities()


# =============================================================================
# Helper Functions
# =============================================================================

def _extract_section(text: str, start_marker: str, end_marker: str) -> Optional[str]:
    """Extract a section between two markers."""
    pattern = rf'{start_marker}[:\s]*(.*?)(?:{end_marker}|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1)
    return None


def _contains_skill(text_lower: str, skill: str) -> bool:
    """
    Skill presence check with boundaries.

    This prevents false positives for short skills like "r" matching inside words.
    """
    if not text_lower or not skill:
        return False
    s = skill.lower().strip()
    if not s:
        return False
    escaped = re.escape(s)
    # Treat these as "skill token characters" (matches resume extraction approach)
    return re.search(rf"(^|[^a-z0-9\+#\.]){escaped}([^a-z0-9\+#\.]|$)", text_lower) is not None


def _has_required_marker(text: str, skill: str) -> bool:
    """Check if a skill has required markers nearby."""
    # Look for skill within context of required keywords
    patterns = [
        rf'{re.escape(skill)}[\s:]*(?:required|must have|essential|mandatory)',
        rf'(?:required|must have|essential)[\s:]*.{0,50}{re.escape(skill)}',
    ]
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def _default_responsibilities() -> List[str]:
    """Return default responsibilities when none can be extracted."""
    return [
        "Design and develop scalable software solutions",
        "Collaborate with cross-functional teams",
        "Write clean, maintainable code",
        "Participate in code reviews",
        "Mentor junior team members"
    ]


def to_dict(result: ParsedJDResult) -> Dict[str, Any]:
    """Convert ParsedJDResult to dictionary."""
    return {
        "role_title": result.role_title,
        "required_skills": result.required_skills,
        "preferred_skills": result.preferred_skills,
        "minimum_experience": result.minimum_experience,
        "seniority": result.seniority,
        "location": result.location,
        "work_mode": result.work_mode,
        "domain": result.domain,
        "keywords": result.keywords,
        "responsibilities": result.responsibilities
    }