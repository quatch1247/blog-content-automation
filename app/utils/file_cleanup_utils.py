import os
import shutil
import logging

logger = logging.getLogger(__name__)

def safe_remove(path: str):
    try:
        if not os.path.exists(path):
            return

        if os.path.isfile(path):
            os.remove(path)
            logger.info(f"[CLEANUP] 파일 삭제: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            logger.info(f"[CLEANUP] 폴더 삭제: {path}")
    except Exception as e:
        logger.warning(f"[CLEANUP WARN] {path} 삭제 실패: {e}")
