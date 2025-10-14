from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.summarize_service import SummaryService
import io

router = APIRouter(prefix="/summaries", tags=["summaries"])

@router.get("/download/{post_id}")
def download_summary_pdf(post_id: int):
    try:
        result = SummaryService.generate_summary_pdf(post_id)
        return StreamingResponse(
            io.BytesIO(result["pdf_bytes"]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
