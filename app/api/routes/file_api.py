from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.schemas.file import PDFUploadResponse, FileListResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload/pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    result = await FileService.save_and_split_pdf(file)
    return PDFUploadResponse(**result)


@router.post("/upload/pdf/multi", response_model=List[PDFUploadResponse]) #프론트 멀티 업로드용.. 스웨거 x
async def upload_multi_pdf(files: List[UploadFile] = File(...)): 
    results = []
    for file in files:
        try:
            result = await FileService.save_and_split_pdf(file)
            results.append(PDFUploadResponse(**result))
        except Exception as e:
            pass
    return results


@router.get("/", response_model=FileListResponse)
def list_files():
    result = FileService.list_files()
    return FileListResponse(
        raw_pdf_count=result["raw_pdf_count"],
        refined_posts=result["refined_posts"],
        refined_post_count=result["refined_post_count"],
    )
    

@router.delete("/truncate/all")
def truncate_all():
    FileService.truncate_all()
    return {"success": True, "message": "모든 PDF 파일, 폴더, DB 기록이 초기화되었습니다."}

