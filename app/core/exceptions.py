import logging
from app.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)

class APIException(Exception):
    def __init__(self, error: ErrorCode, details: list = None):
        self.error = error
        self.details = details or []
        logger.warning(f"[{error.code}] {error.message} | details: {self.details}")
