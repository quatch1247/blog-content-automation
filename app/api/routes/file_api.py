from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.file import PDFUploadResponse, FileListResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload/pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    result = await FileService.save_and_split_pdf(file)
    return PDFUploadResponse(**result)

@router.get("/", response_model=FileListResponse)
def list_files():
    result = FileService.list_files()
    return FileListResponse(
        raw_pdf_count=result["raw_pdf_count"],
        refined_posts=result["refined_posts"],
        refined_post_count=result["refined_post_count"],
    )
