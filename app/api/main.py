from fastapi import APIRouter

from app.api.routes import (
    health_api,
    upload_api
) 

api_router = APIRouter()
api_router.include_router(health_api.router)
api_router.include_router(upload_api.router)

