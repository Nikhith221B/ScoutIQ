from fastapi import APIRouter, HTTPException
from typing import List
import json
from pathlib import Path
import os

router = APIRouter()

# Get the backend directory (parent of app)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FILE = BACKEND_DIR / "app" / "data" / "talents.json"


def load_talents():
    """Load talents from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


@router.get("/talents")
def list_talents():
    """List all talents"""
    return load_talents()


@router.get("/talents/{talent_id}")
def get_talent(talent_id: str):
    """Get talent by ID"""
    talents = load_talents()
    for talent in talents:
        if str(talent.get("id")) == talent_id:
            return talent
    raise HTTPException(status_code=404, detail="Talent not found")