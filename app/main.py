from fastapi import FastAPI
from app.api.main import api_router
from app.core.exception_handlers import api_exception_handler
from app.core.exceptions import APIException
from app.core.init_db import init_db  # ← 초기화 함수 import

app = FastAPI(
    title="Blog Content Automation",
    description="블로그 콘텐츠 자동화 서비스 API",
    version="0.1.0",
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router)

app.add_exception_handler(APIException, api_exception_handler)
