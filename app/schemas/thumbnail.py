from pydantic import BaseModel
from typing import Optional

class ThumbnailRequest(BaseModel):
    post_id: int

class ThumbnailResponse(BaseModel):
    success: bool
    post_id: int
    title: str
    thumbnail_url: str
    message: Optional[str] = "썸네일 생성 완료"
