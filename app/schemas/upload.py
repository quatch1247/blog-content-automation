from typing import List
from pydantic import BaseModel, Field

class SplitFileInfo(BaseModel):
    post_id: str = Field(..., description="블로그 포스트 ID (예: kangsan2023/224002720438)")
    range: str = Field(..., description="포스트가 차지하는 페이지 범위 (예: 1-3)")
    file: str = Field(..., description="분리된 PDF 파일 경로")

class PDFUploadResponse(BaseModel):
    success: bool = Field(default=True, description="업로드 및 분리 성공 여부")
    original_pdf: str = Field(..., description="원본 PDF 저장 경로", example="uploads/raw/블로그-1.pdf")
    split_folder: str = Field(..., description="분리된 PDF 저장 폴더", example="uploads/split/블로그-1/")
    split_files: List[SplitFileInfo] = Field(..., description="분리된 포스트별 PDF 파일 목록")
