from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import APIException

async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.error.status_code,
        content={
            "error": {
                "code": exc.error.code,
                "message": exc.error.message,
                "details": exc.details,
            }
        },
    )
