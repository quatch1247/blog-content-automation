from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def ping(): 
    return {"status": "ok"}