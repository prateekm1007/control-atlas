from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.nkg import NKGRegistry
import json
from pathlib import Path

router = APIRouter()

@router.get("/library")
def get_law_library():
    codex_path = Path(__file__).parent.parent / "core" / "mdi_codex.json"
    with open(codex_path, "r") as f:
        return json.load(f)["laws"]

@router.get("/analytics/matrix")
def get_nkg_matrix(db: Session = Depends(get_db)):
    entries = db.query(NKGRegistry).filter(NKGRegistry.primary_law != None).all()
    matrix = {}
    
    if not entries:
        return {}

    for e in entries:
        p = e.primary_law
        if p not in matrix: 
            matrix[p] = {}
        
        # Ensure the matrix is 2D by logging the primary law against itself
        matrix[p][p] = matrix[p].get(p, 0) + 1
        
        # Log secondary interactions
        for s in (e.secondary_laws or []):
            if s:
                matrix[p][s] = matrix[p].get(s, 0) + 1
                
    return matrix

@router.get("/analytics/summary")
def get_nkg_summary(db: Session = Depends(get_db)):
    total = db.query(NKGRegistry).count()
    return {"sample_size": total, "scope": "Global · Systemic", "window": "Last 30 Days"}
