from typing import Any, Dict, List, Optional
from pydantic import BaseModel  # Pydantic is a library that says — "this data must look exactly like this, otherwise throw an error."

class ComponentScores(BaseModel):  # Just stores the score for each category. Remember SCORE_WEIGHTS in config.py? These are the components that contribute to the final ATS score.
    formatting: float
    keywords: float
    content: float
    skill_validation: float
    ats_compatibility: float

class JDComparison(BaseModel): # When you upload a resume and a job description, this will hold the results of how well they match.
    match_percentage: float
    semantic_similarity: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    skills_gap: List[str]

class SkillValidationDetails(BaseModel): # This checks — did the resume just list a skill, or did it actually show it in a project?
    validated: List[Dict[str, Any]] = []       # [{'skill': str, 'projects': [str]}]
    unvalidated: List[str] = []                # ['Flask', 'A/B Testing', ...]
    total: int = 0
    validated_count: int = 0
    validation_pct: float = 0.0

class IssueDetail(BaseModel):  # Every problem found in the resume gets stored as one IssueDetail object. Very structured — not just "bad formatting" but what it is, how bad, where, and how to fix it.
    issue_title: str
    severity_level: str
    ats_impact: str
    explanation: str
    where_it_appears: str
    how_to_fix: str
    action_items: List[str] = []
    example_improvement: str

class AnalysisResponse(BaseModel):
    ATS_score: float
    component_scores: ComponentScores
    issues_summary: List[str]
    detailed_feedback: List[IssueDetail]
    jd_match_analysis: Optional[JDComparison] = None   # Optional means — this field might exist or might be None
    skill_validation_details: Optional[SkillValidationDetails] = None

    ats_score: float
    keyword_match: float = 0.0
    missing_keywords: List[str] = []
    matched_keywords: List[str] = []
    suggestions: List[str] = []
    strengths: List[str] = []
    critical_issues: List[str] = []
    skills: List[str] = []
    jd_comparison: Optional[JDComparison] = None
    warnings: List[str] = []
    interpretation: str = ""