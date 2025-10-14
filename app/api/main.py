from fastapi import APIRouter

from app.api.routes import (
    file_api,
    health_api,
    thumbnail_api
) 

api_router = APIRouter()
api_router.include_router(health_api.router)
api_router.include_router(file_api.router)
api_router.include_router(thumbnail_api.router)


