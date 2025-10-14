from enum import Enum

class ErrorCode(Enum):
    INVALID_FILE_TYPE = ("E001", "허용되지 않는 파일 형식입니다.", 400)
    FILE_ALREADY_EXISTS = ("E002", "동일한 이름의 파일이 이미 존재합니다.", 409)
    FILE_SAVE_FAILED = ("E003", "파일 저장 중 오류가 발생했습니다.", 500)
    FILE_NOT_FOUND = ("E004", "파일을 찾을 수 없습니다.", 404)

    PDF_PROCESSING_FAILED = ("E005", "PDF 처리 중 오류가 발생했습니다.", 500)
    PDF_SPLIT_FAILED = ("E006", "PDF 분할 중 오류가 발생했습니다.", 500)
    PDF_CONVERT_FAILED = ("E007", "PDF 변환 중 오류가 발생했습니다.", 500)

    DB_SAVE_FAILED = ("E008", "DB 저장 중 오류가 발생했습니다.", 500)
    LLM_API_FAILED = ("E900", "LLM 호출 중 오류가 발생했습니다.", 500)

    PARAMETER_VALIDATION_ERROR = ("E100", "요청 파라미터 검증 실패", 422)
    INTERNAL_ERROR = ("E999", "서버 내부 오류", 500)
    UNAUTHORIZED = ("E401", "인증이 필요합니다.", 401)

    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
