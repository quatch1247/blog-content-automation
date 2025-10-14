from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.thumbnail_service import ThumbnailService
import io

router = APIRouter(prefix="/thumbnails", tags=["thumbnails"])

@router.get("/download/{post_id}")
def download_thumbnail(post_id: int):
    try:
        result = ThumbnailService.generate_thumbnail_info(post_id)
        return StreamingResponse(
            io.BytesIO(result["image_bytes"]),
            media_type="image/webp",
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
