"""
Outreach Simulator Service
Generates recruiter outreach messages, simulated candidate responses,
and calculates interest scores based on various factors.
"""
import hashlib
from typing import Dict, List, Any
from datetime import datetime


def _deterministic_hash(seed: str) -> int:
    """Generate a deterministic hash for consistent demo results."""
    return int(hashlib.md5(seed.encode()).hexdigest()[:8], 16) % 100


def _score_from_hash(base: int, hash_val: int, max_score: int) -> int:
    """Map hash value to a score range deterministically."""
    return base + (hash_val % (max_score - base + 1))


class OutreachSimulator:
    """Simulates recruiter-candidate outreach interactions."""
    
    # Tone templates for outreach messages
    OUTREACH_TEMPLATES = {
        "professional": {
            "subject": "Opportunity at {company} - {title} Role",
            "opening": "I hope this email finds you well.",
            "pitch": "We have an exciting opportunity for a {title} position at {company}.",
            "closing": "Would you be interested in exploring this opportunity?"
        },
        "friendly": {
            "subject": "Exciting {title} role at {company}!",
            "opening": "Hope you're doing great!",
            "pitch": "We're looking for awesome talent for a {title} role at {company}.",
            "closing": "Would you like to chat more about it?"
        },
        "casual": {
            "subject": "{title} role at {company} - interested?",
            "opening": "Hey!",
            "pitch": "Got a {title} position at {company} that might interest you.",
            "closing": "Let me know if you want to hear more!"
        }
    }
    
    # Candidate response templates based on interest level
    RESPONSE_TEMPLATES = {
        "high": [
            "Thank you for reaching out! This sounds like an amazing opportunity. I'm definitely interested and would love to learn more about the role and the team.",
            "This looks great! I've been looking for something exactly like this. When can we schedule a call to discuss the details?",
            "I'm very interested! The role aligns perfectly with my career goals. Please share more details about the position."
        ],
        "medium": [
            "Thanks for the outreach! This sounds interesting. Could you share more details about the role and the team culture?",
            "I appreciate you reaching out. I'm open to exploring this opportunity. What are the next steps?",
            "Interesting! I'd like to know more about the position before deciding. Can we schedule a quick call?"
        ],
        "low": [
            "Thanks for thinking of me, but I'm not looking to make a change right now. Best of luck with the search!",
            "I appreciate the opportunity, but my current situation is working well for me. Perhaps another time.",
            "Thanks for reaching out. I'm currently focused on my present role, but I'll keep this in mind for the future."
        ]
    }
    
    def __init__(self):
        self.default_tone = "professional"
    
    def generate_outreach_message(
        self,
        candidate_name: str,
        job_title: str,
        company: str,
        job_description: str,
        candidate_skills: List[str],
        tone: str = "professional"
    ) -> str:
        """Generate a personalized recruiter outreach message."""
        template = self.OUTREACH_TEMPLATES.get(tone, self.OUTREACH_TEMPLATES["professional"])
        
        # Extract key skills to mention
        skills_mention = ", ".join(candidate_skills[:3]) if candidate_skills else "your expertise"
        
        message = f"""Subject: {template['subject'].format(company=company, title=job_title)}

Dear {candidate_name},

{template['opening']} I am reaching out regarding an exciting opportunity at {company} for the position of {job_title}.

Based on your impressive background in {skills_mention}, we believe you could be a great fit for this role. {job_description[:200]}...

{template['pitch'].format(company=company, title=job_title)}

The position offers:
- Competitive compensation
- {'Hybrid' if 'hybrid' in job_description.lower() else 'Flexible'} work arrangement
- Opportunity to work on cutting-edge projects

{template['closing']}

Best regards,
Recruiter Team"""
        
        return message
    
    def generate_candidate_response(
        self,
        candidate_name: str,
        interest_level: str
    ) -> str:
        """Generate a simulated candidate response based on interest level."""
        import random
        # Use deterministic seed for consistency
        seed = f"{candidate_name}_{interest_level}"
        random.seed(_deterministic_hash(seed))
        
        templates = self.RESPONSE_TEMPLATES.get(interest_level, self.RESPONSE_TEMPLATES["medium"])
        response = random.choice(templates)
        
        # Reset random seed
        random.seed(None)
        
        return response
    
    def calculate_interest_score(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate interest score based on multiple factors.
        Uses deterministic hashing for consistent demo results.
        """
        # Create deterministic seed from candidate and job IDs
        seed = f"{candidate.get('id', 'unknown')}_{job.get('id', 'unknown')}"
        hash_val = _deterministic_hash(seed)
        
        # Factor 1: Enthusiasm for role (0-20 points)
        desired_roles = candidate.get("desired_roles", [])
        job_title = job.get("title", "").lower()
        role_match_enthusiasm = 0
        
        for role in desired_roles:
            if role.lower() in job_title or job_title in role.lower():
                role_match_enthusiasm = 20
                break
        if role_match_enthusiasm == 0:
            role_match_enthusiasm = _score_from_hash(10, hash_val + 1, 20)
        
        # Factor 2: Availability (0-20 points)
        availability = candidate.get("availability", "").lower()
        if "immediate" in availability or "1 week" in availability:
            availability_score = 20
        elif "2 weeks" in availability:
            availability_score = 18
        elif "3 weeks" in availability or "1 month" in availability:
            availability_score = 14
        elif "2 months" in availability:
            availability_score = 10
        else:
            availability_score = _score_from_hash(8, hash_val + 2, 20)
        
        # Factor 3: Compensation alignment (0-20 points)
        candidate_salary = candidate.get("compensation_expectation", 0)
        job_salary_min = job.get("salary_min", 0)
        job_salary_max = job.get("salary_max", 0)
        
        if job_salary_min > 0 and job_salary_max > 0:
            if candidate_salary <= job_salary_max:
                alignment = min(20, int(20 * (1 - (candidate_salary - job_salary_min) / (job_salary_max - job_salary_min + 1))))
                compensation_score = max(0, alignment)
            else:
                compensation_score = _score_from_hash(5, hash_val + 3, 15)
        else:
            compensation_score = _score_from_hash(10, hash_val + 3, 20)
        
        # Factor 4: Role fit (0-20 points)
        candidate_skills = set(candidate.get("skills", []))
        required_skills = set(job.get("required_skills", []))
        preferred_skills = set(job.get("preferred_skills", []))
        
        if required_skills:
            skill_match = len(candidate_skills & required_skills) / len(required_skills)
            role_fit = int(skill_match * 20)
        else:
            role_fit = _score_from_hash(12, hash_val + 4, 20)
        
        # Bonus for preferred skills
        if preferred_skills:
            preferred_match = len(candidate_skills & preferred_skills) / len(preferred_skills)
            role_fit = min(20, role_fit + int(preferred_match * 5))
        
        role_fit_score = min(20, role_fit)
        
        # Factor 5: Response positivity (0-20 points)
        # Based on work preference alignment
        work_pref = candidate.get("work_preference", "hybrid")
        remote_policy = job.get("remote_policy", "hybrid")
        
        if work_pref == remote_policy:
            response_positivity = _score_from_hash(15, hash_val + 5, 20)
        elif (work_pref == "hybrid" and remote_policy in ["remote", "onsite"]) or \
             (remote_policy == "hybrid" and work_pref in ["remote", "onsite"]):
            response_positivity = _score_from_hash(12, hash_val + 5, 18)
        else:
            response_positivity = _score_from_hash(8, hash_val + 5, 15)
        
        # Calculate total score
        total_score = (
            role_match_enthusiasm +
            availability_score +
            compensation_score +
            role_fit_score +
            response_positivity
        )
        
        # Determine interest label
        if total_score >= 75:
            interest_label = "high"
        elif total_score >= 50:
            interest_label = "medium"
        else:
            interest_label = "low"
        
        # Generate explanation
        factors = []
        if role_match_enthusiasm >= 15:
            factors.append("Strong alignment with desired role")
        if availability_score >= 15:
            factors.append("Quick availability")
        if compensation_score >= 15:
            factors.append("Compensation expectations align with offer")
        if role_fit_score >= 15:
            factors.append("Strong skills match")
        if response_positivity >= 15:
            factors.append("Work preference matches")
        
        if not factors:
            factors.append("Moderate fit across factors")
        
        explanation = f"Interest score based on: {', '.join(factors)}."
        
        return {
            "enthusiasm_score": role_match_enthusiasm,
            "availability_score": availability_score,
            "compensation_score": compensation_score,
            "role_fit_score": role_fit_score,
            "response_positivity_score": response_positivity
        }
    
    def simulate(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Run full outreach simulation for a candidate-job pair.
        Returns structured outreach data.
        """
        candidate_name = candidate.get("name", "Candidate")
        job_title = job.get("title", "Open Role")
        company = job.get("company", "Our Company")
        job_description = job.get("raw_text", "")
        
        # Generate outreach message
        outreach_message = self.generate_outreach_message(
            candidate_name=candidate_name,
            job_title=job_title,
            company=company,
            job_description=job_description,
            candidate_skills=candidate.get("skills", []),
            tone=tone
        )
        
        # Calculate interest score
        interest_breakdown = self.calculate_interest_score(candidate, job)
        total_score = sum(interest_breakdown.values())
        
        # Determine interest label
        if total_score >= 75:
            interest_label = "high"
        elif total_score >= 50:
            interest_label = "medium"
        else:
            interest_label = "low"
        
        # Generate candidate response based on interest
        candidate_response = self.generate_candidate_response(
            candidate_name=candidate_name,
            interest_level=interest_label
        )
        
        # Generate explanation
        factors = []
        if interest_breakdown["enthusiasm_score"] >= 15:
            factors.append("role alignment")
        if interest_breakdown["availability_score"] >= 15:
            factors.append("availability")
        if interest_breakdown["compensation_score"] >= 15:
            factors.append("compensation")
        if interest_breakdown["role_fit_score"] >= 15:
            factors.append("skills match")
        if interest_breakdown["response_positivity_score"] >= 15:
            factors.append("work preference")
        
        explanation = f"Interest score of {total_score}/100 based on {', '.join(factors) if factors else 'overall fit'}."
        
        return {
            "outreach_message": outreach_message,
            "candidate_response": candidate_response,
            "interest_score": total_score,
            "interest_breakdown": interest_breakdown,
            "interest_label": interest_label,
            "explanation": explanation
        }


# Singleton instance
_simulator = None


def get_simulator() -> OutreachSimulator:
    """Get the singleton simulator instance."""
    global _simulator
    if _simulator is None:
        _simulator = OutreachSimulator()
    return _simulator