import os
import json
import logging
from typing import List
from fastapi import UploadFile

from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.utils.pdf_utils import convert_pdf_to_html, extract_page_map, detect_post_ranges
from app.utils.pdf_splitter import split_pdf_by_ranges
from app.utils.pdf_refiner import batch_refine_split_posts
from app.utils.date_parser_utils import parse_datetime_flexible
from app.utils.file_cleanup_utils import safe_remove  # 🔥 새로 추가
from app.repositories import pdf_repository
from app.core.db import get_db_session
from app.schemas.upload import SplitFileInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RAW_UPLOAD_DIR = "uploads/raw_pdf"
SPLIT_BASE_DIR = "uploads/split_posts"
REFINED_POSTS_DIR = "uploads/refined_posts"
os.makedirs(RAW_UPLOAD_DIR, exist_ok=True)
os.makedirs(SPLIT_BASE_DIR, exist_ok=True)
os.makedirs(REFINED_POSTS_DIR, exist_ok=True)


class UploadService:
    @staticmethod
    async def save_and_split_pdf(file: UploadFile) -> dict:
        # 파일 확장자 검증
        if not file.filename.lower().endswith(".pdf"):
            raise APIException(ErrorCode.INVALID_FILE_TYPE, details=[file.filename])

        raw_path = os.path.join(RAW_UPLOAD_DIR, file.filename)
        if os.path.exists(raw_path):
            raise APIException(ErrorCode.FILE_ALREADY_EXISTS, details=[file.filename])

        db = get_db_session()
        split_dir = None
        refined_dir = None

        try:
            # PDF 파일 저장
            with open(raw_path, "wb") as f:
                f.write(await file.read())
            logger.info(f"[INFO] 원본 PDF 저장 완료: {raw_path}")

            # RawPdf DB 저장
            raw_pdf_obj = pdf_repository.create_raw_pdf(db, filename=file.filename, path=raw_path)

            # 폴더 준비
            base_name = os.path.splitext(file.filename)[0]
            split_dir = os.path.join(SPLIT_BASE_DIR, base_name)
            refined_dir = os.path.join(REFINED_POSTS_DIR, base_name)
            os.makedirs(split_dir, exist_ok=True)
            os.makedirs(refined_dir, exist_ok=True)

            # PDF → HTML 변환 및 포스트 구간 탐색
            html_str = convert_pdf_to_html(raw_path)
            page_map = extract_page_map(html_str)
            post_ranges = detect_post_ranges(page_map)

            # PDF 분할
            split_files: List[SplitFileInfo] = split_pdf_by_ranges(raw_path, split_dir, post_ranges)
            logger.info(f"[INFO] PDF 분할 완료: {len(split_files)}개 파일 생성")

            # SplitPost DB 저장
            split_post_objs = []
            for split_info in split_files:
                split_filename = os.path.basename(split_info.file)
                split_post_obj = pdf_repository.create_split_post(
                    db,
                    raw_pdf_id=raw_pdf_obj.id,
                    filename=split_filename,
                    path=split_info.file,
                )
                split_post_objs.append(split_post_obj)

            # 분할된 PDF 후처리 (정제)
            refined_results = batch_refine_split_posts(
                split_dir=split_dir,
                output_dir=refined_dir,
                max_workers=2
            )

            # RefinedPost DB 저장
            for idx, refined in enumerate(refined_results.get("results", [])):
                split_post_obj = split_post_objs[idx]

                parsed_json_path = refined.get("parsed_json_path")
                if isinstance(parsed_json_path, dict):
                    parsed_json_path = parsed_json_path.get("path")

                if not isinstance(parsed_json_path, str):
                    raise APIException(
                        ErrorCode.PDF_PROCESSING_FAILED,
                        details=[f"Invalid parsed_json_path type: {type(parsed_json_path)}"]
                    )

                with open(parsed_json_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)

                parsed_date = None
                try:
                    parsed_date = parse_datetime_flexible(meta.get("date")) if meta.get("date") else None
                except Exception as e:
                    logger.warning(f"[WARN] 날짜 파싱 실패 ({meta.get('date')}): {e}")

                pdf_repository.create_refined_post(
                    db,
                    split_post_id=split_post_obj.id,
                    json_path=parsed_json_path,
                    images_dir=os.path.join(os.path.dirname(parsed_json_path), "images"),
                    title=meta.get("title"),
                    author=meta.get("author"),
                    date=parsed_date,
                    url=meta.get("url"),
                )

        except Exception as e:
            logger.error(f"[ERROR] PDF 처리 중 예외 발생: {e}", exc_info=True)
            db.rollback()

            safe_remove(raw_path)
            if split_dir:
                safe_remove(split_dir)
            if refined_dir:
                safe_remove(refined_dir)

            raise APIException(ErrorCode.PDF_PROCESSING_FAILED, details=[str(e)])

        finally:
            db.close()

        return {
            "success": True,
            "original_pdf": raw_path,
            "split_folder": split_dir,
            "split_files": [s.model_dump() for s in split_files],
            "refined_results": refined_results,
            "refined_folder": refined_dir,
        }
