from fastapi import APIRouter, Depends, status
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
        return {"db": "failed"}, status.HTTP_503_SERVICE_UNAVAILABLE
    except Exception:
        return {"db": "failed"}, status.HTTP_503_SERVICE_UNAVAILABLE
