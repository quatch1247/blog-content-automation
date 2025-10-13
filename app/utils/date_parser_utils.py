import re
from datetime import datetime
from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode

def parse_datetime_flexible(date_str: str) -> datetime:
    if not isinstance(date_str, str):
        raise APIException(
            ErrorCode.PDF_PROCESSING_FAILED,
            details=[f"날짜 타입이 문자열이 아닙니다: {type(date_str)}"]
        )

    cleaned = date_str.strip()
    cleaned = re.sub(r"[./]", "-", cleaned)

    try:
        return datetime.strptime(cleaned, "%Y-%m-%d %H:%M")
    except ValueError:
        raise APIException(
            ErrorCode.PDF_PROCESSING_FAILED,
            details=[f"날짜 포맷이 잘못되었습니다: {date_str} (예: 2025/09/23 08:50)"]
        )