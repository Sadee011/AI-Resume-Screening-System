# api/schemas.py
from pydantic import BaseModel
from typing import List, Optional
 
class PredictRequest(BaseModel):
    """API ekkata yawana data format"""
    resume_text:     str
    job_description: str
 
class SkillAnalysis(BaseModel):
    matching_skills:  List[str]
    missing_skills:   List[str]
    coverage_pct:     float
 
class PredictResponse(BaseModel):
    """API eken enana data format"""
    score:        float
    label:        str
    color:        str
    emoji:        str
    skills:       SkillAnalysis
    advice:       str  # Simple recommendation
