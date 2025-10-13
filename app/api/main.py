from fastapi import APIRouter

from app.api.routes import (
    health_api
) 

api_router = APIRouter()
api_router.include_router(health_api.router)

