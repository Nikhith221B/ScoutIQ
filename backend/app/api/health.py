from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI-Powered Talent Scouting & Engagement Agent",
        "version": "0.1.0"
    }