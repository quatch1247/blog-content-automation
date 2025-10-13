import os
from fastapi import UploadFile
from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.utils.pdf_utils import convert_pdf_to_html, extract_page_map, detect_post_ranges
from app.utils.pdf_splitter import split_pdf_by_ranges
from app.utils.pdf_refiner import batch_refine_split_posts  # <-- 추가!

RAW_UPLOAD_DIR = "uploads/raw_pdf"
SPLIT_BASE_DIR = "uploads/split_posts"
REFINED_POSTS_DIR = "uploads/refined_posts"
os.makedirs(RAW_UPLOAD_DIR, exist_ok=True)
os.makedirs(SPLIT_BASE_DIR, exist_ok=True)
os.makedirs(REFINED_POSTS_DIR, exist_ok=True)

class UploadService:
    @staticmethod
    async def save_and_split_pdf(file: UploadFile) -> dict:
        # 파일 유효성 검증
        if not file.filename.lower().endswith(".pdf"):
            raise APIException(ErrorCode.INVALID_FILE_TYPE, details=[file.filename])

        raw_path = os.path.join(RAW_UPLOAD_DIR, file.filename)
        if os.path.exists(raw_path):
            raise APIException(ErrorCode.FILE_ALREADY_EXISTS, details=[file.filename])

        try:
            with open(raw_path, "wb") as f:
                f.write(await file.read())
        except Exception as e:
            raise APIException(ErrorCode.FILE_SAVE_FAILED, details=[str(e)])

        base_name = os.path.splitext(file.filename)[0]
        split_dir = os.path.join(SPLIT_BASE_DIR, base_name)
        os.makedirs(split_dir, exist_ok=True)

        try:
            # PDF → HTML 변환
            html_str = convert_pdf_to_html(raw_path)

            # 페이지별 구간 추출
            page_map = extract_page_map(html_str)

            # 포스트 단위 구간 감지
            post_ranges = detect_post_ranges(page_map)

            # 포스트별로 PDF 분리 저장
            split_files = split_pdf_by_ranges(raw_path, split_dir, post_ranges)

            # 🎯 바로 refined_posts 후처리! (split_dir만 처리)
            refined_results = batch_refine_split_posts(
                split_dir=split_dir,
                output_dir=os.path.join(REFINED_POSTS_DIR, base_name),
                max_workers=2  # 병렬 처리, 코어 수 맞게 조절
            )

        except Exception as e:
            if os.path.exists(split_dir) and not os.listdir(split_dir):
                os.rmdir(split_dir)
            raise APIException(ErrorCode.PDF_PROCESSING_FAILED, details=[str(e)])

        return {
            "success": True,
            "original_pdf": raw_path,
            "split_folder": split_dir,
            "split_files": split_files,
            "refined_results": refined_results,
            "refined_folder": os.path.join(REFINED_POSTS_DIR, base_name),
        }
