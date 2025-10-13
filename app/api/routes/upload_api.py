from fastapi import APIRouter, UploadFile, File
from app.schemas.upload import PDFUploadResponse
from app.services.upload_service import UploadService

router = APIRouter()

@router.post(
    "/upload/pdf",
    response_model=PDFUploadResponse,
    tags=["Upload"],
    summary="PDF 업로드 및 분리",
)
async def upload_pdf(file: UploadFile = File(...)):
    result = await UploadService.save_and_split_pdf(file)
    return PDFUploadResponse(**result)
