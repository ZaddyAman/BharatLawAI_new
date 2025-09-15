import json
import os
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from db import crud, schemas
from db.database import SessionLocal

router = APIRouter()

ACTS_DIR = os.getenv("ACTS_DIR", "/data/annotatedCentralActs")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Cache for all acts data to avoid re-reading files on every request
_all_acts_cache: List[Dict[str, Any]] = []

def flatten_paragraphs(paragraphs: Any) -> str:
    """Recursively flatten paragraphs into a single text string"""
    text_blocks = []

    def recurse(obj: Any):
        if isinstance(obj, str):
            text_blocks.append(obj)
        elif isinstance(obj, dict):
            for val in obj.values():
                recurse(val)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)

    recurse(paragraphs)
    return "\n".join(text_blocks)

def _extract_year_from_date(date_string: str) -> Optional[int]:
    """Extract year from enactment date string like '[27th March, 1855.]'"""
    if not date_string or not isinstance(date_string, str):
        return None

    import re
    # Look for 4-digit year pattern
    year_match = re.search(r'(\d{4})', date_string)
    if year_match:
        try:
            return int(year_match.group(1))
        except ValueError:
            return None
    return None

def _load_all_acts_from_files():
    """Loads all acts data from JSON files into cache."""
    global _all_acts_cache
    if _all_acts_cache: # Only load if cache is empty
        return

    print("Loading all acts from files into cache...")
    temp_acts_data = []
    for fname in os.listdir(ACTS_DIR):
        if fname.endswith(".json"):
            fpath = os.path.join(ACTS_DIR, fname)
            with open(fpath, encoding="utf-8") as f:
                try:
                    act_json = json.load(f)
                    
                    act_title = act_json.get("Act Title", "Unknown Act")
                    act_id = act_json.get("Act ID", os.path.splitext(fname)[0]) # Use filename as ID if not present
                    enactment_date = act_json.get("Enactment Date", "")
                    preamble_dict = act_json.get("Act Definition", {})
                    preamble = flatten_paragraphs(preamble_dict)

                    chapters = []
                    parts = act_json.get("Parts", {})
                    for part_name, part_data in parts.items():
                        chapter_sections = []
                        sections_dict = part_data.get("Sections", {})
                        for sec_no, sec_data in sections_dict.items():
                            heading = sec_data.get("heading", "")
                            paragraphs = sec_data.get("paragraphs", {})
                            text = flatten_paragraphs(paragraphs)
                            chapter_sections.append({
                                "section_no": sec_no,
                                "heading": heading,
                                "text": text
                            })
                        chapters.append({
                            "name": part_name,
                            "sections": chapter_sections
                        })
                    
                    # If no parts, check for top-level sections (some acts are flat)
                    if not chapters and "Sections" in act_json:
                        flat_sections = []
                        for sec_no, sec_data in act_json["Sections"].items():
                            heading = sec_data.get("heading", "")
                            paragraphs = sec_data.get("paragraphs", {})
                            text = flatten_paragraphs(paragraphs)
                            flat_sections.append({
                                "section_no": sec_no,
                                "heading": heading,
                                "text": text
                            })
                        chapters.append({
                            "name": "Main Body", # Default chapter name for flat acts
                            "sections": flat_sections
                        })

                    temp_acts_data.append({
                        "title": act_title,
                        "id": act_id,
                        "enactment_date": enactment_date,
                        "preamble": preamble,
                        "chapters": chapters,
                        "file_name": fname # Store filename to retrieve full act later
                    })
                except Exception as e:
                    print(f"Error processing {fpath}: {e}")
    _all_acts_cache = temp_acts_data
    print(f"Loaded {len(_all_acts_cache)} acts into cache.")

@router.get("/acts")
async def get_acts(skip: int = 0, limit: int = 10, search_query: Optional[str] = None, year: Optional[int] = None, sort_by: Optional[str] = None):
    print(f"[API] Acts request: skip={skip}, limit={limit}, search_query={search_query}, year={year}, sort_by={sort_by}")
    _load_all_acts_from_files() # Ensure cache is loaded

    filtered_acts = _all_acts_cache

    # Apply search filter
    if search_query:
        search_query_lower = search_query.lower()
        filtered_acts = [
            act for act in _all_acts_cache
            if search_query_lower in act["title"].lower()
        ]

    # Apply year filter
    if year:
        filtered_acts = [
            act for act in filtered_acts
            if _extract_year_from_date(act["enactment_date"]) == year
        ]
        print(f"[API] Applied year filter: {year}, remaining acts: {len(filtered_acts)}")

    # Apply sorting
    if sort_by == "date_desc":
        # Sort by year descending, then by date string within year
        filtered_acts.sort(key=lambda x: (_extract_year_from_date(x["enactment_date"]) or 0, x["enactment_date"]), reverse=True)
    elif sort_by == "date_asc":
        # Sort by year ascending, then by date string within year
        filtered_acts.sort(key=lambda x: (_extract_year_from_date(x["enactment_date"]) or 9999, x["enactment_date"]))
    elif sort_by == "title_asc":
        # Sort alphabetically by title
        filtered_acts.sort(key=lambda x: x["title"].lower())
    else:
        # Default: Sort alphabetically by title
        filtered_acts.sort(key=lambda x: x["title"].lower())

    total_count = len(filtered_acts)
    paginated_acts = filtered_acts[skip : skip + limit]

    # For the main list, only return summary data, not full chapters/sections
    summary_acts = [
        {
            "title": act["title"],
            "id": act["id"],
            "enactment_date": act["enactment_date"],
            "file_name": act["file_name"] # Keep filename for detail fetch
        }
        for act in paginated_acts
    ]

    print(f"[API] Acts response: total_count={total_count}, returned_count={len(summary_acts)}")
    return {
        "total_count": total_count,
        "acts": summary_acts
    }

@router.get("/acts/{act_file_name}")
async def get_act_details(act_file_name: str):
    _load_all_acts_from_files() # Ensure cache is loaded

    for act in _all_acts_cache:
        if act["file_name"] == act_file_name:
            # Return the full act details including chapters and sections
            return act
    
    raise HTTPException(status_code=404, detail="Act not found")

@router.get("/judgments")
async def get_judgments(skip: int = 0, limit: int = 10, search_query: Optional[str] = None, year: Optional[int] = None, sort_by: Optional[str] = None, db: Session = Depends(get_db)):
    print(f"[API] Judgments request: skip={skip}, limit={limit}, search_query={search_query}, year={year}, sort_by={sort_by}")
    judgments, total_count = crud.get_judgments(db, skip=skip, limit=limit, search_query=search_query, year=year, sort_by=sort_by)
    print(f"[API] Judgments response: total_count={total_count}, returned_count={len(judgments)}")
    return {
        "total_count": total_count,
        "judgments": judgments
    }

@router.get("/judgments/{judgment_id}")
async def get_judgment_details(judgment_id: int, db: Session = Depends(get_db)):
    db_judgment = crud.get_judgment(db, judgment_id=judgment_id)
    if db_judgment is None:
        raise HTTPException(status_code=404, detail="Judgment not found")
    return db_judgment
