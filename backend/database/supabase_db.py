import logging
import httpx
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict

logger = logging.getLogger('ats_resume_scorer')

from backend.core.config import SUPABASE_URL, SUPABASE_KEY

# Job 1 — Building the Headers
def _get_headers():   # Headers → metadata about the request
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return {
        "apikey": SUPABASE_KEY,   # apikey Your Supabase API key, Authorization Same key, different format — Supabase needs both
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",  # Content-TypeTells Supabase "I'm sending JSON data"
        "Prefer": "return=representation"    # Prefer: return=representation"After saving, send me back the saved record"
    }

# Job 2 — Saving an Analysis
async def save_analysis(user_id: str, filename: str, analysis_result: Dict) -> Optional[str]:  # This saves a resume analysis to the database. Returns the saved record's ID, or None if it failed.
    headers = _get_headers()
    if not headers:
        return None

    def _json_default(o):
        if hasattr(o, 'model_dump'):
            return o.model_dump()  #  Pydantic's method to convert an object to a plain dictionary
        return str(o)
    serializable_result = json.loads(json.dumps(analysis_result, default=_json_default))  # convert that string back to a plain Python dictionary

    doc = {
        "user_id": user_id,
        "filename": filename,
        "ats_score": serializable_result.get("ats_score", 0),
        "keyword_match": serializable_result.get("keyword_match", 0),
        "missing_keywords": serializable_result.get("missing_keywords", []),
        "created_at": datetime.now(timezone.utc).isoformat(),    # current time in UTC, formatted as a string like "2024-01-15T10:23:45+00:00". Always use UTC in databases so there's no timezone confusion.
        "analysis_result": serializable_result,
    }

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analyses"    # .rstrip('/') → removes trailing slash from URL if present, so you don't get https://xyz.com//rest/v1 accidentally. , /rest/v1/ → this is Supabase's API path. Every Supabase database is accessible at this path.
    
    try:
        async with httpx.AsyncClient() as client:    # async with → opens an HTTP client, uses it, then automatically closes it when done. Clean and safe. , httpx is like requests but supports async.
            response = await client.post(url, headers=headers, json=doc)    # await means "pause here until this slow thing finishes, but let others run meanwhile.
            response.raise_for_status()    # raise_for_status() → if Supabase returns an error (like 401 unauthorized, 500 server error), this automatically raises an exception instead of silently failing.
            data = response.json()
            if data and len(data) > 0:
                inserted_id = str(data[0].get("id"))   # extracts user id 
                logger.info(f"Saved analysis for user {user_id}: {inserted_id}")
                return inserted_id
            return None
    except Exception as exc:
        logger.error(f"Failed to save analysis to Supabase: {exc}")
        return None

# Job 3 — Fetching User History
async def get_user_history(user_id: str) -> List[Dict]:
    headers = _get_headers()
    if not headers:
        return []

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analyses"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, 
                headers=headers, 
                params={
                    "user_id": f"eq.{user_id}",   # eq.{user_id} → "where user_id equals this value" (eq = equals)
                    "order": "created_at.desc"    # created_at.desc → sort by date, newest first
                }
            )
            response.raise_for_status()
            docs = response.json()
            
            results = []
            for doc in docs:
                results.append({
                    "id": str(doc.get("id")),     # .get("field", default) → get this field, but if it doesn't exist use the default value instead of crashing.
                    "filename": doc.get("filename", "resume"),
                    "resume_name": doc.get("filename", "resume"),
                    "job_title": "Software Engineer",
                    "ats_score": doc.get("ats_score", 0),
                    "keyword_match": doc.get("keyword_match", 0),
                    "missing_keywords": doc.get("missing_keywords", []),
                    "date": doc.get("created_at", ""),
                    "created_at": doc.get("created_at", ""),
                    "analysis_result": doc.get("analysis_result", {}),
                })
            return results
    except Exception as exc:
        logger.error(f"Failed to fetch history from Supabase: {exc}")
        return []

# Job 4 — Deleting an Analysis
async def delete_analysis(analysis_id: str, user_id: str) -> bool:
    headers = _get_headers()
    if not headers:
        return False

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analyses"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url, 
                headers=headers, 
                params={
                    "id": f"eq.{analysis_id}",
                    "user_id": f"eq.{user_id}"
                }
            )
            response.raise_for_status()
            return True
    except Exception as exc:
        logger.error(f"Failed to delete analysis {analysis_id}: {exc}")
        return False