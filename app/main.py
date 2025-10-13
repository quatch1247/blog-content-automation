# app/main.py

from fastapi import FastAPI
from app.api.main import api_router

app = FastAPI(
    title="Blog Content Automation",
    description="블로그 콘텐츠 자동화 서비스 API",
    version="0.1.0"
)

# 모든 API 라우터 등록 (prefix는 /api로 가정)
app.include_router(api_router)
