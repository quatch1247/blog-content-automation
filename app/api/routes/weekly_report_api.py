from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from datetime import date
import io

from app.services.weekly_report_service import WeeklyReportService

router = APIRouter(prefix="/weekly-report", tags=["weekly-report"])

@router.get("/")
def download_weekly_report(
    start_date: date = Query(..., description="시작일 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료일 (YYYY-MM-DD)")
):
    try:
        result = WeeklyReportService.generate_weekly_report(start_date, end_date)
        return StreamingResponse(
            io.BytesIO(result["pdf_bytes"]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
