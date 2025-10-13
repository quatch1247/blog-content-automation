from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db

router = APIRouter()

@router.get("/health", tags=["Health"])
def ping(): 
    return {"status": "ok"}

@router.get("/health/db", tags=["Health"])
def check_db(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {"db": "ok"}
        return {"db": "failed"}
    except Exception as e:
        return {"db": "failed", "detail": str(e)}
