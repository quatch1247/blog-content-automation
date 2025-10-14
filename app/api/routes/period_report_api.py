from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from datetime import date
import io

from app.services.period_report_service import PeriodReportService

router = APIRouter(prefix="/period-report", tags=["period-report"])

@router.get("/")
def download_period_report(
    start_date: date = Query(..., description="시작일 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료일 (YYYY-MM-DD)")
):
    try:
        result = PeriodReportService.generate_period_report(start_date, end_date)
        return StreamingResponse(
            io.BytesIO(result["pdf_bytes"]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
        )
    except Exception:
        raise HTTPException(status_code=500, detail="알 수 없는 서버 오류입니다.")
